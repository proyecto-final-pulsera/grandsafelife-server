from app_http.app_http import create_http_app
from system.system import System
from backend.database.usersDB.database import DataBase

db = DataBase()
system = System(db)

app = create_http_app(system)