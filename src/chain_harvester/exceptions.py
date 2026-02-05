# TODO: replace ChainException with ChainHarvesterError
class ChainException(Exception):
    pass


class ChainHarvesterError(Exception):
    pass


class ConfigError(ChainHarvesterError):
    pass
