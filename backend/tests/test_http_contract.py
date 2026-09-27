"""Pruebas del contrato HTTP contra respuestas de referencia guardadas."""
import argparse
import importlib.metadata
import json
import os
from pathlib import Path
import platform
import re
import unittest
from urllib.parse import urlsplit

from .contract_cases import cases

HERE = Path(__file__).parent
REFERENCE = HERE / "http_reference.json"

# Conjuntos habilitados
MIGRATED_PATH = re.compile(
    r"/grandsafelife/api/v1/(?:users/[^/]+|users/me/monitoring-requests|"
    r"homes(?:/[^/]+)?|homes/[^/]+/monitoring-requests|monitoring-requests/[^/]+/answer|"
    r"fall-detection/requests(?:/[^/]+)?)/?"
)


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
            from backend.http_api_rest.http_flask import create_http_app
            self.processor = RecordingProcessor(App(db=None))
            self.app = create_http_app(self.processor)
            if hasattr(self.app, "test_client"):
                self.kind = "flask"
                self.client = self.app.test_client()
            else:
                from fastapi.testclient import TestClient
                self.kind = "fastapi"
                self.client = TestClient(self.app, follow_redirects=False)

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
            if not (MIGRATED_PATH.fullmatch(case["path"].split("?")[0])
                    or case["name"].startswith("unknown-")):
                continue
            with self.subTest(case=case["name"]):
                expected = self.reference["cases"][case["name"]].copy()
                if self.transport.kind == "remote":
                    expected.pop("calls")
                self.assertEqual(self.transport.request(case), expected)

    def test_registered_routes(self):
        if self.transport.kind == "remote":
            self.skipTest("Una URL no permite inspeccionar el registro interno de rutas")
        expected = [route for route in self.reference["routes"]
                    if MIGRATED_PATH.fullmatch(route[1])]
        self.assertEqual(business_routes(self.transport), expected)


def business_routes(transport):
    if transport.kind == "flask":
        import re
        return sorted([method, re.sub(r"<(?:[^:>]+:)?([^>]+)>", r"{\1}", rule.rule)]
                      for rule in transport.app.url_map.iter_rules()
                      for method in rule.methods - {"HEAD", "OPTIONS"}
                      if rule.rule.startswith("/grandsafelife/"))
    # OpenAPI expands included routers even in versions that store them lazily.
    return sorted([method.upper(), path] for path, item in transport.app.openapi()["paths"].items()
                  for method in item if method in {"get", "post", "put", "patch", "delete"})


def capture():
    if REFERENCE.exists():
        raise SystemExit("La referencia ya existe: no sobrescribir automáticamente durante la migración.")
    transport = Transport()
    try:
        if transport.kind != "fastapi":
            raise SystemExit("La captura inicial requiere FastAPI local.")
        data = {"python": platform.python_version(), "versions": {
            name: importlib.metadata.version(name) for name in ("fastapi", "starlette", "pydantic", "httpx")
        }, "routes": business_routes(transport), "cases": {}}
        for case in cases():
            data["cases"][case["name"]] = transport.request(case)
        REFERENCE.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"Capturados {len(data['cases'])} casos y {len(data['routes'])} operaciones")
    finally:
        transport.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--capture", action="store_true")
    args = parser.parse_args()
    if args.capture:
        capture()
    else:
        unittest.main(argv=[__file__])
