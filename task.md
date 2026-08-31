# Actualizacion de DB y limpieza de endpoints

# Paso 1: Eliminar antigua DB
Se debe limpiar todo lo que tenga que ver con Postgres. Para eso ir eliminando:

- Eliminar el contenedor de la base de datos postgres desde el docker-compose. No será necesario nada de SQL

- Eliminar la carpeta databse/usersDB

- Dentro de database/ dejar carpeta:
    - repositories: Archivos especificos para hablar contra firebase
    - database.py: Aca vamos a ver cuestiones de inicializcion que se corren al iniciar todo el backend (validaciones, inicializaciones, etc). Este archivo queda en TO DO

Por ahora no nos preocupa la DB porque en este punto de la implementación aún no la vamos a utilizar. Borrar todo a lo bruto

# Paso 2: Creación de nuevos archivos

Basandonos en el archivo de 
"Parte de Guido\datasource_api_documentation.md"

Crear los archivos:
- users_endpoints.py
- homes_endpoints.py
- devices_endpoints.py
- devices_metrics_endpoints.py

La parte de inicialziación no corresponde a la API, sino a un proceso de inicialiazcion interno del servidor

A cada uno de estos archivos incluirle cabecera de descripción de archivo:

"""
@file
@author
@brief

Descripcion del módulo
"""
Aclaracion CODEX:
Leer archivo datasource_api_documentation.md

Crear los endpoints relacionados con usuarios en users_endpoints.py

Cabe destacar que en nuestro patrón de diseño de la API REST se usa una inyección de dependencias. Se le pasa como argumento en el constructor el objeto http_processor que se ocupa de proveer las funciones processNombreEndpoint. Por el momento todas las funciones process van a simplemente retornar éxito y tendrá respuestas mockeadas. De esta manera podremos simplemente probar que funcione bien la api.

Como regla de la API en todas las respuestas se retorna el campo {"op_status": 0, "brief": "descripcion", "resp": "X"}

Para eso se tendrá un mapa de código de error vs descripción. Este mapa vivirá en api_op_codes.py

El campo resp puede ser opcional según si aplica o no

Esta regla aplicará para todos los endpoints siguientes.

Dejar asentado este patrón en AGENTS.md

# Paso 3: Creación de endpoints de usuario



* getUserByID: Le entra el user ID por el header de authentication bearer. Método GET

* getUserByEmail: Le tiene que llegar el authentication bearer para validar si tiene permisos o no sobre ese email consultado. Dejar anotado en //TODO de la correspondiente funcion process esta funcionalidad. Método GET

* createUser: Por el momento la autenticación se hace mediante Firebase Authentication. Esto brinda posibiliadades de conectarlo con google, etc. Sin embargo, se decidió que esa funcionalidad se hace por fuera del servidor, es decir, se usa ese servicio desde la app flutter clietne, pero no pasa por el backend.

Esto implica que el servidor no genera tokens ni ID de usaurio, simplemente los recibe desde afuera.

En caso de que venga un id en null, se retorna INVALID_PARAM.

En el futuro habría que evaluar si es viable que el propio servidor sea quien se comunica con firebase auth y que no sea algo externo al backend. Sin emabrgo, por como se gestionó el proyecto. Por ahora es así. El auth no pasa por el backend

# Paso 4: Endpoints de Hogares

Aclaracion CODEX:
Leer archivo datasource_api_documentation.md

Implementar endpoints en homes_endpoints.py

getHomeByID: Metodo get recibe el auth bearer en el header. En la URL mediante query string se le pasa el ID del home

createHome:  Metodo POST recibe el auth bearer en el header. El ID lo genera el servidor. Lo retorna en la respuesta al request

updateHome:  Metodo POST recibe el auth bearer en el header. El ID del home y data se lo pasas en el json del body del request

deleteHome: Metodo POST recibe el auth bearer en el header. En el body recibe el ID de la casa a eliminar

# Paso 5: Endpoints de Devices
devices_endpoints.py

`getDeviceByID`
- **Descripción:** Recupera la información de un dispositivo mediante su ID. Método GET
El auth bearer va en el header. El ID de dispositivo va en la URL
Si no existe lo reporta en el op_code del response

### `createDevice`
- **Descripción:** Registra un nuevo dispositivo en el sistema. Metodo POST
- **Entradas:**
  - `data` (Map<String, dynamic>) - El objeto JSON del dispositivo.
  - **Retorna:** `Future<String>` - El ID único asignado al dispositivo.

El usuario que lo registra debe utilizar el header de auth bearer

### `updateDevice`
- **Descripción:** Actualiza campos específicos de un dispositivo existente. Metodo POST. Usa header de auth bearer
- **Entradas:**
  - `id` (String) - El ID del dispositivo.
  - `data` (Map<String, dynamic>) - Objeto JSON parcial con los campos a actualizar.
- **Retorna:** `Future<void>`

### `deleteDevice`
- **Descripción:** Elimina el vínculo de un dispositivo. Metodo POST. Usa header de auth bearer
  - *Atención:* Esta acción **no borra** ninguna estadística por defecto; simplemente "libera" el dispositivo para que pueda ser reasignado.
- **Entradas:** `id` (String) - El ID del dispositivo. 
- **Retorna:** `Future<void>`

### `queryDevicesByOwner`
- **Descripción:** Recupera todos los dispositivos vinculados a un usuario administrador específico. Aca se usa el header auth bearer. Metodo GET. Por query string se le pasa el ID de usauario por el cual se intenta filtrar
- **Entradas:** `ownerId` (String) - El ID del usuario **administrador** por el cual se va a filtrar.
- **Retorna:** `Future<List<Map<String, dynamic>>>` - Una lista de objetos JSON correspondientes a dispositivos.

### `queryDevicesByHome`
- **Descripción:** Recupera todos los dispositivos asociados a un hogar específico. Metodo GET. Auth bearer con el ID de usaurio. Por query string se le pasa el ID del home

- **Entradas:** `homeId` (String) - El ID del hogar.
- **Retorna:** `Future<List<Map<String, dynamic>>>` - Una lista de objetos JSON correspondientes a dispositivos.

### `getLocationByDevice`
- **Descripción:** Recupera la última ubicación GPS reportada por el dispositivo. Se le pasa el auth bearer. Metodo GET. Por query striong se le pasa el device ID
- **Entradas:** `deviceId` (String) - El ID del dispositivo.
- **Retorna:** `Future<Map<String, double>>` - Espera un mapa numérico, ej. `{"lat": -34.6037, "long": -58.3816}`

# Paso 6: Endpoints de Metricas
devices_metrics_endpoints.py

# Paso 7: Documentacion
Crear documentacion oficial de la API para cada endpoint. Dejé el documento creado con un template para que sigas de referencia. Basicamente:
- Listado general
- Endpoints especificando:
  - URL
  - Metodo
  - Json entrada
  - Json salida
- Tabla op codes con campo brief
