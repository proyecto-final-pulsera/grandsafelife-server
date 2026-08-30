# Grand Safe Life Server - AGENT.md

## Descripción

Grand Safe Life Server es el backend principal del proyecto Grand Safe Life.

Su responsabilidad es gestionar usuarios, hogares, dispositivos, relaciones de
monitoreo, métricas, alarmas, eventos y notificaciones.

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

---

## Arquitectura

```text
Aplicación móvil u otro cliente
              |
              v
        API REST (FastAPI)
              |
              v
       System / negocio
          /         \
         v           v
Firebase/Firestore  Notifications
```

La división en capas debe conservarse. Cada capa tiene una responsabilidad específica y no debe filtrar detalles internos hacia las demás.

---

## Estructura del proyecto

```text
backend
|
|-- app_http
|-- database
|-- domain
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

No se utilizará la capa ni el patrón `repository` heredado de la implementación
anterior. Ese código se considera obsoleto y se eliminará o reemplazará en los
pasos correspondientes.

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
* Modificar solamente lo necesario para el paso solicitado.
* No conservar código obsoleto por compatibilidad si el paso actual indica reemplazarlo, pero no eliminarlo anticipadamente fuera del alcance solicitado.
