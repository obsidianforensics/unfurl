#!/usr/bin/env python3

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

import configparser
from flask import Flask, render_template, request
from flask_cors import CORS
from unfurl import Unfurl

config = configparser.ConfigParser()
config.read('unfurl.ini')

unfurl_host = config['UNFURL_APP'].get('host', 'localhost')
unfurl_port = config['UNFURL_APP'].get('port', '5000')
unfurl_debug = config['UNFURL_APP'].get('debug', 'True')

app = Flask(__name__)
CORS(app)


@app.route('/')
def index():
    return render_template(
        'graph.html', url_to_unfurl='', unfurl_host=unfurl_host,
        unfurl_port=unfurl_port)


@app.route('/<path:url_to_unfurl>')
def graph(url_to_unfurl):
    return render_template(
        'graph.html', url_to_unfurl=url_to_unfurl,
        unfurl_host=unfurl_host, unfurl_port=unfurl_port)


@app.route('/api/<path:api_path>')
def api(api_path):
    # Get the referrer from the request, which has the full url + query string.
    # Split off the local server and keep just the url we want to parse
    unfurl_this = request.referrer.split(f':{unfurl_port}/', 1)[1]

    unfurl_instance = Unfurl()
    unfurl_instance.add_to_queue(
        data_type='url', key=None,
        extra_options={'widthConstraint': {'maximum': 1200}},
        value=unfurl_this)
    unfurl_instance.parse_queue()

    unfurl_json = unfurl_instance.generate_json()
    return unfurl_json


if __name__ == '__main__':
    app.run(debug=unfurl_debug, host=unfurl_host, port=unfurl_port)
