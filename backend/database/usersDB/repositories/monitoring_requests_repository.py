# database/monitoring_requests_repository.py

from ..connection import connect
from domain.monitoring_request import MonitoringRequest


class MonitoringRequestsRepository:
    def _row_to_monitoring_request(self, row):
        if row is None:
            return None

        return MonitoringRequest(
            request_id=row[0],
            requester_user_id=row[1],
            target_user_id=row[3],
            requested_role=row[4],
            elderly_status=row[5],
            monitor_status=row[6],
            status=row[7],
            elderly_read=row[8],
            requested_user_read=row[9]
        )

    def add_new_monitoring_request(self, monitoring_request) -> int:
        conn = connect()
        cur = conn.cursor()

        cur.execute(
            """
            SELECT request_id
            FROM monitoring_requests
            WHERE requester_user_id = %s
              AND elderly_user_id = %s
              AND requested_user_id = %s
              AND requested_role = %s
              AND status = 'pending';
            """,
            (
                monitoring_request.requester_user_id,
                monitoring_request.elderly_user_id,
                monitoring_request.target_user_id,
                monitoring_request.requested_role
            )
        )

        row = cur.fetchone()

        if row is not None:
            request_id = row[0]
        else:
            cur.execute(
                """
                INSERT INTO monitoring_requests (
                    requester_user_id,
                    elderly_user_id,
                    requested_user_id,
                    requested_role,
                    elderly_status,
                    requested_user_status,
                    status,
                    elderly_read,
                    requested_user_read
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING request_id;
                """,
                (
                    monitoring_request.requester_user_id,
                    monitoring_request.elderly_user_id,
                    monitoring_request.target_user_id,
                    monitoring_request.requested_role,
                    monitoring_request.elderly_status,
                    monitoring_request.monitor_status,
                    monitoring_request.status,
                    monitoring_request.elderly_read,
                    monitoring_request.requested_user_read
                )
            )

            request_id = cur.fetchone()[0]

        conn.commit()
        cur.close()
        conn.close()

        return request_id

    '''Retorna True si pudo actualizar'''
    def update_monitoring_request_status_by_id(
        self,
        request_id: int,
        user_id: int,
        response: str
    ) -> bool:
        request = self.get_monitoring_request_by_id(request_id)

        if request is None:
            return False

        conn = connect()
        cur = conn.cursor()

        if user_id == request.elderly_user_id:
            cur.execute(
                """
                UPDATE monitoring_requests
                SET elderly_status = %s
                WHERE request_id = %s;
                """,
                (response, request_id)
            )

        elif user_id == request.target_user_id:
            cur.execute(
                """
                UPDATE monitoring_requests
                SET requested_user_status = %s
                WHERE request_id = %s;
                """,
                (response, request_id)
            )

        else:
            cur.close()
            conn.close()
            return False

        updated = cur.rowcount > 0

        conn.commit()
        cur.close()
        conn.close()

        return updated

    def get_monitoring_request_by_id(self, request_id: int):
        conn = connect()
        cur = conn.cursor()

        cur.execute(
            """
            SELECT
                request_id,
                requester_user_id,
                elderly_user_id,
                requested_user_id,
                requested_role,
                elderly_status,
                requested_user_status,
                status,
                elderly_read,
                requested_user_read
            FROM monitoring_requests
            WHERE request_id = %s;
            """,
            (request_id,)
        )

        row = cur.fetchone()

        cur.close()
        conn.close()

        return self._row_to_monitoring_request(row)

    def delete_monitoring_request_by_id(self, request_id: int) -> bool:
        conn = connect()
        cur = conn.cursor()

        cur.execute(
            """
            DELETE FROM monitoring_requests
            WHERE request_id = %s;
            """,
            (request_id,)
        )

        deleted = cur.rowcount > 0

        conn.commit()
        cur.close()
        conn.close()

        return deleted

    def get_monitoring_requests_by_user_id(self, user_id: int) -> list:
        conn = connect()
        cur = conn.cursor()

        cur.execute(
            """
            SELECT
                request_id,
                requester_user_id,
                elderly_user_id,
                requested_user_id,
                requested_role,
                elderly_status,
                requested_user_status,
                status,
                elderly_read,
                requested_user_read
            FROM monitoring_requests
            WHERE elderly_user_id = %s
               OR requested_user_id = %s;
            """,
            (user_id, user_id)
        )

        rows = cur.fetchall()

        cur.close()
        conn.close()

        return [
            self._row_to_monitoring_request(row)
            for row in rows
        ]

    def mark_monitoring_request_as_read_by_id(
        self,
        request_id: int,
        user_id: int
    ) -> bool:
        request = self.get_monitoring_request_by_id(request_id)

        if request is None:
            return False

        conn = connect()
        cur = conn.cursor()

        if user_id == request.elderly_user_id:
            cur.execute(
                """
                UPDATE monitoring_requests
                SET elderly_read = TRUE
                WHERE request_id = %s;
                """,
                (request_id,)
            )

        elif user_id == request.target_user_id:
            cur.execute(
                """
                UPDATE monitoring_requests
                SET requested_user_read = TRUE
                WHERE request_id = %s;
                """,
                (request_id,)
            )

        else:
            cur.close()
            conn.close()
            return False

        updated = cur.rowcount > 0

        conn.commit()
        cur.close()
        conn.close()

        return updated