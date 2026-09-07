"""Procesamiento de devices; conserva los mocks y TODO existentes."""


class DevicesProcesses:
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
