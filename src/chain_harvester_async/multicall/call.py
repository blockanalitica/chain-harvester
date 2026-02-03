import logging

from eth_abi.exceptions import InsufficientDataBytes
from web3 import Web3

from chain_harvester.constants import Network
from chain_harvester_async.multicall.exceptions import StateOverrideNotSupportedError
from chain_harvester_async.multicall.signature import _get_signature
from chain_harvester_async.multicall.utils import state_override_supported

log = logging.getLogger(__name__)


class Call:
    def __init__(
        self,
        target,
        function,
        w3=None,
        chain_id=None,
        returns=None,
        block_identifier=None,
        state_override_code=None,
        gas_limit=None,
        origin=None,
    ):
        self.target = Web3.to_checksum_address(target)
        self.returns = returns
        self.block_identifier = block_identifier
        self.state_override_code = state_override_code
        self.w3 = w3
        self.chain_id = chain_id

        self.gas_limit = gas_limit
        self.origin = Web3.to_checksum_address(target) if origin else None

        if isinstance(function, list):
            self.function = function[0]
            self.args = function[1:]
        else:
            self.function = function
            self.args = None

        self.signature = _get_signature(self.function)

    def __repr__(self):
        string = f"<Call {self.function} on {self.target[:8]}"
        if self.block_identifier is not None:
            string += f" block={self.block_identifier}"
        if self.returns is not None:
            string += f" returns={self.returns}"
        return f"{string}>"

    @property
    def data(self):
        return self.signature.encode_data(self.args)

    @staticmethod
    def decode_output(output, signature, returns=None, success=None):
        if success is None:
            apply_handler = lambda handler, value: handler(value)
        else:
            apply_handler = lambda handler, value: handler(success, value)

        if success is None or success:
            try:
                decoded = signature.decode_data(output)
            except InsufficientDataBytes:
                decoded = [None] * (len(returns) if returns else 1)
        else:
            decoded = [None] * (len(returns) if returns else 1)

        if returns:
            return {
                ident: apply_handler(handler, value) if handler else value
                for (ident, handler), value in zip(returns, decoded, strict=False)
            }
        else:
            return decoded if len(decoded) > 1 else decoded[0]

    def __await__(self):
        return self.coroutine().__await__()

    # TODO @eth_retry.auto_retry(min_sleep_time=1, max_sleep_time=3)
    async def coroutine(self, args=None, *, block_identifier=None):
        if not self.w3 or not self.chain_id:
            raise ValueError(
                "Invalid chain configuration: both 'w3' and 'chain_id' must be set before use."
            )

        if self.state_override_code and not state_override_supported(self.chain_id):
            # TODO: test this
            raise StateOverrideNotSupportedError(
                f"State override is not supported on {Network(self.chain_id).__repr__()[1:-1]}."
            )

        output = await self.w3.eth.call(
            *prep_args(
                self.target,
                self.signature,
                args or self.args,
                block_identifier or self.block_identifier,
                self.origin,
                self.gas_limit,
                self.state_override_code,
            )
        )

        result = Call.decode_output(output, self.signature, self.returns)

        log.debug("%s returned %s", self, result)
        return result


def prep_args(target, signature, args, block_identifier, origin, gas_limit, state_override_code):
    calldata = signature.encode_data(args)

    call_dict = {"to": target, "data": calldata}
    prepared_args = [call_dict, block_identifier]

    if origin:
        call_dict["from"] = origin

    if gas_limit:
        call_dict["gas"] = gas_limit

    if state_override_code:
        prepared_args.append({target: {"code": state_override_code}})

    return prepared_args
