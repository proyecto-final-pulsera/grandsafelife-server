"""Configuración de rutas y respuestas de error de la API HTTP."""

import logging
import os

# HTTP
from flask import Flask, Response, request
from flask.logging import default_handler
from google.api_core.exceptions import NotFound as FirestoreNotFound
from werkzeug.exceptions import MethodNotAllowed, NotFound

# Endpoints
from .http_endpoints_users import UsersEndpoints
from .http_endpoints_homes import HomesEndpoints
from .http_endpoints_fall_detection import FallDetectionEndpoints
from .http_endpoints_devices import DevicesEndpoints
from .http_endpoints_devices_stats import DevicesStatsEndpoints
from .http_endpoints_alarms import AlarmsEndpoints
from .http_validation import RequestValidationError

# Recursos de negocio
from ..database.repositories.repository_users import UsersRepository
from ..database.repositories.repository_homes import HomesRepository
from ..database.repositories.repository_devices import DevicesRepository
from ..database.repositories.repository_devices_stats import DevicesStatsRepository
from ..database.repositories.repository_alarms import AlarmsRepository

# Helper para tests
class EmulatorErrorLog(logging.Filter):
    """Resume el error de actualización inexistente en el proyecto local de tests."""

    def filter(self, record):
        if record.exc_info:
            error = record.exc_info[1]
            if isinstance(error, RuntimeError) and isinstance(error.__cause__, FirestoreNotFound):
                record.msg = 'Firestore NotFound: el documento solicitado no existe. %s %s devuelve HTTP 500.'
                record.args = (request.method, request.path)
                record.exc_info = None
                record.exc_text = None
        return True

#==========================
# Configuración de HTTP Server
#==========================
def create_http_app(db, fall_detector, notifier_mng=None):
    """Crea la aplicación Flask, registra los endpoints y configura los errores HTTP."""
    app = Flask(__name__, static_folder=None)
    if (os.environ.get('GCLOUD_PROJECT') == 'demo-grandsafelife' and os.environ.get('FIRESTORE_EMULATOR_HOST') == '127.0.0.1:8080'):
        default_handler.addFilter(EmulatorErrorLog())

    app.config["PROVIDE_AUTOMATIC_OPTIONS"] = False
    app.register_blueprint(UsersEndpoints(UsersRepository(db)).blueprint)
    app.register_blueprint(HomesEndpoints(HomesRepository(db)).blueprint)
    app.register_blueprint(FallDetectionEndpoints(db, fall_detector, notifier_mng).blueprint)
    app.register_blueprint(DevicesEndpoints(DevicesRepository(db)).blueprint)
    app.register_blueprint(DevicesStatsEndpoints(DevicesStatsRepository(db)).blueprint)
    app.register_blueprint(AlarmsEndpoints(AlarmsRepository(db)).blueprint)

    # Deshabilitar HEAD: consulta los encabezados del recurso sin devolver body.
    for rule in app.url_map.iter_rules():
        rule.methods.discard("HEAD")

    # Frente a errores de validación se retorna 422 con la lista de errores en el campo detail.
    @app.errorhandler(RequestValidationError)
    def validation_error(error):
        return {"detail": error.errors}, 422

    # Si existe la URL pero no con el método indicado (GET, POST, PUT, etc) se retorna 405
    @app.errorhandler(MethodNotAllowed)
    def method_not_allowed(error):
        adapter = app.url_map.bind_to_environ(request.environ)
        for rule in app.url_map.iter_rules():
            for method in sorted(rule.methods):
                try:
                    matched, _ = adapter.match(method=method, return_rule=True)
                except (NotFound, MethodNotAllowed):
                    continue
                if matched == rule:
                    return {"detail": "Method Not Allowed"}, 405, {"Allow": ", ".join(sorted(rule.methods))}
        return {"detail": "Method Not Allowed"}, 405

    # Redirigir si sobra la barra final y existe la ruta; en otro caso, retornar 404.
    @app.errorhandler(NotFound)
    def not_found(error):
        if request.path.endswith("/"):
            adapter = app.url_map.bind_to_environ(request.environ)
            try:
                adapter.match(request.path.rstrip("/"), method=request.method)
            except NotFound:
                pass
            except MethodNotAllowed:
                return slash_redirect()
            else:
                return slash_redirect()
        return {"detail": "Not Found"}, 404

    # Solicitud de redirección a la misma URL sin barra final, conservando query string si existe.
    def slash_redirect():
        location = request.base_url.rstrip("/")
        if request.query_string:
            location += "?" + request.query_string.decode("latin-1")
        response = Response(status=307, headers={"Location": location})
        response.headers.pop("Content-Type", None)
        return response

    return app
