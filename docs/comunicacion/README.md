# Módulo de Comunicación: Contacto y Sugerencias (Parte 7)

## Descripción
Implementa:
1. **Formulario de contacto por correo electrónico** (`/comunicacion/`) despachado a través de la clase `ServicioCorreo` hacia el correo configurado en el Singleton `ConfiguracionSistema`.
2. **Buzón interno de sugerencias** (`/comunicacion/sugerencias/`) con validación en servidor, protección Google reCAPTCHA v2 (`crear_captcha()`) y almacenamiento mediante el ORM de Django en la tabla `sugerencias` (modelo `Sugerencia`).

## Rutas (`namespace = "comunicacion"`)
- `/comunicacion/` → `comunicacion:contacto`
- `/comunicacion/sugerencias/` → `comunicacion:sugerencias`

## Pruebas
```bash
python manage.py test comunicacion
```
