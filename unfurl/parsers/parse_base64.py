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
from unfurl import utils

b64_edge = {
    'color': {
        'color': '#2C63FF'
    },
    'title': 'Base64 Parsing Functions',
    'label': 'b64'
}


def run(unfurl, node):

    if not isinstance(node.value, str):
        return False

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
        decoded = base64.urlsafe_b64decode(padded_value)
    elif standard_b64_m:
        decoded = base64.b64decode(padded_value)

    if decoded == node.value or not decoded:
        return

    try:
        # This limits the plugin to only decoding ASCII string that were base64
        # encoded. Obviously other things could be encoded, but it's a start.
        str_decoded = decoded.decode('ascii', errors='strict')

    # This will happen a lot with things that aren't really b64 encoded, or
    # with things that are b64-encoded, but the results are not ASCII
    # (like gzip or protobufs).
    except UnicodeDecodeError:
        # Show the resulting bytes from base64 inflating. Disabled for now,
        # as it's too noisy.
        # unfurl.add_to_queue(data_type='bytes', key=None, value=decoded,
        #                parent_id=node.node_id, incoming_edge_config=b64_edge)
        return

    unfurl.add_to_queue(data_type='string', key=None, value=str_decoded,
                        parent_id=node.node_id, incoming_edge_config=b64_edge)
