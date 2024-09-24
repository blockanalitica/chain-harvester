from web3 import Web3

from chain_harvester.networks.ethereum.mainnet import EthereumMainnetChain
from integration_tests.env import API_KEYS, ETHEREUM_ALCHEMY_API_KEY, RPC_NODES


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


def test__eth_multicall():
    chain = EthereumMainnetChain(rpc_nodes=RPC_NODES, api_keys=API_KEYS)
    block_identifier = 17892782

    response = chain.eth_multicall(
        [
            [
                "0x6D635c8d08a1eA2F1687a5E46b666949c977B7dd",
                "accrued",
                block_identifier,
                [1],
            ]
        ]
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
    assert len(list(events)) == 3


def text__is_eao():
    chain = EthereumMainnetChain(rpc_nodes=RPC_NODES, api_keys=API_KEYS)
    assert chain.is_eoa("0x7d9f92DAa9254Bbd1f479DBE5058f74C2381A898") is False
    assert chain.is_eoa("0x5eafe35109ae22c7674c1a30594abe833a9691e8")


def test__bytes32():
    chain = EthereumMainnetChain(rpc_nodes=RPC_NODES, api_keys=API_KEYS)
    DSCHIEF_1_0_CONTRACT_ADDRESS = "0x8e2a84d6ade1e7fffee039a35ef5f19f13057152"
    DSCHIEF_1_1_CONTRACT_ADDRESS = "0x9ef05f7f6deb616fd37ac3c959a2ddd25a54e4f5"
    DSCHIEF_1_2_CONTRACT_ADDRESS = "0x0a3f6849f78076aefadf113f5bed87720274ddc0"
    topics = [
        "0x4d9a807e05ec038d31d248a43818a2234c2a467865e998b3d4da029d9123b5c2",
        "0x7e816826910b70789c9de9051404b61689ff0e3dcb3e0d73f447b1d797fbdcb0",
        "0xea66f58e474bc09f580000e81f31b334d171db387d0c6098ba47bd897741679b",
        "0xf001c2d12c2288935c811b4977748cb3e5e3c485d08a1fb1984023cb2452d463",
        "0xd8ccd0f300000000000000000000000000000000000000000000000000000000",
        "0xdd46706400000000000000000000000000000000000000000000000000000000",
        "0xa69beaba00000000000000000000000000000000000000000000000000000000",
    ]

    events = chain.get_events_for_contracts_topics(
        [
            DSCHIEF_1_0_CONTRACT_ADDRESS,
            DSCHIEF_1_1_CONTRACT_ADDRESS,
            DSCHIEF_1_2_CONTRACT_ADDRESS,
        ],
        [topics],
        4749330,
        4755630,
        mixed=True,
    )

    assert len(list(events)) == 9


def test__decode_issue():
    chain = EthereumMainnetChain(rpc_nodes=RPC_NODES, api_keys=API_KEYS)
    topics = [
        "0x4d9a807e05ec038d31d248a43818a2234c2a467865e998b3d4da029d9123b5c2",
        "0x7e816826910b70789c9de9051404b61689ff0e3dcb3e0d73f447b1d797fbdcb0",
        "0xea66f58e474bc09f580000e81f31b334d171db387d0c6098ba47bd897741679b",
        "0xf001c2d12c2288935c811b4977748cb3e5e3c485d08a1fb1984023cb2452d463",
        "0xd8ccd0f300000000000000000000000000000000000000000000000000000000",
        "0xdd46706400000000000000000000000000000000000000000000000000000000",
        "0xa69beaba00000000000000000000000000000000000000000000000000000000",
    ]

    events = chain.get_events_for_contracts_topics(
        ["0x9eF05f7F6deB616fd37aC3c959a2dDD25A54E4F5"],
        [topics],
        9761247,
        9762411,
        mixed=True,
    )
    assert len(list(events)) == 3


def test__get_token_info():
    chain = EthereumMainnetChain(rpc_nodes=RPC_NODES, api_keys=API_KEYS)
    data = chain.get_token_info("0x6b175474e89094c44da98b954eedeac495271d0f")
    assert data["name"] == "Dai Stablecoin"
    assert data["symbol"] == "DAI"
    assert data["decimals"] == 18


def test__get_token_info__mkr():
    chain = EthereumMainnetChain(rpc_nodes=RPC_NODES, api_keys=API_KEYS)
    data = chain.get_token_info("0x9f8f72aa9304c8b593d555f12ef6589cc3a579a2")
    assert data["name"] == "Maker"
    assert data["symbol"] == "MKR"
    assert data["decimals"] == 18


def test_decoding_ilk():
    chain = EthereumMainnetChain(rpc_nodes=RPC_NODES, api_keys=API_KEYS, step=10_000_000)
    events = chain.get_events_for_contracts_topics(
        [
            "0xbE4F921cdFEf2cF5080F9Cf00CC2c14F1F96Bd07",
            "0xa1cB9e29f1727d8a0a6E3e0c1334A2323312A2d5",
        ],
        [["0x74ceb2982b813d6b690af89638316706e6acb9a48fced388741b61b510f165b7"]],
        10466460,
        12000000,
        mixed=True,
    )

    assert len(list(events)) == 9


def test_decoding_ilk_bytes():
    chain = EthereumMainnetChain(rpc_nodes=RPC_NODES, api_keys=API_KEYS)
    events = chain.get_events_for_contracts_topics(
        [
            "0x135954d155898D42C90D2a57824C690e0c7BEf1B",
        ],
        [],
        20258969,
        20258971,
        mixed=False,
    )
    assert len(list(events)) == 1


def test_get_block_transactions():
    chain = EthereumMainnetChain(rpc_nodes=RPC_NODES, api_keys=API_KEYS)
    url = f"https://eth-mainnet.g.alchemy.com/v2/{ETHEREUM_ALCHEMY_API_KEY}"
    data = chain.get_block_transactions(url, 20192996)
    assert len(data) == 131


def test_get_transactions_for_contracts():
    chain = EthereumMainnetChain(rpc_nodes=RPC_NODES, api_keys=API_KEYS)
    url = f"https://eth-mainnet.g.alchemy.com/v2/{ETHEREUM_ALCHEMY_API_KEY}"
    data = chain.get_transactions_for_contracts(
        url, ["0x89B78CfA322F6C5dE0aBcEecab66Aee45393cC5A"], 20391781, to_block=20391781
    )
    events = list(data)
    assert len(events) == 1


def test_get_transactions_for_contracts__failed():
    chain = EthereumMainnetChain(rpc_nodes=RPC_NODES, api_keys=API_KEYS)
    url = f"https://eth-mainnet.g.alchemy.com/v2/{ETHEREUM_ALCHEMY_API_KEY}"
    data = chain.get_transactions_for_contracts(
        url,
        ["0x89B78CfA322F6C5dE0aBcEecab66Aee45393cC5A"],
        20391781,
        to_block=20391781,
        failed=True,
    )
    events = list(data)
    assert len(events) == 0


def test__get_token_info__retry():
    chain = EthereumMainnetChain(rpc_nodes=RPC_NODES, api_keys=API_KEYS)
    data = chain.get_token_info("0x6b175474e89094c44da98b954eedeac495271d0f")
    assert data["name"] == "Dai Stablecoin"
    assert data["symbol"] == "DAI"
    assert data["decimals"] == 18

    data = chain.get_token_info("0x9f8f72aa9304c8b593d555f12ef6589cc3a579a3")
    assert data["name"] is None
    assert data["symbol"] is None
