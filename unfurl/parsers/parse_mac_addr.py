# Copyright 2024 Ryan Benson
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

import netaddr
from unfurl import utils

import logging
log = logging.getLogger(__name__)

uuid_edge = {
    'color': {
        'color': 'red'
    },
    'title': 'MAC Parsing Functions',
    'label': '🖧'
}


def run(unfurl, node):
    if node.data_type == 'mac-address':
        vendor_lookup = None
        try:
            mac_addr = netaddr.EUI(node.value)
            vendor_lookup = mac_addr.oui.registration().org
        except netaddr.NotRegisteredError:
            pass
        except Exception as e:
            log.exception(f'Exception while parsing MAC address: {e}')

        if vendor_lookup:
            unfurl.add_to_queue(
                data_type="mac-address.vendor", key=None, value=vendor_lookup, label=f'Vendor: {vendor_lookup}',
                parent_id=node.node_id, incoming_edge_config=uuid_edge)

        if node.value[1] in ['2', '6', 'A', 'E', 'a', 'e']:
            unfurl.add_to_queue(
                data_type="descriptor", key=None,
                value='MAC address may be randomized (locally-administered & unicast bits set)',
                parent_id=node.node_id, incoming_edge_config=uuid_edge)

    else:
        long_int = utils.long_int_re.fullmatch(str(node.value))
        m = utils.mac_addr_re.fullmatch(str(node.value))
        if m and not long_int:
            u = m.group('mac_addr')

            # Check if we need to add colons
            if len(u) == 12:
                pretty_mac = ':'.join([u[i] + u[i + 1] for i in range(0, 12, 2)])
            else:
                pretty_mac = u.upper()

            unfurl.add_to_queue(
                data_type='mac-address', key=None, value=pretty_mac, label=f'MAC address: {pretty_mac}',
                parent_id=node.node_id, incoming_edge_config=uuid_edge)
