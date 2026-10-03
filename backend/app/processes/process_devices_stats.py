"""Procesamiento de devices_stats; conserva los mocks y TODO existentes."""

from datetime import datetime, timedelta

"""
  String _formatDate(DateTime date) {
    return '${date.year.toString().padLeft(4, '0')}-${date.month.toString().padLeft(2, '0')}-${date.day.toString().padLeft(2, '0')}';
  }

  String _formatMonth(DateTime date) {
    return '${date.year.toString().padLeft(4, '0')}-${date.month.toString().padLeft(2, '0')}';
  }
"""

class DevicesStatsProcesses:
    def process_get_daily_metrics(self, device_id, date):
        # La autenticación y los permisos corresponden al blueprint del endpoint.
        # TODO: Consultar las métricas diarias en el repository y retornar {}
        # si no existe el documento, conservando el comportamiento original.

        """
        @override
        Future<Map<String, dynamic>> getDailyMetrics(
            String deviceId,
            DateTime date,
        ) async {
            try {
            final docId = _formatDate(date);
            final doc = await _firestore
                .collection('devices_metrics')
                .doc(deviceId)
                .collection('daily_metrics')
                .doc(docId)
                .get();

            if (!doc.exists) return {};
            final data = doc.data()!;
            data['id'] = doc.id;
            return data;
            } catch (e) {
            throw Exception('Error fetching daily metrics: $e');
            }
        }
        """

        metrics = self._get_mock_daily_metrics()
        metrics["id"] = date
        metrics["updated_at"] = f"{date}T23:59:59Z"
        return metrics

    def process_get_monthly_aggregates(self, device_id, month):
        # La autenticación y los permisos corresponden al blueprint del endpoint.
        # TODO: Consultar los agregados mensuales en el repository y retornar {}
        # si no existe el documento, conservando el comportamiento original.

        """
        @override
        Future<Map<String, dynamic>> getMonthlyAggregates(
            String deviceId,
            DateTime month,
        ) async {
            try {
            final docId = _formatMonth(month);
            final doc = await _firestore
                .collection('devices_metrics')
                .doc(deviceId)
                .collection('monthly_aggregates')
                .doc(docId)
                .get();

            if (!doc.exists) return {};
            final data = doc.data()!;
            data['id'] = doc.id;
            return data;
            } catch (e) {
            throw Exception('Error fetching monthly aggregates: $e');
            }
        }
        """

        aggregates = self._get_mock_monthly_aggregates()
        aggregates["id"] = month
        return aggregates

    def process_get_previous_month_aggregates(self, device_id):
        # La autenticación y los permisos corresponden al blueprint del endpoint.
        # Reutiliza la consulta mensual para conservar el comportamiento original.
        
        """
        @override
        Future<Map<String, dynamic>> getPreviousMonthAggregates(
            String deviceId,
        ) async {
            final now = DateTime.now();
            // Para obtener el mes anterior: restamos 1 al mes actual.
            // DateTime maneja correctamente cuando el mes es 1 (pasa a diciembre del año anterior).
            final previousMonth = DateTime(now.year, now.month - 1);
            return getMonthlyAggregates(deviceId, previousMonth);
        }
        """


        # Mes calendario anterior según la fecha local del servidor, incluido enero.
        now = datetime.now()
        previous_month = now.replace(day=1) - timedelta(days=1)
        month = f"{previous_month.year:04d}-{previous_month.month:02d}"
        return self.process_get_monthly_aggregates(device_id, month)

    def process_get_last_week_metrics(self, device_id):
        # La autenticación y los permisos corresponden al blueprint del endpoint.
        # TODO: Consultar en el repository los últimos siete días, incluido hoy,
        # y retornar únicamente los documentos existentes (o [] si no hay datos).

        """
        @override
        Future<List<Map<String, dynamic>>> getLastWeekMetrics(String deviceId) async {
            final now = DateTime.now();
            final List<String> last7Days = List.generate(7, (index) {
            final date = now.subtract(Duration(days: index));
            return _formatDate(date);
            });

            try {
            final querySnapshot = await _firestore
                .collection('devices_metrics')
                .doc(deviceId)
                .collection('daily_metrics')
                .where(FieldPath.documentId, whereIn: last7Days)
                .get();

            return querySnapshot.docs.map((doc) {
                final data = doc.data();
                data['id'] = doc.id;
                return data;
            }).toList();
            } catch (e) {
            throw Exception('Error fetching last week metrics: $e');
            }
        }
        """
        
        # Mock con datos para cada día del rango, del más antiguo al más reciente.
        today = datetime.now().date()
        metrics = []
        for days_ago in range(6, -1, -1):
            day = today - timedelta(days=days_ago)
            date = f"{day.year:04d}-{day.month:02d}-{day.day:02d}"
            metrics.append(self.process_get_daily_metrics(device_id, date))
        return metrics

    @staticmethod
    def _get_mock_daily_metrics():
        return {
            "id": "2026-09-01",
            "steps": 4350,
            "falls": 0,
            "stumbles": 2,
            "time_lying_down": 8.5,
            "night_rises": 1,
            "panic_button": 0,
            "updated_at": "2026-09-01T23:59:59Z",
        }

    @staticmethod
    def _get_mock_monthly_aggregates():
        return {
            "id": "2026-09",
            "avg_steps": 4120.5,
            "total_falls": 1,
            "total_stumbles": 18,
            "avg_time_lying_down": 7.9,
            "total_night_rises": 14,
            "total_panic_button": 0,
            "sedentarism_level": 45,
            "risk_level": 12,
            "active_days": 13,
        }
