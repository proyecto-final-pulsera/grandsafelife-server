"""Procesamiento de alarms; conserva los mocks y TODO existentes."""

from datetime import datetime, timezone

class AlarmsProcesses:
    def process_get_alarms_by_device_id(self, device_id):
        # La autenticación y los permisos corresponden al blueprint del endpoint.
        # TODO: Consultar el documento de alarmas en el repository y retornar {}
        # si no existe, conservando las fechas en milisegundos Unix.

        """
        @override
        Future<Map<String, dynamic>> getAlarmsByDeviceId(String deviceId) async {
            try {
            final doc = await _firestore.collection('alarms').doc(deviceId).get();
            if (!doc.exists) return {};
            return doc.data() ?? {};
            } catch (e) {
            throw Exception('Error fetching alarms: $e');
            }
        }
        """
        return {
            "alarm_abc_123": {
                "name": "Ibuprofeno 400mg",
                "time_in_minutes": 480,
                "days": 127,
                "is_active": True,
                "state": "taken",
                "created_at": int(datetime(2026, 8, 15, 10, 32, 14, tzinfo=timezone.utc).timestamp() * 1000),
                "updated_at": int(datetime(2026, 9, 1, 18, 21, 47, tzinfo=timezone.utc).timestamp() * 1000),
            },
            "alarm_def_456": {
                "name": "Losartán 50mg",
                "time_in_minutes": 1200,
                "days": 127,
                "is_active": True,
                "state": "pending",
                "created_at": int(datetime(2026, 8, 10, 9, tzinfo=timezone.utc).timestamp() * 1000),
                "updated_at": int(datetime(2026, 9, 1, tzinfo=timezone.utc).timestamp() * 1000),
            },
        }

    def process_set_alarms_by_device_id(self, device_id, alarms):
        # La autenticación y los permisos corresponden al blueprint del endpoint.
        # TODO: Persistir el reemplazo completo en el repository, incluido {}.
        # Conservar state y fechas enviados por la app como en el set original.

        """
        @override
        Future<void> setAlarmsByDeviceId(
            String deviceId,
            Map<String, dynamic> alarms,
        ) async {
            try {
            await _firestore.collection('alarms').doc(deviceId).set(alarms);
            } catch (e) {
            throw Exception('Error setting alarms: $e');
            }
        }
        """

        # Mock de escritura: responde éxito sin persistir ni modificar alarmas.
        return None
