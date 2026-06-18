from fastapi import FastAPI
from pydantic import BaseModel
import psycopg2

app = FastAPI()

DB_CONFIG = {
    "host": "postgres_db",
    "port": 5432,
    "database": "postgres",
    "user": "postgres",
    "password": "1234"
}

class Usuario(BaseModel):
    usr: str
    psw: str

def conectar_db():
    return psycopg2.connect(**DB_CONFIG)

@app.post("/crear_tabla")
def crear_tabla():
    conn = conectar_db()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id SERIAL PRIMARY KEY,
            usr VARCHAR(50),
            psw VARCHAR(50)
        );
    """)

    conn.commit()
    cur.close()
    conn.close()
    return {"mensaje": "Tabla usuarios creada"}

@app.post("/usuarios")
def crear_usuario(usuario: Usuario):
    conn = conectar_db()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO usuarios (usr, psw) VALUES (%s, %s);",
        (usuario.usr, usuario.psw)
    )
    conn.commit()
    cur.close()
    conn.close()
    return {"mensaje": "Usuario creado"}


@app.get("/usuarios")
def consultar_usuarios():
    conn = conectar_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM usuarios;")
    usuarios = cur.fetchall()
    cur.close()
    conn.close()
    return {"usuarios": usuarios}

@app.delete("/usuarios/{id_usuario}")
def eliminar_usuario(id_usuario: int):
    conn = conectar_db()
    cur = conn.cursor()
    cur.execute("DELETE FROM usuarios WHERE id = %s;",(id_usuario,))
    conn.commit()
    cur.close()
    conn.close()
    return {"mensaje": "Usuario eliminado"}