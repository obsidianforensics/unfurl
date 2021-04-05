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

import re

import logging
log = logging.getLogger(__name__)

sonyflake_edge = {
    'color': {
        'color': 'red'
    },
    'title': 'Sonyflake Parsing Functions',
    'label': '❄'
}


def parse_sonyflake(unfurl, node):
    # Ref: https://github.com/sony/sonyflake

    try:
        snowflake = int(node.value, 16)
        ts = (snowflake >> 24)
        timestamp = ts + 140952960000
        sequence = (snowflake >> 16) & 0xFF
        machine_id_1 = (snowflake >> 8) & 0xFF
        machine_id_2 = snowflake & 0xFF

    except Exception as e:
        log.exception(f'Exception parsing snowflake: {e}')
        return

    node.hover = 'Sonyflake is a distributed unique ID generator inspired by ' \
                 'Twitter\'s Snowflake. <a href="https://github.com/sony/sonyflake" ' \
                 'target="_blank">[ref]</a>'

    unfurl.add_to_queue(
        data_type='epoch-centiseconds', key=None, value=timestamp, label=f'Timestamp: {timestamp}',
        hover='The first value in a Sonyflake is a timestamp',
        parent_id=node.node_id, incoming_edge_config=sonyflake_edge)

    unfurl.add_to_queue(
        data_type='integer', key=None, value=sequence, label=f'Sequence: {sequence}',
        hover='For every ID that is generated, this number is incremented and rolls over every 256',
        parent_id=node.node_id, incoming_edge_config=sonyflake_edge)

    unfurl.add_to_queue(
        data_type='integer', key=None, value=machine_id_1, label=f'Machine ID: {machine_id_1}.{machine_id_2}',
        hover='The second value in a Sonyflake is the machine ID. By default this is '
              '<br>the <b>lower half of the private IP address</b> of the system generating the ID',
        parent_id=node.node_id, incoming_edge_config=sonyflake_edge)


def run(unfurl, node):
    if not node.data_type.startswith(('sonyflake', 'hash')):

        long_int = re.fullmatch(r'\d{15}', str(node.value))
        # Sonyflakes should be 15 hex digits long; limiting them to first digit 1-9 limits time frame from 2016 to 2026.
        m = re.fullmatch(r'(?P<sonyflake>[1-9][A-F0-9]{14})', str(node.value).replace('-', '').upper())
        if m and not long_int:
            parse_sonyflake(unfurl, node)

    elif node.data_type == 'sonyflake':
        parse_sonyflake(unfurl, node)
