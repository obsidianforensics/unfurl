#!/usr/bin/env python3

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

import argparse
import configparser
import csv
import os
from unfurl import core
from flask import Flask, render_template, request, redirect, url_for
from flask_cors import CORS
from flask_restx import Api, Namespace, Resource
from urllib.parse import unquote
from unfurl.core import Unfurl

unfurl_app_host = None
unfurl_app_port = None
unfurl_remote_lookups = None
app = Flask(__name__)
CORS(app)


class UnfurlApp:
    def __init__(self, unfurl_debug='True', unfurl_host='localhost', unfurl_port='5000', remote_lookups=False):
        self.unfurl_debug = unfurl_debug
        self.unfurl_host = unfurl_host
        self.unfurl_port = unfurl_port
        self.remote_lookups = remote_lookups

        global unfurl_app_host
        global unfurl_app_port
        global unfurl_remote_lookups
        unfurl_app_host = self.unfurl_host
        unfurl_app_port = self.unfurl_port
        unfurl_remote_lookups = self.remote_lookups

        app.config['remote_lookups'] = remote_lookups
        app.run(debug=unfurl_debug, host=unfurl_host, port=unfurl_port)


@app.route('/')
@app.route('/<path:path>')
def index(path=''):
    url_to_unfurl = ''
    if path:
        # backward compatibility, it is preferable to use the graph route and a quoted URL instead
        if f':{unfurl_app_port}/' in request.url:
            url_to_unfurl = unquote(request.url.split(f':{unfurl_app_port}/', 1)[1])
        else:
            # for tests, the port isn't in the URL, take everything after the domain
            url_to_unfurl = unquote(request.url.split('/', 3)[-1])
        return redirect(url_for('graph', url=url_to_unfurl))
    return render_template('graph.html',
                           unfurl_host=unfurl_app_host,
                           unfurl_port=unfurl_app_port)


@app.route('/graph')
def graph():
    if 'url' not in request.args:
        return redirect(url_for('index'))
    return render_template('graph.html',
                           unfurl_host=unfurl_app_host,
                           unfurl_port=unfurl_app_port)


restx_api = Api(app, title='Unfurl API',
                description='API to submit URLs to expand to an unfurl instance.',
                doc='/doc/')
namespace = Namespace('GenericAPI', description='Generic unfurl API', path='/')
restx_api.add_namespace(namespace)


@namespace.route('/json/visjs')
@namespace.doc(description='Expand a URL and returns the JSON expansion in the vis.js format')
class JsonVisJS(Resource):

    @namespace.param('url', 'The URL to expand', required=False)
    def get(self):
        if 'url' not in request.args:
            return {}
        unfurl_this = unquote(request.args['url'])
        return run(
            unfurl_this,
            return_type='json',
            remote_lookups=app.config['remote_lookups'],
            extra_options={'widthConstraint': {'maximum': 1200}})


def run(url, data_type='url', return_type='json', remote_lookups=False, extra_options=None):
    u = Unfurl(remote_lookups=remote_lookups)
    u.add_to_queue(
        data_type=data_type,
        key=None,
        value=url,
        extra_options=extra_options
    )
    u.parse_queue()
    if return_type == 'text':
        return u.generate_text_tree()
    elif return_type == 'full_json':
        return u.generate_full_json()
    else:
        return u.generate_json()


def web_app(host='localhost', port='5000', debug='True', remote_lookups=False):

    config = configparser.ConfigParser()
    config.read('unfurl.ini')

    if config.has_section('UNFURL_APP'):
        host = config['UNFURL_APP'].get('host')
        port = config['UNFURL_APP'].get('port')
        debug = config['UNFURL_APP'].get('debug')
        try:
            remote_lookups = config['UNFURL_APP'].getboolean('remote_lookups')
        # If we can't interpret it as a boolean, fail "safe" to not allowing lookups
        except ValueError:
            remote_lookups = False

    UnfurlApp(
        unfurl_debug=debug,
        unfurl_host=host,
        unfurl_port=port,
        remote_lookups=remote_lookups)


def cli():
    parser = argparse.ArgumentParser(
        description='unfurl takes a URL and expands ("unfurls") it into a directed graph, extracting every '
                    'bit of information from the URL and exposing the obscured.')
    parser.add_argument(
        'what_to_unfurl',
        help='what to unfurl. typically this is a URL, but it also supports integers (timestamps), '
             'encoded protobufs, and more. if this is instead a file path, unfurl will open '
             'that file and process each line in it as a URL.')
    parser.add_argument(
        '-d', '--detailed', help='show more detailed explanations.', action='store_true')
    parser.add_argument(
        '-f', '--filter', help='only output lines that match this filter.')
    parser.add_argument(
        '-l', '--lookups', help='allow remote lookups to enhance results.', action='store_true')
    parser.add_argument(
        '-o', '--output',
        help='file to save output (as CSV) to. if omitted, output is sent to '
             'stdout (typically this means displayed in the console).')
    parser.add_argument(
        '-t', '--type', help='Type of output to produce', choices=['tree', 'json'], default='tree'
    )
    parser.add_argument(
        '-v', '-V', '--version', action='version', version=f'unfurl v{core.unfurl.__version__}')
    args = parser.parse_args()

    items_to_unfurl = []

    if os.path.isfile(args.what_to_unfurl):
        with open(args.what_to_unfurl, errors='ignore') as f:
            for input_url in f:
                items_to_unfurl.append(input_url.rstrip())

    else:
        items_to_unfurl.append(args.what_to_unfurl)

    if args.output:
        with open(args.output, 'w', newline='', encoding='utf-8') as csv_file:
            csv_writer = csv.writer(csv_file, quoting=csv.QUOTE_ALL)
            csv_writer.writerow(['url', 'unfurled'])

            for item in items_to_unfurl:
                unfurl_instance = core.Unfurl(remote_lookups=args.lookups)
                unfurl_instance.add_to_queue(
                    data_type='url', key=None,
                    value=item)
                unfurl_instance.parse_queue()
                if args.type == 'json':
                    csv_writer.writerow(
                        [item, unfurl_instance.generate_full_json()])
                else:
                    csv_writer.writerow(
                        [item, unfurl_instance.generate_text_tree(
                            detailed=args.detailed,
                            output_filter=args.filter)])

    else:
        for item in items_to_unfurl:
            unfurl_instance = core.Unfurl(remote_lookups=args.lookups)
            unfurl_instance.add_to_queue(
                data_type='url', key=None,
                value=item)
            unfurl_instance.parse_queue()

            if args.type == 'json':
                print(unfurl_instance.generate_full_json())
            else:
                print(unfurl_instance.generate_text_tree(
                    detailed=args.detailed, output_filter=args.filter))
            print()
