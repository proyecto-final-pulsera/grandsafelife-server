"""Hogares: HOMES_T1 a HOMES_T8 del detalle de tests de API REST."""
from unittest.mock import patch
from backend.app.processes.process_homes import HomesProcesses
from backend.http_api_rest.http_endpoints_homes import HomesEndpoints
from base_api_test import BaseApiTest

class HomesTests(BaseApiTest):
    test_all_routes_reject_invalid_token_before_process = (
        BaseApiTest.assert_all_routes_reject_invalid_token_before_process
    )
    endpoints_class = HomesEndpoints
    process_class = HomesProcesses
    prefix = "/grandsafelife/api/v1/homes"

    def test_HOMES_T1_get_home_by_id(self):
        """
        `GET /homes/{home_id}`:
        delegar el ID solicitado y devolver el mapa del hogar con miembros y fechas en milisegundos.
        """
        response = self.client.get(f"{self.prefix}/target", headers=self.headers)
        self.assert_success(response)
        home = response.json["resp"]
        self.assertIsInstance(home, dict)
        self.assertIsInstance(home["name"], str)
        self.assertTrue(home["members"])
        self.assertIsInstance(home["members"], dict)
        for member in home["members"].values():
            self.assertIsInstance(member["email"], str)
            self.assertIsInstance(member["role"], str)
        for field in ("created_at", "updated_at"):
            self.assertIs(type(home[field]), int)
            self.assertGreater(home[field], 1_000_000_000_000)
        self.assert_last_call("process_get_home_by_id", "target")

    def test_HOMES_T2_create_home_with_explicit_and_missing_id(self):
        """
        `POST /homes`:
        aceptar ID explícito o ausente; devolver el ID como string en `resp`. El campo `id` dentro de `data` no debe reemplazar `home_id`
        """
        data = {"id": "embedded-id", "name": "Hogar", "members": {},
                "created_at": 123, "updated_at": None, "extra": [True, None]}
        for target in ("target", None):
            with self.subTest(home_id=target):
                body = {"data": data}
                if target is not None:
                    body["home_id"] = target
                response = self.client.post(self.prefix, headers=self.headers, json=body)
                self.assert_success(response)
                self.assertIsInstance(response.json["resp"], str)
                self.assertEqual(response.json["resp"], target or "home_id_001")
                self.assert_last_call("process_create_home", data, target)

    def test_HOMES_T3_update_home_preserving_fields(self):
        """
        `PATCH /homes/{home_id}`:
        delegar campos parciales, nulos, mapas de miembros y rutas con puntos sin modificarlos; responder sin `resp`.
        """
        for data in (
            {"name": "Nuevo nombre"},
            {"name": None, "created_at": 123, "updated_at": None},
            {"members": {"user-1": {"email": "test@example.com", "role": "admin"}}},
            {"members.user-1.role": "observer", "extra": [1, None]},
        ):
            with self.subTest(data=data):
                response = self.client.patch(f"{self.prefix}/target", headers=self.headers, json=data)
                self.assert_success(response)
                self.assertNotIn("resp", response.json)
                self.assert_last_call("process_update_home", "target", data)

    def test_HOMES_T4_delete_home(self):
        """
        `DELETE /homes/{home_id}`:
        llamar solo al process de eliminación con el ID correcto y responder sin `resp`.
        """
        response = self.client.delete(f"{self.prefix}/target", headers=self.headers)
        self.assert_success(response)
        self.assertNotIn("resp", response.json)
        self.assert_last_call("process_delete_home", "target")
        self.assertEqual(len(self.processor.calls), 1)

    def test_HOMES_T5_get_missing_and_empty_home(self):
        """
        `GET /homes/{home_id}`:
        simular documento inexistente (`null`) y documento existente vacío (`{}`), distinguiendo ambas respuestas.
        """
        for result in (None, {}):
            with self.subTest(process_result=result):
                with patch.object(self.processor.process, "process_get_home_by_id", return_value=result):
                    response = self.client.get(f"{self.prefix}/target", headers=self.headers)
                self.assert_success(response)
                self.assertIn("resp", response.json)
                self.assertEqual(response.json["resp"], result)
                self.assert_last_call("process_get_home_by_id", "target")

    def test_HOMES_T6_reject_requests_without_authorization(self):
        """
        Los cuatro endpoints: rechazar requests sin Authorization.
        """
        for method, path, body in (
            ("GET", "/target", None),
            ("POST", "", {"data": {}}),
            ("PATCH", "/target", {"name": "Hogar"}),
            ("DELETE", "/target", None),
        ):
            with self.subTest(method=method):
                response = self.client.open(self.prefix + path, method=method,
                                            **({"json": body} if body is not None else {}))
                self.assert_rejected(response)

    def test_HOMES_T7_reject_invalid_bodies(self):
        """
        Rechazar envoltorios de creación inválidos, home_id vacío/no textual y bodies de actualización que no sean objetos.
        """
        for body in ([], 123, "invalid", {}, {"data": []}, {"data": None},
                     {"data": {}, "home_id": ""}, {"data": {}, "home_id": 123},
                     {"data": {}, "home_id": False}, {"data": {}, "extra": 1}):
            with self.subTest(create_body=body):
                self.assert_rejected(self.client.post(self.prefix, headers=self.headers, json=body))
        for body in ([], 123, "invalid", False):
            with self.subTest(update_body=body):
                self.assert_rejected(self.client.patch(f"{self.prefix}/target", headers=self.headers, json=body))
        for method, path in (("POST", ""), ("PATCH", "/target")):
            for raw_body in (None, "null", "{"):
                with self.subTest(method=method, raw_body=raw_body):
                    response = self.client.open(self.prefix + path, method=method,
                                                headers=self.headers, data=raw_body,
                                                content_type="application/json")
                    self.assert_rejected(response)

    def test_HOMES_T8_create_and_update_home_with_empty_data(self):
        """
        Crear con `data: {}` y actualizar con `{}`: aceptar y delegar los mapas vacíos.
        """
        for target in ("target", None):
            with self.subTest(operation="create", home_id=target):
                body = {"data": {}}
                if target is not None:
                    body["home_id"] = target
                response = self.client.post(self.prefix, headers=self.headers, json=body)
                self.assert_success(response)
                self.assertEqual(response.json["resp"], target or "home_id_001")
                self.assert_last_call("process_create_home", {}, target)
        with self.subTest(operation="update"):
            response = self.client.patch(f"{self.prefix}/target", headers=self.headers, json={})
            self.assert_success(response)
            self.assertNotIn("resp", response.json)
            self.assert_last_call("process_update_home", "target", {})
