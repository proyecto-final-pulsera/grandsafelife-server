"""Reglas de validación y endpoints HTTP de usuarios."""

from flask import Blueprint
from pydantic import BaseModel, ConfigDict, Field

from .api_op_codes import API_OP_OK, build_api_response
from .http_validation import validate_request


#==========================
#Reglas de validación
#==========================

class UserProfileInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=1)
    email: str = Field(min_length=1)
    avatar: str = Field(min_length=1)


class UserProfileUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str | None = Field(default=None, min_length=1)
    email: str | None = Field(default=None, min_length=1)
    avatar: str | None = Field(default=None, min_length=1)


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

        @self.blueprint.patch("/me")
        def update_current_user():
            authorization, body, _ = validate_request(body_model=UserProfileUpdate)
            self.http_processor.process_update_current_user(
                authorization, body.model_dump(exclude_unset=True),
            )
            return build_api_response(API_OP_OK)

        @self.blueprint.get("/<user_id>")
        def get_user_by_id(user_id):
            authorization, _, _ = validate_request()
            user = self.http_processor.process_get_user_by_id(authorization, user_id)
            return build_api_response(API_OP_OK, user)
