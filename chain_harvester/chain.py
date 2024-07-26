import json
import logging
import os

import eth_abi
import requests
from eth_utils import event_abi_to_log_topic
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from web3 import Web3
from web3.middleware import geth_poa_middleware

from chain_harvester.chainlink import get_usd_price_feed_for_asset_symbol
from chain_harvester.constants import MULTICALL3_ADDRESSES
from chain_harvester.decoders import AnonymousEventLogDecoder, EventLogDecoder
from chain_harvester.multicall import Call, Multicall

log = logging.getLogger(__name__)


class ChainException(Exception):
    pass


class Chain:
    def __init__(
        self,
        rpc=None,
        w3=None,
        step=None,
        chain_id=None,
        rpc_nodes=None,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.rpc = rpc
        self._w3 = w3
        self.step = step or 10_000
        self.provider = rpc

        self.chain_id = chain_id
        self.rpc_nodes = rpc_nodes

        self._abis = {}
        self.current_block = 0

        self.chain = None
        self.network = None

    @property
    def w3(self):
        if not self._w3:
            session = requests.Session()
            retries = 3
            retry = Retry(
                total=retries,
                read=retries,
                connect=retries,
                backoff_factor=0.5,
                status_forcelist=(429,),
                respect_retry_after_header=True,
            )
            adapter = HTTPAdapter(max_retries=retry)
            session.mount("http://", adapter)
            session.mount("https://", adapter)

            self._w3 = Web3(
                Web3.HTTPProvider(self.rpc, request_kwargs={"timeout": 60}, session=session)
            )
            self._w3.middleware_onion.inject(geth_poa_middleware, layer=0)
        return self._w3

    @property
    def eth(self):
        return self.w3.eth

    def get_block_info(self, block_number):
        return self.eth.get_block(block_number)

    def get_latest_block(self, true_latest=False):
        if true_latest:
            return self.eth.get_block_number()
        return self.eth.get_block_number() - 5

    def get_abi_source_url(self, contract_address):
        raise NotImplementedError

    def get_abi_from_source(self, contract_address):
        log.error(
            "ABI for %s was fetched from etherscan. Add it to abis folder!",
            contract_address,
        )
        try:
            response = requests.get(
                self.get_abi_source_url(contract_address),
                timeout=5,
            )
        except requests.exceptions.Timeout:
            log.exception(
                "Timeout when get abi from etherscan",
                extra={"contract_address": contract_address},
            )
            raise

        response.raise_for_status()
        data = response.json()

        if data["status"] != "1":
            raise ChainException("Request to etherscan failed: {}".format(data["result"]))

        abi = json.loads(data["result"])
        return abi

    def load_abi(self, contract_address, abi_name=None):
        contract_address = contract_address.lower()
        abi_address = abi_name or contract_address
        if contract_address not in self._abis:
            file_path = os.path.join(self.abis_path, f"{abi_address}.json")
            if os.path.exists(file_path):
                with open(file_path) as f:
                    self._abis[contract_address] = json.loads(f.read())
            else:
                if not os.path.isdir(self.abis_path):
                    os.mkdir(self.abis_path)
                proxy_contract = self.get_implementation_address(contract_address)
                if proxy_contract != "0x0000000000000000000000000000000000000000":
                    abi = self.get_abi_from_source(proxy_contract)
                else:
                    abi = self.get_abi_from_source(contract_address)
                with open(file_path, "w") as f:
                    json.dump(abi, f)
                self._abis[contract_address] = abi
        return self._abis[contract_address]

    def get_implementation_address(self, contract_address):
        # EIP-1967 storage slot
        contract_address = Web3.to_checksum_address(contract_address)
        slot = "0x360894a13ba1a3210667c828492db98dca3e2076cc3735a920a3ca505d382bbc"
        impl_address = self.eth.get_storage_at(contract_address, int(slot, 16)).hex()
        return Web3.to_checksum_address(impl_address[-40:])

    def get_contract(self, contract_address):
        if Web3.is_address(contract_address):
            contract_address = Web3.to_checksum_address(contract_address)
        abi = self.load_abi(contract_address)
        return self.eth.contract(address=contract_address, abi=abi)

    def call_contract_function(self, contract_address, function_name, *args, **kwargs):
        contract_address = Web3.to_checksum_address(contract_address)
        contract = self.get_contract(contract_address)
        contract_function = contract.get_function_by_name(function_name)
        result = contract_function(*args).call(
            block_identifier=kwargs.get("block_identifier", "latest")
        )
        return result

    def get_storage_at(self, contract_address, position, block_identifier=None):
        contract_address = Web3.to_checksum_address(contract_address)
        content = self.eth.get_storage_at(
            contract_address, position, block_identifier=block_identifier
        ).hex()
        return content

    def get_code(self, address):
        address = Web3.to_checksum_address(address)
        return self.eth.get_code(address).hex()

    def is_eoa(self, address):
        return self.eth.get_code(address) == "0x"

    def _yield_all_events(self, fetch_events_func, from_block, to_block):
        retries = 0
        step = self.step
        while True:
            end_block = min(from_block + step - 1, to_block)
            log.debug(f"Fetching events from {from_block} to {end_block} with step {step}")
            events = fetch_events_func(from_block, end_block)
            if events is None:
                break

            try:
                yield from events
                retries = 0
            except ValueError as e:
                # We're catching ValueError as the limit for each response is either
                # 2000 blocks or 10k logs. Since our step is bigger than 2k blocks, we
                # catch the errors, and retry with smaller step (2k blocks)
                err_code = None
                if len(e.args) > 0 and isinstance(e.args[0], dict):
                    err_code = e.args[0]["code"]

                if err_code in [-32602, -32005, -32000]:
                    if retries > 5:
                        raise

                    step /= 5
                    step = int(step)
                    retries += 1
                    continue
                else:
                    raise

            if end_block >= to_block:
                break

            from_block += step
            # Reset step back to self.step in case we did a retry
            step = self.step

    def get_events_for_contract(self, contract_address, from_block, to_block=None, anonymous=False):
        if not to_block:
            to_block = self.get_latest_block()
        contract_address = Web3.to_checksum_address(contract_address)
        contract = self.get_contract(contract_address)
        decoder = AnonymousEventLogDecoder(contract) if anonymous else EventLogDecoder(contract)

        def fetch_events_for_contract(from_block, to_block):
            filters = {
                "fromBlock": hex(from_block),
                "toBlock": hex(to_block),
                "address": contract_address,
            }
            raw_logs = self.eth.get_logs(filters)
            for raw_log in raw_logs:
                yield decoder.decode_log(raw_log)

        return self._yield_all_events(fetch_events_for_contract, from_block, to_block)

    def get_events_for_contract_topics(
        self, contract_address, topics, from_block, to_block=None, anonymous=False
    ):
        contract_address = Web3.to_checksum_address(contract_address)
        if not isinstance(topics, list):
            raise TypeError("topics must be a list")

        if not to_block:
            to_block = self.get_latest_block()

        contract = self.get_contract(contract_address)

        decoder = AnonymousEventLogDecoder(contract) if anonymous else EventLogDecoder(contract)

        def fetch_events_for_contract_topics(from_block, to_block):
            filters = {
                "fromBlock": hex(from_block),
                "toBlock": hex(to_block),
                "address": contract_address,
                "topics": topics,
            }

            raw_logs = self.eth.get_logs(filters)
            for raw_log in raw_logs:
                yield decoder.decode_log(raw_log)

        return self._yield_all_events(fetch_events_for_contract_topics, from_block, to_block)

    def get_events_for_contracts(
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
            to_block = self.get_latest_block()

        contracts = [
            Web3.to_checksum_address(contract_address) for contract_address in contract_addresses
        ]

        def fetch_events_for_contracts(from_block, to_block):
            filters = {
                "fromBlock": hex(from_block),
                "toBlock": hex(to_block),
                "address": contracts,
            }
            raw_logs = self.eth.get_logs(filters)
            for raw_log in raw_logs:
                contract = self.get_contract(raw_log["address"].lower())
                if mixed:
                    try:
                        decoder = EventLogDecoder(contract)
                        data = decoder.decode_log(raw_log)
                        yield data
                    except KeyError:
                        decoder = AnonymousEventLogDecoder(contract)
                        data = decoder.decode_log(raw_log)
                        yield data
                else:
                    if anonymous:
                        decoder = AnonymousEventLogDecoder(contract)
                    else:
                        decoder = EventLogDecoder(contract)
                    yield decoder.decode_log(raw_log)

        return self._yield_all_events(fetch_events_for_contracts, from_block, to_block)

    def get_events_for_contracts_topics(
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
            to_block = self.get_latest_block()

        contracts = [
            Web3.to_checksum_address(contract_address) for contract_address in contract_addresses
        ]

        def fetch_events_for_contracts_topics(from_block, to_block):
            filters = {
                "fromBlock": hex(from_block),
                "toBlock": hex(to_block),
                "address": contracts,
                "topics": topics,
            }
            raw_logs = self.eth.get_logs(filters)
            for raw_log in raw_logs:
                contract = self.get_contract(raw_log["address"].lower())
                if mixed:
                    try:
                        decoder = EventLogDecoder(contract)
                        data = decoder.decode_log(raw_log)
                        yield data
                    except KeyError:
                        decoder = AnonymousEventLogDecoder(contract)
                        data = decoder.decode_log(raw_log)
                        yield data
                else:
                    if anonymous:
                        decoder = AnonymousEventLogDecoder(contract)
                    else:
                        decoder = EventLogDecoder(contract)
                    yield decoder.decode_log(raw_log)

        return self._yield_all_events(fetch_events_for_contracts_topics, from_block, to_block)

    def get_events_for_topics(self, topics, from_block, to_block=None, anonymous=False):
        if not isinstance(topics, list):
            raise TypeError("topics must be a list")

        if not to_block:
            to_block = self.get_latest_block()

        def fetch_events_for_topics(from_block, to_block):
            filters = {
                "fromBlock": hex(from_block),
                "toBlock": hex(to_block),
                "topics": topics,
            }

            raw_logs = self.eth.get_logs(filters)
            for raw_log in raw_logs:
                contract = self.get_contract(raw_log["address"].lower())
                if anonymous:
                    decoder = AnonymousEventLogDecoder(contract)
                else:
                    decoder = EventLogDecoder(contract)
                yield decoder.decode_log(raw_log)

        return self._yield_all_events(fetch_events_for_topics, from_block, to_block)

    def multicall(self, calls, block_identifier=None):
        multicalls = []
        for address, function, response in calls:
            multicalls.append(Call(address, function, [response]))

        multi = Multicall(multicalls, self.chain_id, _w3=self.w3, block_identifier=block_identifier)

        return multi()

    def abi_to_event_topics(self, contract_address, events=None, ignore=None):
        if events and not isinstance(events, list):
            raise TypeError("events must be a list")

        contract = self.get_contract(contract_address)
        event_abis = [
            abi
            for abi in contract.abi
            if abi["type"] == "event"
            and (events is None or abi["name"] in events)
            and (ignore is None or abi["name"] not in ignore)
        ]
        signed_abis = {f"0x{event_abi_to_log_topic(abi).hex()}": abi for abi in event_abis}
        return signed_abis

    def get_events_topics(self, contract_address, events=None, ignore=None):
        return list(self.abi_to_event_topics(contract_address, events=events, ignore=ignore).keys())

    def address_to_topic(self, address):
        stripped_address = address[2:]
        topic_format = "0x" + stripped_address.lower().rjust(64, "0")
        return topic_format

    def encode_eth_call_payload(self, contract_address, function_name, block_identifier, args):
        contract = self.get_contract(contract_address)
        output_details = {"output_types": [], "output_names": []}
        for element in contract.abi:
            if element["type"] == "function" and element["name"] == function_name:
                for i in element["outputs"]:
                    output_details["output_types"].append(i["type"])
                    output_details["output_names"].append(i["name"])

        data = contract.encodeABI(fn_name=function_name, args=args)

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

    def batch_eth_calls(self, data):
        headers = {"content-type": "application/json"}
        response = requests.post(self.rpc, json=data, headers=headers, timeout=60)
        response.raise_for_status()
        return response.json()

    def eth_multicall(self, calls):
        if len(calls) > 100:
            raise ValueError("Batch request limit exceeded (limit: 100)")

        outputs_details = {}
        payloads = []
        response = []
        request_id = 1
        for contract_address, function_name, block_identifier, args in calls:
            payload, names_types = self.encode_eth_call_payload(
                contract_address, function_name, block_identifier, args
            )
            payload["id"] = request_id
            payloads.append(payload)
            outputs_details[request_id] = names_types
            request_id += 1
        batch_response = self.batch_eth_calls(payloads)
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

    def to_hex_topic(self, topic):
        return Web3.keccak(text=topic).hex()

    def get_token_info(self, address, bytes32=False):
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
        data = self.multicall(calls)
        if data["symbol"] is None:
            data = self.get_token_info(address, bytes32=True)
            data["symbol"] = data["symbol"].decode("utf-8").rstrip("\x00")
            data["name"] = data["name"].decode("utf-8").rstrip("\x00")
        return data

    def get_multicall_address(self):
        return MULTICALL3_ADDRESSES[self.chain_id] if self.chain_id else None

    def create_index(self, block, tx_index, log_index):
        return "_".join((str(block).zfill(12), str(tx_index).zfill(6), str(log_index).zfill(6)))

    def chainlink_price_feed_for_asset_symbol(self, symbol):
        return get_usd_price_feed_for_asset_symbol(symbol, self.chain, self.network)
