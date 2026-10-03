"""Usuarios: USERS_T1 a USERS_T6 del template original."""
from unittest.mock import patch
from backend.app.processes.process_users import UsersProcesses
from backend.http_api_rest.http_endpoints_users import UsersEndpoints
from base_api_test import BaseApiTest


class UsersTests(BaseApiTest):
    endpoints_class = UsersEndpoints
    process_class = UsersProcesses
    prefix = "/grandsafelife/api/v1/users"

    def test_USERS_T1_get_user_by_id(self):
        """Obtener por ID; un documento inexistente retorna null."""
        response = self.client.get(f"{self.prefix}/target", headers=self.headers)
        self.assert_success(response)
        user = response.json["resp"]
        self.assertEqual(user["id"], "target")
        self.assertIsInstance(user["email"], str)
        for field in ("created_at", "updated_at"):
            self.assertIsInstance(user[field], int)
        self.assert_last_call("process_get_user_by_id", "target")
        # Simula documento inexistente: el process actual solo devuelve mocks.
        with patch.object(self.processor.process, "process_get_user_by_id", return_value=None):
            response = self.client.get(f"{self.prefix}/missing", headers=self.headers)
        self.assert_success(response)
        self.assertIsNone(response.json["resp"])

    def test_USERS_T2_get_user_by_email(self):
        """Obtener por email conservando el parámetro enviado."""
        email = "monitor+test@example.com"
        response = self.client.get(f"{self.prefix}/by-email", headers=self.headers,
                                   query_string={"email": email})
        self.assert_success(response)
        self.assertEqual(response.json["resp"]["email"], email)
        self.assertIsInstance(response.json["resp"]["id"], str)
        self.assert_last_call("process_get_user_by_email", email)

    def test_USERS_T3_create_user_with_explicit_and_missing_id(self):
        """Crear con ID explícito o generado, conservando los campos."""
        data = {"name": "María", "avatar": None, "homes": {}, "extra": [True, None]}
        for target in ("target", None):
            with self.subTest(user_id=target):
                body = {"data": data}
                if target is not None:
                    body["user_id"] = target
                response = self.client.post(self.prefix, headers=self.headers, json=body)
                self.assert_success(response)
                self.assertEqual(response.json["resp"], {"user_id": target or "firebase_uid_mock"})
                self.assert_last_call("process_create_user", data, target)

    def test_USERS_T4_update_user_preserving_fields(self):
        """Actualizar el destino conservando nulos y rutas con puntos."""
        data = {"avatar": None, "homes.h1.role": "observer", "extra": [1, None], "created_at": 123}
        response = self.client.patch(f"{self.prefix}/target", headers=self.headers, json=data)
        self.assert_success(response)
        self.assertNotIn("resp", response.json)
        self.assert_last_call("process_update_user", "target", data)

    def test_USERS_T5_reject_requests_without_authorization(self):
        """Los cuatro endpoints requieren Authorization antes del process."""
        for method, path, body in (
            ("GET", "/target", None),
            ("GET", "/by-email?email=test@example.com", None),
            ("POST", "", {"data": {}}),
            ("PATCH", "/target", {"name": "María"}),
        ):
            with self.subTest(method=method, path=path):
                response = self.client.open(self.prefix + path, method=method,
                                            **({"json": body} if body is not None else {}))
                self.assert_rejected(response)

    def test_USERS_T6_reject_invalid_bodies_and_parameters(self):
        """Un request inválido no ejecuta la acción."""
        for body in ({}, {"data": []}, {"data": {}, "user_id": ""},
                     {"data": {}, "user_id": 123}, {"data": {}, "extra": 1}):
            with self.subTest(create_body=body):
                self.assert_rejected(self.client.post(self.prefix, headers=self.headers, json=body))
        for body in ([], 123, "invalid"):
            with self.subTest(update_body=body):
                self.assert_rejected(self.client.patch(f"{self.prefix}/target", headers=self.headers, json=body))
        for query in ({}, {"email": ""}):
            with self.subTest(query=query):
                self.assert_rejected(self.client.get(f"{self.prefix}/by-email", headers=self.headers,
                                                    query_string=query))
