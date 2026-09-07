# Épicas de Grand Safe Life Server

Planificación local del proyecto. Los pasos de implementación se definen en [task.md](task.md) y se ejecutan únicamente cuando el usuario los solicita.

## Épicas pendientes

### E1. Modularización de la capa System

Dividir el `System` monolítico en módulos de casos de uso por área funcional,
conservando un punto de composición claro y evitando que FastAPI acceda
directamente a repositories, notificaciones o machine learning.

### E2. Identidad, autenticación y presencia

Verificar Firebase ID tokens, extraer el UID confiable y distinguir el tipo de
cliente que llama al servidor. Definir además qué significa keep-alive para cada
cliente: renovación de sesión, presencia o conectividad reciente.

### E3. Persistencia y reglas de negocio en Firebase

Diseñar el modelo de Firestore y sus repositories. Reemplazar progresivamente
los processors mock por casos de uso reales para usuarios, hogares, solicitudes
de monitoreo, dispositivos, métricas y alarmas.

### E4. Emparejamientos seguros

Resolver las asociaciones entre personas mayores, monitores, hubs y la
aplicación de la persona mayor. Los emparejamientos deben requerir autorización,
tener un ciclo de vida explícito y no confiar en IDs arbitrarios enviados por un
cliente.

### E5. Ingesta y procesamiento de actividad

Definir la API de la aplicación de la persona mayor para consultar alarmas,
enviar chunks de datos y consultar el resultado de su procesamiento. Integrar el
modelo de machine learning manteniendo aislado el estado de cada solicitud.

### E6. Eventos de caída y notificaciones

Registrar eventos detectados, determinar qué monitores deben ser avisados y
ofrecer a la app de Guido una API para consultar y marcar notificaciones. El
canal de entrega inmediata se definirá sin hacer depender el dato únicamente de
una notificación push.

### E7. Integración y calidad

Probar los recorridos completos, documentar los contratos, definir códigos de
operación faltantes y verificar concurrencia, errores y recuperación en una
escala menor a diez usuarios.

