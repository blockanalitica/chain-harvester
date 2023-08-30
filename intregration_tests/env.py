import os

from dotenv import load_dotenv

load_dotenv()


API_KEYS = {
    "ethereum": {
        "mainnet": os.environ.get("ETHERSCAN_API_KEY"),
        "goerli": os.environ.get("ETHERSCAN_API_KEY"),
    },
    "gnosis": {
        "mainnet": os.environ.get("GNOSISSCAN_API_KEY"),
    },
}

RPC_NODES = {
    "ethereum": {
        "mainnet": os.environ.get("ETHEREUM_MAINNET_RPC"),
        "goerli": os.environ.get("ETHEREUM_GOERLI_RPC"),
    },
    "gnosis": {
        "mainnet": os.environ.get("GNOSIS_MAINNET_RPC"),
    },
}
