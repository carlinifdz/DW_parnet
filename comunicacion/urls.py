from django.urls import path

from . import views

app_name = "comunicacion"

urlpatterns = [
    path(
        "",
        views.contacto,
        name="contacto",
    ),
    path(
        "sugerencias/",
        views.sugerencias,
        name="sugerencias",
    ),
]
