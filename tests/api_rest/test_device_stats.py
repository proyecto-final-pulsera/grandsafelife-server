"""Dispositivos: DEVICES_STATS_T1 a DEVICES_STATS_T7 del detalle de tests de API REST."""
from unittest.mock import patch
from datetime import datetime, timedelta
from backend.app.processes.process_devices_stats import DevicesStatsProcesses
from backend.http_api_rest.http_endpoints_devices_stats import DevicesStatsEndpoints
from base_api_test import BaseApiTest

class DevicesStatsTests(BaseApiTest):
    test_all_routes_reject_invalid_token_before_process = (
        BaseApiTest.assert_all_routes_reject_invalid_token_before_process
    )
    endpoints_class = DevicesStatsEndpoints
    process_class = DevicesStatsProcesses
    prefix = "/grandsafelife/api/v1/devices/target/stats"

    def assert_daily_metrics(self, metrics, expected_date):
        self.assertEqual(metrics["id"], expected_date)
        for field in ("steps", "falls", "stumbles", "night_rises", "panic_button"):
            self.assertIs(type(metrics[field]), int)
        self.assertIn(type(metrics["time_lying_down"]), (int, float))
        self.assertIsInstance(metrics["updated_at"], str)
        updated_at = datetime.fromisoformat(metrics["updated_at"].replace("Z", "+00:00"))
        self.assertEqual(updated_at.date().isoformat(), expected_date)

    def assert_monthly_aggregates(self, aggregates, expected_month):
        self.assertEqual(aggregates["id"], expected_month)
        for field in ("avg_steps", "avg_time_lying_down"):
            self.assertIn(type(aggregates[field]), (int, float))
        for field in ("total_falls", "total_stumbles", "total_night_rises",
                      "total_panic_button", "sedentarism_level", "risk_level", "active_days"):
            self.assertIs(type(aggregates[field]), int)

    def test_DEVICES_STATS_T1_get_daily_metrics(self):
        """
        `GET /devices/{device_id}/stats/daily?date=YYYY-MM-DD`:
        delegar dispositivo y fecha; devolver id igual a la fecha, contadores enteros, tiempo numérico y updated_at ISO 8601 válido.
        """
        date = "2026-09-15"
        response = self.client.get(f"{self.prefix}/daily", headers=self.headers,
                                   query_string={"date": date})
        self.assert_success(response)
        self.assert_daily_metrics(response.json["resp"], date)
        self.assert_last_call("process_get_daily_metrics", "target", date)

    def test_DEVICES_STATS_T2_get_monthly_aggregates(self):
        """
        `GET /devices/{device_id}/stats/monthly?month=YYYY-MM`:
        devolver id igual al mes y los campos que consume MonthlyAggregatesData: promedios numéricos y totales/niveles/días enteros.
        """
        month = "2026-09"
        response = self.client.get(f"{self.prefix}/monthly", headers=self.headers,
                                   query_string={"month": month})
        self.assert_success(response)
        self.assert_monthly_aggregates(response.json["resp"], month)
        self.assert_last_call("process_get_monthly_aggregates", "target", month)

    def test_DEVICES_STATS_T3_get_previous_month(self):
        """
        `GET /devices/{device_id}/stats/monthly/previous`:
        fijar la fecha del servidor para comprobar el mes anterior, incluyendo enero que retrocede a diciembre del año anterior; comprobar los campos mensuales.
        """
        for now, expected_month in (
            (datetime(2026, 10, 3, 12), "2026-09"),
            (datetime(2026, 1, 15, 12), "2025-12"),
            (datetime(2024, 3, 1, 12), "2024-02"),
        ):
            with self.subTest(now=now):
                with patch("backend.app.processes.process_devices_stats.datetime") as clock:
                    clock.now.return_value = now
                    with patch.object(self.processor.process, "process_get_monthly_aggregates",
                                      wraps=self.processor.process.process_get_monthly_aggregates) as monthly:
                        response = self.client.get(f"{self.prefix}/monthly/previous", headers=self.headers)
                        monthly.assert_called_once_with("target", expected_month)
                self.assert_success(response)
                self.assert_monthly_aggregates(response.json["resp"], expected_month)
                self.assert_last_call("process_get_previous_month_aggregates", "target")

    def test_DEVICES_STATS_T4_get_last_week(self):
        """
        `GET /devices/{device_id}/stats/daily/last-week`:
        fijar la fecha para comprobar siete mocks desde hace seis días hasta hoy, sin duplicados, ordenados por fecha y con campos diarios válidos. Incluir cambio de mes/año.
        """
        for now in (datetime(2026, 10, 3, 12), datetime(2026, 1, 3, 12), datetime(2024, 3, 2, 12)):
            with self.subTest(now=now):
                dates = [(now.date() - timedelta(days=days)).isoformat() for days in range(6, -1, -1)]
                with patch("backend.app.processes.process_devices_stats.datetime") as clock:
                    clock.now.return_value = now
                    with patch.object(self.processor.process, "process_get_daily_metrics",
                                      wraps=self.processor.process.process_get_daily_metrics) as daily:
                        response = self.client.get(f"{self.prefix}/daily/last-week", headers=self.headers)
                        self.assertEqual(daily.call_count, 7)
                        self.assertEqual([call.args for call in daily.call_args_list],
                                         [("target", date) for date in dates])
                self.assert_success(response)
                metrics = response.json["resp"]
                self.assertIsInstance(metrics, list)
                self.assertEqual([day["id"] for day in metrics], dates)
                self.assertEqual(len({day["id"] for day in metrics}), 7)
                for day, date in zip(metrics, dates):
                    self.assert_daily_metrics(day, date)
                self.assert_last_call("process_get_last_week_metrics", "target")

    def test_DEVICES_STATS_T5_preserve_missing_and_partial_results(self):
        """
        Simular métricas diarias y mensuales inexistentes (`{}`), semana sin datos (`[]`) y semana con solo algunos días: preservar esas respuestas sin completar días artificialmente.
        """
        partial_week = [self.processor.process.process_get_daily_metrics("target", date)
                        for date in ("2025-12-30", "2026-01-02")]
        for path, query, method, args, result in (
            ("/daily", {"date": "2026-01-03"}, "process_get_daily_metrics", ("target", "2026-01-03"), {}),
            ("/monthly", {"month": "2026-01"}, "process_get_monthly_aggregates", ("target", "2026-01"), {}),
            ("/monthly/previous", {}, "process_get_previous_month_aggregates", ("target",), {}),
            ("/daily/last-week", {}, "process_get_last_week_metrics", ("target",), []),
            ("/daily/last-week", {}, "process_get_last_week_metrics", ("target",), partial_week),
        ):
            with self.subTest(path=path, result=result):
                with patch.object(self.processor.process, method, return_value=result):
                    response = self.client.get(self.prefix + path, headers=self.headers, query_string=query)
                self.assert_success(response)
                self.assertIn("resp", response.json)
                self.assertEqual(response.json["resp"], result)
                self.assert_last_call(method, *args)

    def test_DEVICES_STATS_T6_reject_requests_without_authorization(self):
        """
        Los cuatro endpoints: rechazar requests sin Authorization.
        """
        for path, query in (
            ("/daily", {"date": "2026-09-15"}),
            ("/monthly", {"month": "2026-09"}),
            ("/monthly/previous", {}),
            ("/daily/last-week", {}),
        ):
            with self.subTest(path=path):
                self.assert_rejected(self.client.get(self.prefix + path, query_string=query))

    def test_DEVICES_STATS_T7_reject_invalid_queries(self):
        """
        Rechazar date/month ausentes, vacíos o con formato incorrecto y meses fuera de 01–12; no ejecutar el process.
        """
        for path, parameter, invalid_values in (
            ("/daily", "date", (None, "", "invalid", "2026-9-01", "2026-09-1",
                                 "2026/09/01", "2026-00-01", "2026-13-01", "2026-09-32",
                                 "2026-09-01T00:00:00Z")),
            ("/monthly", "month", (None, "", "invalid", "2026-9", "2026/09",
                                    "2026-00", "2026-13", "2026-09-01")),
        ):
            for value in invalid_values:
                with self.subTest(path=path, value=value):
                    query = {} if value is None else {parameter: value}
                    response = self.client.get(self.prefix + path, headers=self.headers, query_string=query)
                    self.assert_rejected(response)
