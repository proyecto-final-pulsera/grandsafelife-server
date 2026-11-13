"""Endpoint del botón de pánico."""
from flask import Blueprint
from firebase_admin import auth
from pydantic import BaseModel, ConfigDict, Field

from ..authentication.authentication import Authentication
from ..database.repositories.repository_homes import HomesRepository
from ..database.repositories.repository_users import UsersRepository
from ..database.repositories.repository_devices import DevicesRepository
from .api_op_codes import (
    API_OP_FORBIDDEN,
    API_OP_PANIC_NO_RECIPIENTS,
    API_OP_PANIC_NOTIFIED,
    API_OP_UNAUTHORIZED,
    build_api_response,
)
from .http_endpoints_fall_detection import FallLocation
from .http_validation import validate_request


class PanicInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    home_id: str = Field(min_length=1, pattern=r"\S")
    deviceUID: str = Field(min_length=1, pattern=r"\S")
    name: str = Field(min_length=1, pattern=r"\S")
    coords: FallLocation


class PanicEndpoints:
    def __init__(self, db, notifier_mng):
        self.homes = HomesRepository(db)
        self.users = UsersRepository(db)
        self.devices = DevicesRepository(db)
        self.notifier_mng = notifier_mng
        self.authentication = Authentication()
        self.blueprint = Blueprint("panic", __name__, url_prefix="/grandsafelife/api/v1/panic")
        self._register_routes()

    def _register_routes(self):
        @self.blueprint.post("")
        def notify_panic():
            authorization, body, _ = validate_request(body_model=PanicInput)
            try:
                current_uid, _ = self.authentication.get_current_user_uid(authorization)
            except (ValueError, auth.InvalidIdTokenError, auth.RevokedIdTokenError, auth.UserDisabledError):
                return build_api_response(API_OP_UNAUTHORIZED), 401

            device = self.devices.get_device_by_id(body.deviceUID)
            if not device or device.get("owner_id") != current_uid:
                return build_api_response(API_OP_FORBIDDEN), 403

            home = self.homes.get_home_by_id(body.home_id)
            members = home.get("members", {}) if home else {}
            if members.get(current_uid, {}).get("role") != "admin":
                return build_api_response(API_OP_FORBIDDEN), 403

            user_ids = list(members)
            tokens = [self.users.getNotificationsToken(user_id) for user_id in user_ids]
            tokens = list(dict.fromkeys(token for token in tokens if token))
            if not tokens:
                return build_api_response(API_OP_PANIC_NO_RECIPIENTS, {"user_ids": user_ids})

            self.notifier_mng.send_panic_notification(
                tokens, body.home_id, body.deviceUID, body.name, body.coords.model_dump()
            )
            return build_api_response(API_OP_PANIC_NOTIFIED, {"user_ids": user_ids})
