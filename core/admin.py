from django.contrib import admin

from .models import (
    Noticia,
    Cliente,
    Slider,
    Visita,
    UsuarioConectado,
)


@admin.register(Noticia)
class NoticiaAdmin(admin.ModelAdmin):
    list_display = (
        "titulo",
        "fecha_publicacion",
        "activo",
    )

    search_fields = ("titulo", "contenido")
    list_filter = ("activo",)
    readonly_fields = ("fecha_publicacion",)


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = (
        "nombre",
        "sitio_web",
        "activo",
    )

    search_fields = ("nombre",)
    list_filter = ("activo",)


@admin.register(Slider)
class SliderAdmin(admin.ModelAdmin):
    list_display = (
        "titulo",
        "orden",
        "activo",
    )

    list_filter = ("activo",)
    ordering = ("orden",)


@admin.register(Visita)
class VisitaAdmin(admin.ModelAdmin):
    list_display = (
        "id_visita",
        "pagina",
        "fecha_visita",
    )

    list_filter = ("fecha_visita",)
    list_per_page = 20
    readonly_fields = ("pagina", "fecha_visita")

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(UsuarioConectado)
class UsuarioConectadoAdmin(admin.ModelAdmin):
    list_display = (
        "id_sesion",
        "ultima_actividad",
    )

    readonly_fields = (
        "id_sesion",
        "ultima_actividad",
    )

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False