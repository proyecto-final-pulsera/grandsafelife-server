# Pricing de Firebase

Para el proyecto académico voy a utilizar los siguientes servicios de Firebase:

- **Functions**
- **Authentication**
- **Firestore**
- **Messaging**
- **Storage**

La idea es establecer un **tope mensual de gasto** y tener claros los costos de cada servicio para poder estimar el presupuesto.

Como se trata de un proyecto académico, el uso estará principalmente destinado a **pruebas y desarrollo**, con una aplicación pequeña y **sin usuarios reales**. En principio, se espera que el consumo sea bajo y que se mantenga dentro de las cuotas gratuitas.

---

## 💰 Resumen de precios

Actualmente el proyecto utiliza el **plan Blaze**, que funciona bajo un esquema de pago por uso. Sin embargo, varios servicios cuentan con **cuotas sin costo** que, para un proyecto pequeño, suelen ser suficientes.

### ☁️ Cloud Firestore

La cuota sin costo incluye, para la primera base de datos del proyecto:

| Operación | Cuota sin costo |
|---|---:|
| Lecturas | **50.000 / día** |
| Escrituras | **20.000 / día** |
| Eliminaciones | **20.000 / día** |
| Almacenamiento | **1 GiB** |

Para un proyecto académico pequeño, estos límites deberían ser más que suficientes durante la etapa de desarrollo y pruebas.

> ⚠️ Es importante prestar atención a consultas o procesos que puedan ejecutarse repetidamente, ya que las lecturas y escrituras se contabilizan individualmente.

---

### 🔐 Firebase Authentication

Los métodos de autenticación tradicionales se ofrecen sin costo, entre ellos:

- Email y contraseña
- Proveedores como Google
- Otros métodos de autenticación compatibles

Para un proyecto sin usuarios reales y utilizado principalmente para pruebas, el consumo debería ser muy bajo.

---

### 📦 Cloud Storage for Firebase

Storage permite almacenar archivos como:

- Imágenes
- PDFs
- Documentos
- Otros archivos utilizados por la aplicación

Cuenta con una cuota mensual sin costo de hasta **5 GB de almacenamiento**, además de cuotas gratuitas relacionadas con las operaciones y descargas.

Para un proyecto académico pequeño, este límite debería ser suficiente siempre que no se almacenen grandes cantidades de archivos.

Solo deberíamos procurar crear pocos usuario y solo usar storage para imágenes de perfil, en lo psible que pesen poco.

---

### 🔔 Firebase Cloud Messaging (FCM)

**Firebase Cloud Messaging (FCM)** permite enviar notificaciones push y mensajes a los dispositivos.

El envío de mensajes mediante FCM es **gratuito**, por lo que puede utilizarse para realizar pruebas con los dispositivos propios sin que esto represente un costo directo por mensaje.

---

### ⚙️ Cloud Functions for Firebase

Cloud Functions permite ejecutar código en la infraestructura de Google sin tener que mantener un servidor propio.

Al utilizar el **plan Blaze**, se dispone de una cantidad mensual de uso sin costo antes de comenzar a generar cargos.

Para un proyecto académico pequeño, con pocas ejecuciones y sin usuarios reales, es poco probable que el consumo sea elevado.

> ⚠️ De todas formas, hay que prestar especial atención a funciones que puedan ejecutarse de manera inesperada o repetitiva.

---

# 🛡️ ¿Cómo evitar costos inesperados?

Aunque el proyecto sea pequeño, al utilizar el **plan Blaze** es importante tener algunas medidas de control.

## 1. Configurar un presupuesto

Desde la sección de **Facturación de Google Cloud** se puede configurar un presupuesto mensual.

Por ejemplo:

> **Presupuesto mensual: USD 5**

También se pueden configurar alertas para recibir notificaciones cuando el gasto alcance determinados porcentajes:

- 🟡 **50%**
- 🟠 **80%**
- 🔴 **100%**

Esto permite detectar rápidamente si el consumo está creciendo más de lo esperado.

### ⚠️ Importante

Un presupuesto **no funciona como un límite de gasto automático**.

Las alertas de presupuesto normalmente sirven para **notificar**, pero no detienen automáticamente los servicios cuando se alcanza el monto establecido.

Si se necesita detener el consumo automáticamente, hay que implementar mecanismos adicionales mediante Google Cloud.

---

## 2. Monitorear el uso

Es recomendable revisar periódicamente las métricas de consumo desde la consola de Firebase/Google Cloud.

Por ejemplo:

- **Firestore:** lecturas, escrituras y eliminaciones.
- **Storage:** almacenamiento y operaciones.
- **Functions:** invocaciones y tiempo de ejecución.
- **Authentication:** usuarios y métodos utilizados.
- **Messaging:** mensajes enviados.

Esto permite detectar rápidamente comportamientos inesperados.

---

# 📊 Estimación para este proyecto

Dado que se trata de un proyecto:

- 🎓 Académico
- 👤 Sin usuarios reales
- 🧪 Orientado a pruebas
- 📱 Con pocos dispositivos
- 🗄️ Con una cantidad pequeña de datos

es esperable que el consumo se mantenga **muy por debajo de los límites gratuitos** durante el desarrollo normal.

El principal riesgo no sería tanto el uso habitual, sino algún **error de implementación**, como:

- Un bucle que genere lecturas constantemente.
- Una Cloud Function que se dispare de manera repetitiva.
- Subir accidentalmente archivos muy grandes.
- Ejecutar consultas innecesarias de Firestore.
- Dejar algún proceso ejecutándose continuamente.

Por este motivo, una combinación de **presupuesto + alertas + monitoreo del consumo** es una buena medida para trabajar tranquilo.

---

# ✅ Recomendación

Para un proyecto académico de estas características, una configuración razonable sería:

| Medida | Configuración sugerida |
|---|---|
| 💳 Plan | **Blaze** |
| 💰 Presupuesto | **USD 5/mes** como referencia |
| 🔔 Alertas | **50% / 80% / 100%** |
| 📊 Monitoreo | Revisar periódicamente el consumo |
| 🧪 Uso | Desarrollo y pruebas |
| 👥 Usuarios | Sin usuarios reales |

De esta manera se puede utilizar Firebase con bastante tranquilidad, teniendo visibilidad sobre el consumo y detectando rápidamente cualquier comportamiento anormal.
