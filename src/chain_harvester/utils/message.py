from eth_account import Account
from eth_account.messages import encode_defunct


def sign_message(message, private_key):
    """Sign a message using the provided private key.

    Args:
        message (str): The message to sign
        private_key (str): Ethereum private key to sign with

    Returns:
        str: The signature as a hex string
    """
    message_hash = encode_defunct(text=message)
    signed_message = Account.sign_message(message_hash, private_key)
    return signed_message.signature.to_0x_hex()
