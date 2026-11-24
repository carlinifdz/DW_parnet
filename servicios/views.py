from django.shortcuts import render, get_object_or_404
from .models import AreaServicio
from .consultas import areas_activas

# =========================================
# LISTADO GENERAL DE SERVICIOS
# =========================================

def listado_servicios(request):

    areas = areas_activas()

    contexto = {
        "areas": areas,
    }

    return render(
        request,
        "servicios/listado.html",
        contexto
    )

# =========================================
# DETALLE DE AREA DE SERVICIO
# =========================================

def detalle_area(request, id_area):

    area = get_object_or_404(
        AreaServicio,
        id_area=id_area,
        activo=True
    )

    contexto = {
        "area": area,
    }

    return render(
        request,
        "servicios/detalle.html",
        contexto
    )