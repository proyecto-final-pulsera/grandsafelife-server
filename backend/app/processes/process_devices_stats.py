"""Consultas de métricas de dispositivos mediante Cloud Firestore."""
from datetime import datetime, timedelta, timezone
from google.cloud.firestore_v1.base_query import FieldFilter
from google.cloud.firestore_v1.field_path import FieldPath
from ...database.database import get_firestore_client


class DevicesStatsProcesses:
    def __init__(self, db=None):
        self._db = db

    @property
    def db(self):
        if self._db is None:
            self._db = get_firestore_client()
        return self._db

    def _metrics_collection(self, device_id, collection):
        return self.db.collection('devices_metrics').document(device_id).collection(collection)

    @staticmethod
    def _metrics_data(document):
        if not document.exists:
            return {}
        data = document.to_dict()
        data['id'] = document.id
        # La app REST convierte updated_at desde ISO 8601 a Timestamp.
        if isinstance(data.get('updated_at'), datetime):
            data['updated_at'] = data['updated_at'].astimezone(timezone.utc).isoformat().replace('+00:00', 'Z')
        return data

    def process_get_daily_metrics(self, device_id, date):
        try:
            document = self._metrics_collection(device_id, 'daily_metrics').document(date).get()
            return self._metrics_data(document)
        except Exception as error:
            raise RuntimeError(f'Error fetching daily metrics: {error}') from error

    def process_get_monthly_aggregates(self, device_id, month):
        try:
            document = self._metrics_collection(device_id, 'monthly_aggregates').document(month).get()
            return self._metrics_data(document)
        except Exception as error:
            raise RuntimeError(f'Error fetching monthly aggregates: {error}') from error

    def process_get_previous_month_aggregates(self, device_id):
        # Mes calendario anterior según la fecha local del servidor, incluido enero.
        now = datetime.now()
        previous_month = now.replace(day=1) - timedelta(days=1)
        month = f'{previous_month.year:04d}-{previous_month.month:02d}'
        return self.process_get_monthly_aggregates(device_id, month)

    def process_get_last_week_metrics(self, device_id):
        try:
            today = datetime.now().date()
            collection = self._metrics_collection(device_id, 'daily_metrics')
            # El filtro por ID de documento utiliza referencias de Firestore.
            last_seven_days = [
                collection.document((today - timedelta(days=index)).isoformat())
                for index in range(7)
            ]
            documents = collection.where(
                filter=FieldFilter(FieldPath.document_id(), 'in', last_seven_days)
            ).get()
            return [self._metrics_data(document) for document in sorted(documents, key=lambda doc: doc.id)]
        except Exception as error:
            raise RuntimeError(f'Error fetching last week metrics: {error}') from error
