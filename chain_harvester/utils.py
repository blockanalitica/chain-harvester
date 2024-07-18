from decimal import Decimal, getcontext

from web3 import Web3

from .constants import RAY

# interest bearing math
getcontext().prec = 50


def create_index(block, tx_index, log_index):
    return "_".join((str(block).zfill(12), str(tx_index).zfill(6), str(log_index).zfill(6)))


def to_hex_topic(topic):
    return Web3.keccak(text=topic).hex()


def address_to_topic(address):
    stripped_address = address[2:]
    topic_format = "0x" + stripped_address.lower().rjust(64, "0")
    return topic_format


def ray_div(a, b):
    a = Decimal(str(a))
    b = Decimal(str(b))
    half_b = b // Decimal("2")
    result = (a * RAY + half_b) // b if a >= 0 else -(((-a) * RAY + half_b) // b)
    return result


def normalize_to_decimal(value, decimals):
    if value is None:
        return None
    return Decimal(str(value)) / Decimal(str(10**decimals))
