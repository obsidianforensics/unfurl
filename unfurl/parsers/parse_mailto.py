import re

mailto_edge = {
    "color": {"color": "lightblue"},
    "title": "Mailto Parsing Functions",
    "label": "📧",
}


def run(unfurl, node):
    if node.data_type == "url" and node.value.startswith("mailto:"):

        raw = node.value.split(":", 1)
        label = None
        value = None

        if len(raw[1]) == 0:
            return

        if "?" in raw[1]:
            splitq = raw[1].split("?", 1)

            if len(splitq[0]) > 0:
                label = splitq[0]  # 'to' email address
            # rest of the string for node value, parse as 'url.query;'
            value = splitq[1]
        else:
            label = raw[1]

        unfurl.add_to_queue(
            data_type="url.query",
            key=None,
            value=value,
            label=f"to: {label}",
            hover="Mailto link is a type of URL that opens the default mail client for sending an email, per "
            '<a href="https://tools.ietf.org/html/rfc2368" target="_blank">RFC2368</a>',
            parent_id=node.node_id,
            incoming_edge_config=mailto_edge,
        )
