"""Alarmas: ALARMS_T1 a ALARMS_T7 del detalle de tests de API REST."""
from unittest.mock import patch
from backend.app.processes.process_alarms import AlarmsProcesses
from backend.http_api_rest.http_endpoints_alarms import AlarmsEndpoints
from base_api_test import BaseApiTest

class AlarmsTests(BaseApiTest):
    test_all_routes_reject_invalid_token_before_process = (
        BaseApiTest.assert_all_routes_reject_invalid_token_before_process
    )
    endpoints_class = AlarmsEndpoints
    process_class = AlarmsProcesses
    prefix = "/grandsafelife/api/v1/devices/target/alarms"

    def test_ALARMS_T1_get_alarms(self):
        """
        `GET /devices/{device_id}/alarms`: devolver mapa indexado por ID con nombre, horario, días, actividad, state y fechas enteras en milisegundos.
        """
        response = self.client.get(self.prefix, headers=self.headers)
        self.assert_success(response)
        alarms = response.json["resp"]
        self.assertIsInstance(alarms, dict)
        self.assertTrue(alarms)
        for alarm_id, alarm in alarms.items():
            with self.subTest(alarm_id=alarm_id):
                self.assertIsInstance(alarm_id, str)
                self.assertTrue(alarm_id)
                self.assertIsInstance(alarm, dict)
                self.assertIsInstance(alarm["name"], str)
                self.assertTrue(alarm["name"])
                self.assertIs(type(alarm["time_in_minutes"]), int)
                self.assertGreaterEqual(alarm["time_in_minutes"], 0)
                self.assertLessEqual(alarm["time_in_minutes"], 1439)
                self.assertIs(type(alarm["days"]), int)
                self.assertIs(type(alarm["is_active"]), bool)
                self.assertIsInstance(alarm["state"], str)
                for field in ("created_at", "updated_at"):
                    self.assertIs(type(alarm[field]), int)
                    self.assertGreater(alarm[field], 1_000_000_000_000)
        self.assert_last_call("process_get_alarms_by_device_id", "target")

    def test_ALARMS_T2_replace_alarms_preserving_fields(self):
        """
        `PUT /devices/{device_id}/alarms`: delegar el mapa completo con varias alarmas, conservando state y fechas enviados; responder éxito sin `resp`.
        """
        alarms = {
            "alarm-1": {"name": "Primera", "time_in_minutes": 480, "days": 127,
                        "is_active": True, "state": "taken",
                        "created_at": 1786789934000, "updated_at": 1788286907000},
            "alarm-2": {"name": "Segunda", "time_in_minutes": 1200, "days": 31,
                        "is_active": False, "state": "pending",
                        "created_at": 1785247863000, "updated_at": 1788285492000},
        }
        response = self.client.put(self.prefix, headers=self.headers, json=alarms)
        self.assert_success(response)
        self.assertNotIn("resp", response.json)
        self.assert_last_call("process_set_alarms_by_device_id", "target", alarms)

    def test_ALARMS_T3_replace_with_empty_map(self):
        """
        `PUT` con `{}`: aceptar el reemplazo vacío y delegarlo tal cual.
        """
        response = self.client.put(self.prefix, headers=self.headers, json={})
        self.assert_success(response)
        self.assertNotIn("resp", response.json)
        self.assert_last_call("process_set_alarms_by_device_id", "target", {})

    def test_ALARMS_T4_get_empty_alarms(self):
        """
        `GET`: simular documento sin alarmas y devolver `{}`.
        """
        with patch.object(self.processor.process, "process_get_alarms_by_device_id", return_value={}):
            response = self.client.get(self.prefix, headers=self.headers)
        self.assert_success(response)
        self.assertEqual(response.json["resp"], {})
        self.assert_last_call("process_get_alarms_by_device_id", "target")

    def test_ALARMS_T5_accept_boundaries_and_preserve_optional_fields(self):
        """
        `PUT`: aceptar horarios límite 0 y 1439, is_active falso y campos opcionales omitidos; no agregar state ni fechas al mapa enviado al process. Conservar fechas nulas cuando se envían explícitamente.
        """
        for time_in_minutes in (0, 1439):
            for optional_fields in ({}, {"created_at": None, "updated_at": None}):
                with self.subTest(time_in_minutes=time_in_minutes, optional_fields=optional_fields):
                    alarms = {"alarm-1": {"name": "Recordatorio", "time_in_minutes": time_in_minutes,
                                          "days": 0, "is_active": False, **optional_fields}}
                    response = self.client.put(self.prefix, headers=self.headers, json=alarms)
                    self.assert_success(response)
                    self.assertNotIn("resp", response.json)
                    self.assert_last_call("process_set_alarms_by_device_id", "target", alarms)

    def test_ALARMS_T6_reject_requests_without_authorization(self):
        """
        Ambos endpoints: rechazar requests sin Authorization.
        """
        for method in ("GET", "PUT"):
            with self.subTest(method=method):
                response = self.client.open(self.prefix, method=method,
                                            **({"json": {}} if method == "PUT" else {}))
                self.assert_rejected(response)

    def test_ALARMS_T7_reject_invalid_bodies(self):
        """
        `PUT`: rechazar body que no sea objeto, alarma que no sea objeto, campos obligatorios ausentes, nombre vacío, horario -1/1440 y campos desconocidos; no llamar al process.
        """
        for body in ([], 123, "invalid", False):
            with self.subTest(body=body):
                self.assert_rejected(self.client.put(self.prefix, headers=self.headers, json=body))
        for alarm in (None, [], 123, "invalid", False, {}):
            with self.subTest(alarm=alarm):
                self.assert_rejected(self.client.put(self.prefix, headers=self.headers,
                                                    json={"alarm-1": alarm}))
        valid_alarm = {"name": "Recordatorio", "time_in_minutes": 480, "days": 127, "is_active": True}
        for field in valid_alarm:
            with self.subTest(missing_field=field):
                alarm = {key: value for key, value in valid_alarm.items() if key != field}
                self.assert_rejected(self.client.put(self.prefix, headers=self.headers,
                                                    json={"alarm-1": alarm}))
        for changes in ({"name": ""}, {"time_in_minutes": -1},
                        {"time_in_minutes": 1440}, {"unknown": 1}):
            with self.subTest(changes=changes):
                self.assert_rejected(self.client.put(self.prefix, headers=self.headers,
                                                    json={"alarm-1": {**valid_alarm, **changes}}))
        for raw_body in (None, "null", "{"):
            with self.subTest(raw_body=raw_body):
                response = self.client.put(self.prefix, headers=self.headers, data=raw_body,
                                           content_type="application/json")
                self.assert_rejected(response)
