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

import logging
log = logging.getLogger(__name__)

twitter_snowflake_edge = {
    'color': {
        'color': '#1da1f2'
    },
    'title': 'Twitter Snowflake',
    'label': '❄'
}

twitter_edge = {
    'color': {
        'color': '#1da1f2'
    },
    'title': 'Twitter Parsing Functions',
    'label': '@'
}


def parse_twitter_snowflake(unfurl, node):
    # Ref: https://blog.twitter.com/engineering/en_us/a/2010/announcing-snowflake.html
    #      https://ws-dl.blogspot.com/2019/08/2019-08-03-tweetedat-finding-tweet.html
    try:
        snowflake = int(node.value)
        timestamp = (snowflake >> 22) + 1288834974657
        machine_id = (snowflake & 0x3FF000) >> 12
        sequence = snowflake & 0xFFF

    except Exception as e:
        log.exception(f'Exception parsing snowflake: {e}')
        return

    node.hover = 'Twitter Snowflakes are time-based IDs. ' \
                 '<a href="https://blog.twitter.com/engineering/en_us/a/2010/announcing-snowflake.html" ' \
                 'target="_blank">[ref]</a>'

    unfurl.add_to_queue(
        data_type='epoch-milliseconds', key=None, value=timestamp, label=f'Timestamp: {timestamp}',
        hover='The first value in a Twitter Snowflake is a timestamp',
        parent_id=node.node_id, incoming_edge_config=twitter_snowflake_edge)

    unfurl.add_to_queue(
        data_type='integer', key=None, value=machine_id, label=f'Machine ID: {machine_id}',
        hover='The second value in a Twitter Snowflake is the machine ID',
        parent_id=node.node_id, incoming_edge_config=twitter_snowflake_edge)

    unfurl.add_to_queue(
        data_type='integer', key=None, value=sequence, label=f'Sequence: {sequence}',
        hover='For every ID that is generated, this number is incremented and rolls over every 4096',
        parent_id=node.node_id, incoming_edge_config=twitter_snowflake_edge)


def run(unfurl, node):
    if 'twitter.com' in unfurl.find_preceding_domain(node):
        # Make sure potential snowflake is reasonable: between 2015-02-01 & 2022-03-05
        if node.data_type == 'url.path.segment' and \
                unfurl.check_if_int_between(node.value, 561675293291446272, 1500000000000000001):
            parse_twitter_snowflake(unfurl, node)

        elif node.data_type == 'url.query.pair':
            if node.key == 's':
                sharing_codes = {
                    '19': ' from Android',
                    '20': ' from Twitter Web',
                    '21': ' from iOS'
                }

                unfurl.add_to_queue(
                    data_type='descriptor', key=None, value=f'Tweet was shared{sharing_codes.get(node.value, "")}',
                    hover='The sharing platform is a best guess based on observations; if you find a '
                          'new sharing code, please let us know',
                    parent_id=node.node_id, incoming_edge_config=twitter_edge)
