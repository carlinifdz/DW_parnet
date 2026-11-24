from django.urls import path
from . import views

app_name = "core"

urlpatterns = [

    path(
        "",
        views.inicio,
        name="inicio"
    ),

    path(
        "noticias/",
        views.listado_noticias,
        name="listado_noticias"
    ),

    path(
        "noticias/<int:id_noticia>/",
        views.detalle_noticia,
        name="detalle_noticia"
    ),

    path(
        "clientes/",
        views.listado_clientes,
        name="listado_clientes"
    ),

]