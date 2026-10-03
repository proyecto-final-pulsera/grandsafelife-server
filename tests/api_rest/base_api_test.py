"""Base común: blueprint real, process real y registro de llamadas."""
import unittest
# Flask procesa los requests localmente; no hace falta levantar un servidor.
from flask import Flask
# Excepción del servidor para requests cuyo formato no cumple las reglas.
from backend.http_api_rest.http_validation import RequestValidationError

#==============================
# Registro de llamadas a process
#==============================
class RecordingProcessor:
    def __init__(self, process):
        # Guarda el process real y comienza con un registro de llamadas vacío.
        self.process = process
        self.calls = []

    # Funcion que intercepta llamadas a cualquier método del process y las registra en self.calls
    # Ejemplo: self.http_processor.process_get_user_by_id("user_001")
    # Como este objeto no define ese método, Python llama a __getattr__("process_get_user_by_id").
    # target = self.process.process_get_user_by_id
    def __getattr__(self, name):
        # Busca el método en el process real, sin ejecutarlo todavía.
        target = getattr(self.process, name)

        def call(*args, **kwargs):
            # args: argumentos por posición; kwargs: argumentos por nombre.
            # Registra llamada con sus argumentos 
            self.calls.append({"method": name, "args": list(args), "kwargs": kwargs})
            # Ejecuta la acción real con los mismos argumentos y devuelve su resultado.
            return target(*args, **kwargs)

        # Entrega al endpoint la función que registra y luego ejecuta la llamada.
        return call

#=============================
# Base de tests de API REST
#=============================
class BaseApiTest(unittest.TestCase):
    # Cada conjunto define estas clases; por ejemplo, UsersEndpoints y UsersProcesses.
    # unittest.TestCase aporta las comprobaciones assertEqual, assertTrue, etc.
    endpoints_class = None
    process_class = None

    def setUp(self):
        # unittest ejecuta setUp antes de CADA test: no se comparten llamadas entre tests.
        # Instancia el process del conjunto y lo envuelve con el registro de llamadas.
        self.processor = RecordingProcessor(self.process_class())
        # Crea Flask sin rutas de archivos estáticos y activa el modo de pruebas.
        self.app = Flask(__name__, static_folder=None)
        self.app.config["TESTING"] = True
        # Instancia los endpoints con el procesador y registra solo su blueprint.
        # No carga App ni el registro general de rutas del servidor.
        self.app.register_blueprint(self.endpoints_class(self.processor).blueprint)

        # Reproduce la respuesta 422 del servidor ante errores de validación.
        # Este entorno no comprueba los demás manejadores del registro general HTTP.
        @self.app.errorhandler(RequestValidationError)
        def validation_error(error):
            return {"detail": error.errors}, 422

        # Permite client.get/post/patch/etc. dentro del proceso, sin conexión de red.
        self.client = self.app.test_client()
        # Prueba presencia del header; no verifica tokens ni permisos reales.
        self.headers = {"Authorization": "Bearer test-token"}

    def assert_success(self, response):
        # Comprueba el éxito común; cada test verifica por separado el contenido de resp.
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["op_status"], 0)
        self.assertEqual(response.json["brief"], "Operation completed successfully")

    def assert_last_call(self, method, *args):
        # [-1] selecciona la última llamada. Comprueba método y argumentos exactos,
        # sin token adicional y sin argumentos por nombre (kwargs vacío).
        self.assertEqual(self.processor.calls[-1], {
            "method": method, "args": list(args), "kwargs": {},
        })

    def assert_rejected(self, response):
        # Comprueba HTTP 422, errores presentes y ninguna llamada al process.
        # Usar en tests con solo requests rechazados: revisa TODA la lista de llamadas.
        self.assertEqual(response.status_code, 422)
        self.assertTrue(response.json["detail"])
        self.assertEqual(self.processor.calls, [])
