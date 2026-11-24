from core.patrones.singleton import ConfiguracionSistema
from servicios.consultas import areas_activas
from .models import Noticia

# =========================================
# CONFIGURACION GLOBAL
# =========================================

def configuracion_global(request):

    configuracion = ConfiguracionSistema()

    return {
        "configuracion_sistema": (
            configuracion.obtener_configuracion()
        )
    }

# =========================================
# NOTICIAS DE LA BARRA LATERAL
# =========================================

def noticias_sidebar(request):

    noticias = Noticia.objects.filter(
        activo=True
    ).order_by(
        "-fecha_publicacion",
        "-id_noticia"
    )[:2]

    return {
        "noticias_sidebar": noticias
    }

# =========================================
# AREAS DE SERVICIOS
# =========================================

def areas_sidebar(request):

    return {
        "areas_sidebar": areas_activas()
    }