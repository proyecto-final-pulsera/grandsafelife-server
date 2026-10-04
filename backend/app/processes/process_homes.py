"""Procesamiento de hogares autenticados mediante Cloud Firestore."""
from datetime import datetime, timezone
from ...database.database import get_firestore_client


class HomesProcesses:
    def __init__(self, db=None):
        self._db = db

    @property
    def db(self):
        if self._db is None:
            self._db = get_firestore_client()
        return self._db

    def process_get_home_by_id(self, home_id):
        try:
            document = self.db.collection('homes').document(home_id).get()
            if not document.exists:
                return None
            data = document.to_dict()
            data['id'] = document.id
            # El contrato HTTP expresa las fechas en milisegundos Unix.
            for field in ('created_at', 'updated_at'):
                if isinstance(data.get(field), datetime):
                    data[field] = int(data[field].timestamp() * 1000)
            return data
        except Exception as error:
            raise RuntimeError(f'Error fetching home: {error}') from error

    def process_create_home(self, home_data, home_id=None):
        try:
            data = dict(home_data)
            now = datetime.now(timezone.utc)
            data['created_at'] = now
            data['updated_at'] = now
            collection = self.db.collection('homes')
            document = collection.document(home_id) if home_id else collection.document()
            document.set(data)
            return document.id
        except Exception as error:
            raise RuntimeError(f'Error creating home: {error}') from error

    def process_update_home(self, home_id, home_data):
        try:
            data = dict(home_data)
            data['updated_at'] = datetime.now(timezone.utc)
            created_at = data.get('created_at')
            if isinstance(created_at, (int, float)) and not isinstance(created_at, bool):
                data['created_at'] = datetime.fromtimestamp(created_at / 1000, timezone.utc)
            self.db.collection('homes').document(home_id).update(data)
        except Exception as error:
            raise RuntimeError(f'Error updating home: {error}') from error

    def process_delete_home(self, home_id):
        try:
            # Firestore elimina solo el documento; no sus subcolecciones.
            self.db.collection('homes').document(home_id).delete()
        except Exception as error:
            raise RuntimeError(f'Error deleting home: {error}') from error
