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

discord_edge = {
    'color': {
        'color': '#7289da'
    },
    'title': 'Discord Snowflake',
    'label': '❄'
}


def parse_discord_snowflake(unfurl, node):
    try:
        # Ref: https://discordapp.com/developers/docs/reference#snowflakes
        snowflake = int(node.value)
        timestamp = (snowflake >> 22) + 1420070400000
        worker_id = (snowflake & 0x3E0000) >> 17
        internal_process_id = (snowflake & 0x1F000) >> 17
        increment = snowflake & 0xFFF

    except Exception as e:
        print(e)
        return

    node.hover = 'Discord Snowflakes are unique, time-based IDs. ' \
                 '<a href="https://discordapp.com/developers/docs/reference#snowflakes" target="_blank">[ref]</a>'

    unfurl.add_to_queue(
        data_type='epoch-milliseconds', key=None, value=timestamp, label='Timestamp: {}'.format(timestamp),
        hover='The first value in a Discord Snowflake is a timestamp',
        parent_id=node.node_id, incoming_edge_config=discord_edge)

    unfurl.add_to_queue(
        data_type='integer', key=None, value=worker_id, label='Worker ID: {}'.format(worker_id),
        hover='The second value in a Discord Snowflake is the internal worker ID',
        parent_id=node.node_id, incoming_edge_config=discord_edge)

    unfurl.add_to_queue(
        data_type='integer', key=None, value=internal_process_id, label='Process ID: {}'.format(internal_process_id),
        hover='The third value in a Discord Snowflake is the internal process ID',
        parent_id=node.node_id, incoming_edge_config=discord_edge)

    unfurl.add_to_queue(
        data_type='integer', key=None, value=increment, label='Increment: {}'.format(increment),
        hover='For every ID that is generated on that process, this number is incremented',
        parent_id=node.node_id, incoming_edge_config=discord_edge)


def run(unfurl, node):

    # Known pattern from main discordapp.com site
    if node.data_type == 'url.path.segment' and node.value != 'channels':
        if 'discordapp.com' in unfurl.find_preceding_domain(node):
            parse_discord_snowflake(unfurl, node)

    # TODO: Parse attachment URLs
    # Ex: https://cdn.discordapp.com/attachments/622136585277931532/626893414490832918/Discord_Developer_Portal_Snowflakes.pdf
    #              ^                     ^        ^ uploader ID?      ^ file id, with timestamp of upload     ^ filename

    # Check if the node's value would correspond to a Snowflake with timestamp between 2015-02 and 2020-04
    elif unfurl.check_if_int_between(node.value, 15000000000000000, 700000000000000000):
        parse_discord_snowflake(unfurl, node)
