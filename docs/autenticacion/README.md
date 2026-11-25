# Módulo de Autenticación Administrativa (Parte 8)

## Descripción
Implementa el control de acceso para administradores de **ParNet Ingeniería** utilizando el sistema de autenticación nativo de Django (`django.contrib.auth`), validación de rol administrativo (`is_staff` / `is_superuser`) y protección con Google reCAPTCHA v2 (`crear_captcha()`).

## Rutas disponibles (`namespace = "autenticacion"`)
- **Inicio de sesión:** `/acceso/iniciar-sesion/` → `{% url 'autenticacion:iniciar_sesion' %}`
- **Cierre de sesión (solo POST):** `/acceso/cerrar-sesion/` → `{% url 'autenticacion:cerrar_sesion' %}`

## Protección reutilizable para vistas del Panel Administrativo (Parte 9)

Desde `gestion.autenticacion.permisos` se exportan decoradores y mixins listos para proteger cualquier vista privada:

### 1. Vistas basadas en funciones (FBV)
```python
from gestion.autenticacion.permisos import administrador_requerido, permiso_requerido

@administrador_requerido
def panel_principal(request):
    ...

@permiso_requerido("productos.change_producto")
def editar_producto(request, id_producto):
    ...
```

### 2. Vistas basadas en clases (CBV - POO)
```python
from django.views.generic import ListView
from gestion.autenticacion.permisos import (
    AdministradorRequeridoMixin,
    PermisoAdministrativoMixin,
)

class ProductoAdminListView(AdministradorRequeridoMixin, ListView):
    ...

class ProductoAdminDeleteView(PermisoAdministrativoMixin, DeleteView):
    permission_required = "productos.delete_producto"
```

## Pruebas
```bash
python manage.py test gestion.test_autenticacion
```
