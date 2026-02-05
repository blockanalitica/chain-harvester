from chain_harvester_async.networks import (
    ArbitrumMainnetChain,
    AvalancheMainnetChain,
    BaseMainnetChain,
    BlastMainnetChain,
    EthereumMainnetChain,
    EthereumSepoliaChain,
    FilecoinMainnetChain,
    GnosisMainnetChain,
    HemiMainnetChain,
    HyperliquidMainnetChain,
    LineaMainnetChain,
    MonadMainnetChain,
    OptimismMainnetChain,
    PlasmaMainnetChain,
    PlumeMainnetChain,
    PolygonMainnetChain,
    RariMainnetChain,
    ScrollMainnetChain,
    TenderlyTestnetChain,
    UnichainMainnetChain,
)


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
        case "monad":
            return MonadMainnetChain(*args, **kwargs)
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
