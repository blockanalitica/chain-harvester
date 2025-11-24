# TODO: replace ChainException with ChainHarvesterError
class ChainException(Exception):  # noqa: N818
    pass


class ChainHarvesterError(Exception):
    pass


class ConfigError(ChainHarvesterError):
    pass
