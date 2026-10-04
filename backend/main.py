from .http_api_rest.http import create_http_app
from .app.app import App

from .database.database import initialize_firebase

initialize_firebase()
# El cliente Firestore se crea al ejecutar el primer proceso que lo necesita.
application = App(db=None)

app = create_http_app(application)
