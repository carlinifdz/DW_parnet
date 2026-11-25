import logging

from django.shortcuts import (
    render,
    get_object_or_404,
    redirect,
)

from django.views.decorators.http import (
    require_http_methods,
    require_GET,
)

from django.views.decorators.cache import never_cache

from django.db import transaction, DatabaseError

from django.utils import timezone

from .models import AreaServicio

from .consultas import areas_activas

from .forms import SolicitudServicioForm


# =========================================
# REGISTRO DE ERRORES
# =========================================

logger = logging.getLogger(__name__)


# =========================================
# LISTADO DE SERVICIOS
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


# =========================================
# FORMULARIO DE SOLICITUD
# =========================================

@require_http_methods(["GET", "POST"])
def solicitar_servicio(request, id_area=None):

    area_seleccionada = None

    datos_iniciales = {}


    # =========================================
    # SELECCION AUTOMATICA DEL AREA
    # =========================================

    if id_area is not None:

        area_seleccionada = get_object_or_404(

            AreaServicio,

            id_area=id_area,

            activo=True

        )

        datos_iniciales["area"] = (
            area_seleccionada.pk
        )


    # =========================================
    # PROCESAR FORMULARIO
    # =========================================

    if request.method == "POST":

        formulario = SolicitudServicioForm(
            request.POST
        )

        if formulario.is_valid():

            try:

                # Almacenar solicitud en MySQL

                with transaction.atomic():

                    solicitud = formulario.save(
                        commit=False
                    )

                    solicitud.estatus = "Pendiente"

                    solicitud.fecha_solicitud = (
                        timezone.now()
                    )

                    solicitud.save()


            except DatabaseError:

                logger.exception(
                    "Error al almacenar una solicitud "
                    "de servicio."
                )

                formulario.add_error(

                    None,

                    "No fue posible registrar tu solicitud. "
                    "Inténtalo nuevamente."

                )


            else:

                # Generar datos de confirmacion

                request.session["confirmacion_solicitud"] = {

                    "folio": (
                        f"SOL-{solicitud.pk:06d}"
                    ),

                    "area": solicitud.area.nombre,

                    "fecha": timezone.localtime(
                        solicitud.fecha_solicitud
                    ).strftime("%d/%m/%Y %H:%M"),

                    "estatus": solicitud.estatus,

                }

                # Redirigir a la confirmacion

                return redirect(
                    "servicios:confirmacion"
                )


    # =========================================
    # MOSTRAR FORMULARIO
    # =========================================

    else:

        formulario = SolicitudServicioForm(
            initial=datos_iniciales
        )


    contexto = {

        "formulario": formulario,

        "area_seleccionada": area_seleccionada,

    }

    return render(

        request,

        "servicios/solicitud.html",

        contexto

    )


# =========================================
# CONFIRMACION DE SOLICITUD
# =========================================

@never_cache
@require_GET
def confirmacion_solicitud(request):

    confirmacion = request.session.get(
        "confirmacion_solicitud"
    )

    # Impedir acceso sin una solicitud previa

    if not confirmacion:

        return redirect(
            "servicios:solicitar"
        )


    contexto = {

        "confirmacion": confirmacion,

    }

    return render(

        request,

        "servicios/confirmacion.html",

        contexto

    )