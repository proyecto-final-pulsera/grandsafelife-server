"""Reglas de validación y endpoints HTTP de usuarios."""

from flask import Blueprint
from firebase_admin import auth
from pydantic import BaseModel, ConfigDict, Field, JsonValue, RootModel

from ..authentication.authentication import Authentication
from .api_op_codes import API_OP_OK, API_OP_UNAUTHORIZED, build_api_response
from .http_validation import validate_request


#==========================
#Reglas de validación
#==========================

class UserProfileInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    user_id: str | None = Field(default=None, min_length=1)
    data: dict[str, JsonValue]


class UserProfileUpdate(RootModel[dict[str, JsonValue]]):
    """Campos parciales del documento, incluidos nulos y rutas con puntos."""


class UserEmailQuery(BaseModel):
    email: str = Field(min_length=1)


#==========================
#Endpoints
#==========================

class UsersEndpoints:
    def __init__(self, http_processor):
        self.http_processor = http_processor
        self.authentication = Authentication()
        self.blueprint = Blueprint("users", __name__, url_prefix="/grandsafelife/api/v1/users")
        self._register_routes()

    def _register_routes(self):

        @self.blueprint.get("/<user_id>")
        def get_user_by_id(user_id):
            #Validacion de formato
            authorization, _, _ = validate_request()

            # Autenticación antes de ejecutar el process.
            try:
                current_uid, app_type = self.authentication.get_current_user_uid(authorization)
            except (ValueError, auth.InvalidIdTokenError, auth.RevokedIdTokenError, auth.UserDisabledError):
                return build_api_response(API_OP_UNAUTHORIZED), 401

            print(f"[AUTH SERVER] uid={current_uid}", flush=True)

            # TODO: Validar los permisos de current_uid sobre los datos solicitados.
            # app_type es por ahora la constante mockeada MONITOR_APP.

            
            #Procesamiento del request
            user = self.http_processor.process_get_user_by_id(user_id)
            return build_api_response(API_OP_OK, user)


        @self.blueprint.get("/by-email")
        def get_user_by_email():
            #Validacion de formato
            authorization, _, query = validate_request(query_model=UserEmailQuery)

            # Autenticación antes de ejecutar el process.
            try:
                current_uid, app_type = self.authentication.get_current_user_uid(authorization)
            except (ValueError, auth.InvalidIdTokenError, auth.RevokedIdTokenError, auth.UserDisabledError):
                return build_api_response(API_OP_UNAUTHORIZED), 401

            print(f"[AUTH SERVER] uid={current_uid}", flush=True)

            # TODO: Validar los permisos de current_uid sobre los datos solicitados.
            # app_type es por ahora la constante mockeada MONITOR_APP.
            

            #Procesamiento del request
            user = self.http_processor.process_get_user_by_email(query.email)
            return build_api_response(API_OP_OK, user)

        @self.blueprint.post("")
        def create_user():
            #Validacion de formato
            authorization, body, _ = validate_request(body_model=UserProfileInput)

            # Autenticación antes de ejecutar el process.
            try:
                current_uid, app_type = self.authentication.get_current_user_uid(authorization)
            except (ValueError, auth.InvalidIdTokenError, auth.RevokedIdTokenError, auth.UserDisabledError):
                return build_api_response(API_OP_UNAUTHORIZED), 401

            print(f"[AUTH SERVER] uid={current_uid}", flush=True)

            # TODO: Validar los permisos de current_uid sobre los datos solicitados.
            # app_type es por ahora la constante mockeada MONITOR_APP.
            

            #Procesamiento del request
            result = self.http_processor.process_create_user(body.data, body.user_id)
            return build_api_response(API_OP_OK, result)

        @self.blueprint.patch("/<user_id>")
        def update_user(user_id):
            #Validacion de formato
            authorization, body, _ = validate_request(body_model=UserProfileUpdate)

            # Autenticación antes de ejecutar el process.
            try:
                current_uid, app_type = self.authentication.get_current_user_uid(authorization)
            except (ValueError, auth.InvalidIdTokenError, auth.RevokedIdTokenError, auth.UserDisabledError):
                return build_api_response(API_OP_UNAUTHORIZED), 401

            print(f"[AUTH SERVER] uid={current_uid}", flush=True)

            # TODO: Validar los permisos de current_uid sobre los datos solicitados.
            # app_type es por ahora la constante mockeada MONITOR_APP.


            #Procesamiento del request
            self.http_processor.process_update_user(user_id, body.model_dump(exclude_unset=True),)
            return build_api_response(API_OP_OK)
