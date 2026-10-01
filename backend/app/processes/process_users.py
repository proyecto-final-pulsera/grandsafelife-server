"""Procesamiento de users; conserva los mocks y TODO existentes."""


class UsersProcesses:
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
        # TODO: Verificar autenticación y permisos antes de consultar el repository.
        return {
            "id": user_id,
            "name": "María Gómez",
            "email": "maria.gomez@example.com",
            "avatar": "https://example.com/avatars/user_002.png",
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

    def process_get_user_by_email(self, authorization, email):
        # TODO: Verificar autenticación y permisos y buscar el UID por email.
        user = self.process_get_user_by_id(authorization, "user_002")
        return {**user, "email": email}

    def process_create_user(self, authorization, user_data):
        # TODO: Verificar el Firebase ID token, usar su UID como identificador y
        # persistir el perfil con timestamps del servidor y homes vacío.
        return {"user_id": "firebase_uid_mock"}

    def process_update_user(self, authorization, user_id, user_data):
        # TODO: Verificar el token y permisos sobre user_id y sus hogares;
        # persistir los campos recibidos y generar updated_at en el servidor.
        return None
