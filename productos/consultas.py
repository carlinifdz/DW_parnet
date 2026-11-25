from django.db.models import Q

from .models import CategoriaProducto, Producto


def categorias_activas():

    return CategoriaProducto.objects.filter(
        activo=True
    ).order_by(
        "nombre",
        "id_categoria"
    )


def productos_activos(busqueda="", id_categoria=None):

    consulta = Producto.objects.filter(
        activo=True,
        categoria__activo=True
    ).select_related(
        "categoria"
    )

    termino = (busqueda or "").strip()

    if termino:
        consulta = consulta.filter(
            Q(nombre__icontains=termino)
            | Q(codigo__icontains=termino)
            | Q(marca__icontains=termino)
            | Q(modelo__icontains=termino)
            | Q(descripcion__icontains=termino)
        )

    if id_categoria not in (None, ""):
        try:
            id_cat = int(id_categoria)
            consulta = consulta.filter(
                categoria_id=id_cat
            )
        except (TypeError, ValueError):
            pass

    return consulta.order_by(
        "nombre",
        "id_producto"
    )
