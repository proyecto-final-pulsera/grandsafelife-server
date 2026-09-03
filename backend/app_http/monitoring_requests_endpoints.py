"""
@file monitoring_requests_endpoints.py
@author Grand Safe Life
@brief Endpoints HTTP relacionados con solicitudes de monitoreo.

Este módulo contendrá las rutas para crear, consultar y responder solicitudes
de acceso a hogares.
"""

from fastapi import APIRouter


class MonitoringRequestsEndpoints:
    """Agrupa las solicitudes de monitoreo e inyecta su procesador HTTP."""

    def __init__(self, http_processor):
        self.http_processor = http_processor
        self.router = APIRouter(
            prefix="/grandsafelife/api/v1",
            tags=["monitoring-requests"],
        )
