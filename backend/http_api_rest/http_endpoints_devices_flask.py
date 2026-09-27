"""Reglas de validación y endpoints HTTP de dispositivos."""

from flask import Blueprint
from pydantic import BaseModel, ConfigDict, Field

from .api_op_codes import API_OP_OK, build_api_response
from .http_validation import validate_request


#==========================
#Reglas de validación
#==========================

class DeviceAssociationInput(BaseModel):
    """Hogar al cual se vinculará un dispositivo físico existente."""

    model_config = ConfigDict(extra="forbid")

    home_id: str = Field(min_length=1)


class DeviceUpdateInput(BaseModel):
    """Campos del dispositivo configurables desde la aplicación."""

    model_config = ConfigDict(extra="forbid")

    name: str | None = Field(default=None, min_length=1)
    connection_by: str | None = Field(default=None, min_length=1)


#==========================
#Endpoints
#==========================

class DevicesEndpoints:
    """Agrupa las rutas de dispositivos e inyecta su procesador HTTP."""

    def __init__(self, http_processor):
        self.http_processor = http_processor
        self.blueprint = Blueprint(
            "devices", __name__, url_prefix="/grandsafelife/api/v1",
        )
        self._register_routes()

    def _register_routes(self):
        """Registra las operaciones HTTP disponibles para dispositivos."""

        @self.blueprint.get("/devices/<device_id>")
        def get_device_by_id(device_id):
            authorization, _, _ = validate_request()
            device = self.http_processor.process_get_device_by_id(
                authorization, device_id,
            )
            return build_api_response(API_OP_OK, device)

        @self.blueprint.post("/devices/<device_id>/association")
        def associate_device(device_id):
            authorization, body, _ = validate_request(body_model=DeviceAssociationInput)
            associated_device_id = self.http_processor.process_associate_device(
                authorization, device_id, body.home_id,
            )
            return build_api_response(API_OP_OK, associated_device_id)

        @self.blueprint.patch("/devices/<device_id>")
        def update_device(device_id):
            authorization, body, _ = validate_request(body_model=DeviceUpdateInput)
            self.http_processor.process_update_device(
                authorization, device_id, body.model_dump(exclude_unset=True),
            )
            return build_api_response(API_OP_OK)

        @self.blueprint.delete("/devices/<device_id>/association")
        def release_device(device_id):
            authorization, _, _ = validate_request()
            self.http_processor.process_release_device(authorization, device_id)
            return build_api_response(API_OP_OK)

        @self.blueprint.get("/users/<owner_id>/devices")
        def get_devices_by_owner(owner_id):
            authorization, _, _ = validate_request()
            devices = self.http_processor.process_get_devices_by_owner(
                authorization, owner_id,
            )
            return build_api_response(API_OP_OK, devices)

        @self.blueprint.get("/homes/<home_id>/devices")
        def get_devices_by_home(home_id):
            authorization, _, _ = validate_request()
            devices = self.http_processor.process_get_devices_by_home(
                authorization, home_id,
            )
            return build_api_response(API_OP_OK, devices)

        @self.blueprint.get("/devices/<device_id>/location")
        def get_device_location(device_id):
            authorization, _, _ = validate_request()
            location = self.http_processor.process_get_device_location(
                authorization, device_id,
            )
            return build_api_response(API_OP_OK, location)
