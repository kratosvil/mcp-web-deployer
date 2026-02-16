# 📦 Guía de Instalación - MCP Web Deployer

Esta guía proporciona instrucciones detalladas para instalar y configurar MCP Web Deployer en diferentes sistemas operativos.

---

## 📋 Tabla de Contenidos

1. [Pre-requisitos](#pre-requisitos)
2. [Instalación en Windows](#instalación-en-windows)
3. [Instalación en Linux](#instalación-en-linux)
4. [Instalación en macOS](#instalación-en-macos)
5. [Configuración de Claude Desktop](#configuración-de-claude-desktop)
6. [Verificación](#verificación)
7. [Troubleshooting](#troubleshooting)

---

## Pre-requisitos

### Software Requerido

| Software | Versión Mínima | Descarga |
|----------|----------------|----------|
| Python | 3.8+ | [python.org](https://www.python.org/downloads/) |
| Docker Desktop | 20.10+ | [docker.com](https://www.docker.com/products/docker-desktop) |
| Claude Desktop | Última | [claude.ai](https://claude.ai/download) |
| Git | 2.0+ | [git-scm.com](https://git-scm.com/downloads) |

### Verificar Instalaciones
```bash
# Verificar Python
python --version

# Verificar Docker
docker --version

# Verificar Git
git --version
```

---

## Instalación en Windows

### Paso 1: Preparar el Entorno
```powershell
# Crear directorio base
New-Item -Path "C:\MCP\MCP-Despliegues" -ItemType Directory -Force

# Navegar al directorio
Set-Location "C:\MCP\MCP-Despliegues"
```

### Paso 2: Clonar el Repositorio
```powershell
# Clonar desde GitHub
git clone https://github.com/TU_USUARIO/mcp-web-deployer.git

# Entrar al directorio
cd mcp-web-deployer
```

### Paso 3: Ejecutar Script de Setup
```powershell
# Ejecutar setup automático
.\scripts\setup.ps1
```

El script realizará:
- ✅ Verificación de Python y Docker
- ✅ Creación del entorno virtual
- ✅ Instalación de dependencias
- ✅ Configuración de directorios
- ✅ Generación de configuración para Claude

### Paso 4: Configurar Política de Ejecución (si es necesario)

Si obtienes un error de política de ejecución:
```powershell
# Permitir scripts locales
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

---

## Instalación en Linux

### Paso 1: Preparar el Entorno
```bash
# Crear directorio base
mkdir -p ~/MCP/MCP-Despliegues

# Navegar al directorio
cd ~/MCP/MCP-Despliegues
```

### Paso 2: Clonar el Repositorio
```bash
# Clonar desde GitHub
git clone https://github.com/TU_USUARIO/mcp-web-deployer.git

# Entrar al directorio
cd mcp-web-deployer
```

### Paso 3: Crear Entorno Virtual
```bash
# Crear entorno virtual
python3 -m venv venv

# Activar entorno virtual
source venv/bin/activate
```

### Paso 4: Instalar Dependencias
```bash
# Actualizar pip
pip install --upgrade pip

# Instalar dependencias
pip install -r requirements.txt
```

### Paso 5: Verificar Instalación de Docker
```bash
# Verificar Docker
docker info

# Si no está instalado:
# Ubuntu/Debian:
sudo apt-get update
sudo apt-get install docker.io

# Agregar usuario al grupo docker
sudo usermod -aG docker $USER

# Reiniciar sesión para aplicar cambios
```

---

## Instalación en macOS

### Paso 1: Preparar el Entorno
```bash
# Crear directorio base
mkdir -p ~/MCP/MCP-Despliegues

# Navegar al directorio
cd ~/MCP/MCP-Despliegues
```

### Paso 2: Clonar el Repositorio
```bash
# Clonar desde GitHub
git clone https://github.com/TU_USUARIO/mcp-web-deployer.git

# Entrar al directorio
cd mcp-web-deployer
```

### Paso 3: Crear Entorno Virtual
```bash
# Crear entorno virtual
python3 -m venv venv

# Activar entorno virtual
source venv/bin/activate
```

### Paso 4: Instalar Dependencias
```bash
# Actualizar pip
pip install --upgrade pip

# Instalar dependencias
pip install -r requirements.txt
```

### Paso 5: Instalar Docker Desktop

Si no tienes Docker:

1. Descarga Docker Desktop desde [docker.com](https://www.docker.com/products/docker-desktop)
2. Instala la aplicación
3. Inicia Docker Desktop
4. Verifica: `docker info`

---

## Configuración de Claude Desktop

### Windows

1. **Localizar el archivo de configuración**:
```
   %APPDATA%\Claude\claude_desktop_config.json
```

2. **Abrir en el Explorador**:
   - Presiona `Win + R`
   - Escribe: `%APPDATA%\Claude`
   - Abre o crea `claude_desktop_config.json`

3. **Agregar la configuración**:
```json
   {
     "mcpServers": {
       "web-deployer": {
         "command": "C:\\MCP\\MCP-Despliegues\\mcp-web-deployer\\venv\\Scripts\\python.exe",
         "args": [
           "C:\\MCP\\MCP-Despliegues\\mcp-web-deployer\\src\\server.py"
         ]
       }
     }
   }
```

   > ⚠️ **Importante**: 
   > - Usa rutas absolutas
   > - Reemplaza `\` por `\\`
   > - Ajusta la ruta si instalaste en otro directorio

### Linux

1. **Localizar el archivo de configuración**:
```
   ~/.config/Claude/claude_desktop_config.json
```

2. **Crear/editar el archivo**:
```bash
   mkdir -p ~/.config/Claude
   nano ~/.config/Claude/claude_desktop_config.json
```

3. **Agregar la configuración**:
```json
   {
     "mcpServers": {
       "web-deployer": {
         "command": "/home/TU_USUARIO/MCP/MCP-Despliegues/mcp-web-deployer/venv/bin/python",
         "args": [
           "/home/TU_USUARIO/MCP/MCP-Despliegues/mcp-web-deployer/src/server.py"
         ]
       }
     }
   }
```

   > ⚠️ Reemplaza `TU_USUARIO` con tu nombre de usuario

### macOS

1. **Localizar el archivo de configuración**:
```
   ~/Library/Application Support/Claude/claude_desktop_config.json
```

2. **Crear/editar el archivo**:
```bash
   mkdir -p ~/Library/Application\ Support/Claude
   nano ~/Library/Application\ Support/Claude/claude_desktop_config.json
```

3. **Agregar la configuración**:
```json
   {
     "mcpServers": {
       "web-deployer": {
         "command": "/Users/TU_USUARIO/MCP/MCP-Despliegues/mcp-web-deployer/venv/bin/python",
         "args": [
           "/Users/TU_USUARIO/MCP/MCP-Despliegues/mcp-web-deployer/src/server.py"
         ]
       }
     }
   }
```

   > ⚠️ Reemplaza `TU_USUARIO` con tu nombre de usuario

---

## Verificación

### 1. Verificar Entorno Virtual

**Windows**:
```powershell
.\venv\Scripts\python.exe --version
```

**Linux/macOS**:
```bash
./venv/bin/python --version
```

### 2. Verificar Dependencias
```bash
# Activar entorno virtual primero
# Windows: .\venv\Scripts\Activate.ps1
# Linux/macOS: source venv/bin/activate

# Verificar instalación de MCP
pip list | grep mcp
```

### 3. Verificar Docker
```bash
# Ver versión de Docker
docker --version

# Verificar que Docker está corriendo
docker info

# Probar con contenedor de prueba
docker run hello-world
```

### 4. Verificar Configuración de Claude

1. Abre Claude Desktop
2. Ve a Configuración → MCP Servers
3. Deberías ver "web-deployer" en la lista
4. Verifica que el estado sea "Conectado"

### 5. Prueba Funcional

En Claude Desktop, escribe:
```
"Por favor, lista las herramientas MCP disponibles"
```

Deberías ver las 5 herramientas:
- create_html
- deploy_server
- stop_server
- server_status
- list_html_files

---

## Troubleshooting

### Error: "Python no encontrado"

**Windows**:
```powershell
# Verificar instalación
where python

# Reinstalar desde python.org
# Asegúrate de marcar "Add to PATH"
```

**Linux/macOS**:
```bash
# Instalar Python 3
# Ubuntu/Debian:
sudo apt-get install python3 python3-venv

# macOS (con Homebrew):
brew install python@3.11
```

### Error: "Docker daemon no está corriendo"

1. Inicia Docker Desktop manualmente
2. Espera a que el ícono muestre "Running"
3. Verifica: `docker info`

### Error: "Permission denied" en Docker (Linux)
```bash
# Agregar usuario al grupo docker
sudo usermod -aG docker $USER

# Reiniciar sesión
newgrp docker

# O reiniciar el sistema
```

### Error: "Execution Policy" en PowerShell
```powershell
# Cambiar política de ejecución
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Verificar
Get-ExecutionPolicy
```

### Claude Desktop no detecta el servidor MCP

1. **Verifica la ruta del archivo de configuración**:
   - Windows: `%APPDATA%\Claude\claude_desktop_config.json`
   - Linux: `~/.config/Claude/claude_desktop_config.json`
   - macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`

2. **Verifica el formato JSON**:
   - Usa un validador JSON online
   - Asegúrate de que las rutas usen `\\` en Windows

3. **Reinicia Claude Desktop completamente**:
   - Cierra todas las ventanas
   - Espera 5 segundos
   - Abre nuevamente

4. **Verifica los logs de Claude**:
   - Windows: `%APPDATA%\Claude\logs`
   - Linux: `~/.config/Claude/logs`
   - macOS: `~/Library/Logs/Claude`

### Puerto 8080 ya está en uso
```powershell
# Windows: Ver qué proceso usa el puerto
netstat -ano | findstr :8080

# Matar el proceso (reemplaza PID)
taskkill /PID <PID> /F

# O usa otro puerto en Claude:
# "Despliega el servidor en el puerto 8081"
```
```bash
# Linux/macOS: Ver qué proceso usa el puerto
lsof -i :8080

# Matar el proceso
kill -9 <PID>
```

---

## Próximos Pasos

Una vez instalado correctamente:

1. Lee la [Guía de Uso](USAGE.md)
2. Revisa la [Arquitectura](ARCHITECTURE.md)
3. Prueba los ejemplos en `examples/`

---

## Soporte

Si encuentras problemas:

1. Revisa esta guía de troubleshooting
2. Busca en los Issues del repositorio en GitHub
3. Abre un nuevo issue con:
   - Sistema operativo
   - Versiones de software
   - Mensaje de error completo
   - Pasos para reproducir

---

**¡Felicitaciones!** 🎉

Has instalado exitosamente MCP Web Deployer. Ahora puedes desplegar sitios web con solo pedírselo a Claude.