"""Reglas de validación y endpoints HTTP de hogares."""

from flask import Blueprint
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field, field_validator
from pydantic_core import PydanticCustomError

from .api_op_codes import API_OP_OK, build_api_response
from .http_validation import validate_request


#==========================
#Reglas de validación
#==========================

class HomeMemberInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    email: str = Field(min_length=1)
    role: Literal["admin", "observer", "pending"]


class HomeCreateInput(BaseModel):
    """Campos que la aplicación puede proporcionar al crear un hogar."""

    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=1)
    members: dict[str, HomeMemberInput] = Field(default_factory=dict)


class HomeUpdateInput(BaseModel):
    """Campos editables mediante la actualización parcial de un hogar."""

    model_config = ConfigDict(extra="forbid")

    name: str | None = Field(default=None, min_length=1)
    members: dict[str, HomeMemberInput] | None = None

    @field_validator("name", "members")
    @classmethod
    def reject_explicit_null(cls, value):
        if value is None:
            raise PydanticCustomError("null_not_allowed", "El campo no admite null")
        return value


#==========================
#Endpoints
#==========================

class HomesEndpoints:
    """Agrupa las rutas de hogares e inyecta su procesador HTTP."""

    def __init__(self, http_processor):
        self.http_processor = http_processor
        self.blueprint = Blueprint(
            "homes", __name__, url_prefix="/grandsafelife/api/v1/homes",
        )
        self._register_routes()

    def _register_routes(self):
        """Registra las operaciones HTTP disponibles para hogares."""

        @self.blueprint.get("/<home_id>")
        def get_home_by_id(home_id):
            authorization, _, _ = validate_request()
            home = self.http_processor.process_get_home_by_id(authorization, home_id)
            return build_api_response(API_OP_OK, home)

        @self.blueprint.post("")
        def create_home():
            authorization, body, _ = validate_request(body_model=HomeCreateInput)
            home_id = self.http_processor.process_create_home(
                authorization, body.model_dump(),
            )
            return build_api_response(API_OP_OK, home_id)

        @self.blueprint.patch("/<home_id>")
        def update_home(home_id):
            authorization, body, _ = validate_request(body_model=HomeUpdateInput)
            self.http_processor.process_update_home(
                authorization, home_id, body.model_dump(exclude_unset=True),
            )
            return build_api_response(API_OP_OK)

        @self.blueprint.delete("/<home_id>")
        def delete_home(home_id):
            authorization, _, _ = validate_request()
            self.http_processor.process_delete_home(authorization, home_id)
            return build_api_response(API_OP_OK)
