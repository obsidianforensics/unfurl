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
import ulid

uuid_edge = {
    'color': {
        'color': 'orange'
    },
    'title': 'ULID Parsing Functions',
    'label': 'UL'
}


def run(unfurl, node):
    if not node.data_type.startswith('ulid'):
        # ULIDs are Base32 encoded and allow dashes to be added as desired for clarity
        # Ref:
        #   - https://github.com/ulid/spec
        #   - https://www.crockford.com/base32.html
        #
        # Filtering down to reasonable timeframes to reduce FPs:
        #   - 019AHCNC00SM9CSFQFXG3VC1FK <- 2015-01-01
        #   - 01JGFJJZ00TG242KAWHD959K7S <- 2025-01-01

        m = re.match(r'(?P<ulid>01[90A-HJ][A-HJKMNP-Z0-9]{23})', str(node.value).replace('-', ''))
        if m:
            u = m.group('ulid')
            unfurl.add_to_queue(
                data_type='ulid', key=None, value=u, label=f'ULID: {u}',
                hover='ULIDs are identifiers that are comprised of a timestamp and a random number. '
                      '<a href="https://github.com/ulid/spec" target="_blank">[ref]</a>',
                parent_id=node.node_id, incoming_edge_config=uuid_edge,
                extra_options={'widthConstraint': {'maximum': 300}})

    elif node.data_type == 'ulid':
        u = ulid.parse(node.value)
        timestamp = u.timestamp().int
        unfurl.add_to_queue(
            data_type='ulid-parsed', key=None, value=timestamp, label=f'Timestamp: {timestamp}',
            parent_id=node.node_id, incoming_edge_config=uuid_edge)
