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

import networkx
import os
import queue
import sys


class Unfurl:
    def __init__(self):
        self.nodes = {}
        self.edges = []
        self.queue = queue.Queue()
        self.next_id = 1
        self.graph = networkx.DiGraph()
        self.total_nodes = 0

    class Node:
        def __init__(self, node_id, data_type, key, value, label=None, hover=None, parent_id=None,
                     incoming_edge_config=None, extra_options=None):
            self.node_id = node_id
            self.data_type = data_type
            self.key = key
            self.value = value
            self.label = label
            self.hover = hover
            self.parent_id = parent_id
            self.incoming_edge_config = incoming_edge_config
            self.extra_options = extra_options

            if self.label is None:
                if self.key and self.value:
                    self.label = '{}: {}'.format(self.key, self.value)
                elif self.value:
                    self.label = self.value

        def __repr__(self):
            return str(self.__dict__)

    def get_predecessor_node(self, node):
        if not node.parent_id:
            return False
        predecessor = list(self.graph.predecessors(node))
        assert len(predecessor) == 1
        return predecessor[0]

    def get_successor_nodes(self, node):
        successors = list(self.graph.successors(node))
        return successors

    def check_sibling_nodes(self, node, data_type=None, key=None, value=None):
        parent_node = self.get_predecessor_node(node)

        if not parent_node:
            return False

        assert type(parent_node) == Unfurl.Node, \
            'Expected Unfurl.Node as parent type; got {}'.format(type(parent_node))

        sibling_nodes = self.get_successor_nodes(parent_node)

        for sibling_node in sibling_nodes:

            # Skip the "sibling" if it's actually the source node
            if node.node_id == sibling_node.node_id:
                continue

            # For each attribute, check if it is set. If it is and it
            # doesn't match, stop checking this node and go to the next
            if data_type and data_type != sibling_node.data_type:
                continue
            if key and key != sibling_node.key:
                continue
            if value and value != sibling_node.value:
                continue

            # This node matched all the given criteria;
            return True

        # If we got here, no nodes matched all criteria.
        return False

    def find_preceding_domain(self, node):
        parent_node = self.get_predecessor_node(node)

        if not parent_node:
            return ''

        assert isinstance(parent_node, Unfurl.Node), \
            'Expected Unfurl.Node as parent type; got {}'.format(type(parent_node))

        if parent_node.data_type == 'url.hostname':
            assert isinstance(parent_node.value, str)
            return parent_node.value
        elif parent_node.data_type == 'url':
            for child_node in self.get_successor_nodes(parent_node):
                if child_node.data_type == 'url.hostname':
                    assert isinstance(child_node.value, str)
                    return child_node.value
                elif child_node.data_type == 'url.authority':
                    for subcomponent in self.get_successor_nodes(child_node):
                        if subcomponent.data_type == 'url.hostname':
                            assert isinstance(subcomponent.value, str)
                            return subcomponent.value
            return ''
        else:
            return self.find_preceding_domain(parent_node)

    def get_id(self):
        id = self.next_id
        self.next_id += 1
        return id

    def create_node(self, data_type, key, value, label, hover, parent_id=None, incoming_edge_config=None,
                    extra_options=None):
        new_node = self.Node(self.get_id(), data_type=data_type, key=key, value=value, label=label, hover=hover,
                             parent_id=parent_id, incoming_edge_config=incoming_edge_config,
                             extra_options=extra_options)
        assert new_node.node_id not in self.nodes.keys()
        self.nodes[new_node.node_id] = new_node
        self.graph.add_node(new_node)
        self.total_nodes += 1

        if parent_id:
            self.graph.add_edge(self.nodes[parent_id], new_node)

        return new_node.node_id

    @staticmethod
    def check_if_int_between(value, low, high):
        try:
            value = int(value)
        except:
            return False

        if low < value < high:
            return True
        else:
            return False

    def add_to_queue(self, data_type, key, value, label=None, hover=None, parent_id=None, incoming_edge_config=None,
                     extra_options=None):
        new_item = {
            "data_type": data_type,
            "key": key,
            "value": value,
            "label": label,
            "hover": hover,
            'incoming_edge_config': incoming_edge_config,
            'extra_options': extra_options
        }

        if parent_id:
            new_item["parent_id"] = parent_id

        self.queue.put(new_item)

    def run_plugins(self, node):

        parser_path = os.path.join(os.getcwd(), 'parsers')
        if os.path.isdir(parser_path):
            sys.path.insert(0, parser_path)
            try:
                # Get list of available parsers and run them
                parser_listing = os.listdir(parser_path)

                for plugin in parser_listing:
                    if plugin[-3:] == ".py" and plugin[0] != '_':
                        plugin = plugin.replace(".py", "")

                        try:
                            plugin = __import__(plugin)
                        except ImportError as e:
                            print("ImportError: {}".format(e))
                            continue
                        try:
                            plugin.run(self, node)
                        except Exception as e:
                            print("Exception in {}: {}; {}".format(plugin, e, e.args))

            except Exception as e:
                print('Error loading parsers: {}'.format(e))

    def parse(self, queued_item):
        item = queued_item
        node_id = self.create_node(
            data_type=item["data_type"], key=item["key"], value=item["value"], label=item["label"], hover=item["hover"],
            parent_id=item.get("parent_id", None), incoming_edge_config=item.get("incoming_edge_config", None),
            extra_options=item.get('extra_options', None))

        if item.get("parent_id"):
            self.get_predecessor_node(self.nodes[node_id])

        self.run_plugins(self.nodes[node_id])

    def parse_queue(self):
        while not self.queue.empty() and self.total_nodes < 100:
            self.parse(self.queue.get())

    @staticmethod
    def transform_node(node):
        transformed = {
                'id': int(node.node_id),
                'label': '{}'.format(node.label)
        }
        if node.hover:
            transformed['title'] = node.hover
        if node.extra_options:
            transformed.update(node.extra_options)
        return transformed

    @staticmethod
    def transform_edge(edge):
        transformed = {
            'from': int(edge[0].node_id),
            'to': int(edge[1].node_id)
        }

        if edge[1].incoming_edge_config:
            transformed.update(edge[1].incoming_edge_config)
        return transformed

    def generate_json(self):
        data_json = {'nodes': [], 'edges': []}
        for orig_node in self.graph.nodes():
            data_json['nodes'].append(self.transform_node(orig_node))
        for orig_edge in self.graph.edges():
            data_json['edges'].append(self.transform_edge(orig_edge))

        return data_json


def testing():
    test = Unfurl()
    # Discord
    test.add_to_queue(
        data_type='url', key=None,
        value='https://discordapp.com/channels/427876741990711298/551531058039095296')

    # Twitter
    test.add_to_queue(
        data_type="url", key=None, extra_options={'widthConstraint': {'maximum': 1200}},
        value='https://twitter.com/_RyanBenson/status/1098230906194546688')

    # URLs
    test.add_to_queue(
        data_type="url", key=None,
        value="https://www.bing.com/search?q=digital+forensics&qs=n&form=QBLH&sp=-1&pq=digital+forensic&sc=8-16&sk=&cvid=97BF13B59CF84B98B13C067AAA3DB701")

    test.parse_queue()
    print(test.generate_json())


# testing()
