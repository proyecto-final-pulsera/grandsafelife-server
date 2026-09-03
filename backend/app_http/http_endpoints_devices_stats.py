"""
@file http_endpoints_devices_stats.py
@author Grand Safe Life
@brief Endpoints HTTP relacionados con métricas de dispositivos.

Este módulo contendrá las rutas de consulta de métricas diarias y agregados
mensuales.
"""

from fastapi import APIRouter


class DevicesStatsEndpoints:
    """Agrupa las rutas de métricas e inyecta su procesador HTTP."""

    def __init__(self, http_processor):
        self.http_processor = http_processor
        self.router = APIRouter(
            prefix="/grandsafelife/api/v1/devices/{device_id}/stats",
            tags=["device-stats"],
        )
