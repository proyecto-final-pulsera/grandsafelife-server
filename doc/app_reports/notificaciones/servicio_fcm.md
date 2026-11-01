# FCM: Flutter Android + servidor

## Instalación

Creá un proyecto en Firebase Console. Con Firebase CLI instalada, ejecutá desde la app Flutter:

```sh
firebase login
flutter pub add firebase_core firebase_messaging
dart pub global activate flutterfire_cli
flutterfire configure --project=ID_DEL_PROYECTO --platforms=android
```

Esto genera `lib/firebase_options.dart`. Inicializá Firebase en `main.dart`:

```dart
import 'package:flutter/material.dart';
import 'package:firebase_core/firebase_core.dart';
import 'package:firebase_messaging/firebase_messaging.dart';
import 'firebase_options.dart';

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await Firebase.initializeApp(
    options: DefaultFirebaseOptions.currentPlatform,
  );
  runApp(const MyApp());
}
```

## Token y recepción

Luego de inicializar Firebase:

```dart
final messaging = FirebaseMessaging.instance;
await messaging.requestPermission();
final token = await messaging.getToken();
```

El token identifica una instalación, no una sesión. **Enviarlo al servidor o gestor de notificaciones**, asociado al usuario autenticado. Actualizarlo mediante `messaging.onTokenRefresh` y desvincularlo al cerrar sesión. Un usuario puede tener varios tokens.

Con la app abierta, recibir mediante `FirebaseMessaging.onMessage.listen(...)` y mostrar el aviso desde la app. En segundo plano, Android muestra los mensajes que incluyen `notification`. Esto no abre automáticamente una pantalla de alarma.

## Envío desde Java

Usar Firebase Admin SDK en el servidor. En Firebase Console → Configuración del proyecto → Cuentas de servicio, generar una clave privada. Guardarla como `service-account.json`, fuera de Git y de la app.

```java
// Imports de com.google.auth.oauth2, com.google.firebase,
// com.google.firebase.messaging y java.io.FileInputStream.
try (var credentials = new FileInputStream("service-account.json")) {
    FirebaseApp.initializeApp(FirebaseOptions.builder()
        .setCredentials(GoogleCredentials.fromStream(credentials))
        .build());
}

Message message = Message.builder()
    .setToken("TOKEN_DEL_DISPOSITIVO")
    .setNotification(Notification.builder()
        .setTitle("Alerta")
        .setBody("Un familiar necesita ayuda")
        .build())
    .build();

FirebaseMessaging.getInstance().send(message);
```

Para varios usuarios, el servidor obtiene los tokens de sus dispositivos y envía a esos destinatarios; no requiere tópicos.