"""Procesamiento de monitoring; conserva los mocks y TODO existentes."""


class MonitoringProcesses:
    def process_get_monitored_users(self, authorization):
        # TODO:
        # 1) Obtener usuario autenticado.
        # 2) Consultar MonitoringLinks donde el usuario
        #    autenticado sea monitor.
        # 3) Retornar listado de usuarios monitoreados
        #    junto con el rol asociado.
        pass

    def process_get_my_monitors(self, authorization):
        # TODO:
        # 1) Obtener usuario autenticado.
        # 2) Consultar MonitoringLinks donde el usuario
        #    autenticado sea monitoreado.
        # 3) Retornar listado de monitores asociados
        #    junto con el rol de cada uno.
        pass

    def process_delete_monitoring_link(
        self,
        authorization,
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
