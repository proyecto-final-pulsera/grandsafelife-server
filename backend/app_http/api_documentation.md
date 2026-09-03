# Documentación API REST

## Convenciones generales

Todos los endpoints documentados requieren este header:

```http
Authorization: Bearer <firebase_id_token>
```

Mientras la autenticación real permanezca pendiente, el header es obligatorio
pero su contenido todavía no se verifica. Todas las respuestas utilizan el
envelope `op_status`, `brief` y, cuando corresponde, `resp`.

## Listado de endpoints

| CONJUNTO | MÉTODO | URL | DESCRIPCIÓN |
| --- | --- | --- | --- |
| Users | GET | `/grandsafelife/api/v1/users/me` | Recupera el perfil del usuario autenticado. |
| Users | GET | `/grandsafelife/api/v1/users/{user_id}` | Recupera información pública de otro usuario por UID. |
| Users | GET | `/grandsafelife/api/v1/users/by-email?email={email}` | Recupera información pública de otro usuario por email. |
| Users | POST | `/grandsafelife/api/v1/users/me` | Crea el perfil del usuario autenticado. |
| Users | PATCH | `/grandsafelife/api/v1/users/me` | Actualiza parcialmente el perfil del usuario autenticado. |

## Endpoints "Users"

### Obtener el usuario actual

- URL: `/grandsafelife/api/v1/users/me`
- Método: `GET`
- Descripción: recupera la identidad y el perfil completo del usuario autenticado.
- Body: no aplica.

Response mock:

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

### Obtener un usuario por UID

- URL: `/grandsafelife/api/v1/users/{user_id}`
- Método: `GET`
- Descripción: recupera solamente información pública del usuario objetivo.
- Body: no aplica.

Response mock:

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

### Obtener un usuario por email

- URL: `/grandsafelife/api/v1/users/by-email?email={email}`
- Método: `GET`
- Descripción: recupera solamente información pública del usuario correspondiente al email.
- Body: no aplica. `email` se envía como query parameter.

Response mock:

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

### Crear el perfil del usuario actual

- URL: `/grandsafelife/api/v1/users/me`
- Método: `POST`
- Descripción: crea el perfil asociado al UID contenido en el token verificado.

Body:

```json
{
  "name": "Juan Pérez",
  "email": "juan.perez@example.com",
  "avatar": "https://example.com/avatars/user_001.png"
}
```

Response mock:

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

### Actualizar el perfil del usuario actual

- URL: `/grandsafelife/api/v1/users/me`
- Método: `PATCH`
- Descripción: actualiza parcialmente los campos editables del perfil autenticado.

Body de ejemplo:

```json
{
  "name": "Juan P. Pérez",
  "avatar": "https://example.com/avatars/user_001_updated.png"
}
```

Response mock:

```json
{
  "op_status": 0,
  "brief": "Operation completed successfully"
}
```

El body admite solamente `name`, `email` y `avatar`. No permite modificar UID,
`homes`, `created_at` ni `updated_at`.

## Tabla de códigos de operación

| OP STATUS | BRIEF | SIGNIFICADO |
| ---: | --- | --- |
| 0 | `Operation completed successfully` | La operación fue atendida correctamente. |

La tabla se ampliará a medida que se implementen resultados de error.

## Endpoints "Homes"

Pendiente del paso correspondiente.

## Endpoints "Devices"

Pendiente del paso correspondiente.

## Endpoints "Devices Stats"

Pendiente del paso correspondiente.

## Endpoints "Monitoring requests"

Pendiente del paso correspondiente.

## Endpoints "Alarms"

Pendiente del paso correspondiente.
