from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator

from core.patrones.singleton import ConfiguracionSistema

from .models import Slider, Noticia, Cliente


# =========================================
# PAGINA PRINCIPAL
# =========================================

def inicio(request):

    sliders = Slider.objects.filter(
        activo=True
    ).exclude(
        imagen=""
    ).order_by(
        "orden",
        "id_slider"
    )

    contexto = {
        "sliders": sliders,
    }

    return render(
        request,
        "inicio.html",
        contexto
    )


# =========================================
# LISTADO DE NOTICIAS
# =========================================

def listado_noticias(request):

    configuracion = ConfiguracionSistema()

    noticias = Noticia.objects.filter(
        activo=True
    ).order_by(
        "-fecha_publicacion",
        "-id_noticia"
    )

    paginador = Paginator(
        noticias,
        configuracion.registros_por_pagina
    )

    numero_pagina = request.GET.get("page")

    pagina = paginador.get_page(numero_pagina)

    contexto = {
        "pagina": pagina,
    }

    return render(
        request,
        "noticias/listado.html",
        contexto
    )


# =========================================
# DETALLE DE NOTICIA
# =========================================

def detalle_noticia(request, id_noticia):

    noticia = get_object_or_404(
        Noticia,
        id_noticia=id_noticia,
        activo=True
    )

    contexto = {
        "noticia": noticia,
    }

    return render(
        request,
        "noticias/detalle.html",
        contexto
    )


# =========================================
# LISTADO DE CLIENTES
# =========================================

def listado_clientes(request):

    clientes = Cliente.objects.filter(
        activo=True
    ).order_by(
        "nombre",
        "id_cliente"
    )

    contexto = {
        "clientes": clientes,
    }

    return render(
        request,
        "clientes/listado.html",
        contexto
    )