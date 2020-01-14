# Copyright 2019 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import re
import sys

ksuid_edge = {
    'color': {
        'color': 'orange'
    },
    'title': 'KSUID Parsing Functions',
    'label': 'KSUID'
}



# Used instead of zero(January 1, 1970), so that the lifespan of KSUIDs
# will be considerably longer
EPOCH_TIME = 1400000000

TIME_STAMP_LENGTH = 4  # 4 bytes are storing the timestamp = 8 characters
KSUID_LEN = 27 # length of KSUID after encoding

CHARSET = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
BASE = 62

def run(unfurl, node):

    if not node.data_type.startswith('ksuid'):
        # KSuid are 
        # 
        # Ref:
        #   - https://github.com/segmentio/ksuid
        #   - https://github.com/saresend/KSUID

        m = re.match(r'([a-zA-Z0-9]{27})', str(node.value))
        if m and len(node.value) == 27 and str(node.value) > "000000000000000000000000000" and str(node.value) < "aWgEPTl1tmebfsQzFP4bxwgy80V":
            unfurl.add_to_queue(data_type='ksuid', key=None, value=node.value, label=f'KSUID: {node.value}',
                                hover='Ksuid are identifiers that are comprised of a timestamp and a random number. '
                                '<a href="https://github.com/segmentio/ksuid" target="_blank">[ref]</a>',
                                parent_id=node.node_id, incoming_edge_config=ksuid_edge,
                                extra_options={'widthConstraint': {'maximum': 300}})

    elif node.data_type == 'ksuid':

        decoded_str_b62_to_bytes = decodebytes(node.value)     
        time_part_in_bytes = decoded_str_b62_to_bytes[0:TIME_STAMP_LENGTH]        
        timestamp = EPOCH_TIME + int_from_bytes( time_part_in_bytes, byteorder="big", signed=False) 
        random_payload = decoded_str_b62_to_bytes[TIME_STAMP_LENGTH:]

        unfurl.add_to_queue(data_type='epoch-seconds', key=None, value=timestamp,
                           label=f'Timestamp: {timestamp}',
                          parent_id=node.node_id, incoming_edge_config=ksuid_edge)

        unfurl.add_to_queue(data_type='descriptor', key=None, value=random_payload,
                           label=f'Randomly generated payload: {random_payload}',
                          parent_id=node.node_id, incoming_edge_config=ksuid_edge)



def decode(b):
    """Decodes a base62 encoded value ``b``."""

    if b.startswith("0z"):
        b = b[2:]

    l, i, v = len(b), 0, 0
    for x in b:
        v += _value(x) * (BASE ** (l - (i + 1)))
        i += 1

    return v


def decodebytes(s):
    """Decodes a string of base62 data into a bytes object.
    :param s: A string to be decoded in base62
    :rtype: bytes
    """

    decoded = decode(s)
    buf = bytearray()
    while decoded > 0:
        buf.append(decoded & 0xff)
        decoded //= 256
    buf.reverse()

    return bytes(buf)


def _value(ch):
    """Decodes an individual digit of a base62 encoded string."""

    try:
        return CHARSET.index(ch)
    except ValueError:
        raise ValueError("base62: Invalid character (%s)" % ch)

def bytes_to_int(s, byteorder="big", signed=False):
    """Converts a byte array to an integer value.
    Python 3 comes with a built-in function to do this, but we would like to
    keep our code Python 2 compatible.
    """

    try:
        return int.from_bytes(s, byteorder, signed=signed)
    except AttributeError:
        # For Python 2.x
        if byteorder != "big" or signed:
            raise NotImplementedError()

        # NOTE: This won't work if a generator is given
        n = len(s)
        ds = (x << (8 * (n - 1 - i)) for i, x in enumerate(bytearray(s)))

        return sum(ds)

def int_from_bytes(s, byteorder="big", signed=False):
    if sys.version_info[0] >= 3:
        return int.from_bytes(s, byteorder, signed=signed)

    if isinstance(s, list):
        s = "".join(s)

    return int(codecs.encode(s, "hex"), 16)