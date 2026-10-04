# Instalación del entorno de desarrollo en Windows

[installation_for_devs.ps1](../../scripts/installation_for_devs.ps1) instala las herramientas y prepara el entorno Python del repositorio. Requiere Windows, PowerShell 5.1 o posterior, conexión a Internet y permisos de administrador.

## Cómo ejecutarlo

Después de clonar el repositorio, abrir PowerShell **como administrador desde la misma cuenta que se usará para desarrollar**, ubicarse en la raíz de `grandsafelife-server` y ejecutar:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\installation_for_devs.ps1
```

`-ExecutionPolicy Bypass` se aplica únicamente al proceso que ejecuta el script; no cambia permanentemente la política de PowerShell. La instalación acepta los acuerdos de los paquetes indicados. Si una operación falla, el script se detiene y muestra el error; una vez resuelto, se puede volver a ejecutar.

## Herramientas que instala

| Herramienta | Comportamiento |
| --- | --- |
| WinGet | Si falta, instala el proveedor NuGet y el módulo `Microsoft.WinGet.Client` desde PowerShell Gallery, y prepara WinGet con `Repair-WinGetPackageManager -AllUsers`. |
| Git | Instala `Git.Git` si no encuentra `git.exe`. |
| Python 3.13 | Busca esa versión y, si falta, instala `Python.Python.3.13`. Conserva otras versiones de Python. |
| Node.js y npm | Reutiliza Node.js 22 o 24 con npm disponible; en otro caso solicita `OpenJS.NodeJS.LTS` mediante WinGet. |
| Java | Reutiliza Java 21 o 25; en otro caso instala `Microsoft.OpenJDK.21`, necesario para el emulador de Firestore. |
| Visual Studio Code | Instala `Microsoft.VisualStudioCode` si no encuentra `code.cmd`. |
| Extensiones de VS Code | Instala Python (`ms-python.python`) y Pylance (`ms-python.vscode-pylance`), junto con las dependencias que resuelva VS Code. |
| Firebase CLI | Si falta `firebase.cmd`, instala `firebase-tools` mediante npm global y agrega el directorio global de npm al PATH del usuario si es necesario. |

Las instalaciones mediante WinGet usan `--no-upgrade`. Las versiones de parche de las herramientas dependen de lo disponible al ejecutar el script; no se fija una versión exacta de todo el entorno.

## Entorno virtual y dependencias

El script comprueba los submódulos y ejecuta `git submodule update --init --recursive` si detecta alguno sin inicializar. El acceso a sus repositorios debe estar disponible para la cuenta del desarrollador.

Prepara `venv` en la raíz con **Python 3.13**. Reutiliza un entorno compatible con la ruta actual; si es incompatible o conserva una ruta anterior, lo mueve a `.local-venv-backups/<identificador>` antes de crear uno nuevo. Tanto `venv` como los respaldos quedan excluidos de Git por las reglas actuales del repositorio.

Dentro de `venv`:

1. Actualiza `pip`.
2. Instala [backend/tests/requirements.txt](../../backend/tests/requirements.txt), que incluye las dependencias de [requirements.txt](../../requirements.txt) y HTTPX para las pruebas.
3. Ejecuta `pip check`, comprueba los imports de Flask, Pydantic, Firebase Functions y HTTPX, y ejecuta `python -m backend.tests.test_http_contract`.

Las pruebas se ejecutan en proceso local. Si está definida `CONTRACT_BASE_URL`, el script solicita quitarla antes de probar para evitar usar un servidor externo.

No instala Docker ni las dependencias de inferencia del submódulo del modelo. Tampoco inicia emuladores, configura credenciales, inicia sesión en Firebase, despliega recursos ni realiza commits o pushes.

## Opciones

Agregar al comando una de estas opciones cuando corresponda:

- `-ToolsOnly`: instala y verifica las herramientas; omite submódulos, `venv`, dependencias Python y pruebas.
- `-SkipTests`: prepara el entorno y valida dependencias e imports, pero omite las pruebas de contrato.

## Después de instalar

Abrir una terminal nueva para recoger los cambios del PATH. En VS Code, seleccionar `venv\Scripts\python.exe` como intérprete del proyecto.

Desde la raíz se puede activar el entorno con:

```powershell
.\venv\Scripts\Activate.ps1
```

También se puede usar su intérprete directamente, sin activar el entorno:

```powershell
.\venv\Scripts\python.exe -m backend.tests.test_http_contract
```

Cuando se necesite acceder a una cuenta de Firebase, ejecutar manualmente `firebase login`.
