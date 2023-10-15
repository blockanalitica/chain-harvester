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


def test__anonymous_events_decode():
    chain = EthereumMainnetChain(rpc_nodes=RPC_NODES, api_keys=API_KEYS)
    contract_address = "0x35D1b3F3D7966A1DFe207aa4514C12a259A0492B"

    topics = ["0x1a0b287e00000000000000000000000000000000000000000000000000000000"]

    events = chain.get_events_for_contract_topics(
        contract_address,
        topics,
        from_block=18350654,
        to_block=18350656,
        anonymous=True,
    )

    assert len(list(events)) == 2


def test__anonymous_events_fold():
    chain = EthereumMainnetChain(rpc_nodes=RPC_NODES, api_keys=API_KEYS)
    contract_address = "0x35D1b3F3D7966A1DFe207aa4514C12a259A0492B"

    topics = ["0xb65337df00000000000000000000000000000000000000000000000000000000"]

    events = chain.get_events_for_contract_topics(
        contract_address,
        topics,
        from_block=18349061,
        to_block=18349063,
        anonymous=True,
    )

    assert len(list(events)) == 1


def test__mixed_events():
    chain = EthereumMainnetChain(rpc_nodes=RPC_NODES, api_keys=API_KEYS)
    contract_address = "0x135954d155898D42C90D2a57824C690e0c7BEf1B"

    topics = [
        "0x54f095dc7308776bf01e8580e4dd40fd959ea4bf50b069975768320ef8d77d8a",
        "0x851aa1caf4888170ad8875449d18f0f512fd6deb2a6571ea1a41fb9f95acbcd1",
    ]

    events = chain.get_events_for_contracts_topics(
        [contract_address],
        [topics],
        from_block=17322549,
        to_block=17322851,
        mixed=True,
    )
    assert len(list(events)) == 14


def test__mixed_events_contracts():
    chain = EthereumMainnetChain(rpc_nodes=RPC_NODES, api_keys=API_KEYS)
    contracts = [
        "0x135954d155898D42C90D2a57824C690e0c7BEf1B",
        "0xC7Bdd1F2B16447dcf3dE045C4a039A60EC2f0ba3",
        "0xBB856d1742fD182a90239D7AE85706C2FE4e5922",
        "0x09e05fF6142F2f9de8B6B65855A1d56B6cfE4c58",
        "0x60744434d6339a6B27d73d9Eda62b6F66a0a04FA",
        "0xbE286431454714F511008713973d3B053A2d38f3",
        "0xa4f79bC4a5612bdDA35904FDF55Fc4Cb53D1BFf6",
        "0xA41B6EF151E06da0e34B009B86E828308986736D",
        "0x35D1b3F3D7966A1DFe207aa4514C12a259A0492B",
        "0xA950524441892A31ebddF91d3cEEFa04Bf454466",
        "0x65C79fcB50Ca1594B025960e539eD7A9a6D434A3",
        "0x19c0976f590D67707E62397C87829d896Dc0f1F1",
        "0x5a464c28d19848f44199d003bef5ecc87d090f87",
    ]

    topics = [
        "0x85258d09e1e4ef299ff3fc11e74af99563f022d21f3f940db982229dc2a3358c",
        "0x851aa1caf4888170ad8875449d18f0f512fd6deb2a6571ea1a41fb9f95acbcd1",
        "0x1326c8f8fb452b5d26a2406d96790efbb561bf5d2686986a30a5cd847eefc673",
        "0xe177246e00000000000000000000000000000000000000000000000000000000",
        "0xe986e40cc8c151830d4f61050f4fb2e4add8567caad2d5f5496f9158e91fe4c7",
        "0x29ae811400000000000000000000000000000000000000000000000000000000",
        "0x1a0b287e00000000000000000000000000000000000000000000000000000000",
        "0x74ceb2982b813d6b690af89638316706e6acb9a48fced388741b61b510f165b7",
        "0x42f3b824eb9d522b949ff3d8f70db1872c46f3fc68b6df1a4c8d6aaebfcb6796",
    ]

    events = chain.get_events_for_contracts_topics(
        contracts,
        [topics],
        from_block=9529100,
        to_block=9529101,
        mixed=True,
    )

    print(list(events))
    assert len(list(events)) == 20
