"""Pruebas del contrato HTTP contra respuestas de referencia guardadas."""
import json
import os
from pathlib import Path
import re
import unittest
from urllib.parse import urlsplit

from .contract_cases import cases

HERE = Path(__file__).parent
REFERENCE = HERE / "http_reference.json"

class RecordingProcessor:
    def __init__(self, app):
        self.app = app
        self.calls = []

    def __getattr__(self, name):
        target = getattr(self.app, name)

        def call(*args, **kwargs):
            self.calls.append({"method": name, "args": list(args), "kwargs": kwargs})
            return target(*args, **kwargs)
        return call


class Transport:
    def __init__(self):
        self.base_url = os.environ.get("CONTRACT_BASE_URL", "").rstrip("/")
        self.processor = None
        if self.base_url:
            import httpx
            self.client = httpx.Client(follow_redirects=False, timeout=20)
            self.kind = "remote"
        else:
            from backend.app.app import App
            from backend.http_api_rest.http import create_http_app
            self.processor = RecordingProcessor(App(db=None))
            self.app = create_http_app(self.processor)
            self.kind = "flask"
            self.client = self.app.test_client()

    def request(self, case):
        kwargs = {k: v for k, v in case.items() if k in ("headers", "json", "content")}
        if self.processor:
            self.processor.calls.clear()
        if self.kind == "flask":
            if "content" in kwargs:
                kwargs["data"] = kwargs.pop("content")
            response = self.client.open(case["path"], method=case["method"], follow_redirects=False, **kwargs)
            raw = response.get_data(as_text=True)
        else:
            response = self.client.request(case["method"], self.base_url + case["path"], **kwargs)
            raw = response.text
        try:
            body = json.loads(raw)
        except ValueError:
            body = raw
        # Compare semantic HTTP headers; omit deployment-specific Date/Server/length.
        headers = {key: response.headers[key] for key in ("content-type", "allow", "location") if key in response.headers}
        if "location" in headers:
            location = urlsplit(headers["location"])
            base_path = urlsplit(self.base_url).path
            path = location.path
            if base_path and path.startswith(base_path + "/"):
                path = path[len(base_path):]
            headers["location"] = path + ("?" + location.query if location.query else "")
        result = {"status": response.status_code, "headers": headers, "body": body}
        if self.processor:
            result["calls"] = self.processor.calls.copy()
        return result

    def close(self):
        if hasattr(self.client, "close"):
            self.client.close()


class HttpContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.reference = json.loads(REFERENCE.read_text(encoding="utf-8"))
        cls.transport = Transport()

    @classmethod
    def tearDownClass(cls):
        cls.transport.close()

    def test_contract(self):
        requests = cases()
        self.assertEqual([c["name"] for c in requests], list(self.reference["cases"]))
        for case in requests:
            with self.subTest(case=case["name"]):
                expected = self.reference["cases"][case["name"]].copy()
                if self.transport.kind == "remote":
                    expected.pop("calls")
                self.assertEqual(self.transport.request(case), expected)

    def test_registered_routes(self):
        if self.transport.kind == "remote":
            self.skipTest("Una URL no permite inspeccionar el registro interno de rutas")
        expected = self.reference["routes"]
        self.assertEqual(business_routes(self.transport), expected)


def business_routes(transport):
    return sorted([method, re.sub(r"<(?:[^:>]+:)?([^>]+)>", r"{\1}", rule.rule)]
                  for rule in transport.app.url_map.iter_rules()
                  for method in rule.methods - {"HEAD", "OPTIONS"}
                  if rule.rule.startswith("/grandsafelife/"))


if __name__ == "__main__":
    unittest.main()
