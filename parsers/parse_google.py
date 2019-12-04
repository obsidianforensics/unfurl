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

import base64
import struct
from parsers.proto.google_search_pb2 import Ved
from google.protobuf import json_format

google_edge = {
    'color': {
        'color': 'green'
    },
    'title': 'Google-related Parsing Functions',
    'label': 'G'
}

known_sources = {
    'hp': 'Home Page',
    'serp': 'Search Engine Results Page',
    'img': 'Image Search',
    'psy-ab': 'Address Bar'
}


def add_padding_base64(base_64_encoded_string):
    num_extra_bytes = (len(base_64_encoded_string) % 4)  # number of extra bytes needed to make len a multiple of 4
    if num_extra_bytes != 0:
        pad_length = 4 - num_extra_bytes  # ex: 4 - 1 results in 3 extra "=" pad bytes being added
        pad_string = base_64_encoded_string + pad_length * '='
    else:
        pad_string = base_64_encoded_string

    return pad_string


def decode_varint(source):
    result = 0
    number_of_bytes = 0
    for read in source:
        result |= ((read & 0x7F) << (number_of_bytes * 7))
        number_of_bytes += 1
        if (read & 0x80) != 0x80:
            return result, number_of_bytes


def parse_ei(ei):
    """Parse ei parameters from Google searches.

    Based on work by:
      Adrian Leong (cheeky4n6monkey@gmail.com) -
        https://github.com/cheeky4n6monkey/4n6-scripts/blob/master/google-ei-time.py
      Kevin Jones - https://deedpolloffice.com/blog/articles/decoding-ei-parameter
    """

    padded_string = add_padding_base64(ei)
    decoded = base64.urlsafe_b64decode(padded_string)

    # grab 1st 4 bytes and treat as LE unsigned int
    timestamp = struct.unpack('<i', decoded[0:4])[0]
    parsed = [timestamp]

    varint_offset = 4  # First 4 (0-3) bytes are the timestamp
    for _ in [1, 2, 3]:
        value, bytes_used = decode_varint(decoded[varint_offset:])
        parsed.append(value)
        varint_offset += bytes_used

    return parsed


def run(unfurl, node):
    if node.data_type == 'url.query.pair':
        if 'google' in unfurl.find_preceding_domain(node):
            if node.key == 'ei':
                parsed_ei = parse_ei(node.value)
                node.hover = 'The \'<b>ei</b>\' parameter is a base64-encoded protobuf containing four values. ' \
                             '<br>The first is thought to be the timestamp of when the search took place.' \
                             '<br><br>References:<ul>' \
                             '<li><a href="https://deedpolloffice.com/blog/articles/decoding-ei-parameter" ' \
                             'target="_blank">Kevin Jones: How to decode the ei parameter in Google search</a></li>' \
                             '<li><a href="http://cheeky4n6monkey.blogspot.com/2014/10/google-eid.html" ' \
                             'target="_blank">Cheeky4n6Monkey: Google-ei\'d ?!</a></li></ul>'

                assert len(parsed_ei) == 4, \
                    'There should be 4 decoded ei values, but we have {}!'.format(len(parsed_ei))

                unfurl.add_to_queue(
                    data_type='epoch-seconds', key=None, value=parsed_ei[0], label='ei-0: {}'.format(parsed_ei[0]),
                    hover='The first value in the \'ei\' parameter is thought to be the timestamp of when the search '
                          'took place.', parent_id=node.node_id, incoming_edge_config=google_edge)

                for index in [1, 2, 3]:
                    unfurl.add_to_queue(
                        data_type="integer", key=None, value=parsed_ei[index],
                        label='ei-{}: {}'.format(index, parsed_ei[index]),
                        hover="The meaning of the last three 'ei' values is not known.",
                        parent_id=node.node_id, incoming_edge_config=google_edge)

            elif node.key == 'gs_l':
                node.hover = 'The <b>gs_l</b> parameter contains multiple values, delimited by <b>.</b>. <br>' \
                             'We only know the meaning of 7 (of the 26+) parameters.'
                node.extra_options = {'widthConstraint': {'maximum': 1400}}

                params = node.value.split('.')

                known_params = [0, 1, 2, 4, 5, 7, 8, 26]
                for known_param in known_params:
                    if len(params[known_param]) > 0:
                        unfurl.add_to_queue(
                            data_type='google.gs_l', key=str(known_param), value=params[known_param],
                            label='Parameter {}: {}'.format(str(known_param), params[known_param]),
                            parent_id=node.node_id, incoming_edge_config=google_edge)

            elif node.key == 'oq':
                unfurl.add_to_queue(
                    data_type='descriptor', key=None, value='"Original" Search Query: {}'.format(node.value),
                    hover='Original terms entered by the user; auto-complete or suggestions <br>'
                          'may have been used to reach the actual search terms (in <b>q</b>)',
                    parent_id=node.node_id, incoming_edge_config=google_edge)

            elif node.key == 'q':
                unfurl.add_to_queue(
                    data_type='descriptor', key=None, value='Search Query: {}'.format(node.value),
                    hover='Terms used in the Google search', parent_id=node.node_id, incoming_edge_config=google_edge)

            elif node.key == 'source':
                unfurl.add_to_queue(
                    data_type='descriptor', key=None, value='Source: {}'.format(known_sources[node.value]),
                    hover='Source of the Google search', parent_id=node.node_id, incoming_edge_config=google_edge)

            elif node.key == 'start':
                unfurl.add_to_queue(
                    data_type='descriptor', key=None, value='Starting Result: {}'.format(node.value),
                    hover='Google search by default shows 10 results per page; higher <br>'
                          '"start" values may indicate browsing more subsequent results pages.',
                    parent_id=node.node_id, incoming_edge_config=google_edge)

            elif node.key == 'sxsrf':
                sxs_0, sxs_1 = node.value.split(':', 1)
                unfurl.add_to_queue(data_type='google.sxsrf', key=1, value=sxs_0,
                                    parent_id=node.node_id, incoming_edge_config=google_edge)
                unfurl.add_to_queue(
                    data_type='epoch-milliseconds', key=2, value=sxs_1,
                    hover='The <b>sxsrf</b> parameter contains a timestamp, believed<br>'
                          ' to correspond to the previous page load. <br><br>Refernces:<ul><li>'
                          '<a href="https://twitter.com/phillmoore/status/1169846359509233664" target="_blank">'
                          'Phill Moore on Twitter</a></li></ul>', parent_id=node.node_id,
                    incoming_edge_config=google_edge)

            elif node.key == 'uule':
                # https://moz.com/ugc/geolocation-the-ultimate-tip-to-emulate-local-search
                location_string = base64.b64decode(add_padding_base64(node.value[10:]))
                unfurl.add_to_queue(data_type='descriptor', key=None, value=location_string, label=location_string,
                                    parent_id=node.node_id, incoming_edge_config=google_edge)

            elif node.key == 'ved':
                known_ved_descriptions = {
                    'linkIndex':
                        'Unique index for each link on the search page. <br>The higher the number, the farther'
                        ' down the page the link is. <br>This should always be present. '
                        '<a href="https://deedpolloffice.com/blog/articles/decoding-ved-parameter" '
                        'target="_blank">[ref]</a>',
                    'linkType':
                        'The type of link that was clicked on; there are thousands. <br>This should always be '
                        'present. <a href="https://deedpolloffice.com/blog/articles/decoding-ved-parameter" '
                        'target="_blank">[ref]</a>',
                    'subResultPosition':
                        'The position of the link, if it was inside a "group" (like an adword or<br> '
                        'knowledge graph). This starts at 0 and counts up.'
                        '<a href="https://deedpolloffice.com/blog/articles/decoding-ved-parameter" '
                        'target="_blank">[ref]</a>',
                    'resultPosition':
                        'The position of the result on the page. The higher the number, <br>the farther '
                        'down the page the result is. '
                        '<a href="https://deedpolloffice.com/blog/articles/decoding-ved-parameter" '
                        'target="_blank">[ref]</a>',
                    'resultsStart':
                        'The starting position of the first result on the page. <br>On page 2, it will be '
                        '10; and on page 3 it will be 20, <br>and so on. On page 1, the value isn’t '
                        'present (but implicitly, this means a value of 0).'
                        '<a href="https://deedpolloffice.com/blog/articles/decoding-ved-parameter" '
                        'target="_blank">[ref]</a>',
                }
                assert node.value.startswith('0'), 'The ved parameter should start with 0'
                encoded_ved = node.value[1:]
                encoded_ved = base64.urlsafe_b64decode(add_padding_base64(encoded_ved))
                ved = Ved().FromString(encoded_ved)
                ved_dict = json_format.MessageToDict(ved)
                for key, value in ved_dict.items():
                    if key == 'v13Outer':
                        assert isinstance(value, dict), 'ved-13-Outer should be a dict'
                        assert isinstance(value['v13Inner'], dict), 'ved-13-Inner should also be a dict'
                        v13_timestamp = value['v13Inner'].get('timestamp')
                        if v13_timestamp:
                            unfurl.add_to_queue(
                                data_type='epoch-microseconds', key='Timestamp', value=v13_timestamp,
                                parent_id=node.node_id, incoming_edge_config=google_edge,
                                hover='The ved parameter contains a timestamp, believed to <br>correspond to around '
                                      'when the page loaded.')

                        v13_unknown_2 = value['v13Inner'].get('v132')
                        if v13_unknown_2:
                            unfurl.add_to_queue(
                                data_type='google.ved', key='13-2', value=v13_unknown_2,
                                parent_id=node.node_id, incoming_edge_config=google_edge,
                                hover='Inside the ved parameter, the meanings of<br> 13-2 and 13-3 is not known.')

                        v13_unknown_3 = value['v13Inner'].get('v133')
                        if v13_unknown_3:
                            unfurl.add_to_queue(
                                data_type='google.ved', key='13-2', value=v13_unknown_3,
                                parent_id=node.node_id, incoming_edge_config=google_edge,
                                hover='Inside the ved parameter, the meanings of<br> 13-2 and 13-3 is not known.')

                    else:
                        unfurl.add_to_queue(
                            data_type='google.ved', key=key, value=value, label='{}: {}'.format(key, value),
                            hover=known_ved_descriptions.get(key, ''),
                            parent_id=node.node_id, incoming_edge_config=google_edge)

    if node.data_type == "google.gs_l":
        known_values = {
            '0': known_sources,
            '1': {
                '1': 'mouse-click on suggestion',
                '3': 'keyboard [enter] key',
                '10': 'Google Instant Search (untested)'
            }
        }
        if node.key == '0':
            if node.value in known_values[node.key].keys():
                unfurl.add_to_queue(data_type='descriptor', key=None, value=known_values[node.key][node.value],
                                    label='Searcher came from {}'.format(known_values[node.key][node.value]),
                                    hover=None,
                                    parent_id=node.node_id, incoming_edge_config=google_edge)

        if node.key == '1':
            if node.value in known_values[node.key].keys():
                unfurl.add_to_queue(data_type='descriptor', key=None, value=known_values[node.key][node.value],
                                    label='Searcher selected search terms by {}'.format(
                                        known_values[node.key][node.value]), hover=None,
                                    parent_id=node.node_id, incoming_edge_config=google_edge)

        if node.key == '2':
            unfurl.add_to_queue(data_type='descriptor', key=None, value=node.value,
                                label='Selected option {} from suggestion list'.format(node.value), hover=None,
                                parent_id=node.node_id, incoming_edge_config=google_edge)

        if node.key == '4':
            if node.value == '0':
                param_text = 'User clicked on a suggestion'
            else:
                param_text = '{} seconds before the user selected the search box'.format(str(float(node.value) / 1000))

            unfurl.add_to_queue(data_type='descriptor', key=None, value=node.value,
                                label=param_text, hover=None,
                                parent_id=node.node_id, incoming_edge_config=google_edge)

        if node.key == '5':
            if node.value == '0':
                param_text = 'User clicked on a suggestion'
            else:
                param_text = '{} seconds on page before the user completed typing.'.format(
                    str(float(node.value) / 1000))

            unfurl.add_to_queue(data_type='descriptor', key=None, value=node.value,
                                label=param_text, hover=None,
                                parent_id=node.node_id, incoming_edge_config=google_edge)

        if node.key == '7':
            if node.value != '0':
                param_text = 'User spent {} seconds on page in total.'.format(str(float(node.value) / 1000))
                unfurl.add_to_queue(data_type='descriptor', key=None, value=node.value,
                                    label=param_text, hover=None,
                                    parent_id=node.node_id, incoming_edge_config=google_edge)

        if node.key == '8':
            if node.value == '0':
                param_text = 'No characters typed'
            else:
                param_text = '{} keys pressed while user was typing.'.format(node.value)

            unfurl.add_to_queue(data_type='descriptor', key=None, value=node.value,
                                label=param_text, hover='If the search was done in Chrome, this value may be +1.',
                                parent_id=node.node_id, incoming_edge_config=google_edge)

        if node.key == '26':
            if node.value == '1':
                unfurl.add_to_queue(data_type='descriptor', key=None, value=node.value,
                                    label='User typed in query', hover=None,
                                    parent_id=node.node_id, incoming_edge_config=google_edge)

    elif node.data_type == 'google.ved':
        known_link_types = {
            22: 'web',
            152: 'blog search result',
            232: 'book or patent search result',
            235: 'book or patent search result thumbnail',
            244: 'image result in standard SERPs',
            245: 'image search result in basic (non-javascript) image search, or image result in universal search',
            288: 'local search result',
            295: 'news result thumbnail',
            297: 'news result',
            300: 'more results link (listed mainly for Q&A websites)',
            311: 'video result',
            312: 'video result thumbnail',
            338: 'one-line sitelink',
            371: 'shopping search result',
            429: 'image search result [probably not in use any more]',
            586: '"Jump to" link',
            612: 'map search result website link',
            646: 'map search result thumbnail',
            706: 'adword sitelink',
            745: 'breadcrumb',
            1107: 'patent result "Overview" / "Related" / "Discuss" link',
            1140: 'book search result author link',
            1146: 'normal result thumbnail (e.g. for an application, recipe, etc.)',
            1150: 'normal result thumbnail (e.g. for an application, recipe, etc.)',
            1455: 'local search result marker pin icon',
            1532: 'news sub-result (i.e. the same story from a different site)',
            1617: 'adword (i.e. sponsored search result)',
            1701: 'map search result',
            1732: 'knowledge graph repeated sub-link (e.g. football team squad players, album track listings)',
            1907: 'sponsored shopping result thumbnail (in right-hand column of universal search results)',
            1908: 'sponsored shopping result (in right-hand column of universal search results)',
            1986: 'sponsored shopping result thumbnail (in main column of universal search results)',
            1987: 'sponsored shopping result (in main column of universal search results)',
            2060: 'sitelink',
            2237: 'news result video thumbnail',
            2459: 'knowledge graph link',
            2847: 'authorship "by [author]" link',
            2937: 'authorship thumbnail link',
            3588: 'image search result (thumbnail)',
            3596: 'image search result preview "View image" link',
            3597: 'image search result preview thumbnail',
            3598: 'image search result preview title link',
            3599: 'image search result preview "Visit page" link',
            3724: 'image search result preview grey website link underneath title',
            3836: 'knowledge graph main image',
            5077: 'in-depth article result',
            5078: 'in-depth article result thumbnail',
            5158: 'adword one-line sitelink',
            5497: 'dictionary definition link'
        }

        if node.key == 'linkType':
            if known_link_types.get(node.value):
                unfurl.add_to_queue(
                    data_type='descriptor', key=None, value=node.value,
                    label=known_link_types.get(node.value),
                    hover='There are tens of thousands of these values; the \'known\'<br> ones in Unfurl are based on '
                          '<a href="https://github.com/beschulz/ved-decoder" target="_blank">'
                          'Benjamin Schulz\'s work</a>',
                    parent_id=node.node_id, incoming_edge_config=google_edge)
