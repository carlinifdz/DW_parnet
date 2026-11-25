# Módulo de Comunicación: Contacto y Sugerencias (Parte 7)

## Descripción
Implementa:
1. **Formulario de contacto por correo electrónico** (`/comunicacion/`) despachado a través de la clase `ServicioCorreo` hacia el correo configurado en el Singleton `ConfiguracionSistema`.
2. **Buzón interno de sugerencias** (`/comunicacion/sugerencias/`) con validación en servidor, protección Google reCAPTCHA v2 (`crear_captcha()`) y almacenamiento mediante el ORM de Django en la tabla `sugerencias` (modelo `Sugerencia`).

## Rutas (`namespace = "comunicacion"`)
- `/comunicacion/` → `comunicacion:contacto`
- `/comunicacion/sugerencias/` → `comunicacion:sugerencias`

## Variables de entorno para correo SMTP (Gmail)
En el archivo `.env` se configuran las credenciales de despacho SMTP:
```env
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=julioperezr2004@gmail.com
EMAIL_HOST_PASSWORD=<contraseña_de_aplicacion_google>
DEFAULT_FROM_EMAIL=julioperezr2004@gmail.com
CORREO_CONTACTO=julioperezr2004@gmail.com
```

## Pruebas
```bash
python manage.py test comunicacion
```
