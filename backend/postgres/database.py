import psycopg2


DB_CONFIG = {
    "host": "postgres_db",
    "port": 5432,
    "database": "postgres",
    "user": "postgres",
    "password": "1234"
}


class DataBase:
    def __init__(self):
        pass

    def connect(self):
        return psycopg2.connect(**DB_CONFIG)

    def create_users_table(self):
        conn = self.connect()
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

    def create_user(self, usr, psw):
        conn = self.connect()
        cur = conn.cursor()

        cur.execute(
            "INSERT INTO usuarios (usr, psw) VALUES (%s, %s);",
            (usr, psw)
        )

        conn.commit()
        cur.close()
        conn.close()

    def get_users(self):
        conn = self.connect()
        cur = conn.cursor()

        cur.execute("SELECT * FROM usuarios;")
        usuarios = cur.fetchall()

        cur.close()
        conn.close()

        return usuarios

    def delete_user(self, id_usuario):
        conn = self.connect()
        cur = conn.cursor()

        cur.execute("DELETE FROM usuarios WHERE id = %s;", (id_usuario,))

        conn.commit()
        cur.close()
        conn.close()