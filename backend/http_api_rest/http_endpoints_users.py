"""Reglas de validación y endpoints HTTP de usuarios."""

from flask import Blueprint
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field, field_validator
from pydantic_core import PydanticCustomError

from .api_op_codes import API_OP_OK, build_api_response
from .http_validation import validate_request


#==========================
#Reglas de validación
#==========================

class UserProfileInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=1)
    email: str = Field(min_length=1)
    avatar: str | None = Field(default=None, min_length=1)


class UserHomeInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    home_name: str = Field(min_length=1)
    role: Literal["admin", "observer", "pending"]


class UserProfileUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str | None = Field(default=None, min_length=1)
    email: str | None = Field(default=None, min_length=1)
    avatar: str | None = Field(default=None, min_length=1)
    homes: dict[str, UserHomeInput] | None = None

    @field_validator("name", "email", "homes")
    @classmethod
    def reject_explicit_null(cls, value):
        if value is None:
            raise PydanticCustomError("null_not_allowed", "El campo no admite null")
        return value


class UserEmailQuery(BaseModel):
    email: str = Field(min_length=1)


#==========================
#Endpoints
#==========================

class UsersEndpoints:
    def __init__(self, http_processor):
        self.http_processor = http_processor
        self.blueprint = Blueprint("users", __name__, url_prefix="/grandsafelife/api/v1/users")
        self._register_routes()

    def _register_routes(self):
        @self.blueprint.get("/me")
        def get_current_user():
            authorization, _, _ = validate_request()
            user = self.http_processor.process_get_current_user(authorization)
            return build_api_response(API_OP_OK, user)

        @self.blueprint.get("/by-email")
        def get_user_by_email():
            authorization, _, query = validate_request(query_model=UserEmailQuery)
            user = self.http_processor.process_get_user_by_email(authorization, query.email)
            return build_api_response(API_OP_OK, user)

        @self.blueprint.post("/me")
        def create_user():
            authorization, body, _ = validate_request(body_model=UserProfileInput)
            result = self.http_processor.process_create_user(authorization, body.model_dump())
            return build_api_response(API_OP_OK, result)

        @self.blueprint.patch("/<user_id>")
        def update_user(user_id):
            authorization, body, _ = validate_request(body_model=UserProfileUpdate)
            self.http_processor.process_update_user(
                authorization, user_id, body.model_dump(exclude_unset=True),
            )
            return build_api_response(API_OP_OK)

        @self.blueprint.get("/<user_id>")
        def get_user_by_id(user_id):
            authorization, _, _ = validate_request()
            user = self.http_processor.process_get_user_by_id(authorization, user_id)
            return build_api_response(API_OP_OK, user)
