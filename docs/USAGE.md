# 💻 Guía de Uso - MCP Web Deployer

Esta guía te enseña cómo usar todas las funcionalidades del servidor MCP Web Deployer desde Claude Desktop.

---

## 📋 Tabla de Contenidos

1. [Inicio Rápido](#inicio-rápido)
2. [Herramientas Disponibles](#herramientas-disponibles)
3. [Ejemplos Prácticos](#ejemplos-prácticos)
4. [Workflows Comunes](#workflows-comunes)
5. [Tips y Trucos](#tips-y-trucos)
6. [Solución de Problemas](#solución-de-problemas)

---

## Inicio Rápido

### 1. Iniciar el Entorno

**Windows**:
```powershell
cd C:\MCP\MCP-Despliegues\mcp-web-deployer
.\scripts\start.ps1
```

**Linux/macOS**:
```bash
cd ~/MCP/MCP-Despliegues/mcp-web-deployer
source venv/bin/activate
```

### 2. Verificar Docker

Asegúrate de que Docker Desktop esté corriendo:
```bash
docker info
```

### 3. Abrir Claude Desktop

Reinicia Claude Desktop si acabas de configurar el servidor MCP.

### 4. Primer Comando

Escribe en Claude:
```
"Crea un archivo index.html con un mensaje de bienvenida"
```

---

## Herramientas Disponibles

### 🔧 create_html

**Descripción**: Crea un archivo HTML en el directorio `www/`.

**Parámetros**:
- `filename` (string): Nombre del archivo (ej: `index.html`)
- `content` (string): Contenido HTML completo

**Ejemplo de uso**:
```
"Crea un archivo llamado 'about.html' con información sobre el proyecto MCP Web Deployer"
```

**Lo que hace Claude**:
1. Genera contenido HTML apropiado
2. Llama a `create_html` con filename y content
3. El archivo se guarda en `C:\MCP\MCP-Despliegues\mcp-web-deployer\www\`
4. Confirma la creación con detalles del archivo

---

### 🚀 deploy_server

**Descripción**: Despliega un servidor web Nginx en Docker para servir los archivos HTML.

**Parámetros**:
- `port` (integer, opcional): Puerto donde exponer el servidor (default: 8080)

**Ejemplo de uso**:
```
"Despliega el servidor web"
```

O con puerto personalizado:
```
"Despliega el servidor en el puerto 8081"
```

**Lo que hace**:
1. Detiene cualquier contenedor previo
2. Crea un nuevo contenedor Nginx Alpine
3. Monta el directorio `www/` como volumen
4. Expone el puerto especificado
5. Retorna la URL de acceso

**Resultado**:
```
🚀 Servidor web desplegado exitosamente!

🆔 Container ID: abc123def456
🔌 Puerto: 8080
🌐 URL: http://localhost:8080
📁 Directorio: C:\MCP\MCP-Despliegues\mcp-web-deployer\www
🐳 Imagen: nginx:alpine

💡 Abre tu navegador en http://localhost:8080
```

---

### 🛑 stop_server

**Descripción**: Detiene y elimina el contenedor Docker del servidor web.

**Parámetros**: Ninguno

**Ejemplo de uso**:
```
"Detén el servidor web"
```

**Lo que hace**:
1. Ejecuta `docker stop mcp-web-server`
2. Ejecuta `docker rm mcp-web-server`
3. Los archivos HTML en `www/` permanecen intactos

---

### 📊 server_status

**Descripción**: Verifica el estado actual del servidor web Docker.

**Parámetros**: Ninguno

**Ejemplo de uso**:
```
"¿Está activo el servidor web?"
```

O simplemente:
```
"Estado del servidor"
```

**Respuesta cuando está activo**:
```
✅ Servidor web ACTIVO

🆔 Container: abc123def456
📊 Estado: Up 2 minutes
🔌 Puertos: 0.0.0.0:8080->80/tcp
🌐 Acceso: http://localhost:8080

💡 El servidor está sirviendo archivos de www/
```

**Respuesta cuando está inactivo**:
```
⭕ Servidor web INACTIVO

💡 Usa 'deploy_server' para iniciarlo
```

---

### 📂 list_html_files

**Descripción**: Lista todos los archivos HTML en el directorio `www/`.

**Parámetros**: Ninguno

**Ejemplo de uso**:
```
"Lista los archivos HTML disponibles"
```

O:
```
"¿Qué archivos tengo en www?"
```

**Respuesta**:
```
📂 Archivos HTML en www/ (3 encontrados)

📄 index.html
   📊 Tamaño: 2847 bytes
   🕐 Modificado: 2024-02-16 14:30:25

📄 about.html
   📊 Tamaño: 1523 bytes
   🕐 Modificado: 2024-02-16 14:35:10

📄 contact.html
   📊 Tamaño: 1892 bytes
   🕐 Modificado: 2024-02-16 14:40:55

🌐 Accesibles en: http://localhost:8080/FILENAME
```

---

## Ejemplos Prácticos

### Ejemplo 1: Crear y Desplegar un Sitio Simple

**Prompt**:
```
"Crea un archivo index.html con:
- Un título 'Mi Primer Sitio MCP'
- Un párrafo de bienvenida
- Estilos CSS modernos con gradiente azul
Luego despliega el servidor"
```

**Lo que sucede**:
1. Claude genera HTML con los requisitos
2. Llama a `create_html` con el contenido
3. Llama a `deploy_server` para iniciar Nginx
4. Te proporciona la URL: `http://localhost:8080`

---

### Ejemplo 2: Sitio Multi-página

**Prompt 1**:
```
"Crea un archivo index.html con:
- Título 'Mi Portfolio'
- Sección hero con mi nombre
- Links de navegación a 'about.html' y 'projects.html'
- Diseño moderno con CSS"
```

**Prompt 2**:
```
"Crea about.html con:
- Información sobre mi experiencia en DevOps
- Mis habilidades: Python, Docker, Kubernetes, Terraform
- Enlace de regreso a index.html"
```

**Prompt 3**:
```
"Crea projects.html con:
- Una lista de 3 proyectos ficticios
- Descripción breve de cada uno
- Enlace de regreso a index.html"
```

**Prompt 4**:
```
"Despliega el servidor y dime qué archivos tengo"
```

---

### Ejemplo 3: Landing Page para Producto

**Prompt**:
```
"Crea una landing page en index.html para un producto llamado 'DevOps Assistant'.
El producto es una herramienta de automatización de despliegues.

Incluye:
- Header con logo (texto) y navegación
- Sección hero con título atractivo y CTA
- Características del producto (3 columnas)
- Testimonios ficticios (2)
- Footer con redes sociales

Usa gradiente morado-azul, diseño moderno y responsive"
```

---

### Ejemplo 4: Página de Documentación

**Prompt**:
```
"Crea docs.html con documentación técnica sobre MCP Web Deployer:
- Tabla de contenidos lateral
- Secciones: Instalación, Configuración, Uso
- Código de ejemplo con sintaxis highlight
- Diseño tipo documentación técnica"
```

---

### Ejemplo 5: Formulario de Contacto (Frontend)

**Prompt**:
```
"Crea contact.html con un formulario de contacto que incluya:
- Campos: nombre, email, asunto, mensaje
- Validación visual con JavaScript
- Diseño moderno con animaciones
- Nota: el formulario solo valida, no envía datos (es demo)"
```

---

## Workflows Comunes

### Workflow 1: Desarrollo Iterativo
```
1. "Crea un index.html básico"
2. "Despliega el servidor"
3. [Revisar en navegador]
4. "Modifica index.html para agregar una sección de proyectos"
5. [Refrescar navegador - cambios automáticos]
6. "Agrega animaciones CSS a la página"
7. [Refrescar navegador]
```

> 💡 **Tip**: No necesitas redesplegar el servidor, los cambios se reflejan automáticamente al refrescar el navegador.

---

### Workflow 2: Testing Multi-Puerto
```
1. "Despliega el servidor en el puerto 8080"
2. "Crea una versión alternativa en index-v2.html"
3. "Detén el servidor"
4. "Renombra index-v2.html a index.html"
5. "Despliega el servidor en el puerto 8081"
```

Ahora tienes dos versiones corriendo simultáneamente:
- Versión 1: `http://localhost:8080`
- Versión 2: `http://localhost:8081`

---

### Workflow 3: Presentación de Proyectos
```
1. "Crea un sitio de portfolio con 5 páginas"
2. "Despliega el servidor"
3. [Presentar en reunión]
4. "Detén el servidor cuando termine"
```

---

### Workflow 4: Prototipado Rápido
```
1. "Crea un prototipo de dashboard con:
   - Sidebar de navegación
   - Cards con métricas
   - Gráficos ficticios
   - Tabla de datos"
2. "Despliega el servidor"
3. [Obtener feedback]
4. "Modifica el dashboard según este feedback: [detalles]"
```

---

## Tips y Trucos

### 📝 Creación de Contenido

**Tip 1**: Sé específico con los estilos
```
❌ "Crea una página bonita"
✅ "Crea una página con gradiente azul-morado, tipografía moderna (Segoe UI), 
    y animaciones suaves en los elementos"
```

**Tip 2**: Pide componentes reutilizables
```
"Crea un header.html que pueda incluir en todas las páginas con:
- Logo
- Menú de navegación
- Botón de contacto"
```

**Tip 3**: Usa referencias visuales
```
"Crea una página similar a la landing de Stripe, pero con colores verdes"
```

---

### 🚀 Despliegue

**Tip 4**: Usa puertos diferentes para versiones
```
"Despliega la versión actual en 8080 y la experimental en 8081"
```

**Tip 5**: Verifica antes de compartir
```
Antes de compartir la URL con alguien:
1. "¿Está activo el servidor?"
2. "Lista los archivos HTML"
3. Verifica en tu navegador
```

---

### 🔍 Debugging

**Tip 6**: Lista archivos frecuentemente
```
Si algo no se ve bien:
1. "Lista los archivos HTML"
2. Verifica que el archivo correcto existe
3. Verifica la fecha de modificación
```

**Tip 7**: Detén y reinicia si hay problemas
```
"Detén el servidor, luego despliégalo nuevamente"
```

---

### 💾 Organización

**Tip 8**: Usa nombres descriptivos
```
✅ about-me.html, project-portfolio.html, contact-form.html
❌ page1.html, page2.html, test.html
```

**Tip 9**: Crea un index.html maestro
```
"Crea un index.html que sirva como directorio de todas mis páginas de prueba"
```

---

## Solución de Problemas

### Problema: "No puedo acceder a localhost:8080"

**Diagnóstico**:
```
1. "¿Está activo el servidor?"
2. Verifica en tu navegador: http://localhost:8080
3. Revisa que Docker Desktop esté corriendo
```

**Solución**:
```
Si el servidor no está activo:
- "Despliega el servidor"

Si Docker no está corriendo:
- Inicia Docker Desktop manualmente
- Espera que esté "Running"
- "Despliega el servidor"
```

---

### Problema: "Veo el index de Nginx, no mi HTML"

**Causa**: No hay archivo `index.html` en el directorio `www/`.

**Solución**:
```
1. "Lista los archivos HTML"
2. Si no hay index.html:
   - "Crea un index.html con contenido de bienvenida"
3. Refresca el navegador
```

---

### Problema: "Los cambios no se reflejan"

**Solución**:
```
1. Refresca el navegador con Ctrl+F5 (fuerza recarga sin caché)
2. "¿Cuándo fue modificado index.html?"
3. Verifica que Claude modificó el archivo correcto
```

---

### Problema: "Puerto 8080 ya está en uso"

**Solución A**: Usa otro puerto
```
"Despliega el servidor en el puerto 8081"
```

**Solución B**: Detén el proceso que usa 8080
```powershell
# Windows
netstat -ano | findstr :8080
taskkill /PID <PID> /F
```

---

### Problema: "Container name already in use"

**Solución**:
```
"Detén el servidor"
"Despliega el servidor"
```

O manualmente:
```bash
docker stop mcp-web-server
docker rm mcp-web-server
```

---

## Comandos Útiles de Docker

### Ver contenedores activos
```bash
docker ps
```

### Ver todos los contenedores (activos e inactivos)
```bash
docker ps -a
```

### Ver logs del servidor
```bash
docker logs mcp-web-server
```

### Acceder al contenedor
```bash
docker exec -it mcp-web-server sh
```

### Ver uso de recursos
```bash
docker stats mcp-web-server
```

---

## Próximos Pasos

Ahora que dominas el uso básico:

1. **Experimenta**: Crea diferentes tipos de páginas
2. **Aprende**: Revisa la [Arquitectura](ARCHITECTURE.md)
3. **Contribuye**: Comparte tus creaciones
4. **Expande**: Crea tus propias herramientas MCP

---

## Recursos Adicionales

- [Ejemplos HTML en /examples](../examples/)
- [Documentación MCP](https://modelcontextprotocol.io)
- [Guía de Instalación](INSTALLATION.md)
- [Arquitectura del Proyecto](ARCHITECTURE.md)

---

**¡Happy Coding!** 🎉

Recuerda: La mejor forma de aprender es experimentando. No tengas miedo de probar cosas nuevas.