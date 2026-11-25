from django.urls import path
from . import views

app_name = "productos"

urlpatterns = [

    path(
        "",
        views.listado_productos,
        name="listado"
    ),

    path(
        "<int:id_producto>/",
        views.detalle_producto,
        name="detalle"
    ),

    path(
        "<int:id_producto>/ficha-pdf/",
        views.ficha_tecnica_pdf,
        name="ficha_pdf"
    ),

    path(
        "api/productos/",
        views.api_productos,
        name="api_productos"
    ),

    path(
        "api/productos/<int:id_producto>/",
        views.api_detalle_producto,
        name="api_detalle_producto"
    ),

    path(
        "api/categorias/",
        views.api_categorias,
        name="api_categorias"
    ),

]
