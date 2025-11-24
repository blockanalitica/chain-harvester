import logging

import aiohttp
from eth_utils import toolz

from chain_harvester.constants import (
    GAS_LIMIT,
    MULTICALL2_ADDRESSES,
    MULTICALL3_ADDRESSES,
    MULTICALL3_BYTECODE,
)
from chain_harvester.multicall.call import Call
from chain_harvester.multicall.utils import (
    gather,
    state_override_supported,
)

log = logging.getLogger(__name__)


class Multicall:
    def __init__(
        self,
        calls,
        w3,
        chain_id,
        block_identifier=None,
        require_success=True,
        gas_limit=GAS_LIMIT,
        origin=None,
    ):
        self.calls = calls
        self.chain_id = chain_id
        self.block_identifier = block_identifier
        self.require_success = require_success
        self.w3 = w3
        self.chain_id = chain_id
        self.origin = origin
        self.gas_limit = gas_limit

        multicall_map = (
            MULTICALL3_ADDRESSES
            if self.chain_id in MULTICALL3_ADDRESSES
            else MULTICALL2_ADDRESSES
        )
        self.multicall_address = multicall_map[self.chain_id]

    def __await__(self):
        return self.coroutine().__await__()

    @property
    def multicall_sig(self):
        if self.require_success:
            return "aggregate((address,bytes)[])(uint256,bytes[])"
        else:
            return (
                "tryBlockAndAggregate(bool,(address,bytes)[])"
                "(uint256,uint256,(bool,bytes)[])"
            )

    @property
    def aggregate(self):
        state_override_code = None
        # If state override is not supported, we simply skip it.
        # This will mean you're unable to access full historical data on chains without
        # state override support.
        if state_override_supported(self.chain_id):
            state_override_code = MULTICALL3_BYTECODE

        return Call(
            self.multicall_address,
            self.multicall_sig,
            w3=self.w3,
            chain_id=self.chain_id,
            returns=None,
            block_identifier=self.block_identifier,
            state_override_code=state_override_code,
            gas_limit=self.gas_limit,
            origin=self.origin,
        )

    async def coroutine(self):
        batches = await gather(
            (
                self.fetch_outputs(batch, cid=str(i))
                for i, batch in enumerate(batcher.batch_calls(self.calls, batcher.step))
            )
        )
        return dict(toolz.mapcat(dict.items, toolz.concat(batches)))

    def get_args(self, calls):
        if self.require_success is True:
            return [[[call.target, call.data] for call in calls]]
        return [self.require_success, [[call.target, call.data] for call in calls]]

    async def fetch_outputs(self, calls=None, retries=0, cid=""):
        log.debug("coroutine %s started", cid)

        if calls is None:
            calls = self.calls

        try:
            args = self.get_args(calls)
            if self.require_success is True:
                self.block_identifier, outputs = await self.aggregate.coroutine(args)
                outputs = ((None, output) for output in outputs)
            else:
                self.block_identifier, _, outputs = await self.aggregate.coroutine(args)

            outputs = [
                Call.decode_output(output, call.signature, call.returns, success)
                for call, (success, output) in zip(calls, outputs, strict=True)
            ]
            log.debug("coroutine %s finished", cid)
            return outputs
        except Exception as e:
            _raise_or_proceed(e, len(calls), retries=retries)

        # Failed, we need to rebatch the calls and try again.
        batch_results = await gather(
            (
                self.fetch_outputs(chunk, retries + 1, f"{cid}_{i}")
                for i, chunk in enumerate(batcher.rebatch(calls))
            )
        )

        log.debug("coroutine %s finished", cid)
        return [result for chunk in batch_results for result in chunk]


class NotSoBrightBatcher:
    """
    This class helps with processing a large volume of large multicalls.
    It's not so bright, but should quickly bring the batch size down to something
    reasonable for your node.
    """

    def __init__(self):
        self.step = 10000

    def batch_calls(self, calls, step):
        """
        Batch calls into chunks of size `self.step`.
        """
        batches = []
        start = 0
        done = len(calls) - 1
        while True:
            end = start + step
            batches.append(calls[start:end])
            if end >= done:
                return batches
            start = end

    def split_calls(self, calls, unused=None):
        """
        Split calls into 2 batches in case request is too large.
        We do this to help us find optimal `self.step` value.
        """
        center = len(calls) // 2
        chunk_1 = calls[:center]
        chunk_2 = calls[center:]
        return chunk_1, chunk_2

    def rebatch(self, calls):
        # If a separate coroutine changed `step` after calls were last batched, we will
        # use the new `step` for rebatching.
        if self.step <= len(calls) // 2:
            return self.batch_calls(calls, self.step)

        # Otherwise we will split calls in half.
        if self.step >= len(calls):
            new_step = round(len(calls) * 0.99) if len(calls) >= 100 else len(calls) - 1
            log.warning(
                f"Multicall batch size reduced from {self.step} to {new_step}. "
                f"The failed batch had {len(calls)} calls."
            )
            self.step = new_step
        return self.split_calls(calls, self.step)


batcher = NotSoBrightBatcher()


def _raise_or_proceed(e, calls_count, retries):
    """Depending on the exception, either raises or ignores and allows `batcher`
    to rebatch."""
    strings = ()
    if isinstance(e, aiohttp.ClientOSError):
        if "broken pipe" not in str(e).lower():
            raise e
        log.warning(e)
    elif isinstance(e, aiohttp.ClientResponseError):
        strings = "request entity too large", "connection reset by peer"
        if all(string not in str(e).lower() for string in strings):
            raise e
        log.warning(e)
    elif isinstance(e, TimeoutError):
        pass
    elif isinstance(e, ValueError):
        if "out of gas" not in str(e).lower():
            raise e
        if calls_count == 1:
            raise e
        log.warning(e)
    else:
        raise e
