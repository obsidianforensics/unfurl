# Copyright 2024 Ryan Benson
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

import base64
import re

import logging
log = logging.getLogger(__name__)

bluesky_edge = {
    'color': {
        'color': '#1185fe'
    },
    'title': 'Bluesky TID',
    'label': '🦋'
}

tid_re = re.compile(r'[2-7a-z]{13}')

# Create a mapping from "base32-sortable" alphabet to standard base32 alphabet
BASE32_SORTABLE_ALPHABET = "234567abcdefghijklmnopqrstuvwxyz"
STANDARD_ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ234567"
BASE32_SORTABLE_TRANS = str.maketrans(BASE32_SORTABLE_ALPHABET, STANDARD_ALPHABET)

def parse_bluesky_tid(unfurl, node):
    # Ref: https://atproto.com/specs/record-key#record-key-type-tid
    assert tid_re.fullmatch(node.value), "Bluesky TID is not in the expected format (base32-sortable)"
    assert not ord(node.value[0]) & 0x40, "Bluesky TID high bit is set; it must be 0"

    # Translate the base32-sortable string to standard base32, then decode it to 8 raw bytes
    translated_str = node.value.translate(BASE32_SORTABLE_TRANS)
    decoded_bytes = base64.b32decode(translated_str+"===")

    # The first bit is 0, then the next 53 bits are the timestamp (microseconds since the UNIX epoch).
    # The last 10 are a random "clock identifier", so shift those out to get the timestamp.
    timestamp = int.from_bytes(decoded_bytes, byteorder="big") >> 9

    unfurl.add_to_queue(
        data_type='epoch-microseconds', key=None, value=timestamp, label=f'TID Timestamp: {timestamp}',
        hover='Bluesky uses <i>timestamp identifiers</i> ("TIDs") as a way to reference records, '
              'which contain an embedded timestamp.',
        parent_id=node.node_id, incoming_edge_config=bluesky_edge)


def run(unfurl, node):
    if isinstance(node.value, str) and re.fullmatch(tid_re, node.value):
        if node.data_type == 'url.path.segment':
            preceding_domain = unfurl.find_preceding_domain(node)
            if preceding_domain in ['bsky.app']:
                parse_bluesky_tid(unfurl, node)

        # If it's the "root" node and in the format of a TID, parse it.
        # This case covers someone parsing just an ID, not a full URL.
        elif node.node_id == 1:
            parse_bluesky_tid(unfurl, node)