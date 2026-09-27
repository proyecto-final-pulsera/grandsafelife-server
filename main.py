"""Punto de entrada HTTP de Firebase Functions."""

from firebase_functions import https_fn, options

from backend.main import app as _app


@https_fn.on_request(
    region="us-central1",
    min_instances=0,
    max_instances=10,
    concurrency=1,
    cpu=1,
    memory=options.MemoryOption.MB_256,
    timeout_sec=60,
)
def api(req: https_fn.Request) -> https_fn.Response:
    """Entrega la petición a la aplicación HTTP del backend."""
    with _app.request_context(req.environ):
        return _app.full_dispatch_request()
