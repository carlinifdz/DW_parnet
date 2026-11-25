from django.urls import path
from . import views

app_name = "gestion"

urlpatterns = [

    # 9.1 Dashboard general del panel administrativo
    path(
        "",
        views.panel_principal,
        name="panel"
    ),

    # 9.2 CRUD de Productos
    path(
        "productos/",
        views.productos_lista,
        name="productos_lista"
    ),
    path(
        "productos/nuevo/",
        views.producto_crear,
        name="producto_crear"
    ),
    path(
        "productos/<int:id_producto>/editar/",
        views.producto_editar,
        name="producto_editar"
    ),
    path(
        "productos/<int:id_producto>/eliminar/",
        views.producto_eliminar,
        name="producto_eliminar"
    ),

    # 9.3 CRUD de Categorias
    path(
        "categorias/",
        views.categorias_lista,
        name="categorias_lista"
    ),
    path(
        "categorias/nueva/",
        views.categoria_crear,
        name="categoria_crear"
    ),
    path(
        "categorias/<int:id_categoria>/editar/",
        views.categoria_editar,
        name="categoria_editar"
    ),
    path(
        "categorias/<int:id_categoria>/eliminar/",
        views.categoria_eliminar,
        name="categoria_eliminar"
    ),

    # 9.4 Administracion de Solicitudes de Servicios
    path(
        "solicitudes/",
        views.solicitudes_lista,
        name="solicitudes_lista"
    ),
    path(
        "solicitudes/<int:id_solicitud>/",
        views.solicitud_detalle,
        name="solicitud_detalle"
    ),

    # 9.5 Administracion y paginacion de Sugerencias
    path(
        "sugerencias/",
        views.sugerencias_lista,
        name="sugerencias_lista"
    ),
    path(
        "sugerencias/<int:id_sugerencia>/leida/",
        views.sugerencia_marcar_leida,
        name="sugerencia_marcar_leida"
    ),
    path(
        "sugerencias/<int:id_sugerencia>/eliminar/",
        views.sugerencia_eliminar,
        name="sugerencia_eliminar"
    ),

    # 9.6 Administracion de Noticias
    path(
        "noticias/",
        views.noticias_lista,
        name="noticias_lista"
    ),
    path(
        "noticias/nueva/",
        views.noticia_crear,
        name="noticia_crear"
    ),
    path(
        "noticias/<int:id_noticia>/editar/",
        views.noticia_editar,
        name="noticia_editar"
    ),
    path(
        "noticias/<int:id_noticia>/eliminar/",
        views.noticia_eliminar,
        name="noticia_eliminar"
    ),

    # 9.7 Administracion de Clientes
    path(
        "clientes/",
        views.clientes_lista,
        name="clientes_lista"
    ),
    path(
        "clientes/nuevo/",
        views.cliente_crear,
        name="cliente_crear"
    ),
    path(
        "clientes/<int:id_cliente>/editar/",
        views.cliente_editar,
        name="cliente_editar"
    ),
    path(
        "clientes/<int:id_cliente>/eliminar/",
        views.cliente_eliminar,
        name="cliente_eliminar"
    ),

    # 9.8 Administracion del Slider
    path(
        "slider/",
        views.slider_lista,
        name="slider_lista"
    ),
    path(
        "slider/nuevo/",
        views.slider_crear,
        name="slider_crear"
    ),
    path(
        "slider/<int:id_slider>/editar/",
        views.slider_editar,
        name="slider_editar"
    ),
    path(
        "slider/<int:id_slider>/eliminar/",
        views.slider_eliminar,
        name="slider_eliminar"
    ),

]
