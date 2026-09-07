# Paso 1 readme guido
Ese readme que sirve para guido metelo en la carpeta doc con el nombre "guido_readme_modularizacion.md".
Agregale la correccion puntual de en vez de llamarse detectar_caida sea detect_fall(data)

Particularmente la interfaz la pondría asi:

from dataclasses import dataclass
from typing import Any

@dataclass class FallDetectionResult:
is_fall_detected: bool | None
error_code: str | None  


class FallDetection: def detect_fall(self, data: Any) -> FallDetectionResult: 
""" 
Determina si los datos de entrada representan o no una caida.
```yaml
    Args:
        data: TODO: falta definir formato entrada

    Returns:
        FallDetectionResult:
            - is_fall_detected True si fue una caida, so false.
            - op_code OK | INVALID_DATA | ERROR_X
    """
```

# Paso 2 Carpeta no versionada

Por otro lado actualiazar AGENTS.md para que en la carpeta "IA Workflow" esté el archivo task.md ahí dentro pondría el archivo de épicas que ahora se llama README.md lo cambiaría a epics.md.

# Paso 3: evaluar docker
Por otro lado, no se si sea buena idea o no, pero lo que esté relacioando con docker lo pondría también en su carpoeta.

Lo que son los códigos fuente ahora en backend lo renombraría a sources/

# Paso 4: Carpeta para reportes utiles
Agregaría una carpeta llamada doc/tests_reports/ donde la idea es que aca pongamos los reportes del testeo de cada módulo si lo considero relevante. Generalmente en task.md a veces pongo un paso que sea específico de testear algo en particular o si surge algun bug que corresponda documentar. La idea es que vaya directo ahí.

# Paso 5 actualizar git ignore
En el git ignore pondría que se ignore esta nueva carpeta IA Workflow (además de modificar su paradigma, yo haría que ingore absolutamente todo menos las carpetas especificadas, en nuestro caso, sources, docker y doc)

# Paso 6: Eliminar archivos no versionables del repo
Finalmente eliminaría del repo los archivos viejos.