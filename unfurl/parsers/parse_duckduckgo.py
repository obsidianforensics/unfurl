# Copyright 2020 Moshe Kaplan
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

duckduckgo = {
    'color': {
        'color': '#D74F38'
    },
    'title': 'DuckDuckGo-related Parsing Functions',
    'label': '🦆'
}


def run(unfurl, node):
    # Some URL parameters are from https://duckduckgo.com/params
    if node.data_type == 'url.query.pair':
        if 'duckduckgo' in unfurl.find_preceding_domain(node):

            if node.key == 'df':
                df_mappings = {
                    'd': 'Past Day',
                    'm': 'Past Month',
                    'w': 'Past Week',
                    'y': 'Past Year'
                }
                value = df_mappings.get(node.value, 'Unknown')
                unfurl.add_to_queue(
                    data_type='descriptor', key=None, value=f'Time Period: {value}',
                    hover='DuckDuckGo Search Period', parent_id=node.node_id, incoming_edge_config=duckduckgo)

            elif node.key == 'ia':
                ia_mappings = {
                    'images': 'Image Search',
                    'news': 'News Search',
                    'videos': 'Video Search',
                    'web': 'Web Search',
                    'definition': 'Definition',
                    'shopping': 'Shopping Search'
                }
                value = ia_mappings.get(node.value, 'Unknown')
                unfurl.add_to_queue(
                    data_type='descriptor', key=None, value=f'Search Type: {value}',
                    hover='DuckDuckGo Search Type', parent_id=node.node_id, incoming_edge_config=duckduckgo)

            elif node.key == 'q':
                unfurl.add_to_queue(
                    data_type='descriptor', key=None, value=f'Search Query: {node.value}',
                    hover='Terms used in the DuckDuckGo search', parent_id=node.node_id, incoming_edge_config=duckduckgo)

            # ref: https://help.duckduckgo.com/privacy/t/
            elif node.key == 't':
                unfurl.add_to_queue(
                    data_type='descriptor', key=None, value=f'Tracking Code: {node.value}',
                    hover='To assign advertising revenue and collect anonymous aggregate usage <br>information, '
                          'developers add a unique "&t=" parameter to searches <br>made through their applications. '
                          '<a href="https://help.duckduckgo.com/privacy/t/" target="_blank">[ref]</a>',
                    parent_id=node.node_id, incoming_edge_config=duckduckgo)
