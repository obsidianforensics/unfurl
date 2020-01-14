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
import base64

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

TIME_STAMP_LENGTH = 4  # number  bytes storing the timestamp
BODY_LENGTH = 16  # Number of bytes consisting of the UUID

KSUID_ENCODED_STR = 27 # length of KSUID after encoding


def run(unfurl, node):

    if not node.data_type.startswith('ksuid'):
        # KSuid are 
        # 
        # Ref:
        #   - https://github.com/segmentio/ksuid

        m = re.match(r'([a-zA-Z0-9]{27})', str(node.value))
        if m:
            unfurl.add_to_queue(data_type='ksuid', key=None, value=node.value, label=f'KSUID: {node.value}',
                                hover='KSuid are identifiers that are comprised of a timestamp and a random number. '
                                '<a href="https://github.com/segmentio/ksuid" target="_blank">[ref]</a>',
                                parent_id=node.node_id, incoming_edge_config=ksuid_edge,
                                extra_options={'widthConstraint': {'maximum': 300}})

    elif node.data_type == 'ksuid' : # and node.value > "000000000000000000000000000" and node.value < "aWgEPTl1tmebfsQzFP4bxwgy80V":

        b = str(node.value)
       # unfurl.add_to_queue(data_type='b64', key=None, value=b,
      #                     label=f'B64: {b}',
       #                   parent_id=node.node_id, incoming_edge_config=ksuid_edge)


        decoded = base64.urlsafe_b64decode(b + '===')
        print(decoded)

        time_part_in_bytes = decoded[:TIME_STAMP_LENGTH]
        timestamp = int.from_bytes( time_part_in_bytes, byteorder="big", signed=False) + EPOCH_TIME

        random_payload = decoded[TIME_STAMP_LENGTH:]
        print(timestamp, random_payload)

        unfurl.add_to_queue(data_type='epoch-milliseconds', key=None, value=timestamp,
                           label=f'Timestamp: {timestamp}',
                          parent_id=node.node_id, incoming_edge_config=ksuid_edge)

        unfurl.add_to_queue(data_type='integer', key=None, value=random_payload,
                           label=f'Randomly generated payload: {random_payload}',
                          parent_id=node.node_id, incoming_edge_config=ksuid_edge)