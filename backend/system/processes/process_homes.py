"""Procesamiento de homes; conserva los mocks y TODO existentes."""


class HomesProcesses:
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
