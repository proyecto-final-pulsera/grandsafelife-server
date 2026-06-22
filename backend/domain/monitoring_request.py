class MonitoringRequest:
    """
    Solicitud pendiente entre usuarios.

    requester_user_id:
        Usuario que genera la solicitud.

    elderly_user_id:
        Usuario anciano involucrado.

    requested_user_id:
        Usuario al que se le solicita participar
        como admin o monitor.

    requested_role: 
        Persona que monitorea
        admin | monitor

    elderly_status:
        Estado de confirmacion del anciano
        pending | accepted | rejected

    requested_user_status:
        Estado de confirmacion de la persona que monitorea
        pending | accepted | rejected

    status:
        Estado general del request
        pending | accepted | rejected
    
    elderly_read:
        Confrmación de lectura de app anciano 
        True | False
        
    requested_user_read:
        Confrmación de lectura de app monitor
        True | False
    """

    def __init__(
        self,
        request_id=None,

        requester_user_id=None,
        elderly_user_id=None,
        requested_user_id=None,

        requested_role="",

        elderly_status="",
        requested_user_status="",
        status="",

        elderly_read=False,
        requested_user_read=False
    ):
        self.request_id = request_id

        self.requester_user_id = requester_user_id
        self.elderly_user_id = elderly_user_id
        self.requested_user_id = requested_user_id

        self.requested_role = requested_role

        self.elderly_status = elderly_status
        self.requested_user_status = requested_user_status
        self.status = status

        self.elderly_read = elderly_read
        self.requested_user_read = requested_user_read