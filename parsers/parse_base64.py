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

    try:
        # TODO: better validation/detection/etc. This is very basic.
        m = re.match(r'^[A-Za-z0-9_=\-]{8,}$', node.value)
        if m:
            # As far as I can tell, just adding the max padding possible works, even when the padding is excessive.
            decoded = base64.urlsafe_b64decode(node.value + '===')
            if decoded == node.value:
                return

            try:
                # This limits the plugin to only decoding ASCII string that were base64 encoded. Obviously other
                # things could be encoded, but it's a start.
                str_decoded = decoded.decode('ascii', errors='strict')
            except UnicodeDecodeError:
                # This will happen a lot with things that aren't really b64 encoded and things that are b64-encoded, but the results are not
                # ASCII (like gzip or protobufs).
                return

            unfurl.add_to_queue(data_type='b64', key=None, value=str_decoded,
                                parent_id=node.node_id, incoming_edge_config=b64_edge)
    except Exception as e:
        print('parse_base64 exception: {}'.format(e))
