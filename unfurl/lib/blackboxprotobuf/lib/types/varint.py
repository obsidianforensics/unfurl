"""Classes for encoding and decoding varint types"""
import binascii
import struct

from google.protobuf.internal import wire_format, encoder, decoder
import six

from unfurl.lib.blackboxprotobuf.lib.exceptions import EncoderException, DecoderException


def _gen_append_bytearray(arr):
    def _append_bytearray(x):
        if isinstance(x, (str, int)):
            arr.append(x)
        elif isinstance(x, bytes):
            arr.extend(x)
        else:
            raise EncoderException("Unknown type returned by protobuf library")

    return _append_bytearray


def encode_uvarint(value):
    """Encode a long or int into a bytearray."""
    output = bytearray()
    if value < 0:
        raise EncoderException(
            "Error encoding %d as uvarint. Value must be positive" % value
        )
    try:
        encoder._EncodeVarint(_gen_append_bytearray(output), value)
    except (struct.error, ValueError) as exc:
        six.raise_from(EncoderException("Error encoding %d as uvarint." % value), exc)

    return output


def decode_uvarint(buf, pos):
    """Decode bytearray into a long."""
    # Convert buffer to string
    if six.PY2:
        buf = str(buf)
    try:
        value, pos = decoder._DecodeVarint(buf, pos)
    except (TypeError, IndexError, decoder._DecodeError) as exc:
        six.raise_from(
            DecoderException(
                "Error decoding uvarint from %s..."
                % binascii.hexlify(buf[pos : pos + 8])
            ),
            exc,
        )
    return (value, pos)


def encode_varint(value):
    """Encode a long or int into a bytearray."""
    output = bytearray()
    if value > (2 ** 63) or value < -(2 ** 63):
        raise EncoderException("Value %d above maximum varint size" % value)
    try:
        encoder._EncodeSignedVarint(_gen_append_bytearray(output), value)
    except (struct.error, ValueError) as exc:
        six.raise_from(
            EncoderException("Error encoding %d as signed varint." % value), exc
        )
    return output


def decode_varint(buf, pos):
    """Decode bytearray into a long."""
    # Convert buffer to string
    if six.PY2:
        buf = str(buf)
    try:
        value, pos = decoder._DecodeSignedVarint(buf, pos)
    except (TypeError, IndexError, decoder._DecodeError) as exc:
        six.raise_from(
            DecoderException(
                "Error decoding varint from %s..."
                % binascii.hexlify(buf[pos : pos + 8])
            ),
            exc,
        )
    return (value, pos)


def encode_svarint(value):
    """Zigzag encode the potentially signed value prior to encoding"""
    # zigzag encode value
    return encode_uvarint(wire_format.ZigZagEncode(value))


def decode_svarint(buf, pos):
    """Decode bytearray into a long."""
    output, pos = decode_uvarint(buf, pos)
    # zigzag encode value
    return wire_format.ZigZagDecode(output), pos
