#Requires -Version 5.1
#Requires -RunAsAdministrator
<#
.SYNOPSIS
Prepara Windows para desarrollar Grand Safe Life Server.
.DESCRIPTION
Ejecutar como administrador desde la cuenta que se usara para desarrollar.
Instala herramientas faltantes mediante WinGet y prepara .venv con Python 3.13.
Requiere Internet y acepta los acuerdos de los paquetes indicados.
No despliega, inicia sesion en Firebase, modifica contratos ni hace commit/push.
Los entornos virtuales incompatibles se conservan en una carpeta de respaldo.
.EXAMPLE
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\doc\scripts\installation_for_devs.ps1
.EXAMPLE
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\doc\scripts\installation_for_devs.ps1 -ToolsOnly
.LINK
https://learn.microsoft.com/windows/package-manager/winget/
.LINK
https://firebase.google.com/docs/cli
#>
[CmdletBinding()]
param(
    [switch]$ToolsOnly,
    [switch]$SkipTests
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$repoRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)

function Invoke-Checked {
    param([string]$Executable, [string[]]$Arguments)
    & $Executable @Arguments | Out-Host
    if ($LASTEXITCODE -ne 0) {
        throw "Fallo $Executable (codigo $LASTEXITCODE). Revise la salida anterior y vuelva a ejecutar el script al resolverlo."
    }
}

function Update-SessionPath {
    $env:Path = [Environment]::GetEnvironmentVariable('Path', 'Machine') + ';' +
        [Environment]::GetEnvironmentVariable('Path', 'User')
}

function Install-Package {
    param([string]$Id)
    Write-Host "Preparando $Id..." -ForegroundColor Cyan
    # --no-upgrade conserva las instalaciones ya registradas.
    & winget.exe install --id $Id --exact --source winget --silent --no-upgrade --accept-source-agreements --accept-package-agreements
    $result = $LASTEXITCODE
    # APPINSTALLER_CLI_ERROR_UPDATE_NOT_APPLICABLE: ya instalado sin actualizacion.
    if ($result -ne 0 -and $result -ne -1978335189) {
        throw "WinGet no pudo preparar $Id (codigo $result). Revise el error del instalador antes de continuar."
    }
    Update-SessionPath
}

function Find-Python313 {
    $candidates = @(
        (Join-Path $env:LOCALAPPDATA 'Programs\Python\Python313\python.exe'),
        (Join-Path $env:ProgramFiles 'Python313\python.exe')
    )
    if (Get-Command py.exe -ErrorAction SilentlyContinue) {
        try {
            $detected = & py.exe -3.13 -c 'import sys; print(sys.executable)' 2>$null
            if ($LASTEXITCODE -eq 0) { $candidates = @($detected) + $candidates }
        } catch {
            # El administrador de Python informa por stderr los runtimes ausentes.
        }
    }
    foreach ($candidate in $candidates) {
        if (Test-Path -LiteralPath $candidate) {
            $version = & $candidate -c 'import sys; print(sys.version_info.major, sys.version_info.minor, sep=chr(46))' 2>$null
            if ($LASTEXITCODE -eq 0 -and $version -eq '3.13') { return $candidate }
        }
    }
    return $null
}

Update-SessionPath
if (-not (Get-Command winget.exe -ErrorAction SilentlyContinue)) {
    Write-Host 'Instalando WinGet con el modulo oficial de Microsoft...' -ForegroundColor Cyan
    [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
    Install-PackageProvider -Name NuGet -MinimumVersion 2.8.5.201 -Force | Out-Null
    Install-Module -Name Microsoft.WinGet.Client -Repository PSGallery -Scope AllUsers -Force
    Import-Module Microsoft.WinGet.Client
    Repair-WinGetPackageManager -AllUsers
    Update-SessionPath
    if (-not (Get-Command winget.exe -ErrorAction SilentlyContinue)) {
        throw 'WinGet aun no esta disponible. Reinicie la terminal como administrador y ejecute nuevamente el script.'
    }
}

if (-not (Get-Command git.exe -ErrorAction SilentlyContinue)) { Install-Package 'Git.Git' }
$python = Find-Python313
if (-not $python) {
    Install-Package 'Python.Python.3.13'
    $python = Find-Python313
}
if (-not $python) { throw 'No se encontro Python 3.13 despues de la instalacion.' }

$nodeIsSupported = $false
if (Get-Command node.exe -ErrorAction SilentlyContinue) {
    $nodeMajor = & node.exe -p 'process.versions.node.slice(0,2)'
    $nodeIsSupported = $LASTEXITCODE -eq 0 -and $nodeMajor -in @('22', '24')
}
if (-not $nodeIsSupported -or -not (Get-Command npm.cmd -ErrorAction SilentlyContinue)) {
    Install-Package 'OpenJS.NodeJS.LTS'
}
Invoke-Checked 'node.exe' @('--version')
Invoke-Checked 'npm.cmd' @('--version')

# Java 21 permite ejecutar el emulador de Firestore.
$javaIsSupported = $false
if (Get-Command java.exe -ErrorAction SilentlyContinue) {
    $javaVersion = (& java.exe --version 2>$null | Out-String)
    $javaIsSupported = $LASTEXITCODE -eq 0 -and $javaVersion -match '(?:openjdk|java) (21|25)\.'
}
if (-not $javaIsSupported) { Install-Package 'Microsoft.OpenJDK.21' }
Invoke-Checked 'java.exe' @('--version')

if (-not (Get-Command code.cmd -ErrorAction SilentlyContinue)) {
    Install-Package 'Microsoft.VisualStudioCode'
}
Invoke-Checked 'code.cmd' @('--install-extension', 'ms-python.python')
Invoke-Checked 'code.cmd' @('--install-extension', 'ms-python.vscode-pylance')

if (-not (Get-Command firebase.cmd -ErrorAction SilentlyContinue)) {
    Invoke-Checked 'npm.cmd' @('install', '--global', 'firebase-tools')
}
$npmPrefix = & npm.cmd prefix --global
if ($LASTEXITCODE -ne 0) { throw 'No se pudo determinar el directorio global de npm.' }
$npmPrefix = "$npmPrefix".Trim()
$userPath = [Environment]::GetEnvironmentVariable('Path', 'User')
if (@($userPath -split ';') -notcontains $npmPrefix) {
    [Environment]::SetEnvironmentVariable('Path', ($userPath.TrimEnd(';') + ';' + $npmPrefix), 'User')
}
Update-SessionPath
Invoke-Checked (Join-Path $npmPrefix 'firebase.cmd') @('--version')
Invoke-Checked $python @('--version')
Invoke-Checked 'git.exe' @('--version')

if (-not $ToolsOnly) {
    Push-Location $repoRoot
    try {
        # Inicializa solamente submodulos ausentes; no reemplaza trabajo existente.
        $submodules = & git.exe submodule status --recursive
        if ($LASTEXITCODE -ne 0) { throw 'No se pudieron inspeccionar los submodulos.' }
        if (@($submodules | Where-Object { $_ -match '^-' }).Count -gt 0) {
            Invoke-Checked 'git.exe' @('submodule', 'update', '--init', '--recursive')
        }

        $venv = Join-Path $repoRoot '.venv'
        $venvPython = Join-Path $venv 'Scripts\python.exe'
        $validVenv = $false
        if (Test-Path -LiteralPath $venvPython) {
            try {
                & $venvPython -c 'import sys; assert sys.version_info[:2] == (3, 13)' 2>$null
                $validVenv = $LASTEXITCODE -eq 0
            } catch { $validVenv = $false }
        }
        if ($validVenv) {
            # Un venv copiado puede ejecutar Python pero conservar rutas de otra PC.
            $activation = Join-Path $venv 'Scripts\activate.bat'
            $validVenv = (Test-Path -LiteralPath $activation) -and
                (Get-Content -LiteralPath $activation -Raw).Contains("VIRTUAL_ENV=$venv")
        }
        if (-not $validVenv) {
            if (Test-Path -LiteralPath $venv) {
                # Ambos destinos son hijos directos del repositorio calculado arriba.
                $backupRoot = Join-Path $repoRoot '.local-venv-backups'
                New-Item -ItemType Directory -Path $backupRoot -Force | Out-Null
                $backup = Join-Path $backupRoot ([guid]::NewGuid().ToString())
                Move-Item -LiteralPath $venv -Destination $backup
                Write-Host "Entorno anterior conservado en $backup"
            }
            Invoke-Checked $python @('-m', 'venv', $venv)
        }
        Invoke-Checked $venvPython @('-m', 'pip', 'install', '--upgrade', 'pip')
        Invoke-Checked $venvPython @('-m', 'pip', 'install', '-r', 'backend/requirements.txt', '-r', 'backend/tests/requirements.txt', 'Flask>=3.1,<4', 'firebase-functions')
        Invoke-Checked $venvPython @('-m', 'pip', 'check')
        Invoke-Checked $venvPython @('-c', 'import flask, pydantic, firebase_functions, fastapi, httpx')
        if (-not $SkipTests) {
            if ($env:CONTRACT_BASE_URL) { throw 'Quite CONTRACT_BASE_URL para ejecutar las pruebas exclusivamente en proceso local.' }
            Invoke-Checked $venvPython @('-m', 'backend.tests.test_http_contract')
        }
    } finally { Pop-Location }
}

Write-Host 'Preparacion completada. Abra una terminal nueva y seleccione .venv\Scripts\python.exe en VS Code.' -ForegroundColor Green
Write-Host 'Para autenticar Firebase cuando lo necesite: firebase login'
