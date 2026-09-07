"""
@file http_endpoints_devices.py
@author Grand Safe Life
@brief Endpoints HTTP relacionados con dispositivos.

Este módulo contendrá las rutas de consulta, asociación, actualización y
desvinculación de dispositivos.
"""

from typing import Annotated

from fastapi import APIRouter, Header
from pydantic import BaseModel, ConfigDict, Field

from .api_op_codes import API_OP_OK, build_api_response


class DeviceAssociationInput(BaseModel):
    """Hogar al cual se vinculará un dispositivo físico existente."""

    model_config = ConfigDict(extra="forbid")

    home_id: str = Field(min_length=1)


class DeviceUpdateInput(BaseModel):
    """Campos del dispositivo configurables desde la aplicación."""

    model_config = ConfigDict(extra="forbid")

    name: str | None = Field(default=None, min_length=1)
    connection_by: str | None = Field(default=None, min_length=1)


AuthorizationHeader = Annotated[str, Header(alias="Authorization")]


class DevicesEndpoints:
    """Agrupa las rutas de dispositivos e inyecta su procesador HTTP."""

    def __init__(self, http_processor):
        self.http_processor = http_processor
        self.router = APIRouter(
            prefix="/grandsafelife/api/v1",
            tags=["devices"],
        )
        self._register_routes()

    def _register_routes(self):
        """Registra las operaciones HTTP disponibles para dispositivos."""

        @self.router.get("/devices/{device_id}")
        def get_device_by_id(
            device_id: str,
            authorization: AuthorizationHeader,
        ):
            device = self.http_processor.process_get_device_by_id(
                authorization,
                device_id,
            )
            return build_api_response(API_OP_OK, device)

        @self.router.post("/devices/{device_id}/association")
        def associate_device(
            device_id: str,
            request: DeviceAssociationInput,
            authorization: AuthorizationHeader,
        ):
            associated_device_id = self.http_processor.process_associate_device(
                authorization,
                device_id,
                request.home_id,
            )
            return build_api_response(API_OP_OK, associated_device_id)

        @self.router.patch("/devices/{device_id}")
        def update_device(
            device_id: str,
            request: DeviceUpdateInput,
            authorization: AuthorizationHeader,
        ):
            self.http_processor.process_update_device(
                authorization,
                device_id,
                request.model_dump(exclude_unset=True),
            )
            return build_api_response(API_OP_OK)

        @self.router.delete("/devices/{device_id}/association")
        def release_device(
            device_id: str,
            authorization: AuthorizationHeader,
        ):
            self.http_processor.process_release_device(
                authorization,
                device_id,
            )
            return build_api_response(API_OP_OK)

        @self.router.get("/users/{owner_id}/devices")
        def get_devices_by_owner(
            owner_id: str,
            authorization: AuthorizationHeader,
        ):
            devices = self.http_processor.process_get_devices_by_owner(
                authorization,
                owner_id,
            )
            return build_api_response(API_OP_OK, devices)

        @self.router.get("/homes/{home_id}/devices")
        def get_devices_by_home(
            home_id: str,
            authorization: AuthorizationHeader,
        ):
            devices = self.http_processor.process_get_devices_by_home(
                authorization,
                home_id,
            )
            return build_api_response(API_OP_OK, devices)

        @self.router.get("/devices/{device_id}/location")
        def get_device_location(
            device_id: str,
            authorization: AuthorizationHeader,
        ):
            location = self.http_processor.process_get_device_location(
                authorization,
                device_id,
            )
            return build_api_response(API_OP_OK, location)
