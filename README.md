# Grand Safe Life Server

## Descripción

Grand Safe Life Server es el backend central del ecosistema Grand Safe Life.

Su función es actuar como intermediario entre las aplicaciones móviles, los dispositivos monitoreados y los servicios de almacenamiento y notificación. El servidor recibe información de los dispositivos, procesa eventos, almacena datos históricos y distribuye notificaciones a los usuarios autorizados.

La arquitectura está orientada a sistemas IoT y monitoreo remoto de adultos mayores.

---

## Objetivos

* Gestionar usuarios y autenticación.
* Administrar relaciones entre adultos mayores y monitores.
* Gestionar solicitudes de monitoreo y administración.
* Recibir mediciones provenientes de dispositivos móviles.
* Procesar eventos críticos.
* Almacenar información histórica.
* Distribuir notificaciones a los usuarios correspondientes.
* Proveer una API HTTP para aplicaciones móviles.
* Integrar mensajería MQTT para telemetría y eventos.

---

## Estructura del Proyecto

```text
.
│   Dockerfile
│   main.py
│   requirements.txt
│
├── app_http
│   └── app_http.py
│
├── app_mqtt
│   └── app_mqtt.py
│
├── database
│   ├── dataDB
│   │   └── README.md
│   │
│   └── usersDB
│       ├── connection.py
│       ├── database.py
│       ├── schema.py
│       └── repositories
│           ├── users_repository.py
│           ├── monitoring_links_repository.py
│           └── monitoring_requests_repository.py
│
├── domain
│   ├── device.py
│   ├── monitoring_link.py
│   ├── monitoring_request.py
│   └── user.py
│
├── notifications
│   └── notifications.py
│
└── system
    └── system.py
```

---

## Capas del Sistema

La arquitectura se encuentra organizada en capas con responsabilidades claramente separadas.

```text
Entradas HTTP/MQTT -> Procesadas por system:
- Domain: Entidades
- Database: Para configuracion y datos
- Notifications: Para enviar notificaciones
```

### app_http

Implementa la API REST utilizando FastAPI.

Responsabilidades:

* Definición de endpoints.
* Validación de requests.
* Conversión de JSON a objetos internos.
* Comunicación con la capa System.

### app_mqtt

Implementa la integración MQTT.

Responsabilidades:

* Conexión al broker MQTT.
* Recepción de telemetría.
* Recepción de eventos.
* Validación de tópicos y payloads.
* Comunicación con la capa System.

### system

Núcleo de la lógica de negocio.

Responsabilidades:

* Procesamiento de requests HTTP.
* Procesamiento de eventos MQTT.
* Aplicación de reglas de negocio.
* Coordinación entre módulos.
* Generación de notificaciones.
* Persistencia de datos mediante repositorios.

### domain

Define las entidades del sistema.

Responsabilidades:

* Representar el modelo de negocio.
* Servir como DTO entre System y Database.

Entidades actuales:

* User
* Device
* MonitoringLink
* MonitoringRequest

### database

Implementa la persistencia de datos.

#### usersDB

Base de datos relacional destinada a:

* Usuarios.
* Dispositivos.
* Relaciones de monitoreo.
* Solicitudes de monitoreo.
* Configuración y permisos.

Utiliza el patrón Repository para encapsular el acceso a PostgreSQL.

Repositorios actuales:

* UsersRepository
* MonitoringLinksRepository
* MonitoringRequestsRepository

#### dataDB

Módulo reservado para almacenamiento de telemetría y datos históricos.

Actualmente se encuentra en etapa de definición.

Su objetivo será almacenar:

* Mediciones periódicas.
* Eventos generados por dispositivos.
* Alarmas.
* Históricos de actividad.

La implementación tecnológica aún no está definida.

### notifications

Módulo encargado del envío de notificaciones.

Responsabilidades:

* Alertas a monitores.
* Alertas a administradores.
* Integración futura con servicios Push.

---

## Componentes Pendientes

Los siguientes módulos ya están identificados como necesarios para futuras etapas:

### Auth

Responsable de:

* Generación de tokens.
* Validación de sesiones.
* Expiración de tokens.
* Identificación de usuarios autenticados.

Posible estructura:

```text
auth/
├── token_manager.py
└── session_manager.py
```

### Data DB

Responsable del almacenamiento de telemetría y eventos históricos.

La implementación podrá utilizar PostgreSQL, TimescaleDB u otra tecnología según los requerimientos finales del proyecto.

---

## Licencia

Proyecto académico desarrollado como trabajo final de Ingeniería Electrónica.
