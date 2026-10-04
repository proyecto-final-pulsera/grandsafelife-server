from base_api_test import BaseApiTest


class DevicesTests(BaseApiTest):
    def test_crud(self):
        """Crear, consultar, actualizar y eliminar dispositivos; verificar persistencia."""
        self.crud('devices', 'coords')

    def test_queries_and_location(self):
        """Consultar dispositivos por propietario y hogar, incluidos hubs, y su ubicación."""
        for suffix, kind in [('band', 'pulsera'), ('hub', 'hub')]:
            target = self.key + '-' + suffix
            self.ref('devices/' + target).set({'owner_id': self.key, 'home_id': self.key, 'type': kind,
                                             'coords': {'lat': -34.6, 'long': -58.4}})
        self.ref('devices/' + self.key + '-other').set({'owner_id': 'other', 'home_id': 'other'})
        for path in (f'/users/{self.key}/devices', f'/homes/{self.key}/devices'):
            devices = self.success('GET', path)
            self.assertEqual(set(devices), {self.key + '-band', self.key + '-hub'})
            self.assertEqual(devices[self.key + '-hub']['type'], 'hub')
            self.assertEqual(self.success('GET', path.replace(self.key, self.key + '-missing')), {})
        self.assertEqual(self.success('GET', f'/devices/{self.key}-band/location'), {'lat': -34.6, 'long': -58.4})
        self.assertIsNone(self.success('GET', f'/devices/{self.key}-missing/location'))

    def test_validation_and_auth(self):
        """Rechazar tokens y datos inválidos en las rutas sin modificar Firestore."""
        for method, path, body in [('POST', '/users', {'data': {}}), ('POST', '/homes', {'data': {}}),
                                   ('POST', '/devices', {'data': {}}), ('PATCH', '/devices/' + self.key, {}),
                                   ('DELETE', '/devices/' + self.key, None), ('GET', '/devices/' + self.key, None),
                                   ('GET', '/users/' + self.key + '/devices', None),
                                   ('GET', '/homes/' + self.key + '/devices', None),
                                   ('GET', '/devices/' + self.key + '/location', None),
                                   ('GET', '/users/' + self.key, None), ('GET', '/homes/' + self.key, None),
                                   ('PATCH', '/users/' + self.key, {}), ('PATCH', '/homes/' + self.key, {}),
                                   ('DELETE', '/homes/' + self.key, None),
                                   ('GET', '/users/by-email?email=test@example.com', None),
                                   ('GET', '/devices/' + self.key + '/stats/daily?date=2026-01-01', None),
                                   ('GET', '/devices/' + self.key + '/stats/monthly?month=2026-01', None),
                                   ('GET', '/devices/' + self.key + '/stats/monthly/previous', None),
                                   ('GET', '/devices/' + self.key + '/stats/daily/last-week', None),
                                   ('GET', '/devices/' + self.key + '/alarms', None),
                                   ('PUT', '/devices/' + self.key + '/alarms', {})]:
            with self.subTest(method=method, path=path):
                self.rejected(method, path, body, token=False)
                result = self.rejected(method, path, body, status=401, token='invalid')
                self.assertEqual(result['op_status'], 5)
        self.rejected('POST', '/devices', {'data': {}, 'device_id': ''})
        self.rejected('PATCH', '/devices/' + self.key, [])
