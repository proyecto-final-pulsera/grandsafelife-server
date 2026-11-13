"""Reglas de validación y endpoints HTTP de métricas de dispositivos."""

from flask import Blueprint
from firebase_admin import auth
from pydantic import BaseModel, Field

from ..authentication.authentication import Authentication
from .api_op_codes import API_OP_OK, API_OP_UNAUTHORIZED, build_api_response
from .http_validation import validate_request
from .http_endpoints_devices import WristbandInput, authorize_wristband


#==========================
#Reglas de validación
#==========================

class DailyDateQuery(BaseModel):
    """Fecha obligatoria para consultar las métricas diarias."""

    date: str = Field(pattern=r"^\d{4}-(0[1-9]|1[0-2])-([0-2]\d|3[01])$")


class MonthlyDateQuery(BaseModel):
    """Mes obligatorio para consultar los agregados mensuales."""

    month: str = Field(pattern=r"^\d{4}-(0[1-9]|1[0-2])$")


class WristbandStepsInput(WristbandInput):
    steps: int = Field(strict=True, ge=0)


#==========================
#Endpoints
#==========================

class DevicesStatsEndpoints:
    """Agrupa las rutas de métricas e inyecta su procesador HTTP."""

    def __init__(self, repository, devices_repository, homes_repository):
        self.repository = repository
        self.devices = devices_repository
        self.homes = homes_repository
        self.last_wristband_steps = None
        self.authentication = Authentication()
        self.blueprint = Blueprint("devices_stats", __name__, url_prefix="/grandsafelife/api/v1")
        self._register_routes()

    def _register_routes(self):
        """Registra las consultas HTTP de métricas de dispositivos."""

        @self.blueprint.post("/wristband-add-daily-steps")
        def wristband_add_daily_steps():
            authorization, body, _ = validate_request(body_model=WristbandStepsInput)
            error = authorize_wristband(
                self.authentication, authorization, body.device_id, self.devices, self.homes,
            )
            if error is not None:
                return error
            data = body.model_dump()
            self.last_wristband_steps = data
            print(f"[WRISTBAND steps] {data}", flush=True)
            return build_api_response(API_OP_OK)

        @self.blueprint.get("/devices/<device_id>/stats/daily")
        def get_daily_metrics(device_id):
            # Validación de formato.
            authorization, _, query = validate_request(query_model=DailyDateQuery)

            # Autenticación antes de ejecutar el process.
            try:
                current_uid, app_type = self.authentication.get_current_user_uid(authorization)
            except (ValueError, auth.InvalidIdTokenError, auth.RevokedIdTokenError, auth.UserDisabledError):
                return build_api_response(API_OP_UNAUTHORIZED), 401

            print(f"[AUTH SERVER] uid={current_uid}", flush=True)


            # Procesamiento del request con los datos listos para ejecutar la acción.
            metrics = self.repository.get_daily_metrics(device_id, query.date)
            return build_api_response(API_OP_OK, metrics)

        @self.blueprint.get("/devices/<device_id>/stats/monthly")
        def get_monthly_aggregates(device_id):
            # Validación de formato.
            authorization, _, query = validate_request(query_model=MonthlyDateQuery)

            # Autenticación antes de ejecutar el process.
            try:
                current_uid, app_type = self.authentication.get_current_user_uid(authorization)
            except (ValueError, auth.InvalidIdTokenError, auth.RevokedIdTokenError, auth.UserDisabledError):
                return build_api_response(API_OP_UNAUTHORIZED), 401

            print(f"[AUTH SERVER] uid={current_uid}", flush=True)


            # Procesamiento del request con los datos listos para ejecutar la acción.
            aggregates = self.repository.get_monthly_aggregates(device_id, query.month)
            return build_api_response(API_OP_OK, aggregates)

        @self.blueprint.get("/devices/<device_id>/stats/monthly/previous")
        def get_previous_month_aggregates(device_id):
            # Validación de formato.
            authorization, _, _ = validate_request()

            # Autenticación antes de ejecutar el process.
            try:
                current_uid, app_type = self.authentication.get_current_user_uid(authorization)
            except (ValueError, auth.InvalidIdTokenError, auth.RevokedIdTokenError, auth.UserDisabledError):
                return build_api_response(API_OP_UNAUTHORIZED), 401

            print(f"[AUTH SERVER] uid={current_uid}", flush=True)

            # Procesamiento del request con los datos listos para ejecutar la acción.
            aggregates = self.repository.get_previous_month_aggregates(device_id)
            return build_api_response(API_OP_OK, aggregates)

        @self.blueprint.get("/devices/<device_id>/stats/daily/last-week")
        def get_last_week_metrics(device_id):
            # Validación de formato.
            authorization, _, _ = validate_request()

            # Autenticación antes de ejecutar el process.
            try:
                current_uid, app_type = self.authentication.get_current_user_uid(authorization)
            except (ValueError, auth.InvalidIdTokenError, auth.RevokedIdTokenError, auth.UserDisabledError):
                return build_api_response(API_OP_UNAUTHORIZED), 401

            print(f"[AUTH SERVER] uid={current_uid}", flush=True)

            # Procesamiento del request con los datos listos para ejecutar la acción.
            metrics = self.repository.get_last_week_metrics(device_id)
            return build_api_response(API_OP_OK, metrics)
