from .http_api_rest.http import create_http_app
from .app.app import App

# TODO: Inyectar la capa de Firebase cuando se implemente database/database.py.
application = App(db=None)

app = create_http_app(application)
