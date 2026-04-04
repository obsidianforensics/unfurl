# Registry mapping stash context names to compiled proto message classes.
# When parse_protobuf encounters a tagged context, it checks here first.
# If a compiled proto exists, it uses FromString() + MessageToDict() for
# precise, named fields. Otherwise, it falls back to blackboxprotobuf
# with field name labels from field_names.json.

from unfurl.parsers.proto.chrome_searchbox_stats_pb2 import ChromeSearchboxStats
from unfurl.parsers.proto.omnibox_types_pb2 import SuggestType, SuggestSubtype

proto_registry = {
    'google.gs_lcrp': ChromeSearchboxStats,
}

# Registry mapping data_type names to protobuf enum classes.
# When a node has a data_type in this registry, parse_protobuf resolves
# the integer value to a human-friendly enum name.
enum_registry = {
    'omnibox.suggest_type': SuggestType,
    'omnibox.suggest_subtype': SuggestSubtype,
}
