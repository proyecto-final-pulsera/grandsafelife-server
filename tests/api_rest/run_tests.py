"""Ejecuta todos los conjuntos implementados o uno elegido."""
import argparse
from pathlib import Path
import sys
import unittest

#================================
# Grupos de tests
#================================
TESTS_GROUPS = {
    "users": "test_users",
    "homes": "test_homes",
    "devices": "test_devices",
    "devices_stats": "test_devices_stats",
    "alarm": "test_alarms",
    }


def main():
    groups = TESTS_GROUPS

    #python tests/api_rest/run_tests.py --help
    parser = argparse.ArgumentParser(description=__doc__)

    # Para que tome los grupos definidos en TESTS_GROUPS
    parser.add_argument("group", nargs="?", choices=list(groups))
    
    # Recupero argumento (grupo de tests)
    args = parser.parse_args()

    # Obtengo directorio del script particular (o todos)
    directory = Path(__file__).resolve().parent
    sys.path.insert(0, str(directory.parents[1]))
    sys.path.insert(0, str(directory))
    if args.group:
        selected = [args.group]
    else:
        selected = list(groups)

    # Reconozco funciones test_* y creo suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    for group in selected:
        module_name = groups[group]
        group_tests = loader.loadTestsFromName(module_name)
        suite.addTests(group_tests)        
    if suite.countTestCases() == 0:
        parser.error("No se encontraron pruebas")

    # Ejecuto suite    
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    sys.exit(main())
