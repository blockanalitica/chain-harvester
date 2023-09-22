import json
import logging
import os

import requests
from eth_utils import event_abi_to_log_topic
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from web3 import Web3
from web3.middleware import geth_poa_middleware

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

    def get_latest_block(self):
        return self.eth.get_block_number()

    def get_abi_from_source(self, contract_address):
        raise NotImplementedError

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

    def _yield_all_events(self, fetch_events_func, from_block, to_block):
        retries = 0
        step = self.step
        while True:
            log.debug(f"Fetching events from {from_block} to {to_block} with step {step}")
            end_block = min(from_block + step - 1, to_block)
            events = fetch_events_func(from_block, end_block)
            if events is None:
                break

            try:
                yield from events
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
        self, contract_addresses, from_block, to_block=None, anonymous=False
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
                if anonymous:
                    decoder = AnonymousEventLogDecoder(contract)
                else:
                    decoder = EventLogDecoder(contract)
                yield decoder.decode_log(raw_log)

        return self._yield_all_events(fetch_events_for_contracts, from_block, to_block)

    def get_events_for_contracts_topics(
        self, contract_addresses, topics, from_block, to_block=None, anonymous=False
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

    def abi_to_event_topics(self, contract_address, events=None):
        if events and not isinstance(events, list):
            raise TypeError("events must be a list")

        contract = self.get_contract(contract_address)
        event_abis = [
            abi
            for abi in contract.abi
            if abi["type"] == "event" and (events is None or abi["name"] in events)
        ]
        signed_abis = {f"0x{event_abi_to_log_topic(abi).hex()}": abi for abi in event_abis}
        return signed_abis
