# Configuración de Firebase Storage para fotos de perfil

Fecha: 2026-09-28.

## Configuración

| Parámetro | Valor |
|---|---|
| Proyecto Firebase | `grand-safe-band` |
| Bucket | `grand-safe-band.firebasestorage.app` |
| Ruta de cada foto | `user_profile_img/{uid}` |
| Identidad | UID de Firebase Authentication |
| Tamaño máximo | 5 MiB: 5.242.880 bytes |
| Administración | Firebase Console → Storage → Rules |

La app de monitores accede directamente a Storage para las fotos de perfil.
La configuración adapta los permisos del bucket al flujo existente de la app.
El nombre del archivo es el UID del usuario, sin extensión obligatoria.

## Reglas configuradas en la consola

```text
rules_version = '2';

service firebase.storage {
  match /b/{bucket}/o {
    match /user_profile_img/{uid} {
      function esPropietario() {
        return request.auth != null && request.auth.uid == uid;
      }

      allow get: if esPropietario();

      allow create, update: if esPropietario()
        && request.resource.size <= 5 * 1024 * 1024;
    }
  }
}
```

| Operación | Permiso |
|---|---|
| `get` | Usuario autenticado cuyo UID coincide con el archivo |
| `create`, `update` | Mismo propietario, con archivo de hasta 5 MiB |
| `delete`, `list` | Denegado |
| Acceso por reglas a otras rutas | Denegado |

Estas reglas comprueban identidad y tamaño. No condicionan el acceso al
proveedor de login, correo verificado, rol ni documentos de Firestore.
Tampoco validan el tipo MIME o el contenido de la imagen.

## Uso desde la app

1. El usuario inicia sesión mediante Firebase Authentication.
2. `uploadProfilePicture` obtiene su UID y comprueba el tamaño del archivo.
3. `uploadProfileImage` sube la foto a `user_profile_img/{uid}` con `putFile`.
4. La app obtiene la URL mediante `getDownloadURL()` e intenta guardarla como
   `avatar` del usuario. La pantalla de perfil utiliza `Image.network`.

La URL de descarga contiene un token que permite acceder a quien posea el
enlace. La restricción de `get` al propietario controla las solicitudes
evaluadas por las reglas; no convierte esa URL compartible en una descarga
exclusiva de su sesión.

El guardado y la recuperación del campo `avatar` dependen del datasource de
usuarios. Actualmente esas operaciones REST utilizan placeholders, por lo que
el permiso de Storage por sí solo no completa la persistencia del avatar.

## Validación realizada

Resultados del simulador de la consola informados por el usuario, sobre
`user_profile_img/usuario-prueba`:

| Solicitud `get` | Resultado |
|---|---|
| Autenticado, UID `usuario-prueba` | Autorizada |
| Autenticado, UID `otro-usuario` | Rechazada |
| Sin autenticación | Rechazada |

El botón **Ejecutar** prueba las reglas; **Publicar** las aplica al bucket.
Una consulta posterior a Firebase Rules confirmó que las reglas publicadas
coinciden con las de este reporte. La publicación figura con fecha
2026-09-28 21:33:20 de Argentina (2026-09-29 00:33:20 UTC).

El usuario confirmó una carga real desde la app: un archivo `image/jpeg` de
28,38 KB en `user_profile_img/{uid}`, visible en la consola y coincidente con
la foto tomada desde el celular. Los logs muestran que el flujo alcanzó
`updateUser`, posterior a la subida y obtención de la URL de descarga.

La actualización del perfil sigue siendo un placeholder y su recarga devuelve
`avatar: null`; por eso la foto no aparece en la pantalla. La evidencia no
indica una URL incorrecta ni un fallo de carga en Storage.

Queda pendiente probar desde la app el reemplazo y la descarga/visualización
de fotos. También falta validar el rechazo de cargas mayores a 5 MiB, de
escrituras sobre fotos ajenas y de operaciones de borrado/listado.

## Referencias

- [Condiciones de las reglas de Storage](https://firebase.google.com/docs/storage/security/rules-conditions).
- [Administración y publicación de reglas](https://firebase.google.com/docs/rules/manage-deploy).
- [URL de descarga con token](https://firebase.google.com/docs/reference/android/com/google/firebase/storage/StorageReference#getDownloadUrl()).
