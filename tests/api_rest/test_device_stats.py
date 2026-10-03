"""Contratos de usuarios consumidos por la aplicación de monitores."""
import unittest

from backend.app.app import App
from backend.http_api_rest.http import create_http_app
from tests.api_rest.test_http_contract import RecordingProcessor


class UsersSyncTests(unittest.TestCase):
    def setUp(self):
        self.processor = RecordingProcessor(App(db=None))
        self.client = create_http_app(self.processor).test_client()
        self.headers = {"Authorization": "Bearer test-token"}

    def test_create_with_nullable_or_omitted_avatar(self):
        for extra in ({}, {"avatar": None}):
            response = self.client.post("/grandsafelife/api/v1/users",
                headers=self.headers, json={"data": {"name": "María", "email": "m@example.com", **extra}})
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json["resp"], {"user_id": "firebase_uid_mock"})

    def test_update_targets_requested_user_and_preserves_fields(self):
        for body in ({"avatar": None}, {"homes": {}}, {"name": "María"},
                     {"homes": {"h1": {"home_name": "Casa", "role": "pending"}}}):
            response = self.client.patch("/grandsafelife/api/v1/users/other-user",
                headers=self.headers, json=body)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(self.processor.calls[-1], {
                "method": "process_update_user",
                "args": ["Bearer test-token", "other-user", body], "kwargs": {},
            })
            self.assertNotIn("resp", response.json)

    def test_invalid_update_does_not_reach_processor(self):
        for body in ([], 123, "invalid"):
            response = self.client.patch("/grandsafelife/api/v1/users/other-user",
                headers=self.headers, json=body)
            self.assertEqual(response.status_code, 422, body)
            self.assertIn("detail", response.json)
        self.assertEqual(self.processor.calls, [])

    def test_writes_require_authorization(self):
        for method, path, body in (
            ("POST", "", {"data": {"name": "María", "email": "m@example.com"}}),
            ("PATCH", "other-user", {"homes": {}}),
        ):
            response = self.client.open(("/grandsafelife/api/v1/users" + (f"/{path}" if path else "")),
                method=method, json=body)
            self.assertEqual(response.status_code, 422)
        self.assertEqual(self.processor.calls, [])
