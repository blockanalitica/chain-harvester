from eth_utils import event_abi_to_log_topic
from web3._utils.events import get_event_data


class EventLogDecoder:
    def __init__(self, contract):
        self._contract = contract
        event_abis = [abi for abi in self._contract.abi if abi["type"] == "event"]
        self._signed_abis = {event_abi_to_log_topic(abi): abi for abi in event_abis}

    def decode_log(self, log_entry):
        data = b"".join(log_entry["topics"] + [log_entry["data"]])
        selector = data[:32]
        func_abi = self._signed_abis[selector]

        event = get_event_data(self._contract.w3.codec, func_abi, log_entry)
        return event
