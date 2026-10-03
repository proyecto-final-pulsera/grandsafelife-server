# Tests de API REST

Desde `grandsafelife-server`, con el entorno virtual y las dependencias del servidor instaladas:

```powershell
python tests/api_rest/run_tests.py        # Todos los grupos registrados
python tests/api_rest/run_tests.py users  # Solo usuarios
```

## Propuesta de suites

Solo usuarios está implementado y verificado. Los demás casos son propuestas para revisión: no autorizan todavía declarar ni implementar métodos. Los nombres de grupos y archivos se unificarán al incorporar cada suite al ejecutor.

Todas las rutas siguientes llevan el prefijo `/grandsafelife/api/v1`.

Cada test comprueba el estado HTTP, el formato de respuesta y la llamada al process con sus argumentos correctos, sin pasar el token. Un request inválido debe devolver 422 con `detail` y no ejecutar el process. Se usan blueprints y processes locales con mocks, sin red ni Firebase. No se comprueban permisos ni autenticación real: actualmente solo se exige la presencia de Authorization.

Cuando se simula un resultado vacío o inexistente, se sustituye puntualmente la respuesta del process; eso prueba el endpoint, no la persistencia. Los subcasos de una misma prueba se identifican con `subTest`.

### Usuarios — test_users.py

Los seis casos actuales ya están implementados y pasaron. Se propone conservarlos:

- **USERS_T1** — `GET /users/{user_id}`: retornar el ID solicitado y fechas enteras en milisegundos; simular usuario inexistente y esperar `resp: null`.
- **USERS_T2** — `GET /users/by-email?email=...`: conservar el email consultado, incluido `+`, y devolver el usuario encontrado.
- **USERS_T3** — `POST /users`: crear con ID explícito o sin ID y devolver `resp.user_id`; conservar todos los campos de `data`.
- **USERS_T4** — `PATCH /users/{user_id}`: conservar el usuario destino, nulos, campos adicionales y rutas con puntos; responder éxito sin `resp`.
- **USERS_T5** — Los cuatro endpoints: rechazar requests sin Authorization.
- **USERS_T6** — Rechazar email ausente o vacío, envoltorio de creación inválido, ID de creación vacío/no textual, campos extra del envoltorio y body de actualización que no sea objeto.

Ampliaciones propuestas, todavía sin implementar:

- **USERS_T7** — `GET /users/by-email`: simular usuario no encontrado y esperar `resp: null`.
- **USERS_T8** — `POST /users` con `data: {}` y `PATCH /users/{user_id}` con `{}`: aceptar mapas vacíos y delegarlos sin agregar campos.

### Hogares — test_homes.py

- **HOMES_T1** — `GET /homes/{home_id}`: delegar el ID solicitado y devolver el mapa del hogar con miembros y fechas en milisegundos.
- **HOMES_T2** — `POST /homes`: aceptar ID explícito o ausente; devolver el ID como string en `resp`. El campo `id` dentro de `data` no debe reemplazar `home_id`.
- **HOMES_T3** — `PATCH /homes/{home_id}`: delegar campos parciales, nulos, mapas de miembros y rutas con puntos sin modificarlos; responder sin `resp`.
- **HOMES_T4** — `DELETE /homes/{home_id}`: llamar solo al process de eliminación con el ID correcto y responder sin `resp`.
- **HOMES_T5** — `GET /homes/{home_id}`: simular documento inexistente (`null`) y documento existente vacío (`{}`), distinguiendo ambas respuestas.
- **HOMES_T6** — Los cuatro endpoints: rechazar requests sin Authorization.
- **HOMES_T7** — Rechazar envoltorios de creación inválidos, home_id vacío/no textual y bodies de actualización que no sean objetos.
- **HOMES_T8** — Crear con `data: {}` y actualizar con `{}`: aceptar y delegar los mapas vacíos.

### Dispositivos — test_devices.py

- **DEVICES_T1** — `POST /devices`: aceptar ID explícito o ausente; devolver un ID no vacío como string y conservar `data` separado de `device_id`.
- **DEVICES_T2** — `GET /devices/{device_id}`: retornar el ID solicitado, campos del dispositivo y fechas en milisegundos.
- **DEVICES_T3** — `PATCH /devices/{device_id}`: conservar campos parciales, nulos y rutas con puntos; cubrir datos para asociar/liberar el dispositivo y connection_by vacío, phone o ID de hub sin interpretar permisos.
- **DEVICES_T4** — `DELETE /devices/{device_id}`: llamar al process de eliminación, no al de actualización; responder sin `resp`.
- **DEVICES_T5** — `GET /users/{owner_id}/devices`: delegar owner_id y devolver un mapa de dispositivos indexado por ID, compatible con el datasource.
- **DEVICES_T6** — `GET /homes/{home_id}/devices`: delegar home_id y devolver el mapa de dispositivos, incluyendo un hub en el mock.
- **DEVICES_T7** — `GET /devices/{device_id}/location`: delegar el ID y devolver coordenadas numéricas `lat` y `long`.
- **DEVICES_T8** — Lecturas: simular dispositivo inexistente (`null`) y consultas por owner/home sin resultados (`{}`).
- **DEVICES_T9** — `GET /devices/dev_available`: comprobar que el mock de dispositivo disponible tenga home_id, owner_id y connection_by vacíos.
- **DEVICES_T10** — Los siete endpoints: rechazar requests sin Authorization.
- **DEVICES_T11** — Rechazar envoltorio de creación inválido, device_id vacío/no textual y body de actualización que no sea objeto; aceptar data y actualización vacíos.

### Métricas de dispositivos — test_device_stats.py

- **STATS_T1** — `GET /devices/{device_id}/stats/daily?date=YYYY-MM-DD`: delegar dispositivo y fecha; devolver id igual a la fecha, contadores enteros, tiempo numérico y updated_at ISO 8601 válido.
- **STATS_T2** — `GET /devices/{device_id}/stats/monthly?month=YYYY-MM`: devolver id igual al mes y los campos que consume MonthlyAggregatesData: promedios numéricos y totales/niveles/días enteros.
- **STATS_T3** — `GET /devices/{device_id}/stats/monthly/previous`: fijar la fecha del servidor para comprobar el mes anterior, incluyendo enero que retrocede a diciembre del año anterior; comprobar los campos mensuales.
- **STATS_T4** — `GET /devices/{device_id}/stats/daily/last-week`: fijar la fecha para comprobar siete mocks desde hace seis días hasta hoy, sin duplicados, ordenados por fecha y con campos diarios válidos. Incluir cambio de mes/año.
- **STATS_T5** — Simular métricas diarias y mensuales inexistentes (`{}`), semana sin datos (`[]`) y semana con solo algunos días: preservar esas respuestas sin completar días artificialmente.
- **STATS_T6** — Los cuatro endpoints: rechazar requests sin Authorization.
- **STATS_T7** — Rechazar date/month ausentes, vacíos o con formato incorrecto y meses fuera de 01–12; no ejecutar el process.

La validación diaria actual verifica el formato mediante regex, no la existencia de la fecha en el calendario. Rechazar 2026-02-30 o un día 00 requeriría ajustar primero el endpoint; no se propone dar esa capacidad por implementada.

### Alarmas — test_alarms.py

- **ALARMS_T1** — `GET /devices/{device_id}/alarms`: devolver mapa indexado por ID con nombre, horario, días, actividad, state y fechas enteras en milisegundos.
- **ALARMS_T2** — `PUT /devices/{device_id}/alarms`: delegar el mapa completo con varias alarmas, conservando state y fechas enviados; responder éxito sin `resp`.
- **ALARMS_T3** — `PUT` con `{}`: aceptar el reemplazo vacío y delegarlo tal cual.
- **ALARMS_T4** — `GET`: simular documento sin alarmas y devolver `{}`.
- **ALARMS_T5** — `PUT`: aceptar horarios límite 0 y 1439, is_active falso y campos opcionales omitidos; no agregar state ni fechas al mapa enviado al process. Conservar fechas nulas cuando se envían explícitamente.
- **ALARMS_T6** — Ambos endpoints: rechazar requests sin Authorization.
- **ALARMS_T7** — `PUT`: rechazar body que no sea objeto, alarma que no sea objeto, campos obligatorios ausentes, nombre vacío, horario -1/1440 y campos desconocidos; no llamar al process.

La máscara days actualmente acepta un entero sin rango. No se propone probar rechazo fuera de 0–127 hasta que se acuerde esa regla. El PUT es un mock sin persistencia: no se espera que un GET posterior refleje lo guardado.

### API de detección de caídas — propuesta separada

No existe aún su archivo ni está registrada en el ejecutor. Esta sección cubre sus dos endpoints, no el modelo de detección.

- **FALL_T1** — `POST /fall-detection/requests`: aceptar un objeto JSON y devolver el mock actual `resp.request_id: 1`, HTTP 200 y op_status 0.
- **FALL_T2** — `GET /fall-detection/requests/{request_id}`: aceptar un ID entero positivo y devolverlo con HTTP 200 y op_status 1 (en curso).
- **FALL_T3** — Ambos endpoints: rechazar requests sin Authorization.
- **FALL_T4** — `POST`: rechazar body ausente, JSON malformado o body que no sea objeto; aceptar `{}` según el esquema provisional actual.
- **FALL_T5** — `GET`: rechazar ID cero, negativo o no entero.
- **FALL_T6** — Confirmar que los endpoints actuales responden directamente con mocks y no llaman al process: todavía tienen un bypass explícito.

Los estados READY, FAILED y NOT_FOUND quedan pendientes de conectar el process; no son respuestas alcanzables de los endpoints actuales.
