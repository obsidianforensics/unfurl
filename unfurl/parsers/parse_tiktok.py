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

from datetime import datetime
from unfurl.utils import extract_bits, set_bits

import logging
log = logging.getLogger(__name__)

tiktok_edge = {
    'color': {
        'color': '#F60051'
    },
    'title': 'TikTok Parsing Functions',
    'label': '♪'
}


def parse_tiktok_id(unfurl, node, on_tiktok=True):
    """Parse a TikTok ID, extracting the timestamp, sequence, machine ID, and entity type.

    TikTok IDs are 64 bits long; often rendered as a large
     number (6854717870488702213).

    Bits  | Field        | Description
    ------|--------------|--------------------------------
    63:32 | Timestamp    | in epoch seconds format
    31:22 | Milliseconds | 0-999 in most cases
    21:19 | <unused?>    |
    18:14 | Sequence     |
    13:12 | <unused?>    |
    11:8  | Entity Type  | 5 values for 4 entity types
    7:0   | Machine ID   |

    Ref: https://arxiv.org/pdf/2504.13279
"""
    try:
        tiktok_id = int(node.value)
    except ValueError as e:
        # Valid TikTok IDs should be ints, so this wasn't one
        return

    timestamp = extract_bits(tiktok_id, 32, 64)
    milliseconds = extract_bits(tiktok_id, 23, 32)
    sequence = extract_bits(tiktok_id, 14, 19)
    entity_type = extract_bits(tiktok_id, 8, 12)
    machine_id = extract_bits(tiktok_id, 0, 8)

    entity_type_map = {
        0: 'User Account',
        4: 'User Account',
        6: 'Device (smartphone or web browser)',
        11: 'Live session',
        13: 'Video'
    }
    entity_type_str = entity_type_map.get(entity_type, 'Unknown')

    if on_tiktok:
        node.hover = 'TikTok IDs are time-based IDs similar to those of Twitter Snowflakes.'

    unfurl.add_to_queue(
        data_type='epoch-seconds', key=None, value=float(f"{timestamp}.{milliseconds}"),
        label=f'Timestamp: {timestamp}.{milliseconds:03d}',
        # Ref: https://arxiv.org/pdf/2504.13279
        hover='The leading 42 bits in a TikTok ID are a timestamp, thought to represent '
              'when an item was posted or created. The first 32 bits can be interpreted '
              'as a Unix timestamp and the next 10 bits as the milliseconds.',
        parent_id=node.node_id, incoming_edge_config=tiktok_edge)

    unfurl.add_to_queue(
        data_type='integer', key=None, value=sequence, label=f'Sequence: {sequence}',
        hover='Thought to be a counter or sequence number, per https://arxiv.org/pdf/2504.13279',
        parent_id=node.node_id, incoming_edge_config=tiktok_edge)

    unfurl.add_to_queue(
        data_type='integer', key=None, value=machine_id, label=f'Machine ID: {machine_id}',
        hover='Thought to be a data center or machine ID, with different geographic areas correlating to different IDs.',
        parent_id=node.node_id, incoming_edge_config=tiktok_edge)

    unfurl.add_to_queue(
        data_type='descriptor', key=None, value=entity_type_str, label=f'Entity Type: {entity_type_str}',
        hover='Thought to be a counter or sequence number, per https://arxiv.org/pdf/2504.13279',
        parent_id=node.node_id, incoming_edge_config=tiktok_edge)


def create_tiktok_id(timestamp=None, days_ahead=None, sequence=0, machine_id=1, entity_type='video'):
    # Neither are set; make the timestamp now.
    if not timestamp and not days_ahead:
        timestamp = int(datetime.now().timestamp())
    # timestamp is a string; parse it to epoch seconds
    elif isinstance(timestamp, str):
        timestamp = int(datetime.fromisoformat(timestamp).timestamp())
    # Make the timestamp now + days_ahead
    elif not timestamp and days_ahead:
        timestamp = int(datetime.now().timestamp()) + (days_ahead * 86400)

    timestamp_bits = set_bits(timestamp, 32)
    sequence_bits = set_bits(sequence, 14)
    machine_id_bits = set_bits(machine_id, 0)
    entity_type_bits = set_bits(13, 8)

    return int(timestamp_bits + sequence_bits + machine_id_bits + entity_type_bits)

def run(unfurl, node):
    min_reasonable_date = create_tiktok_id('2017-12-01T00:00:00')
    max_reasonable_date = create_tiktok_id(days_ahead=365)

    if node.data_type == 'url.path.segment':
        if 'tiktok.com' in unfurl.find_preceding_domain(node):
            if node.key == 1:
                if node.value.startswith('@'):
                    unfurl.add_to_queue(
                        data_type='descriptor', key=None, value='Username who posted on TikTok',
                        parent_id=node.node_id, incoming_edge_config=tiktok_edge)
                elif node.value == 'embed':
                    unfurl.add_to_queue(
                        data_type='descriptor', key=None, value='TikTok video was embedded on another site',
                        parent_id=node.node_id, incoming_edge_config=tiktok_edge)

            # Check if TikTok ID timestamp would be "reasonable"
            elif unfurl.check_if_int_between(node.value, min_reasonable_date, max_reasonable_date):
                parse_tiktok_id(unfurl, node)

    # If it's the "root" node and a plausible TikTok ID, parse it.
    # This case covers someone parsing just a TikTok ID, not a full URL.
    elif node.node_id == 1 and unfurl.check_if_int_between(node.value, min_reasonable_date, max_reasonable_date):
        parse_tiktok_id(unfurl, node, on_tiktok=False)
