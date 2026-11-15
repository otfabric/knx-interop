#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Checks the adapters' documents against schemas/ with the standard library,
so that scripts/smoke.py needs no third-party package:

    capabilities.schema.json    run capabilities
    client-result.schema.json   run client <op>

It implements the JSON Schema 2020-12 keywords these schemas use and refuses
a schema with any other keyword (SchemaError), so a schema can never rely on
a check that is silently skipped. The unit tests compare it with the
jsonschema package where that is installed.

    document_schema.py <capabilities|client-result> <document.json>...
"""

import json
import os
import sys

SCHEMAS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "schemas")

# Annotations, and the assertions errors() implements.
KEYWORDS = {"$schema", "$id", "$defs", "title", "description",
            "$ref", "type", "const", "enum", "required", "properties", "additionalProperties",
            "items", "minItems", "uniqueItems", "minLength", "minimum"}

TYPES = {
    "object": lambda v: isinstance(v, dict),
    "array": lambda v: isinstance(v, list),
    "string": lambda v: isinstance(v, str),
    "boolean": lambda v: isinstance(v, bool),
    "integer": lambda v: (isinstance(v, int) and not isinstance(v, bool)) or (isinstance(v, float) and v.is_integer()),
    "number": lambda v: isinstance(v, (int, float)) and not isinstance(v, bool),
    "null": lambda v: v is None,
}


class SchemaError(ValueError):
    """The schema uses something errors() does not implement."""


def load(name):
    """The schema schemas/<name>.schema.json."""
    with open(os.path.join(SCHEMAS, name + ".schema.json")) as f:
        return json.load(f)


def _equal(a, b):
    # JSON equality: true is not 1.
    return type(a) is type(b) and a == b if isinstance(a, bool) or isinstance(b, bool) else a == b


def _check(value, schema, root, path, out):
    if schema is True:
        return
    if schema is False:
        out.append("%s: not allowed" % path)
        return
    unknown = set(schema) - KEYWORDS
    if unknown:
        raise SchemaError("unsupported keyword(s) %s at %s" % (", ".join(sorted(unknown)), path))
    if "$ref" in schema:
        ref = schema["$ref"]
        if not ref.startswith("#/$defs/") or ref[len("#/$defs/"):] not in root.get("$defs", {}):
            raise SchemaError("unsupported $ref %r at %s" % (ref, path))
        _check(value, root["$defs"][ref[len("#/$defs/"):]], root, path, out)
    if "type" in schema:
        types = schema["type"] if isinstance(schema["type"], list) else [schema["type"]]
        if any(t not in TYPES for t in types):
            raise SchemaError("unsupported type %r at %s" % (schema["type"], path))
        if not any(TYPES[t](value) for t in types):
            out.append("%s: %s is not of type %s" % (path, json.dumps(value), " or ".join(types)))
            return
    if "const" in schema and not _equal(value, schema["const"]):
        out.append("%s: %s, want %s" % (path, json.dumps(value), json.dumps(schema["const"])))
    if "enum" in schema and not any(_equal(value, e) for e in schema["enum"]):
        out.append("%s: %s is not one of %s" % (path, json.dumps(value), json.dumps(schema["enum"])))
    if isinstance(value, str) and len(value) < schema.get("minLength", 0):
        out.append("%s: shorter than %d" % (path, schema["minLength"]))
    if TYPES["number"](value) and "minimum" in schema and value < schema["minimum"]:
        out.append("%s: %s is less than %s" % (path, value, schema["minimum"]))
    if isinstance(value, list):
        if len(value) < schema.get("minItems", 0):
            out.append("%s: fewer than %d items" % (path, schema["minItems"]))
        if schema.get("uniqueItems") and len({json.dumps(v, sort_keys=True) for v in value}) != len(value):
            out.append("%s: items are not unique" % path)
        if "items" in schema:
            for i, v in enumerate(value):
                _check(v, schema["items"], root, "%s[%d]" % (path, i), out)
    if isinstance(value, dict):
        for key in schema.get("required", ()):
            if key not in value:
                out.append("%s: %r is missing" % (path, key))
        properties = schema.get("properties", {})
        for key, v in value.items():
            if key in properties:
                _check(v, properties[key], root, "%s.%s" % (path, key), out)
            elif "additionalProperties" in schema:
                _check(v, schema["additionalProperties"], root, "%s.%s" % (path, key), out)


def errors(document, schema):
    """The ways document does not match schema, as "<path>: <problem>"
    (empty when it matches). Raises SchemaError for a keyword it does not
    implement."""
    out = []
    _check(document, schema, schema, "$", out)
    return out


def main(argv):
    if len(argv) < 2:
        print(__doc__, file=sys.stderr)
        return 2
    schema = load(argv[0])
    failed = 0
    for path in argv[1:]:
        with open(path) as f:
            problems = errors(json.load(f), schema)
        for p in problems:
            print("FAIL %s: %s" % (path, p))
        if not problems:
            print("ok   %s" % path)
        failed += bool(problems)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
