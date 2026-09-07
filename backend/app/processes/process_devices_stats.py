"""Procesamiento de devices_stats; conserva los mocks y TODO existentes."""


class DevicesStatsProcesses:
    def process_get_daily_metrics(self, authorization, device_id, date):
        # TODO: Verificar token, existencia del dispositivo y acceso al hogar
        # asociado antes de consultar las métricas diarias en el repository.
        metrics = self._get_mock_daily_metrics()
        metrics["id"] = date
        metrics["updated_at"] = f"{date}T23:59:59Z"
        return metrics

    def process_get_monthly_aggregates(self, authorization, device_id, month):
        # TODO: Verificar token y permisos, y consultar los agregados mensuales
        # calculados por el servidor mediante el repository correspondiente.
        aggregates = self._get_mock_monthly_aggregates()
        aggregates["id"] = month
        return aggregates

    def process_get_previous_month_aggregates(self, authorization, device_id):
        # TODO: Verificar token y permisos, calcular el mes calendario anterior
        # en el servidor y consultar sus agregados mediante el repository.
        aggregates = self._get_mock_monthly_aggregates()
        aggregates["id"] = "2026-08"
        return aggregates

    def process_get_last_week_metrics(self, authorization, device_id):
        # TODO: Verificar token y permisos, calcular el rango de siete días en
        # el servidor y consultar únicamente los días con datos existentes.
        first_day = self._get_mock_daily_metrics()
        first_day.update(
            {
                "id": "2026-08-31",
                "steps": 4010,
                "stumbles": 1,
                "time_lying_down": 7.8,
                "updated_at": "2026-08-31T23:59:59Z",
            }
        )
        second_day = self._get_mock_daily_metrics()
        return [first_day, second_day]

    @staticmethod
    def _get_mock_daily_metrics():
        return {
            "id": "2026-09-01",
            "steps": 4350,
            "falls": 0,
            "stumbles": 2,
            "time_lying_down": 8.5,
            "night_rises": 1,
            "panic_button": 0,
            "updated_at": "2026-09-01T23:59:59Z",
        }

    @staticmethod
    def _get_mock_monthly_aggregates():
        return {
            "id": "2026-09",
            "avg_steps": 4120.5,
            "avg_falls": 0.03,
            "avg_stumbles": 1.4,
            "avg_lying_down": 7.9,
            "avg_night_rises": 1.1,
            "total_panic_button_press": 0,
            "sedentarism_level": 45,
            "risk_level": 12,
            "active_days": 13,
        }
