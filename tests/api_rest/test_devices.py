"""Validación del contrato de dispositivos de la app."""
import unittest
from backend.app.app import App
from backend.http_api_rest.http import create_http_app
from tests.api_rest.test_http_contract import RecordingProcessor


class DevicesSyncTests(unittest.TestCase):
    def setUp(self):
        self.processor = RecordingProcessor(App(db=None))
        self.client = create_http_app(self.processor).test_client()
        self.headers = {"Authorization": "Bearer local-test"}

    def test_association_configuration_and_release(self):
        for body in (
            {"name": "Pulsera", "type": "pulsera", "battery": 80,
             "is_active": True, "home_id": "h1", "owner_id": "u1", "connection_by": ""},
            {"connection_by": "phone"}, {"connection_by": "hub_1"},
            {"type": "hub", "battery": -1}, {"home_id": "", "owner_id": ""},
        ):
            response = self.client.patch("/grandsafelife/api/v1/devices/d1", headers=self.headers, json=body)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(self.processor.calls[-1]["args"][-1], body)

    def test_preserves_partial_document_fields(self):
        body = {"id": "stored-id", "created_at": 123, "coords": {"lat": 1, "long": 2},
                "custom": None, "settings.enabled": False}
        response = self.client.patch("/grandsafelife/api/v1/devices/d1", headers=self.headers, json=body)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.processor.calls[-1]["args"], ["Bearer local-test", "d1", body])

    def test_creation_with_optional_id_and_separate_document_data(self):
        data = {"id": "stored-id", "device_id": "stored-field", "coords": {"lat": 1, "long": 2}}
        for device_id in ("chosen-id", None):
            body = {"data": data}
            if device_id is not None:
                body["device_id"] = device_id
            response = self.client.post("/grandsafelife/api/v1/devices", headers=self.headers, json=body)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(self.processor.calls[-1]["args"], ["Bearer local-test", data, device_id])
            self.assertTrue(response.json["resp"])
            if device_id:
                self.assertEqual(response.json["resp"], device_id)

    def test_delete_is_distinct_from_release(self):
        for suffix, method in (("", "process_delete_device"), ("/association", "process_release_device")):
            response = self.client.delete("/grandsafelife/api/v1/devices/d1" + suffix, headers=self.headers)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json, {"op_status": 0, "brief": "Operation completed successfully"})
            self.assertEqual(self.processor.calls[-1]["method"], method)

    def test_missing_document_is_explicit_null(self):
        from unittest.mock import patch
        with patch.object(self.processor.app, "process_get_device_by_id", return_value=None):
            response = self.client.get("/grandsafelife/api/v1/devices/missing", headers=self.headers)
        self.assertEqual(response.status_code, 200)
        self.assertIsNone(response.json["resp"])

    def test_rejects_invalid_body_and_missing_authorization(self):
        for body in ([], "bad", 1):
            response = self.client.patch("/grandsafelife/api/v1/devices/d1", headers=self.headers, json=body)
            self.assertEqual(response.status_code, 422)
        for body in ({}, {"data": []}, {"data": {}, "device_id": ""}, {"data": {}, "unexpected": 1}):
            response = self.client.post("/grandsafelife/api/v1/devices", headers=self.headers, json=body)
            self.assertEqual(response.status_code, 422)
        for method, path, body in (("POST", "/devices", {"data": {}}), ("DELETE", "/devices/d1", None)):
            response = self.client.open("/grandsafelife/api/v1" + path, method=method, json=body)
            self.assertEqual(response.status_code, 422)
        self.assertEqual(self.processor.calls, [])

    def test_available_device_and_hub_dates(self):
        response = self.client.get("/grandsafelife/api/v1/devices/dev_available", headers=self.headers)
        device = response.json["resp"]
        self.assertEqual(device["home_id"], "")
        self.assertEqual(device["owner_id"], "")
        self.assertIsInstance(device["created_at"], int)
        response = self.client.get("/grandsafelife/api/v1/homes/h1/devices", headers=self.headers)
        self.assertTrue(any(d["type"] == "hub" and d["battery"] == -1 for d in response.json["resp"].values()))
