from django.contrib import admin
from .models import AreaServicio, SolicitudServicio
from core.patrones.singleton import ConfiguracionSistema

@admin.register(AreaServicio)
class AreaServicioAdmin(admin.ModelAdmin):
    list_display = (
        "id_area",
        "nombre",
        "activo",
    )

    list_display_links = (
        "id_area",
        "nombre",
    )

    list_editable = ("activo",)

    list_filter = ("activo",)

    search_fields = (
        "nombre",
        "descripcion",
    )

    ordering = ("nombre",)

    list_per_page = 10

    fieldsets = (

        ("Información del área", {
            "fields": (
                "nombre",
                "descripcion",
            )
        }),

        ("Estado", {
            "fields": (
                "activo",
            )
        }),

    )

@admin.register(SolicitudServicio)
class SolicitudServicioAdmin(admin.ModelAdmin):
    list_display = (
        "id_solicitud",
        "nombre",
        "area",
        "correo",
        "estatus",
        "fecha_solicitud",
    )

    search_fields = (
        "nombre",
        "empresa",
        "correo",
    )

    list_filter = (
        "area",
        "estatus",
        "fecha_solicitud",
    )

    readonly_fields = ("fecha_solicitud",)
    llist_per_page = (ConfiguracionSistema().registros_por_pagina)
    list_select_related = ("area",)