"""
@file http_endpoints_users.py
@author Grand Safe Life
@brief Endpoints HTTP relacionados con usuarios.

Este módulo contendrá las rutas de consulta, creación y actualización de
perfiles de usuario.
"""

from fastapi import APIRouter


class UsersEndpoints:
    """Agrupa las rutas de usuarios e inyecta su procesador HTTP."""

    def __init__(self, http_processor):
        self.http_processor = http_processor
        self.router = APIRouter(
            prefix="/grandsafelife/api/v1/users",
            tags=["users"],
        )
