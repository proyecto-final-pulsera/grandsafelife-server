"""
@file app_http.py
@author Grand Safe Life
@brief Construcción de la aplicación HTTP del servidor.

Este módulo ensambla los routers de cada área funcional y les inyecta el objeto
encargado de procesar las operaciones de la API.
"""

from fastapi import FastAPI

from .http_endpoints_alarms import AlarmsEndpoints
from .http_endpoints_devices import DevicesEndpoints
from .http_endpoints_devices_stats import DevicesStatsEndpoints
from .http_endpoints_homes import HomesEndpoints
from .http_endpoints_monitoring_requests import MonitoringRequestsEndpoints
from .http_endpoints_users import UsersEndpoints


def create_http_app(http_processor):
    """Crea la aplicación FastAPI con todos sus grupos de endpoints."""
    app = FastAPI(title="Grand Safe Life API", version="1.0.0")

    endpoint_groups = (
        UsersEndpoints(http_processor),
        HomesEndpoints(http_processor),
        MonitoringRequestsEndpoints(http_processor),
        DevicesEndpoints(http_processor),
        DevicesStatsEndpoints(http_processor),
        AlarmsEndpoints(http_processor),
    )

    for endpoint_group in endpoint_groups:
        app.include_router(endpoint_group.router)

    return app
