"""
@file http_endpoints_homes.py
@author Grand Safe Life
@brief Endpoints HTTP relacionados con hogares.

Este módulo contendrá las rutas de consulta, creación, actualización y
eliminación de hogares.
"""

from fastapi import APIRouter


class HomesEndpoints:
    """Agrupa las rutas de hogares e inyecta su procesador HTTP."""

    def __init__(self, http_processor):
        self.http_processor = http_processor
        self.router = APIRouter(
            prefix="/grandsafelife/api/v1/homes",
            tags=["homes"],
        )
