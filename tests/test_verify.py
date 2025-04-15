import pytest
from eth_account import Account
from eth_account.messages import encode_defunct

from chain_harvester.verify import verify_signature


@pytest.fixture
def ethereum_account():
    # Create a test account with a known private key
    private_key = "0x0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef"
    account = Account.from_key(private_key)
    return {"private_key": private_key, "address": account.address}


def test_verify_valid_signature(ethereum_account):
    # Arrange
    message = "Test message to sign"
    private_key = ethereum_account["private_key"]
    address = ethereum_account["address"]

    # Sign the message
    message_hash = encode_defunct(text=message)
    signed_message = Account.sign_message(message_hash, private_key)
    signature = signed_message.signature.hex()

    # Act
    result = verify_signature(message, signature, address)

    # Assert
    assert result is True


def test_verify_invalid_signature(ethereum_account):
    # Arrange
    message = "Test message to sign"
    wrong_message = "Wrong message"
    private_key = ethereum_account["private_key"]
    address = ethereum_account["address"]

    # Sign a different message
    message_hash = encode_defunct(text=wrong_message)
    signed_message = Account.sign_message(message_hash, private_key)
    signature = signed_message.signature.hex()

    # Act
    result = verify_signature(message, signature, address)

    # Assert
    assert result is False


def test_verify_wrong_address(ethereum_account):
    # Arrange
    message = "Test message to sign"
    private_key = ethereum_account["private_key"]
    wrong_address = "0x1234567890123456789012345678901234567890"

    # Sign the message
    message_hash = encode_defunct(text=message)
    signed_message = Account.sign_message(message_hash, private_key)
    signature = signed_message.signature.hex()

    # Act
    result = verify_signature(message, signature, wrong_address)

    # Assert
    assert result is False


def test_verify_invalid_signature_format():
    # Arrange
    message = "Test message"
    invalid_signature = "not a valid signature"
    address = "0x1234567890123456789012345678901234567890"

    # Act
    result = verify_signature(message, invalid_signature, address)

    # Assert
    assert result is False
