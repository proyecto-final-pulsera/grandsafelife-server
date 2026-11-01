"""Endpoint síncrono de detección de caídas."""
from flask import Blueprint
from firebase_admin import auth
from pydantic import BaseModel, ConfigDict, StrictBool
from ..authentication.authentication import Authentication
from .api_op_codes import API_OP_OK, API_OP_PROCESS_FAILED, API_OP_UNAUTHORIZED, build_api_response
from .http_validation import validate_request

#==========================
#Reglas de validación
#==========================
class FallDetectionInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    fall_detected: StrictBool

#==========================
#Endpoints
#==========================

class FallDetectionEndpoints:
    def __init__(self, db, detector, notifier_mng=None):
        self.db = db
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
            # TODO: Validar permisos y tipo de aplicación como en users.

            result = self.detector.detect_fall(body.model_dump())
            if result.error_code is not None:
                return build_api_response(API_OP_PROCESS_FAILED, {"error_code": result.error_code}), 500

            is_fall = result.is_fall_detected

            if(is_fall):
                # TODO: Recuperar usuarios monitores a los que hay que notificar y enviarles la notificación de caída.
                pass

            return build_api_response(API_OP_OK, {"is_fall": is_fall})
