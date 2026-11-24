from django.contrib import admin
from django.utils.html import format_html

from core.patrones.singleton import ConfiguracionSistema

from .models import (
    Noticia,
    Cliente,
    Slider,
    Visita,
    UsuarioConectado,
)


# =========================================
# NOTICIAS
# =========================================

@admin.register(Noticia)
class NoticiaAdmin(admin.ModelAdmin):

    list_display = (
        "id_noticia",
        "vista_previa",
        "titulo",
        "fecha_publicacion",
        "activo",
    )

    list_display_links = (
        "id_noticia",
        "titulo",
    )

    list_editable = ("activo",)

    search_fields = (
        "titulo",
        "resumen",
        "contenido",
    )

    list_filter = (
        "activo",
        "fecha_publicacion",
    )

    ordering = (
        "-fecha_publicacion",
        "-id_noticia",
    )

    readonly_fields = (
        "fecha_publicacion",
        "vista_previa",
    )

    list_per_page = (
        ConfiguracionSistema().registros_por_pagina
    )

    fieldsets = (
        ("Información de la noticia", {
            "fields": (
                "titulo",
                "resumen",
                "contenido",
            )
        }),
        ("Imagen", {
            "fields": (
                "imagen",
                "vista_previa",
            )
        }),
        ("Publicación", {
            "fields": (
                "activo",
                "fecha_publicacion",
            )
        }),
    )

    @admin.display(description="Vista previa")
    def vista_previa(self, obj):

        if obj and obj.imagen:

            return format_html(
                '<img src="{}" width="120" '
                'style="height:auto;" '
                'alt="Vista previa">',
                obj.imagen.url
            )

        return "Sin imagen"


# =========================================
# CLIENTES
# =========================================

# =========================================
# CLIENTES
# =========================================

@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):

    list_display = (
        "id_cliente",
        "vista_previa",
        "nombre",
        "sitio_web",
        "activo",
    )

    list_display_links = (
        "id_cliente",
        "nombre",
    )

    list_editable = ("activo",)

    search_fields = (
        "nombre",
        "descripcion",
        "sitio_web",
    )

    list_filter = ("activo",)

    ordering = (
        "nombre",
        "id_cliente",
    )

    list_per_page = (
        ConfiguracionSistema().registros_por_pagina
    )

    readonly_fields = ("vista_previa",)

    fieldsets = (

        ("Información de la empresa", {
            "fields": (
                "nombre",
                "descripcion",
                "sitio_web",
            )
        }),

        ("Identidad gráfica", {
            "fields": (
                "logo",
                "vista_previa",
            )
        }),

        ("Estado", {
            "fields": (
                "activo",
            )
        }),

    )

    @admin.display(description="Logotipo")
    def vista_previa(self, obj):

        if obj and obj.logo:

            return format_html(
                '<img src="{}" width="120" '
                'style="height:auto; object-fit:contain;" '
                'alt="Logotipo del cliente">',
                obj.logo.url
            )

        return "Sin logotipo"


# =========================================
# SLIDER
# =========================================

@admin.register(Slider)
class SliderAdmin(admin.ModelAdmin):

    list_display = (
        "id_slider",
        "vista_previa",
        "titulo",
        "orden",
        "activo",
    )

    list_display_links = (
        "id_slider",
        "titulo",
    )

    list_editable = (
        "orden",
        "activo",
    )

    list_filter = ("activo",)

    search_fields = (
        "titulo",
        "descripcion",
    )

    ordering = (
        "orden",
        "id_slider",
    )

    readonly_fields = ("vista_previa",)

    @admin.display(description="Vista previa")
    def vista_previa(self, obj):

        if obj and obj.imagen:

            return format_html(
                '<img src="{}" width="140" '
                'style="height:auto; border-radius:4px;" '
                'alt="Vista previa">',
                obj.imagen.url
            )

        return "Sin imagen"


# =========================================
# VISITAS
# =========================================

@admin.register(Visita)
class VisitaAdmin(admin.ModelAdmin):

    list_display = (
        "id_visita",
        "pagina",
        "fecha_visita",
    )

    list_filter = ("fecha_visita",)

    list_per_page = 20

    readonly_fields = (
        "pagina",
        "fecha_visita",
    )

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


# =========================================
# USUARIOS CONECTADOS
# =========================================

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