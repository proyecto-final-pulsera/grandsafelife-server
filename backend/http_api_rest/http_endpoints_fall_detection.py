"""Endpoint síncrono de detección de caídas."""
from flask import Blueprint
from firebase_admin import auth
from typing import Any
from pydantic import BaseModel, ConfigDict, Field
from ..database.repositories.repository_homes import HomesRepository
from ..database.repositories.repository_users import UsersRepository
from ..database.repositories.repository_devices import DevicesRepository
from ..authentication.authentication import Authentication
from .api_op_codes import API_OP_FALL_DETECTED, API_OP_FALL_DETECTED_NO_RECIPIENTS, API_OP_FALL_NOT_DETECTED, API_OP_FORBIDDEN, API_OP_PROCESS_FAILED, API_OP_UNAUTHORIZED, build_api_response
from .http_validation import validate_request

#==========================
#Reglas de validación
#==========================
class FallLocation(BaseModel):
    model_config = ConfigDict(extra="forbid")
    lat: float = Field(ge=-90, le=90, allow_inf_nan=False)
    long: float = Field(ge=-180, le=180, allow_inf_nan=False)


class FallHeader(BaseModel):
    model_config = ConfigDict(extra="allow")
    fs_acel: float
    fs_press: float
    din_range_acel: float


class FallAccelerometer(BaseModel):
    model_config = ConfigDict(extra="allow")
    data_acel_x: list[Any]
    data_acel_y: list[Any]
    data_acel_z: list[Any]


class FallAltitude(BaseModel):
    model_config = ConfigDict(extra="allow")
    temp: float | list[Any]
    press: list[Any]


class FallTimeseries(BaseModel):
    model_config = ConfigDict(extra="allow")
    accelerometer: FallAccelerometer
    altitud: FallAltitude


class FallDetectionInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    header: FallHeader
    timeseries: FallTimeseries
    home_id: str = Field(min_length=1, pattern=r"\S")
    deviceUID: str = Field(min_length=1, pattern=r"\S")
    name: str = Field(min_length=1, pattern=r"\S")
    coords: FallLocation

#==========================
#Endpoints
#==========================

class FallDetectionEndpoints:
    def __init__(self, db, detector, notifier_mng=None):
        self.db = db
        self.homes = HomesRepository(db)
        self.users = UsersRepository(db)
        self.devices = DevicesRepository(db)
        self.detector = detector
        self.notifier_mng = notifier_mng
        self.authentication = Authentication()
        self.blueprint = Blueprint("fall_detection", __name__, url_prefix="/grandsafelife/api/v1/fall-detection")
        self._register_routes()

    def _register_routes(self):
        @self.blueprint.post("")
        def detect_fall():
            authorization, body, _ = validate_request(body_model=FallDetectionInput)
            try:
                current_uid, app_type = self.authentication.get_current_user_uid(authorization)
            except (ValueError, auth.InvalidIdTokenError, auth.RevokedIdTokenError, auth.UserDisabledError):
                return build_api_response(API_OP_UNAUTHORIZED), 401
            device = self.devices.get_device_by_id(body.deviceUID)
            if not device or device.get("owner_id") != current_uid:
                return build_api_response(API_OP_FORBIDDEN), 403

            home = self.homes.get_home_by_id(body.home_id)
            members = home.get("members", {}) if home else {}
            member = members.get(current_uid, {})
            if member.get("role") != "admin":
                return build_api_response(API_OP_FORBIDDEN), 403

            user_ids = list(members)

            result = self.detector.detect_fall(body.model_dump())
            if result.error_code is not None:
                return build_api_response(API_OP_PROCESS_FAILED, {"error_code": result.error_code}), 500

            is_fall = result.is_fall_detected

            if is_fall:
                tokens = [self.users.getNotificationsToken(user_id) for user_id in user_ids]
                tokens = list(dict.fromkeys(token for token in tokens if token))
                if tokens:
                    self.notifier_mng.send_fall_notification(
                        tokens, body.home_id, body.deviceUID, body.name, body.coords.model_dump()
                    )
                else:
                    # TODO: Definir la acción posterior del servidor ante una caída sin destinatarios.
                    return build_api_response(API_OP_FALL_DETECTED_NO_RECIPIENTS, {"user_ids": user_ids})

            if is_fall:
                code = API_OP_FALL_DETECTED
            else:
                code = API_OP_FALL_NOT_DETECTED
            return build_api_response(code, {"user_ids": user_ids})
