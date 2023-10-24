import binascii

from Crypto.Hash import keccak
from eth_utils import event_abi_to_log_topic, to_int
from web3 import Web3
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


class AnonymousEventLogDecoder:
    def __init__(self, contract):
        self._contract = contract
        self._signed_abis = self.map_abi(self._contract.abi)

    def map_abi(self, abi):
        mapping = {}
        mapping.setdefault("events", {"anonymous": {}, "non-anonymous": {}})
        mapping.setdefault("functions", {})
        for element in abi:
            if element["type"] == "function" and element["inputs"]:
                e = f"{element['name']}({','.join([inp['type'] for inp in element['inputs']])})"
                keccak256 = keccak.new(data=e.encode("utf-8"), digest_bits=256).digest()
                mapping["functions"].setdefault(
                    ("0x" + binascii.hexlify(keccak256).decode("utf-8"))[:10].ljust(66, "0"),
                    {},
                )
                mapping["functions"][
                    ("0x" + binascii.hexlify(keccak256).decode("utf-8"))[:10].ljust(66, "0")
                ]["name"] = element["name"]
                mapping["functions"][
                    ("0x" + binascii.hexlify(keccak256).decode("utf-8"))[:10].ljust(66, "0")
                ]["inputs"] = element["inputs"]
            elif element["type"] == "event" and element["anonymous"]:
                mapping["events"]["anonymous"].setdefault("inputs", element["inputs"])
                mapping["events"]["anonymous"].setdefault("name", element["name"])
            elif element["type"] == "event" and not element["anonymous"]:
                mapping["events"]["non-anonymous"].setdefault(element["name"], element["inputs"])
            else:
                pass

        return mapping

    def decode_log(self, log_entry):
        ARG_KEYS = ["arg1", "arg2", "arg3", "arg4", "arg5", "arg6"]
        DATA_SKIP_BYTES = 138

        topics = log_entry["topics"]
        data = log_entry["data"].hex()
        event_attributes = self._signed_abis["events"]["anonymous"]["inputs"]
        event_layout = {}
        for idx, attribute in enumerate(event_attributes):
            # skip all arg-like attributes as they're not always matching
            # the data types defined in event specification in ABI
            if attribute["indexed"] and attribute["name"] not in ARG_KEYS:
                event_layout.setdefault(
                    attribute["name"],
                    decode_value(value=topics[idx], value_type=attribute["type"]),
                )

        # drop all arg-like topics / just to make sure we got rid of these
        delete = [key for key in event_layout if key in ARG_KEYS]
        [event_layout.pop(key) for key in delete]

        # decode event data using function arguments from abi
        # skip 0x, first two sets of bytes and function signature (2 + 64 + 64 + 8)
        data = data[DATA_SKIP_BYTES:]
        parse_from = 0
        for arg in self._signed_abis["functions"][topics[0].hex()]["inputs"]:
            event_layout.setdefault(
                arg["name"],
                decode_value(value=data[parse_from : parse_from + 64], value_type=arg["type"]),
            )
            parse_from += 64

        item = dict(log_entry)

        item["args"] = {
            "event_name": self._signed_abis["events"]["anonymous"]["name"],
            "event_layout": event_layout,
            "executed_function": self._signed_abis["functions"][topics[0].hex()]["name"],
        }
        return item


def bytes4_to_str(value):
    value = value.hex()
    if value[:2] == "0x":
        value = value[2:]
    return "0x" + value[:8]


def bytes32_to_str(value):
    try:
        return Web3.to_text(value).strip("\x00")
    except UnicodeDecodeError:
        try:
            return int.from_bytes(value, "big")
        except TypeError:
            return int(value, 16)


def address_to_str(value):
    if isinstance(value, str):
        return "0x" + value[-40:]
    else:
        return "0x" + value.hex()[-40:]


def bytes_to_str(value):
    if value[:2] == "0x":
        value = value[2:]
    return "0x" + value


def uint256_to_int(value):
    return to_int(hexstr=value)


def int256_to_int(value):
    # if negative int
    if value[0].lower() in ["8", "9", "a", "b", "c", "d", "e", "f"]:
        return int(value, 16) - 2**256
    else:
        return int(value, 16)


def decode_value(value, value_type):
    if value_type == "bytes":
        return bytes_to_str(value)
    elif value_type == "bytes4":
        return bytes4_to_str(value)
    elif value_type == "bytes32":
        return bytes32_to_str(value)
    elif value_type == "address":
        return address_to_str(value)
    elif value_type == "uint256":
        return uint256_to_int(value)
    elif value_type == "int256":
        return int256_to_int(value)
    else:
        raise Exception(f"Unable to decode {value_type} data type; value: {value}")  # noqa: TRY002
