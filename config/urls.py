from django.contrib import admin
from django.urls import path, include

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [

    path(
        "admin/",
        admin.site.urls
    ),

    path(
        "productos/",
        include("productos.urls")
    ),

    path(
        "servicios/",
        include("servicios.urls")
    ),

    path(
        "comunicacion/",
        include("comunicacion.urls")
    ),

    path(
        "gestion/",
        include("gestion.urls")
    ),

    path(
        "acceso/",
        include("gestion.autenticacion.urls")
    ),

    path(
        "reportes/",
        include("reportes.urls")
    ),

    path(
        "multimedia/",
        include("multimedia.urls")
    ),

    path(
        "",
        include("core.urls")
    ),

]


if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )