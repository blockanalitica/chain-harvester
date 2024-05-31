from web3 import Web3


def create_index(block, tx_index, log_index):
    return "_".join((str(block).zfill(12), str(tx_index).zfill(6), str(log_index).zfill(6)))


def to_hex_topic(self, topic):
    return Web3.keccak(text=topic).hex()


def address_to_topic(self, address):
    stripped_address = address[2:]
    topic_format = "0x" + stripped_address.lower().rjust(64, "0")
    return topic_format
