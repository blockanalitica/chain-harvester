import inspect
import json
import logging
import os

import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from web3 import Web3
from web3.middleware import geth_poa_middleware

log = logging.getLogger(__name__)


class Chain:
    def __init__(
        self,
        rpc=None,
        chain=None,
        step=None,
        etherscan_api_key=None,
        abis_path=None,
        chain_id=None,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.rpc = rpc
        self._chain = chain
        self.step = step or 10_000
        self.provider = rpc
        self.etherscan_api_key = etherscan_api_key
        self.abis_path = abis_path
        self.chain_id = chain_id

        self._abis = {}
        self.current_block = 0
        self.retry = 0

    @property
    def chain(self):
        if not self._chain:
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

            self._chain = Web3(
                Web3.HTTPProvider(
                    self.rpc, request_kwargs={"timeout": 60}, session=session
                )
            )
            self._chain.middleware_onion.inject(geth_poa_middleware, layer=0)
        return self._chain

    @property
    def eth(self):
        return self.chain.eth

    def get_block_info(self, block_number):
        return self.eth.get_block(block_number)

    def get_latest_block(self):
        return self.eth.get_block_number()

    def get_abi_from_etherscan(self, contract_address):
        req = requests.get(
            "https://api.etherscan.io/api?module=contract&action=getabi&address="
            + contract_address
            + "&apikey="
            + self.etherscan_api_key
        )
        resp = json.loads(req.text)
        abi = json.loads(resp["result"])
        return abi

    def load_abi(self, contract_address):
        contract_address = contract_address.lower()
        if contract_address not in self._abis:
            if not os.path.exists(self.abis_path):
                os.makedirs(self.abis_path)
            current_file_path = inspect.getfile(inspect.currentframe())
            current_directory = os.path.dirname(os.path.abspath(current_file_path))
            file_path = os.path.join(
                current_directory, "abis", f"{contract_address}.json"
            )
            if os.path.exists(file_path):
                with open(file_path, "r") as f:
                    self._abis[contract_address] = json.loads(f.read())
            else:
                abi = self.get_abi_from_etherscan(contract_address)

                with open(file_path, "w") as f:
                    json.dump(abi, f)
                with open(file_path, "r") as f:
                    self._abis[contract_address] = json.loads(f.read())
        return self._abis[contract_address]

    def get_contract(self, contract_address):
        if Web3.is_address(contract_address):
            contract_address = Web3.to_checksum_address(contract_address)
        abi = self.load_abi(contract_address)
        return self.chain.eth.contract(address=contract_address, abi=abi)

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

    def _yield_events(self, fetch_events_func, from_block, to_block=None):
        self.current_block = 0
        if not to_block:
            to_block = self.get_latest_block()

        start_block = from_block
        while True:
            end_block = min(start_block + self.step - 1, to_block)
            events = fetch_events_func(start_block, end_block, self.step)
            if events is None:
                break
            else:
                yield events
            if self.current_block >= to_block:
                break
            start_block = self.current_block

    def _return_events_with_retry(
        self, fetch_events_func, start_block, end_block, step, extra_log
    ):
        MAX_RETRIES = 3
        retry = 0
        while retry <= MAX_RETRIES:
            try:
                events = fetch_events_func(start_block, end_block, step)
                self.current_block = end_block
                return events
            except ValueError as e:
                msg = e.args[0]
                if isinstance(msg, dict) and msg["code"] in [-32602, -32005, -32000]:
                    step /= 5
                    end_block = int(start_block + step - 1)
                    continue
                else:
                    log_extra = {
                        "stack": True,
                        "start_block": start_block,
                        "end_block": end_block,
                        "step": step,
                        "exception": e,
                        "retry": retry,
                        **extra_log,
                    }
                    if retry == MAX_RETRIES:
                        log.error(msg, extra=log_extra)
                        return None
                    else:
                        log.warning(msg, extra=log_extra)
                        retry += 1
        return None

    ### Topics

    def _return_events_by_topics(
        self, contract_address, topics, start_block, end_block, step
    ):
        filters = {
            "fromBlock": start_block,
            "toBlock": end_block,
            "address": contract_address,
            "topics": topics,
        }
        events = self.eth.get_logs(filters)
        return events

    def _return_events_by_topic_with_retry(
        self, contract_address, topics, start_block, end_block, step, extra_log
    ):
        def fetch_events_func(start_block, end_block, step):
            return self._return_events_by_topics(
                contract_address, topics, start_block, end_block, step
            )

        return self._return_events_with_retry(
            fetch_events_func, start_block, end_block, step, extra_log
        )

    def yield_contract_events_by_topic(
        self, contract_address, topics, from_block, to_block=None
    ):
        contract_address = Web3.to_checksum_address(contract_address)

        def fetch_events_func(start_block, end_block, step):
            return self._return_events_by_topic_with_retry(
                contract_address,
                topics,
                start_block,
                end_block,
                step,
                extra_log={"topics": topics, "contract_address": contract_address},
            )

        return self._yield_events(fetch_events_func, from_block, to_block)

    ### Event Attr

    def _return_contract_events(
        self, contract, event_attr, start_block, end_block, step
    ):
        attr = contract.events
        cls = getattr(attr, event_attr)
        caller = cls.create_filter
        events = caller(fromBlock=start_block, toBlock=end_block)
        entries = events.get_all_entries()
        return entries

    def _return_contract_events_with_retry(
        self, contract, event_attr, start_block, end_block, step, extra_log
    ):
        def fetch_events_func(start_block, end_block, step):
            return self._return_contract_events(
                contract, event_attr, start_block, end_block, step
            )

        return self._return_events_with_retry(
            fetch_events_func,
            start_block,
            end_block,
            step,
            extra_log={"contract": contract, "event_attr": event_attr, **extra_log},
        )

    def yield_contract_events(
        self, contract_address, event_attr, from_block, to_block=None, **kwargs
    ):
        abi_address = kwargs.get("abi_type", contract_address)
        contract = self.get_contract(abi_address)

        def fetch_events_func(start_block, end_block, step):
            return self._return_contract_events_with_retry(
                contract,
                event_attr,
                start_block,
                end_block,
                step,
                extra_log={
                    "event_attr": event_attr,
                    "contract_address": contract.address,
                },
            )

        return self._yield_events(fetch_events_func, from_block, to_block)