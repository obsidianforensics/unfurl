# Copyright 2026 Ryan Benson
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
import json
import logging
import urllib.request

log = logging.getLogger(__name__)

# Modern Facebook Click IDs (fbclid) use a binary serialization format:
#   [2-char header][base64url-encoded payload][optional _aem_ suffix]
#
# Headers (case-insensitive in practice; hypothesized meanings based on
# observed URL contexts — not officially documented by Meta):
#   'Iw' = likely outbound click (user clicked an external link)
#   'PA' = likely page/ad impression tracking
#
# Payload contains known field names as literal ASCII strings, each followed
# by a length byte and value. Values may be ASCII strings or binary.
# The parser scans for known field names rather than walking sequentially,
# as binary values can contain bytes >= 0x20 that disrupt sequential parsing.
#
# Known fields (reverse-engineered names; not documented by Meta):
#   extn    = extension type (usually 'aem' = Aggregated Event Measurement)
#   brid    = browser ID (links clicks from same browser session)
#   clck    = click tracking (alternative to extn in some variants)
#   srtc    = source tracking code (often wraps app_id as a nested key)
#   app_id  = Facebook App ID (resolvable via Graph API)
#   adid    = advertisement ID (often a binary value)
#
# Optional '_aem_' suffix: 16-byte hash for privacy-preserving ad attribution

facebook_edge = {
    'color': {
        'color': '#1877F2'
    },
    'title': 'Facebook Click ID',
    'label': 'f'
}

KNOWN_FIELDS = {
    'extn': ('Extension Type', 'The tracking extension type. '
             '"aem" = Aggregated Event Measurement, Facebook\'s privacy-preserving '
             'ad attribution system.'),
    'brid': ('Browser ID', 'A browser identifier that links '
             'multiple clicks from the same browser session. Similar to Meta\'s '
             'documented _fbp "browser ID" cookie. (Reverse-engineered name, '
             'not officially documented by Meta.)'),
    'app_id': ('App ID', 'The Facebook application ID that generated or is '
               'tracking this link click.'),
    'adid': ('Ad ID', 'An advertisement identifier, present when the '
             'click originated from a Facebook ad.'),
    'srtc': ('Source Tracking', 'A source tracking code for the click.'),
    'clck': ('Click Tracking', 'A click tracking identifier. '
             'Found in IwY2-prefix fbclids as an alternative to extn.'),
}

# Old-format fbclids (IwAR...) are opaque and can't be decoded
OLD_FORMAT_PREFIXES = ('IwAR', 'iwar')

# Known Facebook App IDs — resolved via Graph API (April 2026).
# These are Meta's own internal app identifiers and are stable.
KNOWN_APP_IDS = {
    '2220391788200892': 'WWW (Comet)',
    '256281040558': 'WWW',
    '350685531728': 'Facebook for Android',
    '6628568379': 'Facebook for iPhone',
    '124024574287414': 'Instagram',
    '567067343352427': 'Instagram for Android (Analytics Only)',
    '905593853150754': 'Instagram Carbon',
    '275254692598279': 'Facebook Lite',
    '409962623085609': 'Facebook Lite for Web (WebLite)',
    '173847642670370': 'Facebook for iPad',
    '437626316973788': 'Messenger for iOS',
    '514771569228061': 'BizWeb',
    '119211728144504': 'Power editor',
    '412378670482': 'Msite',
    '436761779744620': 'Business Manager',
    '2094176354154603': 'Ads Events Manager',
}


def lookup_app_id(app_id, remote=False):
    """Resolve a Facebook App ID to its name.

    Uses a built-in table of known IDs first, then falls back to
    the Graph API for unknown IDs (only if remote=True).
    """
    # Check offline table first
    if app_id in KNOWN_APP_IDS:
        return KNOWN_APP_IDS[app_id]

    if not remote:
        return None

    # Fall back to Graph API
    try:
        url = f'https://graph.facebook.com/{app_id}'
        req = urllib.request.Request(url, headers={'User-Agent': 'unfurl/1.0'})
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read())
            return data.get('name')
    except Exception as e:
        log.debug(f'Failed to resolve Facebook App ID {app_id}: {e}')
        return None


def parse_fbclid(unfurl, node):
    """Parse a modern Facebook Click ID into its component fields."""
    fbclid = str(node.value)

    # Old format is opaque
    if fbclid.startswith(OLD_FORMAT_PREFIXES):
        return

    header = fbclid[:2]
    rest = fbclid[2:]

    # Handle _aem_ suffix
    aem_hash = None
    if '_aem_' in rest:
        rest, aem_suffix = rest.split('_aem_', 1)
        try:
            padded = aem_suffix + '=' * ((4 - len(aem_suffix) % 4) % 4)
            aem_hash = base64.urlsafe_b64decode(padded).hex()
        except Exception:
            aem_hash = aem_suffix

    padded = rest + '=' * ((4 - len(rest) % 4) % 4)
    try:
        data = base64.urlsafe_b64decode(padded)
    except Exception:
        return

    # Parse the binary TLV payload.
    # Format: repeated [ascii_key][length_byte][value_bytes]
    # Known field names appear as literal ASCII in the payload. Rather than
    # walking byte-by-byte (which breaks when binary values contain bytes
    # >= 0x20 that look like ASCII keys), scan for known field names directly.
    fields_found = {}
    data_str = data.decode('latin-1')  # safe 1:1 byte mapping

    for field_key in KNOWN_FIELDS:
        pos = 0
        while True:
            pos = data_str.find(field_key, pos)
            if pos == -1:
                break

            val_start = pos + len(field_key)
            if val_start >= len(data):
                break

            val_len = data[val_start]
            val_offset = val_start + 1

            if val_len == 0 or val_offset + val_len > len(data):
                pos += 1
                continue

            value_bytes = data[val_offset:val_offset + val_len]

            # Check if value is printable ASCII
            is_ascii = all(0x20 <= b < 0x7f for b in value_bytes)

            if is_ascii:
                value = value_bytes.decode('ascii')

                # If the value is itself a known field name, it indicates nesting:
                # e.g. srtc -> app_id -> "2203917882008922"
                if value in KNOWN_FIELDS:
                    nested_key = value
                    ni = val_offset + val_len
                    # Skip any empty key (bytes >= 0x20 before length byte)
                    while ni < len(data) and data[ni] >= 0x20:
                        ni += 1
                    if ni < len(data):
                        nval_len = data[ni]
                        ni += 1
                        if nval_len > 0 and ni + nval_len <= len(data):
                            nval_bytes = data[ni:ni + nval_len]
                            if all(0x20 <= b < 0x7f for b in nval_bytes):
                                fields_found[nested_key] = nval_bytes.decode('ascii')
                else:
                    fields_found[field_key] = value
            else:
                # Binary value — store as hex for fields like adid
                fields_found[field_key] = value_bytes.hex()

            pos = val_offset + val_len

    if not fields_found and not aem_hash:
        return

    node.hover = (
        'Facebook Click ID (fbclid) containing tracking fields. '
        f'Header "{header}" indicates '
        f'{"an outbound link click" if header == "Iw" else "a page/ad impression"}.'
    )

    for field_key, value in fields_found.items():
        label_name, hover_text = KNOWN_FIELDS[field_key]

        # For app_id, resolve to a human-readable name
        if field_key == 'app_id':
            app_name = lookup_app_id(value, remote=unfurl.remote_lookups)
            if app_name:
                label_name = 'App'
                value = f'{app_name} ({value})'

        unfurl.add_to_queue(
            data_type=f'facebook.fbclid.{field_key}',
            key=None, value=value,
            label=f'{label_name}: {value}',
            hover=hover_text,
            parent_id=node.node_id,
            incoming_edge_config=facebook_edge)

    if aem_hash:
        unfurl.add_to_queue(
            data_type='facebook.fbclid.aem_hash',
            key=None, value=aem_hash,
            label=f'AEM Hash: {aem_hash[:16]}...',
            hover='Aggregated Event Measurement hash. A 16-byte value used for '
                  'privacy-preserving ad attribution (related to Apple ATT/SKAdNetwork).',
            parent_id=node.node_id,
            incoming_edge_config=facebook_edge)


def run(unfurl, node):
    if node.data_type == 'url.query.pair' and node.key == 'fbclid':
        parse_fbclid(unfurl, node)
