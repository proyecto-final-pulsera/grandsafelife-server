"""
@file api_op_codes.py
@author Grand Safe Life
@brief Códigos de operación y descripciones unívocas de la API.

El mapa se ampliará a medida que los endpoints necesiten representar nuevos
resultados.
"""

API_OP_OK = 0
API_OP_PROCESS_IN_PROGRESS = 1
API_OP_PROCESS_READY = 2
API_OP_PROCESS_NOT_FOUND = 3
API_OP_PROCESS_FAILED = 4

API_OP_BRIEFS = {
    API_OP_OK: "Operation completed successfully",
    API_OP_PROCESS_IN_PROGRESS: "Processing request in progress",
    API_OP_PROCESS_READY: "Processing result ready",
    API_OP_PROCESS_NOT_FOUND: "Processing request not found",
    API_OP_PROCESS_FAILED: "Processing request failed",
}

_NO_RESPONSE = object()


def get_api_op_brief(op_status: int) -> str:
    """Retorna la descripción unívoca asociada a un código de operación."""
    return API_OP_BRIEFS[op_status]


def build_api_response(op_status: int, resp=_NO_RESPONSE) -> dict:
    """Construye el envelope común de las respuestas HTTP de la aplicación."""
    response = {
        "op_status": op_status,
        "brief": get_api_op_brief(op_status),
    }
    if resp is not _NO_RESPONSE:
        response["resp"] = resp
    return response
