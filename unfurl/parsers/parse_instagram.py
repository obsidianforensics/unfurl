# Copyright 2026 Ryan Benson
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

# Instagram's ID structure (from "Sharding & IDs at Instagram" engineering blog):
#   Bits 63-23: Timestamp in milliseconds since Instagram epoch (41 bits)
#   Bits 22-10: Logical shard ID (13 bits)
#   Bits  9-0:  Auto-increment sequence mod 1024 (10 bits)
#
# Epoch: 1314220021721 ms = 2011-08-24T21:07:01.721Z
# Ref: https://instagram-engineering.com/sharding-ids-at-instagram-1cf5a71e5a5c

INSTAGRAM_EPOCH_MS = 1314220021721

# Instagram shortcode alphabet (URL-safe base64 without padding)
SHORTCODE_ALPHABET = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_'

instagram_edge = {
    'color': {
        'color': '#e5348b'
    },
    'title': 'Instagram ID',
    'label': '📷'
}


def shortcode_to_media_id(shortcode):
    """Decode an Instagram shortcode to its numeric media ID."""
    media_id = 0
    for char in shortcode:
        idx = SHORTCODE_ALPHABET.find(char)
        if idx == -1:
            return None
        media_id = media_id * 64 + idx
    return media_id


def parse_instagram_id(unfurl, node, media_id):
    """Extract timestamp, shard ID, and sequence from an Instagram media ID."""
    timestamp_ms = (media_id >> 23) + INSTAGRAM_EPOCH_MS
    shard_id = (media_id & 0x7FF800) >> 10
    sequence = media_id & 0x3FF

    node.hover = (
        'Instagram IDs encode a creation timestamp, database shard ID, and sequence number. '
        '<a href="https://instagram-engineering.com/sharding-ids-at-instagram-1cf5a71e5a5c" '
        'target="_blank">[ref]</a>'
    )

    unfurl.add_to_queue(
        data_type='epoch-milliseconds', key=None, value=timestamp_ms,
        label=f'Timestamp:\n{timestamp_ms}',
        hover='The creation time of this Instagram media, extracted from the upper 41 bits '
              'of the media ID. This is when Instagram allocated the ID, typically within '
              'seconds of the post being published.',
        parent_id=node.node_id, incoming_edge_config=instagram_edge)

    unfurl.add_to_queue(
        data_type='integer', key=None, value=shard_id,
        label=f'Shard ID: {shard_id}',
        hover='The logical database shard where this media is stored (13 bits, 0-8191).',
        parent_id=node.node_id, incoming_edge_config=instagram_edge)

    unfurl.add_to_queue(
        data_type='integer', key=None, value=sequence,
        label=f'Sequence: {sequence}',
        hover='Auto-increment sequence number within the shard for this millisecond (10 bits, 0-1023).',
        parent_id=node.node_id, incoming_edge_config=instagram_edge)


def run(unfurl, node):
    if node.data_type == 'instagram.shortcode':
        media_id = shortcode_to_media_id(str(node.value))
        if media_id and media_id.bit_length() <= 64:
            parse_instagram_id(unfurl, node, media_id)

    elif node.data_type == 'instagram.story_id':
        try:
            media_id = int(node.value)
            if media_id.bit_length() <= 64:
                parse_instagram_id(unfurl, node, media_id)
        except (ValueError, TypeError):
            pass
