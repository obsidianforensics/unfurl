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


dropbox_edge = {
    'color': {
        'color': '#2C6AFB'
    },
    'title': 'Dropbox Parsing Functions',
    'label': 'DB'
}


def run(unfurl, node):
    # References: https://www.atropos4n6.com/cloud-forensics/artifacts-of-dropbox-usage-on-windows-10-part-2/
    if 'dropbox.com' in unfurl.find_preceding_domain(node):
        if node.data_type == 'url.path' and node.value.startswith('/home'):
            _, viewed_directory = node.value.split('/home', 1)
            viewed_value = ''
            if viewed_directory and viewed_directory != '/':
                viewed_value = f'directory "{viewed_directory[1:]}" from '
            unfurl.add_to_queue(
                data_type='descriptor', key=None, value=f'Viewing {viewed_value}the user\'s "All Files" page',
                parent_id=node.node_id, incoming_edge_config=dropbox_edge)

        elif node.data_type == 'url.path' and node.value.startswith('/h'):
            _, viewed_directory = node.value.split('/h', 1)
            viewed_value = ''
            if viewed_directory and viewed_directory != '/':
                viewed_value = f'directory "{viewed_directory[1:]}" from '
            unfurl.add_to_queue(
                data_type='descriptor', key=None, value=f'Viewing {viewed_value}the user\'s Dropbox "Home" page',
                hover='The Dropbox "Home" page has suggestions, recent, and starred items.',
                parent_id=node.node_id, incoming_edge_config=dropbox_edge)

        elif node.data_type == 'url.query.pair':
            if node.key == 'preview':
                unfurl.add_to_queue(
                    data_type='descriptor', key=None, value=f'File "{node.value}" is being previewed',
                    parent_id=node.node_id, incoming_edge_config=dropbox_edge)
