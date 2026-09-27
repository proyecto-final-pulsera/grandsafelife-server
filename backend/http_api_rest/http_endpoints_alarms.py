"""Reglas de validación y endpoints HTTP de alarmas de dispositivos."""

from flask import Blueprint
from pydantic import BaseModel, ConfigDict, Field, RootModel

from .api_op_codes import API_OP_OK, build_api_response
from .http_validation import validate_request


#==========================
#Reglas de validación
#==========================

class AlarmInput(BaseModel):
    """Campos configurables de una alarma enviados por la aplicación."""

    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=1)
    time_in_minutes: int = Field(ge=0, le=1439)
    days: int
    is_active: bool


class AlarmMapInput(RootModel[dict[str, AlarmInput]]):
    """Representación completa de alarmas indexadas por su ID."""


#==========================
#Endpoints
#==========================

class AlarmsEndpoints:
    """Agrupa las rutas de alarmas e inyecta su procesador HTTP."""

    def __init__(self, http_processor):
        self.http_processor = http_processor
        self.blueprint = Blueprint(
            "alarms", __name__,
            url_prefix="/grandsafelife/api/v1/devices/<device_id>/alarms",
        )
        self._register_routes()

    def _register_routes(self):
        """Registra las operaciones HTTP disponibles para alarmas."""

        @self.blueprint.get("")
        def get_alarms_by_device_id(device_id):
            authorization, _, _ = validate_request()
            alarms = self.http_processor.process_get_alarms_by_device_id(
                authorization, device_id,
            )
            return build_api_response(API_OP_OK, alarms)

        @self.blueprint.put("")
        def set_alarms_by_device_id(device_id):
            authorization, body, _ = validate_request(body_model=AlarmMapInput)
            self.http_processor.process_set_alarms_by_device_id(
                authorization, device_id, body.model_dump(),
            )
            return build_api_response(API_OP_OK)
