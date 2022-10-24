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
    try:
        tiktok_id = int(node.value)
        # TikTok IDs are 63 bits long; the upper 31 bits are the timestamp.
        # Shift it 32 (63-32 = 31) bits right, leaving just the timestamp bits.
        timestamp = (tiktok_id >> 32)

    except Exception as e:
        log.exception(f'Exception parsing TikTok ID: {e}')
        return

    if on_tiktok:
        node.hover = 'TikTok IDs are time-based IDs similar to those of Twitter Snowflakes.'

    unfurl.add_to_queue(
        data_type='epoch-seconds', key=None, value=timestamp, label=f'Timestamp: {timestamp}',
        hover='The leading 31 bits in a TikTok ID are a timestamp, '
              '<br>thought to represent when an item was posted or created.',
        parent_id=node.node_id, incoming_edge_config=tiktok_edge)


def run(unfurl, node):

    if node.data_type == 'url.path.segment':

        if 'tiktok.com' in unfurl.find_preceding_domain(node):
            if node.key == 1:
                if node.value.startswith('@'):
                    unfurl.add_to_queue(
                        data_type='descriptor', key=None, value=f'Username who posted on TikTok',
                        parent_id=node.node_id, incoming_edge_config=tiktok_edge)
                elif node.value == 'embed':
                    unfurl.add_to_queue(
                        data_type='descriptor', key=None, value=f'TikTok video was embedded on another site',
                        parent_id=node.node_id, incoming_edge_config=tiktok_edge)

            # Check if TikTok ID timestamp would be between 2017-12 and 2025-05
            elif unfurl.check_if_int_between(node.value, 6500000000000000000, 7500000000000000000):
                parse_tiktok_id(unfurl, node)

    # If it's the "root" node and a plausible TikTok ID, parse it.
    # This case covers someone parsing just a TikTok ID, not a full URL.
    elif node.node_id == 1 and unfurl.check_if_int_between(node.value, 6500000000000000000, 7500000000000000000):
        parse_tiktok_id(unfurl, node, on_tiktok=False)
