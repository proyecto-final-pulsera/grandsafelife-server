from base_api_test import BaseApiTest


class HomesTests(BaseApiTest):
    def test_crud(self):
        """Crear, consultar, actualizar y eliminar hogares; conservar subcolecciones."""
        self.crud('homes', 'members')

    def test_invalid_inputs(self):
        """Rechazar datos inválidos de hogares sin modificar Firestore."""
        for body in ({}, {'data': []}, {'data': {}, 'home_id': ''}, {'data': {}, 'extra': 1}):
            with self.subTest(body=body):
                self.rejected('POST', '/homes', body)
        self.rejected('PATCH', '/homes/' + self.key, [])
