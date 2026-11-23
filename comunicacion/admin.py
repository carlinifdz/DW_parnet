from django.contrib import admin
from .models import Sugerencia


@admin.register(Sugerencia)
class SugerenciaAdmin(admin.ModelAdmin):
    list_display = (
        "id_sugerencia",
        "nombre",
        "correo",
        "leida",
        "fecha_registro",
    )

    search_fields = (
        "nombre",
        "correo",
        "mensaje",
    )

    list_filter = (
        "leida",
        "fecha_registro",
    )

    readonly_fields = ("fecha_registro",)
    list_per_page = 10