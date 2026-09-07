# FallDetection — contrato de integración

Este documento define el límite entre el detector y el servidor para desarrollar ambos en paralelo. El objetivo es integrar el módulo mediante su interfaz pública y configuración, sin modificar su implementación desde el servidor.

El modelo sigue en evaluación. Los sensores adicionales al acelerómetro, el formato definitivo del chunk y el pipeline pueden evolucionar; no se exige una arquitectura de ML específica.

## Interfaz del módulo

Conservamos la clase `FallDetection` y renombramos `detectar_caida` a `detect_fall(data)`. El contrato principal es síncrono: **entra un chunk y la misma llamada devuelve su clasificación o un error de procesamiento**.

```python
from dataclasses import dataclass
from typing import Any


@dataclass
class FallDetectionResult:
    is_fall_detected: bool | None
    error_code: str | None


class FallDetection:
    def detect_fall(self, data: Any) -> FallDetectionResult:
        """Clasifica un chunk. Formato de entrada pendiente de definición."""
        ...
```

| Resultado | `is_fall_detected` | `error_code` |
| --- | --- | --- |
| Caída detectada | `True` | `None` |
| Sin caída | `False` | `None` |
| Entrada inválida | `None` | `"INVALID_DATA"` |
| Fallo de procesamiento | `None` | Código de error documentado |

- Este resultado reemplaza el retorno actual `(pred, res)`. La probabilidad y los arreglos internos no son necesarios para el servidor.
- En éxito, `error_code` es `None`; no se usa `"OK"`. En error, `is_fall_detected` es `None`. No devolver combinaciones contradictorias ni un `None` en lugar de `FallDetectionResult`.
- Los errores gestionados de validación e inferencia se expresan mediante `error_code`. Un fallo de inicialización que impida construir el detector debe producir una excepción explícita. El servidor también debe gestionar excepciones inesperadas.
- Se conservan `set_threshold` y `get_last_result`. El servidor consume el retorno de cada llamada, nunca el último resultado compartido.
- Cada instancia debe mantener separados sus datos de procesamiento. Documentar restricciones de concurrencia y recursos compartidos; el servidor garantizará una llamada activa por instancia.

El ejemplo describe la interfaz a preparar, no la implementación actual. El nombre final del paquete y cualquier cambio del contrato se acuerdan antes de incorporarlos.

## Responsabilidades del servidor

La asincronía pertenece al servidor:

1. La app envía un chunk por POST y recibe ACK con un identificador de pedido.
2. El servidor administra la espera y ejecuta `detect_fall(data)`.
3. La app consulta por GET: `IN_PROGRESS`, `READY` con resultado o `NOT_FOUND`. Se contempla `FAILED` para errores de procesamiento.
4. Si hubo caída, el servidor inicia las notificaciones correspondientes sin depender del polling.

El servidor administra autenticación, permisos, pedidos, resultados, reintentos y notificaciones. También decide cuántas instancias crear y cómo asignarles trabajo. El detector no necesita implementar HTTP, colas, polling ni envío de avisos.

## Organización esperada

```text
fall_detector/
    __init__.py             # Expone FallDetection y FallDetectionResult.
    fall_detection.py
    data_pipeline.py
    utils.py                # Solo utilidades de inferencia.
    models/                 # Artefactos de la versión elegida.
test/
    main.py                 # Ejecución manual.
    api_example.py          # API de prueba, si se conserva.
    data_input.py           # Adquisición alternativa y lectura de datasets.
    evaluation.py           # Métricas y evaluación.
    fixtures/               # Chunks reproducibles.
requirements.txt            # Dependencias del módulo.
README.md
```

El pipeline y sus utilidades son parte del módulo. En el código actual, `utils.py` mezcla esas funciones con `matriz_confusion` e imports de evaluación: separar estos últimos en `test/`.

El `main.py` actual, la API de demostración y `data_input.py` corresponden a `test/`, junto con sus dependencias y entorno de ejecución. Pueden seguir versionados. El módulo productivo no debe importar código de pruebas.

## Condiciones para una entrega integrable

- **Importación autónoma:** importar el paquete no inicia servidores, adquisición de datos ni pruebas. Los imports internos no dependen del nombre genérico `app` del proyecto que lo consume.
- **Recursos localizables:** resolver modelos respecto del paquete o mediante configuración explícita, sin depender del directorio desde el que se ejecuta el servidor.
- **Versión reproducible:** indicar Python, dependencias probadas y cómo obtener los artefactos exactos que requiere esa versión. Si se versionan modelos o fixtures JSON, revisar las exclusiones actuales de `.gitignore`.
- **Entrada documentada por versión:** incluir esquema del chunk, unidades, frecuencias y longitudes admitidas, con un ejemplo válido. Estos detalles pueden cambiar durante la investigación; deben acompañar cada versión que se entregue para integrar.
- **Verificación mínima:** poder cargar el detector desde otro directorio, procesar chunks consecutivos y comprobar las combinaciones de éxito y error de `FallDetectionResult`. La evaluación predictiva del modelo es independiente de esta verificación de integración.

## Trabajo en paralelo y commits

Cada commit debería tener un propósito revisable. Separar movimientos de archivos de cambios en el algoritmo cuando sean independientes, e incluir los ajustes de imports junto con cada reorganización.

Si cambia la interfaz, el esquema del chunk o una dependencia, acordarlo con quien integra y actualizar el README y los ejemplos en el mismo cambio. Si un modelo requiere una versión específica del pipeline, entregar y documentar ambos juntos.

Antes de entregar, revisar que estén todos los recursos necesarios y que no se incluyan entornos locales, cachés, datasets o salidas generadas por accidente. Con una versión identificable y un ejemplo reproducible, el servidor debería poder incorporar el módulo sin editar sus archivos internos.
