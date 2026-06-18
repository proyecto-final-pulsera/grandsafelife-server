# Grand Safe Life Server

## Descripción

Grand Safe Life Server es el backend central del ecosistema Grand Safe Life.

Su función es actuar como intermediario entre las aplicaciones móviles, los dispositivos monitoreados y los servicios de almacenamiento y notificación. El servidor recibe información de los dispositivos, procesa eventos, almacena datos históricos y distribuye notificaciones a los usuarios autorizados.

La arquitectura está orientada a sistemas IoT y monitoreo remoto de adultos mayores.

---

## Objetivos

* Gestionar usuarios y autenticación.
* Administrar relaciones entre adultos mayores y monitores.
* Recibir mediciones provenientes de dispositivos móviles.
* Procesar eventos críticos.
* Almacenar información histórica.
* Distribuir notificaciones a los usuarios correspondientes.
* Proveer una API HTTP para aplicaciones móviles.
* Integrar mensajería MQTT para telemetría y eventos.

---

## Arquitectura General

```text
Pulsera BLE
      │
      ▼
Aplicación Adulto Mayor
      │
      ├── HTTP
      └── MQTT
      │
      ▼
Grand Safe Life Server
      │
      ├── PostgreSQL
      ├── MQTT Broker
      └── Sistema Notificaciones
      │
      ▼
Aplicación Monitor (e invitados)
```

---

## Estructura del Proyecto

```text
backend/
├── main.py
├── http/
│   └── app_http.py
├── mqtt/
│   └── app_mqtt.py
├── postgres/
│   └── database.py
├── notifications/
│   └── mobile_notifications.py
└── system/
    └── system.py
```

### main.py

Punto de entrada de la aplicación.

Responsabilidades:

* Inicialización del sistema.
* Creación de dependencias.
* Arranque de servicios HTTP y MQTT.

### http/

Implementa la interfaz HTTP utilizando FastAPI.

Responsabilidades:

* Definición de endpoints.
* Validación básica de requests.
* Comunicación con la capa de sistema.

### mqtt/

Implementa la comunicación MQTT.

Responsabilidades:

* Conexión al broker.
* Recepción de mensajes.
* Validación básica de tópicos y payloads.
* Reporte de eventos hacia la capa de sistema.

### postgres/

Capa de acceso a datos.

Responsabilidades:

* Operaciones CRUD.
* Consultas SQL.
* Abstracción de PostgreSQL.

### notifications/

Módulo encargado del envío de notificaciones móviles.

Responsabilidades:

* Envío de alertas.
* Integración futura con servicios para notificaiones push.

### system/

Núcleo de la lógica de negocio.

Responsabilidades:

* Procesamiento de requests HTTP.
* Procesamiento de eventos MQTT.
* Coordinación entre módulos.
* Persistencia de datos.
* Generación de alertas y notificaciones.

---

## Licencia

Proyecto académico desarrollado como trabajo final de Ingeniería Electrónica.