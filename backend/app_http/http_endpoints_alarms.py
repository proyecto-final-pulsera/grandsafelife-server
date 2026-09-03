"""
@file http_endpoints_alarms.py
@author Grand Safe Life
@brief Endpoints HTTP relacionados con alarmas de dispositivos.

Este módulo contendrá las rutas para consultar y reemplazar la configuración de
alarmas de un dispositivo.
"""

from fastapi import APIRouter


class AlarmsEndpoints:
    """Agrupa las rutas de alarmas e inyecta su procesador HTTP."""

    def __init__(self, http_processor):
        self.http_processor = http_processor
        self.router = APIRouter(
            prefix="/grandsafelife/api/v1/devices/{device_id}/alarms",
            tags=["alarms"],
        )
