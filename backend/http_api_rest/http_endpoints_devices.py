"""Reglas de validación y endpoints HTTP de dispositivos."""

from flask import Blueprint
from pydantic import BaseModel, ConfigDict, Field, JsonValue, RootModel

from .api_op_codes import API_OP_OK, build_api_response
from .http_validation import validate_request


#==========================
#Reglas de validación
#==========================


class DeviceUpdateInput(RootModel[dict[str, JsonValue]]):
    """Mapa parcial de campos; conserva nombres, valores nulos y mapas anidados."""


class DeviceCreateInput(BaseModel):
    """Separa el ID del documento de los campos que se guardarán en él."""

    model_config = ConfigDict(extra="forbid")
    device_id: str | None = Field(default=None, min_length=1)
    data: dict[str, JsonValue]


#==========================
#Endpoints
#==========================

class DevicesEndpoints:
    """Agrupa las rutas de dispositivos e inyecta su procesador HTTP."""

    def __init__(self, http_processor):
        self.http_processor = http_processor
        self.blueprint = Blueprint("devices", __name__, url_prefix="/grandsafelife/api/v1",)
        self._register_routes()

    def _register_routes(self):
        """Registra las operaciones HTTP disponibles para dispositivos."""

        @self.blueprint.post("/devices")
        def create_device():
            authorization, body, _ = validate_request(body_model=DeviceCreateInput)

            # TODO: Resolver aquí la autenticación y los permisos antes del process.
            # current_uid, app_type = self.authentication.get_current_user_uid(authorization)
            # Validar el tipo de app y los permisos de current_uid sobre los datos
            # solicitados. Authentication aún no está implementada.
            device_id = self.http_processor.process_create_device(body.data,body.device_id,)
            return build_api_response(API_OP_OK, device_id)

        @self.blueprint.get("/devices/<device_id>")
        def get_device_by_id(device_id):
            authorization, _, _ = validate_request()

            # TODO: Resolver aquí la autenticación y los permisos antes del process.
            # current_uid, app_type = self.authentication.get_current_user_uid(authorization)
            # Validar el tipo de app y los permisos de current_uid sobre los datos
            # solicitados. Authentication aún no está implementada.
            device = self.http_processor.process_get_device_by_id(device_id,)
            return build_api_response(API_OP_OK, device)

        @self.blueprint.patch("/devices/<device_id>")
        def update_device(device_id):
            authorization, body, _ = validate_request(body_model=DeviceUpdateInput)

            # TODO: Resolver aquí la autenticación y los permisos antes del process.
            # current_uid, app_type = self.authentication.get_current_user_uid(authorization)
            # Validar el tipo de app y los permisos de current_uid sobre los datos
            # solicitados. Authentication aún no está implementada.
            self.http_processor.process_update_device(device_id, body.model_dump(exclude_unset=True),)
            return build_api_response(API_OP_OK)

        @self.blueprint.delete("/devices/<device_id>")
        def delete_device(device_id):
            authorization, _, _ = validate_request()

            # TODO: Resolver aquí la autenticación y los permisos antes del process.
            # current_uid, app_type = self.authentication.get_current_user_uid(authorization)
            # Validar el tipo de app y los permisos de current_uid sobre los datos
            # solicitados. Authentication aún no está implementada.
            self.http_processor.process_delete_device(device_id)
            return build_api_response(API_OP_OK)

        @self.blueprint.get("/users/<owner_id>/devices")
        def get_devices_by_owner(owner_id):
            authorization, _, _ = validate_request()

            # TODO: Resolver aquí la autenticación y los permisos antes del process.
            # current_uid, app_type = self.authentication.get_current_user_uid(authorization)
            # Validar el tipo de app y los permisos de current_uid sobre los datos
            # solicitados. Authentication aún no está implementada.
            devices = self.http_processor.process_get_devices_by_owner(owner_id,)
            return build_api_response(API_OP_OK, devices)

        @self.blueprint.get("/homes/<home_id>/devices")
        def get_devices_by_home(home_id):
            authorization, _, _ = validate_request()

            # TODO: Resolver aquí la autenticación y los permisos antes del process.
            # current_uid, app_type = self.authentication.get_current_user_uid(authorization)
            # Validar el tipo de app y los permisos de current_uid sobre los datos
            # solicitados. Authentication aún no está implementada.
            devices = self.http_processor.process_get_devices_by_home(home_id,)
            return build_api_response(API_OP_OK, devices)

        @self.blueprint.get("/devices/<device_id>/location")
        def get_device_location(device_id):
            authorization, _, _ = validate_request()

            # TODO: Resolver aquí la autenticación y los permisos antes del process.
            # current_uid, app_type = self.authentication.get_current_user_uid(authorization)
            # Validar el tipo de app y los permisos de current_uid sobre los datos
            # solicitados. Authentication aún no está implementada.
            location = self.http_processor.process_get_device_location(device_id,)
            return build_api_response(API_OP_OK, location)
