from chain_harvester_async.networks.arbitrum import ArbitrumMainnetChain
from chain_harvester_async.networks.avalanche import AvalancheMainnetChain
from chain_harvester_async.networks.base import BaseMainnetChain
from chain_harvester_async.networks.blast import BlastMainnetChain
from chain_harvester_async.networks.ethereum import EthereumMainnetChain, EthereumSepoliaChain
from chain_harvester_async.networks.filecoin import FilecoinMainnetChain
from chain_harvester_async.networks.gnosis import GnosisMainnetChain
from chain_harvester_async.networks.hemi import HemiMainnetChain
from chain_harvester_async.networks.hyperliquid import HyperliquidMainnetChain
from chain_harvester_async.networks.linea import LineaMainnetChain
from chain_harvester_async.networks.mode import ModeMainnetChain
from chain_harvester_async.networks.optimism import OptimismMainnetChain
from chain_harvester_async.networks.plasma import PlasmaMainnetChain
from chain_harvester_async.networks.plume import PlumeMainnetChain
from chain_harvester_async.networks.polygon import PolygonMainnetChain
from chain_harvester_async.networks.rari import RariMainnetChain
from chain_harvester_async.networks.scroll import ScrollMainnetChain
from chain_harvester_async.networks.tenderly import TenderlyTestnetChain
from chain_harvester_async.networks.unichain import UnichainMainnetChain


def get_chain(network, *args, **kwargs):
    match network:
        case "arbitrum":
            return ArbitrumMainnetChain(*args, **kwargs)
        case "avalanche":
            return AvalancheMainnetChain(*args, **kwargs)
        case "base":
            return BaseMainnetChain(*args, **kwargs)
        case "blast":
            return BlastMainnetChain(*args, **kwargs)
        case "ethereum_core" | "ethereum_prime" | "ethereum_horizon" | "ethereum":
            return EthereumMainnetChain(*args, **kwargs)
        case "sepolia":
            return EthereumSepoliaChain(*args, **kwargs)
        case "filecoin":
            return FilecoinMainnetChain(*args, **kwargs)
        case "gnosis":
            return GnosisMainnetChain(*args, **kwargs)
        case "hemi":
            return HemiMainnetChain(*args, **kwargs)
        case "hyperliquid":
            return HyperliquidMainnetChain(*args, **kwargs)
        case "linea":
            return LineaMainnetChain(*args, **kwargs)
        case "mode":
            return ModeMainnetChain(*args, **kwargs)
        case "optimism":
            return OptimismMainnetChain(*args, **kwargs)
        case "plasma":
            return PlasmaMainnetChain(*args, **kwargs)
        case "plume":
            return PlumeMainnetChain(*args, **kwargs)
        case "polygon":
            return PolygonMainnetChain(*args, **kwargs)
        case "rari":
            return RariMainnetChain(*args, **kwargs)
        case "scroll":
            return ScrollMainnetChain(*args, **kwargs)
        case "tenderly":
            return TenderlyTestnetChain(*args, **kwargs)
        case "unichain":
            return UnichainMainnetChain(*args, **kwargs)
        case _:
            raise ValueError(f"Unknown network: {network}")
