from fastapi import FastAPI
from pydantic import BaseModel


class Usuario(BaseModel):
    usr: str
    psw: str


def create_http_app(system):
    app = FastAPI()

    @app.post("/crear_tabla")
    def crear_tabla():
        return system.process_create_table()

    @app.post("/usuarios")
    def crear_usuario(usuario: Usuario):
        return system.process_create_user(usuario.usr, usuario.psw)

    @app.get("/usuarios")
    def consultar_usuarios():
        return system.process_get_users()

    @app.delete("/usuarios/{id_usuario}")
    def eliminar_usuario(id_usuario: int):
        return system.process_delete_user(id_usuario)

    return app