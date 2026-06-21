class System:
    def __init__(self, db):
        self.db = db

    #==================================================
    # Auth
    #==================================================

    def process_login(self, usr, psw):
        # TODO:
        # 1) Verificar que el usuario exista.
        # 2) Validar contraseña.
        # 3) Generar token de autenticación.
        # 4) Asociar el token a la sesión actual.
        # 5) Retornar token y datos básicos del usuario.
        pass

    def process_get_me(self):
        # TODO:
        # 1) Obtener usuario autenticado a partir del token.
        # 2) Buscar información del usuario en base de datos.
        # 3) Retornar datos básicos del perfil.
        pass

    #==================================================
    # Monitoring
    #==================================================

    def process_get_monitored_users(self):
        # TODO:
        # 1) Obtener usuario autenticado.
        # 2) Consultar MonitoringLinks donde el usuario
        #    autenticado sea monitor.
        # 3) Retornar listado de usuarios monitoreados
        #    junto con el rol asociado.
        pass

    def process_get_my_monitors(self):
        # TODO:
        # 1) Obtener usuario autenticado.
        # 2) Consultar MonitoringLinks donde el usuario
        #    autenticado sea monitoreado.
        # 3) Retornar listado de monitores asociados
        #    junto con el rol de cada uno.
        pass

    #==================================================
    # Monitoring Requests
    #==================================================

    def process_create_monitoring_request(
        self,
        elderly_user_id,
        requested_user_id,
        requested_role
    ):
        # TODO:
        # 1) Obtener usuario autenticado.
        # 2) Validar requested_role.
        # 3) Verificar que no exista una solicitud equivalente.
        # 4) Crear objeto MonitoringRequest.
        # 5) Inicializar estados:
        #       elderly_status = pending
        #       requested_user_status = pending
        #       status = pending
        # 6) Inicializar flags de lectura:
        #       elderly_read = False
        #       requested_user_read = False
        # 7) Guardar solicitud en base de datos.
        # 8) Retornar request_id generado.
        pass

    def process_answer_monitoring_request(
        self,
        request_id,
        answer
    ):
        # TODO:
        # 1) Obtener usuario autenticado.
        # 2) Buscar solicitud.
        # 3) Validar que el usuario participe de ella.
        # 4) Actualizar estado correspondiente:
        #       elderly_status
        #       requested_user_status
        # 5) Recalcular estado global.
        #
        # Casos:
        #
        # accepted + accepted:
        #     status = accepted
        #     crear MonitoringLink
        #
        # rejected + cualquiera:
        #     status = rejected
        #
        # pending restantes:
        #     status = pending
        #
        # 6) Guardar cambios.
        # 7) Retornar resultado actualizado.
        pass

    def process_get_monitoring_requests(self):
        # TODO:
        # 1) Obtener usuario autenticado.
        # 2) Consultar solicitudes relacionadas.
        # 3) Marcar como leídas aquellas que correspondan
        #    al usuario autenticado.
        # 4) Retornar listado completo con:
        #       estados
        #       flags de lectura
        #       participantes
        pass

    #==================================================
    # Monitoring Links
    #==================================================

    def process_delete_monitoring_link(
        self,
        link_id
    ):
        # TODO:
        # 1) Obtener usuario autenticado.
        # 2) Buscar MonitoringLink.
        # 3) Verificar permisos para eliminar:
        #       admin
        #       monitor
        #       usuario monitoreado
        # 4) Eliminar relación.
        # 5) Retornar resultado de la operación.
        pass