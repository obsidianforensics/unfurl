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

import maclookup
import re

uuid_edge = {
    'color': {
        'color': 'red'
    },
    'title': 'MAC Parsing Functions',
    'label': '🖧'
}


def run(unfurl, node):
    if not node.data_type == 'mac-address':
        long_int = re.fullmatch(r'\d{12,}', str(node.value))
        m = re.match(r'(?P<mac_addr>[0-9A-Fa-f]{12}|([0-9A-Fa-f]:){6})$', str(node.value))
        if m and not long_int:
            u = m.group('mac_addr')

            # Check if we need to add colons
            if len(u) == 12:
                pretty_mac = f'{u:0{12}X}'
                pretty_mac = ':'.join([pretty_mac[i]+pretty_mac[i+1] for i in range(0, 12, 2)])

            else:
                pretty_mac = u.upper()

            # TODO: add detection for randomly generated MACs (random 48-bit number with its eighth bit set to 1 as
            #  recommended in RFC 4122)
            unfurl.add_to_queue(
                data_type='mac-address', key=None, value=pretty_mac, label=f'MAC address: {pretty_mac}',
                parent_id=node.node_id, incoming_edge_config=uuid_edge)

    elif node.data_type == 'mac-address' and unfurl.api_keys.get('macaddress_io'):
        client = maclookup.ApiClient(unfurl.api_keys.get('macaddress_io'))
        vendor_lookup = client.get_vendor(node.value).decode('utf-8')

        if vendor_lookup:
            unfurl.add_to_queue(
                data_type="mac-address.vendor", key=None, value=vendor_lookup, label=f'Vendor: {vendor_lookup}',
                parent_id=node.node_id, incoming_edge_config=uuid_edge)
