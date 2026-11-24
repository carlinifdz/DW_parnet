from core.patrones.singleton import ConfiguracionSistema
from .models import Noticia


def configuracion_global(request):

    configuracion = ConfiguracionSistema()

    return {
        "configuracion_sistema": (
            configuracion.obtener_configuracion()
        )
    }


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