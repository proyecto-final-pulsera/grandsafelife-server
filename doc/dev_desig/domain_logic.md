# Diseño de la lógica de negocio

## Alcance

Este documento registra el diseño acordado para organizar los casos de uso,
sus validaciones y los datos internos del servidor. Es una guía para las próximas
implementaciones: los processors actuales conservan mocks y TODO, y todavía no
implementan el contexto autenticado ni las validaciones aquí descritas.

## Organización y responsabilidades

| Ubicación | Responsabilidad |
| --- | --- |
| `backend/http_api_rest/` | Validar contratos HTTP, recibir requests y traducir resultados al envelope de la API. |
| `backend/app/app.py` | Componer los módulos y conservar la interfaz pública `process_*`. |
| `backend/app/processes/process_*.py` | Coordinar cada caso de uso: invocar operaciones, comprobar sus resultados y decidir cómo continuar. |
| `backend/app/processing/` | Alojar las operaciones de negocio, validaciones, permisos y gestión de pedidos que necesiten los casos de uso. |
| `backend/app/domain/` | Definir conceptos y tipos del negocio compartidos, como usuarios, hogares y dispositivos. |
| `backend/database/` | Encapsular persistencia, representaciones de documentos y conversiones de Firestore mediante repositories. |

Los `process_*` deben ser simples y legibles. Los repositories ejecutan lecturas
y escrituras; las decisiones de permisos y negocio corresponden a `app`.
No es necesario extraer una función por cada línea: la separación debe responder
a una responsabilidad concreta.

Se conserva un único `backend/app/domain` para los conceptos de negocio. Las
representaciones propias de la DB permanecen dentro de `database`, sin crear
otro `domain` para documentos de Firestore. Los objetos que describen la ejecución
de un caso de uso pertenecen a `app`; su archivo concreto se definirá cuando
se implementen, por ejemplo `app/context.py`.

## Entrada, contexto y resultado

Se distinguen tres responsabilidades:

- **Entrada:** datos que necesita la operación solicitada, obtenidos del contrato HTTP.
- **Contexto autenticado:** identidad confiable del solicitante y los metadatos internos que realmente necesite el caso de uso.
- **Resultado:** éxito con sus datos, o un error explícito que la capa HTTP pueda traducir.

El `user_id` del contexto se obtiene al verificar la credencial. No se toma como
identidad confiable un ID enviado en el body o en la URL. Los IDs de recursos
objetivo son datos distintos y su acceso requiere autorización.

No se adopta un DTO mutable universal que recorra todas las funciones cambiando
entre estados como `AUTH`, `READY` o `DENIED`. Ese mecanismo permitiría
combinaciones incoherentes, como un estado autenticado sin identidad o un estado
listo sin resultado, y obligaría a cada función a conocer las mutaciones previas.

El contexto autenticado se construye después de verificar la identidad y se
mantiene estable durante el caso de uso. Cada operación devuelve su resultado
explícitamente; ante un fallo, el coordinador interrumpe el recorrido. Los tipos
y nombres definitivos de estos objetos todavía están pendientes.

## Ejemplo: consultar el perfil propio

La ruta actual es `GET /grandsafelife/api/v1/users/me`. El flujo conceptual es:

1. Verificar el token y obtener la identidad confiable.
2. Construir el contexto autenticado con el `user_id`.
3. Aplicar las comprobaciones de negocio que correspondan y consultar el perfil mediante el repository.
4. Devolver el perfil o un resultado de error, por ejemplo perfil inexistente.
5. Traducir el resultado al envelope y código HTTP correspondientes.

Estar autenticado no implica que exista el perfil de la aplicación ni autoriza
automáticamente a consultar otros recursos.

La [propuesta de autenticación](to_do_auth.md) plantea verificar el token en una
dependencia común de FastAPI y entregar la identidad verificada a `app`.
El ejemplo conversado también permite expresar esa verificación como una llamada
a un componente de autenticación desde el coordinador. La ubicación e interfaz
definitivas se resolverán al implementar auth, respetando la frontera HTTP del
proyecto; no se verificará el mismo token de forma duplicada en cada capa.
La autorización de negocio seguirá dentro de `app`.

## Pedidos con ciclo de vida

La detección de caídas requiere un pedido que continúa existiendo después de
responder al POST y cuyo resultado se consulta mediante otro request HTTP.
En ese caso sí corresponde modelar estados explícitos como `IN_PROGRESS`,
`READY` y `FAILED`.

La identidad del solicitante forma parte del contexto del pedido, no de una
etapa de su procesamiento. Consultar un ID requiere verificar permisos.
`NOT_FOUND` representa el resultado de una búsqueda, no el estado de un pedido
almacenado.

El esquema del pedido, sus timestamps, retención, persistencia y comportamiento
ante reinicios siguen pendientes. El manager administrará ese ciclo de vida;
el detector solo recibe el chunk y retorna una clasificación o un error.

## Definiciones pendientes

- Tipos concretos de entrada, contexto y resultado, sin dependencias de FastAPI ni del SDK de Firebase en el dominio.
- Interfaz de autenticación e integración del contexto con los processors actuales.
- Operaciones de permisos y negocio que se extraerán a `processing`.
- Contratos de repositories y conversión entre persistencia y objetos de negocio.
- Esquema y transiciones del pedido de detección de caídas.

Estas definiciones se implementarán en los pasos correspondientes. Documentar
el diseño no implica reemplazar ahora los mocks ni adelantar auth o persistencia.
