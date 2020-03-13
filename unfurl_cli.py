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
import argparse
import json
from unfurl import Unfurl

config = configparser.ConfigParser()
config.read('unfurl.ini')

parser = argparse.ArgumentParser()
parser.add_argument("url", help="URL to parse")
parser.add_argument("--indent", type=int, default=4, help="indent level")
parser.add_argument("--output", help="file.json output to file.json")
args = parser.parse_args()

unfurl_instance = Unfurl()
unfurl_instance.add_to_queue(
        data_type='url',
	key=None,
	extra_options={'widthConstraint': {'maximum': 1200}},
        value=args.url)
unfurl_instance.parse_queue()

unfurl_json = unfurl_instance.generate_json()
ret = ""
if (args.indent < 1):
	ret = json.dumps(unfurl_json)
else: 
	ret = json.dumps(unfurl_json, indent=args.indent)

if (args.output):
	f = open(args.output,'w')
	print(ret, file=f)
else:
	print(ret)
