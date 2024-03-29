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

import base64
import struct
from unfurl import utils

metasploit_edge = {
    'color': {
        'color': 'red'
    },
    'title': 'Metasploit Parsing Functions',
    'label': 'M'
}

# Reference: https://github.com/rapid7/metasploit-framework/blob/master/lib/rex/payloads/meterpreter/uri_checksum.rb
# Metasploit 8-bit checksums
#  URI_CHECKSUM_INITW = 92  # Windows
#  URI_CHECKSUM_INITN = 92  # Native (same as Windows)
#  URI_CHECKSUM_INITP = 80  # Python
#  URI_CHECKSUM_INITJ = 88  # Java
#  URI_CHECKSUM_CONN = 98  # Existing session
#  URI_CHECKSUM_INIT_CONN = 95  # New stageless session

metasploit_checksums = {
    80: 'Python',
    88: 'Java',
    92: 'Windows',
    95: 'New stageless session',
    98: 'Existing session'
}

# Reference: https://github.com/rapid7/metasploit-framework/blob/master/lib/msf/core/payload/uuid.rb
architectures = {
    # 0: 'nil',
    1: 'ARCH_X86',
    2: 'ARCH_X64',
    3: 'ARCH_X64',
    4: 'ARCH_MIPS',
    5: 'ARCH_MIPSLE',
    6: 'ARCH_MIPSBE',
    7: 'ARCH_PPC',
    8: 'ARCH_PPC64',
    9: 'ARCH_CBEA',
    10: 'ARCH_CBEA64',
    11: 'ARCH_SPARC',
    12: 'ARCH_ARMLE',
    13: 'ARCH_ARMBE',
    14: 'ARCH_CMD',
    15: 'ARCH_PHP',
    16: 'ARCH_TTY',
    17: 'ARCH_JAVA',
    18: 'ARCH_RUBY',
    19: 'ARCH_DALVIK',
    20: 'ARCH_PYTHON',
    21: 'ARCH_NODEJS',
    22: 'ARCH_FIREFOX',
    23: 'ARCH_ZARCH',
    24: 'ARCH_AARCH64',
    25: 'ARCH_MIPS64',
    26: 'ARCH_PPC64LE',
    27: 'ARCH_R',
    28: 'ARCH_PPCE500V2'
}

# Reference: https://github.com/rapid7/metasploit-framework/blob/master/lib/msf/core/payload/uuid.rb
platforms = {
    0: 'nil',
    1: 'windows',
    2: 'netware',
    3: 'android',
    4: 'java',
    5: 'ruby',
    6: 'linux',
    7: 'cisco',
    8: 'solaris',
    9: 'osx',
    10: 'bsd',
    11: 'openbsd',
    12: 'bsdi',
    13: 'netbsd',
    14: 'freebsd',
    15: 'aix',
    16: 'hpux',
    17: 'irix',
    18: 'unix',
    19: 'php',
    20: 'js',
    21: 'python',
    22: 'nodejs',
    23: 'firefox',
    24: 'r',
    25: 'apple_ios',
    26: 'juniper',
    27: 'unifi',
    28: 'brocade',
    29: 'mikrotik',
    30: 'arista'
}


def run(unfurl, node):
    # Decoding a Metasploit Shellcode URL
    # Code is based off Didier's Stevens work:
    #  - Finding Metasploit & Cobalt Strike URLs
    #    (https://isc.sans.edu/forums/diary/Finding+Metasploit+Cobalt+Strike+URLs/27204/)
    #  - metatool.py (https://github.com/DidierStevens/Beta/blob/master/metatool.py#L219)
    # Metasploit code:
    #  - https://github.com/rapid7/metasploit-framework/blob/master/lib/rex/payloads/meterpreter/uri_checksum.rb
    if node.data_type == 'url.path' and len(node.value) == 5:
        checksum = sum(map(ord, node.value[1:])) % 0x100
        metasploit_checksum = metasploit_checksums.get(checksum)

        if not metasploit_checksum:
            return

        unfurl.add_to_queue(
            data_type='descriptor', key=None, value=None,
            label=f'Matches Metasploit URL checksum for {metasploit_checksum}',
            hover='Shellcode URLs generated by Metasploit and Cobalt Strike have a path <br>'
                  'of four characters and are validated by a checksum. This URL path fits <br>'
                  f'the pattern and the checksum code matches <b>{metasploit_checksum}</b>. However, <br>'
                  'the checksum is short (8-bits) and <b>this could be a false positive</b>. '
                  '[<a href="https://isc.sans.edu/forums/diary/Finding+Metasploit+Cobalt+Strike+URLs/27204/">ref</a>]',
            parent_id=node.node_id, incoming_edge_config=metasploit_edge)

    # Decoding a Metasploit Payload UUID
    # Ex: http://127.0.0.1/aAF9cpWMQPb-3f_cq1FoJA040uMw26kAnvroJdztpVzDr... (path of at least 22 chars)
    # Code is based off Didier's Stevens work:
    #  - Metasploit's Payload UUID (https://isc.sans.edu/forums/diary/Metasploits+Payload+UUID/23555/)
    #  - metatool.py (https://github.com/DidierStevens/Beta/blob/master/metatool.py#L254)
    # Metasploit docs/code:
    #  - Payload UUID by HD Moore (https://github.com/rapid7/metasploit-framework/wiki/Payload-UUID)
    #  - uuid.rb (https://github.com/rapid7/metasploit-framework/blob/master/lib/msf/core/payload/uuid.rb)

    if node.data_type == 'url.path' and len(node.value) >= 23:

        cleaned_path = node.value.lstrip('/').rstrip('/')

        # URL path should be base64 encoded
        if not (utils.digits_re.search(cleaned_path) and utils.letters_re.search(cleaned_path)
                and utils.urlsafe_b64_re.fullmatch(cleaned_path)):
            return

        decoded = base64.urlsafe_b64decode(cleaned_path[0:22] + '==')
        encoded_payload_uuid_format = '8sBBBBBBBB'
        puid, xor1, xor2, platform_xored, architecture_xored, ts1_xored, ts2_xored, ts3_xored, ts4_xored = \
            struct.unpack(encoded_payload_uuid_format, decoded)

        platform = platform_xored ^ xor1
        platform_name = platforms.get(platform, None)
        if platform_name is None:
            return

        architecture = architecture_xored ^ xor2
        architecture_name = architectures.get(architecture, None)
        if architecture_name is None:
            return

        timestamp = struct.unpack(
            '>I', bytes([ts1_xored ^ xor1, ts2_xored ^ xor2, ts3_xored ^ xor1, ts4_xored ^ xor2]))[0]

        # This is the lowest valid timestamp, per Metasploit code. Someone could customize it to be different, but
        # filtering on this seems like a good way to reduce false positives.
        # Source: https://github.com/rapid7/metasploit-framework/blob/master/lib/msf/core/payload/uuid.rb#L90
        if timestamp < 1420070400:
            return

        unfurl.add_to_queue(
            data_type='descriptor', key='Unique ID', value=bytes.hex(puid),
            hover='Metasploit\'s <b>puid</b> is an optional 8-byte string that<br> '
                  'can be used as the unique payload ID. '
                  '[<a href="https://isc.sans.edu/forums/diary/Metasploits+Payload+UUID/23555/">ref</a> & '
                  '<a href="https://github.com/rapid7/metasploit-framework/blob/master/lib/msf/core/payload/uuid.rb">'
                  'ref</a>]',
            parent_id=node.node_id, incoming_edge_config=metasploit_edge)

        unfurl.add_to_queue(
            data_type='descriptor', key='Platform', value=platform_name.capitalize(),
            hover='The operating system platform for this Metasploit payload.',
            parent_id=node.node_id, incoming_edge_config=metasploit_edge)

        unfurl.add_to_queue(
            data_type='descriptor', key='Architecture', value=architecture_name[5:],
            hover='The hardware architecture for this Metasploit payload.',
            parent_id=node.node_id, incoming_edge_config=metasploit_edge)

        unfurl.add_to_queue(
            data_type='epoch-seconds', key='Timestamp', value=timestamp,
            hover='The timestamp (in Epoch seconds) the payload was generated.',
            parent_id=node.node_id, incoming_edge_config=metasploit_edge)
