"""
@file http_endpoints_homes.py
@author Grand Safe Life
@brief Endpoints HTTP relacionados con hogares.

Este módulo contendrá las rutas de consulta, creación, actualización y
eliminación de hogares.
"""

from typing import Annotated

from fastapi import APIRouter, Header
from pydantic import BaseModel, ConfigDict, Field

from .api_op_codes import API_OP_OK, build_api_response


class HomeCreateInput(BaseModel):
    """Campos que la aplicación puede proporcionar al crear un hogar."""

    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=1)


class HomeUpdateInput(BaseModel):
    """Campos editables mediante la actualización parcial de un hogar."""

    model_config = ConfigDict(extra="forbid")

    name: str | None = Field(default=None, min_length=1)


AuthorizationHeader = Annotated[str, Header(alias="Authorization")]


class HomesEndpoints:
    """Agrupa las rutas de hogares e inyecta su procesador HTTP."""

    def __init__(self, http_processor):
        self.http_processor = http_processor
        self.router = APIRouter(
            prefix="/grandsafelife/api/v1/homes",
            tags=["homes"],
        )
        self._register_routes()

    def _register_routes(self):
        """Registra las operaciones HTTP disponibles para hogares."""

        @self.router.get("/{home_id}")
        def get_home_by_id(home_id: str, authorization: AuthorizationHeader):
            home = self.http_processor.process_get_home_by_id(
                authorization,
                home_id,
            )
            return build_api_response(API_OP_OK, home)

        @self.router.post("")
        def create_home(
            request: HomeCreateInput,
            authorization: AuthorizationHeader,
        ):
            home_id = self.http_processor.process_create_home(
                authorization,
                request.model_dump(),
            )
            return build_api_response(API_OP_OK, home_id)

        @self.router.patch("/{home_id}")
        def update_home(
            home_id: str,
            request: HomeUpdateInput,
            authorization: AuthorizationHeader,
        ):
            self.http_processor.process_update_home(
                authorization,
                home_id,
                request.model_dump(exclude_unset=True),
            )
            return build_api_response(API_OP_OK)

        @self.router.delete("/{home_id}")
        def delete_home(home_id: str, authorization: AuthorizationHeader):
            self.http_processor.process_delete_home(authorization, home_id)
            return build_api_response(API_OP_OK)
