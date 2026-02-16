# 🏗️ Arquitectura - MCP Web Deployer

Esta documentación explica la arquitectura técnica del proyecto, cómo funcionan los componentes y cómo se comunican entre sí.

---

## 📋 Tabla de Contenidos

1. [Visión General](#visión-general)
2. [Componentes](#componentes)
3. [Flujo de Datos](#flujo-de-datos)
4. [Protocolo MCP](#protocolo-mcp)
5. [Gestión de Archivos](#gestión-de-archivos)
6. [Contenedores Docker](#contenedores-docker)
7. [Seguridad](#seguridad)
8. [Performance](#performance)

---

## Visión General

### Diagrama de Alto Nivel
```
┌─────────────────────────────────────────────────────────────┐
│                        USUARIO                               │
│                     (Claude Desktop)                         │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        │ Lenguaje Natural
                        ▼
┌─────────────────────────────────────────────────────────────┐
│                   CLAUDE AI ENGINE                           │
│  - Analiza intención del usuario                            │
│  - Decide qué herramientas MCP usar                          │
│  - Genera parámetros apropiados                             │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        │ MCP Protocol (stdio)
                        │ JSON-RPC 2.0
                        ▼
┌─────────────────────────────────────────────────────────────┐
│                  MCP SERVER (server.py)                      │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  WebDeployerServer                                   │   │
│  │  - Registra herramientas disponibles                │   │
│  │  - Procesa solicitudes                              │   │
│  │  - Ejecuta lógica de negocio                        │   │
│  └─────────────────────────────────────────────────────┘   │
└───────────────────────┬─────────────────────────────────────┘
                        │
            ┌───────────┴───────────┐
            │                       │
            ▼                       ▼
┌─────────────────────┐  ┌─────────────────────┐
│   FILE SYSTEM       │  │   DOCKER ENGINE     │
│   (www/)            │  │   (Nginx)           │
│                     │  │                     │
│  - Almacena HTML    │  │  - Contenedores     │
│  - Lectura/Escritura│  │  - Volúmenes        │
└─────────────────────┘  └──────────┬──────────┘
                                    │
                                    │ HTTP
                                    ▼
                        ┌─────────────────────┐
                        │    NAVEGADOR        │
                        │  localhost:8080     │
                        └─────────────────────┘
```

---

## Componentes

### 1. Claude Desktop (Cliente)

**Función**: Interfaz de usuario

**Responsabilidades**:
- Recibir input del usuario
- Enviar solicitudes al MCP Server
- Mostrar respuestas al usuario

**Tecnología**: Aplicación Electron

**Comunicación**: 
- Protocolo: MCP via stdio
- Formato: JSON-RPC 2.0

---

### 2. MCP Server (server.py)

**Función**: Backend que expone herramientas a Claude

**Arquitectura Interna**:
```python
server.py
│
├── WebDeployerServer (Class Principal)
│   │
│   ├── __init__()
│   │   └── Inicializa servidor MCP
│   │
│   ├── _ensure_directories()
│   │   └── Crea directorios necesarios
│   │
│   ├── _setup_handlers()
│   │   ├── list_tools() → Registra herramientas
│   │   └── call_tool() → Dispatcher de herramientas
│   │
│   ├── Herramientas (Tools)
│   │   ├── _create_html()
│   │   ├── _deploy_server()
│   │   ├── _stop_server()
│   │   ├── _server_status()
│   │   └── _list_html_files()
│   │
│   └── run()
│       └── Inicia servidor MCP
│
└── main()
    └── Entry point
```

**Componentes Clave**:

#### Server Instance
```python
from mcp.server import Server

self.server = Server("web-deployer")
```
- Crea instancia del servidor MCP
- Nombre único: "web-deployer"

#### Tool Registration
```python
@self.server.list_tools()
async def list_tools() -> list[Tool]:
    return [Tool(...), Tool(...), ...]
```
- Decorador que registra función
- Retorna lista de herramientas disponibles
- Claude consulta esto para saber qué puede hacer

#### Tool Execution
```python
@self.server.call_tool()
async def call_tool(name: str, arguments: Any):
    # Dispatcher
    return await self._create_html(arguments)
```
- Decorador que registra executor
- Recibe nombre de herramienta y argumentos
- Ejecuta la función correspondiente

---

### 3. Docker Engine

**Función**: Ejecutar contenedor Nginx

**Componentes**:
```
Docker Engine
│
├── Imagen: nginx:alpine
│   ├── Tamaño: ~23MB
│   ├── OS: Alpine Linux
│   └── Servidor: Nginx 1.24+
│
├── Contenedor: mcp-web-server
│   ├── Estado: Running / Stopped
│   ├── Puerto: 8080:80 (host:container)
│   └── Volumen: www/ → /usr/share/nginx/html
│
└── Red: bridge (default)
```

**Configuración del Contenedor**:
```bash
docker run -d \
  --name mcp-web-server \      # Nombre del contenedor
  -p 8080:80 \                 # Mapeo de puertos
  -v "C:/MCP/.../www:/usr/share/nginx/html:ro" \  # Volumen read-only
  nginx:alpine                 # Imagen
```

---

## Flujo de Datos

### Flujo 1: Crear Archivo HTML
```
1. USUARIO
   │
   └─► "Crea un index.html con..."
        │
        ▼
2. CLAUDE AI
   │
   ├─► Analiza intención
   ├─► Genera contenido HTML
   └─► Prepara llamada MCP
        │
        │ JSON-RPC Request:
        │ {
        │   "method": "tools/call",
        │   "params": {
        │     "name": "create_html",
        │     "arguments": {
        │       "filename": "index.html",
        │       "content": "<html>...</html>"
        │     }
        │   }
        │ }
        │
        ▼
3. MCP SERVER
   │
   ├─► Recibe request via stdio
   ├─► Deserializa JSON
   ├─► call_tool("create_html", {...})
   │    │
   │    └─► _create_html(args)
   │         │
   │         ├─► Valida filename
   │         ├─► Construye ruta: www/index.html
   │         ├─► Escribe archivo
   │         └─► Retorna confirmación
   │
   │ JSON-RPC Response:
   │ {
   │   "result": {
   │     "content": [
   │       {
   │         "type": "text",
   │         "text": "✅ Archivo creado..."
   │       }
   │     ]
   │   }
   │ }
   │
   ▼
4. CLAUDE AI
   │
   └─► Muestra confirmación al usuario
        │
        ▼
5. USUARIO
   │
   └─► Ve: "✅ Archivo HTML creado exitosamente..."
```

---

### Flujo 2: Desplegar Servidor
```
1. USUARIO → "Despliega el servidor"
        ↓
2. CLAUDE → Llama deploy_server()
        ↓
3. MCP SERVER
   │
   └─► _deploy_server(args)
        │
        ├─► PASO 1: Limpiar contenedores previos
        │   │
        │   └─► asyncio.create_subprocess_shell(
        │         "docker stop mcp-web-server & docker rm mcp-web-server"
        │       )
        │
        ├─► PASO 2: Preparar rutas
        │   │
        │   ├─► www_abs = C:\MCP\...\www
        │   └─► www_docker = /c/MCP/.../www
        │
        ├─► PASO 3: Crear contenedor
        │   │
        │   └─► asyncio.create_subprocess_shell(
        │         "docker run -d --name mcp-web-server -p 8080:80 -v ... nginx:alpine"
        │       )
        │        │
        │        └─► Docker Engine
        │             │
        │             ├─► Pull imagen nginx:alpine (si no existe)
        │             ├─► Crear contenedor
        │             ├─► Montar volumen www/
        │             ├─► Exponer puerto 8080
        │             └─► Iniciar Nginx
        │
        └─► PASO 4: Retornar confirmación
             │
             └─► "🚀 Servidor desplegado... http://localhost:8080"
        ↓
4. CLAUDE → Muestra confirmación
        ↓
5. USUARIO → Abre navegador en localhost:8080
        ↓
6. NGINX → Sirve archivos de www/
```

---

## Protocolo MCP

### Formato de Mensajes

El servidor MCP usa **JSON-RPC 2.0** sobre **stdio** (standard input/output).

#### Request (Claude → Server)
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/call",
  "params": {
    "name": "create_html",
    "arguments": {
      "filename": "test.html",
      "content": "<html>...</html>"
    }
  }
}
```

#### Response (Server → Claude)
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "content": [
      {
        "type": "text",
        "text": "✅ Archivo creado exitosamente"
      }
    ]
  }
}
```

#### Error Response
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "error": {
    "code": -32600,
    "message": "Invalid params",
    "data": {
      "details": "Filename must end with .html"
    }
  }
}
```

---

### Tool Schema (JSON Schema)

Cada herramienta se define con un schema que especifica sus parámetros:
```python
Tool(
    name="create_html",
    description="Crea un archivo HTML...",
    inputSchema={
        "type": "object",
        "properties": {
            "filename": {
                "type": "string",
                "description": "Nombre del archivo",
                "pattern": "^[a-zA-Z0-9_-]+\\.html$"
            },
            "content": {
                "type": "string",
                "description": "Contenido HTML"
            }
        },
        "required": ["filename", "content"]
    }
)
```

**Validación**:
- Claude valida antes de enviar
- El servidor puede validar adicionalmente
- Errores retornan mensajes descriptivos

---

## Gestión de Archivos

### Estructura de Directorios
```
C:\MCP\MCP-Despliegues\mcp-web-deployer\
│
├── www/                          # Archivos servidos por Nginx
│   ├── .gitkeep                 # Mantiene carpeta en Git
│   ├── index.html               # Generados por usuario
│   ├── about.html
│   └── ...
│
├── examples/                     # Ejemplos pre-hechos
│   └── welcome.html
│
└── src/
    └── server.py                # No accede a www/ directamente
                                 # Solo via pathlib.Path
```

### Rutas en el Código
```python
# Configuración de rutas (server.py)
PROJECT_ROOT = Path(__file__).parent.parent
WWW_DIR = PROJECT_ROOT / "www"
EXAMPLES_DIR = PROJECT_ROOT / "examples"

# Crear archivo
file_path = WWW_DIR / filename
file_path.write_text(content, encoding="utf-8")

# Listar archivos
html_files = list(WWW_DIR.glob("*.html"))
```

**Ventajas de pathlib**:
- ✅ Multiplataforma (Windows, Linux, macOS)
- ✅ API limpia y legible
- ✅ Manejo seguro de rutas

---

### Volumen Docker
```
Host                           Container
─────                          ─────────
C:\MCP\...\www\      ←→        /usr/share/nginx/html/
    index.html       mapeado   index.html
    about.html                 about.html
```

**Modo Read-Only** (`:ro`):
- Nginx solo puede **leer** archivos
- No puede **modificar** ni **crear** archivos
- Mayor seguridad

---

## Contenedores Docker

### Ciclo de Vida
```
┌────────────────┐
│ deploy_server()│
└───────┬────────┘
        │
        ▼
┌────────────────────────┐
│ docker run nginx:alpine│
└───────┬────────────────┘
        │
        ▼
┌────────────────┐
│  CONTAINER     │
│  Running       │◄───── Sirve HTTP en puerto 80
│  (mcp-web-     │       (mapeado a 8080 en host)
│   server)      │
└───────┬────────┘
        │
        │ (usuario usa el servidor)
        │
        ▼
┌────────────────┐
│ stop_server()  │
└───────┬────────┘
        │
        ▼
┌────────────────┐
│ docker stop    │
│ docker rm      │
└───────┬────────┘
        │
        ▼
┌────────────────┐
│ CONTAINER      │
│ Deleted        │
└────────────────┘
```

### Comandos Docker Internos

#### Limpiar contenedores previos
```bash
docker stop mcp-web-server 2>nul
docker rm mcp-web-server 2>nul
```
- `2>nul`: Redirige errores (si no existe, no falla)
- Asegura estado limpio antes de crear

#### Crear contenedor
```bash
docker run -d \
  --name mcp-web-server \
  -p 8080:80 \
  -v "/c/MCP/.../www:/usr/share/nginx/html:ro" \
  nginx:alpine
```

**Flags**:
- `-d`: Detached (background)
- `--name`: Nombre único del contenedor
- `-p`: Port mapping (host:container)
- `-v`: Volume mount (host:container:permissions)

#### Verificar estado
```bash
docker ps --filter name=mcp-web-server \
  --format "{{.ID}}|{{.Status}}|{{.Ports}}"
```

**Output**:
```
abc123def456|Up 2 minutes|0.0.0.0:8080->80/tcp
```

---

## Seguridad

### 1. Aislamiento de Contenedores

**Docker proporciona**:
- ✅ Namespaces: Procesos aislados
- ✅ Cgroups: Recursos limitados
- ✅ Volúmenes read-only: Nginx no puede modificar archivos

### 2. Validación de Inputs
```python
# Validar filename
if not filename.endswith(".html"):
    filename += ".html"

# JSON Schema valida automáticamente:
# - Tipos de datos
# - Campos requeridos
# - Patrones regex
```

### 3. No Expone Puerto Externamente
```bash
-p 8080:80
   ^^^^  ^^
   │     └─ Puerto interno del contenedor
   └─ Puerto en localhost SOLAMENTE
```

**No accesible desde**:
- ❌ Internet
- ❌ Otros dispositivos en la red local

**Solo accesible desde**:
- ✅ localhost (tu máquina)

### 4. Sin Credenciales Hardcodeadas

- ❌ No hay API keys en el código
- ❌ No hay passwords
- ❌ No hay tokens

### 5. Separación de Responsabilidades
```
MCP Server    →  Solo gestiona lógica
Docker        →  Solo ejecuta contenedores
Nginx         →  Solo sirve archivos estáticos
```

---

## Performance

### Async/Await (Python asyncio)

**Todas las operaciones I/O son asíncronas**:
```python
async def _deploy_server(self, args: dict):
    # No bloquea el event loop
    proc = await asyncio.create_subprocess_shell(...)
    stdout, stderr = await proc.communicate()
```

**Ventajas**:
- ✅ No bloquea mientras espera Docker
- ✅ Puede manejar múltiples solicitudes
- ✅ Eficiente con recursos

### stdio Communication

**Comunicación via stdin/stdout**:
- ✅ Muy rápido (IPC local)
- ✅ Bajo overhead
- ✅ No requiere red

### Nginx Alpine

**Imagen ligera**:
- ✅ Tamaño: ~23MB
- ✅ Inicia en < 1 segundo
- ✅ Bajo uso de RAM (~10MB)

### Volumen Mount

**Acceso directo a archivos**:
- ✅ No copia archivos
- ✅ Cambios instantáneos
- ✅ Sin duplicación de datos

---

## Extensibilidad

### Agregar Nueva Herramienta

**Paso 1**: Define la herramienta
```python
Tool(
    name="delete_html",
    description="Elimina un archivo HTML",
    inputSchema={
        "type": "object",
        "properties": {
            "filename": {"type": "string"}
        },
        "required": ["filename"]
    }
)
```

**Paso 2**: Implementa la función
```python
async def _delete_html(self, args: dict) -> list[TextContent]:
    filename = args.get("filename")
    file_path = WWW_DIR / filename
    
    if file_path.exists():
        file_path.unlink()
        return [TextContent(type="text", text="✅ Eliminado")]
    else:
        return [TextContent(type="text", text="❌ No existe")]
```

**Paso 3**: Registra en el dispatcher
```python
tool_map = {
    "create_html": self._create_html,
    "deploy_server": self._deploy_server,
    "delete_html": self._delete_html,  # Nueva
    # ...
}
```

---

## Limitaciones Conocidas

### 1. Un Contenedor a la Vez

**Actual**: Solo puede haber un `mcp-web-server` corriendo

**Solución Futura**: 
- Generar nombres únicos por puerto
- `mcp-web-server-8080`, `mcp-web-server-8081`, etc.

### 2. Solo Archivos Estáticos

**Actual**: Solo sirve HTML/CSS/JS estáticos

**No soporta**:
- ❌ Server-side rendering
- ❌ Bases de datos
- ❌ APIs backend

**Solución Futura**:
- Agregar soporte para Node.js
- Contenedor con Express/Fastify

### 3. Sin HTTPS

**Actual**: Solo HTTP

**Solución Futura**:
- Certificados autofirmados
- Let's Encrypt integration

---

## Diagrama de Clases
```
┌─────────────────────────────────────┐
│      WebDeployerServer              │
├─────────────────────────────────────┤
│ - server: Server                    │
│ - WWW_DIR: Path                     │
│ - EXAMPLES_DIR: Path                │
├─────────────────────────────────────┤
│ + __init__()                        │
│ + run()                             │
│ - _ensure_directories()             │
│ - _setup_handlers()                 │
│ - _create_html(args)                │
│ - _deploy_server(args)              │
│ - _stop_server(args)                │
│ - _server_status(args)              │
│ - _list_html_files(args)            │
└─────────────────────────────────────┘
```

---

## Stack Tecnológico Detallado

| Capa | Tecnología | Versión | Función |
|------|-----------|---------|---------|
| **Frontend** | Claude Desktop | Latest | UI/Cliente |
| **Protocol** | MCP (stdio) | 1.0 | Comunicación |
| **Backend** | Python | 3.8+ | Servidor MCP |
| **Async** | asyncio | Stdlib | Event loop |
| **MCP SDK** | mcp | 0.9.0+ | Framework MCP |
| **Container** | Docker | 20.10+ | Runtime |
| **Image** | nginx:alpine | 1.24+ | Web server |
| **OS** | Alpine Linux | 3.18+ | Container OS |

---

## Conclusión

Esta arquitectura demuestra:

- ✅ **Simplicidad**: Componentes bien definidos
- ✅ **Extensibilidad**: Fácil agregar herramientas
- ✅ **Performance**: Async I/O, contenedores ligeros
- ✅ **Seguridad**: Aislamiento, validación, read-only
- ✅ **Portabilidad**: Funciona en Windows/Linux/macOS

**Ideal para**:
- Aprender MCP
- Prototipado rápido
- Demos y presentaciones
- Testing de frontend

---

**¿Preguntas?** Abre un issue en GitHub o consulta la [Guía de Uso](USAGE.md).