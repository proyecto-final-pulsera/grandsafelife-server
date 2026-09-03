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
    # Devices (mock implementation)
    #==================================================

    def process_get_device_by_id(self, authorization, device_id):
        # TODO: Verificar el token, la existencia del dispositivo y el acceso
        # del solicitante al hogar asociado antes de consultar el repository.
        device = self._get_mock_devices()["dev_a81f23"].copy()
        device["id"] = device_id
        return device

    def process_associate_device(self, authorization, device_id, home_id):
        # TODO: Verificar token, permisos sobre el hogar y que el dispositivo
        # exista y esté disponible. Resolver owner_id desde el administrador
        # del hogar y persistir consistentemente la asociación.
        return device_id

    def process_update_device(self, authorization, device_id, device_data):
        # TODO: Verificar token y permisos, y validar que connection_by sea -1
        # o un hub válido para el hogar antes de actualizar el repository.
        return None

    def process_release_device(self, authorization, device_id):
        # TODO: Verificar token y permisos, y eliminar home_id y owner_id sin
        # borrar el dispositivo físico ni sus estadísticas históricas.
        return None

    def process_get_devices_by_owner(self, authorization, owner_id):
        # TODO: Verificar token y autorización para consultar los hogares cuyo
        # administrador propietario coincide con owner_id.
        return self._get_mock_devices()

    def process_get_devices_by_home(self, authorization, home_id):
        # TODO: Verificar token y membresía autorizada sobre el hogar, consultar
        # sus dispositivos y excluir hubs de infraestructura del resultado.
        return self._get_mock_devices()

    def process_get_device_location(self, authorization, device_id):
        # TODO: Verificar token, existencia del dispositivo y acceso al hogar
        # asociado antes de recuperar la última ubicación reportada.
        return {"lat": -34.6037, "long": -58.3816}

    @staticmethod
    def _get_mock_devices():
        return {
            "dev_a81f23": {
                "created_at": "2026-08-15T10:32:14Z",
                "updated_at": "2026-09-01T18:21:47Z",
                "home_id": "home_7f3a92",
                "owner_id": "user_admin_001",
                "is_active": True,
                "type": "sensor",
                "battery": 87,
                "name": "Sensor Living",
                "connection_by": "hub_001",
                "coords": {"lat": -34.6037, "long": -58.3816},
            },
            "dev_b42c91": {
                "created_at": "2026-07-28T14:11:03Z",
                "updated_at": "2026-09-01T17:58:12Z",
                "home_id": "home_7f3a92",
                "owner_id": "user_admin_001",
                "is_active": True,
                "type": "camera",
                "battery": 64,
                "name": "Cámara Entrada",
                "connection_by": "hub_001",
                "coords": {"lat": -34.6032, "long": -58.3809},
            },
            "dev_c73e15": {
                "created_at": "2026-08-02T09:45:27Z",
                "updated_at": "2026-09-01T18:05:31Z",
                "home_id": "home_7f3a92",
                "owner_id": "user_admin_001",
                "is_active": False,
                "type": "sensor",
                "battery": 31,
                "name": "Sensor Dormitorio",
                "connection_by": "-1",
                "coords": {"lat": -34.6041, "long": -58.3824},
            },
        }

    #==================================================
    # Device metrics (mock implementation)
    #==================================================

    def process_get_daily_metrics(self, authorization, device_id, date):
        # TODO: Verificar token, existencia del dispositivo y acceso al hogar
        # asociado antes de consultar las métricas diarias en el repository.
        metrics = self._get_mock_daily_metrics()
        metrics["id"] = date
        metrics["updated_at"] = f"{date}T23:59:59Z"
        return metrics

    def process_get_monthly_aggregates(self, authorization, device_id, month):
        # TODO: Verificar token y permisos, y consultar los agregados mensuales
        # calculados por el servidor mediante el repository correspondiente.
        aggregates = self._get_mock_monthly_aggregates()
        aggregates["id"] = month
        return aggregates

    def process_get_previous_month_aggregates(self, authorization, device_id):
        # TODO: Verificar token y permisos, calcular el mes calendario anterior
        # en el servidor y consultar sus agregados mediante el repository.
        aggregates = self._get_mock_monthly_aggregates()
        aggregates["id"] = "2026-08"
        return aggregates

    def process_get_last_week_metrics(self, authorization, device_id):
        # TODO: Verificar token y permisos, calcular el rango de siete días en
        # el servidor y consultar únicamente los días con datos existentes.
        first_day = self._get_mock_daily_metrics()
        first_day.update(
            {
                "id": "2026-08-31",
                "steps": 4010,
                "stumbles": 1,
                "time_lying_down": 7.8,
                "updated_at": "2026-08-31T23:59:59Z",
            }
        )
        second_day = self._get_mock_daily_metrics()
        return [first_day, second_day]

    @staticmethod
    def _get_mock_daily_metrics():
        return {
            "id": "2026-09-01",
            "steps": 4350,
            "falls": 0,
            "stumbles": 2,
            "time_lying_down": 8.5,
            "night_rises": 1,
            "panic_button": 0,
            "updated_at": "2026-09-01T23:59:59Z",
        }

    @staticmethod
    def _get_mock_monthly_aggregates():
        return {
            "id": "2026-09",
            "avg_steps": 4120.5,
            "avg_falls": 0.03,
            "avg_stumbles": 1.4,
            "avg_lying_down": 7.9,
            "avg_night_rises": 1.1,
            "total_panic_button_press": 0,
            "sedentarism_level": 45,
            "risk_level": 12,
            "active_days": 13,
        }

    #==================================================
    # Alarms (mock implementation)
    #==================================================

    def process_get_alarms_by_device_id(self, authorization, device_id):
        # TODO: Verificar token, existencia del dispositivo y acceso del
        # solicitante al hogar asociado antes de consultar el repository.
        return {
            "alarm_abc_123": {
                "name": "Ibuprofeno 400mg",
                "time_in_minutes": 480,
                "days": 127,
                "is_active": True,
                "state": "taken",
                "created_at": "2026-08-15T10:32:14Z",
                "updated_at": "2026-09-01T18:21:47Z",
            },
            "alarm_def_456": {
                "name": "Losartán 50mg",
                "time_in_minutes": 1200,
                "days": 127,
                "is_active": True,
                "state": "pending",
                "created_at": "2026-08-10T09:00:00Z",
                "updated_at": "2026-09-01T00:00:00Z",
            },
        }

    def process_set_alarms_by_device_id(
        self,
        authorization,
        device_id,
        alarms,
    ):
        # TODO: Verificar token y permisos de administración, validar la
        # máscara de días y persistir el reemplazo completo. Conservar o crear
        # state y timestamps desde el servidor, y actualizar estados por horario.
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
