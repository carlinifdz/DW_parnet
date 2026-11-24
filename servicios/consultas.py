from .models import AreaServicio

def areas_activas():

    return AreaServicio.objects.filter(
        activo=True
    ).order_by(
        "nombre",
        "id_area"
    )