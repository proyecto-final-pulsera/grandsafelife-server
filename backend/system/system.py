class System:
    def __init__(self, db):
        self.db = db

    def process_create_table(self):
        self.db.create_users_table()
        return {"mensaje": "Tabla usuarios creada"}

    def process_create_user(self, usr, psw):
        self.db.create_user(usr, psw)
        return {"mensaje": "Usuario creado"}

    def process_get_users(self):
        usuarios = self.db.get_users()
        return {"usuarios": usuarios}

    def process_delete_user(self, id_usuario):
        self.db.delete_user(id_usuario)
        return {"mensaje": "Usuario eliminado"}