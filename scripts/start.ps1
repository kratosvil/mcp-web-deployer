$ErrorActionPreference = "Stop"

Write-Host "MCP Web Deployer - Start" -ForegroundColor Cyan
Write-Host "============================"
Write-Host ""

if (-not (Test-Path "venv\Scripts\Activate.ps1")) {
    Write-Host "Entorno virtual no encontrado" -ForegroundColor Red
    Write-Host "Ejecuta primero: .\scripts\setup.ps1" -ForegroundColor Yellow
    exit 1
}

Write-Host "Activando entorno virtual..." -ForegroundColor Yellow
& ".\venv\Scripts\Activate.ps1"
Write-Host "Entorno activado"
Write-Host ""

Write-Host "Verificando Docker..." -ForegroundColor Yellow
try {
    docker info | Out-Null
    Write-Host "Docker está corriendo"
    Write-Host ""
} catch {
    Write-Host "Docker no está corriendo" -ForegroundColor Red
    exit 1
}

Write-Host "Información del Proyecto" -ForegroundColor Cyan
Write-Host "=========================="
Write-Host ""

$projectDir = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Write-Host "Directorio del proyecto:" -ForegroundColor Yellow
Write-Host $projectDir
Write-Host ""

Write-Host "Directorio www:" -ForegroundColor Yellow
Write-Host (Join-Path $projectDir "www")
Write-Host ""

Write-Host "Herramientas MCP disponibles:" -ForegroundColor Yellow
Write-Host "create_html"
Write-Host "deploy_server"
Write-Host "stop_server"
Write-Host "server_status"
Write-Host "list_html_files"
Write-Host ""

Write-Host "Instrucciones:" -ForegroundColor Cyan
Write-Host "1. Abre Claude Desktop"
Write-Host "2. Pide a Claude que use las herramientas MCP"
Write-Host "3. Ejemplo: Crea un index.html y despliega el servidor"
Write-Host ""

Write-Host "Entorno listo para desarrollo!" -ForegroundColor Green
Write-Host ""
Write-Host "Presiona Ctrl+C para salir"
Write-Host ""

while ($true) {
    Start-Sleep -Seconds 3600
}
