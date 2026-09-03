# Documentación API REST

## 1 - Listado de endpoints

| CONJUNTO | MÉTODO | URL | DESCRIPCIÓN |
| --- | --- | --- | --- |
| Users | GET | `/grandsafelife/api/v1/users/me` | Recupera el perfil del usuario autenticado. |
| Users | GET | `/grandsafelife/api/v1/users/{user_id}` | Recupera información pública de otro usuario por UID. |
| Users | GET | `/grandsafelife/api/v1/users/by-email?email={email}` | Recupera información pública de otro usuario por email. |
| Users | POST | `/grandsafelife/api/v1/users/me` | Crea el perfil del usuario autenticado. |
| Users | PATCH | `/grandsafelife/api/v1/users/me` | Actualiza parcialmente el perfil del usuario autenticado. |
| Homes | GET | `/grandsafelife/api/v1/homes/{home_id}` | Recupera un hogar accesible por ID. |
| Homes | POST | `/grandsafelife/api/v1/homes` | Crea un hogar para el usuario autenticado. |
| Homes | PATCH | `/grandsafelife/api/v1/homes/{home_id}` | Actualiza parcialmente un hogar. |
| Homes | DELETE | `/grandsafelife/api/v1/homes/{home_id}` | Elimina un hogar y sus relaciones. |
| Monitoring requests | POST | `/grandsafelife/api/v1/homes/{home_id}/monitoring-requests` | Invita a un usuario a participar de un hogar. |
| Monitoring requests | GET | `/grandsafelife/api/v1/users/me/monitoring-requests` | Recupera las solicitudes pendientes recibidas. |
| Monitoring requests | POST | `/grandsafelife/api/v1/monitoring-requests/{request_id}/answer` | Acepta o rechaza una solicitud pendiente. |
| Devices | GET | `/grandsafelife/api/v1/devices/{device_id}` | Recupera un dispositivo accesible por ID. |
| Devices | POST | `/grandsafelife/api/v1/devices/{device_id}/association` | Asocia un dispositivo existente a un hogar. |
| Devices | PATCH | `/grandsafelife/api/v1/devices/{device_id}` | Actualiza la configuración editable de un dispositivo. |
| Devices | DELETE | `/grandsafelife/api/v1/devices/{device_id}/association` | Libera un dispositivo sin eliminarlo. |
| Devices | GET | `/grandsafelife/api/v1/users/{owner_id}/devices` | Recupera dispositivos por administrador propietario. |
| Devices | GET | `/grandsafelife/api/v1/homes/{home_id}/devices` | Recupera dispositivos asociados a un hogar. |
| Devices | GET | `/grandsafelife/api/v1/devices/{device_id}/location` | Recupera la última ubicación de un dispositivo. |
| Devices Stats | GET | `/grandsafelife/api/v1/devices/{device_id}/stats/daily?date={YYYY-MM-DD}` | Recupera métricas diarias. |
| Devices Stats | GET | `/grandsafelife/api/v1/devices/{device_id}/stats/monthly?month={YYYY-MM}` | Recupera agregados mensuales. |
| Devices Stats | GET | `/grandsafelife/api/v1/devices/{device_id}/stats/monthly/previous` | Recupera los agregados del mes anterior. |
| Devices Stats | GET | `/grandsafelife/api/v1/devices/{device_id}/stats/daily/last-week` | Recupera métricas de los últimos siete días. |
| Alarms | GET | `/grandsafelife/api/v1/devices/{device_id}/alarms` | Recupera las alarmas de un dispositivo. |
| Alarms | PUT | `/grandsafelife/api/v1/devices/{device_id}/alarms` | Reemplaza la configuración completa de alarmas. |

## 2 - Tabla de códigos de operación

| OP STATUS | BRIEF | SIGNIFICADO |
| ---: | --- | --- |
| 0 | `Operation completed successfully` | La operación fue atendida correctamente. |

## 3 - Convenciones generales

Todos los endpoints documentados requieren este header:

```http
Authorization: Bearer <firebase_id_token>
```

Todas las respuestas reportan:
- `op_status`
- `brief`
- `resp` (Cuando corrresponde)

Los bodies, parámetros y headers se validan mediante FastAPI/Pydantic. Cuando
un request no cumple el esquema declarado, FastAPI responde automáticamente con
HTTP `422 Unprocessable Entity` y no ejecuta la función `process_*`.


## 4 - Endpoints "Users"

### `GET /grandsafelife/api/v1/users/me`

- Descripción: recupera la identidad y el perfil completo del usuario autenticado.
- Body: no aplica.

Response:

```json
{
  "op_status": 0,
  "brief": "Operation completed successfully",
  "resp": {
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
}
```

### `GET /grandsafelife/api/v1/users/{user_id}`

- Descripción: recupera solamente información pública del usuario objetivo.
- Body: no aplica.

Response:

```json
{
  "op_status": 0,
  "brief": "Operation completed successfully",
  "resp": {
    "name": "María Gómez",
    "email": "maria.gomez@example.com",
    "avatar": "https://example.com/avatars/user_002.png"
  }
}
```

### `GET /grandsafelife/api/v1/users/by-email?email={email}`

- Descripción: recupera solamente información pública del usuario correspondiente al email.
- Body: no aplica. `email` se envía como query parameter.

Response:

```json
{
  "op_status": 0,
  "brief": "Operation completed successfully",
  "resp": {
    "name": "María Gómez",
    "email": "maria.gomez@example.com",
    "avatar": "https://example.com/avatars/user_002.png"
  }
}
```

### `POST /grandsafelife/api/v1/users/me`

- Descripción: crea el perfil asociado al UID contenido en el token verificado.

Body:

```json
{
  "name": "Juan Pérez",
  "email": "juan.perez@example.com",
  "avatar": "https://example.com/avatars/user_001.png"
}
```

Response:

```json
{
  "op_status": 0,
  "brief": "Operation completed successfully",
  "resp": {
    "user_id": "firebase_uid_mock"
  }
}
```

El body no admite UID, `homes`, `created_at` ni `updated_at`.

### `PATCH /grandsafelife/api/v1/users/me`

- Descripción: actualiza parcialmente los campos editables del perfil autenticado.

Body de ejemplo:

```json
{
  "name": "Juan P. Pérez",
  "avatar": "https://example.com/avatars/user_001_updated.png"
}
```

Response:

```json
{
  "op_status": 0,
  "brief": "Operation completed successfully"
}
```

El body admite solamente `name`, `email` y `avatar`. No permite modificar UID,
`homes`, `created_at` ni `updated_at`.

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

### `POST /grandsafelife/api/v1/homes`

- Descripción: crea un hogar y agrega al usuario autenticado como administrador.

Body:

```json
{
  "name": "Residencia Principal"
}
```

Response:

```json
{
  "op_status": 0,
  "brief": "Operation completed successfully",
  "resp": "home_id_001"
}
```

El ID, los timestamps y el mapa inicial de miembros son responsabilidad del
servidor. El body no permite enviar esos campos.

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

Este endpoint solamente admite `name`. Los miembros deberán gestionarse
mediante las operaciones específicas de negocio.

### `DELETE /grandsafelife/api/v1/homes/{home_id}`

- Descripción: elimina el hogar y sus referencias en los perfiles relacionados.
- Body: no aplica.

Response:

```json
{
  "op_status": 0,
  "brief": "Operation completed successfully"
}
```

La implementación definitiva exigirá rol administrador y realizará toda la
operación de manera consistente desde el servidor.

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

Los dispositivos físicos existen previamente y poseen un ID único e inmutable.
La aplicación puede asociarlos a un hogar, configurarlos o liberarlos, pero no
crear ni eliminar el registro de hardware.

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

- Descripción: actualiza parcialmente el nombre o la conexión del dispositivo.

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

`connection_by` admite el ID de un hub válido para el hogar o `"-1"` cuando no
se utiliza un hub. Los demás campos del dispositivo no son editables por esta
operación.

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

- Descripción: recupera los dispositivos pertenecientes a hogares administrados por el usuario indicado.
- Body: no aplica.

Response:

```json
{
  "op_status": 0,
  "brief": "Operation completed successfully",
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

Los hubs de infraestructura no se incluyen. Si el hogar no tiene dispositivos,
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
