#!/usr/bin/env python3

# Copyright 2021 Google LLC
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

long_int_re = re.compile(r'\d{8,}')
urlsafe_b64_re = re.compile(r'[A-Za-z0-9_\-]{8,}={0,2}')
standard_b64_re = re.compile(r'[A-Za-z0-9+/]{8,}={0,2}')
hex_re = re.compile(r'[A-F0-9]+', flags=re.IGNORECASE)
digits_re = re.compile(r'\d+')
letters_re = re.compile(r'[A-Z]+', flags=re.IGNORECASE)
float_re = re.compile(r'\d+\.\d+')
mac_addr_re = re.compile(r'(?P<mac_addr>[0-9A-Fa-f]{12}|([0-9A-Fa-f]:){6})')
cisco_7_re = re.compile(r'\d{2}[A-F0-9]{4,}', re.IGNORECASE)
