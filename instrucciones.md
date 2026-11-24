# Ejecución ------------------------------------------------------------------------------------------------------------------------------------------------------------------

Ejecuta el proyecto con `python manage.py runserver`
Entra a `http://127.0.0.1:8000/`
Panel administrativo de Django: `http://127.0.0.1:8000/admin/`


# Intrucciones ---------------------------------------------------------------------------------------------------------------------------------------------------------------

1. Ejecutar db.sql en mysql
2. Crear entorno virtual con `python -m venv venv` 
3. Activa el entorno virtual con `.\venv\Scripts\Activate.ps1`
4. Instala los las librerias requeridas con `python -m pip install -r requirements.txt`
5. Crea un usuario de MySQL con el siguiente scripts, recuerda cambiar la contraseña:
CREATE USER 'parnet_app'@'localhost'
IDENTIFIED BY 'CAMBIAR_POR_CONTRASENA_SEGURA';

GRANT ALL PRIVILEGES
ON parnet_ingenieria.*
TO 'parnet_app'@'localhost';

FLUSH PRIVILEGES;

6. Copia y pega el archivo .env.example y renombralo a .env,
crea una clave segura con `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"` 
y ponla en el campo `DJANGO_SECRET_KEY=`, y pon tu contraseña en el campo `DB_PASSWORD=`

7. comprueba la conexion a Django con `python manage.py check`, si todo está bien debe salir este mensaje `System check identified no issues (0 silenced).`
8. Ejecuta `python manage.py shell -c "from django.db import connection; connection.ensure_connection(); print('Conexion exitosa con MySQL')"`

9. Aplica las migraciones de django `python manage.py migrate`
10. Crea tu adminsitrador con `python manage.py createsuperuser`
11. Ejecuta el proyecto con `python manage.py runserver`

# Explicaciones del codigo ---------------------------------------------------------------------------------------------------------------------------------------------------

1. ORM
Cada parte del ORM se encuentra dentro de cada nucleo de django en el archivo `models.py`

2. Singleton
Se encuentra dentro de `core/patrones/`

3. Pruebas
Se encuentran en `core/tests.py` y se ejecutan con `python manage.py test core servicios`

4. Contador de visitas
A través de `core/middleware.py`
