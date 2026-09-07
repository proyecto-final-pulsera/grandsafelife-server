"""Contrato de detección; importar el paquete no carga el modelo externo."""

from .model import FallDetection, FallDetectionResult

__all__ = ["FallDetection", "FallDetectionResult"]
