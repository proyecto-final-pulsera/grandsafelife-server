class MonitoringRequest:
    """
    Solicitud pendiente entre dos usuarios.

    requester_user_id:
        Usuario que genera la solicitud.

    target_user_id:
        Usuario que debe aceptarla o rechazarla.

    requested_role:
        Rol que tendrá el solicitante si la solicitud es aceptada.

    status:
        - pending
        - accepted
        - rejected

    elderly_read:
        Confirmacion de lectura notificacion
    
    requested_user_read:
        Confirmacion de lectura notificacion
    """    
    def __init__(
        self,
        request_id=None,
        
        #Usuarios involucrados
        requester_user_id=None,
        target_user_id=None,
        requested_role="",

        #Estado confirmacion
        elderly_status="",
        monitor_status="",
        status="",

        #Confirmacion lectura
        elderly_read = False,
        requested_user_read = False,

    ):
        self.request_id = request_id
        self.requester_user_id = requester_user_id
        self.target_user_id = target_user_id
        self.requested_role = requested_role
        self.elderly_status = elderly_status
        self.monitor_status = monitor_status
        self.status = status
        self.elderly_read = elderly_read 
        self.requested_user_read = requested_user_read