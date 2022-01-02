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

import base64
from unfurl.lib import blackboxprotobuf
from unfurl import utils

proto_edge = {
    'color': {
        'color': '#2D9A58'
    },
    'title': 'Protobuf Parsing Functions',
    'label': 'proto'
}

hex_proto_edge = {
    'color': {
        'color': '#2D9A58'
    },
    'title': 'Parsed from hex bytes, then as a protobuf',
    'label': 'hex+proto'
}

b64_proto_edge = {
    'color': {
        'color': '#2D9A58'
    },
    'title': 'Parsed from base64, then as a protobuf',
    'label': 'b64+proto'
}

wire_types = {
    'int': '<b>varint (0)</b>. <br><br>It is displayed here as an int, but it could orginially have '
           'been <br>a int32, int64, uint32, uint64, sint32, sint64, bool, or enum.',
    'fixed64': '<b>64-bit (1)</b>. <br><br>It is displayed here as a fixed64, but it could originally '
               'have been <br>a fixed64, sfixed64, or double.',
    'bytes': '<b>length-delimited (2)</b>. <br><br>It is displayed here as bytes, but it could originally '
             'have been <br>a string, bytes, embedded messages, or packed repeated fields.',
    'string': '<b>length-delimited (2)</b>. <br><br>It is displayed here as a string, but it could originally '
             'have been <br>a string, bytes, embedded messages, or packed repeated fields.',
    'fixed32': '<b>32-bit (5)</b>. <br><br>It is displayed here as an int, but it could originally '
               'have been <br>a fixed32, sfixed32, or float.'
}


def run(unfurl, node):

    def parse_protobuf_into_nodes(pb_value_dict, pb_types, edge_type=None):
        assert isinstance(pb_value_dict, dict), \
            f'"parse_protobuf_into_nodes" expects a dict, but got {type(pb_value_dict)} as input'

        if len(pb_value_dict) > 0:
            for field_number, field_value in pb_value_dict.items():
                if isinstance(field_value, (str, int, float, bytes, bytearray)):
                    unfurl.add_to_queue(
                        data_type='proto', key=field_number, value=str(field_value),
                        hover=f'Field number <b>{field_number}</b> has a wire '
                              f'type of {wire_types[pb_types[field_number]["type"]]}',
                        parent_id=node.node_id, incoming_edge_config=edge_type)
                elif isinstance(field_value, dict):
                    unfurl.add_to_queue(
                        data_type='proto.dict', key=field_number,
                        value={'field_values': field_value, 'field_types': pb_types[field_number]["message_typedef"]},
                        label=f'{field_number}: {field_value}',
                        hover=f'Field number <b>{field_number}</b> '
                              f'is a nested message; it will be parsed further into more nodes',
                        parent_id=node.node_id, incoming_edge_config=edge_type)
                elif isinstance(field_value, list):
                    nested_types = pb_types[field_number]
                    if pb_types[field_number].get("message_typedef"):
                        nested_types = pb_types[field_number]["message_typedef"]

                    unfurl.add_to_queue(
                        data_type='proto.list', key=field_number,
                        value={'field_values': field_value, 'field_types': nested_types},
                        label=f'{field_number}: {field_value}',
                        hover=f'Field number <b>{field_number}</b> '
                              f'is a nested message; it will be parsed further into more nodes',
                        parent_id=node.node_id, incoming_edge_config=edge_type)

    if node.data_type == 'proto.dict':
        parse_protobuf_into_nodes(node.value.get('field_values'), node.value.get('field_types'), proto_edge)
        return

    if node.data_type == 'proto.list':
        for field_value in node.value['field_values']:
            field_types = node.value.get('field_types')
            if not isinstance(field_value, dict):
                field_value = {node.key: field_value}
                field_types = {node.key: field_types}
            parse_protobuf_into_nodes(field_value, field_types, proto_edge)
        return

    if node.data_type == 'bytes':
        try:
            protobuf_values, protobuf_values_types = blackboxprotobuf.decode_message(node.value)
            parse_protobuf_into_nodes(protobuf_values, protobuf_values_types, proto_edge)
            return

        # This will often fail for a wide array of reasons when it tries to parse a non-pb as a pb
        except Exception:
            pass

    if not isinstance(node.value, str):
        return False

    if len(node.value) % 4 == 1:
        # A valid b64 string will not be this length
        return False

    if node.data_type.startswith(('uuid', 'hash')):
        return False

    urlsafe_b64_m = utils.urlsafe_b64_re.fullmatch(node.value)
    standard_b64_m = utils.standard_b64_re.fullmatch(node.value)
    hex_m = utils.hex_re.fullmatch(node.value)
    long_int_m = utils.long_int_re.fullmatch(node.value)
    all_digits_m = utils.digits_re.fullmatch(node.value)
    all_letters_m = utils.digits_re.fullmatch(node.value)

    if hex_m and not (all_digits_m or all_letters_m):
        decoded = bytes.fromhex(node.value)
        try:
            protobuf_values, protobuf_values_types = blackboxprotobuf.decode_message(decoded)
            parse_protobuf_into_nodes(protobuf_values, protobuf_values_types, hex_proto_edge)
            return

        # This will often fail for a wide array of reasons when it tries to parse a non-pb as a pb
        except Exception:
            return

    elif urlsafe_b64_m and not (all_digits_m or all_letters_m):
        try:
            decoded = base64.urlsafe_b64decode(unfurl.add_b64_padding(node.value))
            protobuf_values, protobuf_values_types = blackboxprotobuf.decode_message(decoded)
            parse_protobuf_into_nodes(protobuf_values, protobuf_values_types, b64_proto_edge)
            return

        # This will often fail for a wide array of reasons when it tries to parse a non-pb as a pb
        except Exception:
            return

    elif standard_b64_m and not (all_digits_m or all_letters_m):
        try:
            decoded = base64.b64decode(unfurl.add_b64_padding(node.value))
            protobuf_values, protobuf_values_types = blackboxprotobuf.decode_message(decoded)
            parse_protobuf_into_nodes(protobuf_values, protobuf_values_types, b64_proto_edge)
            return

        # This will often fail for a wide array of reasons when it tries to parse a non-pb as a pb
        except Exception:
            return
