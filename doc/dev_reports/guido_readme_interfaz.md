# Cambios realizados en el módulo de detección de caídas

- **Separación de responsabilidades:** el código de inferencia y los artefactos
  quedaron en `app/`; adquisición, evaluación y ejecución manual pasaron a `test/`.
- **Interfaz pública:** el `__init__.py` raíz exporta `FallDetection` y
  `FallDetectionResult`. `detectar_caida` pasó a llamarse `detect_fall` y devuelve
  clasificación o error explícito, reemplazando la tupla de predicción y probabilidad.
- **Carga e imports:** imports relativos y carga diferida de modelos desde rutas
  del paquete o un directorio configurable, sin iniciar servicios al importar.
- **Mock temporal:** `detect_fall` retorna sin caída desde el bloque
  `TODO: MOCK PROCESAMIENTO`. Eliminar ese bloque habilita el camino real.
- **Validaciones y errores:** se agregaron controles provisionales de entrada,
  validación del umbral y resultados coherentes. Los fallos de procesamiento ya
  no retornan `None`; actualizan también el último resultado de la instancia.
- **Pipeline:** se corrigió la comprobación de valores ausentes y el cálculo de
  factores enteros para remuestreo. No se cambiaron los pesos ni la fusión de modelos.
- **Herramientas:** la API de demostración se reemplazó por un comando manual;
  se eliminaron Dockerfile y .dockerignore. Se separaron las dependencias de uso
  y evaluación y se habilitó versionar modelos y fixtures JSON.
- **Documentación y pruebas:** se agregaron README del módulo y de pruebas, más
  verificaciones del contrato público, mock, rutas y umbral.

El servidor incorpora el repositorio como submódulo en `backend/fall_detection/model`
y consume su interfaz directamente, sin una clase abstracta ni un mock separados.

El esquema definitivo de entrada sigue pendiente. También falta el artefacto
barométrico para verificar inferencia real; las pruebas actuales no evalúan la
precisión del modelo. La API de uso está en el
[README del módulo](../../backend/fall_detection/model/README.md).
