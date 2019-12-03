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

import urllib.parse
import re

urlparse_edge = {
    'color': {
        'color': '#4d4d4d'
    },
    'title': 'URL Parsing Functions',
    'label': 'u'
}


def run(unfurl, node):

    if node.data_type == 'url':
        parsed_url = urllib.parse.urlparse(node.value)

        if parsed_url.netloc:
            unfurl.add_to_queue(data_type='netloc', key=None, value=parsed_url.netloc,
                                hover='This is the URL <b>network location</b> (or netloc), per <a href="'
                                      'https://tools.ietf.org/html/rfc1808.html" target="_blank">RFC1808</a>',
                                parent_id=node.node_id, incoming_edge_config=urlparse_edge)
            if parsed_url.path:
                unfurl.add_to_queue(data_type='url.path', key=None, value=parsed_url.path,
                                    hover='This is the URL <b>path</b>, per <a href="'
                                          'https://tools.ietf.org/html/rfc1808.html" target="_blank">RFC1808</a>',
                                    parent_id=node.node_id, incoming_edge_config=urlparse_edge)
            if parsed_url.query:
                unfurl.add_to_queue(data_type='url.query', key=None, value=parsed_url.query,
                                    hover='This is the URL <b>query</b>, per <a href="'
                                          'https://tools.ietf.org/html/rfc1808.html" target="_blank">RFC1808</a>',
                                    parent_id=node.node_id, incoming_edge_config=urlparse_edge,
                                    extra_options={'widthConstraint': {'maximum': 500}})
            if parsed_url.fragment:
                unfurl.add_to_queue(data_type='url.fragment', key=None, value=parsed_url.fragment,
                                    hover='This is the URL <b>fragment</b>, per <a href="'
                                          'https://tools.ietf.org/html/rfc1808.html" target="_blank">RFC1808</a>',
                                    parent_id=node.node_id,
                                    incoming_edge_config=urlparse_edge)

    elif node.data_type == 'url.path':
        path_segments = node.value.split('/')
        if len(path_segments) > 2:
            for segment_number, path_segment in enumerate(path_segments):
                if path_segment != '':
                    unfurl.add_to_queue(data_type='url.path.segment', key=segment_number, value=path_segment,
                                        hover='This is a URL <b>path segment</b> (the URL path is split on "/"s). Numbering starts at 1.',
                                        parent_id=node.node_id, incoming_edge_config=urlparse_edge)

    elif node.data_type == 'url.query' or node.data_type == 'url.fragment':
        parsed_qs = urllib.parse.parse_qs(node.value)
        for key, value in parsed_qs.items():
            assert type(value) is list
            assert len(value) == 1
            unfurl.add_to_queue(
                data_type='url.query.pair', key=key, value=value[0], label='{}: {}'.format(key, value[0]),
                parent_id=node.node_id, incoming_edge_config=urlparse_edge)

    elif node.data_type == 'url.query.pair':
        try:
            # If we can recognize another URL inside a value, parse it
            parsed_url = urllib.parse.urlparse(node.value)
            if parsed_url.netloc and parsed_url.path:
                unfurl.add_to_queue(data_type='url', key=None, value=node.value, parent_id=node.node_id,
                                    incoming_edge_config=urlparse_edge)
        except:
            # Guess it wasn't a URL
            pass

        # If the value contains more pairs of the form "a=b|c=d|e=f"
        pipe_delimited_pairs_re = re.compile(r'(?P<key>[^|=]+)=(?P<value>[^|=]+)')
        m = pipe_delimited_pairs_re.finditer(node.value)
        if m:
            for match in m:
                unfurl.add_to_queue(data_type='url.query.pair', key=match['key'], value=match['value'],
                                    parent_id=node.node_id, incoming_edge_config=urlparse_edge)
