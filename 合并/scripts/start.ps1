# Start production server (run build.ps1 first)
$ErrorActionPreference = 'Stop'

$Root = Split-Path -Parent $PSScriptRoot
$Backend = Join-Path $Root 'backend'
$StaticDir = Join-Path $Backend 'static'
$EnvFile = Join-Path $Backend '.env'
$Port = if ($env:PORT) { $env:PORT } else { '6001' }

Write-Host '========================================'
Write-Host ' Task Manager - Start'
Write-Host '========================================'

if (-not (Test-Path $StaticDir)) {
    Write-Host 'backend/static not found. Please run build.bat first.' -ForegroundColor Red
    exit 1
}

if (-not (Test-Path $EnvFile)) {
    Write-Host 'backend/.env not found, copy from .env.example ...' -ForegroundColor Yellow
    Copy-Item (Join-Path $Backend '.env.example') $EnvFile
    Write-Host 'Please edit backend/.env and restart.' -ForegroundColor Yellow
}

if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    throw 'python not found'
}

Push-Location $Backend
try {
    Write-Host 'pip install -r requirements.txt ...'
    python -m pip install -r requirements.txt -q

    $env:PORT = $Port
    $env:FLASK_DEBUG = '0'

    Write-Host ''
    Write-Host "URL: http://localhost:$Port" -ForegroundColor Green
    Write-Host 'Press Ctrl+C to stop'
    Write-Host ''

    python app.py
} finally {
    Pop-Location
}
