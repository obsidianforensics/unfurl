#!/usr/bin/env python3

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

import configparser
from unfurl import core

config = configparser.ConfigParser()
config.read('unfurl.ini')

unfurl_host = 'localhost'
unfurl_port = '5000'
unfurl_debug = 'True'
remote_lookups = False

if config.has_section('UNFURL_APP'):
    unfurl_host = config['UNFURL_APP'].get('host')
    unfurl_port = config['UNFURL_APP'].get('port')
    unfurl_debug = config['UNFURL_APP'].get('debug')
    try:
        remote_lookups = config['UNFURL_APP'].getboolean('remote_lookups')
    # If we can't interpret it as a boolean, fail "safe" to not allowing lookups
    except ValueError:
        remote_lookups = False


if __name__ == '__main__':
    core.UnfurlApp(
        unfurl_debug=unfurl_debug,
        unfurl_host=unfurl_host,
        unfurl_port=unfurl_port,
        remote_lookups=remote_lookups)
