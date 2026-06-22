from .connection import connect


class DataBaseSchema:
    def create_tables(self):
        conn = connect()
        cur = conn.cursor()

        # Tabla de usuarios
        cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id SERIAL PRIMARY KEY,
                username VARCHAR(50) NOT NULL UNIQUE,
                password VARCHAR(100) NOT NULL
            );
        """)


        # Tabla de dispositivos
        cur.execute("""
            CREATE TABLE IF NOT EXISTS devices (
                device_id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL
            );
        """)

        # Tabla de monitoreo
        cur.execute("""
            CREATE TABLE IF NOT EXISTS monitoring_links (
                link_id SERIAL PRIMARY KEY,

                monitored_user_id INTEGER NOT NULL,
                monitor_user_id INTEGER NOT NULL,

                monitor_role VARCHAR(20) NOT NULL
            );
        """)

        # Tabla solicitudes de monitoreo
        cur.execute("""
            CREATE TABLE IF NOT EXISTS monitoring_requests (
                request_id SERIAL PRIMARY KEY,

                requester_user_id INTEGER NOT NULL,
                monitored_user_id INTEGER NOT NULL,
                requested_user_id INTEGER NOT NULL,

                requested_role VARCHAR(20) NOT NULL,

                monitored_user_status VARCHAR(20) NOT NULL,
                requested_user_status VARCHAR(20) NOT NULL,
                status VARCHAR(20) NOT NULL,

                monitored_read BOOLEAN NOT NULL DEFAULT FALSE,
                requested_read BOOLEAN NOT NULL DEFAULT FALSE
            );
        """)

        conn.commit()
        cur.close()
        conn.close()