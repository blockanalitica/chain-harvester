from enum import IntEnum
from functools import lru_cache

import requests
from eth_abi import decode, encode
from eth_utils import function_signature_to_4byte_selector
from web3 import Web3

MULTICALL2_BYTECODE = "0x608060405234801561001057600080fd5b50600436106100b45760003560e01c806372425d9d1161007157806372425d9d1461013d57806386d516e814610145578063a8b0574e1461014d578063bce38bd714610162578063c3077fa914610182578063ee82ac5e14610195576100b4565b80630f28c97d146100b9578063252dba42146100d757806327e86d6e146100f8578063399542e91461010057806342cbb15c146101225780634d2301cc1461012a575b600080fd5b6100c16101a8565b6040516100ce919061083b565b60405180910390f35b6100ea6100e53660046106bb565b6101ac565b6040516100ce9291906108ba565b6100c1610340565b61011361010e3660046106f6565b610353565b6040516100ce93929190610922565b6100c161036b565b6100c161013836600461069a565b61036f565b6100c161037c565b6100c1610380565b610155610384565b6040516100ce9190610814565b6101756101703660046106f6565b610388565b6040516100ce9190610828565b6101136101903660046106bb565b610533565b6100c16101a3366004610748565b610550565b4290565b8051439060609067ffffffffffffffff8111156101d957634e487b7160e01b600052604160045260246000fd5b60405190808252806020026020018201604052801561020c57816020015b60608152602001906001900390816101f75790505b50905060005b835181101561033a5760008085838151811061023e57634e487b7160e01b600052603260045260246000fd5b6020026020010151600001516001600160a01b031686848151811061027357634e487b7160e01b600052603260045260246000fd5b60200260200101516020015160405161028c91906107f8565b6000604051808303816000865af19150503d80600081146102c9576040519150601f19603f3d011682016040523d82523d6000602084013e6102ce565b606091505b5091509150816102f95760405162461bcd60e51b81526004016102f090610885565b60405180910390fd5b8084848151811061031a57634e487b7160e01b600052603260045260246000fd5b602002602001018190525050508080610332906109c2565b915050610212565b50915091565b600061034d60014361097b565b40905090565b43804060606103628585610388565b90509250925092565b4390565b6001600160a01b03163190565b4490565b4590565b4190565b6060815167ffffffffffffffff8111156103b257634e487b7160e01b600052604160045260246000fd5b6040519080825280602002602001820160405280156103eb57816020015b6103d8610554565b8152602001906001900390816103d05790505b50905060005b825181101561052c5760008084838151811061041d57634e487b7160e01b600052603260045260246000fd5b6020026020010151600001516001600160a01b031685848151811061045257634e487b7160e01b600052603260045260246000fd5b60200260200101516020015160405161046b91906107f8565b6000604051808303816000865af19150503d80600081146104a8576040519150601f19603f3d011682016040523d82523d6000602084013e6104ad565b606091505b509150915085156104d557816104d55760405162461bcd60e51b81526004016102f090610844565b604051806040016040528083151581526020018281525084848151811061050c57634e487b7160e01b600052603260045260246000fd5b602002602001018190525050508080610524906109c2565b9150506103f1565b5092915050565b6000806060610543600185610353565b9196909550909350915050565b4090565b60408051808201909152600081526060602082015290565b80356001600160a01b038116811461058357600080fd5b919050565b600082601f830112610598578081fd5b8135602067ffffffffffffffff808311156105b5576105b56109f3565b6105c2828385020161094a565b83815282810190868401865b8681101561068c57813589016040601f198181848f030112156105ef578a8bfd5b6105f88261094a565b6106038a850161056c565b81528284013589811115610615578c8dfd5b8085019450508d603f850112610629578b8cfd5b898401358981111561063d5761063d6109f3565b61064d8b84601f8401160161094a565b92508083528e84828701011115610662578c8dfd5b808486018c85013782018a018c9052808a01919091528652505092850192908501906001016105ce565b509098975050505050505050565b6000602082840312156106ab578081fd5b6106b48261056c565b9392505050565b6000602082840312156106cc578081fd5b813567ffffffffffffffff8111156106e2578182fd5b6106ee84828501610588565b949350505050565b60008060408385031215610708578081fd5b82358015158114610717578182fd5b9150602083013567ffffffffffffffff811115610732578182fd5b61073e85828601610588565b9150509250929050565b600060208284031215610759578081fd5b5035919050565b60008282518085526020808601955080818302840101818601855b848110156107bf57858303601f19018952815180511515845284015160408585018190526107ab818601836107cc565b9a86019a945050509083019060010161077b565b5090979650505050505050565b600081518084526107e4816020860160208601610992565b601f01601f19169290920160200192915050565b6000825161080a818460208701610992565b9190910192915050565b6001600160a01b0391909116815260200190565b6000602082526106b46020830184610760565b90815260200190565b60208082526021908201527f4d756c746963616c6c32206167677265676174653a2063616c6c206661696c656040820152601960fa1b606082015260800190565b6020808252818101527f4d756c746963616c6c206167677265676174653a2063616c6c206661696c6564604082015260600190565b600060408201848352602060408185015281855180845260608601915060608382028701019350828701855b8281101561091457605f198887030184526109028683516107cc565b955092840192908401906001016108e6565b509398975050505050505050565b6000848252836020830152606060408301526109416060830184610760565b95945050505050565b604051601f8201601f1916810167ffffffffffffffff81118282101715610973576109736109f3565b604052919050565b60008282101561098d5761098d6109dd565b500390565b60005b838110156109ad578181015183820152602001610995565b838111156109bc576000848401525b50505050565b60006000198214156109d6576109d66109dd565b5060010190565b634e487b7160e01b600052601160045260246000fd5b634e487b7160e01b600052604160045260246000fdfea2646970667358221220c1152f751f29ece4d7bce5287ceafc8a153de9c2c633e3f21943a87d845bd83064736f6c63430008010033"


class Network(IntEnum):
    Mainnet = 1


MULTICALL_ADDRESSES = {
    Network.Mainnet: "0xeefBa1e63905eF1D7ACbA5a8513c70307C1cE441",
}

MULTICALL2_ADDRESSES = {
    Network.Mainnet: "0x5ba1e12693dc8f9c48aad8770482f4739beed696",
}


def split_calls(calls):
    """
    Split calls into 2 batches in case request is too large.
    """
    center = len(calls) // 2
    chunk_1 = calls[:center]
    chunk_2 = calls[center:]
    return chunk_1, chunk_2


class Call:
    def __init__(
        self,
        target,
        function,
        returns=None,
        block_identifier=None,
        state_override_code=None,
        _w3=None,
    ):
        self.target = Web3.to_checksum_address(target)
        self.returns = returns
        self.block_identifier = block_identifier
        self.state_override_code = state_override_code
        self.w3 = _w3

        if isinstance(function, list):
            self.function, *self.args = function
        else:
            self.function = function
            self.args = None

        self.signature = Signature(self.function)

    @property
    def data(self) -> bytes:
        return self.signature.encode_data(self.args)

    def decode_output(self, output, success=None):
        if success is None:
            apply_handler = lambda handler, value: handler(value)
        else:
            apply_handler = lambda handler, value: handler(success, value)

        if success is None or success:
            try:
                decoded = self.signature.decode_data(output)
            except:  # noqa: E722
                success, decoded = False, [None] * len(self.returns)
            decoded = [None] * len(self.returns)
        if self.returns:
            return {
                name: apply_handler(handler, value) if handler else value
                for (name, handler), value in zip(self.returns, decoded)
            }
        else:
            return decoded if len(decoded) > 1 else decoded[0]

    def __call__(self, args=None):
        args = args or self.args
        calldata = self.signature.encode_data(args)

        args = [{"to": self.target, "data": calldata}, self.block_identifier]

        if self.state_override_code:
            args.append({self.target: {"code": self.state_override_code}})

        output = self.w3.eth.call(*args)

        return self.decode_output(output)


class Multicall:
    def __init__(
        self,
        calls,
        block_identifier=None,
        require_success=True,
        _w3=None,
        chain_id=None,
    ):
        self.calls = calls
        self.block_identifier = block_identifier
        self.require_success = require_success
        self.w3 = _w3
        self.chain_id = chain_id
        if require_success is True:
            multicall_map = MULTICALL_ADDRESSES if self.chain_id in MULTICALL_ADDRESSES else MULTICALL2_ADDRESSES
            self.multicall_sig = "aggregate((address,bytes)[])(uint256,bytes[])"
        else:
            multicall_map = MULTICALL2_ADDRESSES
            self.multicall_sig = "tryBlockAndAggregate(bool,(address,bytes)[])(uint256,uint256,(bool,bytes)[])"
        self.multicall_address = multicall_map[self.chain_id]

    def __call__(self):
        result = {}
        for call, (success, output) in zip(self.calls, self.fetch_outputs()):
            result.update(call.decode_output(output, success))
        return result

    def fetch_outputs(self, calls=None, ConnErr_retries=0):
        if calls is None:
            calls = self.calls

        aggregate = Call(
            self.multicall_address,
            self.multicall_sig,
            returns=None,
            _w3=self.w3,
            block_identifier=self.block_identifier,
            state_override_code=MULTICALL2_BYTECODE,
        )

        try:
            args = self.get_args(calls)
            if self.require_success is True:
                _, outputs = aggregate(args)
                outputs = ((None, output) for output in outputs)
            else:
                _, _, outputs = aggregate(args)
            return outputs
        except requests.ConnectionError as e:
            if (
                "('Connection aborted.', ConnectionResetError(104, 'Connection reset by peer'))" not in str(e)
                or ConnErr_retries > 5
            ):
                raise
        except requests.HTTPError as e:
            if "request entity too large" not in str(e).lower():
                raise
        chunk_1, chunk_2 = split_calls(self.calls)
        return self.fetch_outputs(chunk_1, ConnErr_retries=ConnErr_retries + 1) + self.fetch_outputs(
            chunk_2, ConnErr_retries=ConnErr_retries + 1
        )

    def get_args(self, calls):
        if self.require_success is True:
            return [[[call.target, call.data] for call in calls]]
        return [self.require_success, [[call.target, call.data] for call in calls]]


def parse_typestring(typestring):
    if typestring == "()":
        return []
    parts = []
    part = ""
    inside_tuples = 0
    for character in typestring[1:-1]:
        if character == "(":
            inside_tuples += 1
        elif character == ")":
            inside_tuples -= 1
        elif character == "," and inside_tuples == 0:
            parts.append(part)
            part = ""
            continue
        part += character
    parts.append(part)
    return parts


def parse_signature(signature):
    """
    Breaks 'func(address)(uint256)' into ['func', ['address'], ['uint256']]
    """
    parts = []
    stack = []
    start = 0
    for end, character in enumerate(signature):
        if character == "(":
            stack.append(character)
            if not parts:
                parts.append(signature[start:end])
                start = end
        if character == ")":
            stack.pop()
            if not stack:
                parts.append(signature[start : end + 1])
                start = end + 1
    function = "".join(parts[:2])
    input_types = parse_typestring(parts[1])
    output_types = parse_typestring(parts[2])
    return function, input_types, output_types


get_4byte_selector = lru_cache(maxsize=None)(function_signature_to_4byte_selector)


class Signature:
    def __init__(self, signature):
        self.signature = signature
        self.function, self.input_types, self.output_types = parse_signature(signature)

    @property
    def fourbyte(self) -> bytes:
        return get_4byte_selector(self.function)

    def encode_data(self, args=None):
        return self.fourbyte + encode(self.input_types, args) if args else self.fourbyte

    def decode_data(self, output):
        return decode(self.output_types, output)
