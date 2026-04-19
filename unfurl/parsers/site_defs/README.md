# Site Definitions

Site definitions are YAML files that teach Unfurl how to parse URLs for specific websites
without writing Python code. Each `.yaml` file in this directory defines parsing rules for
one site's URL structure.

## Requirements

Site definitions require [PyYAML](https://pypi.org/project/PyYAML/) (`pip install pyyaml`).
Without it, unfurl runs normally but skips all YAML-based site definitions.

## Quick Start

Create a new `.yaml` file in this directory (e.g., `example.yaml`):

```yaml
name: Example Site
domains:
  - example.com
edge:
  color: "#FF6600"
  title: Example Site
  label: "E"

path_rules:
  - match:
      1: users
    position: 2
    apply:
      label: "User: {value}"
      data_type: example.user_id
      hover: A user profile identifier.
```

That's it. Unfurl will automatically load it on the next run. No Python changes needed.

## File Structure

Every site definition has these top-level keys:

```yaml
name: Human-readable site name
domains:
  - example.com          # List of domains this definition applies to.
  - sub.example.com      # Subdomains of listed domains also match
                         # (www.example.com matches example.com).
edge:
  color: "#hex"          # Color for edges in the unfurl graph
  title: Edge tooltip    # Tooltip text shown on hover
  label: "E"             # Short label shown on the edge (emoji works too)

path_rules: [...]        # Rules for URL path segments
query_rules: [...]       # Rules for query string parameters
fragment_rules: [...]    # Rules for URL fragments (anchors)
```

## Path Rules

Path rules match against URL path segments. Unfurl splits the path on `/` and numbers
segments starting at 1. For `github.com/obsidianforensics/unfurl/issues/42`:

| Position | Value              |
|----------|--------------------|
| 1        | obsidianforensics  |
| 2        | unfurl             |
| 3        | issues             |
| 4        | 42                 |

### Position-based rules

Fire when the node's segment position matches. Use `match` to require specific values
at other positions (sibling segments):

```yaml
# Match: example.com/users/:user_id
- match:
    1: users           # Segment 1 must be "users"
  position: 2           # This rule fires on segment 2
  apply:
    label: "User: {value}"
    data_type: example.user_id
    hover: A user identifier.
```

The `match` map is optional. An empty match (`match: {}`) means the rule fires on any
URL for this domain at the given position:

```yaml
# Match: example.com/:username (any first segment)
- match: {}
  position: 1
  apply:
    label: "Username: {value}"
    data_type: example.username
```

### Value-based rules (`on_value`)

Fire when any segment has a specific value, regardless of position:

```yaml
# Match "wiki" anywhere in the path
- match: {}
  on_value: wiki
  apply:
    label: "Wiki"
    data_type: descriptor
```

You can combine `on_value` with `match` to require context:

```yaml
# Match "files" only when segment 3 is "pull" (i.e., a PR files view)
- match:
    3: pull
  on_value: files
  apply:
    label: "Changed Files"
    data_type: descriptor
```

### Excluding values

When using a broad position-based rule (like "segment 1 is a username"), you need to
exclude known non-matching values. Use `exclude_values`:

```yaml
- match: {}
  position: 1
  exclude_values: [login, settings, search, explore, "*.php"]
  apply:
    label: "Profile: {value}"
    data_type: example.username
```

`exclude_values` supports wildcards via [fnmatch](https://docs.python.org/3/library/fnmatch.html):
- `*` matches any characters (e.g., `*.php` matches `profile.php`, `login.php`, etc.)
- `?` matches a single character
- `[seq]` matches any character in seq

Plain strings are exact matches. Wildcards and exact strings can be mixed freely.

### Excluding by sibling

Use `exclude_sibling` to skip when a sibling segment has certain values.
Supports the same wildcards as `exclude_values`:

```yaml
- match: {}
  position: 2
  exclude_sibling:
    key: 1                           # Check segment at position 1
    values: [login, join, settings]  # Skip if segment 1 has any of these
  apply:
    label: "Repo: {value}"
    data_type: example.repo
```

### Rule priority

Rules are evaluated in order. **The first matching rule wins** for each node. Put more
specific rules before general ones:

```yaml
# Specific: stories/highlights/ID
- match:
    1: stories
    2: highlights
  position: 3
  apply:
    label: "Highlight: {value}"

# General: stories/USERNAME
- match:
    1: stories
  position: 2
  apply:
    label: "Stories by: {value}"
```

## Query Rules

Query rules match URL query parameters (`?key=value`) by their key name:

```yaml
query_rules:
  - key: q
    apply:
      label: "Search: {value}"
      data_type: example.search_query
      hover: The search query string.
```

### Hover-only rules

To add hover text to an existing parameter without creating a child node,
use `hover_only`:

```yaml
  - key: __tn__
    apply:
      hover_only: true
      hover: >-
        Content type/rendering flags.
```

### Scoping by path

A query parameter can mean different things depending on the URL path. Use `path` to
restrict a rule to a specific path:

```yaml
  # q means "redirect target" on /url, but "search query" on /search
  - key: q
    path: /url
    apply:
      hover_only: true
      hover: The redirect target URL.
```

Without `path`, the rule fires on every URL for the domain that has the matching key.

### Parsing values as URLs

Set `data_type: url` to have unfurl parse the parameter value as a full URL:

```yaml
  - key: redirect_uri
    apply:
      label: "Redirect: {value}"
      data_type: url
      hover: The OAuth redirect URL.
```

## Fragment Rules

Fragment rules match the URL fragment (the part after `#`) using regular expressions:

```yaml
fragment_rules:
  # Match #L10 or #L10-L20
  - pattern: "^L(?P<start>\\d+)(?:-L(?P<end>\\d+))?$"
    apply:
      label: "Lines {start}-{end}"
      label_single: "Line {start}"   # Used when {end} group is absent
      data_type: example.line_ref
      hover: A line number reference.
```

Named regex groups (e.g., `(?P<start>\\d+)`) become placeholders in labels. If a group
named `end` is absent (didn't match), the `label_single` template is used instead of `label`.

**Note:** YAML requires escaping backslashes in regex patterns. Use `\\d` not `\d`.

## Label Templates

All `label` fields support `{value}` as a placeholder for the node's value:

```yaml
label: "User: {value}"      # -> "User: obsidianforensics"
label: "Issue #{value}"      # -> "Issue #42"
```

Fragment rules also support named group placeholders:

```yaml
label: "Lines {start}-{end}" # -> "Lines 10-20"
```

## The `apply` Block

Every rule has an `apply` block that defines what unfurl does when the rule matches:

| Field       | Required | Description |
|-------------|----------|-------------|
| `label`     | No       | Display label (supports `{value}` placeholder). Defaults to `{value}`. |
| `data_type` | No       | The data type for the created node. Defaults to `descriptor`. |
| `hover`     | No       | Hover/tooltip text (supports HTML like `<br>`, `<b>`, `<a>`). |
| `hover_only`| No       | If `true`, just sets hover text on the existing node (query rules only). |

### Choosing a `data_type`

- Use `descriptor` (the default) for informational labels that don't need further parsing.
- Use a site-specific type like `github.commit_hash` or `facebook.post_id` for values
  that might be parsed further by other unfurl parsers.
- Use `url` to have unfurl parse the value as a complete URL (useful for redirect parameters).
- Use timestamp types like `epoch-seconds` or `epoch-microseconds` to trigger unfurl's
  timestamp parser.

## Testing

Write unit tests in `unfurl/tests/unit/`. Use `has_node()` to check for specific nodes
by data_type, key, or value rather than checking exact node counts (which are fragile):

```python
from unfurl.core import Unfurl
import unittest

def has_node(unfurl_instance, **kwargs):
    for node in unfurl_instance.nodes.values():
        if all(getattr(node, k) == v for k, v in kwargs.items()):
            return True
    return False

class TestExample(unittest.TestCase):
    def test_user_url(self):
        test = Unfurl()
        test.add_to_queue(data_type='url', key=None,
                          value='https://example.com/johndoe')
        test.parse_queue()

        self.assertTrue(has_node(test, data_type='example.username', value='johndoe'))
```

## Examples

See the existing definitions in this directory for complete examples:
- `github.yaml` - Path rules, query rules, fragment rules, exclude_sibling
- `facebook.yaml` - Complex path rules, wildcard excludes, hover_only query rules
- `google.yaml` - Path-scoped query rules, hover_only for context-dependent parameters
- `instagram.yaml` - Multiple URL formats for the same content type
