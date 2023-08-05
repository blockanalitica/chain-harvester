import os

from dotenv import load_dotenv

load_dotenv()

ETHERSCAN_API_KEY = os.environ.get("ETHERSCAN_API_KEY")

RPC_NODES = {"ethereum": {"mainnet": os.environ.get("ETHEREUM_MAINNET_RPC")}}
