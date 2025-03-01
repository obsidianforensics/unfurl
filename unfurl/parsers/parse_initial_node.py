# Copyright 2025 Ryan Benson LLC
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

import re

b64_edge = {
    'color': {
        'color': '#2C63FF'
    },
    'title': 'Initial Cleaning Functions',
    'label': '🧹'
}


def run(unfurl, node):

    if node.node_id != 1 or not isinstance(node.value, str):
        return

    if ' ' in node.value:
        cleaned_value = node.value.replace(' ', '')
        unfurl.add_to_queue(data_type=node.data_type, key=node.key, value=cleaned_value,
                            hover='Removed whitespace from input value',
                            parent_id=node.node_id, incoming_edge_config=b64_edge)

    quoted_re = re.fullmatch(r'["\'](.*)["\']', node.value)
    if quoted_re:
        unfurl.add_to_queue(data_type=node.data_type, key=node.key, value=quoted_re.group(1),
                            hover='Removed outer quotes (" or \') from input value',
                            parent_id=node.node_id, incoming_edge_config=b64_edge)
