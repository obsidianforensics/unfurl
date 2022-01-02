"""Methods for easy encoding and decoding of messages"""

import re
import six
import json
import collections
import unfurl.lib.blackboxprotobuf.lib.types.length_delim
import unfurl.lib.blackboxprotobuf.lib.config
from unfurl.lib.blackboxprotobuf.lib.exceptions import TypedefException


def decode_message(buf, message_type=None, config=None):
    """Decode a message to a Python dictionary.
    Returns tuple of (values, types)
    """

    if config is None:
        config = unfurl.lib.blackboxprotobuf.lib.config.default

    if isinstance(buf, bytearray):
        buf = bytes(buf)
    buf = six.ensure_binary(buf)
    if message_type is None or isinstance(message_type, str):
        if message_type not in config.known_types:
            message_type = {}
        else:
            message_type = config.known_types[message_type]

    value, typedef, _ = unfurl.lib.blackboxprotobuf.lib.types.length_delim.decode_message(
        buf, config, message_type
    )
    return value, typedef


# TODO add explicit validation of values to message type
def encode_message(value, message_type, config=None):
    """Encodes a python dictionary to a message.
    Returns a bytearray
    """

    if config is None:
        config = unfurl.lib.blackboxprotobuf.lib.config.default
    return bytes(
        unfurl.lib.blackboxprotobuf.lib.types.length_delim.encode_message(
            value, config, message_type
        )
    )


def protobuf_to_json(*args, **kwargs):
    """Encode to python dictionary and dump to JSON.
    Takes same arguments as decode_message
    """
    value, message_type = decode_message(*args, **kwargs)
    value = json_safe_transform(
        value, message_type, False, config=kwargs.get("config", None)
    )
    value = sort_output(value, message_type, config=kwargs.get("config", None))
    _annotate_typedef(message_type, value)
    message_type = sort_typedef(message_type)
    return json.dumps(value, indent=2), message_type


def protobuf_from_json(json_str, message_type, *args, **kwargs):
    """Decode JSON string to JSON and then to protobuf.
    Takes same arguments as encode_message
    """
    value = json.loads(json_str)
    _strip_typedef_annotations(message_type)
    value = json_safe_transform(value, message_type, True)
    return encode_message(value, message_type, *args, **kwargs)


def export_protofile(message_types, output_filename):
    """Export the give messages as ".proto" file.
    Expects a dictionary with {message_name: typedef} and a filename to
    write to.
    """
    unfurl.lib.blackboxprotobuf.lib.protofile.export_proto(
        message_types, output_filename=output_filename
    )


def import_protofile(input_filename, save_to_known=True, config=None):
    """import ".proto" files and returns the typedef map
    Expects a filename for the ".proto" file
    """
    if config is None:
        config = unfurl.lib.blackboxprotobuf.lib.config.default

    new_typedefs = unfurl.lib.blackboxprotobuf.lib.protofile.import_proto(
        config, input_filename=input_filename
    )
    if save_to_known:
        config.known_types.update(new_typedefs)
    else:
        return new_typedefs


NAME_REGEX = re.compile(r"\A[a-zA-Z][a-zA-Z0-9_]*\Z")


def validate_typedef(typedef, old_typedef=None, path=None, config=None):
    """Validate the typedef format. Optionally validate wiretype of a field
    number has not been changed
    """
    if path is None:
        path = []
    if config is None:
        config = unfurl.lib.blackboxprotobuf.lib.config.default

    int_keys = set()
    field_names = set()
    for field_number, field_typedef in typedef.items():
        alt_field_number = None
        if "-" in str(field_number):
            field_number, alt_field_number = field_number.split("-")

        # Validate field_number is a number
        if not str(field_number).isdigit():
            raise TypedefException("Field number must be a digit: %s" % field_number)
        field_number = str(field_number)

        field_path = path[:]
        field_path.append(field_number)

        # Check for duplicate field numbers
        if field_number in int_keys:
            raise TypedefException(
                "Duplicate field number: %s" % field_number, field_path
            )
        int_keys.add(field_number)

        # Must have a type field
        if "type" not in field_typedef:
            raise TypedefException(
                "Field number must have a type value: %s" % field_number, field_path
            )
        if alt_field_number is not None:
            if field_typedef["type"] != "message":
                raise TypedefException(
                    "Alt field number (%s) specified for non-message field: %s"
                    % (alt_field_number, field_number),
                    field_path,
                )

        valid_type_fields = [
            "type",
            "name",
            "message_typedef",
            "message_type_name",
            "alt_typedefs",
            "example_value_ignored",
            "seen_repeated",
        ]
        for key, value in field_typedef.items():
            # Check field keys against valid values
            if key not in valid_type_fields:
                raise TypedefException(
                    'Invalid field key "%s" for field number %s' % (key, field_number),
                    field_path,
                )
            if (
                key in ["message_typedef", "message_type_name"]
                and not field_typedef["type"] == "message"
            ):
                raise TypedefException(
                    'Invalid field key "%s" for field number %s' % (key, field_number),
                    field_path,
                )
            if key == "group_typedef" and not field_typedef["type"] == "group":
                raise TypedefException(
                    'Invalid field key "%s" for field number %s' % (key, field_number),
                    field_path,
                )

            # Validate type value
            if key == "type":
                if value not in unfurl.lib.blackboxprotobuf.lib.types.type_maps.WIRETYPES:
                    raise TypedefException(
                        'Invalid type "%s" for field number %s' % (value, field_number),
                        field_path,
                    )
            # Check for duplicate names
            if key == "name":
                if value.lower() in field_names:
                    raise TypedefException(
                        ('Duplicate field name "%s" for field ' "number %s")
                        % (value, field_number),
                        field_path,
                    )
                if not NAME_REGEX.match(value):
                    raise TypedefException(
                        (
                            'Invalid field name "%s" for field '
                            "number %s. Should match %s"
                        )
                        % (value, field_number, "[a-zA-Z_][a-zA-Z0-9_]*"),
                        field_path,
                    )
                if value != "":
                    field_names.add(value.lower())

            # Check if message type name is known
            if key == "message_type_name":
                if value not in config.known_types:
                    raise TypedefException(
                        (
                            'Message type "%s" for field number'
                            " %s is not known. Known types: %s"
                        )
                        % (value, field_number, config.known_types.keys()),
                        field_path,
                    )

            # Recursively validate inner typedefs
            if key in ["message_typedef", "group_typedef"]:
                if old_typedef is None:
                    validate_typedef(value, path=field_path, config=config)
                else:
                    validate_typedef(
                        value, old_typedef[field_number][key], path=field_path
                    )
            if key == "alt_typedefs":
                for alt_field_number, alt_typedef in value.items():
                    # TODO validate alt_typedefs against old typedefs?
                    validate_typedef(alt_typedef, path=field_path, config=config)

    if old_typedef is not None:
        wiretype_map = {}
        for field_number, value in old_typedef.items():
            wiretype_map[
                int(field_number)
            ] = unfurl.lib.blackboxprotobuf.lib.types.type_maps.WIRETYPES[value["type"]]
        for field_number, value in typedef.items():
            field_path = path[:]
            field_path.append(str(field_number))
            if int(field_number) in wiretype_map:
                old_wiretype = wiretype_map[int(field_number)]
                if (
                    old_wiretype
                    != unfurl.lib.blackboxprotobuf.lib.types.type_maps.WIRETYPES[value["type"]]
                ):
                    raise TypedefException(
                        (
                            "Wiretype for field number %s does"
                            " not match old type definition"
                        )
                        % field_number,
                        field_path,
                    )


def json_safe_transform(values, typedef, toBytes, config=None):
    """JSON doesn't handle bytes type well. We want to go through and encode
    every bytes type as latin1 to get a semi readable text"""

    if config is None:
        config = unfurl.lib.blackboxprotobuf.lib.config.default
    name_map = {
        item["name"]: number
        for number, item in typedef.items()
        if item.get("name", None)
    }
    for name, value in values.items():
        alt_number = None
        base_name = name
        if "-" in name:
            base_name, alt_number = name.split("-")

        if base_name in name_map:
            field_number = name_map[base_name]
        else:
            field_number = base_name

        field_type = typedef[field_number]["type"]
        if field_type == "message":
            field_typedef = _get_typedef_for_message(typedef[field_number], config)
            if alt_number is not None:
                # if we have an alt type, then let's look that up instead
                if alt_number not in typedef[field_number].get("alt_typedefs", {}):
                    raise TypedefException(
                        (
                            "Provided alt field name/number "
                            "%s is not valid for field_number %s"
                        )
                        % (alt_number, field_number)
                    )
                field_type = typedef[field_number]["alt_typedefs"][alt_number]
                if isinstance(field_type, dict):
                    field_typedef = field_type
                    field_type = "message"

        is_list = isinstance(value, list)
        field_values = value if is_list else [value]
        for i, field_value in enumerate(field_values):
            if field_type == "bytes":
                if toBytes:
                    field_values[i] = field_value.encode("latin1")
                else:
                    field_values[i] = field_value.decode("latin1")
            elif field_type == "message":
                field_values[i] = json_safe_transform(
                    field_value,
                    field_typedef,
                    toBytes,
                    config=config,
                )

        # convert back to single value if needed
        if not is_list:
            values[name] = field_values[0]
        else:
            values[name] = field_values
    return values


def _get_typedef_for_message(field_typedef, config):
    assert field_typedef["type"] == "message"
    if "message_typedef" in field_typedef:
        return field_typedef["message_typedef"]
    elif field_typedef.get("message_type_name"):
        if field_typedef["message_type_name"] not in config.known_types:
            raise TypedefException(
                "Got 'message_type_name' not in known_messages: %s"
                % field_typedef["message_type_name"]
            )
        return config.known_types[field_typedef["message_type_name"]]
    else:
        raise TypedefException(
            "Got 'message' type without typedef or type name: %s" % field_typedef
        )


def sort_output(value, typedef, config=None):
    """Sort output by the field number in the typedef. Helps with readability
    in a JSON dump"""
    output_dict = collections.OrderedDict()
    if config is None:
        config = unfurl.lib.blackboxprotobuf.lib.config.default

    # Make a list of all the field names we have, aggregate together the alt fields as well
    field_names = {}
    for field_name in value.keys():
        if "-" in field_name:
            field_name_base, alt_number = field_name.split("-")
        else:
            field_name_base = field_name
            alt_number = None
        field_names.setdefault(field_name_base, []).append((field_name, alt_number))

    for field_number, field_def in sorted(typedef.items(), key=lambda t: int(t[0])):
        field_number = str(field_number)
        seen_field_names = field_names.get(field_number, [])

        # Try getting matching fields by name as well
        if field_def.get("name", "") != "":
            field_name = field_def["name"]
            seen_field_names.extend(field_names.get(field_name, []))

        for field_name, alt_number in seen_field_names:
            field_type = field_def["type"]
            field_message_typedef = None
            if field_type == "message":
                field_message_typedef = _get_typedef_for_message(field_def, config)

            if alt_number is not None:
                if alt_number not in field_def["alt_typedefs"]:
                    raise TypedefException(
                        (
                            "Provided alt field name/number "
                            "%s is not valid for field_number %s"
                        )
                        % (alt_number, field_number)
                    )
                field_type = field_def["alt_typedefs"][alt_number]
                if isinstance(field_type, dict):
                    field_message_typedef = field_type
                    field_type = "message"

            if field_type == "message":
                if not isinstance(value[field_name], list):
                    output_dict[field_name] = sort_output(
                        value[field_name], field_message_typedef
                    )
                else:
                    output_dict[field_name] = []
                    for field_value in value[field_name]:
                        output_dict[field_name].append(
                            sort_output(field_value, field_message_typedef)
                        )
            else:
                output_dict[field_name] = value[field_name]

    return output_dict


def sort_typedef(typedef):
    """Sort output by field number and sub_keys so name then type is first"""

    TYPEDEF_KEY_ORDER = ["name", "type", "message_type_name", "example_value_ignored"]
    output_dict = collections.OrderedDict()

    for field_number, field_def in sorted(typedef.items(), key=lambda t: int(t[0])):
        output_field_def = collections.OrderedDict()
        field_def = field_def.copy()
        for key in TYPEDEF_KEY_ORDER:
            if key in field_def:
                output_field_def[key] = field_def[key]
                del field_def[key]
        for key, value in field_def.items():

            # TODO handle alt typedefs
            if key == "message_typedef":
                output_field_def[key] = sort_typedef(value)
            else:
                output_field_def[key] = value
        output_dict[field_number] = output_field_def
    return output_dict


def _annotate_typedef(typedef, message):
    """Add values from message into the typedef so it's easier to figure out
    which field when you're editing manually"""

    for field_number, field_def in typedef.items():
        field_value = None
        field_name = str(field_number)
        if field_name not in message and field_def.get("name", "") != "":
            field_name = field_def["name"]

        if field_name in message:
            field_value = message[field_name]

            # TODO handle alt typedefs
            if field_def["type"] == "message":
                if isinstance(field_value, list):
                    for value in field_value:
                        _annotate_typedef(field_def["message_typedef"], value)
                else:
                    _annotate_typedef(field_def["message_typedef"], field_value)
            else:
                field_def["example_value_ignored"] = field_value


def _strip_typedef_annotations(typedef):
    """Remove example values placed by _annotate_typedef"""
    for _, field_def in typedef.items():
        if "example_value_ignored" in field_def:
            del field_def["example_value_ignored"]
        if "message_typedef" in field_def:
            _strip_typedef_annotations(field_def["message_typedef"])
