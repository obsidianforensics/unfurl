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

import os 
import requests
import json

bitly_edge = {
    'color': {
        'color': '#FFA500'
    },
    'title': 'Bitly URL Shortner ',
    'label': '🔗'
}
  

def expand_bitly_url(unfurl, node):
    # Ref: https://dev.bitly.com/v4/

    # generic token to be set in .env or in environment variables.
    token = os.getenv('token')
    r = requests.post('https://api-ssl.bitly.com/v4/expand', data=json.dumps({'bitlink_id': f"bit.ly/{node.value}" }), headers={'Content-Type':'application/json', 'Authorization': f'Bearer {token}'})       
    shortened_url = r.json()

    node.hover = 'Bitly URL Shortners contain a creation time.' \
                 '<a href="https://dev.bitly.com/v4/#operation/expandBitlink" ' \
                 'target="_blank">[ref]</a>'

    unfurl.add_to_queue(
        data_type='str', key=None, value=shortened_url["created_at"], label=f'Creation time: {shortened_url["created_at"]}',
        hover='Created time',
        parent_id=node.node_id, incoming_edge_config=bitly_edge)

    unfurl.add_to_queue(
        data_type='url', key=None, value=shortened_url["long_url"], label=f'Expanded URL: {shortened_url["long_url"]}',
        hover='Expanded URL',
        parent_id=node.node_id, incoming_edge_config=bitly_edge)


def run(unfurl, node):

    # Known pattern from twitter.com site
    if node.data_type == 'url.path.segment':
        if 'bit.ly' in unfurl.find_preceding_domain(node):
            expand_bitly_url(unfurl, node)
