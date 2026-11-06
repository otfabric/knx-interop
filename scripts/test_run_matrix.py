#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Tests of the results of scripts/run-matrix.py that need no Docker."""

import importlib.util
import os
import time
import types
import unittest

import interop_result

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("run_matrix", os.path.join(HERE, "run-matrix.py"))
rm = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rm)


def matrix(external=None, only=()):
    return rm.Matrix(types.SimpleNamespace(external=external or {}, only=list(only), gate="", report="latest", registry="r", version="v"))


class Results(unittest.TestCase):
    def document(self, m):
        doc = m.result_document("2026-10-30T00:00:00Z")
        doc["summary"] = interop_result.summarize(doc["results"])
        return doc

    def test_a_reproduced_waiver_is_a_known_difference(self):
        m = matrix()
        m.record("tunnel", "describe", "knxultimate", "knxd", "fail", time.monotonic(), "no answer")
        m.record("tunnel", "connect and disconnect", "xknx", "knxd", "pass", time.monotonic())
        doc = self.document(m)
        self.assertEqual(doc["results"][0]["outcome"], "known-difference")
        self.assertEqual(doc["results"][0]["waiver"], "knxultimate-describe-hpai-port")
        self.assertEqual(interop_result.problems(doc), [])
        self.assertEqual(interop_result.schema_errors(doc), [])

    def test_a_waiver_that_passes_is_stale_and_fails_the_run(self):
        m = matrix()
        m.record("tunnel", "describe", "knxultimate", "knxd", "pass", time.monotonic())
        doc = self.document(m)
        self.assertFalse(doc["waivers"][0]["reproduced"])
        self.assertTrue(interop_result.problems(doc))

    def test_an_all_unsupported_run_fails(self):
        m = matrix()
        m.record("tunnel", "describe", "xknx", "knxd", "unsupported", time.monotonic(), None)
        self.assertTrue(interop_result.problems(self.document(m)))

    def test_a_server_that_does_not_start_is_an_infrastructure_error(self):
        m = matrix()
        m.record("tunnel", "server start", "-", "knxd", "fail", time.monotonic(), "did not answer")
        doc = self.document(m)
        self.assertEqual(doc["results"][0]["outcome"], "infra-error")
        self.assertEqual(doc["results"][0]["roles"], {"peer": "knxd"})

    def test_independent_is_what_the_image_says(self):
        m = matrix(external={"sut": "img"}, only=["own", "xknx", "sut", "old"])
        m.caps = {"own": {"version": "v1", "upstream": {"independentEngine": False}},
                  "xknx": {"version": "4.0.0", "upstream": {"independentEngine": True}},
                  "sut": {"version": "x"}, "old": {"version": "y"}}
        got = {i["name"]: i["independent"] for i in m.result_document("2026-11-06T00:00:00Z")["implementations"]}
        self.assertEqual(got, {"own": False, "xknx": True, "sut": False, "old": True})
        # A stack that is not independent is preferred as observer; with
        # --adapters, nothing outside the list is used.
        self.assertEqual(m.helpers("xknx", "calimero-tools"), ["sut", "own", "xknx"])

    def test_an_image_override_wins(self):
        m = matrix(external={"sut": "img"})
        os.environ["ADAPTER_IMAGE_calimero_server"] = "local/cs:1"
        try:
            self.assertEqual(m.image("calimero-server"), "local/cs:1")
        finally:
            del os.environ["ADAPTER_IMAGE_calimero_server"]
        self.assertEqual(m.image("sut"), "img")
        self.assertEqual(m.image("xknx"), "r/knx-interop-xknx:v")

    def test_a_scenario_without_an_id_stops_the_run(self):
        with self.assertRaises(SystemExit):
            matrix().record("tunnel", "not in the table", "xknx", "knxd", "pass", time.monotonic())


if __name__ == "__main__":
    unittest.main()
