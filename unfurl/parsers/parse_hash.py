# Copyright 2021 Google LLC
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

import name_that_hash
import re
import requests

hash_edge = {
    'color': {
        'color': '#4A93AE'
    },
    'title': 'Hash Identification Functions',
    'label': '#'
}

hash_lookup_edge = {
    'color': {
        'color': '#4A93AE'
    },
    'title': 'Hash Lookup Functions',
    'label': '#'
}


def nitrxgen_md5_lookup(value):
    response = requests.get(f'https://www.nitrxgen.net/md5db/{value}', verify=False).text

    if response:
        return response
    else:
        return False


def virustotal_lookup(unfurl, hash_value):

    response = requests.get(f'https://www.virustotal.com/api/v3/files/{hash_value}',
                            headers={'x-apikey': unfurl.api_keys.get('virustotal')})

    if response.status_code == 200:
        try:
            result = response.json()
            return result['data']['attributes']
        except:
            return False


def run(unfurl, node):

    # if node.data_type in ('url.query.pair', 'string'):
    # if node.data_type.startswith(('uuid', 'hash')):
    if node.data_type.startswith('uuid'):
        return

    if node.data_type.startswith('hash'):
        if node.data_type == 'hash.md5':
            hash_plaintext = nitrxgen_md5_lookup(node.value)

            if hash_plaintext:
                unfurl.add_to_queue(
                    data_type=f'text', key='Plaintext',
                    value=hash_plaintext,
                    hover='Queried Nitrxgen database of MD5 hashes and found a matching plaintext value',
                    parent_id=node.node_id, incoming_edge_config=hash_lookup_edge)

        if node.data_type in ('hash.md5', 'hash.sha-1', 'hash.sha-256',):
            vt_results = virustotal_lookup(unfurl, node.value)
            if vt_results:
                label_text = 'Hash found on VirusTotal'
                if vt_results.get("type_description"):
                    label_text += f'\nFile Type: {vt_results.get("type_description")};'

                if vt_results.get("meaningful_name"):
                    label_text += f'\nName: {vt_results.get("meaningful_name")};'

                if vt_results.get("reputation"):
                    label_text += f'\nReputation: {vt_results.get("reputation")};'

                unfurl.add_to_queue(
                    data_type=f'text', key='Hash found on VirusTotal',
                    value=None, label=label_text,
                    hover='Queried VirusTotal with the hash value and found a match.',
                    parent_id=node.node_id, incoming_edge_config=hash_lookup_edge)

    else:
        if not isinstance(node.value, (bytes, str)):
            return

        digits_re = re.compile(r'\d')
        letters_re = re.compile(r'[A-Z]', flags=re.IGNORECASE)
        hex_re = re.compile(r'^[A-F0-9]+$', flags=re.IGNORECASE)

        try:
            # Filter for values that are only hex chars (A-F,0-9) and contains both a letter and number.
            # This could conceivably filter out valid hashes, but will filter out many more invalid values.
            if hex_re.match(node.value) and digits_re.search(node.value) and letters_re.search(node.value):

                name_that_hash_results = name_that_hash.runner.api_return_hashes_as_dict([node.value])

                if not name_that_hash_results.get(node.value):
                    return

                hash_results = name_that_hash_results[node.value]

                hash_hover = f'This is potentially a <b>{hash_results[0]["name"]}</b> hash.'
                if len(hash_results) > 3:
                    hash_hover = f'This is potentially a <b>{hash_results[0]["name"]}</b> hash, but it also matches '\
                                 f'the format <br>of <b>{len(hash_results)}</b> other hash types, including '\
                                 f'<b>{hash_results[1]["name"]}</b> and <b>{hash_results[2]["name"]}</b>.'
                if hash_results:
                    unfurl.add_to_queue(
                        data_type=f'hash.{hash_results[0]["name"].lower()}', key=f'{hash_results[0]["name"]} Hash',
                        value=node.value, label=f'Potential {hash_results[0]["name"]} hash',
                        hover=hash_hover, parent_id=node.node_id, incoming_edge_config=hash_edge)

        except Exception as e:
            pass
