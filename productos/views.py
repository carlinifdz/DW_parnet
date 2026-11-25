from django.core.paginator import Paginator
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views.decorators.http import require_GET

from core.patrones.singleton import ConfiguracionSistema

from .consultas import categorias_activas, productos_activos
from .models import Producto
from .pdf import generar_ficha_tecnica_pdf


# =========================================
# SERIALIZACION AUXILIAR PARA API REST
# =========================================

def _serializar_producto(producto):
    categoria = getattr(producto, "categoria", None)

    return {
        "id_producto": producto.id_producto,
        "codigo": producto.codigo,
        "nombre": producto.nombre,
        "descripcion": producto.descripcion or "",
        "marca": producto.marca or "",
        "modelo": producto.modelo or "",
        "precio": float(producto.precio),
        "stock": producto.stock,
        "estatus": producto.estatus,
        "imagen": producto.imagen_url,
        "ficha_tecnica": producto.ficha_tecnica or "",
        "categoria": {
            "id_categoria": (
                categoria.id_categoria if categoria else None
            ),
            "nombre": (
                categoria.nombre if categoria else ""
            ),
        },
        "url_detalle": reverse(
            "productos:detalle",
            kwargs={"id_producto": producto.id_producto}
        ),
        "url_ficha_pdf": reverse(
            "productos:ficha_pdf",
            kwargs={"id_producto": producto.id_producto}
        ),
    }


def _serializar_categoria(categoria):
    return {
        "id_categoria": categoria.id_categoria,
        "nombre": categoria.nombre,
        "descripcion": categoria.descripcion or "",
    }


# =========================================
# CATALOGO GENERAL DE PRODUCTOS
# =========================================

def listado_productos(request):

    configuracion = ConfiguracionSistema()

    busqueda = request.GET.get("q", "").strip()
    categoria_param = request.GET.get("categoria", "").strip()

    categoria_actual = None
    if categoria_param:
        try:
            categoria_actual = int(categoria_param)
        except ValueError:
            categoria_actual = None

    categorias = categorias_activas()

    productos = productos_activos(
        busqueda=busqueda,
        id_categoria=categoria_actual
    )

    paginador = Paginator(
        productos,
        configuracion.registros_por_pagina
    )

    numero_pagina = request.GET.get("page")

    pagina = paginador.get_page(numero_pagina)

    contexto = {
        "pagina": pagina,
        "categorias": categorias,
        "busqueda": busqueda,
        "categoria_actual": categoria_actual,
    }

    return render(
        request,
        "productos/listado.html",
        contexto
    )


# =========================================
# DETALLE DE PRODUCTO
# =========================================

def detalle_producto(request, id_producto):

    producto = get_object_or_404(
        Producto.objects.select_related("categoria"),
        id_producto=id_producto,
        activo=True,
        categoria__activo=True
    )

    contexto = {
        "producto": producto,
    }

    return render(
        request,
        "productos/detalle.html",
        contexto
    )


# =========================================
# DESCARGA DE FICHA TECNICA EN PDF
# =========================================

@require_GET
def ficha_tecnica_pdf(request, id_producto):

    producto = get_object_or_404(
        Producto.objects.select_related("categoria"),
        id_producto=id_producto,
        activo=True,
        categoria__activo=True
    )

    contenido_pdf = generar_ficha_tecnica_pdf(producto)

    codigo_limpio = (
        (producto.codigo or f"prod-{producto.id_producto}")
        .replace(" ", "_")
        .lower()
    )
    nombre_archivo = f"ficha_tecnica_{codigo_limpio}.pdf"

    respuesta = HttpResponse(
        contenido_pdf,
        content_type="application/pdf"
    )
    respuesta["Content-Disposition"] = (
        f'attachment; filename="{nombre_archivo}"'
    )

    return respuesta


# =========================================
# API REST DE PRODUCTOS Y CATEGORIAS
# =========================================

@require_GET
def api_productos(request):

    busqueda = request.GET.get("q", "").strip()
    categoria_param = request.GET.get("categoria", "").strip()

    categoria_id = None
    if categoria_param:
        try:
            categoria_id = int(categoria_param)
        except ValueError:
            categoria_id = None

    productos = list(
        productos_activos(
            busqueda=busqueda,
            id_categoria=categoria_id
        )
    )

    datos = {
        "total": len(productos),
        "resultados": [
            _serializar_producto(producto)
            for producto in productos
        ],
    }

    return JsonResponse(datos)


@require_GET
def api_detalle_producto(request, id_producto):

    producto = get_object_or_404(
        Producto.objects.select_related("categoria"),
        id_producto=id_producto,
        activo=True,
        categoria__activo=True
    )

    return JsonResponse(
        _serializar_producto(producto)
    )


@require_GET
def api_categorias(request):

    categorias = list(categorias_activas())

    datos = {
        "total": len(categorias),
        "resultados": [
            _serializar_categoria(categoria)
            for categoria in categorias
        ],
    }

    return JsonResponse(datos)
