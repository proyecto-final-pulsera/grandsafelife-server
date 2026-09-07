"""
@file http_endpoints_users.py
@author Grand Safe Life
@brief Endpoints HTTP relacionados con usuarios.

Este módulo contendrá las rutas de consulta, creación y actualización de
perfiles de usuario.
"""

from typing import Annotated

from fastapi import APIRouter, Header, Query
from pydantic import BaseModel, ConfigDict, Field

from .api_op_codes import API_OP_OK, build_api_response


class UserProfileInput(BaseModel):
    """Campos editables al crear el perfil de Grand Safe Life."""

    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=1)
    email: str = Field(min_length=1)
    avatar: str = Field(min_length=1)


class UserProfileUpdate(BaseModel):
    """Campos que la aplicación puede modificar parcialmente."""

    model_config = ConfigDict(extra="forbid")

    name: str | None = Field(default=None, min_length=1)
    email: str | None = Field(default=None, min_length=1)
    avatar: str | None = Field(default=None, min_length=1)


AuthorizationHeader = Annotated[str, Header(alias="Authorization")]


class UsersEndpoints:
    """Agrupa las rutas de usuarios e inyecta su procesador HTTP."""

    def __init__(self, http_processor):
        self.http_processor = http_processor
        self.router = APIRouter(
            prefix="/grandsafelife/api/v1/users",
            tags=["users"],
        )
        self._register_routes()

    def _register_routes(self):
        """Registra las rutas estáticas antes de la ruta dinámica por UID."""

        @self.router.get("/me")
        def get_current_user(authorization: AuthorizationHeader):
            user = self.http_processor.process_get_current_user(authorization)
            return build_api_response(API_OP_OK, user)

        @self.router.get("/by-email")
        def get_user_by_email(
            authorization: AuthorizationHeader,
            email: Annotated[str, Query(min_length=1)],
        ):
            user = self.http_processor.process_get_user_by_email(
                authorization,
                email,
            )
            return build_api_response(API_OP_OK, user)

        @self.router.post("/me")
        def create_user(
            request: UserProfileInput,
            authorization: AuthorizationHeader,
        ):
            result = self.http_processor.process_create_user(
                authorization,
                request.model_dump(),
            )
            return build_api_response(API_OP_OK, result)

        @self.router.patch("/me")
        def update_current_user(
            request: UserProfileUpdate,
            authorization: AuthorizationHeader,
        ):
            self.http_processor.process_update_current_user(
                authorization,
                request.model_dump(exclude_unset=True),
            )
            return build_api_response(API_OP_OK)

        @self.router.get("/{user_id}")
        def get_user_by_id(user_id: str, authorization: AuthorizationHeader):
            user = self.http_processor.process_get_user_by_id(
                authorization,
                user_id,
            )
            return build_api_response(API_OP_OK, user)
