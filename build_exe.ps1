Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $projectRoot

$venvPython = Join-Path $projectRoot '.venv\Scripts\python.exe'
if (-not (Test-Path $venvPython)) {
    throw "Missing virtual environment at $venvPython. Create it first using py -3.14 -m venv .venv"
}

& $venvPython -m pip install --only-binary=:all: -r requirements-build.txt
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

& $venvPython -m PyInstaller --noconfirm --clean --onefile --windowed --name Pong main.py
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host "Build complete: $projectRoot\dist\Pong.exe"
