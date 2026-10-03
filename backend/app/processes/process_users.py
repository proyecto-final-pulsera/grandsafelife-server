"""Procesamiento de users; conserva los mocks y TODO existentes."""


class UsersProcesses:
    def process_get_user_by_id(self, user_id):
        # La autenticación y los permisos corresponden al blueprint del endpoint.
        #TODO replicar comportamiento exacto de guido
        """
          @override
            Future<Map<String, dynamic>?> getUserByID(String id) async {
                try {
                final doc = await _firestore.collection('users').doc(id).get();
                if (!doc.exists) return null;
                final data = doc.data()!;
                data['id'] = doc.id;
                return data;
                } catch (e) {
                throw Exception('Error fetching user: $e');
                }
            }
        """

        return {
            "id": user_id,
            "name": "María Gómez",
            "email": "maria.gomez@example.com",
            "avatar": "https://example.com/avatars/user_002.png",
            "created_at": 1783700000000,
            "updated_at": 1783882718000,
            "homes": {
                "home_id_001": {
                    "home_name": "Residencia Principal",
                    "role": "admin",
                },
                "home_id_002": {
                    "home_name": "Casa de Campo",
                    "role": "pending",
                },
            },
        }

    def process_get_user_by_email(self, email):
        # La autenticación y los permisos corresponden al blueprint del endpoint.
        # TODO: Buscar el UID del usuario destino por email mediante el repository.

        """
          @override
            Future<Map<String, dynamic>?> getUserByEmail(String email) async {
                try {
                final querySnapshot = await _firestore
                    .collection('users')
                    .where('email', isEqualTo: email)
                    .limit(1)
                    .get();

                if (querySnapshot.docs.isEmpty) return null;

                final doc = querySnapshot.docs.first;
                final data = doc.data();
                data['id'] = doc.id;
                return data;
                } catch (e) {
                throw Exception('Error fetching user by email: $e');
                }
            }
        """

        user = self.process_get_user_by_id("user_002")
        return {**user, "email": email}

    def process_create_user(self, user_data, user_id=None):
        # La autenticación y los permisos corresponden al blueprint del endpoint.
        # TODO: Con ID,
        # crear o reemplazar el documento completo mediante el repository (sin
        # merge); sin ID, generar uno. Conservar todos los campos recibidos,
        # incluidos homes e id. Generar created_at y updated_at en ambos casos.

        """
         @override
            Future<String> createUser(Map<String, dynamic> data, {String? id}) async {
                try {
                data['created_at'] = Timestamp.fromDate(DateTime.now());
                data['updated_at'] = Timestamp.fromDate(DateTime.now());

                if (id != null && id.isNotEmpty) {
                    await _firestore.collection('users').doc(id).set(data);
                    return id;
                } else {
                    final docRef = await _firestore.collection('users').add(data);
                    return docRef.id;
                }
                } catch (e) {
                throw Exception('Error creating user: $e');
                }
            } 
        """

        return {"user_id": user_id or "firebase_uid_mock"}

    def process_update_user(self, user_id, user_data):
        # La autenticación y los permisos corresponden al blueprint del endpoint.
        # TODO: Aplicar update parcial mediante el repository y generar updated_at en el
        # servidor, sobrescribiendo el recibido. Conservar campos omitidos y
        # valores nulos; aceptar rutas con puntos. Fallar si no existe el usuario.
        # created_at solo cambia si se recibe explícitamente (milisegundos Unix).

        """
          @override
        Future<void> updateUser(String id, Map<String, dynamic> data) async {
            try {
            data['updated_at'] = Timestamp.fromDate(DateTime.now());
            await _firestore.collection('users').doc(id).update(data);
            } catch (e) {
            throw Exception('Error updating user: $e');
            }
        }
        """
        return None
