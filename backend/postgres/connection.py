import psycopg2

DB_CONFIG = {
    "host": "postgres_db",
    "port": 5432,
    "database": "postgres",
    "user": "postgres",
    "password": "1234"
}

def connect():
    return psycopg2.connect(**DB_CONFIG)