"""Verificación de identidad mediante un ID token de Firebase.

Firebase Admin debe estar inicializado antes de verificar tokens.
El tipo de aplicación es temporalmente fijo; no se validan roles del hogar.
"""
from firebase_admin import auth

MONITOR_APP = "MONITOR_APP"


class Authentication:
    def get_current_user_uid(self, authorization: str) -> tuple[str, str]:
        """Recibe Authorization: Bearer <ID token> y retorna (uid, app_type).

        Propaga los errores de Firebase si el token no es válido o expiró.
        MONITOR_APP es un mock, no una aplicación identificada por el token.
        """
        if not isinstance(authorization, str):
            raise ValueError("Token inválido o no proporcionado")

        parts = authorization.split()
        if len(parts) != 2 or parts[0].lower() != "bearer":
            raise ValueError("Token inválido o no proporcionado")

        decoded_token = auth.verify_id_token(parts[1])
        return decoded_token["uid"], MONITOR_APP


def get_current_user_uid(authorization: str) -> tuple[str, str]:
    """Acceso a la autenticación para consumidores que usan la función del módulo."""
    return Authentication().get_current_user_uid(authorization)
