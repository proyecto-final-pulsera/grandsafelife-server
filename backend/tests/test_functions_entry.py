"""Verifica el descubrimiento y la entrada HTTP de la función sin servicios externos."""

import json
import unittest
from unittest.mock import patch

from flask import Flask, request
from firebase_functions.private.serving import get_functions, functions_as_yaml
import yaml

from .contract_cases import cases
from .test_http_contract import REFERENCE, Transport


class FunctionsEntryTests(unittest.TestCase):
    def test_discovery(self):
        """El SDK descubre una sola función con los recursos configurados."""
        with patch("google.auth.default", side_effect=AssertionError("No se requieren credenciales")):
            functions = get_functions()
        self.assertEqual(set(functions), {"api"})
        endpoint = yaml.safe_load(functions_as_yaml(functions))["endpoints"]["api"]
        expected = {
            "entryPoint": "api", "platform": "gcfv2", "region": ["us-central1"],
            "minInstances": 0, "maxInstances": 10, "concurrency": 1,
            "cpu": 1, "availableMemoryMb": 256, "timeoutSeconds": 60,
            "httpsTrigger": {},
        }
        for key, value in expected.items():
            self.assertEqual(endpoint[key], value, key)

    def test_http_entry(self):
        """El contexto externo entrega todos los requests a api conservando sus respuestas."""
        from main import api

        outer = Flask("functions_entry_test", static_folder=None)

        def invoke(path=""):
            return api(request)

        methods = ["GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS"]
        outer.add_url_rule("/", view_func=invoke, methods=methods, provide_automatic_options=False)
        outer.add_url_rule("/<path:path>", view_func=invoke, methods=methods, provide_automatic_options=False)
        transport = Transport.__new__(Transport)
        transport.base_url = ""
        transport.processor = None
        transport.kind = "flask"
        transport.client = outer.test_client()
        reference = json.loads(REFERENCE.read_text(encoding="utf-8"))["cases"]
        try:
            with patch("google.auth.default", side_effect=AssertionError("No se requieren credenciales")):
                for case in cases():
                    with self.subTest(case=case["name"]):
                        expected = {k: v for k, v in reference[case["name"]].items() if k != "calls"}
                        self.assertEqual(transport.request(case), expected)
        finally:
            transport.close()


if __name__ == "__main__":
    unittest.main()
