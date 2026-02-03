class BaseExplorerMixin:
    chain_id = None

    def __init__(
        self,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)

    async def get_abi_from_source(self, contract_address):
        raise NotImplementedError(f"{self.__class__.__name__} must implement get_abi_from_source()")

    async def get_block_for_timestamp_fallback(self, timestamp):
        raise NotImplementedError(
            f"{self.__class__.__name__} must implement get_block_for_timestamp_fallback()"
        )
