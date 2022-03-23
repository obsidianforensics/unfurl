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

discord_edge = {
    'color': {
        'color': '#7289da'
    },
    'title': 'Discord Snowflake',
    'label': '❄'
}


def parse_discord_snowflake(unfurl, node):
    try:
        snowflake = int(node.value)
    # Some non-integer values can appear here (like @me) instead; abandon parsing
    except ValueError:
        return

    try:
        # Ref: https://discordapp.com/developers/docs/reference#snowflakes
        timestamp = (snowflake >> 22) + 1420070400000
        worker_id = (snowflake & 0x3E0000) >> 17
        internal_process_id = (snowflake & 0x1F000) >> 17
        increment = snowflake & 0xFFF

    except Exception as e:
        log.exception(f'Exception parsing Discord snowflake: {e}')
        return

    node.hover = 'Discord Snowflakes are unique, time-based IDs. ' \
                 '<a href="https://discordapp.com/developers/docs/reference#snowflakes" target="_blank">[ref]</a>'

    unfurl.add_to_queue(
        data_type='epoch-milliseconds', key=None, value=timestamp, label=f'Timestamp:\n{timestamp}',
        hover='The first value in a Discord Snowflake is a timestamp associated with object creation',
        parent_id=node.node_id, incoming_edge_config=discord_edge)

    unfurl.add_to_queue(
        data_type='integer', key=None, value=worker_id, label=f'Worker ID: {worker_id}',
        hover='The second value in a Discord Snowflake is the internal worker ID',
        parent_id=node.node_id, incoming_edge_config=discord_edge)

    unfurl.add_to_queue(
        data_type='integer', key=None, value=internal_process_id, label=f'Process ID: {internal_process_id}',
        hover='The third value in a Discord Snowflake is the internal process ID',
        parent_id=node.node_id, incoming_edge_config=discord_edge)

    unfurl.add_to_queue(
        data_type='integer', key=None, value=increment, label=f'Increment: {increment}',
        hover='For every ID that is generated on that process, this number is incremented',
        parent_id=node.node_id, incoming_edge_config=discord_edge)


def run(unfurl, node):

    # Known patterns from main Discord site
    discord_domains = ['discordapp.com', 'discordapp.net', 'discord.com']
    if any(discord_domain in unfurl.find_preceding_domain(node) for discord_domain in discord_domains):
        if node.data_type == 'url.path.segment':
            # Viewing a channel on a server
            # Ex: https://discordapp.com/channels/427876741990711298/551531058039095296
            if unfurl.check_sibling_nodes(node, data_type='url.path.segment', key=1, value='channels'):
                if node.key == 2:
                    unfurl.add_to_queue(
                        data_type='description', key=None, value=None, label='Server ID',
                        hover='The timestamp in the associated Discord Snowflake is the time of Server creation',
                        parent_id=node.node_id, incoming_edge_config=discord_edge)
                    parse_discord_snowflake(unfurl, node)

                elif node.key == 3:
                    unfurl.add_to_queue(
                        data_type='description', key=None, value=None, label='Channel ID',
                        hover='The timestamp in the associated Discord Snowflake is the time of Channel creation '
                              'on the given Server',
                        parent_id=node.node_id, incoming_edge_config=discord_edge)
                    parse_discord_snowflake(unfurl, node)

                # Linking to a specific message
                # Ex: https://discordapp.com/channels/427876741990711298/537760691302563843/643183730227281931
                elif node.key == 4:
                    unfurl.add_to_queue(
                        data_type='description', key=None, value=None, label='Message ID',
                        hover='The timestamp in the associated Discord Snowflake is the time the Message was sent',
                        parent_id=node.node_id, incoming_edge_config=discord_edge)
                    parse_discord_snowflake(unfurl, node)

            # File Attachment URLs
            # Ex: https://cdn.discordapp.com/attachments/622136585277931532/626893414490832918/asdf.png
            elif unfurl.check_sibling_nodes(node, data_type='url.path.segment', key=1, value='attachments'):
                if node.key == 2:
                    unfurl.add_to_queue(
                        data_type='description', key=None, value=None, label='Channel ID',
                        hover='The timestamp in the associated Discord Snowflake is the time of channel creation',
                        parent_id=node.node_id, incoming_edge_config=discord_edge)
                    parse_discord_snowflake(unfurl, node)

                elif node.key == 3:
                    unfurl.add_to_queue(
                        data_type='description', key=None, value=None, label='File ID',
                        hover='The timestamp in the associated Discord Snowflake is the time the attachment '
                              'was uploaded.',
                        parent_id=node.node_id, incoming_edge_config=discord_edge)
                    parse_discord_snowflake(unfurl, node)

                elif node.key == 4:
                    unfurl.add_to_queue(
                        data_type='description', key=None, value=None, label='Attachment File Name',
                        parent_id=node.node_id, incoming_edge_config=discord_edge)

            # Check if the node's value would correspond to a Snowflake with timestamp between 2015-02 and 2022-07
            elif unfurl.check_if_int_between(node.value, 15000000000000000, 1000000000000000001):
                parse_discord_snowflake(unfurl, node)
