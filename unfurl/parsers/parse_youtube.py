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


youtube_edge = {
    'color': {
        'color': '#ff0000'
    },
    'title': 'Youtube Parsing Functions',
    'label': 'Y'
}


def run(unfurl, node):
    youtube_domains = ['youtube.com', 'youtu.be']
    if any(youtube_domain in unfurl.find_preceding_domain(node) for youtube_domain in youtube_domains):
        if node.key == 't':
            param_text = f'The youtube video will begin playing at {str(node.value)} seconds.'
            unfurl.add_to_queue(
                data_type='descriptor', key=None, value=node.value, label=param_text,
                parent_id=node.node_id, incoming_edge_config=youtube_edge)
