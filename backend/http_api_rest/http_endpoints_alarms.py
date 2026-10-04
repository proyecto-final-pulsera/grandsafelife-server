"""Reglas de validación y endpoints HTTP de alarmas de dispositivos."""

from flask import Blueprint
from firebase_admin import auth
from pydantic import BaseModel, ConfigDict, Field, RootModel

from ..authentication.authentication import Authentication
from .api_op_codes import API_OP_OK, API_OP_UNAUTHORIZED, build_api_response
from .http_validation import validate_request


#==========================
#Reglas de validación
#==========================

class AlarmInput(BaseModel):
    """Campos de una alarma enviados por la aplicación; fechas en milisegundos Unix."""

    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=1)
    time_in_minutes: int = Field(ge=0, le=1439)
    days: int
    is_active: bool
    state: str = "none"
    created_at: int | None = None
    updated_at: int | None = None


class AlarmMapInput(RootModel[dict[str, AlarmInput]]):
    """Representación completa de alarmas indexadas por su ID."""


#==========================
#Endpoints
#==========================

class AlarmsEndpoints:
    """Agrupa las rutas de alarmas e inyecta su procesador HTTP."""

    def __init__(self, http_processor):
        self.http_processor = http_processor
        self.authentication = Authentication()
        self.blueprint = Blueprint("alarms", __name__, url_prefix="/grandsafelife/api/v1/devices/<device_id>/alarms",)
        self._register_routes()

    def _register_routes(self):
        """Registra las operaciones HTTP disponibles para alarmas."""

        @self.blueprint.get("")
        def get_alarms_by_device_id(device_id):
            # Validación de formato.
            authorization, _, _ = validate_request()

            # Autenticación antes de ejecutar el process.
            try:
                current_uid, app_type = self.authentication.get_current_user_uid(authorization)
            except (ValueError, auth.InvalidIdTokenError, auth.RevokedIdTokenError, auth.UserDisabledError):
                return build_api_response(API_OP_UNAUTHORIZED), 401

            print(f"[AUTH SERVER] uid={current_uid}", flush=True)

            # TODO: Validar los permisos de current_uid sobre los datos solicitados.
            # app_type es por ahora la constante mockeada MONITOR_APP.

            # Procesamiento del request con los datos listos para ejecutar la acción.
            alarms = self.http_processor.process_get_alarms_by_device_id(device_id)
            return build_api_response(API_OP_OK, alarms)

        @self.blueprint.put("")
        def set_alarms_by_device_id(device_id):
            # Validación de formato.
            authorization, body, _ = validate_request(body_model=AlarmMapInput)

            # Autenticación antes de ejecutar el process.
            try:
                current_uid, app_type = self.authentication.get_current_user_uid(authorization)
            except (ValueError, auth.InvalidIdTokenError, auth.RevokedIdTokenError, auth.UserDisabledError):
                return build_api_response(API_OP_UNAUTHORIZED), 401

            print(f"[AUTH SERVER] uid={current_uid}", flush=True)

            # TODO: Validar los permisos de current_uid sobre los datos solicitados.
            # app_type es por ahora la constante mockeada MONITOR_APP.

            # Procesamiento del reemplazo completo, incluido un mapa vacío.
            self.http_processor.process_set_alarms_by_device_id(
                device_id, body.model_dump(exclude_unset=True),
            )
            return build_api_response(API_OP_OK)
