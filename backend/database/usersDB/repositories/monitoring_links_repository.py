# database/monitoring_links_repository.py

from ..connection import connect
from domain.monitoring_link import MonitoringLink

class MonitoringLinksRepository:
    def _row_to_monitoring_link(self, row):
        if row is None:
            return None

        return MonitoringLink(
            link_id=row[0],
            elderly_user_id=row[1],
            monitor_user_id=row[2],
            monitor_role=row[3]
        )
    
    def add_new_monitoring_link(self, monitoring_link) -> int:
        conn = connect()
        cur = conn.cursor()

        cur.execute(
            """
            SELECT link_id
            FROM monitoring_links
            WHERE monitored_user_id = %s
              AND monitor_user_id = %s
              AND monitor_role = %s;
            """,
            (
                monitoring_link.elderly_user_id,
                monitoring_link.monitor_user_id,
                monitoring_link.monitor_role
            )
        )

        row = cur.fetchone()

        if row is not None:
            link_id = row[0]
        else:
            cur.execute(
                """
                INSERT INTO monitoring_links (
                    monitored_user_id,
                    monitor_user_id,
                    monitor_role
                )
                VALUES (%s, %s, %s)
                RETURNING link_id;
                """,
                (
                    monitoring_link.elderly_user_id,
                    monitoring_link.monitor_user_id,
                    monitoring_link.monitor_role
                )
            )

            link_id = cur.fetchone()[0]

        conn.commit()
        cur.close()
        conn.close()

        return link_id

    def delete_monitoring_link_by_id(self, link_id: int) -> bool:
        conn = connect()
        cur = conn.cursor()

        cur.execute(
            """
            DELETE FROM monitoring_links
            WHERE link_id = %s;
            """,
            (link_id,)
        )

        deleted = cur.rowcount > 0

        conn.commit()
        cur.close()
        conn.close()

        return deleted

    def get_monitors_by_monitored_user_id(self, monitored_user_id: int) -> list:
        conn = connect()
        cur = conn.cursor()

        cur.execute(
            """
            SELECT
                link_id,
                monitored_user_id,
                monitor_user_id,
                monitor_role
            FROM monitoring_links
            WHERE monitored_user_id = %s;
            """,
            (monitored_user_id,)
        )

        rows = cur.fetchall()

        cur.close()
        conn.close()

        return [
            self._row_to_monitoring_link(row)
            for row in rows
        ]

    def get_monitored_users_by_monitor_user_id(self, monitor_user_id: int) -> list:
        conn = connect()
        cur = conn.cursor()

        cur.execute(
            """
            SELECT
                link_id,
                monitored_user_id,
                monitor_user_id,
                monitor_role
            FROM monitoring_links
            WHERE monitor_user_id = %s;
            """,
            (monitor_user_id,)
        )

        rows = cur.fetchall()

        cur.close()
        conn.close()

        return [
            self._row_to_monitoring_link(row)
            for row in rows
        ]