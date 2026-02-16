"""
Tests para MCP Web Deployer Server.

Ejecutar con:
    pytest tests/ -v
    pytest tests/ -v --tb=short   (output corto en errores)
    pytest tests/ -v -k "create"  (solo tests que contengan "create")
"""

import asyncio
import os
import shutil
from pathlib import Path
from unittest.mock import AsyncMock, patch, MagicMock

import pytest

# Ajustar path para imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.server import WebDeployerServer, WWW_DIR, EXAMPLES_DIR, CONTAINER_NAME


# ============================================================
# Fixtures
# ============================================================

@pytest.fixture
def server():
    """Crea una instancia del servidor para cada test."""
    return WebDeployerServer()


@pytest.fixture
def temp_www(tmp_path):
    """Usa un directorio temporal como www/ para tests aislados."""
    import src.server as srv
    original_www = srv.WWW_DIR
    srv.WWW_DIR = tmp_path
    yield tmp_path
    srv.WWW_DIR = original_www


# ============================================================
# Tests de inicializacion
# ============================================================

class TestServerInit:
    """Tests de inicializacion del servidor."""

    def test_server_creates_instance(self, server):
        """El servidor se instancia correctamente."""
        assert server is not None
        assert server.server is not None

    def test_server_name(self, server):
        """El servidor tiene el nombre correcto."""
        assert server.server.name == "web-deployer"

    def test_www_directory_exists(self, server):
        """El directorio www/ existe tras inicializar."""
        assert WWW_DIR.exists()
        assert WWW_DIR.is_dir()

    def test_examples_directory_exists(self, server):
        """El directorio examples/ existe tras inicializar."""
        assert EXAMPLES_DIR.exists()
        assert EXAMPLES_DIR.is_dir()

    def test_gitkeep_exists(self, server):
        """El archivo .gitkeep existe en www/."""
        gitkeep = WWW_DIR / ".gitkeep"
        assert gitkeep.exists()


# ============================================================
# Tests de create_html
# ============================================================

class TestCreateHtml:
    """Tests para la herramienta create_html."""

    @pytest.mark.asyncio
    async def test_create_html_basic(self, server, temp_www):
        """Crea un archivo HTML basico."""
        result = await server._create_html({
            "filename": "test.html",
            "content": "<html><body>Test</body></html>"
        })
        assert len(result) == 1
        assert "creado exitosamente" in result[0].text
        assert (temp_www / "test.html").exists()

    @pytest.mark.asyncio
    async def test_create_html_content_matches(self, server, temp_www):
        """El contenido del archivo creado coincide con el input."""
        content = "<html><body><h1>Hola</h1></body></html>"
        await server._create_html({
            "filename": "check.html",
            "content": content
        })
        saved = (temp_www / "check.html").read_text(encoding="utf-8")
        assert saved == content

    @pytest.mark.asyncio
    async def test_create_html_adds_extension(self, server, temp_www):
        """Agrega .html si el filename no lo tiene."""
        await server._create_html({
            "filename": "noext",
            "content": "<html></html>"
        })
        assert (temp_www / "noext.html").exists()

    @pytest.mark.asyncio
    async def test_create_html_default_filename(self, server, temp_www):
        """Usa index.html como nombre por defecto."""
        await server._create_html({"content": "<html></html>"})
        assert (temp_www / "index.html").exists()

    @pytest.mark.asyncio
    async def test_create_html_overwrite(self, server, temp_www):
        """Sobreescribe un archivo existente."""
        await server._create_html({
            "filename": "over.html",
            "content": "version 1"
        })
        await server._create_html({
            "filename": "over.html",
            "content": "version 2"
        })
        saved = (temp_www / "over.html").read_text(encoding="utf-8")
        assert saved == "version 2"

    @pytest.mark.asyncio
    async def test_create_html_metadata_in_response(self, server, temp_www):
        """La respuesta incluye metadata del archivo."""
        result = await server._create_html({
            "filename": "meta.html",
            "content": "<html>x</html>"
        })
        text = result[0].text
        assert "meta.html" in text
        assert "Timestamp" in text


# ============================================================
# Tests de list_html_files
# ============================================================

class TestListHtmlFiles:
    """Tests para la herramienta list_html_files."""

    @pytest.mark.asyncio
    async def test_list_empty_directory(self, server, temp_www):
        """Lista vacia cuando no hay archivos HTML."""
        result = await server._list_html_files({})
        assert "vacio" in result[0].text.lower() or "vacío" in result[0].text

    @pytest.mark.asyncio
    async def test_list_finds_html_files(self, server, temp_www):
        """Encuentra archivos HTML creados."""
        (temp_www / "page1.html").write_text("<html>1</html>")
        (temp_www / "page2.html").write_text("<html>2</html>")
        result = await server._list_html_files({})
        text = result[0].text
        assert "page1.html" in text
        assert "page2.html" in text
        assert "2 encontrados" in text

    @pytest.mark.asyncio
    async def test_list_ignores_non_html(self, server, temp_www):
        """No lista archivos que no son .html."""
        (temp_www / "style.css").write_text("body{}")
        (temp_www / "app.js").write_text("console.log(1)")
        (temp_www / "page.html").write_text("<html></html>")
        result = await server._list_html_files({})
        text = result[0].text
        assert "page.html" in text
        assert "style.css" not in text
        assert "app.js" not in text

    @pytest.mark.asyncio
    async def test_list_shows_file_size(self, server, temp_www):
        """Muestra el tamano del archivo."""
        (temp_www / "sized.html").write_text("<html>test</html>")
        result = await server._list_html_files({})
        assert "bytes" in result[0].text


# ============================================================
# Tests de deploy_server (con mock de Docker)
# ============================================================

class TestDeployServer:
    """Tests para deploy_server (Docker mockeado)."""

    @pytest.mark.asyncio
    async def test_deploy_success(self, server):
        """Deploy exitoso retorna URL y container ID."""
        mock_proc = AsyncMock()
        mock_proc.communicate = AsyncMock(
            return_value=(b"abc123def456789\n", b"")
        )
        mock_proc.returncode = 0

        with patch("asyncio.create_subprocess_shell", return_value=mock_proc):
            result = await server._deploy_server({"port": 8080})

        text = result[0].text
        assert "desplegado exitosamente" in text
        assert "http://localhost:8080" in text
        assert "abc123def456" in text

    @pytest.mark.asyncio
    async def test_deploy_custom_port(self, server):
        """Deploy con puerto personalizado."""
        mock_proc = AsyncMock()
        mock_proc.communicate = AsyncMock(
            return_value=(b"containerid123\n", b"")
        )
        mock_proc.returncode = 0

        with patch("asyncio.create_subprocess_shell", return_value=mock_proc):
            result = await server._deploy_server({"port": 9090})

        assert "http://localhost:9090" in result[0].text

    @pytest.mark.asyncio
    async def test_deploy_failure(self, server):
        """Deploy fallido muestra error."""
        mock_proc = AsyncMock()
        mock_proc.communicate = AsyncMock(
            return_value=(b"", b"port already in use")
        )
        mock_proc.returncode = 1

        with patch("asyncio.create_subprocess_shell", return_value=mock_proc):
            result = await server._deploy_server({"port": 8080})

        assert "Error" in result[0].text

    @pytest.mark.asyncio
    async def test_deploy_default_port(self, server):
        """Usa puerto 8080 por defecto."""
        mock_proc = AsyncMock()
        mock_proc.communicate = AsyncMock(
            return_value=(b"containerid123\n", b"")
        )
        mock_proc.returncode = 0

        with patch("asyncio.create_subprocess_shell", return_value=mock_proc):
            result = await server._deploy_server({})

        assert "8080" in result[0].text


# ============================================================
# Tests de stop_server (con mock de Docker)
# ============================================================

class TestStopServer:
    """Tests para stop_server (Docker mockeado)."""

    @pytest.mark.asyncio
    async def test_stop_success(self, server):
        """Stop exitoso confirma detencion."""
        mock_proc = AsyncMock()
        mock_proc.communicate = AsyncMock(return_value=(b"", b""))
        mock_proc.returncode = 0

        with patch("asyncio.create_subprocess_shell", return_value=mock_proc):
            result = await server._stop_server({})

        text = result[0].text
        assert "detenido" in text
        assert "intactos" in text

    @pytest.mark.asyncio
    async def test_stop_no_server_running(self, server):
        """Stop sin servidor activo muestra advertencia."""
        mock_proc = AsyncMock()
        mock_proc.communicate = AsyncMock(
            return_value=(b"", b"No such container")
        )
        mock_proc.returncode = 1

        with patch("asyncio.create_subprocess_shell", return_value=mock_proc):
            result = await server._stop_server({})

        assert "No se encontr" in result[0].text


# ============================================================
# Tests de server_status (con mock de Docker)
# ============================================================

class TestServerStatus:
    """Tests para server_status (Docker mockeado)."""

    @pytest.mark.asyncio
    async def test_status_active(self, server):
        """Muestra estado activo cuando el contenedor corre."""
        mock_proc = AsyncMock()
        mock_proc.communicate = AsyncMock(
            return_value=(b"abc123def456|Up 5 minutes|0.0.0.0:8080->80/tcp\n", b"")
        )
        mock_proc.returncode = 0

        with patch("asyncio.create_subprocess_shell", return_value=mock_proc):
            result = await server._server_status({})

        text = result[0].text
        assert "ACTIVO" in text
        assert "abc123def456" in text
        assert "Up 5 minutes" in text

    @pytest.mark.asyncio
    async def test_status_inactive(self, server):
        """Muestra estado inactivo cuando no hay contenedor."""
        mock_proc = AsyncMock()
        mock_proc.communicate = AsyncMock(return_value=(b"", b""))
        mock_proc.returncode = 0

        with patch("asyncio.create_subprocess_shell", return_value=mock_proc):
            result = await server._server_status({})

        assert "INACTIVO" in result[0].text


# ============================================================
# Tests de constantes y configuracion
# ============================================================

class TestConfig:
    """Tests de configuracion del proyecto."""

    def test_container_name(self):
        """El nombre del contenedor es correcto."""
        assert CONTAINER_NAME == "mcp-web-server"

    def test_default_port(self):
        from src.server import DEFAULT_PORT
        assert DEFAULT_PORT == 8080

    def test_www_dir_is_path(self):
        """WWW_DIR es un objeto Path."""
        assert isinstance(WWW_DIR, Path)

    def test_examples_dir_is_path(self):
        """EXAMPLES_DIR es un objeto Path."""
        assert isinstance(EXAMPLES_DIR, Path)
