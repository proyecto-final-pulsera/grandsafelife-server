"""
@file http_endpoints_monitoring_requests.py
@author Grand Safe Life
@brief Endpoints HTTP relacionados con solicitudes de monitoreo.

Este módulo contendrá las rutas para crear, consultar y responder solicitudes
de acceso a hogares.
"""

from typing import Annotated, Literal

from fastapi import APIRouter, Header
from pydantic import BaseModel, ConfigDict, Field

from .api_op_codes import API_OP_OK, build_api_response


class MonitoringRequestCreateInput(BaseModel):
    """Datos proporcionados al invitar a un usuario a un hogar."""

    model_config = ConfigDict(extra="forbid")

    email: str = Field(min_length=1)
    role: Literal["admin", "observer"]


class MonitoringRequestAnswerInput(BaseModel):
    """Respuesta permitida para una solicitud pendiente."""

    model_config = ConfigDict(extra="forbid")

    answer: Literal["accepted", "rejected"]


AuthorizationHeader = Annotated[str, Header(alias="Authorization")]


class MonitoringRequestsEndpoints:
    """Agrupa las solicitudes de monitoreo e inyecta su procesador HTTP."""

    def __init__(self, http_processor):
        self.http_processor = http_processor
        self.router = APIRouter(
            prefix="/grandsafelife/api/v1",
            tags=["monitoring-requests"],
        )
        self._register_routes()

    def _register_routes(self):
        """Registra las operaciones HTTP de solicitudes de monitoreo."""

        @self.router.post("/homes/{home_id}/monitoring-requests")
        def create_monitoring_request(
            home_id: str,
            request: MonitoringRequestCreateInput,
            authorization: AuthorizationHeader,
        ):
            request_id = self.http_processor.process_create_monitoring_request(
                authorization,
                home_id,
                request.model_dump(),
            )
            return build_api_response(API_OP_OK, request_id)

        @self.router.get("/users/me/monitoring-requests")
        def get_my_monitoring_requests(authorization: AuthorizationHeader):
            requests = self.http_processor.process_get_my_monitoring_requests(
                authorization,
            )
            return build_api_response(API_OP_OK, requests)

        @self.router.post("/monitoring-requests/{request_id}/answer")
        def answer_monitoring_request(
            request_id: str,
            request: MonitoringRequestAnswerInput,
            authorization: AuthorizationHeader,
        ):
            self.http_processor.process_answer_monitoring_request(
                authorization,
                request_id,
                request.answer,
            )
            return build_api_response(API_OP_OK)
