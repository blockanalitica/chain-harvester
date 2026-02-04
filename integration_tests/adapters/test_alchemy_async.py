import pytest
from chain_harvester_async.adapters.alchemy import get_blocks
from integration_tests.env import ALCHEMY_SUBGRAPH_QUERY_KEY


# TODO: i get some endpoint error, so i think i might not have correct credentials
# hence why the `skip` mark
@pytest.mark.skip(reason="Only for manual testing")
async def test_get_blocks():
    url = (
        f"https://subgraph.satsuma-prod.com/{ALCHEMY_SUBGRAPH_QUERY_KEY}"
        "/derp--93638/community/blocks-mainnet/version/v1/api"
    )
    blocks_gen = get_blocks(url, 23865575, to_block=23865600)

    blocks = [block async for block in blocks_gen]
    assert len(blocks) == 25
