from unittest.mock import patch

import pytest
import requests

from chain_harvester.multicall import Call, Multicall

TARGET = "0x0000000000000000000000000000000000000001"
CONN_RESET = requests.ConnectionError(
    "('Connection aborted.', ConnectionResetError(104, 'Connection reset by peer'))"
)
TOO_LARGE = requests.HTTPError("413 Client Error: Request Entity Too Large")


def make_calls(count):
    return [
        Call(TARGET, ["balanceOf(uint256)(uint256)", i], [[f"b{i}", None]]) for i in range(count)
    ]


def fake_aggregate(max_calls, error):
    sizes = []

    def aggregate(self, args):
        batch = args[0]
        sizes.append(len(batch))
        if len(batch) > max_calls:
            raise error
        return 0, [data for _, data in batch]

    return aggregate, sizes


@pytest.mark.parametrize("error", [CONN_RESET, TOO_LARGE])
def test_fetch_outputs_splits_failed_calls_and_keeps_order(error):
    calls = make_calls(4)
    aggregate, sizes = fake_aggregate(1, error)
    multicall = Multicall(calls, chain_id=1)

    with patch.object(Call, "__call__", aggregate):
        outputs = list(multicall.fetch_outputs())

    assert outputs == [(None, call.data) for call in calls]
    assert sizes == [4, 2, 1, 1, 2, 1, 1]


@pytest.mark.parametrize("error", [CONN_RESET, TOO_LARGE])
def test_fetch_outputs_raises_when_single_call_fails(error):
    aggregate, sizes = fake_aggregate(0, error)
    multicall = Multicall(make_calls(2), chain_id=1)

    with patch.object(Call, "__call__", aggregate), pytest.raises(type(error)):
        list(multicall.fetch_outputs())

    assert sizes == [2, 1]


def test_fetch_outputs_stops_retrying_connection_resets():
    aggregate, sizes = fake_aggregate(0, CONN_RESET)
    multicall = Multicall(make_calls(128), chain_id=1)

    with patch.object(Call, "__call__", aggregate), pytest.raises(requests.ConnectionError):
        list(multicall.fetch_outputs())

    assert sizes == [128, 64, 32, 16, 8, 4, 2]
