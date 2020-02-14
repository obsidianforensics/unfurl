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

import requests
import json

shortlink_edge = {
    'color': {
        'color': '#E7572C'
    },
    'title': 'URL Shortener Parser',
    'label': '🔗'
}
  

def expand_bitly_url(bitlink_id, api_key):
    # Ref: https://dev.bitly.com/v4/

    r = requests.post(
        'https://api-ssl.bitly.com/v4/expand',
        data=json.dumps({'bitlink_id': f'bit.ly/{bitlink_id}'}),
        headers={'Content-Type': 'application/json', 'Authorization': f'Bearer {api_key}'})

    if r.status_code == 200:
        return r.json()
    else:
        return False


def expand_tinyurl(tinyurl):
    r = requests.get(f'https://tinyurl.com/{tinyurl}', allow_redirects=False)

    if r.status_code == 301:
        return r.headers['Location']
    else:
        return False


def run(unfurl, node):
    bitly_domains = ['bit.ly', 'bitly.com', 'j.mp']
    if node.data_type == 'url.path':
        if any(bitly_domain in unfurl.find_preceding_domain(node) for bitly_domain in bitly_domains):
            expanded_info = expand_bitly_url(node.value[1:], unfurl.api_keys.get('bitly'))

            if not expanded_info:
                return

            node.hover = 'Bitly Short Links can be expanded via the Bitly API to show the ' \
                         '"long" URL and the creation time of the short-link.' \
                         '<a href="https://dev.bitly.com/v4/#operation/expandBitlink" ' \
                         'target="_blank">[ref]</a>'

            if expanded_info['created_at'].endswith('+0000'):
                expanded_info['created_at'] = expanded_info['created_at'][:-5]

            if expanded_info['created_at'][10] == 'T':
                expanded_info['created_at'] = f'{expanded_info["created_at"][:10]} {expanded_info["created_at"][11:]}'

            unfurl.add_to_queue(
                data_type='description', key=None, value=expanded_info['created_at'],
                label=f'Creation Time:\n{expanded_info["created_at"]}',
                hover='Short-link creation time, retrieved from Bitly API',
                parent_id=node.node_id, incoming_edge_config=shortlink_edge)

            unfurl.add_to_queue(
                data_type='url', key=None, value=expanded_info['long_url'],
                label=f'Expanded URL: {expanded_info["long_url"]}', hover='Expanded URL, retrieved from Bitly API',
                parent_id=node.node_id, incoming_edge_config=shortlink_edge)

        elif 'tinyurl.com' in unfurl.find_preceding_domain(node):
            expanded_url = expand_tinyurl(node.value)
            if expanded_url:
                unfurl.add_to_queue(
                    data_type='url', key=None, value=expanded_url,
                    label=f'Expanded URL: {expanded_url}', hover='Expanded URL, retrieved from TinyURL',
                    parent_id=node.node_id, incoming_edge_config=shortlink_edge)