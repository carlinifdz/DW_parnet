from core.patrones.singleton import ConfiguracionSistema


def configuracion_global(request):

    configuracion = ConfiguracionSistema()

    return {
        "configuracion_sistema": (
            configuracion.obtener_configuracion()
        )
    }