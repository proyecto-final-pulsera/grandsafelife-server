# Grand Safe Life Server - AGENT.md

## Descripción

Grand Safe Life Server es el backend principal del proyecto Grand Safe Life.

Su responsabilidad es gestionar usuarios, hogares, dispositivos, relaciones de
monitoreo, métricas, alarmas, eventos y notificaciones.

Es un proyecto académico y didáctico. Durante la materia se lo trata como si
fuera un producto real para practicar decisiones y buenas prácticas de
ingeniería, pero no es un producto final ni necesita resolver anticipadamente
problemas propios de una plataforma de gran escala.

La aplicación móvil nunca debe acceder directamente a Firebase ni conocer cómo
se almacenan los datos. La API REST es la única interfaz entre cualquier cliente
y el servidor.

---

## Dirección actual del proyecto

La interfaz `DataSource` y los contratos JSON definidos para la aplicación de
Guido se utilizan como punto de partida para diseñar la API. No constituyen una
especificación incuestionable ni representan la totalidad de las funciones del
servidor.

Al definir la API:

* Conservar los contratos esperados por la aplicación cuando sean razonables.
* Adaptarlos cuando expongan detalles internos de persistencia o contradigan las reglas del negocio.
* No convertir en endpoints responsabilidades locales del cliente, como inicializar una conexión.
* No permitir que el cliente tome decisiones que corresponden al servidor, como elegir identificadores internos o timestamps de auditoría.
* Diseñar también los endpoints faltantes, aunque no estén incluidos en la interfaz inicial de Guido.

E1 — Migración de backend actual a Cloud Functions conserva el comportamiento
ejecutable registrado en `backend/tests/http_reference.json`. No rediseñar los
contratos durante esta migración. La capa HTTP vive en `backend/http_api_rest`.

El alcance inicial contempla menos de diez usuarios. Las decisiones deben ser
correctas y defendibles, pero proporcionales a esa escala. Se priorizan una
implementación clara, verificable y fácil de explicar por sobre infraestructura
distribuida o abstracciones destinadas a una escala hipotética.

---

## Arquitectura

```text
Aplicación móvil u otro cliente
              |
              v
      Cloud Function HTTP `api`
              |
              v
        API REST (Flask)
              |
              v
       App / negocio
       /       |       \
      v        v        v
Firebase  Notifications  Machine Learning
```

La división en capas debe conservarse. Cada capa tiene una responsabilidad específica y no debe filtrar detalles internos hacia las demás.

La arquitectura objetivo es un monolito modular alojado en una única función
HTTP, con Flask para el enrutamiento y Pydantic para validar. E1 mantiene los
mocks actuales, sin persistencia, autenticación, FCM ni inferencia real.
Compartir un despliegue no autoriza a mezclar responsabilidades.

La transición se ejecuta por pasos: FastAPI y Docker permanecen como referencia
hasta completar su reemplazo y validación local. No retirarlos anticipadamente.

---

## Estructura del proyecto

```text
backend
|
|-- http_api_rest
|-- database
|-- fall_detection
|-- notifications
`-- app
    `-- domain
```

---

## Responsabilidades por módulo

### http_api_rest

Importar esta capa como `backend.http_api_rest`. El flujo objetivo se ejecuta
desde la raíz mediante el emulador de Functions. Durante el paso 1, la referencia
FastAPI se prueba sin Docker según `backend/tests/README.md`.

Implementa la API REST mediante Flask y constituye la única interfaz pública
del servidor.

Responsabilidades:

* Definir endpoints y métodos HTTP.
* Definir y validar los contratos de entrada y salida.
* Convertir JSON a los tipos usados por el servidor.
* Invocar las operaciones correspondientes de `app`.
* Traducir los resultados del sistema a respuestas HTTP adecuadas.
* Aplicar autenticación en la frontera HTTP cuando corresponda.

No debe contener:

* Lógica de negocio.
* Acceso directo a Firebase o Firestore.
* Conocimiento de colecciones, documentos o consultas de persistencia.

Los endpoints deben organizarse por área funcional. Cada sección debe vivir en
un archivo diferente dentro de `backend/http_api_rest`; por ejemplo, autenticación,
usuarios, hogares, dispositivos, monitoreo, métricas y alarmas. El archivo que crea la aplicación Flask solamente debe registrar esas rutas.
Los módulos deben nombrarse con el patrón `http_endpoints_<area>.py`.

Cada módulo de endpoints expone una clase que recibe `http_processor` en su
constructor y publica su Blueprint de Flask. Esta inyección permite que las rutas
deleguen en métodos `process_*` sin construir ni conocer las dependencias
internas del sistema. `http.py` se limita a construir estas clases y registrar
sus Blueprints mediante `create_http_app`. Hasta el paso 2 se conservan los
`APIRouter` existentes como referencia ejecutable.

### app

Contiene y coordina la lógica de negocio.

Responsabilidades:

* Ejecutar los casos de uso solicitados por la API.
* Aplicar reglas de negocio.
* Validar identidad, relaciones y permisos.
* Coordinar la persistencia y las notificaciones.
* Evitar que las decisiones del negocio dependan del formato interno de
  Firestore.

La API no debe saltarse esta capa para acceder a los datos.

### database

Encapsula la integración con Firebase y Firestore.

Responsabilidades:

* Inicializar y configurar Firebase del lado servidor.
* Leer y escribir documentos.
* Ejecutar consultas de Firestore.
* Convertir los datos persistidos a tipos que puedan consumir las capas
  superiores.
* Ocultar nombres de colecciones y detalles propios de Firebase al resto del
  sistema siempre que sea posible.

Firebase/Firestore es la única persistencia prevista actualmente.

Dentro de `database` se mantiene una capa `repositories`. Cada repository
encapsula las operaciones de persistencia de un área concreta, como usuarios,
hogares o dispositivos, y oculta la sintaxis y estructura propias de Firestore.

Los repositories deben:

* Ser la única capa que ejecuta consultas y escrituras de Firestore.
* Exponer operaciones con nombres vinculados al dominio y no a la sintaxis de
  Firebase.
* Convertir documentos de Firestore a los tipos esperados por las capas
  superiores y viceversa.
* No contener validaciones de permisos ni reglas de negocio.
* No retornar objetos internos del SDK de Firebase fuera de `database`.

El código de repositories heredado se considera obsoleto por estar asociado al
diseño anterior. Se reemplazará por repositories específicos para Firebase en
los pasos correspondientes.

La inicialización de Firebase es una responsabilidad interna del servidor y no
debe exponerse como endpoint.

### app/domain

Contiene las entidades y tipos propios del negocio.

No debe contener:

* Acceso a Firebase.
* Conocimiento de colecciones o documentos.
* Dependencias de Flask, FastAPI o Firebase Functions.
* Lógica de negocio compleja.

Los contratos HTTP no deben confundirse automáticamente con las entidades de
dominio. Pueden parecerse, pero cada uno debe modelar su propia responsabilidad.

### notifications

Contiene la integración y lógica de envío de notificaciones.

Las notificaciones deben ser solicitadas desde `app`; los endpoints no deben
enviarlas directamente.

`app` decide, según el resultado del caso de uso y las reglas del negocio, si
corresponde generar una notificación. El módulo `notifications` se limita a
prepararla y enviarla mediante el proveedor elegido.

### fall_detection

Contiene la carga del modelo y el procesamiento de datos mediante machine
learning.

El repositorio externo vive como submódulo en `backend/fall_detection/model`.
La interfaz pública se exporta desde la raíz del submódulo. El retorno mock
temporal vive dentro de detect_fall, marcado para eliminarse. El futuro
manager también pertenece a `fall_detection`; `app/processing` se reserva para
negocio y permisos. Este módulo no decide autorizaciones ni notificaciones.

Responsabilidades:

* Inicializar y cargar el modelo del lado servidor.
* Exponer una interfaz interna explícita para ejecutar inferencias.
* Validar o transformar las entradas propias del modelo.
* Retornar resultados sin decidir las reglas generales del negocio.
* Mantener separados los datos y el contexto de cada solicitud.

La aplicación móvil no accede directamente al modelo. Los endpoints invocan a
`app`; esta capa decide cuándo utilizar `fall_detection` y qué hacer con el
resultado.

Inicialmente se utilizará un modelo compartido por todas las solicitudes, no una
instancia por usuario. El modelo no debe almacenar un usuario actual ni otro
estado global mutable que pueda mezclar datos entre solicitudes.

La implementación debe permitir medir tiempos de inferencia, controlar errores
y limitar la concurrencia si el modelo no soporta ejecuciones simultáneas. No se
agregarán colas distribuidas, servicios independientes ni escalado automático
sin una necesidad observada o un paso que lo solicite.

---

## Cloud Functions y desarrollo local

El destino acordado es una única función HTTP `api` en `grand-safe-band`, región
`us-central1`, codebase `backend`, runtime Python 3.13. La raíz del repositorio
será el directorio fuente; `backend` conserva sus paquetes y capas. El `main.py`
raíz exportará `api` y la composición de Flask y `App` permanecerá en el backend.

Configuración inicial para los mocks: mínimo cero y máximo diez instancias,
concurrencia uno, una CPU, 256 MiB y timeout de 60 segundos. No cargar artefactos
ni bibliotecas de inferencia al iniciar. La memoria de una instancia no constituye
persistencia compartida. No ejecutar trabajo de negocio después de responder.

Usar el emulador de Functions para validar la integración cuando esté preparado
en los pasos 3 y 4. Docker se retira solamente después de esa validación. No
desplegar hasta el paso 5 expresamente solicitado. No alterar la función
`addmessage`, la prueba de concepto, reglas, índices ni datos de Firestore.

Versionar código, dependencias, pruebas, documentación, `firebase.json` y
`.firebaserc`; excluir secretos, credenciales, entornos, cachés y logs. Excluir
también pruebas, documentación y planificación del paquete de despliegue.
El diseño de inferencia y ejecución del manager sigue pendiente para E5.

---

## Reglas de la API REST

* La API REST es la única vía de acceso al servidor para la aplicación.
* El cliente no accede directamente a Firebase ni recibe credenciales para hacerlo.
* Cada endpoint representa una operación válida del sistema, no una operación genérica sobre una colección.
* Los identificadores internos son generados y controlados por el servidor.
* Si se necesita aceptar un identificador externo, debe modelarse explícitamente como tal y no asumirse como clave interna.
* `created_at`, `updated_at` y otros datos de auditoría son responsabilidad del servidor.
* Toda lectura o modificación debe validar autenticación y permisos cuando corresponda.
* Los requests y responses deben tener esquemas explícitos; evitar contratos abiertos equivalentes a `Map<String, dynamic>` salvo que el caso realmente lo requiera.
* Los nombres y estructuras internas de Firebase no forman parte del contrato público.
* La compatibilidad con los JSON actuales de la app es deseable, pero no debe comprometer seguridad, consistencia ni autoridad del servidor.
* Todos los endpoints deben responder con el envelope de la aplicación, que
  contiene siempre `op_status` y `brief`, y contiene `resp` solamente cuando
  corresponda.
* Cada `op_status` de la aplicación tiene exactamente un `brief` asociado. Esa
  relación se centraliza en `backend/http_api_rest/api_op_codes.py` y se amplía a
  medida que aparecen nuevos resultados.
* La API utiliza inicialmente `200` para una operación atendida correctamente,
  `400` para errores del cliente gestionados explícitamente por la aplicación y
  `500` para errores internos del servidor. Los errores automáticos de
  validación conservan el estado HTTP `422` y el JSON `detail` observado en
  FastAPI/Pydantic. El código HTTP
  no reemplaza el `op_status` propio de la aplicación.
* Conservar errores JSON `404`/`405`, validación de path/query/body/headers,
  campos adicionales prohibidos y distinción entre omisión y `null`. No agregar
  CORS ni autenticación real en E1. `/docs`, `/redoc`, `/openapi.json` y su ruta
  auxiliar de OAuth son herramientas de FastAPI excluidas de la migración.

---

## Planificación local en IA Workflow

`README.md` permanece en la raíz como presentación versionada del sistema y
entrada a su documentación. `IA Workflow/epics.md` contiene las épicas pendientes.
`IA Workflow/task.md` funciona como backlog ordenado de implementación y puede reemplazarse
al cerrar una etapa, ya que el trabajo terminado queda reflejado en el código,
la documentación de la API y el historial de Git.

Las referencias a `task.md` en estas reglas corresponden siempre a
`IA Workflow/task.md`, relativo a la raíz del repositorio. No crear otra copia
en la raíz. Los archivos activos `IA Workflow/task.md` y `IA Workflow/epics.md`
son locales y están excluidos de Git. Solo se versionan `task.example.md` y
`epics.example.md` dentro de esa carpeta. Al preparar un checkout nuevo, copiar
los ejemplos a sus nombres activos si hace falta, sin sobrescribir planificación
existente. Los ejemplos no son tareas autorizadas.

`AGENTS.md` contiene las reglas compartidas y permanece versionado. La carpeta
`.agents/`, actualmente vacía, queda local e ignorada; no reemplaza la planificación
de `IA Workflow/`. Si se incorporan skills compartidas en el futuro, revisar
explícitamente su inclusión en Git.

El formato esperado de `IA Workflow/task.md` será similar a:

```markdown
## Paso 1

Descripción del paso.

## Paso 2

Descripción del paso.

## Paso 3

Descripción del paso.
```

`task.md` aporta contexto sobre el objetivo general, pero no autoriza a ejecutar todos los pasos de una vez.

Reglas de ejecución:

* Leer el archivo completo para comprender el rumbo general antes de trabajar en un paso.
* Ejecutar únicamente el paso que el usuario solicite expresamente en el chat.
* No adelantar pasos posteriores aunque parezcan necesarios o convenientes.
* Actualizar la documentación de endpoints solo por pedido explícito del usuario.
  Cuando lo solicite, mantener
  sincronizados URL, método, contrato y códigos con el código implementado.
* En la documentación, titular cada endpoint con el formato
  ``### `MÉTODO /ruta` ``. Usar `Response:` para los ejemplos de salida, sin
  calificarlos como mocks.
* Al terminar el paso solicitado, detenerse y entregar el resultado para que el usuario pueda verificarlo.
* Aplicar los ajustes que el usuario pida antes de continuar.
* Avanzar al siguiente paso solamente cuando el usuario lo indique expresamente.
* Si para completar el paso actual falta una definición que cambia materialmente el contrato o la arquitectura, señalarla y acordarla antes de asumirla.

---

## Reportes de testing y desarrollo

**Política de documentación:** crear o actualizar documentación únicamente por
pedido explícito del usuario. Terminar un paso o cerrar `IA Workflow/task.md`
no autoriza por sí solo a documentar. Esto incluye README, documentación de API,
diseños y reportes. Esta regla prevalece sobre indicaciones previas de
documentación automática, incremental o al cierre.

Al finalizar el último paso de `IA Workflow/task.md`, recordar al usuario que
puede actualizar la documentación y preguntarle si quiere hacerlo. Esperar su
respuesta antes de crear o modificar documentación.

La documentación del proyecto debe describir el sistema y su uso, de forma
independiente de la metodología de trabajo: no incluir épicas, sprints, números
de pasos ni estados del backlog. La planificación queda en `IA Workflow/`.
Mantener la documentación breve, sin duplicar información ni crear archivos
innecesarios. Esta política no impide implementar y ejecutar pruebas.

La documentación técnica de la aplicación se centraliza en `doc/app_reports/`.
El contrato de la API REST se mantiene en
`doc/app_reports/api_rest/api_documentation.md`. Por el momento se utilizan
documentos Markdown; se agregarán subdivisiones cuando sean necesarias.

Cuando el usuario pide un reporte en el chat o en `IA Workflow/task.md`, se
refiere a un documento Markdown tipo README, guardado dentro de `doc/` según
su propósito:

* `doc/tests_reports/`: reportes de testing, validación de módulos y análisis
  de bugs que se solicite documentar. Incluir alcance, pruebas realizadas,
  resultados y, cuando corresponda, pasos de reproducción y pendientes.
* `doc/dev_desig/`: diseños y decisiones de arquitectura acordados, incluyendo
  lógica de negocio, autenticación y futuros diseños de notificaciones. Mantener
  explícita la distinción entre decisiones acordadas y definiciones pendientes.
* `doc/dev_reports/`: análisis y propuestas de desarrollo de mayor alcance,
  TODOs que requieren explicación y documentos para compartir con otros
  desarrolladores del proyecto, como Guido o Santi. Incluir el contexto,
  contratos o cambios esperados y las definiciones pendientes que correspondan.

Usar un archivo `.md` con nombre descriptivo por tema; no es necesario que se
llame literalmente `README.md`. Si ya existe un reporte del mismo tema,
actualizarlo cuando el pedido sea una continuación. Respetar una ubicación o
un formato diferente si el usuario lo indica explícitamente.

Mantener los reportes concisos y proporcionales al pedido. No generar un
reporte por cada prueba rutinaria. Aplicar la política de documentación anterior.
La respuesta del chat debe enlazar
el documento creado o actualizado. Los reportes no reemplazan el backlog ni
autorizan a implementar los cambios que describen.

---

## Principios de desarrollo

* Mantener módulos pequeños y con responsabilidades claras.
* Mantener los endpoints delgados y la lógica de negocio en `app`.
* Mantener Firebase y Firestore dentro de `database`.
* Evitar duplicación de lógica.
* Priorizar contratos explícitos y legibles.
* Priorizar claridad antes que optimizaciones prematuras.
* No agregar abstracciones innecesarias.
* Aplicar prácticas similares a las de un producto real cuando tengan valor
  didáctico o eviten errores concretos.
* No sobrearquitecturar para una escala que el proyecto no necesita.
* Preferir primero una solución simple y medible; optimizar o distribuir después
  de observar una limitación real.
* Modificar solamente lo necesario para el paso solicitado.
* No conservar código obsoleto por compatibilidad si el paso actual indica reemplazarlo, pero no eliminarlo anticipadamente fuera del alcance solicitado.
