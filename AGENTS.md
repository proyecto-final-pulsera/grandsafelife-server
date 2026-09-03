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

La implementación HTTP anterior puede desestimarse. Los endpoints definitivos y sus contratos se volverán a definir dentro de `backend/app_http`.

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
      Un contenedor Docker
              |
              v
        API REST (FastAPI)
              |
              v
       System / negocio
       /       |       \
      v        v        v
Firebase  Notifications  Machine Learning
```

La división en capas debe conservarse. Cada capa tiene una responsabilidad específica y no debe filtrar detalles internos hacia las demás.

La arquitectura inicial es un monolito modular: FastAPI, procesamiento de
requests, reglas de negocio, integración con Firebase, decisión y envío de
notificaciones y procesamiento mediante el modelo de machine learning se
despliegan juntos en un único contenedor. Que compartan un contenedor no autoriza
a mezclar sus responsabilidades en el código.

---

## Estructura del proyecto

```text
backend
|
|-- app_http
|-- database
|-- domain
|-- machine_learning
|-- notifications
`-- system
```

---

## Responsabilidades por módulo

### app_http

Implementa la API REST mediante FastAPI y constituye la única interfaz pública
del servidor.

Responsabilidades:

* Definir endpoints y métodos HTTP.
* Definir y validar los contratos de entrada y salida.
* Convertir JSON a los tipos usados por el servidor.
* Invocar las operaciones correspondientes de `system`.
* Traducir los resultados del sistema a respuestas HTTP adecuadas.
* Aplicar autenticación en la frontera HTTP cuando corresponda.

No debe contener:

* Lógica de negocio.
* Acceso directo a Firebase o Firestore.
* Conocimiento de colecciones, documentos o consultas de persistencia.

Los endpoints deben organizarse por área funcional. Cada sección debe vivir en
un archivo diferente dentro de `backend/app_http`; por ejemplo, autenticación,
usuarios, hogares, dispositivos, monitoreo, métricas y alarmas. El archivo que crea la aplicación FastAPI solamente debe registrar o incluir esas rutas.
Los módulos deben nombrarse con el patrón `http_endpoints_<area>.py`.

Cada módulo de endpoints expone una clase que recibe `http_processor` en su
constructor y publica su `APIRouter`. Esta inyección permite que las rutas
deleguen en métodos `process_*` sin construir ni conocer las dependencias
internas del sistema. `app_http.py` se limita a construir estas clases y registrar
sus routers en FastAPI.

### system

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

### domain

Contiene las entidades y tipos propios del negocio.

No debe contener:

* Acceso a Firebase.
* Conocimiento de colecciones o documentos.
* Dependencias de FastAPI.
* Lógica de negocio compleja.

Los contratos HTTP no deben confundirse automáticamente con las entidades de
dominio. Pueden parecerse, pero cada uno debe modelar su propia responsabilidad.

### notifications

Contiene la integración y lógica de envío de notificaciones.

Las notificaciones deben ser solicitadas desde `system`; los endpoints no deben
enviarlas directamente.

`system` decide, según el resultado del caso de uso y las reglas del negocio, si
corresponde generar una notificación. El módulo `notifications` se limita a
prepararla y enviarla mediante el proveedor elegido.

### machine_learning

Contiene la carga del modelo y el procesamiento de datos mediante machine
learning.

Responsabilidades:

* Inicializar y cargar el modelo del lado servidor.
* Exponer una interfaz interna explícita para ejecutar inferencias.
* Validar o transformar las entradas propias del modelo.
* Retornar resultados sin decidir las reglas generales del negocio.
* Mantener separados los datos y el contexto de cada solicitud.

La aplicación móvil no accede directamente al modelo. Los endpoints invocan a
`system`; esta capa decide cuándo utilizar `machine_learning` y qué hacer con el
resultado.

Inicialmente se utilizará un modelo compartido por todas las solicitudes, no una
instancia por usuario. El modelo no debe almacenar un usuario actual ni otro
estado global mutable que pueda mezclar datos entre solicitudes.

La implementación debe permitir medir tiempos de inferencia, controlar errores
y limitar la concurrencia si el modelo no soporta ejecuciones simultáneas. No se
agregarán colas distribuidas, servicios independientes ni escalado automático
sin una necesidad observada o un paso que lo solicite.

---

## Contenedor y despliegue

Docker forma parte de la estrategia de empaquetado del servidor, principalmente
para fijar el entorno y las dependencias del módulo de machine learning.

Alcance inicial:

* Un único contenedor para todo el backend.
* Una única aplicación FastAPI como proceso principal.
* Un solo worker inicialmente, para evitar cargar copias innecesarias del modelo
  en memoria.
* Una instancia del modelo cargada y compartida dentro de ese worker.
* Firebase permanece como servicio externo en la nube y no se ejecuta dentro del
  contenedor.
* El proveedor de hosting se definirá más adelante.

Cada worker adicional puede cargar otra copia completa del modelo. Por eso no se
debe aumentar la cantidad de workers o réplicas sin medir antes memoria, tiempo
de inferencia y comportamiento concurrente.

Aunque todos los módulos se desplieguen juntos, deben comunicarse mediante
interfaces internas claras. Esto permite separar el módulo de machine learning
o notificaciones en otro servicio en el futuro si aparece una necesidad real,
sin diseñar hoy una arquitectura distribuida.

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
  relación se centraliza en `backend/app_http/api_op_codes.py` y se amplía a
  medida que aparecen nuevos resultados.
* La API utiliza inicialmente los estados HTTP básicos `200` para una operación
  atendida correctamente, `400` para errores atribuibles al request del cliente
  y `500` para errores internos del servidor. El código HTTP no reemplaza el
  `op_status` propio de la aplicación.

---

## Flujo de trabajo mediante task.md

El usuario creará un archivo `task.md` en la raíz del proyecto para enumerar el
plan completo de trabajo. Su formato esperado será similar a:

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
* Al terminar el paso solicitado, detenerse y entregar el resultado para que el usuario pueda verificarlo.
* Aplicar los ajustes que el usuario pida antes de continuar.
* Avanzar al siguiente paso solamente cuando el usuario lo indique expresamente.
* Si para completar el paso actual falta una definición que cambia materialmente el contrato o la arquitectura, señalarla y acordarla antes de asumirla.

---

## Principios de desarrollo

* Mantener módulos pequeños y con responsabilidades claras.
* Mantener los endpoints delgados y la lógica de negocio en `system`.
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
