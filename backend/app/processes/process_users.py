"""Procesamiento de usuarios autenticados mediante Cloud Firestore."""
from datetime import datetime, timezone
from ...database.database import get_firestore_client
from google.cloud.firestore_v1.base_query import FieldFilter


class UsersProcesses:
    def __init__(self, db=None):
        self._db = db

    @property
    def db(self):
        if self._db is None:
            self._db = get_firestore_client()
        return self._db

    @staticmethod
    def _user_data(document):
        if not document.exists:
            return None
        data = document.to_dict()
        data['id'] = document.id
        # El contrato HTTP expresa las fechas en milisegundos Unix.
        for field in ('created_at', 'updated_at'):
            if isinstance(data.get(field), datetime):
                data[field] = int(data[field].timestamp() * 1000)
        return data

    def process_get_user_by_id(self, user_id):
        try:
            return self._user_data(self.db.collection('users').document(user_id).get())
        except Exception as error:
            raise RuntimeError(f'Error fetching user: {error}') from error

    def process_get_user_by_email(self, email):
        try:
            documents = self.db.collection('users').where(
                filter=FieldFilter('email', '==', email)
            ).limit(1).get()
            return self._user_data(documents[0]) if documents else None
        except Exception as error:
            raise RuntimeError(f'Error fetching user by email: {error}') from error

    def process_create_user(self, user_data, user_id=None):
        try:
            data = dict(user_data)
            now = datetime.now(timezone.utc)
            data['created_at'] = now
            data['updated_at'] = now
            collection = self.db.collection('users')
            document = collection.document(user_id) if user_id else collection.document()
            document.set(data)
            return {'user_id': document.id}
        except Exception as error:
            raise RuntimeError(f'Error creating user: {error}') from error

    def process_update_user(self, user_id, user_data):
        try:
            data = dict(user_data)
            data['updated_at'] = datetime.now(timezone.utc)
            created_at = data.get('created_at')
            if isinstance(created_at, (int, float)) and not isinstance(created_at, bool):
                data['created_at'] = datetime.fromtimestamp(created_at / 1000, timezone.utc)
            self.db.collection('users').document(user_id).update(data)
        except Exception as error:
            raise RuntimeError(f'Error updating user: {error}') from error
