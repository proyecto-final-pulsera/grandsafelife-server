"""Infraestructura compartida para probar la API con Firebase local."""
import json
import os
import unittest
from datetime import datetime, timezone
from urllib.error import HTTPError
from urllib.request import Request, build_opener, ProxyHandler, HTTPRedirectHandler
from uuid import uuid4

#=====================================================
# Helpers
#=====================================================

# Proyecto de pruebas y URL base de la API local.
PROJECT = 'demo-grandsafelife'
API = f'http://127.0.0.1:5001/{PROJECT}/us-central1/api/grandsafelife/api/v1'


# Impide que el cliente HTTP siga redirecciones automáticamente.
class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        """Recibe una redirección HTTP y devuelve None para impedir su seguimiento."""
        return None


# Envía una petición HTTP y devuelve el código de estado y el contenido.
def http(method, url, body=None, headers=None):
    """Recibe método, URL, body y headers; devuelve (estado HTTP, JSON o texto)."""
    request = Request(url, data=None if body is None else json.dumps(body).encode(),
                      headers={'Content-Type': 'application/json', **(headers or {})}, method=method)
    # Envía la petición sin usar proxies ni seguir redirecciones.
    opener = build_opener(ProxyHandler({}), NoRedirect())
    try:
        response = opener.open(request, timeout=30)
    except HTTPError as error:
        response = error
    with response:
        raw = response.read().decode()
        try:
            result = json.loads(raw)
        except ValueError:
            result = raw
        return response.status, result


# Verifica las variables de entorno y los emuladores registrados en el hub.
def require_emulators():
    """Sin argumentos; valida el entorno local. Retorna None o lanza un error."""
    expected = {'GCLOUD_PROJECT': PROJECT, 'FIRESTORE_EMULATOR_HOST': '127.0.0.1:8080',
                'FIREBASE_AUTH_EMULATOR_HOST': '127.0.0.1:9099'}
    for key, value in expected.items():
        if os.environ.get(key) != value:
            raise RuntimeError(f'{key} debe ser {value}. Usar el ejecutor de tests/README.md.')
    status, hub = http('GET', 'http://127.0.0.1:4400/emulators')
    if status != 200:
        raise RuntimeError('No responde el hub de emuladores.')
    for name, port in [('auth', 9099), ('firestore', 8080), ('functions', 5001)]:
        if hub.get(name, {}).get('port') != port:
            raise RuntimeError(f'Falta el emulador {name} en el puerto {port}.')

#=====================================================
# Clase de tests base
#=====================================================
class BaseApiTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Recibe la clase del test (Ej. UserTests); prepara su cliente Firestore y registra su cierre"""
        require_emulators()
        from google.auth.credentials import AnonymousCredentials
        from google.cloud.firestore import Client
        cls.db = Client(project=PROJECT, credentials=AnonymousCredentials())
        cls.addClassCleanup(cls.db.close)

    def setUp(self):
        """Inicia sesion con usuario de prueba y token sesion."""
        self.key = 'test-' + uuid4().hex
        self.refs = []
        status, user = http('POST', 'http://127.0.0.1:9099/identitytoolkit.googleapis.com/v1/accounts:signUp?key=local-test',
                            {'email': self.key + '@example.com', 'password': 'LocalTest123!', 'returnSecureToken': True})
        self.assertEqual(status, 200, user)
        self.token = user['idToken']
        self.addCleanup(self.cleanup)

    def cleanup(self):
        """Elimina los documentos registrados y el usuario Auth del test."""
        try:
            for ref in reversed(self.refs):
                ref.delete()
        finally:
            status, result = http('POST', 'http://127.0.0.1:9099/identitytoolkit.googleapis.com/v1/accounts:delete?key=local-test',
                                  {'idToken': self.token})
            self.assertEqual(status, 200, result)

    def ref(self, path):
        """Agrega ruta a referencias Firestore y la registra futura limpieza al finalizar el test."""
        ref = self.db.document(path)
        self.refs.append(ref)
        return ref

    def request(self, method, path, body=None, token=True):
        """
        Envía request HTTP
        token=True usa el token del test, 'invalid' uno inválido y False omite el header.
        """
        headers = {'Authorization': 'Bearer ' + self.token} if token is True else (
            {'Authorization': 'Bearer invalid-token'} if token == 'invalid' else {})
        return http(method, API + path, body, headers)

    def success(self, method, path, body=None):
        """Envía request, verificando HTTP 200 y éxito. Retorna campo resp de la rta de la API."""
        status, result = self.request(method, path, body)
        self.assertEqual(status, 200, result)
        self.assertEqual(result['op_status'], 0)
        self.assertEqual(result['brief'], 'Operation completed successfully')
        return result.get('resp')

    def assert_timestamp(self, value):
        """Recibe un valor de Firestore; verifica datetime posterior a Unix."""
        self.assertIsInstance(value, datetime)
        self.assertGreater(value.timestamp(), 0)

    def crud(self, collection, nested):
        """Recibe colección y campo anidado; comprueba el ciclo CRUD. Retorna None.
        Se usa con users/homes/devices; prueba eliminación solo para homes y devices.
        Luego en test_users/homes/devices.py agregan otros tests específicos
        """
        # Paso 1: Preparo la ruta y registro el documento para su limpieza.
        path = f'/{collection}/{self.key}'
        ref = self.ref(f'{collection}/{self.key}')

        # Paso 2: Distingo la consulta de un documento inexistente de uno vacío.
        self.assertIsNone(self.success('GET', path))
        ref.set({})
        self.assertEqual(self.success('GET', path), {'id': self.key})

        # Paso 3: Creo con ID explícito y verifico campos y timestamps en Firestore.
        data = {'name': 'Original', 'id': 'embedded', nested: {'one': {'role': 'admin'}, 'two': {'role': 'observer'}},
                'created_at': 1, 'updated_at': 2, 'extra': [True, None]}
        result = self.success('POST', '/' + collection, {'data': data, collection[:-1] + '_id': self.key})
        self.assertEqual(result, {'user_id': self.key} if collection == 'users' else self.key)
        stored = ref.get().to_dict()
        self.assertEqual(stored['id'], 'embedded')
        self.assertEqual(stored['extra'], data['extra'])
        self.assert_timestamp(stored['created_at'])
        created_at = stored['created_at']
        self.assert_timestamp(stored['updated_at'])

        # Paso 4: Actualizo un nulo y una ruta anidada; verifico campos conservados y updated_at.
        self.success('PATCH', path, {'name': None, nested + '.one.role': 'pending', 'updated_at': 0})
        stored = ref.get().to_dict()
        self.assertIsNone(stored['name'])
        self.assertEqual(stored[nested]['one']['role'], 'pending')
        self.assertEqual(stored[nested]['two']['role'], 'observer')
        self.assertEqual(stored['created_at'], created_at)
        self.assertGreaterEqual(stored['updated_at'], created_at)

        # Paso 5: Reemplazo el mapa anidado y envío created_at en milisegundos.
        self.success('PATCH', path, {'created_at': 123, nested: {}})
        self.assertEqual(ref.get().to_dict()[nested], {})
        self.assertEqual(int(ref.get().to_dict()['created_at'].timestamp() * 1000), 123)

        # Paso 6: Compruebo que una actualización con body vacío sea aceptada.
        self.success('PATCH', path, {})

        # Paso 7: Reemplazo el documento con datos vacíos; deben quedar solo las fechas.
        self.success('POST', '/' + collection, {'data': {}, collection[:-1] + '_id': self.key})
        self.assertEqual(set(ref.get().to_dict()), {'created_at', 'updated_at'})

        # Paso 8: Creo sin ID y verifico el documento con el ID generado.
        generated = self.success('POST', '/' + collection, {'data': {'name': 'Generated'}})
        generated = generated['user_id'] if collection == 'users' else generated
        self.assertTrue(generated)
        self.assertEqual(self.ref(f'{collection}/{generated}').get().to_dict()['name'], 'Generated')

        # Paso 9: Consulto por API y verifico updated_at como entero en milisegundos.
        wire = self.success('GET', path)
        self.assertIs(type(wire['updated_at']), int)

        # Paso 10: Intento actualizar un documento inexistente y verifico que no se cree.
        missing = self.key + '-missing'
        print('Caso esperado: actualizar un documento inexistente provoca Firestore NotFound (HTTP 500).', flush=True)
        self.assertEqual(self.request('PATCH', f'/{collection}/{missing}', {})[0], 500)
        self.assertFalse(self.ref(f'{collection}/{missing}').get().exists)

        # Paso 11: Para homes y devices, elimino el documento conservando su subcolección.
        if collection != 'users':
            child = self.ref(f'{collection}/{self.key}/children/kept')
            child.set({'keep': True})
            self.success('DELETE', path)
            self.assertFalse(ref.get().exists)
            self.assertTrue(child.get().exists)
            # Paso 12: Repito la eliminación para comprobar que también sea exitosa.
            self.success('DELETE', path)

    def rejected(self, method, path, body, status=422, token=True):
        """Envía una petición y comprueba el status esperado y los documentos vigilados.

        Recibe método, ruta, body, status y opción de token; devuelve el contenido recibido.
        """
        ref = self.ref('devices/' + self.key)
        ref.set({'sentinel': True})
        # Compara estos documentos antes y después de la petición rechazada.
        watched = [self.ref(collection + '/' + self.key)
                   for collection in ('users', 'homes', 'alarms')]
        before = [document.get().to_dict() for document in watched]
        code, result = self.request(method, path, body, token=token)
        self.assertEqual(code, status, result)
        self.assertEqual(ref.get().to_dict(), {'sentinel': True})
        self.assertEqual([document.get().to_dict() for document in watched], before)
        return result
