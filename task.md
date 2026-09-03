# Actualizacion de DB y limpieza de endpoints

# Paso 1: Eliminar antigua DB
Se debe limpiar todo lo que tenga que ver con Postgres. Para eso ir eliminando:

- Eliminar el contenedor de la base de datos postgres desde el docker-compose. No será necesario nada de SQL

- Eliminar la carpeta databse/usersDB

- Dentro de database/ dejar carpeta:
    - repositories: Archivos especificos para hablar contra firebase
    - database.py: Aca vamos a ver cuestiones de inicializcion que se corren al iniciar todo el backend (validaciones, inicializaciones, etc). Este archivo queda en TO DO

Por ahora no nos preocupa la DB porque en este punto de la implementación aún no la vamos a utilizar. Borrar todo a lo bruto

# Paso 2: Creación de nuevos archivos

Basandonos en el archivo de 
"Parte de Guido\datasource_api_documentation.md"

Crear los archivos:
- users_endpoints.py
- homes_endpoints.py
- monitoring_requests_endpoints.py
- devices_endpoints.py
- devices_stats_endpoints.py
- alarms_endpoints.py

La parte de inicialziación no corresponde a la API, sino a un proceso de inicialiazcion interno del servidor

A cada uno de estos archivos incluirle cabecera de descripción de archivo:

"""
@file
@author
@brief

Descripcion del módulo
"""
Aclaracion CODEX:
Leer archivo datasource_api_documentation.md

Cabe destacar que en nuestro patrón de diseño de la API REST se usa una inyección de dependencias. Se le pasa como argumento en el constructor el objeto http_processor que se ocupa de proveer las funciones processNombreEndpoint. Por el momento todas las funciones process van a simplemente retornar éxito y tendrá respuestas mockeadas. De esta manera podremos simplemente probar que funcione bien la api.

Como regla de la API en todas las respuestas se retorna el campo {"op_status": 0, "brief": "descripcion", "resp": "X"}

Para eso se tendrá un mapa de código de error vs descripción. Este mapa vivirá en api_op_codes.py

El campo resp puede ser opcional según si aplica o no

Esta regla aplicará para todos los endpoints siguientes.

Dejar asentado este patrón en AGENTS.md


Como verás los endpoints están pensados como funciones. Se debe ponerle una nomenclatura más adecuada a lo que es HTTP.

Creo que conviene ponerle de nombres

grandsafelife/api/v1/users/*
grandsafelife/api/v1/homes/*
grandsafelife/api/v1/monitoring-requests/*
grandsafelife/api/v1/devices/*
grandsafelife/api/v1/devices/{device_id}/stats/*
grandsafelife/api/v1/devices/{device_id}/alarms/*

# Paso 3: Creación de endpoints de usuario
Crear los endpoints relacionados con usuarios en users_endpoints.py

Todos estos endpoints utilizan el header:

```http
Authorization: Bearer <firebase_id_token>
```

El bearer contiene el Firebase ID token y no el UID. El servidor verificará el
token y obtendrá de allí el UID confiable del solicitante. La implementación
real de esa validación se resolverá según lo documentado en `to_do_auth.md`.

## JSON de usuario esperado por la aplicación

El contrato entregado por Guido espera un usuario con esta estructura:

```json
{
  "name": "Juan Pérez",
  "email": "juan.perez@example.com",
  "avatar": "https://example.com/avatars/user_001.png",
  "created_at": 1783700000000,
  "updated_at": 1783882718000,
  "homes": {
    "home_id_001": {
      "home_name": "Residencia Principal",
      "role": "admin"
    },
    "home_id_002": {
      "home_name": "Casa de Campo",
      "role": "pending"
    }
  }
}
```

Los valores admitidos inicialmente para `homes.*.role` son `admin`, `observer`
y `pending`.

`created_at` y `updated_at` son administrados por el servidor. Al crear el
perfil, `homes` comienza vacío salvo que una operación de negocio indique lo
contrario. La app no debe imponer timestamps ni relaciones de hogares mediante
el endpoint de creación de perfil.

## `getCurrentUser`

```http
GET /grandsafelife/api/v1/users/me
```

Recupera la identidad y el perfil completo del usuario autenticado. No recibe un
UID adicional: el processor obtiene el UID del token verificado.

## `getUserByID`

```http
GET /grandsafelife/api/v1/users/{user_id}
```

Recupera únicamente la información pública de otro usuario mediante su UID. El
token identifica al solicitante y `user_id` identifica al usuario objetivo.

Dejar un `TODO` en la función process correspondiente para implementar la
validación de permisos y terminar de definir el subconjunto exacto de campos
públicos. La respuesta mock no debe exponer `homes` ni otra información privada.

## `getUserByEmail`

```http
GET /grandsafelife/api/v1/users/by-email?email={email}
```

Recupera únicamente la información pública de otro usuario mediante su email.
El token identifica al solicitante. Dejar un `TODO` en la función process
correspondiente para implementar la validación de permisos y terminar de definir
el subconjunto exacto de campos públicos.

## `createUser`

```http
POST /grandsafelife/api/v1/users/me
```

Firebase Authentication crea previamente la identidad desde la aplicación
Flutter. Este endpoint crea la información inicial o perfil de Grand Safe Life
asociado a ese usuario recién autenticado.

El servidor no genera el token ni el UID. Verifica el ID token, extrae su UID y
lo utiliza como identificador del perfil. El UID no se recibe en el body.

El body contiene solamente los campos iniciales editables por la app, por
ejemplo:

```json
{
  "name": "Juan Pérez",
  "email": "juan.perez@example.com",
  "avatar": "https://example.com/avatars/user_001.png"
}
```

Si falta el token, es inválido o no contiene un UID válido, se retorna el código
de operación de autenticación correspondiente. No se utiliza `INVALID_PARAM`
por un ID ausente en el body, porque dicho ID no forma parte del request.

## `updateCurrentUser`

```http
PATCH /grandsafelife/api/v1/users/me
```

Actualiza parcialmente los campos editables del perfil propio. El UID se obtiene
del token verificado y el body contiene únicamente los campos que se desean
modificar. El servidor actualiza `updated_at` y no permite modificar directamente
`created_at`, `updated_at` ni `homes` mediante este endpoint.

Por el momento todas las funciones process de esta sección retornan éxito y
respuestas mockeadas. La autenticación, autorización y persistencia real quedan
indicadas mediante `TODO` para los pasos posteriores.

# Paso 4: Endpoints de Hogares

Leer `Parte de Guido/datasource_api_documentation.md` e implementar los
endpoints en `homes_endpoints.py`.

Todos los endpoints utilizan:

```http
Authorization: Bearer <firebase_id_token>
```

El servidor obtiene del token el UID del usuario solicitante y `system` valida
si posee permisos sobre el hogar antes de ejecutar la operación.

Un usuario puede pertenecer a más de un hogar. La creación, actualización y
eliminación de un hogar son operaciones del servidor: la app realiza un único
request y el servidor mantiene de forma consistente el hogar y las relaciones
de usuarios afectadas.

## JSON de hogar esperado por la aplicación

El contrato entregado por Guido espera un hogar con esta estructura:

```json
{
  "name": "Residencia Principal",
  "created_at": 1783882718000,
  "updated_at": 1783882718000,
  "members": {
    "user_id_001": {
      "email": "juan.perez@example.com",
      "role": "admin"
    },
    "user_id_002": {
      "email": "maria.gomez@example.com",
      "role": "observer"
    }
  }
}
```

Los valores admitidos inicialmente para `members.*.role` son `admin`,
`observer` y `pending`. `created_at` y `updated_at` son administrados por el
servidor.

## `getHomeByID`

```http
GET /grandsafelife/api/v1/homes/{home_id}
```

Recupera un hogar mediante su ID. El ID se incluye como parámetro de ruta y no
como query string.

Response mock exitoso:

```json
{
  "op_status": 0,
  "brief": "Home retrieved successfully",
  "resp": {
    "name": "Residencia Principal",
    "created_at": 1783882718000,
    "updated_at": 1783882718000,
    "members": {
      "user_id_001": {
        "email": "juan.perez@example.com",
        "role": "admin"
      },
      "user_id_002": {
        "email": "maria.gomez@example.com",
        "role": "observer"
      }
    }
  }
}
```

Dejar en la función process los `TODO` correspondientes a existencia del hogar,
pertenencia del usuario y permisos de lectura.

## `createHome`

```http
POST /grandsafelife/api/v1/homes
```

Crea un hogar nuevo. El ID lo genera el servidor. El usuario autenticado se
agrega automáticamente como miembro con rol `admin`; la app no debe enviar su
UID ni construir manualmente el mapa inicial de miembros.

Body:

```json
{
  "name": "Residencia Principal"
}
```

La operación interna deberá crear el hogar y reflejar la relación en el perfil
del usuario como una única operación de negocio.

La interfaz de Guido espera recibir el ID asignado como resultado de
`createHome`. Por eso el envelope retorna el ID directamente en `resp`:

```json
{
  "op_status": 0,
  "brief": "Home created successfully",
  "resp": "home_id_001"
}
```

## `updateHome`

```http
PATCH /grandsafelife/api/v1/homes/{home_id}
```

Actualiza parcialmente los campos editables de un hogar. El body contiene
solamente los campos que se desean modificar.

Body de ejemplo:

```json
{
  "name": "Nuevo nombre de la residencia"
}
```

En este endpoint no se permite modificar directamente `created_at`,
`updated_at` ni `members`. Las altas, bajas y cambios de rol de miembros deberán
resolverse mediante operaciones específicas del negocio. `system` deberá
verificar que el usuario posea rol suficiente para editar el hogar.

Response mock exitoso:

```json
{
  "op_status": 0,
  "brief": "Home updated successfully"
}
```

## `deleteHome`

```http
DELETE /grandsafelife/api/v1/homes/{home_id}
```

Elimina permanentemente un hogar. El servidor debe validar que el solicitante
posea permisos de administrador y debe eliminar también las referencias al hogar
en los perfiles de todos los miembros afectados. La app no realiza escrituras
adicionales para completar la operación.

Este endpoint no lleva body.

Response mock exitoso:

```json
{
  "op_status": 0,
  "brief": "Home deleted successfully"
}
```

Por el momento todas las funciones process de esta sección retornan éxito y
respuestas mockeadas. La autenticación, autorización, consistencia entre
documentos y persistencia real quedan indicadas mediante `TODO` para los pasos
posteriores.

# Paso 5: Solicitudes de monitoreo y acceso a hogares
monitoring_requests_endpoints.py

Esta sección modela la invitación y aceptación de usuarios dentro de un hogar.
La app no modifica directamente el mapa `members` para agregar personas. El
servidor crea una solicitud, consulta al destinatario y actualiza las relaciones
solamente cuando la solicitud es aceptada.

`pending`, `accepted` y `rejected` son estados de una solicitud. No deben
utilizarse como roles. Los roles iniciales de un miembro aceptado son `admin` y
`observer`.

Todos los endpoints utilizan:

```http
Authorization: Bearer <firebase_id_token>
```

## JSON esperado para una solicitud de monitoreo

```json
{
  "request_id": "request_id_001",
  "home_id": "home_id_001",
  "home_name": "Residencia Principal",
  "requester": {
    "name": "Juan Pérez",
    "email": "juan.perez@example.com"
  },
  "requested_role": "observer",
  "status": "pending",
  "created_at": 1783882718000,
  "updated_at": 1783882718000
}
```

Los IDs internos de los usuarios involucrados son resueltos por el servidor y no
es necesario exponerlos a la aplicación dentro de este contrato.

## `createMonitoringRequest`

```http
POST /grandsafelife/api/v1/homes/{home_id}/monitoring-requests
```

Invita a otro usuario a participar del hogar. `system` debe verificar que el
solicitante sea administrador, resolver al destinatario mediante su email y
comprobar que no exista ya una membresía o solicitud pendiente equivalente.

Body:

```json
{
  "email": "maria.gomez@example.com",
  "role": "observer"
}
```

Response mock exitoso:

```json
{
  "op_status": 0,
  "brief": "Monitoring request created successfully",
  "resp": "request_id_001"
}
```

## `getMyMonitoringRequests`

```http
GET /grandsafelife/api/v1/users/me/monitoring-requests
```

Recupera las solicitudes relacionadas con el usuario autenticado que la app
necesita mostrar. Inicialmente se priorizan las solicitudes recibidas pendientes;
si posteriormente se necesitan enviadas o históricas, se agregará un filtro
explícito.

Response mock exitoso:

```json
{
  "op_status": 0,
  "brief": "Monitoring requests retrieved successfully",
  "resp": [
    {
      "request_id": "request_id_001",
      "home_id": "home_id_001",
      "home_name": "Residencia Principal",
      "requester": {
        "name": "Juan Pérez",
        "email": "juan.perez@example.com"
      },
      "requested_role": "observer",
      "status": "pending",
      "created_at": 1783882718000,
      "updated_at": 1783882718000
    }
  ]
}
```

## `answerMonitoringRequest`

```http
POST /grandsafelife/api/v1/monitoring-requests/{request_id}/answer
```

Permite que el destinatario acepte o rechace una solicitud pendiente.

Body:

```json
{
  "answer": "accepted"
}
```

Los valores permitidos son `accepted` y `rejected`. El servidor valida que el
usuario autenticado sea el destinatario y que la solicitud siga pendiente.

Si la respuesta es `accepted`, el servidor agrega al usuario en `home.members`
con el rol solicitado y agrega el hogar en `user.homes` como una única operación
de negocio. Si es `rejected`, no modifica las membresías.

Response mock exitoso:

```json
{
  "op_status": 0,
  "brief": "Monitoring request answered successfully"
}
```

Por el momento las funciones process retornan respuestas mockeadas. Dejar como
`TODO` la autenticación real, permisos, prevención de duplicados, actualización
atómica de relaciones y envío de notificaciones.


# Paso 6: Endpoints de Devices
devices_endpoints.py

Leer `Parte de Guido/datasource_api_documentation.md` e implementar los
endpoints en `devices_endpoints.py`.

Todos los endpoints utilizan:

```http
Authorization: Bearer <firebase_id_token>
```

## Modelo de dispositivos

Cada dispositivo físico posee un identificador único e inmutable. Los
dispositivos ya existen previamente en la base de datos; la aplicación no crea
nuevos registros de hardware ni elige sus IDs.

Un dispositivo se asocia directamente a un hogar mediante `home_id`, no a un
usuario particular. Las personas quedan relacionadas con el dispositivo de
manera indirecta por su pertenencia a ese hogar.

El campo `owner_id` identifica al usuario administrador propietario del hogar,
no al anciano que utiliza o es monitoreado mediante el dispositivo. Al asociar
un dispositivo, el servidor obtiene `owner_id` desde la administración del hogar
y no permite que la app lo elija libremente.

La operación que la interfaz de Guido denomina `createDevice` debe interpretarse
en nuestra API como vincular un dispositivo existente a un hogar.

Un dispositivo puede comunicarse mediante un hub o sin hub. El hub es
infraestructura de comunicación y no se consulta desde la app como si fuera uno
de los dispositivos monitoreados. `connection_by` conserva la información de
qué hub utiliza el dispositivo o indica que no utiliza ninguno.

## JSON de dispositivo esperado por la aplicación

Para un dispositivo individual, el contrato entregado por Guido espera esta
estructura. El campo `id` se agrega de manera aditiva para que el objeto pueda
identificarse fuera de un mapa indexado:

```json
{
  "id": "dev_a81f23",
  "created_at": "2026-08-15T10:32:14Z",
  "updated_at": "2026-09-01T18:21:47Z",
  "home_id": "home_7f3a92",
  "owner_id": "user_admin_001",
  "is_active": true,
  "type": "sensor",
  "battery": 87,
  "name": "Sensor Living",
  "connection_by": "hub_001",
  "coords": {
    "lat": -34.6037,
    "long": -58.3816
  }
}
```

Reglas del contrato de Guido:

* `id` identifica de forma única al dispositivo.
* `type` describe el tipo de dispositivo monitoreado, por ejemplo `sensor` o
  `camera`; `hub` no se expone como un tipo consultable desde estos endpoints.
* `home_id` identifica el hogar al que está asociado el dispositivo.
* `owner_id` identifica al administrador propietario de ese hogar.
* `is_active` indica si el dispositivo se encuentra conectado al servidor.
* `connection_by` contiene el ID del hub utilizado o `-1` cuando el dispositivo
  no está conectado mediante un hub.
* `coords` contiene la última ubicación conocida.
* Las fechas se representan como strings ISO 8601 en UTC.

Campos controlados por el servidor o el dispositivo, y no editables libremente
por la app:

* Número de serie.
* `type`.
* `home_id` y `owner_id`, excepto mediante las operaciones específicas de
  asociación o desvinculación. Ambos campos deben mantenerse consistentes con
  la administración del hogar.
* `is_active`.
* `battery`.
* `coords`.
* `created_at`.
* `updated_at`.

## `getDeviceByID`

```http
GET /grandsafelife/api/v1/devices/{device_id}
```

Recupera un dispositivo mediante su ID. `system` debe comprobar que el
solicitante esté autorizado a consultar el hogar asociado. Si el
dispositivo no existe se informa mediante el `op_status` correspondiente.

Response mock exitoso:

```json
{
  "op_status": 0,
  "brief": "Device retrieved successfully",
  "resp": {
    "id": "dev_a81f23",
    "created_at": "2026-08-15T10:32:14Z",
    "updated_at": "2026-09-01T18:21:47Z",
    "home_id": "home_7f3a92",
    "owner_id": "user_admin_001",
    "is_active": true,
    "type": "sensor",
    "battery": 87,
    "name": "Sensor Living",
    "connection_by": "hub_001",
    "coords": {
      "lat": -34.6037,
      "long": -58.3816
    }
  }
}
```

## `associateDevice`

Reemplaza conceptualmente al método `createDevice` de la interfaz de Guido.

```http
POST /grandsafelife/api/v1/devices/{device_id}/association
```

Vincula un dispositivo existente a un hogar. El servidor debe rechazar IDs
inexistentes, dispositivos ya vinculados y hogares sobre los cuales el usuario
no tenga permisos suficientes.

Body:

```json
{
  "home_id": "home_7f3a92"
}
```

El servidor ya conoce los demás datos del dispositivo. No se recibe `owner_id`
en el body: se obtiene del administrador propietario de `home_id`. El acceso del
resto de las personas al dispositivo se determina mediante sus relaciones con el
hogar.

La interfaz de Guido espera un `Future<String>` al completar `createDevice`. Para
mantener esa compatibilidad, la asociación retorna el número de serie:

```json
{
  "op_status": 0,
  "brief": "Device associated successfully",
  "resp": "dev_a81f23"
}
```

## `updateDevice`

```http
PATCH /grandsafelife/api/v1/devices/{device_id}
```

Actualiza parcialmente campos configurables del dispositivo. Inicialmente la app
puede modificar `name` y la configuración `connection_by`. Cualquier cambio de
conexión debe validar que el hub indicado exista y sea válido para ese hogar.

Body de ejemplo:

```json
{
  "name": "Sensor Dormitorio",
  "connection_by": "hub_001"
}
```

Response mock exitoso:

```json
{
  "op_status": 0,
  "brief": "Device updated successfully"
}
```

## `deleteDevice`

La operación no elimina el hardware existente. Solamente elimina su asociación
actual para dejarlo disponible nuevamente.

```http
DELETE /grandsafelife/api/v1/devices/{device_id}/association
```

El servidor elimina `home_id` y `owner_id`, y deja el dispositivo disponible
para asociarlo a otro hogar. No elimina las estadísticas históricas del
dispositivo.

Este endpoint no lleva body.

Response mock exitoso:

```json
{
  "op_status": 0,
  "brief": "Device released successfully"
}
```

## `queryDevicesByOwner`

```http
GET /grandsafelife/api/v1/users/{owner_id}/devices
```

Recupera los dispositivos cuyo `owner_id` corresponde al usuario administrador
indicado. Conceptualmente equivale a recuperar los dispositivos pertenecientes
a los hogares administrados por ese usuario. `system` debe validar que el
solicitante pueda consultar esa relación.

Aunque `owner_id` pueda persistirse en el dispositivo para facilitar la consulta,
su fuente de verdad es la administración del hogar. El servidor debe mantenerlo
sincronizado si cambia el administrador propietario.

El `resp` utiliza el mismo mapa indexado por ID definido en
`queryDevicesByHome`. Si no existen dispositivos accesibles, retorna `{}`.

## `queryDevicesByHome`

```http
GET /grandsafelife/api/v1/homes/{home_id}/devices
```

Recupera todos los dispositivos monitoreados asociados a un hogar. Los hubs no
se incluyen como elementos consultables. `system` valida que el usuario
autenticado sea miembro autorizado del hogar.

Aunque conceptualmente representa una colección, el contrato de Guido no retorna
un array JSON. Retorna un objeto o mapa cuyas claves son los IDs de dispositivo.

Response mock exitoso:

```json
{
  "op_status": 0,
  "brief": "Devices retrieved successfully",
  "resp": {
    "dev_a81f23": {
      "created_at": "2026-08-15T10:32:14Z",
      "updated_at": "2026-09-01T18:21:47Z",
      "home_id": "home_7f3a92",
      "owner_id": "user_admin_001",
      "is_active": true,
      "type": "sensor",
      "battery": 87,
      "name": "Sensor Living",
      "connection_by": "hub_001",
      "coords": {
        "lat": -34.6037,
        "long": -58.3816
      }
    },
    "dev_b42c91": {
      "created_at": "2026-07-28T14:11:03Z",
      "updated_at": "2026-09-01T17:58:12Z",
      "home_id": "home_7f3a92",
      "owner_id": "user_admin_001",
      "is_active": true,
      "type": "camera",
      "battery": 64,
      "name": "Cámara Entrada",
      "connection_by": "hub_001",
      "coords": {
        "lat": -34.6032,
        "long": -58.3809
      }
    },
    "dev_c73e15": {
      "created_at": "2026-08-02T09:45:27Z",
      "updated_at": "2026-09-01T18:05:31Z",
      "home_id": "home_7f3a92",
      "owner_id": "user_admin_001",
      "is_active": false,
      "type": "sensor",
      "battery": 31,
      "name": "Sensor Dormitorio",
      "connection_by": "-1",
      "coords": {
        "lat": -34.6041,
        "long": -58.3824
      }
    }
  }
}
```

Si el hogar no tiene dispositivos, `resp` retorna `{}`.

## `getLocationByDevice`

```http
GET /grandsafelife/api/v1/devices/{device_id}/location
```

Recupera la última ubicación GPS reportada por un dispositivo. El servidor
valida los permisos del solicitante mediante el hogar asociado.

Response mock exitoso:

```json
{
  "op_status": 0,
  "brief": "Device location retrieved successfully",
  "resp": {
    "lat": -34.6037,
    "long": -58.3816
  }
}
```

Por el momento todas las funciones process de esta sección retornan respuestas
mockeadas. Dejar como `TODO` la autenticación real, permisos, persistencia,
validaciones de hubs y consistencia de asociaciones con hogares.

# Paso 7: Endpoints de Metricas
devices_stats_endpoints.py

Todos los endpoints reciben el token de Firebase Authentication mediante el
header `Authorization: Bearer <firebase_id_token>`. El servidor valida la
identidad y que el solicitante tenga acceso al hogar asociado al dispositivo.

Las métricas son de solo lectura para la app. Su carga y procesamiento
corresponden a los dispositivos y al servidor.

## JSON de métricas diarias esperado por la aplicación

```json
{
  "id": "2026-09-01",
  "steps": 4350,
  "falls": 0,
  "stumbles": 2,
  "time_lying_down": 8.5,
  "night_rises": 1,
  "panic_button": 0,
  "updated_at": "2026-09-01T23:59:59Z"
}
```

El campo `id` identifica el día y utiliza el formato `YYYY-MM-DD`.

## JSON de agregados mensuales esperado por la aplicación

```json
{
  "id": "2026-09",
  "avg_steps": 4120.5,
  "avg_falls": 0.03,
  "avg_stumbles": 1.4,
  "avg_lying_down": 7.9,
  "avg_night_rises": 1.1,
  "total_panic_button_press": 0,
  "sedentarism_level": 45,
  "risk_level": 12,
  "active_days": 13
}
```

El campo `id` identifica el mes y utiliza el formato `YYYY-MM`. Los agregados
son calculados por el servidor y nunca por la aplicación.

## `getDailyMetrics`

```http
GET /grandsafelife/api/v1/devices/{device_id}/stats/daily?date={YYYY-MM-DD}
```

Recupera las métricas de un dispositivo para una fecha determinada.

Response mock exitoso:

```json
{
  "op_status": 0,
  "brief": "Daily metrics retrieved successfully",
  "resp": {
    "id": "2026-09-01",
    "steps": 4350,
    "falls": 0,
    "stumbles": 2,
    "time_lying_down": 8.5,
    "night_rises": 1,
    "panic_button": 0,
    "updated_at": "2026-09-01T23:59:59Z"
  }
}
```

Si no existen datos para esa fecha, `resp` retorna `{}`.

## `getMonthlyAggregates`

```http
GET /grandsafelife/api/v1/devices/{device_id}/stats/monthly?month={YYYY-MM}
```

Recupera los agregados de un dispositivo para un mes determinado.

Response mock exitoso:

```json
{
  "op_status": 0,
  "brief": "Monthly aggregates retrieved successfully",
  "resp": {
    "id": "2026-09",
    "avg_steps": 4120.5,
    "avg_falls": 0.03,
    "avg_stumbles": 1.4,
    "avg_lying_down": 7.9,
    "avg_night_rises": 1.1,
    "total_panic_button_press": 0,
    "sedentarism_level": 45,
    "risk_level": 12,
    "active_days": 13
  }
}
```

Si no existen datos para ese mes, `resp` retorna `{}`.

## `getPreviousMonthAggregates`

```http
GET /grandsafelife/api/v1/devices/{device_id}/stats/monthly/previous
```

Recupera los agregados correspondientes al mes calendario inmediatamente
anterior al actual. El mes se calcula en el servidor.

El response exitoso utiliza el mismo JSON que `getMonthlyAggregates`. Si no hay
datos, `resp` retorna `{}`.

## `getLastWeekMetrics`

```http
GET /grandsafelife/api/v1/devices/{device_id}/stats/daily/last-week
```

Recupera las métricas diarias de los últimos siete días, incluyendo el día
actual. `resp` es un array ordenado cronológicamente desde el día más antiguo
hasta el más reciente. Solamente incluye días con datos existentes.

Response mock exitoso abreviado:

```json
{
  "op_status": 0,
  "brief": "Last week metrics retrieved successfully",
  "resp": [
    {
      "id": "2026-08-31",
      "steps": 4010,
      "falls": 0,
      "stumbles": 1,
      "time_lying_down": 7.8,
      "night_rises": 1,
      "panic_button": 0,
      "updated_at": "2026-08-31T23:59:59Z"
    },
    {
      "id": "2026-09-01",
      "steps": 4350,
      "falls": 0,
      "stumbles": 2,
      "time_lying_down": 8.5,
      "night_rises": 1,
      "panic_button": 0,
      "updated_at": "2026-09-01T23:59:59Z"
    }
  ]
}
```

Si no existen métricas en el período, `resp` retorna `[]`.

Por el momento todas las funciones process retornan respuestas mockeadas. Dejar
como `TODO` la autenticación real, permisos, persistencia y cálculo periódico de
agregados.


# Paso 8: Endpoints de Alarmas
alarms_endpoints.py

Todos los endpoints reciben el token de Firebase Authentication mediante el
header `Authorization: Bearer <firebase_id_token>`. El servidor valida que el
solicitante tenga permisos de administración sobre el hogar asociado al
dispositivo cuando la operación modifica alarmas.

## JSON de alarmas esperado por la aplicación

Las alarmas se representan como un objeto o mapa cuyas claves son sus IDs:

```json
{
  "alarm_abc_123": {
    "name": "Ibuprofeno 400mg",
    "time_in_minutes": 480,
    "days": 127,
    "is_active": true,
    "state": "taken",
    "created_at": "2026-08-15T10:32:14Z",
    "updated_at": "2026-09-01T18:21:47Z"
  },
  "alarm_def_456": {
    "name": "Losartán 50mg",
    "time_in_minutes": 1200,
    "days": 127,
    "is_active": true,
    "state": "pending",
    "created_at": "2026-08-10T09:00:00Z",
    "updated_at": "2026-09-01T00:00:00Z"
  }
}
```

Reglas iniciales:

* `time_in_minutes` representa minutos transcurridos desde la medianoche.
* `days` es una máscara de bits para los días de la semana; `127` representa
  todos los días.
* `state` puede ser `none`, `pending`, `taken` o `missed`.
* El servidor administra `state`, `created_at` y `updated_at`.
* El servidor deberá actualizar los estados según el horario y reiniciarlos al
  comenzar un nuevo día según los días configurados.

## `getAlarmsByDeviceId`

```http
GET /grandsafelife/api/v1/devices/{device_id}/alarms
```

Recupera todas las alarmas configuradas para un dispositivo.

Response mock exitoso:

```json
{
  "op_status": 0,
  "brief": "Device alarms retrieved successfully",
  "resp": {
    "alarm_abc_123": {
      "name": "Ibuprofeno 400mg",
      "time_in_minutes": 480,
      "days": 127,
      "is_active": true,
      "state": "taken",
      "created_at": "2026-08-15T10:32:14Z",
      "updated_at": "2026-09-01T18:21:47Z"
    }
  }
}
```

Si el dispositivo no tiene alarmas, `resp` retorna `{}`.

## `setAlarmsByDeviceId`

```http
PUT /grandsafelife/api/v1/devices/{device_id}/alarms
```

Reemplaza el bloque completo de alarmas del dispositivo. Se utiliza una operación
`PUT` porque la app envía la representación completa que debe quedar almacenada;
las claves omitidas se consideran eliminadas.

Body:

```json
{
  "alarm_abc_123": {
    "name": "Ibuprofeno 400mg",
    "time_in_minutes": 480,
    "days": 127,
    "is_active": true
  },
  "alarm_def_456": {
    "name": "Losartán 50mg",
    "time_in_minutes": 1200,
    "days": 127,
    "is_active": true
  }
}
```

La app no envía `state`, `created_at` ni `updated_at` como fuente de verdad. El
servidor conserva o genera esos valores según se trate de una alarma existente o
nueva.

Response mock exitoso:

```json
{
  "op_status": 0,
  "brief": "Device alarms updated successfully"
}
```

Por el momento todas las funciones process retornan respuestas mockeadas. Dejar
como `TODO` la autenticación real, permisos, persistencia, validación de la
máscara de días y actualización automática de estados.


# Paso 9: Documentacion
Crear documentacion oficial de la API para cada endpoint. Dejé el documento creado con un template para que sigas de referencia. Basicamente:
- Listado general
- Endpoints especificando:
  - URL
  - Metodo
  - brief
  - Json entrada
  - Json salida
- Tabla op codes con campo brief
