import pytest

from chain_harvester.adapters.alchemy_chain import AlchemyChain
from integration_tests.constants import USDT_CONTRACT


async def test_batch_codes():
    alchemy = AlchemyChain("ethereum")
    data = await alchemy.get_batch_codes(["0xe8e8f41ed29e46f34e206d7d2a7d6f735a3ff2cb"])
    assert data == ["0x"]


async def test_get_block_transactions():
    alchemy = AlchemyChain("ethereum")
    data = await alchemy.get_block_transactions(23865575)
    assert len(data) == 184


@pytest.mark.skip(reason="Only for manual testing")
async def test_get_transactions_for_contracts():
    alchemy = AlchemyChain("ethereum")

    transactions = alchemy.get_transactions_for_contracts(
        [USDT_CONTRACT], 23865575, 23865575
    )
    all_transactions = [transaction async for transaction in transactions]

    assert len(all_transactions) == 24
