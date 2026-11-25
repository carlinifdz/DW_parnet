# Módulo de Productos (`productos`)

## Descripción General

El módulo `productos` implementa el catálogo público de productos industriales de **ParNet Ingeniería** (Parte 5 del proyecto), incluyendo:

- Catálogo dinámico con imágenes y estatus de inventario (`Existencia` o `Agotado`).
- Buscador multicriterio (nombre, código, marca, modelo y descripción) y filtro por categorías activas.
- Paginación controlada por el patrón Singleton (`ConfiguracionSistema().registros_por_pagina`).
- Página de detalle de cada producto con especificaciones completas.
- Generación y descarga dinámica de fichas técnicas en formato **PDF** (`%PDF-1.4`).
- **API REST** en formato JSON para consulta de productos y categorías.

## Rutas Disponibles

| Ruta | Nombre | Método | Descripción |
| --- | --- | --- | --- |
| `/productos/` | `productos:listado` | `GET` | Catálogo paginado con buscador (`?q=`) y filtro (`?categoria=`) |
| `/productos/<id_producto>/` | `productos:detalle` | `GET` | Vista detallada del producto y su ficha técnica |
| `/productos/<id_producto>/ficha-pdf/` | `productos:ficha_pdf` | `GET` | Descarga de la ficha técnica del producto en formato PDF |
| `/productos/api/productos/` | `productos:api_productos` | `GET` | Endpoint REST JSON del listado de productos activos |
| `/productos/api/productos/<id_producto>/` | `productos:api_detalle_producto` | `GET` | Endpoint REST JSON del detalle de un producto |
| `/productos/api/categorias/` | `productos:api_categorias` | `GET` | Endpoint REST JSON de categorías activas |

## Ejecución de Pruebas

```powershell
python manage.py test core servicios productos
```
