from base_api_test import BaseApiTest


class AlarmsTests(BaseApiTest):
    def test_replace_clear_and_dates(self):
        """Consultar, reemplazar y vaciar alarmas; conservar estados y fechas."""
        prefix = f'/devices/{self.key}/alarms'
        ref = self.ref('alarms/' + self.key)
        self.assertEqual(self.success('GET', prefix), {})
        alarm = {'name': 'Medication', 'time_in_minutes': 480, 'days': 127, 'is_active': True,
                 'state': 'taken', 'created_at': 123, 'updated_at': None}
        self.assertIsNone(self.success('PUT', prefix, {'first': alarm, 'second': alarm}))
        stored = ref.get().to_dict()
        self.assert_timestamp(stored['first']['created_at'])
        self.assertEqual(self.success('GET', prefix), {'first': alarm, 'second': alarm})
        minimal = {key: value for key, value in alarm.items() if key not in ('state', 'created_at', 'updated_at')}
        self.success('PUT', prefix, {'third': minimal})
        self.assertEqual(ref.get().to_dict(), {'third': minimal})
        self.success('PUT', prefix, {})
        self.assertTrue(ref.get().exists)
        self.assertEqual(ref.get().to_dict(), {})
        self.assertEqual(self.success('GET', prefix), {})

    def test_validation(self):
        """Rechazar alarmas inválidas conservando los datos existentes."""
        prefix = f'/devices/{self.key}/alarms'
        ref = self.ref('alarms/' + self.key)
        ref.set({'kept': {'name': 'Original'}})
        for body in ([], {'a': {}}, {'a': {'name': 'A', 'time_in_minutes': 1440, 'days': 1, 'is_active': True}}):
            self.rejected('PUT', prefix, body)
            self.assertEqual(ref.get().to_dict(), {'kept': {'name': 'Original'}})
