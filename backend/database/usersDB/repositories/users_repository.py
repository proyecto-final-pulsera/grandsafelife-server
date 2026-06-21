from ..connection import connect
from domain.user import User


class UsersRepository:
    def _row_to_user(self, row):
        if row is None:
            return None

        return User(
            user_id=row[0],
            username=row[1],
            password=row[2]
        )

    def add_new_user(self, user) -> int:
        conn = connect()
        cur = conn.cursor()

        cur.execute(
            """
            INSERT INTO users (
                username,
                password
            )
            VALUES (%s, %s)
            RETURNING user_id;
            """,
            (
                user.username,
                user.password
            )
        )

        user_id = cur.fetchone()[0]

        conn.commit()
        cur.close()
        conn.close()

        return user_id

    def delete_user_by_id(self, user_id: int) -> bool:
        conn = connect()
        cur = conn.cursor()

        cur.execute(
            """
            DELETE FROM users
            WHERE user_id = %s;
            """,
            (user_id,)
        )

        deleted = cur.rowcount > 0

        conn.commit()
        cur.close()
        conn.close()

        return deleted

    def user_exists_by_username(self, username: str) -> bool:
        conn = connect()
        cur = conn.cursor()

        cur.execute(
            """
            SELECT 1
            FROM users
            WHERE username = %s;
            """,
            (username,)
        )

        exists = cur.fetchone() is not None

        cur.close()
        conn.close()

        return exists

    def get_user_by_username(self, username: str):
        conn = connect()
        cur = conn.cursor()

        cur.execute(
            """
            SELECT
                user_id,
                username,
                password
            FROM users
            WHERE username = %s;
            """,
            (username,)
        )

        row = cur.fetchone()

        cur.close()
        conn.close()

        return self._row_to_user(row)

    def get_user_by_id(self, user_id: int):
        conn = connect()
        cur = conn.cursor()

        cur.execute(
            """
            SELECT
                user_id,
                username,
                password
            FROM users
            WHERE user_id = %s;
            """,
            (user_id,)
        )

        row = cur.fetchone()

        cur.close()
        conn.close()

        return self._row_to_user(row)