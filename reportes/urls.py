from django.urls import path
from . import views

app_name = "reportes"

urlpatterns = [

    path(
        "",
        views.panel_reportes,
        name="panel"
    ),

    path(
        "inventario/",
        views.reporte_inventario,
        name="inventario"
    ),

    path(
        "inventario/exportar/pdf/",
        views.exportar_inventario_pdf,
        name="inventario_pdf"
    ),

    path(
        "inventario/exportar/excel/",
        views.exportar_inventario_excel,
        name="inventario_excel"
    ),

    path(
        "sugerencias/exportar/excel/",
        views.exportar_sugerencias_excel,
        name="sugerencias_excel"
    ),

    path(
        "sugerencias/exportar/pdf/",
        views.exportar_sugerencias_pdf,
        name="sugerencias_pdf"
    ),

    path(
        "dashboards/servicios/",
        views.dashboard_servicios,
        name="dashboard_servicios"
    ),

    path(
        "dashboards/productos/",
        views.dashboard_productos,
        name="dashboard_productos"
    ),

    path(
        "api/dashboards/",
        views.api_dashboards,
        name="api_dashboards"
    ),

]
