from functools import wraps
from urllib.parse import urlparse

from django.conf import settings
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.mixins import AccessMixin, PermissionRequiredMixin
from django.contrib.auth.views import redirect_to_login
from django.core.exceptions import PermissionDenied
from django.shortcuts import resolve_url


def es_administrador(usuario):
    """
    Determina si un usuario autenticado posee privilegios administrativos
    dentro del sistema utilizando la autenticación nativa de Django.
    """
    return bool(
        usuario
        and usuario.is_authenticated
        and usuario.is_active
        and (usuario.is_staff or usuario.is_superuser)
    )


def _redirigir_a_login(request, login_url=None, redirect_field_name=REDIRECT_FIELD_NAME):
    path = request.build_absolute_uri()
    resolved_login_url = resolve_url(login_url or settings.LOGIN_URL)
    login_scheme, login_netloc = urlparse(resolved_login_url)[:2]
    current_scheme, current_netloc = urlparse(path)[:2]
    if (not login_scheme or login_scheme == current_scheme) and (
        not login_netloc or login_netloc == current_netloc
    ):
        path = request.get_full_path()
    return redirect_to_login(path, resolved_login_url, redirect_field_name)


def administrador_requerido(
    function=None,
    redirect_field_name=REDIRECT_FIELD_NAME,
    login_url=None,
):
    """
    Decorador reutilizable para proteger vistas basadas en funciones.
    - Si el visitante no ha iniciado sesión, redirige a la página de login.
    - Si está autenticado pero no es administrador (is_staff), lanza 403.
    """

    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            usuario = getattr(request, "user", None)
            if not usuario or not usuario.is_authenticated:
                return _redirigir_a_login(request, login_url, redirect_field_name)
            if not es_administrador(usuario):
                raise PermissionDenied(
                    "No cuentas con permisos administrativos para acceder a esta sección."
                )
            return view_func(request, *args, **kwargs)

        return _wrapped_view

    if function:
        return decorator(function)
    return decorator


def permiso_requerido(permiso, login_url=None):
    """
    Decorador reutilizable que verifica que el usuario sea administrador
    y además posea el permiso o permisos indicados de Django.
    Si no ha iniciado sesión, redirige al login; si no tiene el permiso,
    responde con 403 PermissionDenied.
    """
    if isinstance(permiso, str):
        permisos = (permiso,)
    else:
        permisos = tuple(permiso)

    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            usuario = getattr(request, "user", None)
            if not usuario or not usuario.is_authenticated:
                return _redirigir_a_login(request, login_url)
            if not es_administrador(usuario) or not usuario.has_perms(permisos):
                raise PermissionDenied(
                    "No cuentas con los permisos necesarios para realizar esta operación."
                )
            return view_func(request, *args, **kwargs)

        return _wrapped_view

    return decorator


class AdministradorRequeridoMixin(AccessMixin):
    """
    Mixin POO reutilizable para proteger vistas basadas en clases (CBV)
    del panel administrativo.
    """

    def dispatch(self, request, *args, **kwargs):
        usuario = getattr(request, "user", None)
        if not usuario or not usuario.is_authenticated:
            return self.handle_no_permission()
        if not es_administrador(usuario):
            raise PermissionDenied(
                "No cuentas con permisos administrativos para acceder a esta sección."
            )
        return super().dispatch(request, *args, **kwargs)


class PermisoAdministrativoMixin(AdministradorRequeridoMixin, PermissionRequiredMixin):
    """
    Mixin POO que exige que el usuario sea administrador y además posea
    los permisos configurados en `permission_required`.
    """

    raise_exception = True
