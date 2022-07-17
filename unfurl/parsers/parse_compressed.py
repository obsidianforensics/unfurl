# Copyright 2020 Google LLC
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
import zlib
from unfurl import utils

zip_edge = {
    'color': {
        'color': '#2C63FF'
    },
    'title': 'Compression-related Parsing Functions',
    'label': 'zip'
}

b64_zip_edge = {
    'color': {
        'color': '#2C63FF'
    },
    'title': 'Compression-related Parsing Functions',
    'label': 'b64+zip'
}


def run(unfurl, node):

    if not isinstance(node.value, str):
        return False

    if node.data_type == 'zlib':
        inflated_str = zlib.decompress(node.value)
        unfurl.add_to_queue(
            data_type='zlib-inflate', key=None, value=inflated_str,
            hover='This data was inflated using zlib',
            parent_id=node.node_id, incoming_edge_config=zip_edge)
        return

    if node.data_type in ('url.scheme', 'url.host', 'url.domain', 'url.tld'):
        return

    # This checks for base64 encoding, which is often used before compression. Initially, the base64 decoding was
    # in parse_base64.py, but the intermediary node seemed like not useful clutter. I moved it here and combined
    # the parser into b64+zlib
    if len(node.value) % 4 == 1:
        # A valid b64 string will not be this length
        return False

    urlsafe_b64_m = utils.urlsafe_b64_re.fullmatch(node.value)
    standard_b64_m = utils.standard_b64_re.fullmatch(node.value)
    long_int_m = utils.long_int_re.fullmatch(node.value)

    # Long integers pass the b64 regex, but we don't want those here.
    if long_int_m:
        return

    decoded = None
    padded_value = unfurl.add_b64_padding(node.value)
    if not padded_value:
        return

    if urlsafe_b64_m:
        decoded = base64.urlsafe_b64decode(unfurl.add_b64_padding(node.value))
    elif standard_b64_m:
        decoded = base64.b64decode(unfurl.add_b64_padding(node.value))

    if decoded == node.value or not decoded:
        return

    try:
        inflated_bytes = zlib.decompress(decoded)
    except:
        # If we can't inflate it, bail on this parser.
        return

    try:
        inflated_str = inflated_bytes.decode('ascii', errors='strict')
        if re.fullmatch(r'[\w=&%\.-]+', inflated_str):
            unfurl.add_to_queue(
                data_type='string', key=None, value=inflated_str,
                parent_id=node.node_id,
                hover='This data was base64-decoded, then zlib inflated',
                incoming_edge_config=b64_zip_edge)
            return
    except:
        # If we couldn't decode the inflated bytes as ASCII, that's ok; we'll
        # just show the raw inflated bytes below.
        pass

    unfurl.add_to_queue(
        data_type='bytes', key=None, value=inflated_bytes, parent_id=node.node_id,
        hover='This data was inflated using zlib', incoming_edge_config=b64_zip_edge)
