class MonitoringLink:
    """
    Representa una relación de monitoreo entre dos usuarios.

    El usuario identificado por elderly_user_id es el usuario monitoreado.

    El usuario identificado por monitor_user_id posee permisos sobre el
    usuario monitoreado según el rol indicado en monitor_role.

    Roles soportados:
        - admin: acceso completo sobre la configuración y monitoreo.
        - guest: acceso restringido.
    """

    def __init__(
        self,
        link_id=None,
        elderly_user_id=None,
        monitor_user_id=None,
        monitor_role=""
    ):
        self.link_id = link_id
        self.elderly_user_id = elderly_user_id
        self.monitor_user_id = monitor_user_id
        self.monitor_role = monitor_role