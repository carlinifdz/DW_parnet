from django.contrib import admin
from .models import CategoriaProducto, Producto
from core.patrones.singleton import ConfiguracionSistema


@admin.register(CategoriaProducto)
class CategoriaProductoAdmin(admin.ModelAdmin):
    list_display = (
        "id_categoria",
        "nombre",
        "activo",
    )

    search_fields = ("nombre",)
    list_filter = ("activo",)


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = (
        "codigo",
        "nombre",
        "categoria",
        "marca",
        "precio",
        "stock",
        "estatus",
        "activo",
    )

    search_fields = (
        "codigo",
        "nombre",
        "marca",
        "modelo",
    )

    list_filter = (
        "categoria",
        "activo",
        "marca",
    )

    list_per_page = (ConfiguracionSistema().registros_por_pagina)

    readonly_fields = (
        "fecha_registro",
        "fecha_actualizacion",
    )

    list_select_related = ("categoria",)