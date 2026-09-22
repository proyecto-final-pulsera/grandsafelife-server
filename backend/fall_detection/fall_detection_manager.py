"""Contrato del manager de detección; ejecución interna todavía mockeada."""

from dataclasses import dataclass
from enum import Enum
from typing import Any

from .model import FallDetectionResult


class ProcessingStatus(str, Enum):
    IN_PROGRESS = "IN_PROGRESS"
    READY = "READY"
    FAILED = "FAILED"
    NOT_FOUND = "NOT_FOUND"


@dataclass(frozen=True)
class ProcessingResult:
    """Resultado de una consulta; NOT_FOUND no es un estado persistido."""

    request_id: int
    status: ProcessingStatus
    result: FallDetectionResult | None = None

    def __post_init__(self):
        if type(self.request_id) is not int or self.request_id <= 0:
            raise ValueError("request_id debe ser un entero positivo.")
        if not isinstance(self.status, ProcessingStatus):
            raise ValueError("Estado de procesamiento inválido.")
        if self.status in (ProcessingStatus.IN_PROGRESS, ProcessingStatus.NOT_FOUND):
            if self.result is not None:
                raise ValueError("Un pedido pendiente o inexistente no tiene resultado.")
        elif not isinstance(self.result, FallDetectionResult):
            raise ValueError("READY y FAILED requieren un resultado del detector.")
        elif (self.status == ProcessingStatus.READY) != (self.result.error_code is None):
            raise ValueError("El estado no coincide con el resultado del detector.")


class FallProcessorManager:
    """API provisional ejecutable, sin cola, persistencia ni inferencia real."""

    # TODO: Crear N detectores y admitir una llamada activa por instancia.
    # TODO: Generar IDs únicos, registrar pedidos y asignar trabajo disponible.
    # TODO: Mantener resultados por ID y traducir excepciones a FAILED.
    # TODO: Definir capacidad, sincronización, cierre y recuperación tras fallos.
    # TODO: Acordar retención/expiración y asociación del pedido con el contexto
    # autenticado que controla app. Este manager no decide permisos.
    # La concurrencia y el ciclo de vida se implementarán en la épica E5.

    def __init__(self, N: int = 1):
        if type(N) is not int or N <= 0:
            raise ValueError("N debe ser un entero positivo.")
        self.N = N
        print("TODO: FallProcessorManager sin implementar; no se crean detectores.")

    def appendNewProcessData(self, data: Any) -> int:
        """Recibe un chunk deserializado y retorna el ID; hoy siempre retorna 1."""
        # TODO: Registrar y encolar data; no ejecutar inferencia en esta llamada.
        print("TODO: appendNewProcessData sin implementar; se devuelve un ID mock.")
        return 1

    def getResultById(self, request_id: int) -> ProcessingResult:
        """Consulta un ID; hoy retorna READY sin caída para cualquier ID válido."""
        # TODO: Consultar el registro real: IN_PROGRESS, READY, FAILED o NOT_FOUND.
        print("TODO: getResultById sin implementar; se devuelve un resultado mock.")
        return ProcessingResult(
            request_id=request_id,
            status=ProcessingStatus.READY,
            result=FallDetectionResult(False, None),
        )
