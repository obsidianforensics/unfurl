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

import base64
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


def parse_twitter_snowflake(unfurl, node, encoding_type='integer', on_twitter=True):
    # Ref: https://blog.twitter.com/engineering/en_us/a/2010/announcing-snowflake.html
    #      https://ws-dl.blogspot.com/2019/08/2019-08-03-tweetedat-finding-tweet.html
    if encoding_type == 'integer':
        try:
            snowflake = int(node.value)
            timestamp = (snowflake >> 22) + 1288834974657
            machine_id = (snowflake & 0x3FF000) >> 12
            sequence = snowflake & 0xFFF
            assert 0 <= sequence <= 4096, \
                f'Sequence number should be between 0 and 4096; got {sequence}'

        except Exception as e:
            log.exception(f'Exception parsing snowflake: {e}')
            return

    # Ref: https://www.hackerfactor.com/blog/index.php?/archives/634-Name-Dropping.html
    # So far, I've only observed this in file attachments (images) to tweets. This format
    # also has three extra bytes at the "end" (LSBs); I don't know their function.
    elif encoding_type == 'base64':
        try:
            padded_value = unfurl.add_b64_padding(node.value)
            snowflake_bytes = base64.urlsafe_b64decode(padded_value)
            snowflake_int = int.from_bytes(snowflake_bytes, 'big')
            timestamp = (snowflake_int >> 46) + 1288834974657
            machine_id = (snowflake_int & 0x3FF000000000) >> 36
            sequence = (snowflake_int & 0xFFF000000) >> 24
            assert 0 <= sequence <= 4096, \
                f'Sequence number should be between 0 and 4096; got {sequence}'

            # Since we are trying to parse things that might not be valid, make sure the decoded
            # timestamp is "reasonable" (between 2010-11 (the Snowflake epoch) and 2024-01
            if not 1288834974657 < timestamp < 1704070800000:
                return

        except Exception as e:
            log.warning(f'Exception parsing snowflake: {e}')
            return
    else:
        return

    if on_twitter:
        node.hover = 'Twitter Snowflakes are time-based IDs. ' \
                     '<a href="https://blog.twitter.com/engineering/en_us/a/2010/announcing-snowflake.html" ' \
                     'target="_blank">[ref]</a>'

    else:
        unfurl.add_to_queue(
            data_type='descriptor', key=None, value='File may originally be from Twitter (based on file name)',
            hover='File name is consistent with Twitter\'s naming scheme for image attachments. The name also contains '
                  'an embedded timestamp.', parent_id=node.node_id, incoming_edge_config=twitter_snowflake_edge)

    unfurl.add_to_queue(
        data_type='epoch-milliseconds', key=None, value=timestamp, label=f'Timestamp: {timestamp}',
        hover='The first value in a Twitter Snowflake is a timestamp',
        parent_id=node.node_id, incoming_edge_config=twitter_snowflake_edge)

    unfurl.add_to_queue(
        data_type='integer', key=None, value=machine_id, label=f'Machine ID: {machine_id}',
        hover='The second value in a Twitter Snowflake is the machine ID. A machine ID can be further divided '
              'into a datacenter ID (first 5 bits) and worker ID (last 5 bits)',
        parent_id=node.node_id, incoming_edge_config=twitter_snowflake_edge)

    unfurl.add_to_queue(
        data_type='integer', key=None, value=sequence, label=f'Sequence: {sequence}',
        hover='For every ID that is generated, this number is incremented and rolls over every 4096',
        parent_id=node.node_id, incoming_edge_config=twitter_snowflake_edge)


def run(unfurl, node):
    preceding_domain = unfurl.find_preceding_domain(node)
    if preceding_domain == 'twitter.com':
        # Make sure potential snowflake is reasonable: between 2015-02-01 & 2024-06-10
        if node.data_type == 'url.path.segment' and \
                unfurl.check_if_int_between(node.value, 261675293291446272, 1800000000000000001):
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

    # I've only seen `pbs.twimg.com`, but there could be other subdomains used for image attachments to tweets
    elif '.twimg.com' in preceding_domain:
        if node.data_type == 'url.path.segment':
            # Viewing an image attached to a tweet
            # Ex: https://pbs.twimg.com/media/ErD8xv0VkAIBJe7?format=jpg&name=medium
            if unfurl.check_sibling_nodes(node, data_type='url.path.segment', key=1, value='media'):
                if node.key == 2:
                    parse_twitter_snowflake(unfurl, node, encoding_type='base64')

    # It's possible an image from Twitter was saved off and then uploaded somewhere else. The file name
    # pattern appears fairly unique, so if we see a file name that matches it and decodes to a "reasonable"
    # timestamp, show it in the graph.
    elif node.data_type == 'file.name' and len(node.value) == 15:
        parse_twitter_snowflake(unfurl, node, encoding_type='base64', on_twitter=False)
