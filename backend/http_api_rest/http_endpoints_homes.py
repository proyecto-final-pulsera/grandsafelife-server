"""Reglas de validación y endpoints HTTP de hogares."""

from flask import Blueprint
from firebase_admin import auth
from pydantic import BaseModel, ConfigDict, Field, JsonValue, RootModel

from ..authentication.authentication import Authentication
from .api_op_codes import API_OP_OK, API_OP_UNAUTHORIZED, build_api_response
from .http_validation import validate_request


#==========================
#Reglas de validación
#==========================

class HomeCreateInput(BaseModel):
    """Campos que la aplicación puede proporcionar al crear un hogar."""

    model_config = ConfigDict(extra="forbid")

    home_id: str | None = Field(default=None, min_length=1)
    data: dict[str, JsonValue]


class HomeUpdateInput(RootModel[dict[str, JsonValue]]):
    """Campos parciales del documento, incluidos nulos y rutas con puntos."""


#==========================
#Endpoints
#==========================

class HomesEndpoints:
    """Agrupa las rutas de hogares e inyecta su procesador HTTP."""

    def __init__(self, http_processor):
        self.http_processor = http_processor
        self.authentication = Authentication()
        self.blueprint = Blueprint(
            "homes", __name__, url_prefix="/grandsafelife/api/v1/homes",
        )
        self._register_routes()

    def _register_routes(self):
        """Registra las operaciones HTTP disponibles para hogares."""

        @self.blueprint.get("/<home_id>")
        def get_home_by_id(home_id):
            authorization, _, _ = validate_request()

            # Autenticación antes de ejecutar el process.
            try:
                current_uid, app_type = self.authentication.get_current_user_uid(authorization)
            except (ValueError, auth.InvalidIdTokenError, auth.RevokedIdTokenError, auth.UserDisabledError):
                return build_api_response(API_OP_UNAUTHORIZED), 401

            print(f"[AUTH SERVER] uid={current_uid}", flush=True)

            # TODO: Validar los permisos de current_uid sobre los datos solicitados.
            # app_type es por ahora la constante mockeada MONITOR_APP.
            home = self.http_processor.process_get_home_by_id(home_id)
            return build_api_response(API_OP_OK, home)

        @self.blueprint.post("")
        def create_home():
            authorization, body, _ = validate_request(body_model=HomeCreateInput)

            # Autenticación antes de ejecutar el process.
            try:
                current_uid, app_type = self.authentication.get_current_user_uid(authorization)
            except (ValueError, auth.InvalidIdTokenError, auth.RevokedIdTokenError, auth.UserDisabledError):
                return build_api_response(API_OP_UNAUTHORIZED), 401

            print(f"[AUTH SERVER] uid={current_uid}", flush=True)

            # TODO: Validar los permisos de current_uid sobre los datos solicitados.
            # app_type es por ahora la constante mockeada MONITOR_APP.
            home_id = self.http_processor.process_create_home(
                body.data, body.home_id,
            )
            return build_api_response(API_OP_OK, home_id)

        @self.blueprint.patch("/<home_id>")
        def update_home(home_id):
            authorization, body, _ = validate_request(body_model=HomeUpdateInput)

            # Autenticación antes de ejecutar el process.
            try:
                current_uid, app_type = self.authentication.get_current_user_uid(authorization)
            except (ValueError, auth.InvalidIdTokenError, auth.RevokedIdTokenError, auth.UserDisabledError):
                return build_api_response(API_OP_UNAUTHORIZED), 401

            print(f"[AUTH SERVER] uid={current_uid}", flush=True)

            # TODO: Validar los permisos de current_uid sobre los datos solicitados.
            # app_type es por ahora la constante mockeada MONITOR_APP.
            self.http_processor.process_update_home(
                home_id, body.model_dump(exclude_unset=True),
            )
            return build_api_response(API_OP_OK)

        @self.blueprint.delete("/<home_id>")
        def delete_home(home_id):
            authorization, _, _ = validate_request()

            # Autenticación antes de ejecutar el process.
            try:
                current_uid, app_type = self.authentication.get_current_user_uid(authorization)
            except (ValueError, auth.InvalidIdTokenError, auth.RevokedIdTokenError, auth.UserDisabledError):
                return build_api_response(API_OP_UNAUTHORIZED), 401

            print(f"[AUTH SERVER] uid={current_uid}", flush=True)

            # TODO: Validar los permisos de current_uid sobre los datos solicitados.
            # app_type es por ahora la constante mockeada MONITOR_APP.
            self.http_processor.process_delete_home(home_id)
            return build_api_response(API_OP_OK)
