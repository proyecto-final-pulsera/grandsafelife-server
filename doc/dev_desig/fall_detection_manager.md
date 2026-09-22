# Manager de detección de caídas

## Responsabilidad y ubicación

`backend/fall_detection/fall_detection_manager.py` declara `FallProcessorManager`.
El módulo administrará pedidos y ejecución del detector. `app` conserva la
autorización, el contexto del solicitante y las decisiones posteriores, como
solicitar notificaciones. El manager se inyecta en `FallDetectionProcesses`.

## API interna

| Operación | Entrada | Salida |
| --- | --- | --- |
| `FallProcessorManager(N=1)` | Cantidad positiva de instancias previstas. | Manager; `ValueError` si N no es un entero positivo. |
| `appendNewProcessData(data)` | Chunk JSON ya deserializado; esquema pendiente. | ID entero positivo del pedido. |
| `getResultById(request_id)` | ID entero positivo. | `ProcessingResult`; `ValueError` si el ID no es válido. |

`ProcessingResult` contiene `request_id`, `status` y `result`. El campo `result`
envuelve el `FallDetectionResult` del modelo y solo aparece con un estado final.

| Estado de consulta | Resultado del detector |
| --- | --- |
| `IN_PROGRESS` | `None`. |
| `READY` | Clasificación booleana, sin error. |
| `FAILED` | Código de error, sin clasificación. |
| `NOT_FOUND` | `None`; significa que la consulta no encontró un pedido. |

Este contrato interno no contiene códigos HTTP ni el envelope de la API.

## Alcance implementado en el paso 4

Los métodos imprimen un aviso de implementación pendiente. El constructor
conserva N pero no crea detectores; enviar datos retorna siempre `1`, sin guardar
el chunk. Consultar cualquier ID válido retorna `READY` sin caída, aunque no se
haya enviado antes. Son respuestas fijas para revisar el contrato.

No hay cola, IDs únicos, ejecución ni persistencia. Los processors conservan
sus TODO y los endpoints mantienen su bypass: el GET HTTP continúa respondiendo
«en curso». La respuesta mock del manager todavía no llega a HTTP.

## Diseño pendiente: épica E5

La implementación inicial se plantea con una instancia. Se evaluará una cola
acotada dentro del proceso y un registro por ID, evitando trabajo simultáneo
sobre un mismo detector. Faltan definir capacidad, asignación, estados,
sincronización, errores de carga, cierre y retención de resultados.

Alternativas para evaluar cuando se pueda medir el modelo completo:

- **Threads dentro del servidor:** permiten ejecutar trabajo fuera del recorrido
  del request; su paralelismo efectivo depende del modelo y sus librerías.
- **Procesos separados:** aíslan la ejecución, pero requieren transferir datos y
  pueden duplicar el modelo en memoria. Evaluarlos solo si las mediciones justifican ese costo.
- **Otro contenedor o servicio:** reservarlo para una necesidad observada de
  aislamiento o escalado; no se incorpora en esta etapa del monolito.

Antes de aumentar N se medirán memoria, latencia y concurrencia soportada. El
parámetro no implica que hoy existan instancias ni ejecuciones paralelas.

La identidad confiable y su relación con cada pedido siguen pendientes del DTO
de contexto de `app`, junto con E2 y E3. No se agrega un `user_id` proporcionado
por el cliente al contrato del detector ni se delegan permisos en este manager.
También quedan abiertos expiración, comportamiento ante reinicios y cómo recibe
`app` la finalización para decidir notificaciones sin depender del polling.
