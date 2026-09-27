"""Reglas de validación y endpoints HTTP de solicitudes de monitoreo."""

from typing import Literal

from flask import Blueprint
from pydantic import BaseModel, ConfigDict, Field

from .api_op_codes import API_OP_OK, build_api_response
from .http_validation import validate_request


#==========================
#Reglas de validación
#==========================

class MonitoringRequestCreateInput(BaseModel):
    """Email del destinatario y rol solicitado para participar del hogar."""

    model_config = ConfigDict(extra="forbid")

    email: str = Field(min_length=1)
    role: Literal["admin", "observer"]


class MonitoringRequestAnswerInput(BaseModel):
    """Respuesta admitida para una solicitud de monitoreo."""

    model_config = ConfigDict(extra="forbid")

    answer: Literal["accepted", "rejected"]


#==========================
#Endpoints
#==========================

class MonitoringRequestsEndpoints:
    """Agrupa las rutas y delega las operaciones en el procesador inyectado."""

    def __init__(self, http_processor):
        """Recibe el procesador y prepara el Blueprint de solicitudes."""
        self.http_processor = http_processor
        self.blueprint = Blueprint(
            "monitoring_requests", __name__, url_prefix="/grandsafelife/api/v1",
        )
        self._register_routes()

    def _register_routes(self):
        """Registra creación, consulta y respuesta de solicitudes."""

        @self.blueprint.post("/homes/<home_id>/monitoring-requests")
        def create_monitoring_request(home_id):
            """Valida la invitación y solicita su creación para el hogar indicado."""
            authorization, body, _ = validate_request(body_model=MonitoringRequestCreateInput)
            request_id = self.http_processor.process_create_monitoring_request(
                authorization, home_id, body.model_dump(),
            )
            return build_api_response(API_OP_OK, request_id)

        @self.blueprint.get("/users/me/monitoring-requests")
        def get_my_monitoring_requests():
            """Consulta las solicitudes recibidas por el usuario."""
            authorization, _, _ = validate_request()
            requests = self.http_processor.process_get_my_monitoring_requests(authorization)
            return build_api_response(API_OP_OK, requests)

        @self.blueprint.post("/monitoring-requests/<request_id>/answer")
        def answer_monitoring_request(request_id):
            """Valida y entrega la respuesta a la solicitud indicada."""
            authorization, body, _ = validate_request(body_model=MonitoringRequestAnswerInput)
            self.http_processor.process_answer_monitoring_request(
                authorization, request_id, body.answer,
            )
            return build_api_response(API_OP_OK)
