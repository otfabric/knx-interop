#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Tests of the checks of scripts/smoke.py that need no Docker (a stand-in
answers its docker calls), and of scripts/document_schema.py, which checks
the documents against schemas/."""

import copy
import importlib.util
import json
import os
import subprocess
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import document_schema  # noqa: E402
import smoke  # noqa: E402

# Documents as the adapters print them (knxd: both roles with server
# features; cbsigma: a member the contract does not name; the probe: the
# smallest).
CAPABILITIES = {
    "knxd": json.loads('{"features":{"answer":true,"connect":true,"describe":false,"discover":false,"nat":true,"routing":true,'
                       '"secure":false,"tunnel":true,"dptCodec":false,"tcp":false,"property":false,"busmonitor":false,'
                       '"server":{"tcp":true,"property":false,"busmonitor":true}},"implementation":"knxd","notes":"...",'
                       '"roles":["server","client"],"schemaVersion":"1.0","upstream":{"name":"knxd","version":"0.14.73-1",'
                       '"independentEngine":true},"version":"0.14.73-1"}'),
    "cbsigma": json.loads('{"features":{"answer":true,"busmonitor":true,"dataSecure":true,"describe":true,"discover":true,'
                          '"keyring":true,"nat":true,"property":false,"remoteProperty":false,"routing":true,"secure":true,'
                          '"secureUdp":false,"surrogate":false,"tcp":true,"toolAccess":false,"tunnel":true},'
                          '"implementation":"cbsigma","notes":"...","roles":["client"],"schemaVersion":"1.0",'
                          '"simulator":{"name":"cB-Sigma knx-sim","revision":"","version":"v0.2.0"},'
                          '"upstream":{"independentEngine":true,"name":"cB-Sigma knx","revision":"","version":"v0.2.0"},'
                          '"version":"v0.2.0"}'),
    "probe": json.loads('{"features": {"describe": true, "negative": true}, "implementation": "probe", "roles": ["client"], '
                        '"schemaVersion": "1.0", "upstream": {"independentEngine": true, "name": "probe", "version": "1.0"}, '
                        '"version": "1.0"}'),
}
RESULT = json.loads('{"data": {}, "durationMs": 0, "error": "no DESCRIPTION_RESPONSE", "implementation": "probe", '
                    '"op": "describe", "schemaVersion": "1.0", "status": "fail", "version": "1.0"}')


class FakeDocker:
    """Answers smoke.docker(...) calls: `run ... capabilities` with a
    document, the licence listing with the missing components, a client
    operation with a result document and its exit status."""

    def __init__(self, capabilities=None, missing="", result=None, code=1):
        self.capabilities, self.missing, self.result, self.code = capabilities, missing, result, code
        self.calls = []

    def __call__(self, *args, timeout=120):
        self.calls.append(args)
        if args[-1] == "capabilities":
            return subprocess.CompletedProcess(args, 0, json.dumps(self.capabilities) + "\n", "")
        if "--entrypoint" in args and "sh" in args:
            return subprocess.CompletedProcess(args, 0, self.missing, "")
        if "client" in args:
            return subprocess.CompletedProcess(args, self.code, json.dumps(self.result) + "\n", "")
        return subprocess.CompletedProcess(args, 0, "", "")


class SmokeChecks(unittest.TestCase):
    def smoke(self, adapter, fake):
        orig = smoke.docker
        smoke.docker = fake
        self.addCleanup(setattr, smoke, "docker", orig)
        return smoke.Smoke(adapter, "image:test", "probe:test")

    def test_the_adapters_capabilities_pass(self):
        for name, doc in CAPABILITIES.items():
            self.assertIsNone(self.smoke(name, FakeDocker(doc)).capabilities(), name)

    def test_a_feature_that_is_not_a_boolean_fails(self):
        doc = copy.deepcopy(CAPABILITIES["knxd"])
        doc["features"]["tunnel"] = "yes"
        reason = self.smoke("knxd", FakeDocker(doc)).capabilities()
        self.assertIsNotNone(reason)
        self.assertIn("$.features.tunnel", reason)

    def test_a_server_feature_that_is_not_a_boolean_fails(self):
        doc = copy.deepcopy(CAPABILITIES["knxd"])
        doc["features"]["server"]["tcp"] = 1
        self.assertIn("$.features.server.tcp", self.smoke("knxd", FakeDocker(doc)).capabilities() or "")

    def test_an_unknown_role_fails(self):
        doc = copy.deepcopy(CAPABILITIES["probe"])
        doc["roles"] = ["client", "router"]
        self.assertIn("$.roles[1]", self.smoke("probe", FakeDocker(doc)).capabilities() or "")

    def test_an_upstream_revision_that_is_not_a_string_fails(self):
        doc = copy.deepcopy(CAPABILITIES["cbsigma"])
        doc["upstream"]["revision"] = None
        self.assertIn("$.upstream.revision", self.smoke("cbsigma", FakeDocker(doc)).capabilities() or "")

    def test_a_result_document_of_the_contract_passes(self):
        s = self.smoke("probe", FakeDocker(CAPABILITIES["probe"], result=RESULT, code=1))
        self.assertIsNone(s.client("describe", ("fail",)))

    def test_a_result_document_with_a_duration_that_is_not_a_number_fails(self):
        result = dict(RESULT, durationMs="12")
        s = self.smoke("probe", FakeDocker(CAPABILITIES["probe"], result=result, code=1))
        self.assertIn("$.durationMs", s.client("describe", ("fail",)) or "")

    def test_a_result_document_without_data_fails(self):
        result = dict(RESULT)
        del result["data"]
        s = self.smoke("probe", FakeDocker(CAPABILITIES["probe"], result=result, code=1))
        self.assertIn("'data' is missing", s.client("describe", ("fail",)) or "")

    def test_licence_texts_present(self):
        fake = FakeDocker()
        self.assertIsNone(self.smoke("cbsigma", fake).licences())
        self.assertEqual(fake.calls[-1][-4:], ("knx", "knx-sim", "go", "knx-interop"))

    def test_licence_texts_missing_fail(self):
        reason = self.smoke("xknx", FakeDocker(missing="knx-interop\n")).licences()
        self.assertEqual(reason, "no licence texts in /licenses/knx-interop/")

    def test_every_published_image_has_licence_texts(self):
        with open(os.path.join(os.path.dirname(HERE), "Makefile")) as f:
            published = [l.split("?=")[1].split() for l in f if l.startswith("PUBLISHED_ADAPTERS ?=")][0]
        self.assertEqual(sorted(smoke.LICENCES), sorted(published))


class DocumentSchema(unittest.TestCase):
    def test_types_follow_json(self):
        schema = {"type": "integer"}
        self.assertEqual(document_schema.errors(0, schema), [])
        self.assertEqual(document_schema.errors(2.0, schema), [])
        self.assertNotEqual(document_schema.errors(True, schema), [])
        self.assertNotEqual(document_schema.errors(1.5, schema), [])
        self.assertNotEqual(document_schema.errors(1, {"const": True}), [])
        self.assertNotEqual(document_schema.errors(False, {"enum": [0]}), [])

    def test_an_unsupported_keyword_is_refused(self):
        with self.assertRaises(document_schema.SchemaError):
            document_schema.errors("x", {"pattern": "^x$"})
        with self.assertRaises(document_schema.SchemaError):
            document_schema.errors({}, {"$ref": "https://example.com/other.json"})

    def test_the_schemas_use_only_supported_keywords(self):
        for name in ("capabilities", "client-result"):
            schema = document_schema.load(name)
            document_schema.errors({}, schema)  # raises SchemaError otherwise
            document_schema.errors(CAPABILITIES["knxd"], schema)

    @unittest.skipUnless(importlib.util.find_spec("jsonschema"), "jsonschema is not installed")
    def test_it_agrees_with_jsonschema(self):
        import jsonschema
        cases = {"capabilities": list(CAPABILITIES.values()), "client-result": [RESULT]}
        bad_caps = copy.deepcopy(CAPABILITIES["knxd"])
        bad_caps["features"]["server"]["busmonitor"] = "yes"
        no_upstream = copy.deepcopy(CAPABILITIES["probe"])
        del no_upstream["upstream"]
        cases["capabilities"] += [bad_caps, no_upstream, dict(CAPABILITIES["probe"], roles=[]), dict(CAPABILITIES["probe"], schemaVersion="2.0")]
        cases["client-result"] += [dict(RESULT, status="skip"), dict(RESULT, durationMs=-1), dict(RESULT, error=None), dict(RESULT, data=[])]
        for name, docs in cases.items():
            schema = document_schema.load(name)
            jsonschema.Draft202012Validator.check_schema(schema)
            validator = jsonschema.Draft202012Validator(schema)
            for doc in docs:
                ours = document_schema.errors(doc, schema)
                theirs = list(validator.iter_errors(doc))
                self.assertEqual(bool(ours), bool(theirs), "%s %s: ours %s, jsonschema %s" % (
                    name, json.dumps(doc)[:80], ours, [e.message for e in theirs]))


if __name__ == "__main__":
    unittest.main()
