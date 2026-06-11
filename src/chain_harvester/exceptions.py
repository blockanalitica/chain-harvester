# TODO: replace ChainException with ChainHarvesterError
class ChainException(Exception):
    pass


class ChainHarvesterError(Exception):
    pass


class ConfigError(ChainHarvesterError):
    pass


class ArchiveHeightBehindError(ChainHarvesterError):
    """The hypersync replica serving a query has indexed fewer blocks than the
    requested to_block, so the requested range cannot be fully covered."""

    def __init__(self, to_block, archive_height):
        self.to_block = to_block
        self.archive_height = archive_height
        super().__init__(
            f"hypersync archive height {archive_height} is behind requested to_block {to_block}"
        )
