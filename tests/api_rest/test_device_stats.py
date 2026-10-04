from datetime import datetime, timedelta, timezone
from base_api_test import BaseApiTest


class DevicesStatsTests(BaseApiTest):
    def test_daily_monthly_and_week(self):
        """Consultar métricas diarias, mensuales, del mes anterior y de la última semana."""
        prefix = f'/devices/{self.key}/stats'
        root = f'devices_metrics/{self.key}'
        today = datetime.now().date()
        self.assertEqual(self.success('GET', prefix + '/daily?date=' + today.isoformat()), {})
        self.assertEqual(self.success('GET', prefix + '/monthly?month=2000-01'), {})
        self.assertEqual(self.success('GET', prefix + '/daily/last-week'), [])
        stamp = datetime(2026, 1, 1, tzinfo=timezone.utc)
        for index in (0, 3, 6, 7):
            day = (today - timedelta(days=index)).isoformat()
            self.ref(root + '/daily_metrics/' + day).set({'steps': index, 'updated_at': stamp})
        day = today.isoformat()
        self.assertEqual(self.success('GET', prefix + '/daily?date=' + day),
                         {'id': day, 'steps': 0, 'updated_at': '2026-01-01T00:00:00Z'})
        week = self.success('GET', prefix + '/daily/last-week')
        self.assertEqual([row['id'] for row in week], sorted((today - timedelta(days=i)).isoformat() for i in (0, 3, 6)))
        previous = (today.replace(day=1) - timedelta(days=1)).strftime('%Y-%m')
        self.ref(root + '/monthly_aggregates/' + previous).set({'avg_steps': 123.5})
        expected = {'id': previous, 'avg_steps': 123.5}
        self.assertEqual(self.success('GET', prefix + '/monthly?month=' + previous), expected)
        self.assertEqual(self.success('GET', prefix + '/monthly/previous'), expected)

    def test_invalid_queries(self):
        """Rechazar fechas y meses inválidos o ausentes."""
        prefix = f'/devices/{self.key}/stats'
        for query in ('/daily', '/daily?date=no-date', '/monthly', '/monthly?month=2026-13'):
            self.rejected('GET', prefix + query, None)
