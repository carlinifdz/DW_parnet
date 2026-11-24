from core.patrones.singleton import ConfiguracionSistema
from servicios.consultas import areas_activas
from .models import Noticia, Visita
from .middleware import es_pagina_publica
from .estadisticas import contar_usuarios_conectados

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
# NOTICIAS
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

# =========================================
# CONTADOR DE VISITAS
# =========================================

def contador_visitas(request):

    if not es_pagina_publica(request):

        return {
            "total_visitas": 0
        }

    total = Visita.objects.count()

    if request.method == "GET":

        total += 1

    return {
        "total_visitas": total
    }

# =========================================
# CONTADOR DE USUARIOS CONECTADOS
# =========================================

def contador_usuarios(request):

    if not es_pagina_publica(request):

        return {
            "usuarios_conectados": 0
        }

    return {

        "usuarios_conectados": (
            contar_usuarios_conectados()
        )

    }