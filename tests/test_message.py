import pytest
from eth_account import Account
from eth_account.messages import encode_defunct

from chain_harvester.message import sign_message, verify_signature


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


def test_sign_message(ethereum_account):
    # Arrange
    message = "Test message to sign"
    private_key = ethereum_account["private_key"]
    address = ethereum_account["address"]

    # Act
    signature = sign_message(message, private_key)

    # Assert
    # Verify the signature matches what we'd expect
    result = verify_signature(message, signature, address)
    assert result is True

    # Also check it's a valid hex string of the expected length for a signature
    assert signature.startswith("0x")
    assert len(signature) > 2  # More than just "0x"


def test_sign_and_verify_message_flow(ethereum_account):
    # Arrange
    message = "Important message that needs signing"
    private_key = ethereum_account["private_key"]
    address = ethereum_account["address"]

    # Act - Sign message
    signature = sign_message(message, private_key)

    # Act - Verify signature
    is_valid = verify_signature(message, signature, address)

    # Assert
    assert is_valid is True
