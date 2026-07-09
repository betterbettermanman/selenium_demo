# Dev mode: backend(6002) + frontend vite(5173)
$ErrorActionPreference = 'Stop'

$Root = Split-Path -Parent $PSScriptRoot
$Backend = Join-Path $Root 'backend'
$Frontend = Join-Path $Root 'frontend'
$Port = if ($env:PORT) { $env:PORT } else { '6002' }

Write-Host '========================================'
Write-Host ' Task Manager - Dev Mode'
Write-Host '========================================'

$backendCmd = "Set-Location '$Backend'; `$env:PORT='$Port'; `$env:FLASK_DEBUG='1'; python app.py"
$frontendCmd = "Set-Location '$Frontend'; if (-not (Test-Path node_modules)) { npm install }; npm run dev"

Start-Process powershell -ArgumentList '-NoExit', '-Command', $backendCmd
Start-Sleep -Seconds 2
Start-Process powershell -ArgumentList '-NoExit', '-Command', $frontendCmd

Write-Host ''
Write-Host "Backend : http://localhost:$Port" -ForegroundColor Green
Write-Host 'Frontend: http://localhost:5173' -ForegroundColor Green
Write-Host 'Started in two new windows. Close window to stop.'
