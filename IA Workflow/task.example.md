# Tareas de la iteración — ejemplo

Copiar este archivo como `task.md` en esta carpeta y adaptarlo a la iteración.
`task.md` es local y no se versiona. Este ejemplo no autoriza ejecutar pasos.
Leer el backlog completo y ejecutar solo el paso solicitado por el usuario.

## Paso 1: Definir el contrato de un módulo

Épica relacionada: E1 de `epics.md`.

Alcance: documentar entrada, salida, errores y responsabilidades del módulo.
No implementar todavía la integración.

Resultado: un documento en `doc/dev_reports/` con nombre descriptivo.
Criterio de aceptación: contrato explícito y decisiones pendientes identificadas.

## Paso 2: Implementar el contrato acordado

Alcance: aplicar el contrato validado en el paso anterior y actualizar su documentación.
Criterio de aceptación: comprobar el caso exitoso y los errores relevantes,
conservando los contratos existentes fuera del alcance.

## Paso 3: Reportar la validación

Generar un reporte en `doc/tests_reports/` con alcance, pruebas, resultados y
pendientes. Este paso solicita expresamente un reporte; las pruebas rutinarias
no requieren un documento adicional.
