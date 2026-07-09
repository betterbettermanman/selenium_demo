# Build frontend and copy to backend/static
$ErrorActionPreference = 'Stop'

$Root = Split-Path -Parent $PSScriptRoot
$Frontend = Join-Path $Root 'frontend'
$Backend = Join-Path $Root 'backend'
$StaticDir = Join-Path $Backend 'static'
$DistDir = Join-Path $Frontend 'dist'

Write-Host '========================================'
Write-Host ' Task Manager - Build'
Write-Host '========================================'

function Test-Command($Name) {
    if (-not (Get-Command $Name -ErrorAction SilentlyContinue)) {
        throw "Command not found: $Name"
    }
}

Test-Command node
Test-Command npm

Push-Location $Frontend
try {
    if (-not (Test-Path 'node_modules')) {
        Write-Host '[1/3] npm install...'
        npm install
    } else {
        Write-Host '[1/3] skip npm install (node_modules exists)'
    }

    Write-Host '[2/3] npm run build...'
    npm run build
    if (-not (Test-Path $DistDir)) {
        throw 'Build failed: frontend/dist not found'
    }
} finally {
    Pop-Location
}

Write-Host '[3/3] copy to backend/static ...'
if (Test-Path $StaticDir) {
    Remove-Item $StaticDir -Recurse -Force
}
Copy-Item $DistDir $StaticDir -Recurse

Write-Host ''
Write-Host 'Build done.' -ForegroundColor Green
Write-Host "Static files: $StaticDir"
Write-Host 'Next: run start.bat' -ForegroundColor Green
