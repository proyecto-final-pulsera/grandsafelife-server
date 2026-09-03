from .op_status import (
    OP_STATUS_INVALID_PASSWORD,
    OP_STATUS_OK,
    OP_STATUS_USER_NOT_FOUND,
)


class System:
    def __init__(self, db):
        self.db = db

    #==================================================
    # Auth
    #==================================================

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

    #==================================================
    # User profiles (mock implementation)
    #==================================================

    def process_get_current_user(self, authorization):
        # TODO: Verificar el Firebase ID token, extraer el UID y recuperar el
        # perfil real mediante el repository de usuarios.
        return {
            "name": "Juan Pérez",
            "email": "juan.perez@example.com",
            "avatar": "https://example.com/avatars/user_001.png",
            "created_at": 1783700000000,
            "updated_at": 1783882718000,
            "homes": {
                "home_id_001": {
                    "home_name": "Residencia Principal",
                    "role": "admin",
                },
                "home_id_002": {
                    "home_name": "Casa de Campo",
                    "role": "pending",
                },
            },
        }

    def process_get_user_by_id(self, authorization, user_id):
        # TODO: Verificar autenticación y permisos, y definir definitivamente
        # el subconjunto de campos públicos antes de consultar el repository.
        return {
            "name": "María Gómez",
            "email": "maria.gomez@example.com",
            "avatar": "https://example.com/avatars/user_002.png",
        }

    def process_get_user_by_email(self, authorization, email):
        # TODO: Verificar autenticación y permisos, y definir definitivamente
        # el subconjunto de campos públicos antes de consultar el repository.
        return {
            "name": "María Gómez",
            "email": email,
            "avatar": "https://example.com/avatars/user_002.png",
        }

    def process_create_user(self, authorization, user_data):
        # TODO: Verificar el Firebase ID token, usar su UID como identificador y
        # persistir el perfil con timestamps del servidor y homes vacío.
        return {"user_id": "firebase_uid_mock"}

    def process_update_current_user(self, authorization, user_data):
        # TODO: Verificar el Firebase ID token y actualizar mediante el
        # repository solamente los campos editables recibidos.
        return None

    #==================================================
    # Monitoring
    #==================================================

    def process_get_monitored_users(self, authorization):
        # TODO:
        # 1) Obtener usuario autenticado.
        # 2) Consultar MonitoringLinks donde el usuario
        #    autenticado sea monitor.
        # 3) Retornar listado de usuarios monitoreados
        #    junto con el rol asociado.
        pass

    def process_get_my_monitors(self, authorization):
        # TODO:
        # 1) Obtener usuario autenticado.
        # 2) Consultar MonitoringLinks donde el usuario
        #    autenticado sea monitoreado.
        # 3) Retornar listado de monitores asociados
        #    junto con el rol de cada uno.
        pass

    #==================================================
    # Monitoring Requests
    #==================================================

    def process_create_monitoring_request(
        self,
        authorization,
        monitored_user_id,
        requested_user_id,
        requested_role
    ):
        # TODO:
        # 1) Obtener usuario autenticado.
        # 2) Validar requested_role.
        # 3) Verificar que no exista una solicitud equivalente.
        # 4) Crear objeto MonitoringRequest.
        # 5) Inicializar estados:
        #       elderly_status = pending
        #       requested_user_status = pending
        #       status = pending
        # 6) Inicializar flags de lectura:
        #       elderly_read = False
        #       requested_user_read = False
        # 7) Guardar solicitud en base de datos.
        # 8) Retornar request_id generado.
        pass

    def process_answer_monitoring_request(
        self,
        authorization,
        request_id,
        answer
    ):
        # TODO:
        # 1) Obtener usuario autenticado.
        # 2) Buscar solicitud.
        # 3) Validar que el usuario participe de ella.
        # 4) Actualizar estado correspondiente:
        #       elderly_status
        #       requested_user_status
        # 5) Recalcular estado global.
        #
        # Casos:
        #
        # accepted + accepted:
        #     status = accepted
        #     crear MonitoringLink
        #
        # rejected + cualquiera:
        #     status = rejected
        #
        # pending restantes:
        #     status = pending
        #
        # 6) Guardar cambios.
        # 7) Retornar resultado actualizado.
        pass

    def process_get_monitoring_requests(self, authorization):
        # TODO:
        # 1) Obtener usuario autenticado.
        # 2) Consultar solicitudes relacionadas.
        # 3) Marcar como leídas aquellas que correspondan
        #    al usuario autenticado.
        # 4) Retornar listado completo con:
        #       estados
        #       flags de lectura
        #       participantes
        pass

    #==================================================
    # Monitoring Links
    #==================================================

    def process_delete_monitoring_link(
        self,
        authorization,
        link_id
    ):
        # TODO:
        # 1) Obtener usuario autenticado.
        # 2) Buscar MonitoringLink.
        # 3) Verificar permisos para eliminar:
        #       admin
        #       monitor
        #       usuario monitoreado
        # 4) Eliminar relación.
        # 5) Retornar resultado de la operación.
        pass

    def _get_current_user_id_by_token(self, token):
        if token is None:
            return None
        try:
            return int(token)
        except ValueError:
            return None
