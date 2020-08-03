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

import datetime
import re

timestamp_edge = {
    'color': {
        'color': 'blue'
    },
    'title': 'Date & Time Parsing Functions',
    'label': '🕓'
}

digits_re = re.compile(r'^\d+$')
float_re = re.compile(r'^\d+\.\d+$')
hex_re = re.compile(r'^[A-F0-9]+$', flags=re.IGNORECASE)


def decode_epoch_seconds(seconds):
    """Decode a numeric timestamp in Epoch seconds format to a human-readable timestamp.

    An Epoch timestamp (1-10 digits) is an integer that counts the number of seconds since Jan 1 1970.

    Useful values for ranges (all Jan-1 00:00:00):
      1970: 0
      2015: 1420070400
      2025: 1735689600
      2030: 1900000000

    """
    return datetime.datetime.utcfromtimestamp(float(seconds)), 'Epoch seconds'


def decode_epoch_centiseconds(centiseconds):
    """Decode a numeric timestamp in Epoch centiseconds (10 ms) format to a human-readable timestamp.

    An Epoch centisecond timestamp (1-12 digits) is an integer that counts the number of centiseconds (10 ms)
    since Jan 1 1970.

    Useful values for ranges (all Jan-1 00:00:00):
      1970: 0
      2015: 142007040000
      2025: 173568960000
      2030: 190000000000

    """
    # Trim off the 3 trailing 0s (don't add precision that wasn't in the timestamp)
    converted_ts = str(datetime.datetime.utcfromtimestamp(float(centiseconds) / 100))[:-4]
    return converted_ts, 'Epoch centiseconds'


def decode_epoch_milliseconds(milliseconds):
    """Decode a numeric timestamp in Epoch milliseconds format to a human-readable timestamp.

    An Epoch millisecond timestamp (1-13 digits) is an integer that counts the number of milliseconds since Jan 1 1970.

    Useful values for ranges (all Jan-1 00:00:00):
      1970: 0
      2015: 1420070400000
      2025: 1735689600000
      2030: 1900000000000

    """
    # Trim off the 3 trailing 0s (don't add precision that wasn't in the timestamp)
    converted_ts = str(datetime.datetime.utcfromtimestamp(float(milliseconds) / 1000))[:-3]
    return converted_ts, 'Epoch milliseconds'


def decode_epoch_microseconds(microseconds):
    """Decode a numeric timestamp in Epoch milliseconds format to a human-readable timestamp.

    An Epoch millisecond timestamp (1-10 digits) is an integer that counts the number of milliseconds since Jan 1 1970.

    Useful values for ranges (all Jan-1 00:00:00):
      1970: 0
      2015: 1420070400000
      2025: 1735689600000
      2030: 1900000000000

    """
    # Trim off the 3 trailing 0s (don't add precision that wasn't in the timestamp)
    converted_ts = str(datetime.datetime.utcfromtimestamp(float(microseconds) / 1000000))
    return converted_ts, 'Epoch microseconds'


def decode_webkit(microseconds):
    """Decode a numeric timestamp in Webkit format to a human-readable timestamp.

    A Webkit timestamp (17 digits) is an integer that counts the number of microseconds since 12:00AM Jan 1 1601 UTC.

    Useful values for ranges (all Jan-1 00:00:00):
      1970: 11644473600000000
      2015: 13064544000000000
      2025: 13380163200000000

    """
    return datetime.datetime.utcfromtimestamp((float(microseconds) / 1000000) - 11644473600), 'Webkit'


def decode_windows_filetime(intervals):
    """Decode a numeric timestamp in Windows FileTime format to a human-readable timestamp.

    A Windows FileTime timestamp (18 digits) is a 64-bit value that represents the number of 100-nanosecond intervals
    since 12:00AM Jan 1 1601 UTC.

    Useful values for ranges (all Jan-1 00:00:00):
      1970: 116444736000000000
      2015: 130645440000000000
      2025: 133801632000000000
      2065: 146424672000000000

    """
    return datetime.datetime.utcfromtimestamp((float(intervals) / 10000000) - 11644473600), 'Windows FileTime'


def decode_datetime_ticks(ticks):
    """Decode a numeric timestamp in .Net/C# DateTime ticks format to a human-readable timestamp.

    A .Net/C# DateTime ticks timestamp (18 digits) is the number of 100-nanosecond intervals that have elapsed since
    12:00:00 midnight, January 1, 0001 (0:00:00 UTC on January 1, 0001, in the Gregorian calendar), which represents
    DateTime.MinValue. It does not include the number of ticks that are attributable to leap seconds.

    A single tick represents one hundred nanoseconds or one ten-millionth of a second. There are 10,000 ticks in a
    millisecond, or 10 million ticks in a second.

    (^ from https://docs.microsoft.com/en-us/dotnet/api/system.datetime.ticks?view=netframework-4.8)

    Useful values for ranges (all Jan-1 00:00:00):
      1970: 621355968000000000
      2015: 635556672000000000
      2025: 638712864000000000
      2038: 642815136000000000

    """
    return (datetime.datetime(1, 1, 1) + datetime.timedelta(microseconds=ticks/10)), 'DateTime ticks'


def decode_mac_absolute_time(seconds):
    """Decode a numeric timestamp in Mac Absolute Time format to a human-readable timestamp.

    A Mac Absolute Time timestamp (9 digits typically) is the number of seconds since 2001-01-01. This time format is
    also known as CFAbsoluteTime, Core Data timestamp, or Cocoa Core Data timestamp. Negative values are allowed and
    denote timestamps before the reference date.

    ref: https://developer.apple.com/documentation/corefoundation/cfabsolutetime

    Useful values for ranges (all Jan-1 00:00:00):
      1970: -978307200
      2015: 441763200
      2025: 757382400
      2035: 1072915200

    """
    return datetime.datetime.utcfromtimestamp(float(seconds)+978307200), 'Mac Absolute Time / Cocoa'


def run(unfurl, node):
    new_timestamp = (None, 'unknown')

    if node.data_type == 'epoch-seconds':
        new_timestamp = decode_epoch_seconds(node.value)

    elif node.data_type == 'epoch-centiseconds':
        new_timestamp = decode_epoch_centiseconds(node.value)

    elif node.data_type == 'epoch-milliseconds':
        new_timestamp = decode_epoch_milliseconds(node.value)

    elif node.data_type == 'epoch-microseconds':
        new_timestamp = decode_epoch_microseconds(node.value)

    elif node.data_type == 'windows-filetime':
        new_timestamp = decode_windows_filetime(node.value)

    elif node.data_type == 'webkit':
        new_timestamp = decode_webkit(node.value)

    elif node.data_type == 'datetime-ticks':
        new_timestamp = decode_datetime_ticks(node.value)

    elif node.data_type == 'mac-absolute-time':
        new_timestamp = decode_mac_absolute_time(node.value)

    else:
        matches_digits = re.match(digits_re, str(node.value))
        matches_float = re.match(float_re, str(node.value))
        matches_hex = re.match(hex_re, str(node.value))

        if matches_digits:
            timestamp = int(node.value)

            # Windows FileTime (18 digits)
            if 130645440000000000 <= timestamp <= 133801632000000000:  # 2015 <= ts <= 2025
                new_timestamp = decode_windows_filetime(timestamp)

            # .Net/C# DateTime ticks (18 digits)
            elif 635556672000000000 <= timestamp <= 638712864000000000:  # 2015 <= ts <= 2025
                new_timestamp = decode_datetime_ticks(timestamp)

            # WebKit (17 digits)
            elif 13064544000000000 <= timestamp <= 13380163200000000:  # 2015 <= ts <= 2025
                new_timestamp = decode_webkit(timestamp)

            # Epoch microseconds (16 digits)
            elif 1420070400000000 <= timestamp <= 1735689600000000:  # 2015 <= ts <= 2025
                new_timestamp = decode_epoch_microseconds(timestamp)

            # Epoch milliseconds (13 digits)
            elif 1420070400000 <= timestamp <= 1735689600000:  # 2015 <= ts <= 2025
                new_timestamp = decode_epoch_milliseconds(timestamp)

            # Epoch seconds (10 digits)
            elif 1420070400 <= timestamp <= 1735689600:  # 2015 <= ts <= 2025
                new_timestamp = decode_epoch_seconds(timestamp)

            # Mac Absolute Time (9 digits)
            elif 441763200 <= timestamp <= 757382400:  # 2015 <= ts <= 2025
                new_timestamp = decode_mac_absolute_time(timestamp)

        elif matches_float:
            timestamp = float(node.value)

            # Epoch seconds (10 digits)
            if 1420070400.0 <= timestamp <= 1735689600.0:  # 2015 <= ts <= 2025
                new_timestamp = decode_epoch_seconds(timestamp)

            # Mac Absolute Time (9 digits)
            elif 441763200.0 <= timestamp <= 757382400.0:  # 2015 <= ts <= 2025
                new_timestamp = decode_mac_absolute_time(timestamp)

        elif matches_hex:
            # TODO: Do some parsing for timestamps that are in hex formats
            pass

    if new_timestamp != (None, 'unknown'):
        unfurl.add_to_queue(
            data_type=new_timestamp[1], key=None, value=new_timestamp[0],
            hover=f'Converted as {new_timestamp[1]}', parent_id=node.node_id,
            incoming_edge_config=timestamp_edge)
