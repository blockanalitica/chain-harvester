from web3 import Web3

from chain_harvester.networks.ethereum.mainnet import EthereumMainnetChain
from intregration_tests.env import API_KEYS, RPC_NODES


def test__call_contract_function():
    chain = EthereumMainnetChain(rpc=RPC_NODES["ethereum"]["mainnet"], api_keys=API_KEYS)

    assert chain.rpc == RPC_NODES["ethereum"]["mainnet"]
    name = chain.call_contract_function("0x6b175474e89094c44da98b954eedeac495271d0f", "name")
    assert name == "Dai Stablecoin"


def test__load_abi():
    chain = EthereumMainnetChain(
        rpc=RPC_NODES["ethereum"]["mainnet"], api_keys=API_KEYS, abis_path="test-abis/"
    )
    abi = chain.load_abi("0x6b175474e89094c44da98b954eedeac495271d0f")
    abi_name = chain.load_abi("0x6b175474e89094c44da98b954eedeac495271d0f", abi_name="token")
    assert abi == abi_name


def test__get_events_for_contract():
    chain = EthereumMainnetChain(rpc_nodes=RPC_NODES, api_keys=API_KEYS)

    events = chain.get_events_for_contract(
        "0x6b175474e89094c44da98b954eedeac495271d0f",
        from_block=17850969,
        to_block=17850974,
    )

    assert len(list(events)) == 3


def test__get_events_for_contract_topics():
    chain = EthereumMainnetChain(rpc_nodes=RPC_NODES, api_keys=API_KEYS)

    events = chain.get_events_for_contract_topics(
        "0x6b175474e89094c44da98b954eedeac495271d0f",
        ["0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"],
        from_block=17850969,
        to_block=17850974,
    )
    assert len(list(events)) == 3


def test__multicall():
    chain = EthereumMainnetChain(rpc_nodes=RPC_NODES, api_keys=API_KEYS)

    calls = []
    calls.append(
        (
            "0x6b175474e89094c44da98b954eedeac495271d0f",
            ["symbol()(string)"],
            ["symbol", None],
        )
    )
    calls.append(
        (
            "0x6b175474e89094c44da98b954eedeac495271d0f",
            ["name()(string)"],
            ["name", None],
        )
    )
    result = chain.multicall(calls)
    assert result["symbol"] == "DAI"
    assert result["name"] == "Dai Stablecoin"


def test__anonymous_events():
    chain = EthereumMainnetChain(rpc_nodes=RPC_NODES, api_keys=API_KEYS)
    contract_address = "0x35D1b3F3D7966A1DFe207aa4514C12a259A0492B"

    topics = ["0xb65337df00000000000000000000000000000000000000000000000000000000"]

    events = chain.get_events_for_contract_topics(
        contract_address,
        topics,
        from_block=18163919,
        to_block=18163920,
        anonymous=True,
    )

    assert len(list(events)) == 1


def test__encode_eth_call_payload():
    chain = EthereumMainnetChain(rpc_nodes=RPC_NODES, api_keys=API_KEYS)
    block_identifier = 17892782

    response = chain.eth_multicall(
        [["0x6D635c8d08a1eA2F1687a5E46b666949c977B7dd", "accrued", block_identifier, [1]]]
    )
    assert response == [{"amt": 700000000000000000000}]

    ilk = Web3.to_bytes(text="ETH-A").ljust(32, b"\x00")
    urn = Web3.to_checksum_address("0x526e31defe9e23dc540d955839825b20c90332f9")
    response = chain.eth_multicall(
        [
            [
                "0x35D1b3F3D7966A1DFe207aa4514C12a259A0492B".lower(),
                "urns",
                block_identifier,
                [ilk, urn],
            ]
        ]
    )
    assert response == [{"ink": 42500000000000000000, "art": 13890243153162300485451}]
