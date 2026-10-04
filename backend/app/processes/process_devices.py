"""Procesamiento de dispositivos autenticados mediante Cloud Firestore."""
from datetime import datetime, timezone
from google.cloud.firestore_v1.base_query import FieldFilter
from ...database.database import get_firestore_client


class DevicesProcesses:
    def __init__(self, db=None):
        self._db = db

    @property
    def db(self):
        if self._db is None:
            self._db = get_firestore_client()
        return self._db

    @staticmethod
    def _device_data(document):
        if not document.exists:
            return None
        data = document.to_dict()
        data['id'] = document.id
        for field in ('created_at', 'updated_at'):
            if isinstance(data.get(field), datetime):
                data[field] = int(data[field].timestamp() * 1000)
        return data

    def process_create_device(self, device_data, device_id=None):
        try:
            data = dict(device_data)
            now = datetime.now(timezone.utc)
            data['created_at'] = now
            data['updated_at'] = now
            collection = self.db.collection('devices')
            document = collection.document(device_id) if device_id else collection.document()
            document.set(data)
            return document.id
        except Exception as error:
            raise RuntimeError(f'Error creating device: {error}') from error

    def process_get_device_by_id(self, device_id):
        try:
            return self._device_data(self.db.collection('devices').document(device_id).get())
        except Exception as error:
            raise RuntimeError(f'Error fetching device: {error}') from error

    def process_update_device(self, device_id, device_data):
        try:
            data = dict(device_data)
            data['updated_at'] = datetime.now(timezone.utc)
            created_at = data.get('created_at')
            if isinstance(created_at, (int, float)) and not isinstance(created_at, bool):
                data['created_at'] = datetime.fromtimestamp(created_at / 1000, timezone.utc)
            self.db.collection('devices').document(device_id).update(data)
        except Exception as error:
            raise RuntimeError(f'Error updating device: {error}') from error

    def process_delete_device(self, device_id):
        try:
            # Elimina solo el documento, sin borrar sus subcolecciones.
            self.db.collection('devices').document(device_id).delete()
        except Exception as error:
            raise RuntimeError(f'Error deleting device: {error}') from error

    def _query_devices(self, field, value):
        documents = self.db.collection('devices').where(
            filter=FieldFilter(field, '==', value)
        ).get()
        # La API REST devuelve un mapa por ID; la app lo convierte en lista.
        return {document.id: self._device_data(document) for document in documents}

    def process_get_devices_by_owner(self, owner_id):
        try:
            return self._query_devices('owner_id', owner_id)
        except Exception as error:
            raise RuntimeError(f'Error querying devices: {error}') from error

    def process_get_devices_by_home(self, home_id):
        try:
            return self._query_devices('home_id', home_id)
        except Exception as error:
            raise RuntimeError(f'Error querying devices by home: {error}') from error

    def process_get_device_location(self, device_id):
        try:
            document = self.db.collection('devices').document(device_id).get()
            if not document.exists:
                return None
            return document.to_dict().get('coords')
        except Exception as error:
            raise RuntimeError(f'Error fetching device location: {error}') from error
