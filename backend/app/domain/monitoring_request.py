class MonitoringRequest:
    """
    Solicitud pendiente entre usuarios.

    requester_user_id:
        Usuario que genera la solicitud.

    monitored_user_id:
        Usuario anciano involucrado.

    requested_user_id:
        Usuario al que se le solicita participar
        como admin o monitor.

    requested_role: 
        Persona que monitorea
        admin | monitor

    monitored_user_status:
        Estado de confirmacion del anciano
        pending | accepted | rejected

    requested_user_status:
        Estado de confirmacion de la persona que monitorea
        pending | accepted | rejected

    status:
        Estado general del request
        pending | accepted | rejected
    
    monitored_read:
        Confrmación de lectura de app anciano 
        True | False
        
    requested_read:
        Confrmación de lectura de app monitor
        True | False
    """

    def __init__(
        self,
        request_id=None,

        requester_user_id=None,
        monitored_user_id=None,
        requested_user_id=None,

        requested_role="",

        monitored_user_status="",
        requested_user_status="",
        status="",

        monitored_read=False,
        requested_read=False
    ):
        self.request_id = request_id

        self.requester_user_id = requester_user_id
        self.monitored_user_id = monitored_user_id
        self.requested_user_id = requested_user_id

        self.requested_role = requested_role

        self.monitored_user_status = monitored_user_status
        self.requested_user_status = requested_user_status
        self.status = status

        self.monitored_read = monitored_read
        self.requested_read = requested_read