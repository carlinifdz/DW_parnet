from .models import Visita

from .estadisticas import registrar_usuario_conectado


# Aplicaciones publicas

NAMESPACES_PUBLICOS = {
    "core",
    "productos",
    "servicios",
    "comunicacion",
    "multimedia",
}

def es_pagina_publica(request):

    ruta = getattr(
        request,
        "resolver_match",
        None
    )

    if ruta is None:
        return False

    # Excluir la API de estadisticas

    if ruta.view_name == "core:api_estadisticas":
        return False

    return ruta.namespace in NAMESPACES_PUBLICOS


# =========================================
# MIDDLEWARE DE VISITAS Y ACTIVIDAD
# =========================================

class RegistroVisitasMiddleware:

    def __init__(self, get_response):

        self.get_response = get_response

    def __call__(self, request):

        response = self.get_response(request)

        # Excluir solicitudes distintas de GET

        if request.method != "GET":
            return response

        # Excluir paginas privadas y recursos

        if not es_pagina_publica(request):
            return response

        # Excluir respuestas fallidas

        if response.status_code != 200:
            return response

        # Comprobar el tipo de contenido

        tipo_contenido = response.get(
            "Content-Type",
            ""
        )

        if not tipo_contenido.startswith("text/html"):
            return response

        if response.streaming:
            return response

        # Registrar visita

        Visita.objects.create(
            pagina=request.path[:255]
        )

        # Registrar actividad del visitante

        registrar_usuario_conectado(request)

        return response