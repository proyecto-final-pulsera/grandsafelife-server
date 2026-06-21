# database/monitoring_requests_repository.py

from .connection import connect


class MonitoringRequestsRepository:
    def add_new_monitoring_request(self, monitoring_request) -> int:
        '''
        brief:
            Agrega una nueva solicitud de monitoreo.

        params:
            monitoring_request: Objeto MonitoringRequest

        retval:
            request_id de la solicitud creada.
            Si la solicitud ya existe, devuelve el request_id existente.
        '''
        # TODO
        pass

    def update_monitoring_request_status_by_id(
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
            response: Respuesta del usuario (accepted / rejected)

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

    def get_monitoring_requests_by_user_id(self, user_id: int) -> list:
        '''
        brief:
            Obtiene las solicitudes de monitoreo relacionadas con un usuario.

        params:
            user_id: Identificador del usuario.

        retval:
            Lista de objetos MonitoringRequest donde el usuario participa como:
                - target_user_id
                - elderly_user_id
        '''
        # TODO
        pass

    def mark_monitoring_request_as_read_by_id(
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
            False si el usuario no participa en la solicitud o la solicitud no existe.
        '''
        # TODO
        pass