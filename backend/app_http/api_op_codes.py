"""
@file api_op_codes.py
@author Grand Safe Life
@brief Códigos de operación y descripciones unívocas de la API.

El mapa se ampliará a medida que los endpoints necesiten representar nuevos
resultados.
"""

API_OP_OK = 0

API_OP_BRIEFS = {
    API_OP_OK: "Operation completed successfully",
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
