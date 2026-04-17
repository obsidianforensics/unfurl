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

import re
import logging

log = logging.getLogger(__name__)

mongo_edge = {
    'color': {
        'color': '#13AA52'  # MongoDB green
    },
    'title': 'MongoDB ObjectID Parsing',
    'label': 'Mongo'
}


def run(unfurl, node):
    if not node.data_type.startswith('mongo'):
        # MongoDB ObjectIDs are exactly 24 hex characters (12 bytes).
        # Leading '/' is optional to handle URL path segments.
        m = re.fullmatch(r'/?([0-9A-F]{24})', str(node.value), re.IGNORECASE)
        if m:
            oid = m.group(1).lower()
            # First 4 bytes are a Unix timestamp; filter to MongoDB's lifespan (2009 onward)
            # to reduce false positives against other 24-char hex values.
            ts_int = int(oid[:8], 16)
            if 1230768000 <= ts_int <= 1893456000:  # 2009-01-01 to 2030-01-01
                unfurl.add_to_queue(
                    data_type='mongo.objectid', key=None, value=oid,
                    label=f'MongoDB ObjectID: {oid}',
                    hover='MongoDB ObjectIDs are 12-byte unique identifiers that embed a creation timestamp. '
                          '<a href="https://www.mongodb.com/docs/manual/reference/method/ObjectId/">[ref]</a>',
                    parent_id=node.node_id, incoming_edge_config=mongo_edge,
                    extra_options={'widthConstraint': {'maximum': 400}})

    elif node.data_type == 'mongo.objectid':
        oid = str(node.value)

        # Bytes 0-3 (hex[0:8]): 4-byte big-endian Unix timestamp in seconds.
        # Reliable across all MongoDB versions.
        timestamp = int(oid[:8], 16)
        unfurl.add_to_queue(
            data_type='epoch-seconds', key=None, value=timestamp,
            label=f'Timestamp: {timestamp}',
            hover='The first 4 bytes of a MongoDB ObjectID are a Unix timestamp (seconds) '
                  'representing when the ID was generated.',
            parent_id=node.node_id, incoming_edge_config=mongo_edge)

        # Bytes 4-8 (hex[8:18]): In MongoDB < 4.0, this was a 3-byte machine identifier
        # (first 3 bytes of the MD5 hash of the hostname) followed by a 2-byte process ID.
        # In MongoDB 4.0+ (released July 2019), both were replaced by a single 5-byte random
        # value generated once per process at startup. The two formats are indistinguishable
        # from the ObjectID bytes alone.
        random_val = oid[8:18]
        unfurl.add_to_queue(
            data_type='descriptor', key=None, value=random_val,
            label=f'Machine/Process (or random): {random_val}',
            hover='In MongoDB &lt; 4.0: 3-byte machine identifier + 2-byte process ID. '
                  'In MongoDB 4.0+: a single 5-byte random value per process. '
                  'The two formats are indistinguishable without additional context.',
            parent_id=node.node_id, incoming_edge_config=mongo_edge)

        # Bytes 9-11 (hex[18:24]): 3-byte incrementing counter, initialized to a random value.
        # Incremented for each ObjectID generated within the same second on the same process,
        # so multiple IDs created in rapid succession will have sequential counter values.
        counter = int(oid[18:24], 16)
        unfurl.add_to_queue(
            data_type='integer', key=None, value=counter,
            label=f'Counter: {counter}',
            hover='The last 3 bytes are an incrementing counter (initialized to a random value). '
                  'Multiple ObjectIDs generated in the same second will have sequential counter values.',
            parent_id=node.node_id, incoming_edge_config=mongo_edge)
