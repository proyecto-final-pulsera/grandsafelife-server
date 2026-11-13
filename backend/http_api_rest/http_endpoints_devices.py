"""Reglas de validación y endpoints HTTP de dispositivos."""

from typing import Literal

from flask import Blueprint
from firebase_admin import auth
from pydantic import BaseModel, ConfigDict, Field, JsonValue, RootModel

from ..authentication.authentication import Authentication
from .api_op_codes import API_OP_OK, API_OP_UNAUTHORIZED, API_OP_FORBIDDEN, build_api_response
from .http_validation import validate_request


#==========================
#Reglas de validación
#==========================


class DeviceUpdateInput(RootModel[dict[str, JsonValue]]):
    """Mapa parcial de campos; conserva nombres, valores nulos y mapas anidados."""


class DeviceCreateInput(BaseModel):
    """Separa el ID del documento de los campos que se guardarán en él."""

    model_config = ConfigDict(extra="forbid")
    device_id: str | None = Field(default=None, min_length=1)
    data: dict[str, JsonValue]


class WristbandInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    device_id: str = Field(min_length=1, pattern=r"\S")


class WristbandKeepAliveInput(WristbandInput):
    # Unix timestamp en milisegundos, generado por la app.
    timestamp: int = Field(strict=True, gt=0)


class WristbandBatteryInput(WristbandInput):
    level: int = Field(strict=True, ge=0, le=100)


class WristbandStateInput(WristbandInput):
    state: Literal["WEARED", "NO_WEARED", "DISCONNECTED"]


def authorize_wristband(authentication, authorization, device_id, devices, homes):
    """Verifica el token, la propiedad de la pulsera y el rol en su hogar real."""
    try:
        current_uid, _ = authentication.get_current_user_uid(authorization)
    except (ValueError, auth.InvalidIdTokenError, auth.RevokedIdTokenError, auth.UserDisabledError):
        return build_api_response(API_OP_UNAUTHORIZED), 401

    device = devices.get_device_by_id(device_id)
    if not device or device.get("owner_id") != current_uid:
        return build_api_response(API_OP_FORBIDDEN), 403

    home_id = device.get("home_id")
    home = homes.get_home_by_id(home_id) if home_id else None
    member = ((home or {}).get("members") or {}).get(current_uid) or {}
    if member.get("role") != "admin":
        return build_api_response(API_OP_UNAUTHORIZED), 403
    return None


#==========================
#Endpoints
#==========================

class DevicesEndpoints:
    """Agrupa las rutas de dispositivos e inyecta su procesador HTTP."""

    def __init__(self, repository, homes_repository):
        self.repository = repository
        self.homes = homes_repository
        self.last_wristband_data = {}
        self.authentication = Authentication()
        self.blueprint = Blueprint("devices", __name__, url_prefix="/grandsafelife/api/v1",)
        self._register_routes()

    def _register_routes(self):
        """Registra las operaciones HTTP disponibles para dispositivos."""

        def receive_wristband_data(model, operation):
            authorization, body, _ = validate_request(body_model=model)
            error = authorize_wristband(
                self.authentication, authorization, body.device_id, self.repository, self.homes,
            )
            if error is not None:
                return error
            data = body.model_dump()
            self.last_wristband_data[operation] = data
            print(f"[WRISTBAND {operation}] {data}", flush=True)
            return build_api_response(API_OP_OK)

        @self.blueprint.post("/wristband-keep-alive")
        def wristband_keep_alive():
            return receive_wristband_data(WristbandKeepAliveInput, "keep_alive")

        @self.blueprint.post("/wristband-battery")
        def wristband_battery():
            return receive_wristband_data(WristbandBatteryInput, "battery")

        @self.blueprint.post("/wristband-state")
        def wristband_state():
            return receive_wristband_data(WristbandStateInput, "state")

        @self.blueprint.post("/devices")
        def create_device():
            authorization, body, _ = validate_request(body_model=DeviceCreateInput)

            # Autenticación antes de ejecutar el process.
            try:
                current_uid, app_type = self.authentication.get_current_user_uid(authorization)
            except (ValueError, auth.InvalidIdTokenError, auth.RevokedIdTokenError, auth.UserDisabledError):
                return build_api_response(API_OP_UNAUTHORIZED), 401

            print(f"[AUTH SERVER] uid={current_uid}", flush=True)

            device_id = self.repository.create_device(body.data,body.device_id,)
            return build_api_response(API_OP_OK, device_id)

        @self.blueprint.get("/devices/<device_id>")
        def get_device_by_id(device_id):
            authorization, _, _ = validate_request()

            # Autenticación antes de ejecutar el process.
            try:
                current_uid, app_type = self.authentication.get_current_user_uid(authorization)
            except (ValueError, auth.InvalidIdTokenError, auth.RevokedIdTokenError, auth.UserDisabledError):
                return build_api_response(API_OP_UNAUTHORIZED), 401

            print(f"[AUTH SERVER] uid={current_uid}", flush=True)

            device = self.repository.get_device_by_id(device_id,)
            return build_api_response(API_OP_OK, device)

        @self.blueprint.patch("/devices/<device_id>")
        def update_device(device_id):
            authorization, body, _ = validate_request(body_model=DeviceUpdateInput)

            # Autenticación antes de ejecutar el process.
            try:
                current_uid, app_type = self.authentication.get_current_user_uid(authorization)
            except (ValueError, auth.InvalidIdTokenError, auth.RevokedIdTokenError, auth.UserDisabledError):
                return build_api_response(API_OP_UNAUTHORIZED), 401

            print(f"[AUTH SERVER] uid={current_uid}", flush=True)

            self.repository.update_device(device_id, body.model_dump(exclude_unset=True),)
            return build_api_response(API_OP_OK)

        @self.blueprint.delete("/devices/<device_id>")
        def delete_device(device_id):
            authorization, _, _ = validate_request()

            # Autenticación antes de ejecutar el process.
            try:
                current_uid, app_type = self.authentication.get_current_user_uid(authorization)
            except (ValueError, auth.InvalidIdTokenError, auth.RevokedIdTokenError, auth.UserDisabledError):
                return build_api_response(API_OP_UNAUTHORIZED), 401

            print(f"[AUTH SERVER] uid={current_uid}", flush=True)

            self.repository.delete_device(device_id)
            return build_api_response(API_OP_OK)

        @self.blueprint.get("/users/<owner_id>/devices")
        def get_devices_by_owner(owner_id):
            authorization, _, _ = validate_request()

            # Autenticación antes de ejecutar el process.
            try:
                current_uid, app_type = self.authentication.get_current_user_uid(authorization)
            except (ValueError, auth.InvalidIdTokenError, auth.RevokedIdTokenError, auth.UserDisabledError):
                return build_api_response(API_OP_UNAUTHORIZED), 401

            print(f"[AUTH SERVER] uid={current_uid}", flush=True)

            devices = self.repository.get_devices_by_owner(owner_id,)
            return build_api_response(API_OP_OK, devices)

        @self.blueprint.get("/homes/<home_id>/devices")
        def get_devices_by_home(home_id):
            authorization, _, _ = validate_request()

            # Autenticación antes de ejecutar el process.
            try:
                current_uid, app_type = self.authentication.get_current_user_uid(authorization)
            except (ValueError, auth.InvalidIdTokenError, auth.RevokedIdTokenError, auth.UserDisabledError):
                return build_api_response(API_OP_UNAUTHORIZED), 401

            print(f"[AUTH SERVER] uid={current_uid}", flush=True)

            devices = self.repository.get_devices_by_home(home_id,)
            return build_api_response(API_OP_OK, devices)

        @self.blueprint.get("/devices/<device_id>/location")
        def get_device_location(device_id):
            authorization, _, _ = validate_request()

            # Autenticación antes de ejecutar el process.
            try:
                current_uid, app_type = self.authentication.get_current_user_uid(authorization)
            except (ValueError, auth.InvalidIdTokenError, auth.RevokedIdTokenError, auth.UserDisabledError):
                return build_api_response(API_OP_UNAUTHORIZED), 401

            print(f"[AUTH SERVER] uid={current_uid}", flush=True)

            location = self.repository.get_device_location(device_id,)
            return build_api_response(API_OP_OK, location)
