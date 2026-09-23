# Grand Safe Life — Reporte de la prueba de concepto de Cloud Functions

Fecha: 23 de septiembre de 2026.

## 1. Objetivo y resultado

El objetivo fue comprobar si Cloud Functions for Firebase permite alojar un backend HTTP escrito en Python, evitando administrar un servidor y conservando la posibilidad de utilizar la arquitectura por capas del proyecto.

**La prueba mínima fue exitosa tanto localmente como en Google Cloud.** Se desplegó una función HTTP que recibe un texto, lo guarda en Firestore y devuelve el ID del documento creado. El usuario verificó la respuesta y la existencia del documento en ambas pruebas.

Esto valida el recorrido HTTP → Python → Firestore. No implica que ya se haya migrado el backend completo, implementado autenticación ni probado notificaciones FCM.

## 2. Elección de hosting

Se tomó como referencia Cloud Functions de segunda generación, basada en Cloud Run. Google construye y ejecuta el código en contenedores; en el flujo utilizado no fue necesario escribir un Dockerfile ni administrar esos contenedores manualmente.

Las funciones HTTP son adecuadas como punto de entrada a los casos de uso del backend. Pueden importar módulos Python y llamar a clases, servicios y repositorios. La organización por capas no requiere un mecanismo especial de Firebase.

Durante la migración habrá que revisar dependencias y cualquier supuesto de ejecución permanente o conservación de estado en memoria entre peticiones. La compatibilidad de todo el backend aún no fue inspeccionada.

Referencias: [Comparación de generaciones](https://firebase.google.com/docs/functions/version-comparison) y [despliegue de funciones sobre Cloud Run](https://cloud.google.com/run/docs/deploy-functions).

## 3. Proyecto y entorno preparados

Se utilizó el proyecto Firebase **`grand-safe-band`**, con plan **Blaze**. Se dejaron accesibles desde la consola Functions, Authentication, Firestore y Messaging. Tener esos accesos directos no implica que todos los servicios estén implementados.

La prueba se creó en una carpeta independiente del backend existente:

```text
C:\Users\nnico\OneDrive\Desktop\Grand Safe Life\Software\cloud-functions-poc
```

Herramientas y versiones observadas en las salidas compartidas:

| Componente | Estado observado |
| --- | --- |
| Firebase CLI | 15.22.4 |
| Python inicial del equipo | 3.14.5 |
| Python agregado para el entorno virtual | 3.13.15 |
| Java para el emulador de Firestore | Microsoft OpenJDK 21.0.12.1 |
| `firebase-functions` instalado | 0.5.0 |
| `firebase-admin` instalado | 7.6.0 |

El entorno virtual se creó con Python 3.13 porque la sección del tutorial aportada indicaba soporte hasta esa versión. Sin embargo, el registro del despliegue mostró **Python 3.14 (2nd Gen)** y una creación exitosa. Queda pendiente revisar la configuración y alinear la versión local con la desplegada; no debe asumirse que crear un `venv` determina automáticamente el runtime remoto.

Referencia principal utilizada: [Primeros pasos: escribir, probar y desplegar funciones](https://firebase.google.com/docs/functions/get-started).

## 4. Inicialización y dependencias

Se verificó la sesión de Firebase CLI y se vinculó el directorio al proyecto existente. Se inicializaron Firestore y Functions, seleccionando Python. Se omitieron las Agent Skills opcionales y la instalación automática de dependencias.

```powershell
firebase login
firebase init firestore
firebase init functions
cd functions
py -3.13 -m venv venv
.\venv\Scripts\python.exe -m pip install -r requirements.txt
```

La instalación terminó con `Successfully installed`. Los avisos sobre entradas de caché ignoradas no impidieron completarla.

La estructura relevante quedó organizada alrededor de `.firebaserc`, `firebase.json`, los archivos de reglas e índices de Firestore y la carpeta `functions`, con `main.py`, `requirements.txt` y `venv`.

## 5. Función implementada

Se inicializó el Firebase Admin SDK y se conservó la configuración global `max_instances=10`. La función utilizada fue:

```python
from firebase_functions import firestore_fn, https_fn
from firebase_functions.options import set_global_options
from firebase_admin import initialize_app, firestore
import google.cloud.firestore

set_global_options(max_instances=10)

app = initialize_app()


@https_fn.on_request()
def addmessage(req: https_fn.Request) -> https_fn.Response:
    original = req.args.get("text")

    if original is None:
        return https_fn.Response("No text parameter provided", status=400)

    firestore_client: google.cloud.firestore.Client = firestore.client()
    _, doc_ref = firestore_client.collection("messages").add({
        "original": original
    })

    return https_fn.Response(f"Message with ID {doc_ref.id} added.")
```

Se decidió omitir `makeuppercase`, la segunda función del tutorial, porque su disparador de Firestore no era necesario para validar el backend HTTP. El import `firestore_fn` quedó en el bloque original, aunque ya no se utiliza.

Cada apertura del enlace con `?text=Hola` crea un documento nuevo. Ese comportamiento corresponde al ejemplo de prueba; no constituye todavía el diseño final de los endpoints del proyecto. La respuesta es texto con el ID, no JSON ni una redirección a la consola.

## 6. Verificación local

Se ejecutó `firebase emulators:start`. El primer intento falló porque Java no estaba disponible. Se instaló OpenJDK 21 y se reinició la terminal para actualizar el PATH.

Luego arrancaron correctamente Functions y Firestore. La función se probó en:

```text
http://127.0.0.1:5001/grand-safe-band/us-central1/addmessage?text=Hola
```

Se obtuvo una respuesta con el ID `UfBv6yQzjRCXXguWlFwK` y se verificó en la interfaz local de Firestore un documento con `original: Hola`.

El aviso de servicios no emulados no impidió la prueba: la función utilizada accedía a Firestore, cuyo emulador sí estaba activo.

Referencias: [Ejecución local de funciones](https://firebase.google.com/docs/functions/local-emulator) y [Firebase Local Emulator Suite](https://firebase.google.com/docs/emulator-suite).

## 7. Despliegue y verificación en la nube

Desde la raíz de la prueba se ejecutó:

```powershell
firebase deploy --only functions
```

La CLI habilitó las APIs requeridas que faltaban, subió el código y creó `addmessage` en la región `us-central1`. El registro terminó con `Deploy complete!`.

Endpoint desplegado, consignado sin ejecutar una nueva petición:

```text
https://us-central1-grand-safe-band.cloudfunctions.net/addmessage
```

El usuario abrió la URL con `?text=Hola` y confirmó que cada petición agregaba un documento a Firestore real. El backend quedó ejecutándose en Google Cloud, independientemente de que la computadora local permanezca encendida.

También se configuró la limpieza de imágenes de Artifact Registry con una antigüedad de un día. Esta limpieza de artefactos no elimina la función desplegada ni los documentos de Firestore.

`max_instances=10` configura el escalado por función; no significa que siempre existan diez instancias ni establece un presupuesto en dólares. Referencia: [Administración de funciones, escalado y limpieza de artefactos](https://firebase.google.com/docs/functions/manage-functions).

## 8. Por qué esta arquitectura permite usar FCM

Cloud Functions proporciona el entorno de servidor donde ejecutar la lógica del proyecto. **Firebase Cloud Messaging (FCM)** proporciona el servicio de mensajería hacia las aplicaciones. Son responsabilidades complementarias: el backend decide cuándo avisar y a quién; FCM transporta el mensaje hacia la instalación destinataria.

FCM contempla un entorno de servidor de confianza para enviar mensajes y una aplicación cliente preparada para recibirlos. Una función en Google Cloud puede cumplir ese papel de servidor. Referencia: [Descripción general de FCM](https://firebase.google.com/docs/cloud-messaging).

El **Firebase Admin SDK para Python** dispone de funciones de envío de mensajes. Por eso, el backend puede consultar las relaciones entre ancianos y monitores y luego enviar un mensaje desde su lógica de aplicación. No hace falta un disparador de Analytics ni una función como `makeuppercase` para hacerlo.

El flujo previsto es:

```text
App del anciano
      ↓ petición HTTP con datos
Cloud Function → caso de uso → procesamiento
      ↓ si corresponde una alerta
Consulta de monitores asociados y destinos registrados
      ↓
Firebase Admin SDK → FCM → apps de los monitores
```

La documentación consultada describe destinos mediante FID registrado o token de registro y presenta FID como opción recomendada. Antes de implementarlo hay que comprobar compatibilidad con las versiones de los SDK del backend y de las apps. El ID de un usuario no debe confundirse con el destino de mensajería de una instalación. También existe envío a múltiples destinatarios. Referencia: [Envío de mensajes mediante Admin SDK](https://firebase.google.com/docs/cloud-messaging/send/admin-sdk).

Se mantiene como orientación utilizar **Data Messages**, con datos del evento que la app pueda interpretar. La recepción de esos datos y la presentación de una alarma o notificación visible son tareas distintas: la app debe implementar su comportamiento. Referencia: [Tipos de mensajes de FCM](https://firebase.google.com/docs/cloud-messaging/customize-messages/set-message-type).

**FCM no se implementó ni se probó en esta sesión.** Quedan pendientes el registro de destinos, los permisos de envío, las asociaciones entre usuarios, el código emisor y la recepción móvil. También habrá que comprobar el comportamiento en segundo plano y las restricciones del sistema operativo; el envío aceptado por el servidor no demuestra que una alarma se haya mostrado al usuario. Referencia: [Recepción de mensajes en Android](https://firebase.google.com/docs/cloud-messaging/android/receive-messages).

## 9. Facturación y alcance de la prueba

El usuario informó un presupuesto de 25 USD y cuatro días restantes de crédito de bienvenida al comenzar. No se inspeccionó la configuración de facturación: un presupuesto de alertas no debe confundirse con un límite que detiene servicios. Referencia: [Presupuestos y alertas de Firebase](https://firebase.google.com/docs/projects/billing/budget-alerts).

El crédito promocional y las cuotas gratuitas son conceptos distintos. El vencimiento del crédito no elimina las cuotas gratuitas aplicables, pero puede dejar consumo facturable a cargo de la cuenta de pago. Referencia: [Programa gratuito de Google Cloud](https://docs.cloud.google.com/free/docs/free-cloud-features?hl=es).

No se implementó autenticación del endpoint durante esta prueba. El éxito del ejemplo demuestra ejecución y persistencia; no acredita todavía seguridad, rendimiento ni preparación del backend completo para producción.

## 10. Decisión y próximos pasos

Se consideró validado Cloud Functions como opción de hosting para los endpoints HTTP. La siguiente decisión fue adaptar el backend existente antes de implementar autenticación, preservando su arquitectura.

El alcance acordado para esa adaptación es:

- Reemplazar la entrada HTTP actual por funciones HTTP de Firebase.
- Conservar casos de uso, dominio, repositorios y capas internas.
- Mantener los mocks y los contratos actuales: métodos, parámetros, respuestas y códigos de estado.
- Revisar dependencias, configuración, runtime y estado en memoria.
- Mantener separadas la adaptación del hosting, la autenticación y la migración de mocks a Firebase real.

El orden de trabajo actualizado queda así:

**Adaptar backend a Cloud Functions → autenticación → reemplazar mocks por Firebase → necesidades de la app del anciano → FCM.**

El próximo paso concreto es revisar el backend actual y determinar los cambios mínimos de su entrada HTTP. Esa revisión y la migración aún no se realizaron en este chat.
