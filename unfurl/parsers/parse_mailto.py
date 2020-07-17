import urllib.parse

mailto_edge = {
    "color": {"color": "lightblue"},
    "title": "Mailto Parsing Functions",
    "label": "📧",
}


def run(unfurl, node):
    if node.data_type == "url" and node.value.startswith("mailto:"):

        raw = node.value.split(":", 1)

        if len(raw[1]) == 0:
            return

        nodes = []

        if "?" in raw[1]:
            split_qs = raw[1].split("?", 1)

            if len(split_qs[0]) > 0:
                nodes.append({"k": "to", "v": split_qs[0]})

            # rest of the string for node value, parse as 'url.query;'
            for pair in split_qs[1].replace("&amp;", "&").split("&"):
                r = pair.split("=", 1)
                nodes.append({"k": r[0], "v": r[1]})
        else:
            nodes.append({"k": "to", "v": raw[1]})

        for n in nodes:
            k = n["k"]
            v = n["v"]
            unfurl_val = None
            if k in ["to", "cc", "bcc"]:
                if "," in v:
                    data_type = "mailto.email.multiple"
                else:
                    data_type = "email"
                unfurl_val = v
            else:
                data_type = "url.query"
                unfurl_val = f"{k}={v}"

            unfurl.add_to_queue(
                data_type=data_type,
                key=k,
                value=unfurl_val,
                label=f"{k}: {v}",
                hover="Mailto link is a type of URL that opens the default mail client for sending an email, per "
                '<a href="https://tools.ietf.org/html/rfc2368" target="_blank">RFC2368</a>',
                parent_id=node.node_id,
                incoming_edge_config=mailto_edge,
            )

            print("-" * 20)

    if node.data_type == "mailto.email.multiple":
        for raw_email in node.value.split(","):
            email = raw_email.replace("%20", " ").strip()
            unfurl.add_to_queue(
                data_type="email",
                key=None,
                value=email,
                label=f"{node.key}: {email}",
                hover="Mailto link is a type of URL that opens the default mail client for sending an email, per "
                '<a href="https://tools.ietf.org/html/rfc2368" target="_blank">RFC2368</a>',
                parent_id=node.node_id,
                incoming_edge_config=mailto_edge,
            )
