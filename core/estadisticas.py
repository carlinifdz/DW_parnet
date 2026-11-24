from datetime import timedelta
from hashlib import sha256

from django.utils import timezone

from core.patrones.singleton import ConfiguracionSistema

from .models import UsuarioConectado

# =========================================
# REGISTRAR ACTIVIDAD DE UNA SESION
# =========================================

def registrar_usuario_conectado(request):

    if not request.session.session_key:

        request.session.create()

    clave_sesion = request.session.session_key

    id_sesion = sha256(
        clave_sesion.encode("utf-8")
    ).hexdigest()

    UsuarioConectado.objects.update_or_create(

        id_sesion=id_sesion,

        defaults={
            "ultima_actividad": timezone.now()
        }

    )

    return id_sesion

# =========================================
# CONSULTAR USUARIOS ACTIVOS
# =========================================

def contar_usuarios_conectados():

    configuracion = ConfiguracionSistema()

    tiempo_limite = timezone.now() - timedelta(

        minutes=configuracion.tiempo_usuario_activo

    )

    return UsuarioConectado.objects.filter(

        ultima_actividad__gte=tiempo_limite

    ).count()

# =========================================
# LIMPIAR SESIONES INACTIVAS
# =========================================

def limpiar_usuarios_inactivos():

    configuracion = ConfiguracionSistema()

    tiempo_limite = timezone.now() - timedelta(

        minutes=configuracion.tiempo_usuario_activo

    )

    eliminados, _ = UsuarioConectado.objects.filter(

        ultima_actividad__lt=tiempo_limite

    ).delete()

    return eliminados