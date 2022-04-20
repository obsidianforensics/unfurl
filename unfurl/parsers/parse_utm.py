# Copyright 2022 Google LLC
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

utm_edge = {
    'color': {
        'color': 'green'
    },
    'title': 'UTM Parsing Functions',
    'label': 'UTM'
}


def run(unfurl, node):
    if node.data_type == 'url.query.pair':
        if node.key == 'utm_source':
            unfurl.add_to_queue(
                data_type='descriptor', key=None,
                value='Identifies which site sent the traffic (search engine, newsletter, etc)',
                hover='UTM (Urchin Tracking Module) parameters are used by websites to track effectiveness of '
                      'marketing campaigns. Unfurl\'s descriptions are of what each parameter is typically used '
                      'for, but site owners can customize them.',
                parent_id=node.node_id, incoming_edge_config=utm_edge)

        elif node.key == 'utm_medium':
            unfurl.add_to_queue(
                data_type='descriptor', key=None,
                value='Identifies the type of link clicked (email, cpc, etc)',
                hover='UTM (Urchin Tracking Module) parameters are used by websites to track effectiveness of '
                      'marketing campaigns. Unfurl\'s descriptions are of what each parameter is typically used '
                      'for, but site owners can customize them.',
                parent_id=node.node_id, incoming_edge_config=utm_edge)

        elif node.key == 'utm_campaign':
            unfurl.add_to_queue(
                data_type='descriptor', key=None,
                value='Identifies the specific product promotion or strategic campaign',
                hover='UTM (Urchin Tracking Module) parameters are used by websites to track effectiveness of '
                      'marketing campaigns. Unfurl\'s descriptions are of what each parameter is typically used '
                      'for, but site owners can customize them.',
                parent_id=node.node_id, incoming_edge_config=utm_edge)

        elif node.key == 'utm_content':
            unfurl.add_to_queue(
                data_type='descriptor', key=None,
                value='Identifies what the user clicked (text_link, top_banner, etc)',
                hover='UTM (Urchin Tracking Module) parameters are used by websites to track effectiveness of '
                      'marketing campaigns. Unfurl\'s descriptions are of what each parameter is typically used '
                      'for, but site owners can customize them.',
                parent_id=node.node_id, incoming_edge_config=utm_edge)

        elif node.key == 'utm_term':
            unfurl.add_to_queue(
                data_type='descriptor', key=None,
                value='Identifies search terms',
                hover='UTM (Urchin Tracking Module) parameters are used by websites to track effectiveness of '
                      'marketing campaigns. Unfurl\'s descriptions are of what each parameter is typically used '
                      'for, but site owners can customize them.',
                parent_id=node.node_id, incoming_edge_config=utm_edge)
