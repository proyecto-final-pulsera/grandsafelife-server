"""Contratos de hogares para los flujos de la app de monitores."""
import unittest
from backend.app.app import App
from backend.http_api_rest.http import create_http_app
from tests.api_rest.test_http_contract import RecordingProcessor


class HomesSyncTests(unittest.TestCase):
    def setUp(self):
        self.processor = RecordingProcessor(App(db=None))
        self.client = create_http_app(self.processor).test_client()
        self.headers = {"Authorization": "Bearer local-test"}

    def test_create_and_update_members(self):
        members = {"u1": {"email": "u@example.com", "role": "admin"}}
        body = {"name": "Casa", "members": members}
        response = self.client.post("/grandsafelife/api/v1/homes", headers=self.headers, json=body)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["resp"], "home_id_001")
        self.assertEqual(self.processor.calls[-1]["args"][-1], body)
        for role in ("pending", "observer", "admin"):
            members["u2"] = {"email": "other@example.com", "role": role}
            response = self.client.patch("/grandsafelife/api/v1/homes/h1",
                headers=self.headers, json={"members": members})
            self.assertEqual(response.status_code, 200)
            self.assertEqual(self.processor.calls[-1]["args"][-1], {"members": members})
        for patch in ({"members": {}}, {"name": "Otro nombre"}):
            response = self.client.patch("/grandsafelife/api/v1/homes/h1", headers=self.headers, json=patch)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(self.processor.calls[-1]["args"][-1], patch)

    def test_invalid_bodies_do_not_reach_business(self):
        for method, path in (("POST", "/homes"), ("PATCH", "/homes/h1")):
            for extra in ({"members": None}, {"created_at": 123}, {"id": "h1"},
                          {"members": {"u": {"email": "a", "role": "invalid"}}}):
                response = self.client.open("/grandsafelife/api/v1" + path, method=method,
                    headers=self.headers, json={"name": "Casa", **extra})
                self.assertEqual(response.status_code, 422)
        self.assertEqual(self.processor.calls, [])
