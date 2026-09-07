# Épicas del proyecto — ejemplo

Copiar este archivo como `epics.md` en esta carpeta y adaptarlo al proyecto.
`epics.md` es local y no se versiona. Las épicas describen objetivos amplios;
sus pasos ejecutables se definen en `task.md` y requieren el pedido del usuario.

## E1. Integración de un módulo

Objetivo: incorporar un módulo mediante una interfaz estable, sin editar sus
detalles internos desde el componente que lo consume.

Alcance: acordar contratos, dependencias, manejo de errores y verificar la integración.
Fuera de alcance: cambios del algoritmo interno que no requiera la integración.

Criterio de cierre: integración reproducible y contratos documentados.
Pendientes: identificar las decisiones técnicas todavía abiertas.

## E2. Validación del flujo completo

Objetivo: verificar el recorrido entre la entrada del sistema y su resultado.
Alcance: escenarios exitosos, errores y recuperación relevantes.
Criterio de cierre: escenarios verificables y pendientes registrados.
