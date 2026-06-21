from .connection import connect

class DataBase:
    def __init__(self):
        pass

    def add_new_user(self, username: str, password: str) -> int:
        '''
        brief:
            Agrega un nuevo usuario a la base de datos.

        params:
            username: Nombre de usuario.
            password: Contraseña del usuario.

        retval:
            user_id del usuario creado.
        '''
        # TODO
        pass

    def delete_user_by_id(self, user_id: int) -> bool:
        '''
        brief:
            Elimina un usuario por su identificador.

        params:
            user_id: Identificador del usuario a eliminar.

        retval:
            True si el usuario fue eliminado.
            False si no existía.
        '''
        # TODO
        pass

    def user_exists(self, username: str) -> bool:
        '''
        brief:
            Verifica si existe un usuario con el username indicado.

        params:
            username: Nombre de usuario a consultar.

        retval:
            True si el usuario existe.
            False si no existe.
        '''
        # TODO
        pass

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
            link_id de la relación creada
            si la relacion ya existe retorna el link_id existente
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

    def get_monitors(self, monitored_user_id: int) -> list:
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

    def get_monitored_users(self, monitor_user_id: int) -> list:
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

    def add_new_monitoring_request(self, monitoring_request) -> int:
        '''
        brief:
            Agrega una nueva solicitud de monitoreo.

        params:
            monitoring_request: Objeto MonitoringRequest con:
                - requester_user_id
                - elderly_user_id
                - requested_user_id
                - requested_role
                - elderly_status
                - requested_user_status
                - status
                - elderly_read
                - requested_user_read

        retval:
            request_id de la solicitud creada.
            Si la solicitud ya existe, devuelve el request_id existente.
        '''
        # TODO
        pass

    def update_monitoring_request_status(
        self,
        request_id: int,
        user_id: int,
        response: str
    ) -> bool:
        '''
        brief:
            Actualiza el estado de respuesta de una solicitud de monitoreo
            para el usuario indicado.

        params:
            request_id: Identificador de la solicitud.
            user_id: Usuario que responde la solicitud.
            response: Respuesta del usuario. Valores esperados:
                - accepted
                - rejected

        retval:
            True si la solicitud fue actualizada.
            False si la solicitud no existe o el usuario no pertenece a ella.
        '''
        # TODO
        pass

    def get_monitoring_request_by_id(self, request_id: int):
        '''
        brief:
            Obtiene una solicitud de monitoreo por su identificador.

        params:
            request_id: Identificador de la solicitud.

        retval:
            Objeto MonitoringRequest si existe.
            None si no existe.
        '''
        # TODO
        pass

    def delete_monitoring_request_by_id(self, request_id: int) -> bool:
        '''
        brief:
            Elimina una solicitud de monitoreo por su identificador.

        params:
            request_id: Identificador de la solicitud.

        retval:
            True si la solicitud fue eliminada.
            False si no existía.
        '''
        # TODO
        pass

    def get_monitoring_requests(self, user_id: int) -> list:
        '''
        brief:
            Obtiene las solicitudes de monitoreo relacionadas con un usuario.

        params:
            user_id: Identificador del usuario.

        retval:
            Lista de objetos MonitoringRequest donde el usuario participa como:
                - requester_user_id
                - elderly_user_id
                - requested_user_id
        '''
        # TODO
        pass

    def mark_monitoring_request_as_read(
        self,
        request_id: int,
        user_id: int
    ) -> bool:
        '''
        brief:
            Marca como leída una solicitud para el usuario indicado.

        params:
            request_id: Identificador de la solicitud.
            user_id: Usuario que marca la solicitud como leída.

        retval:
            True si fue actualizada.
            False si el usuario no participa en la solicitud
            o la solicitud no existe.
        '''
        # TODO
        pass