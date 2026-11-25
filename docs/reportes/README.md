# Módulo de Reportes y Dashboards (`reportes`)

## Descripción General

El módulo `reportes` implementa los reportes ejecutivos, la clasificación de inventario, la exportación de documentos oficiales (Excel `.xlsx` y PDF `.pdf`) y los dos dashboards estadísticos de **ParNet Ingeniería** (Parte 10 del proyecto).

Todas las vistas están protegidas mediante el decorador `@administrador_requerido` de `gestion.autenticacion.permisos`.

## Funcionalidades Incluidas

- **10.1 y 10.2 Reporte general de inventario y clasificación de existencias:** listado completo de productos clasificados automáticamente como `Existencia` (`stock > 0`) o `Agotado` (`stock == 0`), coincidiendo con `vw_inventario`.
- **10.3 Exportación del reporte de inventario:** descarga en formato PDF y Excel (`.xlsx`).
- **10.4 Exportación de sugerencias a Excel (`.xlsx`):** reporte de todas las sugerencias recibidas.
- **10.5 Exportación de sugerencias a PDF (`.pdf`):** documento tabular con todas las sugerencias recibidas.
- **10.6 Dashboard de solicitudes por tipo de servicio:** gráfica comparativa y tabla basada en `vw_dashboard_servicios`.
- **10.7 Dashboard de productos por categoría:** gráfica comparativa y tabla basada en `vw_dashboard_productos`.

## Rutas Disponibles (`namespace = "reportes"`)

| Ruta | Nombre | Descripción |
| --- | --- | --- |
| `/reportes/` | `reportes:panel` | Panel general de reportes, métricas y los dos dashboards |
| `/reportes/inventario/` | `reportes:inventario` | Reporte general de inventario con filtros por estatus y categoría |
| `/reportes/inventario/exportar/pdf/` | `reportes:inventario_pdf` | Exportación del inventario a PDF |
| `/reportes/inventario/exportar/excel/` | `reportes:inventario_excel` | Exportación del inventario a Excel (`.xlsx`) |
| `/reportes/sugerencias/exportar/excel/` | `reportes:sugerencias_excel` | Exportación de sugerencias a Excel (`.xlsx`) |
| `/reportes/sugerencias/exportar/pdf/` | `reportes:sugerencias_pdf` | Exportación de sugerencias a PDF |
| `/reportes/dashboards/servicios/` | `reportes:dashboard_servicios` | Dashboard detallado de solicitudes por área de servicio |
| `/reportes/dashboards/productos/` | `reportes:dashboard_productos` | Dashboard detallado de productos activos por categoría |
| `/reportes/api/dashboards/` | `reportes:api_dashboards` | Endpoint JSON con etiquetas y valores de ambos dashboards |

## Ejecución de Pruebas

```powershell
python manage.py test reportes
```
