class Device:
    """
    Asociación dispositivo a usuario.
    El dispositivo sería una pulsera
    El usuario sería alguien con perfil de anciano
    """
    def __init__(
        self,
        device_id=None,
        user_id=""
    ):
        self.device_id = device_id
        self.user_id = user_id