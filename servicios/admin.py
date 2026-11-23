from django.contrib import admin
from .models import AreaServicio, SolicitudServicio


@admin.register(AreaServicio)
class AreaServicioAdmin(admin.ModelAdmin):
    list_display = (
        "id_area",
        "nombre",
        "activo",
    )

    search_fields = ("nombre",)
    list_filter = ("activo",)


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
    list_per_page = 10
    list_select_related = ("area",)