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

bing_edge = {
    'color': {
        'color': '#228372'
    },
    'title': 'Bing-related Parsing Functions',
    'label': 'B'
}


def run(unfurl, node):
    if node.data_type == 'url.query.pair':
        if 'bing' in unfurl.find_preceding_domain(node):

            # Many of the corresponding names of these QSPs were found on bing.com/as/init?pt...
            # Their function is not completely understood.
            if node.key == 'pq':
                unfurl.add_to_queue(
                    data_type='descriptor', key=None, value=f'"Partial" Search Query: {node.value}',
                    hover='Partial search terms entered by the user; auto-complete or suggestions <br>'
                          'may have been used to reach the actual search terms (in <b>q</b>)',
                    parent_id=node.node_id, incoming_edge_config=bing_edge)

            elif node.key == 'q':
                unfurl.add_to_queue(
                    data_type='descriptor', key=None, value=f'Search Query: {node.value}',
                    hover='Terms used in the Bing search', parent_id=node.node_id, incoming_edge_config=bing_edge)

            elif node.key == 'cp':
                unfurl.add_to_queue(
                    data_type='descriptor', key=None, value=f'Cursor Position: {node.value}',
                    parent_id=node.node_id, incoming_edge_config=bing_edge)

            elif node.key == 'cvid':
                unfurl.add_to_queue(
                    data_type='descriptor', key=None, value=f'Conversation ID',
                    parent_id=node.node_id, incoming_edge_config=bing_edge)

            elif node.key == 'sc':
                unfurl.add_to_queue(
                    data_type='descriptor', key=None, value=f'Suggestion Count: {node.value}',
                    parent_id=node.node_id, incoming_edge_config=bing_edge)

            elif node.key == 'sp':
                unfurl.add_to_queue(
                    data_type='descriptor', key=None, value=f'Suggestion Position: {node.value}',
                    hover='An sp of "-1" indicates no suggestion was used for the search',
                    parent_id=node.node_id, incoming_edge_config=bing_edge)

            elif node.key == 'qs':
                unfurl.add_to_queue(
                    data_type='descriptor', key=None, value=f'Suggestion Type: {node.value}',
                    parent_id=node.node_id, incoming_edge_config=bing_edge)

            elif node.key == 'qsc':
                unfurl.add_to_queue(
                    data_type='descriptor', key=None, value=f'Preview Pane Suggestion Type: {node.value}',
                    parent_id=node.node_id, incoming_edge_config=bing_edge)

            elif node.key == 'sk':
                unfurl.add_to_queue(
                    data_type='descriptor', key=None, value=f'Skip Value: {node.value}',
                    parent_id=node.node_id, incoming_edge_config=bing_edge)

            elif node.key == 'skc':
                unfurl.add_to_queue(
                    data_type='descriptor', key=None, value=f'Preview Pane Skip Value: {node.value}',
                    parent_id=node.node_id, incoming_edge_config=bing_edge)

            elif node.key == 'ghc':
                unfurl.add_to_queue(
                    data_type='descriptor', key=None, value=f'Ghosting: {node.value}',
                    parent_id=node.node_id, incoming_edge_config=bing_edge)

            elif node.key == 'ds':
                unfurl.add_to_queue(
                    data_type='descriptor', key=None, value=f'Data Set: {node.value}',
                    parent_id=node.node_id, incoming_edge_config=bing_edge)

            elif node.key == 'sid':
                unfurl.add_to_queue(
                    data_type='descriptor', key=None, value=f'Session ID: {node.value}',
                    parent_id=node.node_id, incoming_edge_config=bing_edge)

            elif node.key == 'qt':
                unfurl.add_to_queue(
                    data_type='descriptor', key=None, value=f'Timestamp: {node.value}',
                    parent_id=node.node_id, incoming_edge_config=bing_edge)

            elif node.key == 'ig':
                unfurl.add_to_queue(
                    data_type='descriptor', key=None, value=f'Impression GUID: {node.value}',
                    parent_id=node.node_id, incoming_edge_config=bing_edge)

            elif node.key == 'bq':
                unfurl.add_to_queue(
                    data_type='descriptor', key=None, value=f'Base Query: {node.value}',
                    parent_id=node.node_id, incoming_edge_config=bing_edge)

            elif node.key == 'nclid':
                unfurl.add_to_queue(
                    data_type='descriptor', key=None, value=f'Hashed MUID: {node.value}',
                    parent_id=node.node_id, incoming_edge_config=bing_edge)

            elif node.key == 'hgr':
                unfurl.add_to_queue(
                    data_type='descriptor', key=None, value=f'Home Geographic Region: {node.value}',
                    parent_id=node.node_id, incoming_edge_config=bing_edge)

            elif node.key == 'first':
                unfurl.add_to_queue(
                    data_type='descriptor', key=None, value=f'Starting Result: {node.value}',
                    hover='Bing search by default shows 8 results per page; higher <br>'
                          '"first" values may indicate browsing more subsequent results pages.',
                    parent_id=node.node_id, incoming_edge_config=bing_edge)
