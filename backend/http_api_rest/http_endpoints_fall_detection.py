"""Contratos HTTP de detección de caídas; integración con process_* pendiente."""

from typing import Annotated, Literal

from fastapi import APIRouter, Header, Path
from pydantic import BaseModel, ConfigDict, Field, JsonValue, RootModel

from .api_op_codes import (
    API_OP_OK,
    API_OP_PROCESS_FAILED,
    API_OP_PROCESS_IN_PROGRESS,
    API_OP_PROCESS_NOT_FOUND,
    API_OP_PROCESS_READY,
    build_api_response,
)


class FallDetectionInput(RootModel[dict[str, JsonValue]]):
    """Objeto JSON crudo provisional; el esquema del chunk está por definir."""


class RequestReference(BaseModel):
    model_config = ConfigDict(extra="forbid")

    request_id: int = Field(gt=0)


class FallDetectionResultResponse(RequestReference):
    is_fall: bool


class FallDetectionErrorResponse(RequestReference):
    error_code: str = Field(min_length=1)


class AcceptedResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    op_status: Literal[API_OP_OK]
    brief: str
    resp: RequestReference


class InProgressResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    op_status: Literal[API_OP_PROCESS_IN_PROGRESS]
    brief: str
    resp: RequestReference


class ReadyResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    op_status: Literal[API_OP_PROCESS_READY]
    brief: str
    resp: FallDetectionResultResponse


class NotFoundResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    op_status: Literal[API_OP_PROCESS_NOT_FOUND]
    brief: str
    resp: RequestReference


class FailedResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    op_status: Literal[API_OP_PROCESS_FAILED]
    brief: str
    resp: FallDetectionErrorResponse


AuthorizationHeader = Annotated[str, Header(alias="Authorization")]
RequestId = Annotated[int, Path(gt=0)]


class FallDetectionEndpoints:
    """Expone rutas con respuestas fijas hasta implementar los casos de uso."""

    def __init__(self, http_processor):
        self.http_processor = http_processor
        self.router = APIRouter(
            prefix="/grandsafelife/api/v1/fall-detection/requests",
            tags=["fall-detection"],
        )
        self._register_routes()

    def _register_routes(self):
        @self.router.post("", response_model=AcceptedResponse)
        def create_fall_detection_request(
            request: FallDetectionInput,
            authorization: AuthorizationHeader,
        ):
            # TODO: Quitar el bypass cuando se implemente el caso de uso.
            # result = self.http_processor.process_create_fall_detection_request(
            #     authorization, request.model_dump()
            # )
            # Respuesta fija: todavía no se registra ni procesa ningún pedido.
            return build_api_response(API_OP_OK, {"request_id": 1})

        @self.router.get(
            "/{request_id}",
            response_model=InProgressResponse | ReadyResponse,
            responses={
                400: {"model": NotFoundResponse},
                500: {"model": FailedResponse},
            },
        )
        def get_fall_detection_request(
            request_id: RequestId,
            authorization: AuthorizationHeader,
        ):
            # TODO: Quitar el bypass cuando se implemente el caso de uso.
            # result = self.http_processor.process_get_fall_detection_request(
            #     authorization, request_id
            # )
            # Traducir su resultado: IN_PROGRESS/READY -> 200,
            # NOT_FOUND -> 400, FAILED -> 500 (fallo interno de procesamiento).
            # Respuesta fija: cualquier ID válido permanece en curso.
            return build_api_response(
                API_OP_PROCESS_IN_PROGRESS, {"request_id": request_id}
            )
