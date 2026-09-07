class User:
    """
    Usuario registrado en el sistema.
    Esta entidad representa únicamente credenciales e identidad.
    """
    def __init__(
        self,
        user_id=None,
        username="",
        password=""
    ):
        self.user_id = user_id
        self.username = username
        self.password = password