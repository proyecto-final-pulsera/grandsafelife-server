"""Ejecuta la suite HTTP contra Auth, Firestore y Functions locales."""
import argparse
import os
from pathlib import Path
import sys
import unittest

GROUPS = {'users': 'test_users', 'homes': 'test_homes', 'devices': 'test_devices',
          'devices_stats': 'test_device_stats', 'alarm': 'test_alarms'}
GROUP_TITLES = {'test_users': 'Users', 'test_homes': 'Homes', 'test_devices': 'Devices',
                'test_device_stats': 'Device Stats', 'test_alarms': 'Alarms'}


#===========================================
# Clase para imprimir resultados de tests
#===========================================
class ReadableTestResult(unittest.TextTestResult):
    """Toma los resultados de las pruebas y los imprime."""

    def __init__(self, stream, descriptions, verbosity):
        super().__init__(stream, descriptions, verbosity)
        self.current_group = None
        self.group_number = 0

    def write_line(self, text=''):
        self.stream.writeln(text)
        self.stream.flush()

    def startTest(self, test):
        super().startTest(test)
        module = test.__class__.__module__
        if module != self.current_group:
            self.current_group = module
            self.group_number = 0
            self.write_line()
            self.write_line('=' * 27)
            self.write_line('Tests - ' + GROUP_TITLES.get(module, module))
            self.write_line('=' * 27)
        self.group_number += 1
        self.write_line('-' * 46)
        self.write_line(f'Test {self.group_number}')
        self.write_line(test.shortDescription() or test.id())
        self.before_counts = (len(self.failures), len(self.errors), len(self.skipped),
                              len(self.expectedFailures), len(self.unexpectedSuccesses))

    def stopTest(self, test):
        # Se imprime después del cleanup, incluyendo fallos de subtests.
        counts = (len(self.failures), len(self.errors), len(self.skipped),
                  len(self.expectedFailures), len(self.unexpectedSuccesses))
        labels = ('FALLO', 'ERROR', 'OMITIDO', 'FALLO ESPERADO', 'ÉXITO INESPERADO')
        changes = [label for label, before, after in zip(labels, self.before_counts, counts)
                   if after > before]
        self.write_line('Resultado: ' + (', '.join(changes) if changes else 'OK'))
        super().stopTest(test)


#===========================================
# Orquestador de tests
#===========================================
def main():
    # Leo el grupo de tests a ejecutar desde los argumentos de línea de comando.
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('group', nargs='?', choices=GROUPS)
    args = parser.parse_args()

    # Se configuran las variables de entorno del proceso de tests.
    for key, value in {
        'GCLOUD_PROJECT': 'demo-grandsafelife',
        'GOOGLE_CLOUD_PROJECT': 'demo-grandsafelife',
        'FIRESTORE_EMULATOR_HOST': '127.0.0.1:8080',
        'FIREBASE_AUTH_EMULATOR_HOST': '127.0.0.1:9099',
    }.items():
        # Se rechazan configuraciones incompatibles
        if os.environ.get(key) not in (None, value):
            parser.error(f'{key} apunta a otro destino; se esperaba {value}.')
        os.environ[key] = value

    # Agrego la carpeta de este archivo a las rutas donde Python busca módulos.
    # Esto permite importar base_api_test y los módulos test_users, test_homes, etc.
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from base_api_test import require_emulators

    # Verifico que los emuladores necesarios estén activos en los puertos esperados.
    try:
        require_emulators()
    except Exception as error:
        parser.error(f'No se puede ejecutar de forma aislada: {error}')

    # Se arma la suite con todos los tests correspondientes al grupo solicitado, o todos si no se especifica.
    suite = unittest.TestSuite()
    for group in ([args.group] if args.group else GROUPS):
        suite.addTests(unittest.defaultTestLoader.loadTestsFromName(GROUPS[group]))

    # Se ejecuta la suite y se imprime el resultado
    result = unittest.TextTestRunner(
        stream=sys.stdout,
        verbosity=0,
        resultclass=ReadableTestResult,
    ).run(suite)

    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    sys.exit(main())
