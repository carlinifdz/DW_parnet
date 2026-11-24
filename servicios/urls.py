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
        "<int:id_area>/",
        views.detalle_area,
        name="detalle"
    ),

]