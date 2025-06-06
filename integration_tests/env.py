import os

from dotenv import load_dotenv

load_dotenv()

ETHERSCAN_API_KEY = os.environ.get("ETHERSCAN_API_KEY")

API_KEYS = {
    "ethereum": {
        "mainnet": os.environ.get("ETHERSCAN_API_KEY"),
    },
    "gnosis": {
        "mainnet": os.environ.get("GNOSISSCAN_API_KEY"),
    },
    "tenderly": {
        "testnet": os.environ.get("TENDERLY_API_KEY"),
    },
    "linea": {
        "mainnet": os.environ.get("LINEASCAN_API_KEY"),
    },
    "rari": {"mainnet": "n/a"},
    "base": {
        "mainnet": os.environ.get("BASESCAN_API_KEY"),
    },
    "hyperliquid": {
        "mainnet": os.environ.get("HYPERLIQUID_API_KEY"),
    },
}

RPC_NODES = {
    "ethereum": {
        "mainnet": os.environ.get("ETHEREUM_MAINNET_RPC"),
    },
    "gnosis": {
        "mainnet": os.environ.get("GNOSIS_MAINNET_RPC"),
    },
    "tenderly": {
        "testnet": os.environ.get("TENDERLY_TESTNET_RPC"),
    },
    "linea": {
        "mainnet": os.environ.get("LINEA_MAINNET_RPC"),
    },
    "rari": {
        "mainnet": os.environ.get("RARI_MAINNET_RPC"),
    },
    "base": {
        "mainnet": os.environ.get("BASE_MAINNET_RPC"),
    },
    "hyperliquid": {
        "mainnet": os.environ.get("HYPERLIQUID_MAINNET_RPC"),
    },
}

ETHEREUM_ALCHEMY_API_KEY = os.environ.get("ETHEREUM_ALCHEMY_API_KEY")
