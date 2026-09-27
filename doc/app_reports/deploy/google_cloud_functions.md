# Uso de Google Cloud Functions

## Implementación actual

El backend está publicado en el proyecto Firebase `grand-safe-band` mediante una única función HTTP llamada `api`, de segunda generación. Esa función contiene el código del backend y las dependencias necesarias; Flask organiza sus rutas. 
Google administra la infraestructura que lo ejecuta, sin que tengamos que mantener un servidor.

URL publicada:

```text
https://us-central1-grand-safe-band.cloudfunctions.net/api
```

A esa URL se agregan las rutas `/grandsafelife/api/v1/...`, detalladas en la [documentación de la API REST](../api_rest/api_documentation.md).

## Cómo arranca y atiende las peticiones

1. El `main.py` de la raíz exporta `api`, marcada con `@https_fn.on_request`. Es el punto de entrada que Firebase descubre y publica.
2. Ese archivo importa la aplicación de `backend/main.py`. Allí se crea `App` y se entrega a `create_http_app`, que construye Flask y registra los grupos de endpoints mediante Blueprints.
3. Cuando llega una petición, `api` crea el contexto de Flask y le entrega la solicitud. Conserva el body en caché y usa una copia de su flujo para evitar que los dos contextos consuman el mismo flujo de lectura.
4. Flask elige el endpoint según la ruta y el método HTTP. La capa HTTP valida la entrada y llama a `App` cuando corresponde.
5. La respuesta vuelve al cliente a través de la función `api`.

La aplicación se construye al cargar cada instancia y puede reutilizarse para varias peticiones. Una sola función desplegada puede tener varias instancias: Google las inicia según la demanda.

## Configuración y despliegue

`firebase.json` indica que el código fuente parte de la raíz del repositorio y pertenece a la codebase `backend`. La codebase identifica este conjunto de código para su despliegue. `.firebaserc` lo asocia a `grand-safe-band`, y
`requirements.txt` declara las dependencias de ejecución.

La configuración actual es:

| Parámetro | Valor |
| --- | --- |
| Región | `us-central1` |
| Runtime | Python 3.13 |
| Instancias mínimas / máximas | 0 / 10 |
| Peticiones simultáneas por instancia | 1 |
| CPU y memoria por instancia | 1 CPU y 256 MiB |
| Tiempo máximo por petición | 60 segundos |

Con el [entorno de desarrollo preparado](../../dev_reports/installation_for_devs.md), los comandos se ejecutan desde la raíz. Para probar localmente:

```powershell
firebase emulators:start --only functions --project grand-safe-band
```

La URL local de la función es
`http://127.0.0.1:5001/grand-safe-band/us-central1/api`.

Para publicar, con una sesión de Firebase autorizada:

```powershell
firebase deploy --only functions:backend:api --project grand-safe-band
```

## Consideraciones actuales

- Los recursos configurados corresponden a los mocks actuales; todavía no se dimensionaron para ejecutar el modelo de detección.
- El paquete excluye las partes del proyecto que no tienen que ver con recursos para ejecutar en la nube: entornos virtuales, credenciales, cachés, tests, documentación, scripts, etc. Las bibliotecas de inferencia no forman parte de las dependencias de ejecución.
- Firebase genera imágenes de despliegue en Artifact Registry. Se conserva la política de limpieza de imágenes de más de un día.
- Con cero instancias mínimas no se mantiene una instancia siempre encendida; una petición puede necesitar esperar su arranque.
- La memoria de una instancia no es almacenamiento permanente ni compartido con las demás. No se utiliza para conservar pedidos o resultados reales.

## Referencias y límites de diseño

- [Funciones HTTP y enrutamiento con Flask](https://firebase.google.com/docs/functions/http-events).
- [Organización por codebases](https://firebase.google.com/docs/functions/organize-functions).
- [Ejecución local](https://firebase.google.com/docs/functions/local-emulator).
- [Configuración de runtime y escalado](https://firebase.google.com/docs/functions/manage-functions).
- [Restricciones de ejecución y estado](https://firebase.google.com/docs/functions/tips).

TODO Explicar basado en ejemplo
- [Ejemplo didáctico](https://firebase.google.com/docs/functions/get-started?hl=es-419)

## Desarrollos futuros

El flujo previsto es enviar datos con `POST /grandsafelife/api/v1/fall-detection/requests`, recibir un `request_id` y consultar luego con `GET /grandsafelife/api/v1/fall-detection/requests/{request_id}`.

Queda por definir:

- Dónde se ejecutará el procesamiento y cómo se iniciará de forma fiable si la API responde antes de terminar. No está elegida una cola ni otro servicio.
- Cómo guardar pedidos, estados y resultados para poder consultarlos desde cualquier instancia, incluso después de un reinicio.
- Cómo generar IDs únicos, asociarlos al usuario autorizado y manejar errores, capacidad, concurrencia y vencimiento de resultados.
- Con qué frecuencia consultará el cliente y cómo distinguirá un pedido en curso, listo, fallido o inexistente.

Estas decisiones deberán conectar los endpoints con los casos de uso y el [manager de detección](../../dev_desig/fall_detection_manager.md), midiendo antes el tiempo y la memoria que requiere el modelo.
