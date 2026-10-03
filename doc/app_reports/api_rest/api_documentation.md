# Documentación API REST

La API está alojada en Firebase Cloud Functions, en la función `api`.
URL base a la que se agregan las rutas completas de este documento:

```text
https://us-central1-grand-safe-band.cloudfunctions.net/api
```

Por ejemplo, `GET /grandsafelife/api/v1/users/user_001` se invoca en:

```text
https://us-central1-grand-safe-band.cloudfunctions.net/api/grandsafelife/api/v1/users/user_001
```

## 1 - Listado de endpoints

| CONJUNTO | MÉTODO | URL | DESCRIPCIÓN | App Guido | Le pega a la api? | Falencia | Function | Tested |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Users | GET | `/grandsafelife/api/v1/users/{user_id}` | Recupera el perfil completo de un usuario por UID. | Sí | Sí | - | getUserByID | |
| Users | GET | `/grandsafelife/api/v1/users/by-email?email={email}` | Recupera el perfil completo de un usuario por email. | Sí | Sí | - | getUserByEmail | |
| Users | POST | `/grandsafelife/api/v1/users` | Crea o reemplaza el documento de un usuario. | Sí | Sí | - | createUser | |
| Users | PATCH | `/grandsafelife/api/v1/users/{affected_user_id}` | Actualiza el perfil y los hogares del usuario afectado. | Sí | Sí | - | updateUser | |
| Homes | GET | `/grandsafelife/api/v1/homes/{home_id}` | Recupera un hogar accesible por ID. | Sí | Sí | - | getHomeByID | OK |
| Homes | POST | `/grandsafelife/api/v1/homes` | Crea o reemplaza un documento de hogar. | Sí | Sí | - | createHome | OK |
| Homes | PATCH | `/grandsafelife/api/v1/homes/{home_id}` | Actualiza parcialmente un hogar. | Sí | Sí | - | updateHome | OK |
| Homes | DELETE | `/grandsafelife/api/v1/homes/{home_id}` | Elimina el hogar indicado. | Sí | Sí | - | deleteHome | OK |
| Devices | GET | `/grandsafelife/api/v1/devices/{device_id}` | Recupera un dispositivo accesible por ID. | Sí | Sí | - | getDeviceByID | |
| Devices | POST | `/grandsafelife/api/v1/devices` | Crea o reemplaza un documento de dispositivo. | Sí | Sí | - | createDevice | |
| Devices | PATCH | `/grandsafelife/api/v1/devices/{device_id}` | Actualiza la configuración editable de un dispositivo. | Sí | Sí | - | updateDevice | |
| Devices | DELETE | `/grandsafelife/api/v1/devices/{device_id}` | Elimina el documento del dispositivo. | Sí | Sí | - | deleteDevice | |
| Devices | GET | `/grandsafelife/api/v1/users/{owner_id}/devices` | Recupera dispositivos por administrador propietario. | Sí | Sí | - | queryDevicesByOwner | |
| Devices | GET | `/grandsafelife/api/v1/homes/{home_id}/devices` | Recupera dispositivos asociados a un hogar. | Sí | Sí | - | queryDevicesByHome | |
| Devices | GET | `/grandsafelife/api/v1/devices/{device_id}/location` | Recupera la última ubicación de un dispositivo. | Sí | Sí | - | getLocationByDevice | |
| Devices Stats | GET | `/grandsafelife/api/v1/devices/{device_id}/stats/daily?date={YYYY-MM-DD}` | Recupera métricas diarias. | Sí | Sí | Pendiente | getDailyMetrics | |
| Devices Stats | GET | `/grandsafelife/api/v1/devices/{device_id}/stats/monthly?month={YYYY-MM}` | Recupera agregados mensuales. | Sí | No | Pendiente | getMonthlyAggregates | |
| Devices Stats | GET | `/grandsafelife/api/v1/devices/{device_id}/stats/monthly/previous` | Recupera los agregados del mes anterior. | Sí | No | Pendiente | getPreviousMonthAggregates | |
| Devices Stats | GET | `/grandsafelife/api/v1/devices/{device_id}/stats/daily/last-week` | Recupera métricas de los últimos siete días. | Sí | Sí | Pendiente | getLastWeekMetrics | |
| Alarms | GET | `/grandsafelife/api/v1/devices/{device_id}/alarms` | Recupera las alarmas de un dispositivo. | Sí | Sí | Pendiente | getAlarmsByDeviceId | |
| Alarms | PUT | `/grandsafelife/api/v1/devices/{device_id}/alarms` | Reemplaza la configuración completa de alarmas. | Sí | No | Pendiente | setAlarmsByDeviceId | |
| Fall detection | POST | `/grandsafelife/api/v1/fall-detection/requests` | Envía un chunk y obtiene el ID del pedido. | No | - | - | - | |
| Fall detection | GET | `/grandsafelife/api/v1/fall-detection/requests/{request_id}` | Consulta el estado y resultado del pedido. | No | - | - | - | |

## 2 - Tabla de códigos de operación

| OP STATUS | BRIEF | SIGNIFICADO |
| ---: | --- | --- |
| 0 | `Operation completed successfully` | La operación fue atendida correctamente. |
| 1 | `Processing request in progress` | Pedido en curso. |
| 2 | `Processing result ready` | Clasificación disponible. |
| 3 | `Processing request not found` | Pedido no encontrado. |
| 4 | `Processing request failed` | Fallo de procesamiento. |

## 3 - Convenciones generales

Todos los endpoints documentados requieren este header:

```http
Authorization: Bearer <firebase_id_token>
```

Las respuestas de las operaciones reportan:

- `op_status`
- `brief`
- `resp` (cuando corresponde)

La capa HTTP valida los bodies, parámetros y headers según las reglas de cada endpoint, utilizando Pydantic para los modelos.  Si un request no cumple esas reglas, responde con HTTP `422 Unprocessable Entity` y una lista de errores en `detail`, sin ejecutar la operación.

### Redirecciones

Las rutas se invocan sin barra final. Si se agrega una barra y existe la ruta sin ella, la API responde con `307 Temporary Redirect`, cuerpo vacío y el encabezado `Location` con la URL de destino, conservando el query string.

El cliente debe seguir `Location` conservando el método HTTP y el body original; no debe intentar interpretar la respuesta 307 como JSON. Para la misma API, debe conservar también el encabezado `Authorization`. Si la biblioteca HTTP no sigue redirecciones automáticamente, hay que habilitarlo o repetir la petición en la URL indicada. Usar directamente las rutas sin barra final evita este paso.

En el despliegue, el alojamiento puede agregar `Content-Type: text/html` a esa respuesta vacía; no significa que haya un documento HTML que procesar.

## 4 - Endpoints "Users"

### `GET /grandsafelife/api/v1/users/{user_id}`

- Descripción: recupera el perfil completo del usuario identificado por `user_id`, incluidos sus hogares y roles.
- Parámetro: `user_id` es el UID del usuario consultado.
- Body: no aplica.

Response:

```json
{
  "op_status": 0,
  "brief": "Operation completed successfully",
  "resp": {
    "id": "user_002",
    "name": "María Gómez",
    "email": "maria.gomez@example.com",
    "avatar": "https://example.com/avatars/user_002.png",
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
}
```

`id` coincide con el `user_id` solicitado. `created_at` y `updated_at` son
enteros en milisegundos desde Unix epoch. `avatar` puede ser `null`.
`homes` es un objeto indexado por ID de hogar; si el usuario no tiene hogares,
se devuelve `{}`.

### `GET /grandsafelife/api/v1/users/by-email?email={email}`

- Descripción: recupera el perfil completo del usuario identificado por `email`, incluidos sus hogares y roles.
- Parámetro: `email` se envía como query parameter.
- Body: no aplica.

Response:

```json
{
  "op_status": 0,
  "brief": "Operation completed successfully",
  "resp": {
    "id": "user_002",
    "name": "María Gómez",
    "email": "maria.gomez@example.com",
    "avatar": "https://example.com/avatars/user_002.png",
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
}
```

`id` es el UID del usuario encontrado; `email` coincide con el email consultado. `created_at` y `updated_at` son
enteros en milisegundos desde Unix epoch. `avatar` puede ser `null`.
`homes` es un objeto indexado por ID de hogar; si el usuario no tiene hogares,
se devuelve `{}`.

### `POST /grandsafelife/api/v1/users`

- Descripción: crea un documento de usuario o reemplaza por completo el del ID indicado.
- Function: `createUser(data, id: ...)`.

Body:

```json
{
  "user_id": "firebase_uid_001",
  "data": {
    "id": "firebase_uid_001",
    "name": "Juan Pérez",
    "email": "juan.perez@example.com",
    "avatar": null,
    "homes": {
      "home_id_001": {"home_name": "Casa", "role": "admin"}
    }
  }
}
```

`user_id` corresponde al argumento opcional `id` del datasource. Con un ID no
vacío, el servidor deberá crear o reemplazar ese documento completo (`set`, sin
merge). Si no se indica, deberá crear un documento con ID generado (`add`).
Flutter omite `user_id` si su argumento es `null` o vacío. El Bearer identifica
al solicitante para validar permisos; no sustituye al ID solicitado.

`data` contiene todos los campos recibidos por el datasource, incluidos `homes`,
campos adicionales y valores nulos. Un `id` o `user_id` dentro de `data` es un
campo del documento, no el selector de su ruta. No se inicializa `homes` vacío
si el cliente envía otro valor. El objeto `data` puede estar vacío.

Flutter omite `created_at` y `updated_at`: el servidor generará ambas fechas
actuales al crear y al reemplazar, sobrescribiendo cualquier valor previo.
La persistencia y los permisos quedan pendientes; el mock devuelve el ID
solicitado o `firebase_uid_mock` cuando se omite, sin guardar cambios.

Response:

```json
{
  "op_status": 0,
  "brief": "Operation completed successfully",
  "resp": {"user_id": "firebase_uid_001"}
}
```

Flutter retorna el string `resp.user_id`.

### `PATCH /grandsafelife/api/v1/users/{affected_user_id}`

- Descripción: actualiza parcialmente el perfil y los hogares del usuario identificado por `affected_user_id`.
- Parámetro: `affected_user_id` es el UID del usuario cuyo perfil se modifica. Puede ser el usuario de la sesión o un tercero, por ejemplo el invitado al agregarlo a un hogar o el miembro al desvincularlo.
- El token Bearer identifica a quien realiza la solicitud; `affected_user_id` identifica a quien recibe el cambio. Ambos pueden ser distintos.
- Cada request modifica un solo usuario. `homes` contiene los hogares de ese usuario, no una lista de usuarios invitados. Cuando Flutter elimina un hogar, envía una actualización por cada miembro afectado.

Body de ejemplo:

```json
{
  "name": "Juan P. Pérez",
  "avatar": null,
  "homes": {
    "home_id_001": {"home_name": "Residencia Principal", "role": "admin"}
  }
}
```

Response:

```json
{
  "op_status": 0,
  "brief": "Operation completed successfully"
}
```

El body contiene todos los campos recibidos por `updateUser`, incluidos `id`,
campos adicionales, mapas, listas y valores `null`. No se limita a los campos
del perfil. `id` dentro del body es un dato del documento: el usuario destino
se determina exclusivamente por la ruta.

Los campos omitidos se conservan. `homes` reemplaza el mapa completo y `{}` lo
vacía; `homes.home_id_001.role` actualiza solamente esa ruta. Un valor `null`
se guarda como tal, no elimina el campo. El servidor deberá aplicar `update`
al documento existente y devolver un error si no existe.

Flutter omite `updated_at`, que el servidor generará en cada actualización.
`created_at` se conserva si no se envía; si viene como `Timestamp`, Flutter lo
envía en milisegundos Unix y el servidor deberá convertirlo al guardar la fecha.
No se regenera automáticamente la fecha de creación.

Actualmente la operación confirma la recepción sin persistir cambios ni verificar
el token. La validación de permisos sobre el usuario y sus hogares queda pendiente.

## 5 - Endpoints "Homes"

### `GET /grandsafelife/api/v1/homes/{home_id}`

- Descripción: recupera el hogar si el usuario autenticado posee acceso.
- Body: no aplica.

Response:

```json
{
  "op_status": 0,
  "brief": "Operation completed successfully",
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

`created_at` y `updated_at` son enteros en milisegundos Unix. Flutter los convierte
a `Timestamp` conservando su valor y agrega `id` desde la ruta. Los UID de
`members` identifican a los integrantes del hogar; los del ejemplo son ficticios.

### `POST /grandsafelife/api/v1/homes`

- Descripción: crea o reemplaza el documento completo de un hogar.

Body:

```json
{
  "home_id": "home_id_001",
  "data": {
    "name": "Residencia Principal",
    "members": {
      "user_id_001": {"email": "juan.perez@example.com", "role": "admin"}
    }
  }
}
```

`home_id` corresponde al argumento opcional `id` de `createHome`. Flutter lo
omite cuando es nulo o vacío. Con ID, el servidor deberá ejecutar `set(data)`
sin merge: crear o reemplazar todo el documento. Sin ID, deberá ejecutar `add(data)`
y devolver el ID generado. Un campo `id` o `home_id` dentro de `data` es un dato
del documento y no selecciona su ruta.

`data` conserva todos los campos recibidos, incluidos mapas, campos adicionales
y valores nulos; puede ser `{}`. Flutter omite `created_at` y `updated_at` porque
el servidor generará ambas fechas actuales, tanto al crear como al reemplazar.
La app actualiza `user.homes` por separado.

Response:

```json
{"op_status": 0, "brief": "Operation completed successfully", "resp": "home_id_001"}
```

Flutter retorna el ID recibido. El mock devuelve el ID solicitado o `home_id_001`
si no se indicó, sin persistencia ni validación real del token.

### `PATCH /grandsafelife/api/v1/homes/{home_id}`

- Descripción: actualiza parcialmente los campos editables de un hogar.

Body de ejemplo:

```json
{
  "name": "Nuevo nombre de la residencia"
}
```

Response:

```json
{
  "op_status": 0,
  "brief": "Operation completed successfully"
}
```

El body conserva todos los campos recibidos por `updateHome`, incluidos `id`,
campos adicionales, valores nulos y rutas con puntos como `members.user_id_001.role`.
El hogar destino se determina por la ruta, no por un campo `id` dentro del body.
Los campos omitidos se conservan. Un mapa `members` reemplaza ese campo completo;
`{}` lo vacía y una ruta con puntos modifica solo el campo indicado.

Flutter omite `updated_at`, que generará el servidor en cada actualización.
Si se recibe `created_at` como `Timestamp`, se envía en milisegundos Unix para
convertirlo al persistir; si se omite, se conserva. El servidor deberá aplicar
`homes.doc(home_id).update(data)` y fallar si el documento no existe.
Actualmente confirma la recepción sin persistir cambios ni verificar el token.

### `DELETE /grandsafelife/api/v1/homes/{home_id}`

- Descripción: elimina el hogar indicado. Flutter desvincula antes a sus miembros y libera sus dispositivos mediante llamadas separadas.
- Body: no aplica.

Response:

```json
{
  "op_status": 0,
  "brief": "Operation completed successfully"
}
```

Actualmente confirma la recepción sin persistir cambios ni verificar el token.
La implementación persistente deberá validar rol administrador y ejecutar
`homes.doc(home_id).delete()`: elimina únicamente ese documento, no la colección,
otros documentos ni subcolecciones. Si no existe, también es exitoso. No genera fechas.

## 6 - Endpoints "Monitoring requests"

Las solicitudes usan `pending`, `accepted` y `rejected` como estados. Estos
valores no son roles; los roles admitidos para una invitación son `admin` y
`observer`.

### `POST /grandsafelife/api/v1/homes/{home_id}/monitoring-requests`

- Descripción: invita por email a otro usuario a participar del hogar.

Body:

```json
{
  "email": "maria.gomez@example.com",
  "role": "observer"
}
```

Response:

```json
{
  "op_status": 0,
  "brief": "Operation completed successfully",
  "resp": "request_id_001"
}
```

El servidor obtiene al solicitante desde el token, comprueba su rol
administrador y resuelve internamente al destinatario mediante el email. El body
no admite IDs, estado ni timestamps.

### `GET /grandsafelife/api/v1/users/me/monitoring-requests`

- Descripción: recupera inicialmente las solicitudes pendientes recibidas por el usuario autenticado.
- Body: no aplica.

Response:

```json
{
  "op_status": 0,
  "brief": "Operation completed successfully",
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

Si posteriormente se necesitan solicitudes enviadas o históricas, se agregará
un filtro explícito al contrato.

### `POST /grandsafelife/api/v1/monitoring-requests/{request_id}/answer`

- Descripción: permite al destinatario aceptar o rechazar una solicitud pendiente.

Body:

```json
{
  "answer": "accepted"
}
```

`answer` admite únicamente `accepted` o `rejected`.

Response:

```json
{
  "op_status": 0,
  "brief": "Operation completed successfully"
}
```

Al aceptar, el servidor agregará atómicamente al usuario en `home.members` y el
hogar en `user.homes`, utilizando el rol pedido. Al rechazar, no modificará las
membresías.

## 7 - Endpoints "Devices"

El datasource permite leer, crear o reemplazar, actualizar y eliminar documentos
de dispositivos. La pantalla de asociación utiliza `updateDevice` sobre un
dispositivo existente. El registro de un dispositivo y su asociación son operaciones distintas.

Las fechas se expresan en milisegundos Unix. Flutter las convierte a `Timestamp`.
Los tipos son `hub` y `pulsera`; para hubs sin batería se utiliza -1.
El ID de prueba `dev_available` devuelve propietario y hogar vacíos para probar
la asociación. Los mocks no persisten cambios. Los contratos conservan los campos
de los documentos consumidos por Flutter; no requieren cambiar las colecciones.
Autenticación, permisos y acceso a Firestore se implementarán en el servidor.

### `GET /grandsafelife/api/v1/devices/{device_id}`

- Descripción: recupera un dispositivo si el solicitante tiene acceso al hogar asociado.
- Body: no aplica.

Response:

```json
{
  "op_status": 0,
  "brief": "Operation completed successfully",
  "resp": {
    "id": "dev_a81f23",
    "created_at": 1786789934000,
    "updated_at": 1788286907000,
    "home_id": "home_7f3a92",
    "owner_id": "user_admin_001",
    "is_active": true,
    "type": "pulsera",
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

Si el documento no existe, la respuesta exitosa contiene `"resp": null` y Flutter
retorna `null`. Un documento existente vacío se representa como `{}` y Flutter
agrega su `id`. Se conservan todos los campos; las fechas presentes se convierten
a `Timestamp`, sin inventar fechas para documentos que no las tengan.

### `POST /grandsafelife/api/v1/devices`

- Descripción: crea un documento o reemplaza completamente el del ID indicado.
- Function: `createDevice(data, id: ...)`, disponible en el datasource aunque no
  se invoque actualmente desde las pantallas.

Body de ejemplo:

```json
{
  "device_id": "dev_a81f23",
  "data": {
    "id": "dev_a81f23",
    "name": "Pulsera",
    "type": "pulsera",
    "home_id": "",
    "owner_id": "",
    "connection_by": "",
    "battery": 80,
    "is_active": true,
    "coords": {"lat": -34.6037, "long": -58.3816}
  }
}
```

`device_id` es opcional: corresponde al argumento `id` del datasource y selecciona
el documento. Flutter lo omite cuando el argumento es `null` o vacío; el servidor
genera entonces un ID. Los campos dentro de `data`, incluido un eventual `id`,
son datos del documento y no seleccionan su ruta. `data` es un objeto JSON que
conserva campos adicionales, mapas, listas y valores nulos.

Al implementar persistencia, el servidor generará `created_at` y `updated_at`
al crear **y al reemplazar**, igual que `set(data)` sin merge. Flutter omite
esas dos fechas del request. El mock devuelve el ID recibido o genera uno,
sin guardar datos.

Response:

```json
{"op_status": 0, "brief": "Operation completed successfully", "resp": "dev_a81f23"}
```

El endpoint de asociación siguiente no es utilizado por el flujo actual de Flutter.

### `POST /grandsafelife/api/v1/devices/{device_id}/association`

- Descripción: vincula un dispositivo físico existente a un hogar.

Body:

```json
{
  "home_id": "home_7f3a92"
}
```

Response:

```json
{
  "op_status": 0,
  "brief": "Operation completed successfully",
  "resp": "dev_a81f23"
}
```

El servidor resuelve `owner_id` desde el administrador del hogar. El body no
admite ese campo ni información operativa del dispositivo.

### `PATCH /grandsafelife/api/v1/devices/{device_id}`

- Descripción: actualiza parcialmente los campos del documento del dispositivo.

Body de ejemplo:

```json
{
  "name": "Sensor Dormitorio",
  "connection_by": "hub_001"
}
```

Response:

```json
{
  "op_status": 0,
  "brief": "Operation completed successfully"
}
```

El body es el mapa parcial recibido por `updateDevice`: conserva `coords`, `id`,
campos adicionales, mapas anidados, rutas de campo con puntos y valores `null`.
No se restringe a una selección de campos del modelo Flutter. Los valores de
`created_at` que sean `Timestamp` se transportan como milisegundos Unix.
Flutter omite `updated_at`, que generará el servidor en cada actualización.

La persistencia deberá aplicar `update(data)`: conservar campos omitidos,
reemplazar los mapas enviados completos y actualizar solamente el campo indicado
cuando se use una ruta con puntos; fallar si el documento no existe. No regenerar
`created_at` automáticamente. Para asociar, la app envía hogar y propietario;
para liberar, ambos son strings vacíos. El mock confirma sin guardar cambios.

### `DELETE /grandsafelife/api/v1/devices/{device_id}`

- Descripción: elimina el documento del dispositivo, como `doc(id).delete()`.
- Function: `deleteDevice`.
- Body: no aplica.

Response:

```json
{"op_status": 0, "brief": "Operation completed successfully"}
```

El contrato elimina el documento y también acepta que ya no exista. No implica
borrar subcolecciones ni otros documentos. Flutter retorna `void`. El mock
confirma la operación sin persistencia.

### `DELETE /grandsafelife/api/v1/devices/{device_id}/association`

- Descripción: elimina la asociación actual y deja disponible el dispositivo.
- Body: no aplica.

Response:

```json
{
  "op_status": 0,
  "brief": "Operation completed successfully"
}
```

La operación elimina `home_id` y `owner_id`, pero conserva el registro físico y
sus estadísticas históricas.

### `GET /grandsafelife/api/v1/users/{owner_id}/devices`

- Descripción: recupera todos los documentos cuyo `owner_id` coincide con el indicado, incluidos hubs.
- Body: no aplica.

Response:

```json
{
  "op_status": 0,
  "brief": "Operation completed successfully",
  "resp": {
    "dev_a81f23": {
      "created_at": 1786789934000,
      "updated_at": 1788286907000,
      "home_id": "home_7f3a92",
      "owner_id": "user_admin_001",
      "is_active": true,
      "type": "pulsera",
      "battery": 87,
      "name": "Sensor Living",
      "connection_by": "hub_001",
      "coords": {
        "lat": -34.6037,
        "long": -58.3816
      }
    }
  }
}
```

El resultado es un objeto indexado por ID. Si no hay dispositivos accesibles,
`resp` es `{}`.

### `GET /grandsafelife/api/v1/homes/{home_id}/devices`

- Descripción: recupera los dispositivos monitoreados asociados a un hogar.
- Body: no aplica.

Response:

```json
{
  "op_status": 0,
  "brief": "Operation completed successfully",
  "resp": {
    "dev_a81f23": {
      "created_at": 1786789934000,
      "updated_at": 1788286907000,
      "home_id": "home_7f3a92",
      "owner_id": "user_admin_001",
      "is_active": true,
      "type": "pulsera",
      "battery": 87,
      "name": "Sensor Living",
      "connection_by": "hub_001",
      "coords": {
        "lat": -34.6037,
        "long": -58.3816
      }
    },
    "dev_b42c91": {
      "created_at": 1785247863000,
      "updated_at": 1788285492000,
      "home_id": "home_7f3a92",
      "owner_id": "user_admin_001",
      "is_active": true,
      "type": "hub",
      "battery": -1,
      "name": "Hub Entrada",
      "connection_by": "hub_001",
      "coords": {
        "lat": -34.6032,
        "long": -58.3809
      }
    },
    "dev_c73e15": {
      "created_at": 1785663927000,
      "updated_at": 1788285931000,
      "home_id": "home_7f3a92",
      "owner_id": "user_admin_001",
      "is_active": false,
      "type": "pulsera",
      "battery": 31,
      "name": "Sensor Dormitorio",
      "connection_by": "",
      "coords": {
        "lat": -34.6041,
        "long": -58.3824
      }
    }
  }
}
```

Los hubs se incluyen, como en la consulta original de Firestore. Si el hogar no tiene dispositivos,
`resp` es `{}`.

### `GET /grandsafelife/api/v1/devices/{device_id}/location`

- Descripción: recupera la última ubicación GPS reportada por el dispositivo.
- Body: no aplica.

Response:

```json
{
  "op_status": 0,
  "brief": "Operation completed successfully",
  "resp": {
    "lat": -34.6037,
    "long": -58.3816
  }
}
```

La respuesta de ubicación usa `lat` y `long` numéricos. El datasource convierte
`long` a `lng` para el mapa de Flutter, conservando los valores recibidos.

## 8 - Endpoints "Devices Stats"

Las métricas son de solo lectura para la aplicación. Su carga, procesamiento y
agregación corresponden a los dispositivos y al servidor.

### `GET /grandsafelife/api/v1/devices/{device_id}/stats/daily?date={YYYY-MM-DD}`

- Descripción: recupera las métricas de un dispositivo para la fecha solicitada.
- Body: no aplica. `date` es un query parameter con formato `YYYY-MM-DD`.

Response:

```json
{
  "op_status": 0,
  "brief": "Operation completed successfully",
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

Si no existen datos para la fecha solicitada, `resp` es `{}`.

### `GET /grandsafelife/api/v1/devices/{device_id}/stats/monthly?month={YYYY-MM}`

- Descripción: recupera los agregados calculados para el mes solicitado.
- Body: no aplica. `month` es un query parameter con formato `YYYY-MM`.

Response:

```json
{
  "op_status": 0,
  "brief": "Operation completed successfully",
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

Si no existen datos para el mes solicitado, `resp` es `{}`.

### `GET /grandsafelife/api/v1/devices/{device_id}/stats/monthly/previous`

- Descripción: recupera los agregados del mes calendario anterior, calculado por el servidor.
- Body: no aplica.

Response:

```json
{
  "op_status": 0,
  "brief": "Operation completed successfully",
  "resp": {
    "id": "2026-08",
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

Si no existen agregados para el mes anterior, `resp` es `{}`.

### `GET /grandsafelife/api/v1/devices/{device_id}/stats/daily/last-week`

- Descripción: recupera los días con datos dentro de los últimos siete días, incluido el actual.
- Body: no aplica.

Response:

```json
{
  "op_status": 0,
  "brief": "Operation completed successfully",
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

El array está ordenado del día más antiguo al más reciente y omite los días sin
datos. Si el período completo está vacío, `resp` es `[]`.

## 9 - Endpoints "Alarms"

Las alarmas se representan como un objeto cuyas claves son sus IDs. El servidor
administra sus estados y timestamps; la aplicación solamente configura nombre,
horario, días e indicador de actividad.

### `GET /grandsafelife/api/v1/devices/{device_id}/alarms`

- Descripción: recupera todas las alarmas configuradas para un dispositivo.
- Body: no aplica.

Response:

```json
{
  "op_status": 0,
  "brief": "Operation completed successfully",
  "resp": {
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
}
```

`time_in_minutes` representa minutos desde la medianoche. `days` es una máscara
de bits para los días de la semana. `state` puede ser `none`, `pending`, `taken`
o `missed`. Si el dispositivo no tiene alarmas, `resp` es `{}`.

### `PUT /grandsafelife/api/v1/devices/{device_id}/alarms`

- Descripción: reemplaza el mapa completo de alarmas del dispositivo.

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

Response:

```json
{
  "op_status": 0,
  "brief": "Operation completed successfully"
}
```

Las claves omitidas se consideran eliminadas y un body `{}` elimina todas las
alarmas. La aplicación no puede enviar `state`, `created_at` ni `updated_at`;
el servidor conserva o genera esos valores según corresponda. El horario debe
estar entre `0` y `1439` minutos.

## 10 - Endpoints "Fall detection"

Estado actual: las rutas devuelven respuestas fijas. No registran pedidos ni
ejecutan inferencia. La integración con `process_*`, autenticación efectiva,
permisos y ciclo de vida del pedido quedan pendientes. El header `Authorization`
es obligatorio, pero todavía no se verifica su token.

### `POST /grandsafelife/api/v1/fall-detection/requests`

- Descripción: envía datos para detección de caídas y obtiene un ID de pedido.
- Body: objeto JSON crudo, con estructura interna provisional hasta que se
  defina el chunk del detector. No se recibe un string que contenga JSON.
- HTTP: `200` para la recepción; `422` si falta el body o el header, o el body
  no es un objeto JSON. La aceptación no indica que la clasificación esté lista.
- Implementación actual: retorna siempre el ID de ejemplo `1`; no genera un
  ID único ni conserva el body. El manager asignará los IDs en una etapa posterior.

Body (ejemplo estructural, no define el formato de los sensores):

```json
{}
```

Response:

```json
{
  "op_status": 0,
  "brief": "Operation completed successfully",
  "resp": { "request_id": 1 }
}
```

### `GET /grandsafelife/api/v1/fall-detection/requests/{request_id}`

- Descripción: consulta el pedido identificado por `request_id`.
- Parámetro: `request_id` es un entero positivo generado por el servidor.
- Body: no aplica.
- Implementación actual: cualquier ID válido devuelve pedido en curso; todavía no se consulta su existencia. Los demás resultados quedan declarados en el contrato HTTP documentado aquí para la integración posterior.
- Un ID inválido o la ausencia del header produce HTTP `422`.
- Conocer un ID no otorgará permisos: el caso de uso deberá verificar acceso.

Response:

Pedido en curso — HTTP `200`:

```json
{
  "op_status": 1,
  "brief": "Processing request in progress",
  "resp": { "request_id": 1 }
}
```

Resultado listo — HTTP `200`:

```json
{
  "op_status": 2,
  "brief": "Processing result ready",
  "resp": { "request_id": 1, "is_fall": true }
}
```

`is_fall` puede ser `true` o `false` y solamente aparece en un resultado listo.

Pedido no encontrado — HTTP `400`:

```json
{
  "op_status": 3,
  "brief": "Processing request not found",
  "resp": { "request_id": 1 }
}
```

Pedido fallido por un error interno de procesamiento — HTTP `500`:

```json
{
  "op_status": 4,
  "brief": "Processing request failed",
  "resp": { "request_id": 1, "error_code": "PROCESSING_ERROR" }
}
```

`error_code` es un código público de procesamiento, nunca un traceback ni un
mensaje interno del proveedor. Su catálogo definitivo y el tratamiento de datos
rechazados por el detector quedan pendientes de la integración del caso de uso.
