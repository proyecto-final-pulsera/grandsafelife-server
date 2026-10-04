#Requires -Version 5.1
<#
.SYNOPSIS
Ejecuta los tests HTTP contra Firebase Emulator Suite local.
.EXAMPLE
.\tests\run.ps1
.EXAMPLE
.\tests\run.ps1 -Group users
.EXAMPLE
.\tests\run.ps1 -ExistingEmulators
#>
[CmdletBinding()]
param(
    [ValidateSet('users', 'homes', 'devices', 'devices_stats', 'alarm')]
    [string]$Group,
    [switch]$ExistingEmulators
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$testRepoRoot = Split-Path -Parent $PSScriptRoot
$testPython = Join-Path $testRepoRoot 'venv\Scripts\python.exe'
if (-not (Test-Path -LiteralPath $testPython)) {
    throw 'Falta venv\Scripts\python.exe. Preparar el entorno siguiendo tests/README.md.'
}
$testArguments = @('tests/api_rest/run_tests.py')
if ($Group) { $testArguments += $Group }
$testExitCode = 1
Push-Location $testRepoRoot
try {
    if ($ExistingEmulators) {
        & $testPython @testArguments
    } else {
        $testFirebase = Get-Command firebase.cmd -ErrorAction SilentlyContinue
        if (-not $testFirebase) { throw 'Falta Firebase CLI (firebase.cmd) en PATH.' }
        if (-not (Get-Command java.exe -ErrorAction SilentlyContinue)) {
            throw 'Falta Java en PATH. Instalar Java 21 para el emulador de Firestore.'
        }
        # La ruta relativa evita problemas con espacios en el nombre del repositorio.
        $testCommand = '.\venv\Scripts\python.exe tests/api_rest/run_tests.py'
        if ($Group) { $testCommand += ' ' + $Group }
        & $testFirebase.Source emulators:exec --project demo-grandsafelife --only auth,firestore,functions $testCommand
    }
    $testExitCode = $LASTEXITCODE
} finally {
    Pop-Location
}
exit $testExitCode
