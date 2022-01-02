from .types import type_maps


class Config:
    def __init__(self):

        # Map of message type names to typedefs, previously stored at
        # `blackboxprotobuf.known_messages`
        self.known_types = {}

        # Default type for "bytes" like objects that aren't messages or strings
        # Other option is currently just 'bytes_hex'
        self.default_binary_type = "bytes"

        # Change the default type for a wiretype (eg.
        self.default_types = {}

    def get_default_type(self, wiretype):
        default_type = self.default_types.get(wiretype, None)
        if default_type is None:
            default_type = type_maps.WIRE_TYPE_DEFAULTS.get(wiretype, None)

        return default_type


default = Config()
