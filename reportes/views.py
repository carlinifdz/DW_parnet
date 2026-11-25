from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_GET

from gestion.autenticacion.permisos import administrador_requerido
from productos.consultas import categorias_activas

from .consultas import (
    obtener_dashboard_productos,
    obtener_dashboard_servicios,
    obtener_reporte_inventario,
    obtener_sugerencias_reporte,
    resumen_inventario,
)
from .exportacion import (
    generar_inventario_excel,
    generar_inventario_pdf,
    generar_sugerencias_excel,
    generar_sugerencias_pdf,
)


MIME_XLSX = (
    "application/vnd.openxmlformats-officedocument."
    "spreadsheetml.sheet"
)


# =========================================
# PANEL PRINCIPAL DE REPORTES Y DASHBOARDS
# =========================================

@administrador_requerido
@require_GET
def panel_reportes(request):

    productos = obtener_reporte_inventario()
    metricas = resumen_inventario(productos)

    sugerencias = obtener_sugerencias_reporte()
    datos_servicios = obtener_dashboard_servicios()
    datos_productos = obtener_dashboard_productos()

    total_solicitudes = sum(
        item["total"] for item in datos_servicios
    )

    max_servicios = max(
        (item["total"] for item in datos_servicios),
        default=1
    ) or 1
    for item in datos_servicios:
        item["porcentaje"] = round(
            (item["total"] / max_servicios) * 100
        )

    max_productos = max(
        (item["total"] for item in datos_productos),
        default=1
    ) or 1
    for item in datos_productos:
        item["porcentaje"] = round(
            (item["total"] / max_productos) * 100
        )

    contexto = {
        "metricas": metricas,
        "total_sugerencias": len(sugerencias),
        "total_solicitudes": total_solicitudes,
        "dashboard_servicios": datos_servicios,
        "dashboard_productos": datos_productos,
    }

    return render(
        request,
        "reportes/panel.html",
        contexto
    )


# =========================================
# REPORTE GENERAL DE INVENTARIO (10.1, 10.2)
# =========================================

@administrador_requerido
@require_GET
def reporte_inventario(request):

    estatus_filtro = request.GET.get("estatus", "").strip()
    categoria_param = request.GET.get("categoria", "").strip()
    busqueda = request.GET.get("q", "").strip()

    categoria_actual = None
    if categoria_param:
        try:
            categoria_actual = int(categoria_param)
        except ValueError:
            categoria_actual = None

    productos = obtener_reporte_inventario(
        estatus=estatus_filtro,
        id_categoria=categoria_actual,
        busqueda=busqueda
    )

    metricas = resumen_inventario(productos)
    categorias = categorias_activas()

    contexto = {
        "productos": productos,
        "metricas": metricas,
        "categorias": categorias,
        "estatus_actual": estatus_filtro,
        "categoria_actual": categoria_actual,
        "busqueda": busqueda,
    }

    return render(
        request,
        "reportes/inventario.html",
        contexto
    )


# =========================================
# EXPORTACION DE INVENTARIO (10.3)
# =========================================

@administrador_requerido
@require_GET
def exportar_inventario_pdf(request):

    estatus_filtro = request.GET.get("estatus", "").strip()
    categoria_param = request.GET.get("categoria", "").strip()
    busqueda = request.GET.get("q", "").strip()

    productos = obtener_reporte_inventario(
        estatus=estatus_filtro,
        id_categoria=categoria_param or None,
        busqueda=busqueda
    )

    contenido = generar_inventario_pdf(productos)

    respuesta = HttpResponse(
        contenido,
        content_type="application/pdf"
    )
    respuesta["Content-Disposition"] = (
        'attachment; filename="reporte_inventario_parnet.pdf"'
    )

    return respuesta


@administrador_requerido
@require_GET
def exportar_inventario_excel(request):

    estatus_filtro = request.GET.get("estatus", "").strip()
    categoria_param = request.GET.get("categoria", "").strip()
    busqueda = request.GET.get("q", "").strip()

    productos = obtener_reporte_inventario(
        estatus=estatus_filtro,
        id_categoria=categoria_param or None,
        busqueda=busqueda
    )

    contenido = generar_inventario_excel(productos)

    respuesta = HttpResponse(
        contenido,
        content_type=MIME_XLSX
    )
    respuesta["Content-Disposition"] = (
        'attachment; filename="reporte_inventario_parnet.xlsx"'
    )

    return respuesta


# =========================================
# EXPORTACION DE SUGERENCIAS (10.4, 10.5)
# =========================================

@administrador_requerido
@require_GET
def exportar_sugerencias_excel(request):

    sugerencias = obtener_sugerencias_reporte()
    contenido = generar_sugerencias_excel(sugerencias)

    respuesta = HttpResponse(
        contenido,
        content_type=MIME_XLSX
    )
    respuesta["Content-Disposition"] = (
        'attachment; filename="reporte_sugerencias_parnet.xlsx"'
    )

    return respuesta


@administrador_requerido
@require_GET
def exportar_sugerencias_pdf(request):

    sugerencias = obtener_sugerencias_reporte()
    contenido = generar_sugerencias_pdf(sugerencias)

    respuesta = HttpResponse(
        contenido,
        content_type="application/pdf"
    )
    respuesta["Content-Disposition"] = (
        'attachment; filename="reporte_sugerencias_parnet.pdf"'
    )

    return respuesta


# =========================================
# DASHBOARDS DE SERVICIOS Y PRODUCTOS (10.6, 10.7)
# =========================================

@administrador_requerido
@require_GET
def dashboard_servicios(request):

    datos_servicios = obtener_dashboard_servicios()
    total_solicitudes = sum(
        item["total"] for item in datos_servicios
    )

    max_total = max(
        (item["total"] for item in datos_servicios),
        default=1
    ) or 1

    for item in datos_servicios:
        item["porcentaje"] = round(
            (item["total"] / max_total) * 100
        )

    contexto = {
        "dashboard_servicios": datos_servicios,
        "total_solicitudes": total_solicitudes,
    }

    return render(
        request,
        "reportes/dashboard_servicios.html",
        contexto
    )


@administrador_requerido
@require_GET
def dashboard_productos(request):

    datos_productos = obtener_dashboard_productos()
    total_productos = sum(
        item["total"] for item in datos_productos
    )

    max_total = max(
        (item["total"] for item in datos_productos),
        default=1
    ) or 1

    for item in datos_productos:
        item["porcentaje"] = round(
            (item["total"] / max_total) * 100
        )

    contexto = {
        "dashboard_productos": datos_productos,
        "total_productos": total_productos,
    }

    return render(
        request,
        "reportes/dashboard_productos.html",
        contexto
    )


@administrador_requerido
@require_GET
def api_dashboards(request):

    datos_servicios = obtener_dashboard_servicios()
    datos_productos = obtener_dashboard_productos()

    return JsonResponse({
        "servicios": {
            "etiquetas": [
                item["servicio"] for item in datos_servicios
            ],
            "valores": [
                item["total"] for item in datos_servicios
            ],
            "resultados": datos_servicios,
        },
        "productos": {
            "etiquetas": [
                item["categoria"] for item in datos_productos
            ],
            "valores": [
                item["total"] for item in datos_productos
            ],
            "resultados": datos_productos,
        },
    })
