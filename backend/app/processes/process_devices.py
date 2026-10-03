"""Procesamiento de devices; conserva los mocks y TODO existentes."""
from uuid import uuid4


class DevicesProcesses:
    def process_create_device(self, device_data, device_id=None):
        # La autenticación y los permisos corresponden al blueprint del endpoint.
        # TODO: Persistir el registro completo. Si se indica
        # el ID externo, reemplazar el registro existente; si no, crear uno nuevo.
        # Generar created_at y updated_at en ambas ramas, incluso al reemplazar.

        """
          @override
        Future<String> createDevice(Map<String, dynamic> data, {String? id}) async {
            try {
            data['created_at'] = Timestamp.fromDate(DateTime.now());
            data['updated_at'] = Timestamp.fromDate(DateTime.now());

            if (id != null && id.isNotEmpty) {
                await _firestore.collection('devices').doc(id).set(data);
                return id;
            } else {
                final docRef = await _firestore.collection('devices').add(data);
                return docRef.id;
            }
            } catch (e) {
            throw Exception('Error creating device: $e');
            }
        }
        """

        return device_id or uuid4().hex

    def process_get_device_by_id(self, device_id):
        # La autenticación y los permisos corresponden al blueprint del endpoint.
        # TODO: Consultar el dispositivo mediante el repository.
        # Retornar None si no existe; si existe, todos sus campos e ID real.

        """
          @override
            Future<Map<String, dynamic>?> getDeviceByID(String id) async {
                try {
                final doc = await _firestore.collection('devices').doc(id).get();
                if (!doc.exists) return null;
                final data = doc.data()!;
                data['id'] = doc.id;
                return data;
                } catch (e) {
                throw Exception('Error fetching device: $e');
                }
            }
        """

        device = self._get_mock_devices()["dev_a81f23"].copy()
        device["id"] = device_id
        if device_id == "dev_available":
            device.update(home_id="", owner_id="", connection_by="")
        return device

    def process_update_device(self, device_id, device_data):
        # La autenticación y los permisos corresponden al blueprint del endpoint.
        # Validar la conexión (vacío, phone o ID de hub) y generar updated_at.
        # TODO: Aplicar update parcial (incluidas rutas de campo con puntos); fallar
        # si no existe. Conservar campos omitidos y no regenerar created_at.
        """
          @override
        Future<void> updateDevice(String id, Map<String, dynamic> data) async {
            try {
            data['updated_at'] = Timestamp.fromDate(DateTime.now());
            await _firestore.collection('devices').doc(id).update(data);
            } catch (e) {
            throw Exception('Error updating device: $e');
            }
        }
        """
        return None

    def process_delete_device(self, device_id):
        # La autenticación y los permisos corresponden al blueprint del endpoint.
        # TODO: Eliminar únicamente el documento
        # devices/{device_id}; no eliminar subcolecciones ni desvincular solamente.
        # La eliminación de un documento inexistente también debe ser exitosa.

        """
          @override
        Future<void> deleteDevice(String id) async {
            try {
            await _firestore.collection('devices').doc(id).delete();
            } catch (e) {
            throw Exception('Error deleting device: $e');
            }
        }
        """

        return None

    def process_get_devices_by_owner(self, owner_id):
        # La autenticación y los permisos corresponden al blueprint del endpoint.
        # TODO: Consultar los documentos
        # devices con owner_id == owner_id, sin derivarlo de homes.

        """
          @override
        Future<List<Map<String, dynamic>>> queryDevicesByOwner(String ownerId) async {
            try {
            final querySnapshot = await _firestore
                .collection('devices')
                .where('owner_id', isEqualTo: ownerId)
                .get();

            return querySnapshot.docs.map((doc) {
                final data = doc.data();
                data['id'] = doc.id;
                return data;
            }).toList();
            } catch (e) {
            throw Exception('Error querying devices: $e');
            }
        }
        """

        return self._get_mock_devices()

    def process_get_devices_by_home(self, home_id):
        # La autenticación y los permisos corresponden al blueprint del endpoint.
        # TODO: Consultar
        # sus dispositivos por home_id == home_id, incluidos hubs, mediante el repository.
        """
          @override
  Future<List<Map<String, dynamic>>> queryDevicesByHome(String homeId) async {
    try {
      final querySnapshot = await _firestore
          .collection('devices')
          .where('home_id', isEqualTo: homeId)
          .get();

      return querySnapshot.docs.map((doc) {
        final data = doc.data();
        data['id'] = doc.id;
        return data;
      }).toList();
    } catch (e) {
      throw Exception('Error querying devices by home: $e');
    }
  }
        """
        return self._get_mock_devices()

    def process_get_device_location(self, device_id):
        # La autenticación y los permisos corresponden al blueprint del endpoint.
        # TODO: Recuperar la última ubicación reportada mediante el repository.

        """
          @override
        Future<Map<String, double>> getLocationByDevice(String deviceId) async {
            // Mock implementation for now
            return {'lat': -34.6037, 'lng': -58.3816};
        }
        """
        return {"lat": -34.6037, "long": -58.3816}

    @staticmethod
    def _get_mock_devices():
        return {
            "dev_a81f23": {
                "created_at": 1786789934000,
                "updated_at": 1788286907000,
                "home_id": "home_7f3a92",
                "owner_id": "user_admin_001",
                "is_active": True,
                "type": "pulsera",
                "battery": 87,
                "name": "Sensor Living",
                "connection_by": "hub_001",
                "coords": {"lat": -34.6037, "long": -58.3816},
            },
            "dev_b42c91": {
                "created_at": 1785247863000,
                "updated_at": 1788285492000,
                "home_id": "home_7f3a92",
                "owner_id": "user_admin_001",
                "is_active": True,
                "type": "hub",
                "battery": -1,
                "name": "Hub Entrada",
                "connection_by": "hub_001",
                "coords": {"lat": -34.6032, "long": -58.3809},
            },
            "dev_c73e15": {
                "created_at": 1785663927000,
                "updated_at": 1788285931000,
                "home_id": "home_7f3a92",
                "owner_id": "user_admin_001",
                "is_active": False,
                "type": "pulsera",
                "battery": 31,
                "name": "Sensor Dormitorio",
                "connection_by": "",
                "coords": {"lat": -34.6041, "long": -58.3824},
            },
        }
