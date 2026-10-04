"""Dispositivos: DEVICES_T1 a DEVICES_T11 del detalle de tests de API REST."""
from unittest.mock import patch
from backend.app.processes.process_devices import DevicesProcesses
from backend.http_api_rest.http_endpoints_devices import DevicesEndpoints
from base_api_test import BaseApiTest

class DevicesTests(BaseApiTest):
    test_all_routes_reject_invalid_token_before_process = (
        BaseApiTest.assert_all_routes_reject_invalid_token_before_process
    )
    endpoints_class = DevicesEndpoints
    process_class = DevicesProcesses
    prefix = "/grandsafelife/api/v1"

    def test_DEVICES_T1_create_device(self):
        """
        `POST /devices`:
        aceptar ID explícito o ausente; devolver un ID no vacío como string y conservar `data` separado de `device_id`.
        """
        data = {"id": "embedded-id", "device_id": "data-id", "name": "Pulsera",
                "owner_id": None, "extra": [True, None], "created_at": 123}
        for target in ("target", None):
            with self.subTest(device_id=target):
                body = {"data": data}
                if target is not None:
                    body["device_id"] = target
                response = self.client.post(f"{self.prefix}/devices", headers=self.headers, json=body)
                self.assert_success(response)
                device_id = response.json["resp"]
                self.assertIsInstance(device_id, str)
                self.assertTrue(device_id)
                if target is not None:
                    self.assertEqual(device_id, target)
                else:
                    self.assertNotIn(device_id, (data["id"], data["device_id"]))
                self.assert_last_call("process_create_device", data, target)

    def test_DEVICES_T2_get_device_by_id(self):
        """
        `GET /devices/{device_id}`:
        retornar el ID solicitado, campos del dispositivo y fechas en milisegundos.
        """
        response = self.client.get(f"{self.prefix}/devices/target", headers=self.headers)
        self.assert_success(response)
        device = response.json["resp"]
        self.assertEqual(device["id"], "target")
        for field in ("home_id", "owner_id", "connection_by", "type", "name"):
            self.assertIsInstance(device[field], str)
        self.assertIs(type(device["is_active"]), bool)
        self.assertIs(type(device["battery"]), int)
        for field in ("created_at", "updated_at"):
            self.assertIs(type(device[field]), int)
            self.assertGreater(device[field], 1_000_000_000_000)
        self.assertEqual(set(device["coords"]), {"lat", "long"})
        for value in device["coords"].values():
            self.assertIn(type(value), (int, float))
        self.assert_last_call("process_get_device_by_id", "target")

    def test_DEVICES_T3_update_device_preserving_fields(self):
        """
        `PATCH /devices/{device_id}`:
        conservar campos parciales, nulos y rutas con puntos; cubrir datos para asociar/liberar el dispositivo y connection_by vacío, phone o ID de hub sin interpretar permisos.
        """
        for data in (
            {"name": "Nuevo nombre"},
            {"name": None, "created_at": 123, "updated_at": None, "extra": [1, None]},
            {"coords.lat": -34.6, "coords.long": -58.4},
            {"home_id": "home-target", "owner_id": "owner-target", "connection_by": "hub-target"},
            {"home_id": "", "owner_id": "", "connection_by": ""},
            {"connection_by": "phone"},
        ):
            with self.subTest(data=data):
                response = self.client.patch(f"{self.prefix}/devices/target", headers=self.headers, json=data)
                self.assert_success(response)
                self.assertNotIn("resp", response.json)
                self.assert_last_call("process_update_device", "target", data)

    def test_DEVICES_T4_delete_device(self):
        """
        `DELETE /devices/{device_id}`:
        llamar al process de eliminación, no al de actualización; responder sin `resp`.
        """
        response = self.client.delete(f"{self.prefix}/devices/target", headers=self.headers)
        self.assert_success(response)
        self.assertNotIn("resp", response.json)
        self.assert_last_call("process_delete_device", "target")
        self.assertEqual(len(self.processor.calls), 1)

    def test_DEVICES_T5_get_devices_by_owner(self):
        """
        `GET /users/{owner_id}/devices`:
        delegar owner_id y devolver un mapa de dispositivos indexado por ID, compatible con el datasource.
        """
        response = self.client.get(f"{self.prefix}/users/owner-target/devices", headers=self.headers)
        self.assert_success(response)
        devices = response.json["resp"]
        self.assertIsInstance(devices, dict)
        self.assertTrue(devices)
        for device_id, device in devices.items():
            self.assertIsInstance(device_id, str)
            self.assertTrue(device_id)
            self.assertIsInstance(device, dict)
            self.assertIsInstance(device["owner_id"], str)
            self.assertIsInstance(device["name"], str)
        self.assert_last_call("process_get_devices_by_owner", "owner-target")

    def test_DEVICES_T6_get_devices_by_home(self):
        """
        `GET /homes/{home_id}/devices`:
        delegar home_id y devolver el mapa de dispositivos, incluyendo un hub en el mock.
        """
        response = self.client.get(f"{self.prefix}/homes/home-target/devices", headers=self.headers)
        self.assert_success(response)
        devices = response.json["resp"]
        self.assertIsInstance(devices, dict)
        self.assertTrue(devices)
        for device_id, device in devices.items():
            self.assertIsInstance(device_id, str)
            self.assertTrue(device_id)
            self.assertIsInstance(device, dict)
            self.assertIsInstance(device["home_id"], str)
            self.assertIsInstance(device["type"], str)
        self.assertTrue(any(device["type"] == "hub" for device in devices.values()))
        self.assert_last_call("process_get_devices_by_home", "home-target")

    def test_DEVICES_T7_get_device_location(self):
        """
        `GET /devices/{device_id}/location`:
        delegar el ID y devolver coordenadas numéricas `lat` y `long`."""
        response = self.client.get(f"{self.prefix}/devices/target/location", headers=self.headers)
        self.assert_success(response)
        location = response.json["resp"]
        self.assertIsInstance(location, dict)
        self.assertEqual(set(location), {"lat", "long"})
        for value in location.values():
            self.assertIn(type(value), (int, float))
        self.assert_last_call("process_get_device_location", "target")

    def test_DEVICES_T8_get_missing_device_and_empty_queries(self):
        """
        Lecturas: simular dispositivo inexistente (`null`) y consultas por owner/home sin resultados (`{}`).
        """
        for path, method, target, result in (
            ("/devices/missing", "process_get_device_by_id", "missing", None),
            ("/users/owner-target/devices", "process_get_devices_by_owner", "owner-target", {}),
            ("/homes/home-target/devices", "process_get_devices_by_home", "home-target", {}),
        ):
            with self.subTest(path=path):
                with patch.object(self.processor.process, method, return_value=result):
                    response = self.client.get(self.prefix + path, headers=self.headers)
                self.assert_success(response)
                self.assertIn("resp", response.json)
                self.assertEqual(response.json["resp"], result)
                self.assert_last_call(method, target)

    def test_DEVICES_T9_get_available_device_mock(self):
        """
        `GET /devices/dev_available`:
        comprobar que el mock de dispositivo disponible tenga home_id, owner_id y connection_by vacíos.
        """
        response = self.client.get(f"{self.prefix}/devices/dev_available", headers=self.headers)
        self.assert_success(response)
        device = response.json["resp"]
        self.assertEqual(device["id"], "dev_available")
        for field in ("home_id", "owner_id", "connection_by"):
            self.assertEqual(device[field], "")
        self.assert_last_call("process_get_device_by_id", "dev_available")

    def test_DEVICES_T10_reject_requests_without_authorization(self):
        """
        Los siete endpoints: rechazar requests sin Authorization.
        """
        for method, path, body in (
            ("POST", "/devices", {"data": {}}),
            ("GET", "/devices/target", None),
            ("PATCH", "/devices/target", {"name": "Pulsera"}),
            ("DELETE", "/devices/target", None),
            ("GET", "/users/owner-target/devices", None),
            ("GET", "/homes/home-target/devices", None),
            ("GET", "/devices/target/location", None),
        ):
            with self.subTest(method=method, path=path):
                response = self.client.open(self.prefix + path, method=method,
                                            **({"json": body} if body is not None else {}))
                self.assert_rejected(response)

    def test_DEVICES_T11_validate_bodies_and_accept_empty_data(self):
        """
        Rechazar envoltorio de creación inválido, device_id vacío/no textual y body de actualización que no sea objeto; aceptar data y actualización vacíos.
        """
        # Todos los rechazos se comprueban antes de los requests válidos,
        # ya que assert_rejected exige un registro de llamadas vacío.
        for body in ([], 123, "invalid", {}, {"data": []}, {"data": None},
                     {"data": {}, "device_id": ""}, {"data": {}, "device_id": 123},
                     {"data": {}, "device_id": False}, {"data": {}, "extra": 1}):
            with self.subTest(create_body=body):
                self.assert_rejected(self.client.post(f"{self.prefix}/devices", headers=self.headers, json=body))
        for body in ([], 123, "invalid", False):
            with self.subTest(update_body=body):
                self.assert_rejected(self.client.patch(f"{self.prefix}/devices/target", headers=self.headers, json=body))
        for method, path in (("POST", "/devices"), ("PATCH", "/devices/target")):
            for raw_body in (None, "null", "{"):
                with self.subTest(method=method, raw_body=raw_body):
                    response = self.client.open(self.prefix + path, method=method,
                                                headers=self.headers, data=raw_body,
                                                content_type="application/json")
                    self.assert_rejected(response)
        for target in ("target", None):
            with self.subTest(operation="create_empty", device_id=target):
                body = {"data": {}}
                if target is not None:
                    body["device_id"] = target
                response = self.client.post(f"{self.prefix}/devices", headers=self.headers, json=body)
                self.assert_success(response)
                self.assertIsInstance(response.json["resp"], str)
                self.assertTrue(response.json["resp"])
                if target is not None:
                    self.assertEqual(response.json["resp"], target)
                self.assert_last_call("process_create_device", {}, target)
        with self.subTest(operation="update_empty"):
            response = self.client.patch(f"{self.prefix}/devices/target", headers=self.headers, json={})
            self.assert_success(response)
            self.assertNotIn("resp", response.json)
            self.assert_last_call("process_update_device", "target", {})
