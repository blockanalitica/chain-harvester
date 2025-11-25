from environs import env

ETHERSCAN_API_KEY = env("ETHERSCAN_API_KEY", None)
ALCHEMY_SUBGRAPH_QUERY_KEY = env("ALCHEMY_SUBGRAPH_QUERY_KEY", None)

USDS_CONTRACT = "0xdc035d45d973e3ec169d2276ddab16f1e407384f"
USDT_CONTRACT = "0xdac17f958d2ee523a2206206994597c13d831ec7"

DEMO_ABI = [
    {
        "inputs": [{"internalType": "address", "name": "morpho", "type": "address"}],
        "stateMutability": "nonpayable",
        "type": "constructor",
    },
    {"inputs": [], "name": "ZeroAddress", "type": "error"},
    {
        "anonymous": False,
        "inputs": [
            {
                "indexed": True,
                "internalType": "address",
                "name": "metaMorpho",
                "type": "address",
            },
            {
                "indexed": True,
                "internalType": "address",
                "name": "caller",
                "type": "address",
            },
            {
                "indexed": False,
                "internalType": "address",
                "name": "initialOwner",
                "type": "address",
            },
            {
                "indexed": False,
                "internalType": "uint256",
                "name": "initialTimelock",
                "type": "uint256",
            },
            {
                "indexed": True,
                "internalType": "address",
                "name": "asset",
                "type": "address",
            },
            {
                "indexed": False,
                "internalType": "string",
                "name": "name",
                "type": "string",
            },
            {
                "indexed": False,
                "internalType": "string",
                "name": "symbol",
                "type": "string",
            },
            {
                "indexed": False,
                "internalType": "bytes32",
                "name": "salt",
                "type": "bytes32",
            },
        ],
        "name": "CreateMetaMorpho",
        "type": "event",
    },
    {
        "inputs": [],
        "name": "MORPHO",
        "outputs": [{"internalType": "address", "name": "", "type": "address"}],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [
            {"internalType": "address", "name": "initialOwner", "type": "address"},
            {
                "internalType": "uint256",
                "name": "initialTimelock",
                "type": "uint256",
            },
            {"internalType": "address", "name": "asset", "type": "address"},
            {"internalType": "string", "name": "name", "type": "string"},
            {"internalType": "string", "name": "symbol", "type": "string"},
            {"internalType": "bytes32", "name": "salt", "type": "bytes32"},
        ],
        "name": "createMetaMorpho",
        "outputs": [
            {
                "internalType": "contract IMetaMorpho",
                "name": "metaMorpho",
                "type": "address",
            }
        ],
        "stateMutability": "nonpayable",
        "type": "function",
    },
    {
        "inputs": [{"internalType": "address", "name": "", "type": "address"}],
        "name": "isMetaMorpho",
        "outputs": [{"internalType": "bool", "name": "", "type": "bool"}],
        "stateMutability": "view",
        "type": "function",
    },
]
