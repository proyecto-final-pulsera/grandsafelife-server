# Grand Safe Life Server

Backend de Grand Safe Life, un sistema académico de monitoreo y asistencia para
personas mayores. El proyecto se desarrolla con criterios similares a los de un
producto real, manteniendo una escala y complejidad acordes al contexto
didáctico.

## Esencia del sistema

Una persona mayor utiliza una pulsera que genera información de actividad. Si
el sistema detecta una caída, el servidor debe registrar el evento y avisar a
las personas autorizadas que la monitorean.

La conectividad de cada persona mayor utiliza una de estas dos modalidades:

- **Hub:** un hub instalado en un hogar puede brindar conectividad a varias
  personas y sus pulseras.
- **Aplicación móvil de la persona mayor:** la relación entre la aplicación y la
  persona es uno a uno. Permite operar fuera del hogar mediante datos móviles y
  aportar coordenadas del teléfono.

Ambas modalidades son excluyentes para una misma persona en un momento dado. El
servidor debe conocer cuál está activa y evitar asociaciones contradictorias.

Las personas monitoras utilizan la aplicación desarrollada por Guido. Desde
ella pueden consultar la información autorizada, administrar hogares y
dispositivos, configurar alarmas para la persona monitoreada y recibir avisos de
caídas.

## Componentes

```text
Pulsera ──► Hub ───────────────┐
                              │
Pulsera ──► App persona mayor ─┼──► API REST ──► System
                              │                    ├── Firebase
App de monitores ─────────────┘                    ├── Machine Learning
                                                   └── Notificaciones
```

El backend se mantiene inicialmente como un monolito modular desplegado en un
único contenedor Docker. Firebase/Firestore es un servicio externo y constituye
la persistencia del sistema.

## Documentación

- [Contrato HTTP](doc/app_reports/api_rest/api_documentation.md).
- [Interfaz del detector de caídas](doc/dev_reports/guido_readme_interfaz.md).
- [Investigación de autenticación con Firebase](doc/dev_reports/to_do_auth.md).
- [Reglas de arquitectura y trabajo](AGENTS.md).

La planificación local se mantiene en `IA Workflow/task.md` y
`IA Workflow/epics.md`, excluidos de Git. Para iniciar una planificación nueva,
copiar [task.example.md](<IA Workflow/task.example.md>) y
[epics.example.md](<IA Workflow/epics.example.md>) a esos nombres.
Cada paso se ejecuta por separado cuando se solicita.
