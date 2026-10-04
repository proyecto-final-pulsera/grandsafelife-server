from base_api_test import BaseApiTest


class UsersTests(BaseApiTest):
    def test_crud(self):
        """Crear, consultar, reemplazar y actualizar usuarios; verificar campos y fechas."""
        self.crud('users', 'homes')

    def test_email_and_missing(self):
        """Buscar usuarios por email y comprobar el resultado cuando no existen."""
        email = self.key + '@example.com'
        self.ref('users/' + self.key).set({'email': email, 'created_at': None})
        self.assertEqual(self.success('GET', '/users/by-email?email=' + email),
                         {'id': self.key, 'email': email, 'created_at': None})
        self.assertIsNone(self.success('GET', '/users/by-email?email=missing-' + email))

    def test_invalid_inputs(self):
        """Rechazar datos y parámetros inválidos sin modificar Firestore."""
        for body in ({}, {'data': []}, {'data': {}, 'user_id': ''}, {'data': {}, 'extra': 1}):
            with self.subTest(body=body):
                self.rejected('POST', '/users', body)
        self.rejected('PATCH', '/users/' + self.key, [])
        self.rejected('GET', '/users/by-email', None)
