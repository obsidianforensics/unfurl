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

mastodon_edge = {
    'color': {
        'color': '#419BDD'
    },
    'title': 'Mastodon Snowflake',
    'label': '❄'
}


def parse_mastodon_snowflake(unfurl, node):
    # Ref: https://github.com/tootsuite/mastodon/issues/1059
    #      https://github.com/tootsuite/mastodon/blob/master/lib/mastodon/snowflake.rb
    try:
        snowflake = int(node.value)
        seq_data = snowflake & 0xFF
        timestamp = (snowflake >> 16) 

    except Exception as e:
        print(e)
        return

    node.hover = 'Mastodon Snowflakes are time-based IDs similar to those of Twitter Snowflakes. ' \
                 '<a href="https://blog.twitter.com/engineering/en_us/a/2010/announcing-snowflake.html" ' \
                 'target="_blank">[ref]</a>'

    unfurl.add_to_queue(
        data_type='epoch-milliseconds', key=None, value=timestamp, label=f'Timestamp: {timestamp}',
        hover='The first 16 bits value in a Mastodon Snowflake is a timestamp.',
        parent_id=node.node_id, incoming_edge_config=mastodon_edge)

    unfurl.add_to_queue(
         data_type='integer', key=None, value=seq_data, label=f'Sequence data: {seq_data}',
         hover="The 'sequence data' is intended to be unique within a given millisecond. It is a 2 byte value.",
         parent_id=node.node_id, incoming_edge_config=mastodon_edge)


def run(unfurl, node):

    # Known pattern from mastodon.social site
    if node.data_type == 'url.path.segment':
        # Mastodon by nature is federated and there are many, many domains hosting instances. This list was taken
        # from instances.social, sorted by popularity.
        mastodon_domains = ['pawoo.net', 'mastodon.social', 'mstdn.jp', 'switter.at', 'mastodon.cloud', 'baraag.net',
                            'sinblr.com', 'mastodon.xyz', 'mastodon.technology', 'mstdn.io', 'infosec.exchange']

        # Check if node is a child of a mastodon domain, is an integer, & timestamp would be between 2015-01 and 2030-01
        if any(mastodon_domain in unfurl.find_preceding_domain(node) for mastodon_domain in mastodon_domains) and \
                unfurl.check_if_int_between(node.value, 93065733734400000, 124089536413761540):
            parse_mastodon_snowflake(unfurl, node)
