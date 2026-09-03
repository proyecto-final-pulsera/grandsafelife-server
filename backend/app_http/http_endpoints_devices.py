"""
@file http_endpoints_devices.py
@author Grand Safe Life
@brief Endpoints HTTP relacionados con dispositivos.

Este módulo contendrá las rutas de consulta, asociación, actualización y
desvinculación de dispositivos.
"""

from fastapi import APIRouter


class DevicesEndpoints:
    """Agrupa las rutas de dispositivos e inyecta su procesador HTTP."""

    def __init__(self, http_processor):
        self.http_processor = http_processor
        self.router = APIRouter(
            prefix="/grandsafelife/api/v1/devices",
            tags=["devices"],
        )
