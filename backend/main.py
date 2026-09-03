from app_http.app_http import create_http_app
from system.system import System

# TODO: Inyectar la capa de Firebase cuando se implemente database/database.py.
system = System(db=None)

app = create_http_app(system)
