import os
from pathlib import Path
from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / ".env")


# Seguridad

SECRET_KEY = os.environ["DJANGO_SECRET_KEY"]

DEBUG = os.getenv("DJANGO_DEBUG", "False").lower() == "true"

ALLOWED_HOSTS = ["localhost", "127.0.0.1"]


# Aplicaciones

INSTALLED_APPS = [
    # Aplicaciones de Django
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django_recaptcha",

    # Aplicaciones de ParNet
    "core",
    "productos",
    "servicios",
    "comunicacion",
    "gestion",
]


# Middleware

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "core.middleware.RegistroVisitasMiddleware",
]


# Rutas principales

ROOT_URLCONF = "config.urls"


# Plantillas HTML

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",

        "DIRS": [
            BASE_DIR / "templates",
        ],

        "APP_DIRS": True,

        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",

                "core.context_processors.configuracion_global",
                "core.context_processors.noticias_sidebar",
                "core.context_processors.areas_sidebar",
                "core.context_processors.contador_visitas",
                "core.context_processors.contador_usuarios",
            ],
        },
    },
]


WSGI_APPLICATION = "config.wsgi.application"


# Base de datos MySQL

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",

        "NAME": os.environ["DB_NAME"],
        "USER": os.environ["DB_USER"],
        "PASSWORD": os.environ["DB_PASSWORD"],

        "HOST": os.getenv("DB_HOST", "localhost"),
        "PORT": os.getenv("DB_PORT", "3306"),

        "OPTIONS": {
            "charset": "utf8mb4",
            "init_command": "SET sql_mode='STRICT_TRANS_TABLES'",
        },
    }
}


# Validación de contraseñas

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "UserAttributeSimilarityValidator"
        ),
    },
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "MinimumLengthValidator"
        ),
    },
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "CommonPasswordValidator"
        ),
    },
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "NumericPasswordValidator"
        ),
    },
]


# Autenticación y correo electrónico

LOGIN_URL = "autenticacion:iniciar_sesion"
LOGIN_REDIRECT_URL = "core:inicio"
LOGOUT_REDIRECT_URL = "autenticacion:iniciar_sesion"

EMAIL_BACKEND = os.getenv(
    "EMAIL_BACKEND",
    "django.core.mail.backends.console.EmailBackend"
)
EMAIL_HOST = os.getenv("EMAIL_HOST", "localhost")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", "587"))
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD", "")
EMAIL_USE_TLS = os.getenv("EMAIL_USE_TLS", "True").lower() == "true"
DEFAULT_FROM_EMAIL = os.getenv(
    "DEFAULT_FROM_EMAIL",
    "no-reply@parnet.com.mx"
)


# Idioma y zona horaria

LANGUAGE_CODE = "es-mx"

TIME_ZONE = "America/Monterrey"

USE_I18N = True

USE_TZ = True


# Archivos estáticos

STATIC_URL = "/static/"

STATICFILES_DIRS = [
    BASE_DIR / "static",
]

STATIC_ROOT = BASE_DIR / "staticfiles"


# Archivos multimedia

MEDIA_URL = "/media/"

MEDIA_ROOT = BASE_DIR / "media"


# Llaves primarias predeterminadas

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# =========================================
# GOOGLE RECAPTCHA V2
# =========================================

RECAPTCHA_PUBLIC_KEY = os.getenv(
    "RECAPTCHA_PUBLIC_KEY"
)

RECAPTCHA_PRIVATE_KEY = os.getenv(
    "RECAPTCHA_PRIVATE_KEY"
)


# Permitir claves oficiales de prueba
# solamente durante el desarrollo local

if DEBUG:

    SILENCED_SYSTEM_CHECKS = [
        *globals().get("SILENCED_SYSTEM_CHECKS", []),
        "django_recaptcha.recaptcha_test_key_error",
    ]