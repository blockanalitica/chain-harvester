from eth_abi.abi import default_codec
from eth_abi.decoding import TupleDecoder
from eth_abi.encoding import TupleEncoder
from eth_utils import function_signature_to_4byte_selector

_SIGNATURES = {}

_get_encoder = default_codec._registry.get_encoder
_get_decoder = default_codec._registry.get_decoder
_stream_cls = default_codec.stream_class


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


def _get_signature(signature):
    try:
        return _SIGNATURES[signature]
    except KeyError:
        instance = Signature(signature)
        _SIGNATURES[signature] = instance
        return instance


class Signature:
    def __init__(self, signature):
        self.signature = signature
        parsed = parse_signature(signature)
        self.function = parsed[0]
        self.input_types = parsed[1]
        self.output_types = parsed[2]

        self.fourbyte = function_signature_to_4byte_selector(self.function)

        self._encoder = (
            TupleEncoder(encoders=tuple(_get_encoder(type_str) for type_str in self.input_types))
            if self.input_types
            else None
        )

        self._decoder = TupleDecoder(
            decoders=tuple(_get_decoder(type_str) for type_str in self.output_types)
        )

    def encode_data(self, args=None):
        return self.fourbyte + self._encoder(args) if args else self.fourbyte

    def decode_data(self, output):
        return self._decoder(_stream_cls(output))
