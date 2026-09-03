"""
@file http_endpoints_devices_stats.py
@author Grand Safe Life
@brief Endpoints HTTP relacionados con métricas de dispositivos.

Este módulo contendrá las rutas de consulta de métricas diarias y agregados
mensuales.
"""

from typing import Annotated

from fastapi import APIRouter, Header, Query

from .api_op_codes import API_OP_OK, build_api_response


AuthorizationHeader = Annotated[str, Header(alias="Authorization")]
DailyDateQuery = Annotated[
    str,
    Query(pattern=r"^\d{4}-(0[1-9]|1[0-2])-([0-2]\d|3[01])$"),
]
MonthlyDateQuery = Annotated[
    str,
    Query(pattern=r"^\d{4}-(0[1-9]|1[0-2])$"),
]


class DevicesStatsEndpoints:
    """Agrupa las rutas de métricas e inyecta su procesador HTTP."""

    def __init__(self, http_processor):
        self.http_processor = http_processor
        self.router = APIRouter(
            prefix="/grandsafelife/api/v1/devices/{device_id}/stats",
            tags=["device-stats"],
        )
        self._register_routes()

    def _register_routes(self):
        """Registra las consultas HTTP de métricas de dispositivos."""

        @self.router.get("/daily")
        def get_daily_metrics(
            device_id: str,
            date: DailyDateQuery,
            authorization: AuthorizationHeader,
        ):
            metrics = self.http_processor.process_get_daily_metrics(
                authorization,
                device_id,
                date,
            )
            return build_api_response(API_OP_OK, metrics)

        @self.router.get("/monthly")
        def get_monthly_aggregates(
            device_id: str,
            month: MonthlyDateQuery,
            authorization: AuthorizationHeader,
        ):
            aggregates = self.http_processor.process_get_monthly_aggregates(
                authorization,
                device_id,
                month,
            )
            return build_api_response(API_OP_OK, aggregates)

        @self.router.get("/monthly/previous")
        def get_previous_month_aggregates(
            device_id: str,
            authorization: AuthorizationHeader,
        ):
            aggregates = (
                self.http_processor.process_get_previous_month_aggregates(
                    authorization,
                    device_id,
                )
            )
            return build_api_response(API_OP_OK, aggregates)

        @self.router.get("/daily/last-week")
        def get_last_week_metrics(
            device_id: str,
            authorization: AuthorizationHeader,
        ):
            metrics = self.http_processor.process_get_last_week_metrics(
                authorization,
                device_id,
            )
            return build_api_response(API_OP_OK, metrics)
