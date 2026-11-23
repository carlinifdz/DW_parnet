# Ejecución ----------------------------------------------------------------------------------------------------------------------------------------------------------

Ejecuta el proyecto con `python manage.py runserver`
Entra a `http://127.0.0.1:8000/`
Panel administrativo de Django: `http://127.0.0.1:8000/admin/`


# Intrucciones -------------------------------------------------------------------------------------------------------------------------------------------------------

1. Ejecutar db.sql en mysql
2. Crear entorno virtual con python `-m venv venv` 
3. Activalo el entorno virtual con `.\venv\Scripts\Activate.ps1`
4. Instala los las librerias requeridas con `python -m pip install -r requirements.txt`
5. En la raiz del proyecto, crea el proyecto Django con `django-admin startproject config .`
6. Ejecuta las siguientes lineas de codigo:
python manage.py startapp core
python manage.py startapp productos
python manage.py startapp servicios
python manage.py startapp comunicacion
python manage.py startapp gestion

7. Crea un usuario de MySQL con el siguiente scripts, recuerda cambiar la contraseña:
CREATE USER 'parnet_app'@'localhost'
IDENTIFIED BY 'CAMBIAR_POR_CONTRASENA_SEGURA';

GRANT ALL PRIVILEGES
ON parnet_ingenieria.*
TO 'parnet_app'@'localhost';

FLUSH PRIVILEGES;

8. Copia y pega el archivo .env.example y renombralo a .env,
crea una clave segura con `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"` 
y ponla en el campo `DJANGO_SECRET_KEY=`, y pon tu contraseña en el campo `DB_PASSWORD=`

9. comprueba la conexion a SQL con `python manage.py check`, si todo está bien debe salir este mensaje `System check identified no issues (0 silenced).`
10. Ejecuta `python manage.py shell -c "from django.db import connection; connection.ensure_connection(); print('Conexion exitosa con MySQL')"`
11. Crea las migraciones de django `python manage.py migrate`
12. Crea tu  adminsitrador con `python manage.py createsuperuser`
13. Ejecuta el proyecto con `python manage.py runserver`