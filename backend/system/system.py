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
    # Homes (mock implementation)
    #==================================================

    def process_get_home_by_id(self, authorization, home_id):
        # TODO: Verificar el Firebase ID token, la existencia del hogar, la
        # pertenencia del solicitante y sus permisos de lectura.
        return {
            "name": "Residencia Principal",
            "created_at": 1783882718000,
            "updated_at": 1783882718000,
            "members": {
                "user_id_001": {
                    "email": "juan.perez@example.com",
                    "role": "admin",
                },
                "user_id_002": {
                    "email": "maria.gomez@example.com",
                    "role": "observer",
                },
            },
        }

    def process_create_home(self, authorization, home_data):
        # TODO: Verificar el Firebase ID token y crear atómicamente el hogar y
        # la relación del usuario autenticado como miembro administrador.
        return "home_id_001"

    def process_update_home(self, authorization, home_id, home_data):
        # TODO: Verificar que el hogar exista y que el usuario autenticado tenga
        # permisos suficientes antes de persistir los campos editables.
        return None

    def process_delete_home(self, authorization, home_id):
        # TODO: Verificar rol administrador y eliminar consistentemente el
        # hogar y todas sus referencias en los perfiles de sus miembros.
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

    def process_create_monitoring_request(self, authorization, home_id, data):
        # TODO: Verificar el token y el rol administrador del solicitante,
        # resolver el destinatario por email, prevenir membresías o solicitudes
        # pendientes duplicadas, persistir y enviar la notificación.
        return "request_id_001"

    def process_get_my_monitoring_requests(self, authorization):
        # TODO: Verificar el token y consultar las solicitudes pendientes
        # recibidas por el usuario autenticado mediante el repository.
        return [
            {
                "request_id": "request_id_001",
                "home_id": "home_id_001",
                "home_name": "Residencia Principal",
                "requester": {
                    "name": "Juan Pérez",
                    "email": "juan.perez@example.com",
                },
                "requested_role": "observer",
                "status": "pending",
                "created_at": 1783882718000,
                "updated_at": 1783882718000,
            }
        ]

    def process_answer_monitoring_request(
        self,
        authorization,
        request_id,
        answer
    ):
        # TODO: Verificar token, existencia y estado pendiente de la solicitud,
        # y que el usuario autenticado sea su destinatario. Si acepta, agregar
        # atómicamente ambas relaciones de membresía; si rechaza, no agregarlas.
        # Persistir el estado definitivo y enviar las notificaciones necesarias.
        return None

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
