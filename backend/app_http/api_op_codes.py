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


def get_api_op_brief(op_status: int) -> str:
    """Retorna la descripción unívoca asociada a un código de operación."""
    return API_OP_BRIEFS[op_status]
