"""Configuración de rutas y respuestas de error de la API HTTP."""

from flask import Flask, Response, request
from werkzeug.exceptions import MethodNotAllowed, NotFound

from .http_endpoints_users_flask import UsersEndpoints
from .http_endpoints_monitoring_requests_flask import MonitoringRequestsEndpoints
from .http_endpoints_homes_flask import HomesEndpoints
from .http_endpoints_fall_detection_flask import FallDetectionEndpoints
from .http_endpoints_devices_flask import DevicesEndpoints
from .http_validation import RequestValidationError

def create_http_app(http_processor):
    """Crea la aplicación Flask, registra los endpoints y configura los errores HTTP."""
    app = Flask(__name__, static_folder=None)
    app.config["PROVIDE_AUTOMATIC_OPTIONS"] = False
    app.register_blueprint(UsersEndpoints(http_processor).blueprint)
    app.register_blueprint(MonitoringRequestsEndpoints(http_processor).blueprint)
    app.register_blueprint(HomesEndpoints(http_processor).blueprint)
    app.register_blueprint(FallDetectionEndpoints(http_processor).blueprint)
    app.register_blueprint(DevicesEndpoints(http_processor).blueprint)

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
