#!/usr/bin/env python3
"""
MCP Web Deployer Server
=======================

Servidor MCP (Model Context Protocol) que permite a Claude Desktop
desplegar sitios web estáticos mediante contenedores Docker.

Licencia: MIT

Este proyecto demuestra:
- Integración de AI (Claude) con DevOps
- Implementación de servidores MCP personalizados
- Automatización de despliegues con Docker
- Buenas prácticas de desarrollo Python
"""

import asyncio
import json
import sys
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

try:
    from mcp.server import Server
    from mcp.types import Tool, TextContent
    from mcp.server.stdio import stdio_server
except ImportError:
    print("Error: MCP SDK no instalado. Ejecuta: pip install mcp")
    sys.exit(1)

# Configuración de rutas
# Obtiene el directorio raíz del proyecto (dos niveles arriba de este archivo)
PROJECT_ROOT = Path(__file__).parent.parent
WWW_DIR = PROJECT_ROOT / "www"
EXAMPLES_DIR = PROJECT_ROOT / "examples"

# Nombre del contenedor Docker
CONTAINER_NAME = "mcp-web-server"
DEFAULT_PORT = 8080


class WebDeployerServer:
    """
    Servidor MCP para despliegue automatizado de sitios web.
    
    Proporciona herramientas para:
    - Crear archivos HTML
    - Desplegar servidores web en Docker
    - Gestionar el ciclo de vida del servidor
    - Consultar estado del sistema
    
    Attributes:
        server (Server): Instancia del servidor MCP
    """
    
    def __init__(self):
        """
        Inicializa el servidor MCP y configura el entorno.
        
        - Crea el servidor MCP con nombre identificador
        - Asegura que existan los directorios necesarios
        - Registra los manejadores de herramientas
        """
        self.server = Server("web-deployer")
        self._ensure_directories()
        self._setup_handlers()
    
    def _ensure_directories(self):
        """
        Crea los directorios necesarios si no existen.
        
        Directorios creados:
        - www/: Donde se guardan los archivos HTML del usuario
        - examples/: Ejemplos de archivos HTML pre-configurados
        """
        WWW_DIR.mkdir(exist_ok=True)
        EXAMPLES_DIR.mkdir(exist_ok=True)
        
        # Crear archivo .gitkeep para mantener la carpeta www/ en Git
        # pero sin incluir su contenido
        gitkeep = WWW_DIR / ".gitkeep"
        if not gitkeep.exists():
            gitkeep.touch()
    
    def _setup_handlers(self):
        """
        Registra los manejadores de herramientas MCP.
        
        Define qué herramientas están disponibles y cómo se ejecutan.
        Cada handler es una función asíncrona decorada que responde
        a solicitudes específicas del cliente MCP (Claude Desktop).
        """
        
        @self.server.list_tools()
        async def list_tools() -> list[Tool]:
            """
            Retorna la lista de herramientas disponibles para Claude.
            
            Claude Desktop usa esta información para saber qué puede hacer
            con este servidor MCP. Cada Tool especifica:
            - name: Identificador único
            - description: Cuándo y cómo usarla (ayuda a Claude a decidir)
            - inputSchema: Parámetros aceptados (formato JSON Schema)
            
            Returns:
                Lista de objetos Tool con todas las herramientas disponibles
            """
            return [
                Tool(
                    name="create_html",
                    description=(
                        "Crea un archivo HTML en el directorio www/. "
                        "Acepta contenido HTML personalizado. El archivo será "
                        "servido automáticamente cuando el servidor esté activo."
                    ),
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "filename": {
                                "type": "string",
                                "description": "Nombre del archivo (ej: index.html, about.html)",
                                "pattern": "^[a-zA-Z0-9_-]+\\.html$"
                            },
                            "content": {
                                "type": "string",
                                "description": "Contenido HTML completo del archivo"
                            }
                        },
                        "required": ["filename", "content"]
                    }
                ),
                Tool(
                    name="deploy_server",
                    description=(
                        "Despliega un servidor web Nginx en Docker para servir "
                        "los archivos HTML del directorio www/. El servidor será "
                        "accesible en http://localhost:PORT (default: 8080)"
                    ),
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "port": {
                                "type": "integer",
                                "description": "Puerto donde exponer el servidor",
                                "default": DEFAULT_PORT,
                                "minimum": 1024,
                                "maximum": 65535
                            }
                        }
                    }
                ),
                Tool(
                    name="stop_server",
                    description=(
                        "Detiene y elimina el contenedor Docker del servidor web. "
                        "Los archivos HTML permanecen en el directorio www/."
                    ),
                    inputSchema={
                        "type": "object",
                        "properties": {}
                    }
                ),
                Tool(
                    name="server_status",
                    description=(
                        "Verifica el estado actual del servidor web Docker. "
                        "Muestra si está activo, en qué puerto, y estadísticas básicas."
                    ),
                    inputSchema={
                        "type": "object",
                        "properties": {}
                    }
                ),
                Tool(
                    name="list_html_files",
                    description=(
                        "Lista todos los archivos HTML en el directorio www/. "
                        "Útil para ver qué archivos están disponibles para servir."
                    ),
                    inputSchema={
                        "type": "object",
                        "properties": {}
                    }
                )
            ]
        
        @self.server.call_tool()
        async def call_tool(name: str, arguments: Any) -> list[TextContent]:
            """
            Ejecuta una herramienta específica cuando Claude la invoca.
            
            Este es el dispatcher principal que recibe todas las invocaciones
            de herramientas y las redirige al método apropiado.
            
            Args:
                name: Nombre de la herramienta a ejecutar
                arguments: Diccionario con los parámetros de entrada
            
            Returns:
                Lista de TextContent con los resultados de la ejecución
                
            Raises:
                ValueError: Si la herramienta no existe
            """
            # Mapeo de nombres de herramientas a métodos
            tool_map = {
                "create_html": self._create_html,
                "deploy_server": self._deploy_server,
                "stop_server": self._stop_server,
                "server_status": self._server_status,
                "list_html_files": self._list_html_files,
            }
            
            # Validar que la herramienta existe
            if name not in tool_map:
                raise ValueError(f"Herramienta desconocida: {name}")
            
            # Ejecutar la herramienta correspondiente
            return await tool_map[name](arguments)
    
    async def _create_html(self, args: dict) -> list[TextContent]:
        """
        Crea un archivo HTML en el directorio www/.
        
        Proceso:
        1. Valida el nombre del archivo
        2. Escribe el contenido HTML
        3. Retorna confirmación con metadata
        
        Args:
            args: Diccionario con 'filename' y 'content'
        
        Returns:
            Lista con TextContent de confirmación
        """
        filename = args.get("filename", "index.html")
        content = args.get("content", "")
        
        # Validación: solo permitir archivos .html
        if not filename.endswith(".html"):
            filename += ".html"
        
        # Construir ruta completa
        file_path = WWW_DIR / filename
        
        try:
            # Escribir contenido al archivo
            file_path.write_text(content, encoding="utf-8")
            
            # Retornar confirmación con información útil
            return [
                TextContent(
                    type="text",
                    text=(
                        f"✅ Archivo HTML creado exitosamente\n\n"
                        f"📄 Archivo: {filename}\n"
                        f"📍 Ruta: {file_path}\n"
                        f"📊 Tamaño: {len(content)} caracteres\n"
                        f"🕐 Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
                        f"💡 Para ver el archivo, despliega el servidor con 'deploy_server'"
                    )
                )
            ]
        except Exception as e:
            return [
                TextContent(
                    type="text",
                    text=f"❌ Error al crear archivo: {str(e)}"
                )
            ]
    
    async def _deploy_server(self, args: dict) -> list[TextContent]:
        """
        Despliega un servidor web Nginx en Docker.
        
        Proceso detallado:
        1. Obtiene el puerto de configuración
        2. Detiene cualquier contenedor previo
        3. Inicia nuevo contenedor Nginx con:
           - Imagen: nginx:alpine (ligera y segura)
           - Puerto mapeado: host:container
           - Volumen: www/ montado en /usr/share/nginx/html (read-only)
        4. Verifica que el contenedor inició correctamente
        
        Args:
            args: Diccionario con 'port' opcional
        
        Returns:
            Lista con TextContent del resultado del despliegue
        """
        port = args.get("port", DEFAULT_PORT)
        
        try:
            # Paso 1: Limpiar contenedores previos
            # Usamos 2>nul & para ignorar errores si no existe el contenedor
            cleanup_cmd = (
                f'docker stop {CONTAINER_NAME} 2>nul & '
                f'docker rm {CONTAINER_NAME} 2>nul & '
                f'echo.'  # Comando dummy para evitar error
            )
            
            proc = await asyncio.create_subprocess_shell(
                cleanup_cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            await proc.communicate()
            
            # Paso 2: Obtener ruta absoluta del directorio www/
            # Docker requiere rutas absolutas para volúmenes
            www_abs = WWW_DIR.absolute()
            
            # Convertir ruta de Windows a formato Docker
            # C:\MCP\MCP-Despliegues\mcp-web-deployer\... -> /c/MCP/MCP-Despliegues/mcp-web-deployer/...
            www_docker = str(www_abs).replace("\\", "/").replace("C:", "/c")
            
            # Paso 3: Construir comando Docker
            docker_cmd = (
                f'docker run -d '
                f'--name {CONTAINER_NAME} '
                f'-p {port}:80 '
                f'-v "{www_docker}:/usr/share/nginx/html:ro" '
                f'nginx:alpine'
            )
            
            # Ejecutar comando Docker
            proc = await asyncio.create_subprocess_shell(
                docker_cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await proc.communicate()
            
            # Verificar resultado
            if proc.returncode == 0:
                container_id = stdout.decode().strip()[:12]
                return [
                    TextContent(
                        type="text",
                        text=(
                            f"🚀 Servidor web desplegado exitosamente!\n\n"
                            f"🆔 Container ID: {container_id}\n"
                            f"🔌 Puerto: {port}\n"
                            f"🌐 URL: http://localhost:{port}\n"
                            f"📁 Directorio: {www_abs}\n"
                            f"🐳 Imagen: nginx:alpine\n\n"
                            f"💡 Abre tu navegador en http://localhost:{port}\n"
                            f"📝 Los archivos en www/ se sirven automáticamente"
                        )
                    )
                ]
            else:
                error_msg = stderr.decode()
                return [
                    TextContent(
                        type="text",
                        text=(
                            f"❌ Error al desplegar servidor\n\n"
                            f"Detalles: {error_msg}\n\n"
                            f"💡 Verifica que Docker Desktop esté corriendo"
                        )
                    )
                ]
                
        except Exception as e:
            return [
                TextContent(
                    type="text",
                    text=f"❌ Excepción al desplegar: {str(e)}"
                )
            ]
    
    async def _stop_server(self, args: dict = None) -> list[TextContent]:
        """
        Detiene y elimina el contenedor Docker del servidor web.
        
        Los archivos HTML en www/ no se eliminan, solo el contenedor.
        
        Returns:
            Lista con TextContent del resultado
        """
        try:
            # Comando combinado: detener Y eliminar
            cmd = f'docker stop {CONTAINER_NAME} && docker rm {CONTAINER_NAME}'
            
            proc = await asyncio.create_subprocess_shell(
                cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await proc.communicate()
            
            if proc.returncode == 0:
                return [
                    TextContent(
                        type="text",
                        text=(
                            f"🛑 Servidor web detenido y eliminado\n\n"
                            f"✅ Contenedor '{CONTAINER_NAME}' removido\n"
                            f"📁 Los archivos en www/ se mantienen intactos"
                        )
                    )
                ]
            else:
                return [
                    TextContent(
                        type="text",
                        text=f"⚠️ No se encontró servidor web activo"
                    )
                ]
                
        except Exception as e:
            return [
                TextContent(
                    type="text",
                    text=f"❌ Error al detener servidor: {str(e)}"
                )
            ]
    
    async def _server_status(self, args: dict = None) -> list[TextContent]:
        """
        Verifica el estado del contenedor Docker.
        
        Usa 'docker ps' para consultar si el contenedor está corriendo
        y obtiene información adicional como puertos y tiempo activo.
        
        Returns:
            Lista con TextContent del estado actual
        """
        try:
            # Obtener información del contenedor
            # --format: salida personalizada con placeholders
            cmd = (
                f'docker ps --filter name={CONTAINER_NAME} '
                f'--format "{{{{.ID}}}}|{{{{.Status}}}}|{{{{.Ports}}}}"'
            )
            
            proc = await asyncio.create_subprocess_shell(
                cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await proc.communicate()
            output = stdout.decode().strip()
            
            if output:
                # Parsear salida
                parts = output.split("|")
                container_id = parts[0][:12]
                status = parts[1] if len(parts) > 1 else "Unknown"
                ports = parts[2] if len(parts) > 2 else "Unknown"
                
                return [
                    TextContent(
                        type="text",
                        text=(
                            f"✅ Servidor web ACTIVO\n\n"
                            f"🆔 Container: {container_id}\n"
                            f"📊 Estado: {status}\n"
                            f"🔌 Puertos: {ports}\n"
                            f"🌐 Acceso: http://localhost:{DEFAULT_PORT}\n\n"
                            f"💡 El servidor está sirviendo archivos de www/"
                        )
                    )
                ]
            else:
                return [
                    TextContent(
                        type="text",
                        text=(
                            f"⭕ Servidor web INACTIVO\n\n"
                            f"💡 Usa 'deploy_server' para iniciarlo"
                        )
                    )
                ]
                
        except Exception as e:
            return [
                TextContent(
                    type="text",
                    text=f"❌ Error verificando estado: {str(e)}"
                )
            ]
    
    async def _list_html_files(self, args: dict = None) -> list[TextContent]:
        """
        Lista todos los archivos HTML en el directorio www/.
        
        Muestra información útil:
        - Nombre del archivo
        - Tamaño
        - Fecha de modificación
        
        Returns:
            Lista con TextContent de los archivos encontrados
        """
        try:
            # Obtener todos los archivos .html
            html_files = list(WWW_DIR.glob("*.html"))
            
            if not html_files:
                return [
                    TextContent(
                        type="text",
                        text=(
                            f"📂 Directorio www/ está vacío\n\n"
                            f"💡 Usa 'create_html' para crear archivos"
                        )
                    )
                ]
            
            # Construir lista de archivos con metadata
            file_list = []
            for file in html_files:
                size = file.stat().st_size
                mtime = datetime.fromtimestamp(file.stat().st_mtime)
                file_list.append(
                    f"📄 {file.name}\n"
                    f"   📊 Tamaño: {size} bytes\n"
                    f"   🕐 Modificado: {mtime.strftime('%Y-%m-%d %H:%M:%S')}"
                )
            
            files_text = "\n\n".join(file_list)
            
            return [
                TextContent(
                    type="text",
                    text=(
                        f"📂 Archivos HTML en www/ ({len(html_files)} encontrados)\n\n"
                        f"{files_text}\n\n"
                        f"🌐 Accesibles en: http://localhost:{DEFAULT_PORT}/FILENAME"
                    )
                )
            ]
            
        except Exception as e:
            return [
                TextContent(
                    type="text",
                    text=f"❌ Error listando archivos: {str(e)}"
                )
            ]
    
    async def run(self):
        """
        Inicia el servidor MCP.
        
        Configura la comunicación stdio (stdin/stdout) que es el mecanismo
        que usa Claude Desktop para comunicarse con servidores MCP.
        
        El servidor queda corriendo indefinidamente esperando comandos.
        """
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                self.server.create_initialization_options()
            )


async def main():
    """
    Función principal de entrada del programa.
    
    Instancia y ejecuta el servidor MCP.
    """
    print("🚀 Iniciando MCP Web Deployer Server...", file=sys.stderr)
    print(f"📁 Directorio www: {WWW_DIR}", file=sys.stderr)
    
    server = WebDeployerServer()
    await server.run()


if __name__ == "__main__":
    """
    Punto de entrada cuando se ejecuta el script directamente.
    
    asyncio.run() ejecuta la función asíncrona main() hasta que complete.
    """
    asyncio.run(main())