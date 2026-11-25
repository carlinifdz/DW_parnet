# Módulo de Panel Administrativo Personalizado (`gestion`)

## Descripción General

El módulo `gestion` implementa el **Panel Administrativo Personalizado** de **ParNet Ingeniería** (Parte 9 del proyecto), permitiendo a los administradores autenticados gestionar todos los catálogos, solicitudes, sugerencias, contenidos institucionales y reportes desde una interfaz unificada con el diseño institucional del sitio.

Todas las rutas utilizan el decorador `@administrador_requerido` de `gestion.autenticacion.permisos`.

## Funcionalidades Incluidas

- **9.1 Diseño general del panel administrativo (`/gestion/`):** Resumen ejecutivo de indicadores, accesos rápidos y menú administrativo.
- **9.2 CRUD de Productos (`/gestion/productos/...`):** Creación, consulta con buscador/filtros, edición, carga de imágenes y eliminación de productos.
- **9.3 CRUD de Categorías (`/gestion/categorias/...`):** Creación, edición y eliminación protegida de categorías de productos.
- **9.4 Administración de Solicitudes de Servicios (`/gestion/solicitudes/...`):** Consulta filtrable por área y estatus, y actualización del estatus de atención (`Pendiente`, `En proceso`, `Atendida`, `Cancelada`).
- **9.5 Administración y Paginación de Sugerencias (`/gestion/sugerencias/...`):** Listado paginado con `ConfiguracionSistema().registros_por_pagina`, cambio de estado (`Leída`/`No leída`), eliminación y enlaces directos de exportación a Excel (`.xlsx`) y PDF (`.pdf`).
- **9.6 Administración de Noticias (`/gestion/noticias/...`):** CRUD completo de noticias institucionales.
- **9.7 Administración de Clientes (`/gestion/clientes/...`):** CRUD completo del catálogo de clientes.
- **9.8 Administración del Slider (`/gestion/slider/...`):** CRUD completo de banners y orden de aparición.
- **9.9 Integración de Reportes y Dashboards:** Visualización directa de los dashboards de servicios y productos dentro del panel y acceso al centro de reportes.

## Ejecución de Pruebas

```powershell
python manage.py test gestion
```
