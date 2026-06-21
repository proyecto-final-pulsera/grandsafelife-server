# database/monitoring_links_repository.py

from .connection import connect


class MonitoringLinksRepository:
    def add_new_monitoring_link(self, monitoring_link) -> int:
        '''
        brief:
            Agrega una nueva relación de monitoreo.

        params:
            monitoring_link: Objeto MonitoringLink con:
                - monitored_user_id
                - monitor_user_id
                - monitor_role

        retval:
            link_id de la relación creada.
            Si la relación ya existe, retorna el link_id existente.
        '''
        # TODO
        pass

    def delete_monitoring_link_by_id(self, link_id: int) -> bool:
        '''
        brief:
            Elimina una relación de monitoreo por su identificador.

        params:
            link_id: Identificador de la relación a eliminar.

        retval:
            True si la relación fue eliminada.
            False si no existía.
        '''
        # TODO
        pass

    def get_monitors_by_monitored_user_id(self, monitored_user_id: int) -> list:
        '''
        brief:
            Obtiene los usuarios que monitorean a un usuario determinado.

        params:
            monitored_user_id: Identificador del usuario monitoreado.

        retval:
            Lista de objetos MonitoringLink donde:
                - monitored_user_id coincide con el parámetro recibido.
        '''
        # TODO
        pass

    def get_monitored_users_by_monitor_user_id(self, monitor_user_id: int) -> list:
        '''
        brief:
            Obtiene los usuarios monitoreados por un usuario determinado.

        params:
            monitor_user_id: Identificador del usuario que monitorea.

        retval:
            Lista de objetos MonitoringLink donde:
                - monitor_user_id coincide con el parámetro recibido.
        '''
        # TODO
        pass