import base64
import re


b64_edge = {
    'color': {
        'color': '#2C63FF'
    },
    'title': 'Base64 Parsing Functions',
    'label': 'b64'
}


def run(unfurl, node):

    if not isinstance(node.value, str):
        return False

    if len(node.value) % 4 == 1:
        # A valid b64 string will not be this length
        return False

    urlsafe_b64_m = re.fullmatch(r'[A-Za-z0-9_=\-]{8,}', node.value)
    standard_b64_m = re.fullmatch(r'[A-Za-z0-9+/=]{8,}', node.value)
    long_int = re.fullmatch(r'\d{8,}', node.value)

    # Long integers pass the b64 regex, but we don't want those here.
    if long_int:
        return

    decoded = None
    if urlsafe_b64_m:
        decoded = base64.urlsafe_b64decode(unfurl.add_b64_padding(node.value))
    elif standard_b64_m:
        decoded = base64.b64decode(unfurl.add_b64_padding(node.value))

    if decoded == node.value or not decoded:
        return

    try:
        # This limits the plugin to only decoding ASCII string that were base64
        # encoded. Obviously other things could be encoded, but it's a start.
        str_decoded = decoded.decode('ascii', errors='strict')

    # This will happen a lot with things that aren't really b64 encoded, or
    # with things that are b64-encoded, but the results are not ASCII
    # (like gzip or protobufs).
    except UnicodeDecodeError:
        # Show the resulting bytes from base64 inflating. Disabled for now,
        # as it's too noisy.
        # unfurl.add_to_queue(data_type='bytes', key=None, value=decoded,
        #                parent_id=node.node_id, incoming_edge_config=b64_edge)
        return

    unfurl.add_to_queue(data_type='b64', key=None, value=str_decoded,
                        parent_id=node.node_id, incoming_edge_config=b64_edge)
