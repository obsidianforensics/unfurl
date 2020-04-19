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
import os


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


def expand_url_via_redirect_header(base_url, shortcode):
    r = requests.get(f'{base_url}{shortcode}', allow_redirects=False)

    if r.status_code in [301, 302]:
        return r.headers['Location']
    else:
        return False


def run(unfurl, node):
    bitly_domains = ['bit.ly', 'bitly.com', 'j.mp']
    if node.data_type == 'url.path':
        if any(bitly_domain in unfurl.find_preceding_domain(node) for bitly_domain in bitly_domains):
            expanded_info = expand_bitly_url(node.value[1:], unfurl.api_keys.get('bitly', os.environ.get('bitly')))

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

            return

        redirect_expands = [
            {'domain': 'bit.do', 'base_url': 'https://bit.do/'},
            {'domain': 'buff.ly', 'base_url': 'https://buff.ly/'},
            {'domain': 'db.tt', 'base_url': 'https://db.tt/'},
            {'domain': 'dlvr.it', 'base_url': 'https://dlvr.it/'},
            {'domain': 'goo.gl', 'base_url': 'https://goo.gl/'},
            {'domain': 'ift.tt', 'base_url': 'https://ift.tt/'},
            {'domain': 'is.gd', 'base_url': 'https://is.gd/'},
            {'domain': 'lnkd.in', 'base_url': 'https://www.linkedin.com/slink?code='},
            {'domain': 'ow.ly', 'base_url': 'http://ow.ly/'},
            {'domain': 'reut.rs', 'base_url': 'https://reut.rs/'},
            {'domain': 't.co', 'base_url': 'https://t.co/'},
            {'domain': 'tr.im', 'base_url': 'https://tr.im/'},
            {'domain': 'trib.al', 'base_url': 'https://trib.al/'},
            {'domain': 'tinyurl.com', 'base_url': 'https://tinyurl.com/'},
            {'domain': 'x.co', 'base_url': 'https://x.co/'},
        ]

        for redirect_expand in redirect_expands:
            if redirect_expand['domain'] in unfurl.find_preceding_domain(node):
                expanded_url = expand_url_via_redirect_header(redirect_expand['base_url'], node.value[1:])
                if expanded_url:
                    unfurl.add_to_queue(
                        data_type='url', key=None, value=expanded_url,
                        label=f'Expanded URL: {expanded_url}',
                        hover=f'Expanded URL, retrieved from {redirect_expand["domain"]} via "Location" header',
                        parent_id=node.node_id, incoming_edge_config=shortlink_edge)
