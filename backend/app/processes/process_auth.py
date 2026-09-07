"""Procesamiento de auth; conserva los mocks y TODO existentes."""

class AuthProcesses:
    def __init__(self, db):
        self.db = db

    def process_login(self, usr, psw):
        # TODO: Revisar esta firma heredada al implementar autenticación.
        # El diseño previsto verifica Firebase ID tokens; el servidor no
        # recibe contraseñas ni genera tokens a partir del ID del usuario.
        pass

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
