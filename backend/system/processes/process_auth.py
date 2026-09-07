"""Procesamiento de auth; conserva los mocks y TODO existentes."""

from ..op_status import (
    OP_STATUS_INVALID_PASSWORD,
    OP_STATUS_OK,
    OP_STATUS_USER_NOT_FOUND,
)


class AuthProcesses:
    def __init__(self, db):
        self.db = db

    def process_login(self, usr, psw):
        user = self.db.users.get_user_by_username(usr)

        if user is None:
            return {"op_status": OP_STATUS_USER_NOT_FOUND}

        if user.password != psw:
            return {"op_status": OP_STATUS_INVALID_PASSWORD}

        return {
            "op_status": OP_STATUS_OK,
            "token": str(user.user_id)
        }

    def process_get_me(self, authorization):
        # TODO:
        # 1) Obtener usuario autenticado a partir del token.
        # 2) Buscar información del usuario en base de datos.
        # 3) Retornar datos básicos del perfil.
        pass

    def _get_current_user_id_by_token(self, token):
        if token is None:
            return None
        try:
            return int(token)
        except ValueError:
            return None
