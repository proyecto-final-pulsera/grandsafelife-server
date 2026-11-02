from .http_api_rest.http import create_http_app

from .database.database import get_firestore_client
from .fall_detection.model import FallDetection
from .notifications.notifications import Notifications

db = get_firestore_client()
fall_detector = FallDetection()
notifier_mng = Notifications()

app = create_http_app(db=db, fall_detector=fall_detector, notifier_mng=notifier_mng)
