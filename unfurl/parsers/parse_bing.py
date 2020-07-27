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
            if node.key == 'pq':
                unfurl.add_to_queue(
                    data_type='descriptor', key=None, value=f'"Previous" Search Query: {node.value}',
                    hover='Previous terms entered by the user; auto-complete or suggestions <br>'
                          'may have been used to reach the actual search terms (in <b>q</b>)',
                    parent_id=node.node_id, incoming_edge_config=bing_edge)

            elif node.key == 'q':
                unfurl.add_to_queue(
                    data_type='descriptor', key=None, value=f'Search Query: {node.value}',
                    hover='Terms used in the Bing search', parent_id=node.node_id, incoming_edge_config=bing_edge)

            elif node.key == 'first':
                unfurl.add_to_queue(
                    data_type='descriptor', key=None, value=f'Starting Result: {node.value}',
                    hover='Bing search by default shows 8 results per page; higher <br>'
                          '"first" values may indicate browsing more subsequent results pages.',
                    parent_id=node.node_id, incoming_edge_config=bing_edge)
