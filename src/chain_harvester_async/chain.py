import asyncio
import json
import logging
import os
from collections import defaultdict

import aiofiles
import aiofiles.os
import aiofiles.ospath as ospath
import aiohttp
import eth_abi
from botocore.exceptions import ClientError
from environs import env
from eth_abi.exceptions import InvalidPointer
from eth_utils.abi import event_abi_to_log_topic
from hexbytes import HexBytes
from web3 import AsyncWeb3, Web3
from web3._utils.rpc_abi import RPC
from web3.exceptions import ContractLogicError, Web3RPCError
from web3.middleware import ExtraDataToPOAMiddleware, validation
from web3.providers.rpc.utils import (
    REQUEST_RETRY_ALLOWLIST,
    ExceptionRetryConfiguration,
)

from chain_harvester_async.adapters import sink
from chain_harvester_async.chainlink.chainlink import get_usd_price_feed_for_asset_symbol
from chain_harvester.constants import CHAINS, MULTICALL3_ADDRESSES, NULL_ADDRESS
from chain_harvester.decoders import (
    AnonymousEventLogDecoder,
    EventLogDecoder,
    EventRawLogDecoder,
    MissingABIEventDecoderError,
)
from chain_harvester.exceptions import ChainException, ConfigError
from chain_harvester.utils.codes import get_code_name
from chain_harvester_async.utils.http import retry_post_json
from chain_harvester_async.utils.s3 import fetch_abi_from_s3, save_abi_to_s3

from chain_harvester_async.multicall.call import Call
from chain_harvester_async.multicall.multicall import Multicall

log = logging.getLogger(__name__)

# Disable chain id validation on eth_call method as we're always just fetching data
# and under current assumption we never run any important queries that modify
# the chain
validation.METHODS_TO_VALIDATE = set(validation.METHODS_TO_VALIDATE) - {RPC.eth_call}


class Chain:
    latest_block_offset = 5

    def __init__(
        self,
        chain,
        network,
        rpc=None,
        chain_id=None,
        abis_path=None,
        step=None,
        s3=None,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self._w3 = None

        self.chain = chain
        self.network = network
        self.chain_id = chain_id or CHAINS[self.chain][self.network]

        rpc_env = f"{self.chain.upper()}_{self.network.upper()}_RPC"
        self.rpc = rpc or env(rpc_env, None)
        if not self.rpc:
            raise ConfigError(
                "Missing RPC configuration. Provide 'rpc' explicitly or set the "
                f"environment variable '{rpc_env}'."
            )

        self.abis_path = abis_path or f"abis/{self.chain.lower()}/{self.network.lower()}/"

        self.s3_config = None
        if s3 and s3.get("bucket_name") and s3.get("dir"):
            self.s3_config = {
                "bucket_name": s3["bucket_name"],
                "dir": s3["dir"],
                "region": s3.get("region", "eu-west-1"),
                "chain": chain,
                "network": network,
            }

        step_env = f"{self.chain.upper()}_{self.network.upper()}_STEP"
        self.step = step or env.int(step_env, 10_000)

        self._abis = {}
        self._contracts = {}

    @property
    def w3(self):
        if not self._w3:
            timeout = aiohttp.ClientTimeout(total=60)

            exception_retry_config = ExceptionRetryConfiguration(
                errors=(ClientError, asyncio.TimeoutError),
                retries=3,
                backoff_factor=0.5,
                method_allowlist=REQUEST_RETRY_ALLOWLIST,
            )

            self._w3 = AsyncWeb3(
                AsyncWeb3.AsyncHTTPProvider(
                    self.rpc,
                    request_kwargs={"timeout": timeout},
                    exception_retry_configuration=exception_retry_config,
                )
            )
            self._w3.middleware_onion.inject(ExtraDataToPOAMiddleware, layer=0)
        return self._w3

    @property
    def eth(self):
        return self.w3.eth

    async def aclose(self):
        if not self._w3:
            return

        await self._w3.provider.disconnect()

    async def get_block_info(self, block_number):
        return await self.eth.get_block(block_number)

    async def get_latest_block(self, offset=None):
        """
        Return the latest block number adjusted by an offset.

        If `offset` is provided, it is used directly. Otherwise the chain's
        predefined `latest_block_offset` value is applied. This is useful for
        chains whose RPC endpoints lag behind the true latest block and require
        querying a safely-confirmed block height instead.

        Returns the block number after subtracting the effective offset.
        """
        effective_offset = offset if offset is not None else self.latest_block_offset
        latest_block = await self.eth.get_block_number()
        return latest_block - effective_offset

    async def get_abi_from_source(self, contract_address):
        raise NotImplementedError

    async def _fetch_abi_from_web(self, contract_address, refetch_on_block=None):
        proxy_contract = await self.get_implementation_address(contract_address, refetch_on_block)
        abi_address = contract_address if proxy_contract == NULL_ADDRESS else proxy_contract
        abi = await self.get_abi_from_source(abi_address)
        return abi

    async def _handle_abi_s3(self, contract_address, file_path):
        """Fetch abi from s3 if it exists, otherwise fetch from web and upload to s3"""
        log.debug("Attempting to fetch ABI for contract %s from S3", contract_address)
        try:
            abi = await fetch_abi_from_s3(self.s3_config, contract_address)
        except ClientError as e:
            if e.response["Error"]["Code"] != "NoSuchKey":
                raise

            log.debug(
                "Couldn't fetch ABI for contract %s from S3. Fetching from web instead",
                contract_address,
            )
            abi = await self._fetch_abi_from_web(contract_address)
            # First save it to s3
            log.debug("Saving ABI for contract %s to S3", contract_address)
            await save_abi_to_s3(self.s3_config, contract_address, abi)
            # Then save it to local storage
            log.debug("Saving ABI for contract %s to local storage", contract_address)
            async with aiofiles.open(file_path, "w") as f:
                await f.write(json.dumps(abi))
        return abi

    async def _handle_abi_local_storage(self, contract_address, file_path):
        """Fetch ABI from web and save to local storage"""
        log.error(
            "ABI for %s was fetched from 3rd party service. Add it to abis folder!",
            contract_address,
        )
        abi = await self._fetch_abi_from_web(contract_address)

        async with aiofiles.open(file_path, "w") as f:
            await f.write(json.dumps(abi))
        return abi

    async def load_abi(self, contract_address, refetch_on_block=None, **kwargs):
        contract_address = contract_address.lower()

        # if refetch_on_block is set, we should skip storing the ABI to file as it's
        # usually only used when backpopulating stuff and storing it to the file will
        # replace the current abi with an old one
        if refetch_on_block:
            log.info(
                "Fetching new ABI on block %s without storing it to file",
                refetch_on_block,
            )
            abi = await self._fetch_abi_from_web(contract_address, refetch_on_block)
            self._abis[contract_address] = abi
            return abi

        if contract_address in self._abis:
            return self._abis[contract_address]

        file_path = os.path.join(self.abis_path, f"{contract_address}.json")
        if await ospath.exists(file_path):
            async with aiofiles.open(file_path) as f:
                data = await f.read()

            abi = json.loads(data)
            self._abis[contract_address] = abi
            return abi
        else:
            # Create the abis_path if it doesn't exist yet
            await aiofiles.os.makedirs(self.abis_path, exist_ok=True)

        if self.s3_config:
            abi = await self._handle_abi_s3(contract_address, file_path)
        else:
            abi = await self._handle_abi_local_storage(contract_address, file_path)
        self._abis[contract_address] = abi
        return abi

    async def get_implementation_address(self, contract_address, block_identifier=None):
        # EIP-1967 storage slot
        contract_address = Web3.to_checksum_address(contract_address)

        # Logic contract address
        slot = "0x360894a13ba1a3210667c828492db98dca3e2076cc3735a920a3ca505d382bbc"
        impl_address = await self.get_storage_at(contract_address, int(slot, 16), block_identifier)

        address = Web3.to_checksum_address(impl_address[-40:])

        #  Beacon contract address
        if address == NULL_ADDRESS:
            try:
                data = await self.multicall(
                    [
                        (
                            contract_address,
                            "implementation()(address)",
                            ["address", None],
                        ),
                    ],
                    block_identifier=block_identifier,
                )
                if data["address"]:
                    address = Web3.to_checksum_address(data["address"])
            except ContractLogicError:
                pass

        return address

    async def get_contract(self, contract_address, refetch_on_block=None):
        # This function can be called many, many times, so we cache already instantiated
        # contracts
        contract_address = Web3.to_checksum_address(contract_address)

        if refetch_on_block or contract_address not in self._contracts:
            abi = await self.load_abi(contract_address, refetch_on_block=refetch_on_block)
            contract = self.eth.contract(
                address=contract_address,
                abi=abi,
            )
            self._contracts[contract_address] = contract
        return self._contracts[contract_address]

    async def call_contract_function(self, contract_address, function_name, *args, **kwargs):
        contract_address = Web3.to_checksum_address(contract_address)
        contract = await self.get_contract(contract_address)
        contract_function = contract.get_function_by_name(function_name)
        result = await contract_function(*args).call(
            block_identifier=kwargs.get("block_identifier", "latest")
        )
        return result

    async def get_storage_at(self, contract_address, position, block_identifier=None):
        contract_address = Web3.to_checksum_address(contract_address)
        content = await self.eth.get_storage_at(
            contract_address, position, block_identifier=block_identifier
        )
        return content.hex()

    async def get_code(self, address):
        address = Web3.to_checksum_address(address)
        code = await self.eth.get_code(address)
        return code.hex()

    async def _yield_all_events(self, fetch_events_func, from_block, to_block):
        retries = 0
        step = self.step

        while True:
            end_block = min(from_block + step - 1, to_block)
            log.debug(
                "Fetching events from %s to %s with step %s",
                from_block,
                end_block,
                step,
            )
            try:
                async for event in fetch_events_func(from_block, end_block):
                    yield event
                retries = 0

            except Web3RPCError as e:
                # We're catching Web3RPCError as the limit for each response is either
                # 2000 blocks or 10k logs. Since our step is bigger than 2k blocks, we
                # catch the errors, and retry with smaller step (2k blocks)

                err_code = e.rpc_response["error"]["code"]
                if err_code in [-32602, -32005, -32000]:
                    if retries > 5:
                        raise

                    step /= 5
                    step = max(int(step), 2000)
                    retries += 1
                    continue
                else:
                    raise

            if end_block >= to_block:
                break

            from_block += step
            # Reset step back to self.step in case we did a retry
            step = self.step

    def _decode_raw_log(self, contract, raw_log, mixed, anonymous):
        # In order to not always instantiate new decoder, we store it under a specific
        # key directly on contract in order to cache it
        if hasattr(contract, "_ch_decoder"):
            decoder = contract._ch_decoder
        else:
            decoder = EventRawLogDecoder(contract)
            contract._ch_decoder = decoder

        return decoder.decode_log(raw_log, mixed, anonymous)

    def _generate_fetch_events_func(
        self,
        contracts,
        from_block,
        to_block,
        topics,
        anonymous,
        mixed,
    ):
        async def fetch_events_for_contracts_topics(from_block, to_block):
            filters = {
                "fromBlock": hex(from_block),
                "toBlock": hex(to_block),
                "address": contracts,
            }
            if topics:
                filters["topics"] = topics

            raw_logs = await self.eth.get_logs(filters)
            for raw_log in raw_logs:
                if (
                    HexBytes("0xbc7cd75a20ee27fd9adebab32041f755214dbc6bffa90cc0225b39da2e5c2d3b")
                    in raw_log["topics"]
                ):
                    log.warning(
                        "Skipping Upgraded event on proxy contract %s",
                        raw_log["address"],
                    )
                    continue
                # TODO: Skip BeaconUpgraded event in a similar fashion to the one above

                contract = await self.get_contract(raw_log["address"].lower())
                try:
                    data = self._decode_raw_log(contract, raw_log, mixed, anonymous)
                except MissingABIEventDecoderError:
                    log.warning(
                        "Contract ABI (%s) is missing an event definition. Fetching a "
                        "new ABI on block %s",
                        raw_log["address"].lower(),
                        raw_log["blockNumber"],
                    )
                    contract = await self.get_contract(
                        raw_log["address"].lower(),
                        refetch_on_block=raw_log["blockNumber"],
                    )
                    data = self._decode_raw_log(contract, raw_log, mixed, anonymous)

                yield data

        return fetch_events_for_contracts_topics

    def get_events_for_contract(self, contract_address, from_block, to_block=None, anonymous=False):
        return self.get_events_for_contracts(
            [contract_address], from_block, to_block=to_block, anonymous=anonymous
        )

    async def get_events_for_contracts(
        self,
        contract_addresses,
        from_block,
        to_block=None,
        anonymous=False,
        mixed=False,
    ):
        if not isinstance(contract_addresses, list):
            raise TypeError("contract_addresses must be a list")

        if not to_block:
            to_block = await self.get_latest_block()

        contracts = [
            Web3.to_checksum_address(contract_address) for contract_address in contract_addresses
        ]

        fetch_events_func = self._generate_fetch_events_func(
            contracts, from_block, to_block, None, anonymous, mixed
        )

        async for event in self._yield_all_events(fetch_events_func, from_block, to_block):
            yield event

    def get_events_for_contract_topics(
        self, contract_address, topics, from_block, to_block=None, anonymous=False
    ):
        return self.get_events_for_contracts_topics(
            [contract_address],
            topics,
            from_block,
            to_block=to_block,
            anonymous=anonymous,
        )

    async def get_events_for_contracts_topics(
        self,
        contract_addresses,
        topics,
        from_block,
        to_block=None,
        anonymous=False,
        mixed=False,
    ):
        if not isinstance(contract_addresses, list):
            raise TypeError("contract_addresses must be a list")

        if not isinstance(topics, list):
            raise TypeError("topics must be a list")

        if not to_block:
            to_block = await self.get_latest_block()

        contracts = [
            Web3.to_checksum_address(contract_address) for contract_address in contract_addresses
        ]

        fetch_events_func = self._generate_fetch_events_func(
            contracts, from_block, to_block, topics, anonymous, mixed
        )
        async for event in self._yield_all_events(fetch_events_func, from_block, to_block):
            yield event

    async def get_events_for_topics(self, topics, from_block, to_block=None, anonymous=False):
        if not isinstance(topics, list):
            raise TypeError("topics must be a list")

        if not to_block:
            to_block = await self.get_latest_block()

        async def fetch_events_for_topics_func(from_block, to_block):
            filters = {
                "fromBlock": hex(from_block),
                "toBlock": hex(to_block),
                "topics": topics,
            }

            raw_logs = await self.eth.get_logs(filters)
            for raw_log in raw_logs:
                try:
                    contract = await self.get_contract(raw_log["address"].lower())
                except ChainException:
                    log.warning("Contract not verified for %s", {raw_log["address"]})
                    continue
                if anonymous:
                    decoder = AnonymousEventLogDecoder(contract)
                else:
                    decoder = EventLogDecoder(contract)
                yield decoder.decode_log(raw_log)

        async for event in self._yield_all_events(
            fetch_events_for_topics_func, from_block, to_block
        ):
            yield event

    async def get_latest_event_before_block(self, address, topics, block_number, max_tries=5):
        step = self.step
        current_step = step
        for _ in range(max_tries):
            events = self.get_events_for_contract_topics(
                address, topics, block_number - step + 1, to_block=block_number
            )
            items = [event async for event in events]
            if items:
                return items[-1]
            step *= 2
        step = current_step
        return None

    async def multicall(self, calls, block_identifier=None, require_success=True, origin=None):
        call_objs = []
        for address, function, response in calls:
            call_objs.append(Call(address, function, returns=[response]))

        mc = Multicall(
            call_objs,
            self.w3,
            self.chain_id,
            block_identifier=block_identifier,
            require_success=require_success,
            origin=origin,
        )
        return await mc

    async def abi_to_event_topics(self, contract_address, events=None, ignore=None):
        if events and not isinstance(events, list):
            raise TypeError("events must be a list")

        contract = await self.get_contract(contract_address)
        event_abis = [
            abi
            for abi in contract.abi
            if abi["type"] == "event"
            and (events is None or abi["name"] in events)
            and (ignore is None or abi["name"] not in ignore)
        ]

        signed_abis = {f"0x{event_abi_to_log_topic(abi).hex()}": abi for abi in event_abis}
        return signed_abis

    async def get_events_topics(self, contract_address, events=None, ignore=None):
        topics = await self.abi_to_event_topics(contract_address, events=events, ignore=ignore)
        return list(topics.keys())

    async def encode_eth_call_payload(
        self, contract_address, function_name, block_identifier, args
    ):
        contract = await self.get_contract(contract_address)
        output_details = {"output_types": [], "output_names": []}
        for element in contract.abi:
            if element["type"] == "function" and element["name"] == function_name:
                for i in element["outputs"]:
                    output_details["output_types"].append(i["type"])
                    output_details["output_names"].append(i["name"])

        data = contract.encode_abi(abi_element_identifier=function_name, args=args)

        if isinstance(block_identifier, int):
            block_identifier = hex(block_identifier)

        payload = {
            "jsonrpc": "2.0",
            "params": [
                {
                    "to": contract_address,
                    "data": data,
                },
                block_identifier,
            ],
            "method": "eth_call",
        }

        return payload, output_details

    async def batch_eth_calls(self, calls):
        if len(calls) > 100:
            raise ValueError("Batch request limit exceeded (limit: 100)")

        outputs_details = {}
        payloads = []
        response = []
        request_id = 1
        for contract_address, function_name, block_identifier, args in calls:
            payload, names_types = await self.encode_eth_call_payload(
                contract_address, function_name, block_identifier, args
            )
            payload["id"] = request_id
            payloads.append(payload)
            outputs_details[request_id] = names_types
            request_id += 1

        headers = {"content-type": "application/json"}
        batch_response = await retry_post_json(self.rpc, json=payloads, headers=headers)
        for r in batch_response:
            decoded_response = eth_abi.abi.decode(
                outputs_details[r["id"]]["output_types"], bytes.fromhex(r["result"][2:])
            )
            response.append(
                dict(
                    zip(
                        outputs_details[r["id"]]["output_names"],
                        decoded_response,
                        strict=False,
                    )
                )
            )
        return response

    async def get_token_info(self, address, bytes32=False, retry=False):
        calls = []
        calls.append(
            (
                address,
                ["decimals()(uint8)"],
                ["decimals", None],
            )
        )
        if bytes32:
            calls.append(
                (
                    address,
                    ["name()(bytes32)"],
                    ["name", None],
                )
            )
        else:
            calls.append(
                (
                    address,
                    ["name()(string)"],
                    ["name", None],
                )
            )
        if bytes32:
            calls.append(
                (
                    address,
                    ["symbol()(bytes32)"],
                    ["symbol", None],
                )
            )
        else:
            calls.append(
                (
                    address,
                    ["symbol()(string)"],
                    ["symbol", None],
                )
            )

        try:
            data = await self.multicall(calls)
        except InvalidPointer:
            data = await self.get_token_info(address, bytes32=True, retry=True)
            if data["symbol"] is None:
                return data
            data["symbol"] = data["symbol"].decode("utf-8").rstrip("\x00")
            data["name"] = data["name"].decode("utf-8").rstrip("\x00")
        return data

    def get_multicall_address(self):
        return MULTICALL3_ADDRESSES[self.chain_id] if self.chain_id else None

    def chainlink_price_feed_for_asset_symbol(self, symbol):
        return get_usd_price_feed_for_asset_symbol(symbol, self.chain, self.network)

    async def get_timestamp_for_block(self, block_number):
        block_info = None
        if sink.supports_chain(self.chain):
            try:
                block_info = await sink.fetch_block_info(self.chain, block_number)
            except Exception:
                log.exception(
                    "Couldn't fetch block info from sink. Block number: %s chain: %s",
                    block_number,
                    self.chain,
                )
            if block_info:
                return block_info["timestamp"]
        return self.get_block_info(block_number).timestamp

    async def get_block_for_timestamp_fallback(self, timestamp):
        raise NotImplementedError

    async def get_block_for_timestamp(self, timestamp):
        """
        Fetches the block number for a given timestamp.

        Args:
            timestamp (int): The timestamp for which to fetch the block number.

        Returns:
            int: The block number.
        """
        nearest_block = None
        # First try to fetch the block from sink.
        if sink.supports_chain(self.chain):
            try:
                nearest_block = await sink.fetch_nearest_block(self.chain, timestamp)
            except Exception:
                log.exception(
                    "Couldn't fetch nearest block from sink. Timestamp: %s chain: %s",
                    timestamp,
                    self.chain,
                )

        # As a fallback use etherscan or other similar apis
        if not nearest_block:
            nearest_block = await self.get_block_for_timestamp_fallback(timestamp)
        return nearest_block

    async def get_owners_for_proxies(self, addresses, code):
        code_name = get_code_name(code)

        if code_name in ["GnosisSafeProxy", "Proxy", "SafeProxy"]:
            return await self.get_owners_for_gnosis_safe(addresses)
        elif code_name in [
            "AccountImplementation",
            "DSProxy",
            "Vault",
            "CenoaCustomProxy",
        ]:
            return await self.get_dsproxy_owners(addresses)
        elif code_name in ["InstaAccountV2"]:
            return await self.get_insta_account_owners(addresses)
        return {}

    async def get_owners_for_gnosis_safe(self, addresses):
        calls = []

        results = {}
        for address in addresses:
            calls.append(
                (
                    address,
                    ["getOwners()(address[])"],
                    [address, None],
                )
            )
            if len(calls) == 5000:
                data = await self.multicall(calls)
                for address, value in data.items():
                    owners = [owner.lower() for owner in value]
                    results[address] = owners
                calls = []
        if calls:
            data = await self.multicall(calls)
            for address, value in data.items():
                owners = [owner.lower() for owner in value]
                results[address] = owners
        return results

    async def get_dsproxy_owners(self, addresses):
        calls = []
        results = {}
        for address in addresses:
            calls.append(
                (
                    address,
                    ["owner()(address)"],
                    [address, None],
                )
            )
            if len(calls) == 5000:
                data = await self.multicall(calls)
                for address, value in data.items():
                    results[address] = [value.lower()]
                calls = []
        if calls:
            data = await self.multicall(calls)
            for address, value in data.items():
                results[address] = [value.lower()]
        return results

    async def get_insta_account_owners(self, addresses):
        calls = []
        accounts = {}
        for address in addresses:
            calls.append(
                (
                    "0x4c8a1BEb8a87765788946D6B19C6C6355194AbEb",
                    ["accountID(address)(uint64)", address],
                    [f"{address}", None],
                )
            )
        data = await self.multicall(calls)

        account_ids = []
        for key, value in data.items():
            account_ids.append(value)
            accounts[value] = key

        owners_mapping = {}
        calls = []
        for account_id in account_ids:
            calls.append(
                (
                    "0x4c8a1BEb8a87765788946D6B19C6C6355194AbEb",
                    ["accountLink(uint64)((address,address,uint64))", account_id],
                    [f"{account_id}", None],
                )
            )
            data = await self.multicall(calls)
            multiple_owners_insta_ids = []
            for account_id, values in data.items():
                count = values[2]
                if count > 2:
                    multiple_owners_insta_ids.append(
                        {
                            "account_id": account_id,
                            "first": values[0],
                            "last": values[1],
                            "count": count,
                        }
                    )
                else:
                    owners = []
                    for i in range(count):
                        owners.append(values[i])
                owners_mapping[int(account_id)] = owners

            for proxy in multiple_owners_insta_ids:
                count = proxy["count"]
                account_id = proxy["account_id"]
                first = proxy["first"]
                last = proxy["last"]
                owners = [proxy["first"], proxy["last"]]
                calls = []
                while len(owners) < count:
                    calls.append(
                        (
                            "0x4c8a1BEb8a87765788946D6B19C6C6355194AbEb",
                            [
                                "accountList(uint64,address)((address,address))",
                                int(account_id),
                                first,
                            ],
                            ["first", None],
                        )
                    )
                    calls.append(
                        (
                            "0x4c8a1BEb8a87765788946D6B19C6C6355194AbEb",
                            [
                                "accountList(uint64,address)((address,address))",
                                int(account_id),
                                last,
                            ],
                            ["last", None],
                        )
                    )
                    account_list = await self.multicall(calls)

                    owners.append(account_list["first"][1])
                    owners.append(account_list["last"][0])
                    owners = list(set(owners))
                    first = account_list["first"][1]
                    last = account_list["last"][0]
                owners_mapping[int(account_id)] = owners
        results = {}
        for account_id, owners in owners_mapping.items():
            results[accounts[account_id]] = owners

        return results

    async def get_multiple_erc4626_info(self, addresses, block_identifier=None):
        calls = []
        for address in addresses:
            calls.extend(
                [
                    (
                        address,
                        [
                            "name()(string)",
                        ],
                        [f"{address}::name", None],
                    ),
                    (
                        address,
                        [
                            "symbol()(string)",
                        ],
                        [f"{address}::symbol", None],
                    ),
                    (
                        address,
                        [
                            "asset()(address)",
                        ],
                        [f"{address}::asset", None],
                    ),
                    (
                        address,
                        [
                            "decimals()(uint8)",
                        ],
                        [f"{address}::decimals", None],
                    ),
                    (
                        address,
                        [
                            "totalAssets()(uint256)",
                        ],
                        [f"{address}::total_assets", None],
                    ),
                    (
                        address,
                        [
                            "totalSupply()(uint256)",
                        ],
                        [f"{address}::total_supply", None],
                    ),
                    (
                        address,
                        [
                            "convertToAssets(uint256)(uint256)",
                            10 ** (36 - 6),
                        ],
                        [f"{address}::convert_to_assets", None],
                    ),
                ]
            )

        data = await self.multicall(calls, block_identifier=block_identifier)

        result = defaultdict(dict)
        for key, value in data.items():
            address, label = key.split("::")
            result[address][label] = value
        return result

    async def get_erc4626_info(self, address, block_identifier=None):
        info = await self.get_multiple_erc4626_info([address], block_identifier=block_identifier)
        return info[address]
