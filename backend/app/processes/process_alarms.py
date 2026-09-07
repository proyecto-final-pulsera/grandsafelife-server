"""Procesamiento de alarms; conserva los mocks y TODO existentes."""


class AlarmsProcesses:
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
