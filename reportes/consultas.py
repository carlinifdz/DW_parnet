from django.db.models import Count, Q

from comunicacion.models import Sugerencia
from productos.models import CategoriaProducto, Producto
from servicios.models import AreaServicio


def obtener_reporte_inventario(estatus=None, id_categoria=None, busqueda=""):
    """
    Obtiene el listado de productos para el reporte general de inventario
    incluyendo su clasificación como 'Existencia' (stock > 0) o 'Agotado' (stock == 0).
    """
    consulta = Producto.objects.select_related(
        "categoria"
    ).order_by(
        "nombre",
        "id_producto"
    )

    termino = (busqueda or "").strip()
    if termino:
        consulta = consulta.filter(
            Q(nombre__icontains=termino)
            | Q(codigo__icontains=termino)
            | Q(marca__icontains=termino)
            | Q(modelo__icontains=termino)
        )

    if id_categoria not in (None, ""):
        try:
            consulta = consulta.filter(
                categoria_id=int(id_categoria)
            )
        except (TypeError, ValueError):
            pass

    estatus_limpio = (estatus or "").strip().lower()
    if estatus_limpio == "existencia":
        consulta = consulta.filter(stock__gt=0)
    elif estatus_limpio == "agotado":
        consulta = consulta.filter(stock__lte=0)

    return list(consulta)


def resumen_inventario(productos):
    """
    Calcula métricas generales a partir de una lista de productos.
    """
    total_productos = len(productos)
    en_existencia = sum(
        1 for prod in productos if prod.stock > 0
    )
    agotados = total_productos - en_existencia
    unidades_totales = sum(
        max(0, int(prod.stock)) for prod in productos
    )

    return {
        "total_productos": total_productos,
        "en_existencia": en_existencia,
        "agotados": agotados,
        "unidades_totales": unidades_totales,
    }


def obtener_sugerencias_reporte():
    """
    Retorna todas las sugerencias ordenadas de la más reciente a la más antigua.
    """
    return list(
        Sugerencia.objects.all().order_by(
            "-fecha_registro",
            "-id_sugerencia"
        )
    )


def obtener_dashboard_servicios():
    """
    Retorna las áreas de servicio con el total de solicitudes asociadas,
    equivalente a `vw_dashboard_servicios` de MySQL.
    """
    filas = (
        AreaServicio.objects.annotate(
            total=Count("solicitudes")
        )
        .order_by("-total", "nombre", "id_area")
    )

    resultados = []
    for area in filas:
        resultados.append({
            "id_area": area.id_area,
            "servicio": area.nombre,
            "total": int(getattr(area, "total", 0)),
        })

    return resultados


def obtener_dashboard_productos():
    """
    Retorna las categorías de productos con el total de productos activos,
    equivalente a `vw_dashboard_productos` de MySQL.
    """
    filas = (
        CategoriaProducto.objects.annotate(
            total=Count(
                "productos",
                filter=Q(productos__activo=True)
            )
        )
        .order_by("-total", "nombre", "id_categoria")
    )

    resultados = []
    for cat in filas:
        resultados.append({
            "id_categoria": cat.id_categoria,
            "categoria": cat.nombre,
            "total": int(getattr(cat, "total", 0)),
        })

    return resultados
