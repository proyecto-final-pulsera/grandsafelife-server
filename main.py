"""Punto de entrada HTTP de Firebase Functions."""

from io import BytesIO

from firebase_functions import https_fn, options


@https_fn.on_request(
    region="us-central1",
    min_instances=0,
    max_instances=10,
    concurrency=1,
    cpu=1,
    memory=options.MemoryOption.GB_1,
    timeout_sec=60,
)
def api(req: https_fn.Request) -> https_fn.Response:
    """Entrega la petición a la aplicación HTTP del backend."""
    # Firebase importa este archivo localmente durante el deploy para descubrir la función.
    # Importar el backend acá difiere la inicialización de Firestore hasta la primera
    # petición, cuando la función desplegada puede usar su cuenta de servicio.
    from backend.main import app as _app

    # Cada contexto lee su propio flujo; el request externo conserva el body en caché.
    environ = req.environ.copy()
    environ["wsgi.input"] = BytesIO(req.get_data())
    with _app.request_context(environ):
        return _app.full_dispatch_request()
