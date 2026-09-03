"""
@file http_endpoints_alarms.py
@author Grand Safe Life
@brief Endpoints HTTP relacionados con alarmas de dispositivos.

Este módulo contendrá las rutas para consultar y reemplazar la configuración de
alarmas de un dispositivo.
"""

from typing import Annotated

from fastapi import APIRouter, Header
from pydantic import BaseModel, ConfigDict, Field, RootModel

from .api_op_codes import API_OP_OK, build_api_response


class AlarmInput(BaseModel):
    """Campos configurables de una alarma enviados por la aplicación."""

    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=1)
    time_in_minutes: int = Field(ge=0, le=1439)
    days: int
    is_active: bool


class AlarmMapInput(RootModel[dict[str, AlarmInput]]):
    """Representación completa de alarmas indexadas por su ID."""


AuthorizationHeader = Annotated[str, Header(alias="Authorization")]


class AlarmsEndpoints:
    """Agrupa las rutas de alarmas e inyecta su procesador HTTP."""

    def __init__(self, http_processor):
        self.http_processor = http_processor
        self.router = APIRouter(
            prefix="/grandsafelife/api/v1/devices/{device_id}/alarms",
            tags=["alarms"],
        )
        self._register_routes()

    def _register_routes(self):
        """Registra las operaciones HTTP disponibles para alarmas."""

        @self.router.get("")
        def get_alarms_by_device_id(
            device_id: str,
            authorization: AuthorizationHeader,
        ):
            alarms = self.http_processor.process_get_alarms_by_device_id(
                authorization,
                device_id,
            )
            return build_api_response(API_OP_OK, alarms)

        @self.router.put("")
        def set_alarms_by_device_id(
            device_id: str,
            request: AlarmMapInput,
            authorization: AuthorizationHeader,
        ):
            self.http_processor.process_set_alarms_by_device_id(
                authorization,
                device_id,
                request.model_dump(),
            )
            return build_api_response(API_OP_OK)
