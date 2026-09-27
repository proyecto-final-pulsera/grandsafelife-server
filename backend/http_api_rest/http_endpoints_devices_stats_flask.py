"""Reglas de validación y endpoints HTTP de métricas de dispositivos."""

from flask import Blueprint
from pydantic import BaseModel, Field

from .api_op_codes import API_OP_OK, build_api_response
from .http_validation import validate_request


#==========================
#Reglas de validación
#==========================

class DailyDateQuery(BaseModel):
    """Fecha obligatoria para consultar las métricas diarias."""

    date: str = Field(pattern=r"^\d{4}-(0[1-9]|1[0-2])-([0-2]\d|3[01])$")


class MonthlyDateQuery(BaseModel):
    """Mes obligatorio para consultar los agregados mensuales."""

    month: str = Field(pattern=r"^\d{4}-(0[1-9]|1[0-2])$")


#==========================
#Endpoints
#==========================

class DevicesStatsEndpoints:
    """Agrupa las rutas de métricas e inyecta su procesador HTTP."""

    def __init__(self, http_processor):
        self.http_processor = http_processor
        self.blueprint = Blueprint(
            "devices_stats", __name__,
            url_prefix="/grandsafelife/api/v1/devices/<device_id>/stats",
        )
        self._register_routes()

    def _register_routes(self):
        """Registra las consultas HTTP de métricas de dispositivos."""

        @self.blueprint.get("/daily")
        def get_daily_metrics(device_id):
            authorization, _, query = validate_request(query_model=DailyDateQuery)
            metrics = self.http_processor.process_get_daily_metrics(
                authorization, device_id, query.date,
            )
            return build_api_response(API_OP_OK, metrics)

        @self.blueprint.get("/monthly")
        def get_monthly_aggregates(device_id):
            authorization, _, query = validate_request(query_model=MonthlyDateQuery)
            aggregates = self.http_processor.process_get_monthly_aggregates(
                authorization, device_id, query.month,
            )
            return build_api_response(API_OP_OK, aggregates)

        @self.blueprint.get("/monthly/previous")
        def get_previous_month_aggregates(device_id):
            authorization, _, _ = validate_request()
            aggregates = self.http_processor.process_get_previous_month_aggregates(
                authorization, device_id,
            )
            return build_api_response(API_OP_OK, aggregates)

        @self.blueprint.get("/daily/last-week")
        def get_last_week_metrics(device_id):
            authorization, _, _ = validate_request()
            metrics = self.http_processor.process_get_last_week_metrics(
                authorization, device_id,
            )
            return build_api_response(API_OP_OK, metrics)
