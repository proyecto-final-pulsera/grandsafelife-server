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
        # TODO: Validar el token y los miembros recibidos; generar ID y fechas
        # y persistir el hogar. La app actualiza user.homes por separado.
        return "home_id_001"

    def process_update_home(self, authorization, home_id, home_data):
        # TODO: Verificar que el hogar exista y que el usuario autenticado tenga
        # permisos suficientes antes de persistir name y members; generar
        # updated_at en el servidor y conservar los campos omitidos.
        return None

    def process_delete_home(self, authorization, home_id):
        # TODO: Verificar rol administrador y eliminar el hogar.
        # La app desvincula miembros y dispositivos antes de esta operación.
        return None
