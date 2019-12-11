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

import re
import uuid

uuid_edge = {
    'color': {
        'color': 'orange'
    },
    'title': 'UUID Parsing Functions',
    'label': 'UU'
}


def run(unfurl, node):
    if not node.data_type.startswith('uuid'):
        m = re.match(r'(?P<uuid>[0-9A-Fa-f]{8}-?([0-9A-Fa-f]{4}-?){3}(?P<mac>[0-9A-Fa-f]{12}))', str(node.value))
        if m:
            u = m.group('uuid')
            unfurl.add_to_queue(data_type="uuid", key=None, value=u, label="UUID: {}".format(u),
                                parent_id=node.node_id, incoming_edge_config=uuid_edge)

    elif node.data_type == 'uuid':
        u = uuid.UUID(node.value)
        # TODO: reference: http://www.mahonri.info/cgi/uuid.cgi
        if u.version == 1:
            unfurl.add_to_queue(data_type="uuid-parsed", key=None, value=node.value,
                                label="Version 1 UUID is based on time and MAC address",
                                parent_id=node.node_id, incoming_edge_config=uuid_edge)

            # Timestamp is 60-bits, the number of 100-nanosecond intervals since midnight 15 October 1582 Coordinated
            # Universal Time (UTC). The offset to the Unix epoch is 12219292800000 milliseconds. Divide ts by 10000
            # to go from 100-ns intervals to milliseconds.x
            timestamp = u.time/10000 - 12219292800000
            unfurl.add_to_queue(data_type="epoch-milliseconds", key=None, value=timestamp,
                                label="Time generated: {}".format(timestamp),
                                parent_id=node.node_id, incoming_edge_config=uuid_edge)

            # TODO: add detection for randomly generated MACs (random 48-bit number with its eighth bit set to 1 as
            #  recommended in RFC 4122)
            pretty_mac = '{value:0{length}X}'.format(value=u.node, length=12)
            pretty_mac = ':'.join([pretty_mac[i]+pretty_mac[i+1] for i in range(0, 12, 2)])

            unfurl.add_to_queue(
                data_type='mac-address', key=None, value=pretty_mac, label="MAC address: {}".format(pretty_mac),
                parent_id=node.node_id, incoming_edge_config=uuid_edge)

        elif u.version == 3:
            unfurl.add_to_queue(
                data_type="uuid-parsed", key=None, value=node.value,
                label="Version 3 UUID is generated based on a namespace and a name, which are combined and hashed using MD5",
                parent_id=node.node_id, incoming_edge_config=uuid_edge)

        elif u.version == 4:
            unfurl.add_to_queue(
                data_type="uuid-parsed", key=None, value=node.value, label="Version 4 UUID is randomly generated",
                parent_id=node.node_id, incoming_edge_config=uuid_edge)

        elif u.hex[12] == '5':
            unfurl.add_to_queue(
                data_type="uuid-parsed", key=None, value=node.value,
                label="Version 5 UUID is generated based on a namespace and a name, which are combined and hashed using SHA-1",
                parent_id=node.node_id, incoming_edge_config=uuid_edge)

    # TODO: Add lookup of well-known GUIDs?
    # https://github.com/EricZimmerman/GuidMapping/blob/master/Resources/GuidToName.txt
