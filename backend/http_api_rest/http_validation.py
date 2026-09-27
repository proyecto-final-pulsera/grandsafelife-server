"""Mecanismo común de validación, invocado explícitamente por cada endpoint.
Cada endpoint aporta los modelos con las reglas de path, body y query string.
Exige la presencia de Authorization, sin verificar Bearer ni el token.
Devuelve los datos validados para continuar el flujo en la API.
Ante errores, lanza una excepción que el manejador HTTP convierte en 422."""

import json
from copy import deepcopy

from flask import request
from pydantic import ValidationError


JSON_INVALID_ERROR = {
    "type": "json_invalid",
    "loc": ["body"],
    "msg": "JSON decode error",
    "input": {},
    "ctx": {},
}


def _json_invalid(exc):
    """Copia la plantilla y agrega la posición y el motivo del JSON inválido."""
    error = deepcopy(JSON_INVALID_ERROR)
    error["loc"].append(exc.pos)
    error["ctx"]["error"] = exc.msg
    return error


class RequestValidationError(Exception):
    def __init__(self, errors):
        """Conserva la lista de errores que se devolverá en el campo detail."""
        self.errors = errors
        super().__init__("Invalid request")


def _missing(location):
    """Construye un error de campo obligatorio ausente en la ubicación indicada."""
    return {"type": "missing", "loc": location, "msg": "Field required", "input": None}


def _validate(model, value, source, errors):
    """Retorna el modelo validado o acumula sus errores con el origen path/body/query."""
    try:
        return model.model_validate(value, from_attributes=True)
    except ValidationError as exc:
        for error in exc.errors(include_url=False):
            error["loc"] = [source, *error["loc"]]
            # Un parámetro de query ausente se representa con input=None.
            if source == "query" and error["type"] == "missing":
                error["input"] = None
            errors.append(error)


def validate_request(*, body_model=None, query_model=None, path_model=None):
    """
    @brief Comprueba Authorization y valida path/body/query según los modelos del endpoint.
    @retval  retorna (auth, body, query).

    Path, body y query se validan solo si se proporciona su modelo. Ante errores,
    lanza RequestValidationError para impedir que el endpoint continúe.
    """
    errors = []
    body = query = None

    # Lectura del body y decodificación de JSON según el Content-Type.
    if body_model is not None:
        raw = request.get_data()
        if raw:
            if request.is_json:
                try:
                    body = json.loads(raw)
                except json.JSONDecodeError as exc:
                    raise RequestValidationError([_json_invalid(exc)]) from exc
            else:
                body = raw.decode("utf-8", errors="replace")

    # Validación de parámetros de la ruta.
    if path_model is not None:
        _validate(path_model, request.view_args, "path", errors)

    # Validación de query string en URL
    if query_model is not None:
        query = _validate(query_model, {key: request.args.getlist(key)[-1]
                                      for key in request.args}, "query", errors)

    # Comprobar que exista Authorization; no verificar Bearer ni el token.
    authorization = request.headers.get("Authorization")
    if authorization is None:
        errors.append(_missing(["header", "Authorization"]))

    # Validar la presencia del body y sus campos contra el modelo indicado.
    if body_model is not None:
        if body is None:
            errors.append(_missing(["body"]))
        else:
            body = _validate(body_model, body, "body", errors)

    # El manejador registrado en http.py convierte esta excepción en HTTP 422.
    if errors:
        raise RequestValidationError(errors)

    # Devolver los datos validados para que el endpoint continúe hacia App.
    return authorization, body, query
