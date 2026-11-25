from django.urls import path

from . import views


app_name = "servicios"


urlpatterns = [

    path(
        "",
        views.listado_servicios,
        name="listado"
    ),

    path(
        "solicitar/",
        views.solicitar_servicio,
        name="solicitar"
    ),

    path(
        "solicitar/<int:id_area>/",
        views.solicitar_servicio,
        name="solicitar_area"
    ),

    path(
        "confirmacion/",
        views.confirmacion_solicitud,
        name="confirmacion"
    ),

    path(
        "<int:id_area>/",
        views.detalle_area,
        name="detalle"
    ),

]