from .http_api_rest.http import create_http_app

from .database.database import get_firestore_client
from .fall_detection.model import FallDetection

db = get_firestore_client()
fall_detector = FallDetection()

app = create_http_app(db=db, fall_detector=fall_detector, notifier_mng=None)
