import pytest
from types import SimpleNamespace
from chain_harvester.constants import Network
from chain_harvester_async.multicall.call import Call
from chain_harvester_async.multicall.exceptions import StateOverrideNotSupportedError


@pytest.mark.asyncio
async def test_state_override_not_supported_raises():
    w3 = SimpleNamespace(eth=SimpleNamespace(call=None))  # never used
    call = Call(
        target="0x0000000000000000000000000000000000000000",
        function="totalSupply()(uint256)",
        w3=w3,
        chain_id=Network.Gnosis,  # in NO_STATE_OVERRIDE
        state_override_code="0xdeadbeef",
    )
    with pytest.raises(StateOverrideNotSupportedError):
        await call.coroutine()
