$ErrorActionPreference = "Stop"

Write-Host "MCP Web Deployer - Setup" -ForegroundColor Cyan
Write-Host "================================"
Write-Host ""

Write-Host "Verificando Python..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "$pythonVersion encontrado" -ForegroundColor Green
} catch {
    Write-Host "Python no encontrado." -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Verificando Docker..." -ForegroundColor Yellow
try {
    $dockerVersion = docker --version
    Write-Host "$dockerVersion encontrado" -ForegroundColor Green
} catch {
    Write-Host "Docker no encontrado." -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Creando entorno virtual..." -ForegroundColor Yellow
if (Test-Path "venv") {
    Remove-Item -Recurse -Force venv
}

python -m venv venv
Write-Host "Entorno virtual creado" -ForegroundColor Green

Write-Host ""
Write-Host "Activando entorno virtual..." -ForegroundColor Yellow
& ".\venv\Scripts\Activate.ps1"

Write-Host ""
Write-Host "Instalando dependencias..." -ForegroundColor Yellow
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
Write-Host "Dependencias instaladas" -ForegroundColor Green

Write-Host ""
Write-Host "Configurando directorios..." -ForegroundColor Yellow
if (-not (Test-Path "www")) {
    New-Item -ItemType Directory -Path "www" | Out-Null
}
if (-not (Test-Path "www\.gitkeep")) {
    New-Item -ItemType File -Path "www\.gitkeep" | Out-Null
}

Write-Host "Directorios configurados" -ForegroundColor Green

Write-Host ""
Write-Host "Configuracion de Claude Desktop" -ForegroundColor Cyan
Write-Host "--------------------------------"
Write-Host ""

$projectDir = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$pythonPath = Join-Path $projectDir "venv\Scripts\python.exe"
$serverPath = Join-Path $projectDir "src\server.py"

$config = @{
    mcpServers = @{
        "web-deployer" = @{
            command = $pythonPath
            args    = @($serverPath)
        }
    }
}

$configExample = $config | ConvertTo-Json -Depth 5

Write-Host "Agrega esta configuracion a:" -ForegroundColor Yellow
Write-Host "$env:APPDATA\Claude\claude_desktop_config.json"
Write-Host ""

Write-Host $configExample

Write-Host ""
Write-Host "Setup completado!" -ForegroundColor Green
Write-Host ""
Write-Host "Proximos pasos:" -ForegroundColor Cyan
Write-Host "1. Configura Claude Desktop con la configuracion de arriba"
Write-Host "2. Reinicia Claude Desktop"
Write-Host "3. Ejecuta: .\scripts\start.ps1"
