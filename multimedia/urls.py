from django.urls import path

from . import views

app_name = "multimedia"

urlpatterns = [
    path(
        "quienes-somos/",
        views.quienes_somos,
        name="quienes_somos",
    ),
    path(
        "casos-exito/",
        views.casos_exito,
        name="casos_exito",
    ),
    path(
        "socios/",
        views.socios,
        name="socios",
    ),
    path(
        "video/",
        views.video_institucional,
        name="video",
    ),
]
