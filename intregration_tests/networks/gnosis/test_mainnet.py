from chain_harvester.networks.gnosis.mainnet import GnosisMainnetChain
from intregration_tests.env import API_KEYS, RPC_NODES


def test__call_contract_function():
    chain = GnosisMainnetChain(rpc=RPC_NODES["gnosis"]["mainnet"], api_keys=API_KEYS)

    assert chain.rpc == RPC_NODES["gnosis"]["mainnet"]
    name = chain.call_contract_function("0xe91d153e0b41518a2ce8dd3d7944fa863463a97d", "name")
    assert name == "Wrapped XDAI"


def test__get_events_for_contract():
    chain = GnosisMainnetChain(rpc_nodes=RPC_NODES, api_keys=API_KEYS)

    events = chain.get_events_for_contract(
        "0xe91d153e0b41518a2ce8dd3d7944fa863463a97d",
        from_block=29718440,
        to_block=29718445,
    )

    assert len(list(events)) == 10


def test__get_events_for_contract_topics():
    chain = GnosisMainnetChain(rpc_nodes=RPC_NODES, api_keys=API_KEYS)

    events = chain.get_events_for_contract_topics(
        "0xe91d153e0b41518a2ce8dd3d7944fa863463a97d",
        ["0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"],
        from_block=29718440,
        to_block=29718445,
    )
    assert len(list(events)) == 6


def test__multicall():
    chain = GnosisMainnetChain(rpc_nodes=RPC_NODES, api_keys=API_KEYS)

    calls = []
    calls.append(
        (
            "0xe91d153e0b41518a2ce8dd3d7944fa863463a97d",
            ["symbol()(string)"],
            ["symbol", None],
        )
    )
    calls.append(
        (
            "0xe91d153e0b41518a2ce8dd3d7944fa863463a97d",
            ["name()(string)"],
            ["name", None],
        )
    )
    result = chain.multicall(calls)
    assert result["symbol"] == "WXDAI"
    assert result["name"] == "Wrapped XDAI"


def test__multicall__history():
    chain = GnosisMainnetChain(rpc_nodes=RPC_NODES, api_keys=API_KEYS)

    calls = []
    calls.append(
        (
            "0xe91d153e0b41518a2ce8dd3d7944fa863463a97d",
            ["balanceOf(address)(uint256)", "0xe91d153e0b41518a2ce8dd3d7944fa863463a97d"],
            ["balanceOf", None],
        )
    )
    result = chain.multicall(calls, block_identifier=29719907)
    assert result["balanceOf"] == 17779092364971360576215

    calls = []
    calls.append(
        (
            "0xe91d153e0b41518a2ce8dd3d7944fa863463a97d",
            ["balanceOf(address)(uint256)", "0xe91d153e0b41518a2ce8dd3d7944fa863463a97d"],
            ["balanceOf", None],
        )
    )
    result = chain.multicall(calls, block_identifier=27719907)
    assert result["balanceOf"] == 17766592364971360576215
