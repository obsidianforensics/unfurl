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

import ipaddress
import re
import textwrap
from datetime import datetime
from typing import Union

long_int_re = re.compile(r'\d{8,}')
urlsafe_b64_re = re.compile(r'[A-Za-z0-9_\-]{8,}={0,2}')
standard_b64_re = re.compile(r'[A-Za-z0-9+/]{8,}={0,2}')
hex_re = re.compile(r'([A-F0-9]{2})+', flags=re.IGNORECASE)
digits_re = re.compile(r'\d+')
letters_re = re.compile(r'[A-Z]+', flags=re.IGNORECASE)
digits_and_slash_re = re.compile(r'[0-9/]+')
letters_and_slash_re = re.compile(r'[A-Z/]+', flags=re.IGNORECASE)
float_re = re.compile(r'\d+\.\d+')
mac_addr_re = re.compile(r'(?P<mac_addr>[0-9A-Fa-f]{12}|([0-9A-Fa-f]{2}[:-]){5}[0-9A-Fa-f]{2})')
cisco_7_re = re.compile(r'\d{2}[A-F0-9]{4,}', re.IGNORECASE)
octal_ip_re = re.compile(r'(0[0-7]{3})\.(0[0-7]{3})\.(0[0-7]{3})\.(0[0-7]{3})')


def parse_ip_address(potential_ip):
    if re.fullmatch(digits_re, potential_ip):
        potential_ip = int(potential_ip)
    elif re.fullmatch(r'0x[A-F0-9]{8}', potential_ip, flags=re.IGNORECASE):
        potential_ip = int(potential_ip, base=16)
    elif re.fullmatch(octal_ip_re, potential_ip):
        m = re.fullmatch(octal_ip_re, potential_ip)
        potential_ip = f"{int(m.group(1), 8)}.{int(m.group(2), 8)}.{int(m.group(3), 8)}.{int(m.group(4), 8)}"
    try:
        parsed_ip = ipaddress.ip_address(potential_ip)
    except ValueError:
        parsed_ip = None

    return parsed_ip


def wrap_hover_text(hover_text: Union[str, None]) -> Union[str, None]:
    if not hover_text:
        return None

    if not isinstance(hover_text, str):
        return None

    # If there are any manually-inserted <br> or links, leave it
    # alone. This isn't perfect detection, but it'll do.
    if '<a' in hover_text or '<br' in hover_text:
        return hover_text

    # If the text is just a little long, I'd rather have it all on
    # one line than split into one long line and a short second line
    if len(hover_text) < 70:
        return hover_text

    # "Wrap" the hover text by splitting it into lines of length <width>,
    # then joining them together with a <br>.
    return '<br>'.join(textwrap.wrap(hover_text, width=60))


def create_epoch_seconds_timestamp(iso_timestamp: str | None = None, days_ahead: int | None = None, offset: int | float = 0) -> int:
    """
    Create a timestamp (number of seconds since Unix epoch) from either an ISO 8601-formatted timestamp string or for
    some number of days in the future. Optionally, an offset (in seconds) can be provided that will be subtracted
    from the return timestamp.

    :param iso_timestamp: An ISO 8601-formatted timestamp string (ex: 2015-02-01T00:00:00)
    :param days_ahead: Number of days ahead the timestamp should be created for (ex: 365)
    :param offset: The offset in seconds from the Unix epoch
    :return: An integer timestamp (in seconds)
    """

    # Neither are set; make the timestamp now.
    if not iso_timestamp and not days_ahead:
        timestamp = int(datetime.now().timestamp())
    # timestamp is a string; parse it to epoch seconds
    elif iso_timestamp:
        timestamp = int(datetime.fromisoformat(iso_timestamp).timestamp())
    # Make the timestamp now + days_ahead
    elif not iso_timestamp and days_ahead:
        timestamp = int(datetime.now().timestamp()) + (days_ahead * 86400)
    else:
        raise ValueError('Invalid options passed')

    return int(timestamp - offset)


def extract_bits(identifier: int, start: int, end: int) -> int:
    """
    Extract a subset of bits from an integer based on specified start and
    end positions. This operation shifts the specified bit range to the
    rightmost (least-significant) position and applies a mask to select
    the desired bits.

    :param identifier: The integer value from which bits will be extracted.
    :param start: The starting index of the bit range (inclusive).
    :param end: The ending index of the bit range (exclusive).
    :return: Extracted bits as an integer.
    """

    shifted = identifier >> start
    mask = (1 << (end - start)) - 1
    return shifted & mask

def set_bits(value: int, offset: int, max_size=None) -> int:
    return int(value << offset)

