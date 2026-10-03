"""
TODO: 
Implementar la verificación de token y permisos de administración

"""
from firebase_admin import auth

def get_current_user_uid(authorization: str) -> str:
    scheme, _, token = authorization.partition(" ")

    if scheme.lower() != "bearer" or not token:
        raise ValueError("Token inválido o no proporcionado")

    decoded_token = auth.verify_id_token(token)
    return decoded_token["uid"]