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

Pendiente del paso correspondiente.

## 8 - Endpoints "Devices Stats"

Pendiente del paso correspondiente.

## 9 - Endpoints "Alarms"

Pendiente del paso correspondiente.
