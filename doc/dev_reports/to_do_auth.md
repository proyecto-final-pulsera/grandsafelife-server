# Pendiente: autenticación entre Flutter y el servidor

## Objetivo

Definir e implementar la autenticación de los requests enviados por la
aplicación Flutter a la API REST de Grand Safe Life.

Firebase Authentication continuará realizando el registro y el inicio de sesión
desde la aplicación. El backend no recibe contraseñas ni implementa un endpoint
de login propio. Sin embargo, el backend debe verificar la identidad de quien
realiza cada request antes de ejecutar operaciones o controlar permisos.

---

## Distinción entre UID e ID token

Firebase expone ambos valores, pero tienen responsabilidades diferentes:

* El `uid` es el identificador estable del usuario dentro del proyecto Firebase.
* El ID token es un JWT firmado por Firebase que demuestra que el cliente posee
  una sesión autenticada válida.

El UID no es una credencial. Enviarlo solo y comprobar que existe en Firebase
Authentication no demuestra que el request haya sido realizado por ese usuario.
Cualquier cliente podría copiar o reemplazar ese valor.

Por ese motivo, Flutter debe enviar el ID token. El servidor verifica el token y
extrae de él el UID que utilizará como fuente de verdad.

```text
Flutter inicia sesión con Firebase Authentication
                    |
                    v
Flutter obtiene el Firebase ID token
                    |
                    v
Authorization: Bearer <ID token>
                    |
                    v
FastAPI verifica firma, formato y vigencia
                    |
                    v
FastAPI extrae el UID confiable
                    |
                    v
System valida permisos y ejecuta el caso de uso
```

---

## Recuperación del token en Flutter

El paquete `firebase_auth` expone el método:

```dart
Future<String?> getIdToken([bool forceRefresh = false])
```

Ejemplo:

```dart
final firebaseUser = FirebaseAuth.instance.currentUser;

if (firebaseUser == null) {
  throw StateError('Usuario no autenticado');
}

final idToken = await firebaseUser.getIdToken();

if (idToken == null) {
  throw StateError('No se pudo obtener el Firebase ID token');
}
```

No debe forzarse la renovación en cada request. Con `getIdToken()` Firebase
reutiliza el token actual si todavía es válido y solicita uno nuevo cuando hace
falta. `getIdToken(true)` queda reservado para situaciones en las que exista una
razón concreta para forzar la renovación.

El token se envía a la API mediante HTTPS:

```dart
final response = await http.get(
  Uri.parse('$baseUrl/grandsafelife/api/v1/users/me'),
  headers: {
    'Authorization': 'Bearer $idToken',
  },
);
```

Esta obtención y agregado del header debería centralizarse en el cliente HTTP de
la aplicación y no repetirse manualmente en cada pantalla o repository.

---

## Verificación del token en FastAPI

El backend utilizará Firebase Admin SDK para verificar el ID token:

```python
from firebase_admin import auth

decoded_token = auth.verify_id_token(id_token)
current_user_uid = decoded_token["uid"]
```

La extracción del header, validación del esquema `Bearer` y verificación del
token deben centralizarse en una dependencia reutilizable de FastAPI.

Ejemplo conceptual:

```python
from fastapi import Header
from firebase_admin import auth


def get_current_user_uid(authorization: str = Header(...)) -> str:
    scheme, _, token = authorization.partition(" ")

    if scheme.lower() != "bearer" or not token:
        raise InvalidAuthenticationError()

    decoded_token = auth.verify_id_token(token)
    return decoded_token["uid"]
```

Los endpoints reciben el UID ya verificado. La capa `system` utiliza ese UID
para validar permisos y relaciones antes de acceder a los repositories.

---

## Autenticación y autorización

Son verificaciones diferentes:

* Autenticación: validar el ID token y determinar quién realiza el request.
* Autorización: determinar si ese usuario puede ejecutar la operación solicitada
  sobre un hogar, dispositivo, métrica u otro usuario.

Ejemplo:

```http
GET /grandsafelife/api/v1/users/{target_user_id}
Authorization: Bearer <firebase_id_token>
```

En este caso:

* El ID token identifica al usuario solicitante.
* `target_user_id` identifica al usuario objetivo.
* `system` verifica si el solicitante tiene permiso para consultar al objetivo.

Para operaciones sobre el perfil propio no es necesario que Flutter envíe su
UID:

```http
GET /grandsafelife/api/v1/users/me
Authorization: Bearer <firebase_id_token>
```

El servidor obtiene el UID exclusivamente del token verificado.

---

## Registro y creación del perfil

Firebase Authentication crea la identidad autenticable desde Flutter. La API no
crea esa identidad ni genera su UID.

El endpoint de creación de usuario del servidor debe interpretarse como creación
del perfil de Grand Safe Life asociado a una identidad Firebase existente. El
servidor obtiene el UID desde el token y no debe confiar en un UID enviado en el
body.

Ejemplo conceptual:

```http
POST /grandsafelife/api/v1/users/me
Authorization: Bearer <firebase_id_token>
Content-Type: application/json

{
  "name": "Juan Pérez",
  "email": "juan.perez@example.com",
  "avatar": null
}
```

El documento podría persistirse internamente como `users/{uid_verificado}`.

---

## Inicio de sesión con Google

El `googleAuth.idToken` utilizado para construir una credencial de Google no es
el token que se envía al backend de Grand Safe Life.

Primero Flutter utiliza esa credencial para iniciar sesión en Firebase:

```dart
final googleCredential = GoogleAuthProvider.credential(
  idToken: googleAuth.idToken,
);

final userCredential =
    await FirebaseAuth.instance.signInWithCredential(googleCredential);
```

Después obtiene el Firebase ID token de la sesión resultante:

```dart
final firebaseIdToken = await userCredential.user?.getIdToken();
```

La API siempre recibe un Firebase ID token, independientemente de si el usuario
inició sesión mediante contraseña, Google u otro proveedor.

---

## Impacto esperado sobre los endpoints

La estructura funcional de los endpoints no cambia sustancialmente. Los cambios
transversales son:

* Los endpoints protegidos exigen `Authorization: Bearer <ID token>`.
* Una dependencia HTTP común verifica el token.
* Los processors reciben el UID autenticado ya validado.
* Los endpoints `/users/me` obtienen la identidad exclusivamente del token.
* Los IDs incluidos en una URL o body representan recursos objetivo, no la
  identidad autenticada del solicitante.
* `system` continúa siendo responsable de la autorización.

---

## Manejo de errores pendiente de definir

Se deben agregar códigos de operación propios y sus `brief` unívocos para, como
mínimo:

* Header `Authorization` ausente.
* Esquema distinto de `Bearer`.
* Token vacío.
* Token inválido o mal firmado.
* Token vencido.
* Usuario autenticado sin permisos para la operación.

También queda pendiente confirmar el código HTTP exacto para autenticación y
autorización. La opción REST convencional sería utilizar `401` para identidad no
válida y `403` para permisos insuficientes, manteniendo siempre el `op_status`
propio dentro del response.

---

## Tareas pendientes

1. Confirmar el contrato final del header de autenticación.
2. Definir dónde vivirá la dependencia común de FastAPI.
3. Inicializar Firebase Admin SDK del lado servidor.
4. Definir los códigos de operación de autenticación en `api_op_codes.py`.
5. Implementar la verificación del token.
6. Crear pruebas para token válido, ausente, inválido y usuario sin permisos.
7. Ajustar los endpoints de usuario para distinguir `/users/me` de operaciones
   autorizadas sobre otros usuarios.
8. Coordinar con Guido la incorporación de `getIdToken()` al cliente HTTP.

---

## Referencias

* [Firebase: verificar ID tokens en un backend propio](https://firebase.google.com/docs/auth/admin/verify-id-tokens?hl=es-419)
* [FlutterFire `User.getIdToken()`](https://pub.dev/documentation/firebase_auth/latest/firebase_auth/User/getIdToken.html)
* [Firebase Admin Authentication](https://firebase.google.com/docs/auth/admin)
* [Firebase Admin SDK para el servidor](https://firebase.google.com/docs/admin/setup)
