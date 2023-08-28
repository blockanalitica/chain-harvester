from eth_utils import event_abi_to_log_topic
from web3._utils.abi import get_abi_input_names, get_abi_input_types, map_abi_data
from web3._utils.normalizers import BASE_RETURN_NORMALIZERS


class EventLogDecoder:
    def __init__(self, contract):
        self._contract = contract
        self._event_abis = [abi for abi in self._contract.abi if abi["type"] == "event"]
        self._signed_abis = {event_abi_to_log_topic(abi): abi for abi in self._event_abis}

    def decode_log(self, log):
        data = b"".join(log["topics"] + [log["data"]])

        selector, params = data[:32], data[32:]

        func_abi = self._signed_abis[selector]

        names = get_abi_input_names(func_abi)
        types = get_abi_input_types(func_abi)

        decoded = self._contract.w3.codec.decode(types, params)
        normalized = map_abi_data(BASE_RETURN_NORMALIZERS, types, decoded)

        decoded_data = dict(zip(names, normalized))

        log = dict(log)
        log["decoded_data"] = decoded_data
        log["event_name"] = func_abi["name"]
        return log
