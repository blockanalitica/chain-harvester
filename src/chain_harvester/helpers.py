from chain_harvester.networks.arbitrum.mainnet import ArbitrumMainnetChain
from chain_harvester.networks.avalanche.mainnet import AvalancheMainnetChain
from chain_harvester.networks.base.mainnet import BaseMainnetChain
from chain_harvester.networks.blast.mainnet import BlastMainnetChain
from chain_harvester.networks.ethereum.mainnet import EthereumMainnetChain
from chain_harvester.networks.ethereum.sepolia import EthereumSepoliaChain
from chain_harvester.networks.filecoin.mainnet import FilecoinMainnetChain
from chain_harvester.networks.gnosis.mainnet import GnosisMainnetChain
from chain_harvester.networks.hemi.mainnet import HemiMainnetChain
from chain_harvester.networks.hyperliquid.mainnet import HyperliquidMainnetChain
from chain_harvester.networks.linea.mainnet import LineaMainnetChain
from chain_harvester.networks.mode.mainnet import ModeMainnetChain
from chain_harvester.networks.optimism.mainnet import OptimismMainnetChain
from chain_harvester.networks.plasma.mainnet import PlasmaMainnetChain
from chain_harvester.networks.plume.mainnet import PlumeMainnetChain
from chain_harvester.networks.polygon.mainnet import PolygonMainnetChain
from chain_harvester.networks.rari.mainnet import RariMainnetChain
from chain_harvester.networks.scroll.mainnet import ScrollMainnetChain
from chain_harvester.networks.tenderly.testnet import TenderlyTestnetChain
from chain_harvester.networks.unichain.mainnet import UnichainMainnetChain


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
