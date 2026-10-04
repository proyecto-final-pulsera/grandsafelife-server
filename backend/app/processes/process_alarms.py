"""Lectura y reemplazo de alarmas de dispositivos mediante Cloud Firestore."""
from datetime import datetime, timezone
from ...database.database import get_firestore_client


class AlarmsProcesses:
    def __init__(self, db=None):
        self._db = db

    @property
    def db(self):
        if self._db is None:
            self._db = get_firestore_client()
        return self._db

    def process_get_alarms_by_device_id(self, device_id):
        try:
            document = self.db.collection('alarms').document(device_id).get()
            if not document.exists:
                return {}
            alarms = document.to_dict() or {}
            for alarm in alarms.values():
                for field in ('created_at', 'updated_at'):
                    if isinstance(alarm.get(field), datetime):
                        alarm[field] = int(alarm[field].timestamp() * 1000)
            return alarms
        except Exception as error:
            raise RuntimeError(f'Error fetching alarms: {error}') from error

    def process_set_alarms_by_device_id(self, device_id, alarms):
        try:
            data = {}
            for alarm_id, alarm in alarms.items():
                data[alarm_id] = dict(alarm)
                for field in ('created_at', 'updated_at'):
                    value = data[alarm_id].get(field)
                    if isinstance(value, (int, float)) and not isinstance(value, bool):
                        data[alarm_id][field] = datetime.fromtimestamp(value / 1000, timezone.utc)
            # Reemplazo completo, incluido {}; no se generan fechas ni estados.
            self.db.collection('alarms').document(device_id).set(data)
        except Exception as error:
            raise RuntimeError(f'Error setting alarms: {error}') from error
