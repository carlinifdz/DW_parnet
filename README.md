# ParNet Ingeniería

Aplicación web académica para una empresa de ingeniería, orientada a la consulta de productos, solicitud de servicios y administración de información. El proyecto utiliza Python, Django y MySQL, con una interfaz responsiva.

## Tecnologías

- Python 3.12 o 3.13.
- Django 5.2 LTS.
- MySQL 8.0.16 o superior (preferentemente 8.4 LTS).
- HTML5, CSS3, Bootstrap y JavaScript.
- Django ORM, Git y GitHub.

## Estado del proyecto

Actualmente se cuenta con el script inicial de MySQL. La configuración de Django y los módulos funcionales se desarrollarán por etapas. Este documento describe la configuración inicial propuesta; los archivos indicados deberán incorporarse al repositorio durante esta etapa.

## Estructura propuesta

```text
parnet-ingenieria/
├── config/                  # Configuración de Django
├── core/                    # Inicio y funciones generales
├── productos/               # Catálogo e inventario
├── servicios/               # Solicitudes de servicios
├── comunicacion/            # Contacto y sugerencias
├── gestion/                 # Administración y reportes
├── templates/               # Plantillas HTML compartidas
├── static/                  # CSS, JavaScript e imágenes estáticas
├── media/                   # Archivos cargados por usuarios
├── database/
│   └── parnet_ingenieria.sql
├── docs/                    # Documentación del proyecto
├── .env.example
├── .gitignore
├── manage.py
├── requirements.txt
└── README.md
```

## Requisitos previos

Instalar Python, MySQL Server, Git y, opcionalmente, MySQL Workbench y Visual Studio Code. Comprobar las instalaciones:

```bash
python --version
git --version
mysql --version
```

En Linux o macOS puede ser necesario utilizar `python3` en lugar de `python`. Si el cliente MySQL no está en PATH, se puede utilizar Workbench para importar el SQL.

## 1. Inicialización del repositorio (una sola vez)

Esta sección es para el integrante encargado de crear la estructura inicial. Los demás deben seguir la sección de instalación local una vez publicados los archivos.

Desde la raíz del repositorio, crear el entorno virtual:

```bash
python -m venv .venv
```

Activarlo en Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

En Linux o macOS:

```bash
source .venv/bin/activate
```

Crear `requirements.txt` con el siguiente contenido:

```text
Django>=5.2,<5.3
mysqlclient>=2.2.1,<3
python-dotenv>=1.0,<2
```

Instalar dependencias y crear el proyecto:

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m django startproject config .
python manage.py startapp core
python manage.py startapp productos
python manage.py startapp servicios
python manage.py startapp comunicacion
python manage.py startapp gestion
```

Crear las carpetas `templates`, `static`, `media`, `database` y `docs`. Colocar el script SQL existente en `database/parnet_ingenieria.sql`.

Si `mysqlclient` necesita compilarse en Ubuntu/Debian, instalar previamente `python3-dev`, `default-libmysqlclient-dev`, `build-essential` y `pkg-config`. En macOS puede requerir las bibliotecas cliente de MySQL y `pkg-config`.

## 2. Instalación local para cada integrante

```bash
git clone <URL_DEL_REPOSITORIO>
cd <CARPETA_DEL_REPOSITORIO>
python -m venv .venv
```

Activar el entorno virtual según el sistema operativo, como se indica en la sección anterior, y ejecutar:

```bash
python -m pip install -r requirements.txt
```

## 3. Configuración de MySQL

Abrir MySQL Workbench, conectarse al servidor local y ejecutar `database/parnet_ingenieria.sql` una sola vez en una base nueva. El script crea la base `parnet_ingenieria`, sus tablas, vistas y datos de prueba. No volver a ejecutar los INSERT de prueba en una base ya poblada.

Alternativamente, desde una terminal que admita redirección (CMD, Bash o Zsh):

```bash
mysql -u root -p < database/parnet_ingenieria.sql
```

Crear un usuario exclusivo para la aplicación desde una conexión con permisos administrativos:

```sql
CREATE USER 'parnet_app'@'localhost'
IDENTIFIED BY 'REEMPLAZAR_POR_CONTRASENA_SEGURA';
GRANT ALL PRIVILEGES ON parnet_ingenieria.*
TO 'parnet_app'@'localhost';
```

Estos permisos se destinan únicamente al entorno local de desarrollo y permiten ejecutar migraciones. En producción se deberán separar y limitar los permisos.

## 4. Variables de entorno

Crear y publicar un archivo `.env.example` sin credenciales reales:

```dotenv
DJANGO_SECRET_KEY=
DJANGO_DEBUG=True
DB_NAME=parnet_ingenieria
DB_USER=parnet_app
DB_PASSWORD=
DB_HOST=localhost
DB_PORT=3306
```

Cada integrante debe copiarlo como `.env` (PowerShell: `Copy-Item .env.example .env`; Bash: `cp .env.example .env`) y completar su contraseña local y su clave secreta. Generar una clave con:

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Nunca subir `.env` ni contraseñas al repositorio.

## 5. Configuración de Django

El encargado de la inicialización deberá modificar `config/settings.py`. Agregar los imports y cargar las variables después de la declaración de `BASE_DIR`:

```python
import os
from dotenv import load_dotenv

load_dotenv(BASE_DIR / '.env')
```

Sustituir las definiciones existentes de `SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS` y `DATABASES`:

```python
SECRET_KEY = os.environ['DJANGO_SECRET_KEY']
DEBUG = os.getenv('DJANGO_DEBUG', 'False').lower() == 'true'
ALLOWED_HOSTS = ['localhost', '127.0.0.1']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.environ['DB_NAME'],
        'USER': os.environ['DB_USER'],
        'PASSWORD': os.environ['DB_PASSWORD'],
        'HOST': os.getenv('DB_HOST', 'localhost'),
        'PORT': os.getenv('DB_PORT', '3306'),
        'OPTIONS': {'charset': 'utf8mb4'},
    }
}
```

Agregar a `INSTALLED_APPS` las aplicaciones locales, conservando las que Django incluye por defecto:

```python
'core',
'productos',
'servicios',
'comunicacion',
'gestion',
```

En la configuración existente de `TEMPLATES`, cambiar `DIRS` a `[BASE_DIR / 'templates']`. Agregar o actualizar:

```python
LANGUAGE_CODE = 'es-mx'
TIME_ZONE = 'America/Monterrey'
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
```

## 6. Integración de la base existente con ORM

Las tablas del catálogo y demás módulos ya se crean mediante el SQL. No deben crearse nuevamente mediante migraciones automáticas. Para obtener un borrador de sus modelos:

```bash
python manage.py inspectdb categorias_productos productos areas_servicios solicitudes_servicios sugerencias noticias clientes slider visitas usuarios_conectados
```

Revisar la salida y distribuir los modelos en las aplicaciones correspondientes. Conservar `db_table` y `managed = False` para las tablas gestionadas por el script SQL. Revisar tipos, claves y relaciones antes de utilizar los modelos. Los cambios futuros de estas tablas deberán coordinarse mediante scripts SQL versionados mientras permanezcan sin gestión de migraciones de Django.

Para la autenticación se utilizará inicialmente el sistema nativo de Django (`auth_user`, permisos y sesiones). La tabla `administradores` del SQL queda reservada y no será una segunda fuente de credenciales. Esta decisión deberá reflejarse en el modelo físico final; si se requiere usar esa tabla se diseñará un modelo de usuario personalizado antes de ejecutar la primera migración.

## 7. Ejecutar el proyecto

```bash
python manage.py check
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Las migraciones iniciales crean las tablas internas de Django, no sustituyen el script SQL. Crear el superusuario es una operación local; no compartir sus credenciales.

- Sitio local: http://127.0.0.1:8000/
- Administración de Django: http://127.0.0.1:8000/admin/

El sitio público inicialmente puede mostrar la página predeterminada de Django. El servidor de desarrollo no debe utilizarse en producción.

## 8. Archivos ignorados por Git

Crear `.gitignore` antes del primer commit:

```gitignore
.venv/
venv/
__pycache__/
*.py[cod]
.env
.env.*
!.env.example
media/
staticfiles/
*.log
.vscode/
.idea/
.DS_Store
Thumbs.db
```

Los scripts SQL, modelos, migraciones, plantillas, archivos estáticos y documentación sí deben versionarse. Las imágenes de demostración necesarias para el sitio pueden almacenarse en `static/` o distribuirse mediante un procedimiento documentado.

## 9. Flujo de trabajo con Git

La rama `main` debe contener código estable. Cada integrante trabajará en una rama propia por funcionalidad. Ejemplo:

```bash
git switch main
git pull origin main
git switch -c feature/catalogo-productos
# Realizar cambios y comprobarlos antes del commit
git status
git add productos/
git commit -m "Implementar estructura del catálogo de productos"
git push -u origin feature/catalogo-productos
```

Abrir un pull request para que otro integrante revise los cambios antes de integrarlos a `main`. No subir credenciales, entornos virtuales ni datos personales. Avisar al equipo antes de modificar el esquema SQL o las dependencias.

## 10. Módulos pendientes

- Diseño general conforme a la referencia de Photoshop y página principal con slider.
- Catálogo, búsqueda, imágenes y ficha técnica en PDF.
- Solicitudes de servicios y sugerencias con CAPTCHA; contacto por correo.
- Autenticación y administración de productos, noticias y sugerencias paginadas.
- Reportes de inventario, exportación de sugerencias a Excel y PDF, y dos dashboards.
- Noticias dinámicas, clientes con enlaces, visitas y usuarios activos.
- API REST, patrón Singleton, integración multimedia y video de 2 a 4 minutos.
- Pruebas, compatibilidad de navegadores, implementación y documentación.

## 11. Documentación y acuerdos del equipo

Mantener en `docs/` el análisis de requerimientos, arquitectura, modelo físico de base de datos, programación, pruebas, implementación y diagrama de Gantt con responsables y tiempos. Actualizar el Gantt desde el inicio del desarrollo.

Usar programación orientada a objetos, ORM y buenas prácticas de organización. No utilizar PHP. Validar formularios en el servidor, proteger rutas administrativas y almacenar contraseñas mediante hashes seguros.

## Verificación de la configuración inicial

- [ ] El repositorio puede clonarse e instalar sus dependencias.
- [ ] La base de datos y los datos de prueba se importan correctamente.
- [ ] Las variables de entorno locales no se incluyen en Git.
- [ ] `python manage.py check` finaliza sin errores.
- [ ] Las migraciones internas de Django se ejecutan correctamente.
- [ ] El servidor local inicia y permite acceder al panel de administración.
- [ ] El equipo acuerda la distribución de módulos y actualiza el Gantt.
