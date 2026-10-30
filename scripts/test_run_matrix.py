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


def matrix():
    return rm.Matrix(types.SimpleNamespace(external={}, gate="", report="latest", registry="r", version="v"))


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

    def test_a_scenario_without_an_id_stops_the_run(self):
        with self.assertRaises(SystemExit):
            matrix().record("tunnel", "not in the table", "xknx", "knxd", "pass", time.monotonic())


if __name__ == "__main__":
    unittest.main()
