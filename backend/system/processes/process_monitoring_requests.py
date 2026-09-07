"""Procesamiento de monitoring_requests; conserva los mocks y TODO existentes."""


class MonitoringRequestsProcesses:
    def process_create_monitoring_request(self, authorization, home_id, data):
        # TODO: Verificar el token y el rol administrador del solicitante,
        # resolver el destinatario por email, prevenir membresías o solicitudes
        # pendientes duplicadas, persistir y enviar la notificación.
        return "request_id_001"

    def process_get_my_monitoring_requests(self, authorization):
        # TODO: Verificar el token y consultar las solicitudes pendientes
        # recibidas por el usuario autenticado mediante el repository.
        return [
            {
                "request_id": "request_id_001",
                "home_id": "home_id_001",
                "home_name": "Residencia Principal",
                "requester": {
                    "name": "Juan Pérez",
                    "email": "juan.perez@example.com",
                },
                "requested_role": "observer",
                "status": "pending",
                "created_at": 1783882718000,
                "updated_at": 1783882718000,
            }
        ]

    def process_answer_monitoring_request(
        self,
        authorization,
        request_id,
        answer
    ):
        # TODO: Verificar token, existencia y estado pendiente de la solicitud,
        # y que el usuario autenticado sea su destinatario. Si acepta, agregar
        # atómicamente ambas relaciones de membresía; si rechaza, no agregarlas.
        # Persistir el estado definitivo y enviar las notificaciones necesarias.
        return None
