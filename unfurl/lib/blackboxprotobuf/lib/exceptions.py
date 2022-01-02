"""Exception classes for BlackboxProtobuf"""


class BlackboxProtobufException(Exception):
    """Base class for excepions raised by Blackbox Protobuf"""

    def __init__(self, message, path=None, *args):
        self.path = path
        super(BlackboxProtobufException, self).__init__(message, *args)

    def set_path(self, path):
        if self.path is None:
            self.path = path


class TypedefException(BlackboxProtobufException):
    """Thrown when an error is identified in the type definition, such as
    conflicting or incosistent values."""

    def __str__(self):
        message = super(TypedefException, self).__str__()
        if self.path is not None:
            message = (
                "Encountered error within typdef for field %s: "
                % "->".join(map(str, self.path))
            ) + message
        return message


class EncoderException(BlackboxProtobufException, ValueError):
    """Thrown when there is an error encoding a dictionary to a type definition"""

    def __str__(self):
        message = super(EncoderException, self).__str__()
        if self.path is not None:
            message = (
                "Encountered error encoding field %s: " % "->".join(map(str, self.path))
            ) + message
        return message


class DecoderException(BlackboxProtobufException, ValueError):
    """Thrown when there is an error decoding a bytestring to a dictionary"""

    def __str__(self):
        message = super(DecoderException, self).__str__()
        if self.path is not None:
            message = (
                "Encountered error decoding field %s: " % "->".join(map(str, self.path))
            ) + message
        return message
