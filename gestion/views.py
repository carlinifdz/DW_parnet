from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import ProtectedError, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from comunicacion.models import Sugerencia
from core.models import Cliente, Noticia, Slider
from core.patrones.singleton import ConfiguracionSistema
from gestion.autenticacion.permisos import administrador_requerido
from productos.models import CategoriaProducto, Producto
from reportes.consultas import (
    obtener_dashboard_productos,
    obtener_dashboard_servicios,
    obtener_reporte_inventario,
    resumen_inventario,
)
from servicios.models import AreaServicio, SolicitudServicio

from .forms import (
    CategoriaProductoForm,
    ClienteForm,
    NoticiaForm,
    ProductoForm,
    SliderForm,
    SolicitudServicioEstatusForm,
)


# =========================================
# 9.1 Y 9.9 DASHBOARD DEL PANEL ADMINISTRATIVO
# =========================================

@administrador_requerido
def panel_principal(request):

    productos = obtener_reporte_inventario()
    metricas_inv = resumen_inventario(productos)

    total_categorias = CategoriaProducto.objects.count()
    total_solicitudes = SolicitudServicio.objects.count()
    solicitudes_pendientes = SolicitudServicio.objects.filter(
        estatus=SolicitudServicio.Estatus.PENDIENTE
    ).count()

    total_sugerencias = Sugerencia.objects.count()
    sugerencias_no_leidas = Sugerencia.objects.filter(
        leida=False
    ).count()

    total_noticias = Noticia.objects.count()
    total_clientes = Cliente.objects.count()
    total_sliders = Slider.objects.count()

    # Integracion de dashboards (9.9)
    datos_servicios = obtener_dashboard_servicios()
    max_servicios = max(
        (item["total"] for item in datos_servicios),
        default=1
    ) or 1
    for item in datos_servicios:
        item["porcentaje"] = round(
            (item["total"] / max_servicios) * 100
        )

    datos_productos = obtener_dashboard_productos()
    max_productos = max(
        (item["total"] for item in datos_productos),
        default=1
    ) or 1
    for item in datos_productos:
        item["porcentaje"] = round(
            (item["total"] / max_productos) * 100
        )

    contexto = {
        "seccion_activa": "dashboard",
        "metricas_inv": metricas_inv,
        "total_categorias": total_categorias,
        "total_solicitudes": total_solicitudes,
        "solicitudes_pendientes": solicitudes_pendientes,
        "total_sugerencias": total_sugerencias,
        "sugerencias_no_leidas": sugerencias_no_leidas,
        "total_noticias": total_noticias,
        "total_clientes": total_clientes,
        "total_sliders": total_sliders,
        "dashboard_servicios": datos_servicios[:6],
        "dashboard_productos": datos_productos,
    }

    return render(
        request,
        "gestion/panel/dashboard.html",
        contexto
    )


# =========================================
# 9.2 CRUD DE PRODUCTOS
# =========================================

@administrador_requerido
def productos_lista(request):

    configuracion = ConfiguracionSistema()
    busqueda = request.GET.get("q", "").strip()
    categoria_param = request.GET.get("categoria", "").strip()

    consulta = Producto.objects.select_related(
        "categoria"
    ).order_by("nombre", "id_producto")

    if busqueda:
        consulta = consulta.filter(
            Q(nombre__icontains=busqueda)
            | Q(codigo__icontains=busqueda)
            | Q(marca__icontains=busqueda)
            | Q(modelo__icontains=busqueda)
        )

    categoria_actual = None
    if categoria_param:
        try:
            categoria_actual = int(categoria_param)
            consulta = consulta.filter(
                categoria_id=categoria_actual
            )
        except ValueError:
            categoria_actual = None

    paginador = Paginator(
        consulta,
        configuracion.registros_por_pagina
    )
    pagina = paginador.get_page(request.GET.get("page"))

    categorias = CategoriaProducto.objects.order_by("nombre")

    contexto = {
        "seccion_activa": "productos",
        "pagina": pagina,
        "categorias": categorias,
        "busqueda": busqueda,
        "categoria_actual": categoria_actual,
    }

    return render(
        request,
        "gestion/panel/productos_lista.html",
        contexto
    )


@administrador_requerido
def producto_crear(request):

    if request.method == "POST":
        form = ProductoForm(request.POST, request.FILES)
        if form.is_valid():
            producto = form.save()
            messages.success(
                request,
                f"El producto '{producto.nombre}' fue registrado correctamente."
            )
            return redirect("gestion:productos_lista")
    else:
        form = ProductoForm()

    contexto = {
        "seccion_activa": "productos",
        "form": form,
        "titulo_formulario": "Registrar Nuevo Producto",
        "es_edicion": False,
    }

    return render(
        request,
        "gestion/panel/producto_form.html",
        contexto
    )


@administrador_requerido
def producto_editar(request, id_producto):

    producto = get_object_or_404(
        Producto,
        id_producto=id_producto
    )

    if request.method == "POST":
        form = ProductoForm(
            request.POST,
            request.FILES,
            instance=producto
        )
        if form.is_valid():
            producto = form.save()
            messages.success(
                request,
                f"El producto '{producto.nombre}' fue actualizado correctamente."
            )
            return redirect("gestion:productos_lista")
    else:
        form = ProductoForm(instance=producto)

    contexto = {
        "seccion_activa": "productos",
        "form": form,
        "producto": producto,
        "titulo_formulario": f"Editar Producto: {producto.codigo}",
        "es_edicion": True,
    }

    return render(
        request,
        "gestion/panel/producto_form.html",
        contexto
    )


@administrador_requerido
@require_POST
def producto_eliminar(request, id_producto):

    producto = get_object_or_404(
        Producto,
        id_producto=id_producto
    )
    nombre = producto.nombre
    producto.delete()

    messages.success(
        request,
        f"El producto '{nombre}' fue eliminado del catálogo."
    )
    return redirect("gestion:productos_lista")


# =========================================
# 9.3 CRUD DE CATEGORIAS DE PRODUCTOS
# =========================================

@administrador_requerido
def categorias_lista(request):

    categorias = CategoriaProducto.objects.order_by(
        "nombre",
        "id_categoria"
    )

    contexto = {
        "seccion_activa": "categorias",
        "categorias": categorias,
    }

    return render(
        request,
        "gestion/panel/categorias_lista.html",
        contexto
    )


@administrador_requerido
def categoria_crear(request):

    if request.method == "POST":
        form = CategoriaProductoForm(request.POST)
        if form.is_valid():
            categoria = form.save()
            messages.success(
                request,
                f"La categoría '{categoria.nombre}' fue registrada correctamente."
            )
            return redirect("gestion:categorias_lista")
    else:
        form = CategoriaProductoForm()

    contexto = {
        "seccion_activa": "categorias",
        "form": form,
        "titulo_formulario": "Registrar Nueva Categoría",
        "es_edicion": False,
    }

    return render(
        request,
        "gestion/panel/categoria_form.html",
        contexto
    )


@administrador_requerido
def categoria_editar(request, id_categoria):

    categoria = get_object_or_404(
        CategoriaProducto,
        id_categoria=id_categoria
    )

    if request.method == "POST":
        form = CategoriaProductoForm(
            request.POST,
            instance=categoria
        )
        if form.is_valid():
            categoria = form.save()
            messages.success(
                request,
                f"La categoría '{categoria.nombre}' fue actualizada correctamente."
            )
            return redirect("gestion:categorias_lista")
    else:
        form = CategoriaProductoForm(instance=categoria)

    contexto = {
        "seccion_activa": "categorias",
        "form": form,
        "categoria": categoria,
        "titulo_formulario": f"Editar Categoría: {categoria.nombre}",
        "es_edicion": True,
    }

    return render(
        request,
        "gestion/panel/categoria_form.html",
        contexto
    )


@administrador_requerido
@require_POST
def categoria_eliminar(request, id_categoria):

    categoria = get_object_or_404(
        CategoriaProducto,
        id_categoria=id_categoria
    )
    nombre = categoria.nombre

    try:
        categoria.delete()
        messages.success(
            request,
            f"La categoría '{nombre}' fue eliminada correctamente."
        )
    except ProtectedError:
        messages.error(
            request,
            f"No es posible eliminar la categoría '{nombre}' porque tiene productos asociados."
        )

    return redirect("gestion:categorias_lista")


# =========================================
# 9.4 ADMINISTRACION DE SOLICITUDES DE SERVICIOS
# =========================================

@administrador_requerido
def solicitudes_lista(request):

    configuracion = ConfiguracionSistema()
    estatus_filtro = request.GET.get("estatus", "").strip()
    area_param = request.GET.get("area", "").strip()

    consulta = SolicitudServicio.objects.select_related(
        "area"
    ).order_by("-fecha_solicitud", "-id_solicitud")

    if estatus_filtro:
        consulta = consulta.filter(estatus=estatus_filtro)

    area_actual = None
    if area_param:
        try:
            area_actual = int(area_param)
            consulta = consulta.filter(area_id=area_actual)
        except ValueError:
            area_actual = None

    paginador = Paginator(
        consulta,
        configuracion.registros_por_pagina
    )
    pagina = paginador.get_page(request.GET.get("page"))

    areas = AreaServicio.objects.order_by("nombre")

    contexto = {
        "seccion_activa": "solicitudes",
        "pagina": pagina,
        "areas": areas,
        "estatus_opciones": SolicitudServicio.Estatus.choices,
        "estatus_actual": estatus_filtro,
        "area_actual": area_actual,
    }

    return render(
        request,
        "gestion/panel/solicitudes_lista.html",
        contexto
    )


@administrador_requerido
def solicitud_detalle(request, id_solicitud):

    solicitud = get_object_or_404(
        SolicitudServicio.objects.select_related("area"),
        id_solicitud=id_solicitud
    )

    if request.method == "POST":
        form = SolicitudServicioEstatusForm(
            request.POST,
            instance=solicitud
        )
        if form.is_valid():
            form.save()
            messages.success(
                request,
                f"El estatus de la solicitud #{solicitud.id_solicitud} fue actualizado a '{solicitud.estatus}'."
            )
            return redirect("gestion:solicitudes_lista")
    else:
        form = SolicitudServicioEstatusForm(instance=solicitud)

    contexto = {
        "seccion_activa": "solicitudes",
        "solicitud": solicitud,
        "form": form,
    }

    return render(
        request,
        "gestion/panel/solicitud_detalle.html",
        contexto
    )


# =========================================
# 9.5 ADMINISTRACION Y PAGINACION DE SUGERENCIAS
# =========================================

@administrador_requerido
def sugerencias_lista(request):

    configuracion = ConfiguracionSistema()
    estado_filtro = request.GET.get("leida", "").strip()

    consulta = Sugerencia.objects.all().order_by(
        "-fecha_registro",
        "-id_sugerencia"
    )

    if estado_filtro == "1":
        consulta = consulta.filter(leida=True)
    elif estado_filtro == "0":
        consulta = consulta.filter(leida=False)

    paginador = Paginator(
        consulta,
        configuracion.registros_por_pagina
    )
    pagina = paginador.get_page(request.GET.get("page"))

    contexto = {
        "seccion_activa": "sugerencias",
        "pagina": pagina,
        "estado_actual": estado_filtro,
    }

    return render(
        request,
        "gestion/panel/sugerencias_lista.html",
        contexto
    )


@administrador_requerido
@require_POST
def sugerencia_marcar_leida(request, id_sugerencia):

    sugerencia = get_object_or_404(
        Sugerencia,
        id_sugerencia=id_sugerencia
    )
    sugerencia.leida = not sugerencia.leida
    sugerencia.save()

    estado_txt = "leída" if sugerencia.leida else "no leída"
    messages.success(
        request,
        f"La sugerencia #{sugerencia.id_sugerencia} fue marcada como {estado_txt}."
    )
    return redirect("gestion:sugerencias_lista")


@administrador_requerido
@require_POST
def sugerencia_eliminar(request, id_sugerencia):

    sugerencia = get_object_or_404(
        Sugerencia,
        id_sugerencia=id_sugerencia
    )
    sugerencia.delete()

    messages.success(
        request,
        "La sugerencia fue eliminada correctamente."
    )
    return redirect("gestion:sugerencias_lista")


# =========================================
# 9.6 ADMINISTRACION DE NOTICIAS
# =========================================

@administrador_requerido
def noticias_lista(request):

    configuracion = ConfiguracionSistema()
    noticias = Noticia.objects.all().order_by(
        "-fecha_publicacion",
        "-id_noticia"
    )

    paginador = Paginator(
        noticias,
        configuracion.registros_por_pagina
    )
    pagina = paginador.get_page(request.GET.get("page"))

    contexto = {
        "seccion_activa": "noticias",
        "pagina": pagina,
    }

    return render(
        request,
        "gestion/panel/noticias_lista.html",
        contexto
    )


@administrador_requerido
def noticia_crear(request):

    if request.method == "POST":
        form = NoticiaForm(request.POST, request.FILES)
        if form.is_valid():
            noticia = form.save()
            messages.success(
                request,
                f"La noticia '{noticia.titulo}' fue publicada correctamente."
            )
            return redirect("gestion:noticias_lista")
    else:
        form = NoticiaForm()

    contexto = {
        "seccion_activa": "noticias",
        "form": form,
        "titulo_formulario": "Publicar Nueva Noticia",
        "es_edicion": False,
    }

    return render(
        request,
        "gestion/panel/noticia_form.html",
        contexto
    )


@administrador_requerido
def noticia_editar(request, id_noticia):

    noticia = get_object_or_404(
        Noticia,
        id_noticia=id_noticia
    )

    if request.method == "POST":
        form = NoticiaForm(
            request.POST,
            request.FILES,
            instance=noticia
        )
        if form.is_valid():
            noticia = form.save()
            messages.success(
                request,
                f"La noticia '{noticia.titulo}' fue actualizada correctamente."
            )
            return redirect("gestion:noticias_lista")
    else:
        form = NoticiaForm(instance=noticia)

    contexto = {
        "seccion_activa": "noticias",
        "form": form,
        "noticia": noticia,
        "titulo_formulario": f"Editar Noticia: {noticia.titulo}",
        "es_edicion": True,
    }

    return render(
        request,
        "gestion/panel/noticia_form.html",
        contexto
    )


@administrador_requerido
@require_POST
def noticia_eliminar(request, id_noticia):

    noticia = get_object_or_404(
        Noticia,
        id_noticia=id_noticia
    )
    titulo = noticia.titulo
    noticia.delete()

    messages.success(
        request,
        f"La noticia '{titulo}' fue eliminada correctamente."
    )
    return redirect("gestion:noticias_lista")


# =========================================
# 9.7 ADMINISTRACION DE CLIENTES
# =========================================

@administrador_requerido
def clientes_lista(request):

    clientes = Cliente.objects.all().order_by(
        "nombre",
        "id_cliente"
    )

    contexto = {
        "seccion_activa": "clientes",
        "clientes": clientes,
    }

    return render(
        request,
        "gestion/panel/clientes_lista.html",
        contexto
    )


@administrador_requerido
def cliente_crear(request):

    if request.method == "POST":
        form = ClienteForm(request.POST, request.FILES)
        if form.is_valid():
            cliente = form.save()
            messages.success(
                request,
                f"El cliente '{cliente.nombre}' fue registrado correctamente."
            )
            return redirect("gestion:clientes_lista")
    else:
        form = ClienteForm()

    contexto = {
        "seccion_activa": "clientes",
        "form": form,
        "titulo_formulario": "Registrar Nuevo Cliente",
        "es_edicion": False,
    }

    return render(
        request,
        "gestion/panel/cliente_form.html",
        contexto
    )


@administrador_requerido
def cliente_editar(request, id_cliente):

    cliente = get_object_or_404(
        Cliente,
        id_cliente=id_cliente
    )

    if request.method == "POST":
        form = ClienteForm(
            request.POST,
            request.FILES,
            instance=cliente
        )
        if form.is_valid():
            cliente = form.save()
            messages.success(
                request,
                f"El cliente '{cliente.nombre}' fue actualizado correctamente."
            )
            return redirect("gestion:clientes_lista")
    else:
        form = ClienteForm(instance=cliente)

    contexto = {
        "seccion_activa": "clientes",
        "form": form,
        "cliente": cliente,
        "titulo_formulario": f"Editar Cliente: {cliente.nombre}",
        "es_edicion": True,
    }

    return render(
        request,
        "gestion/panel/cliente_form.html",
        contexto
    )


@administrador_requerido
@require_POST
def cliente_eliminar(request, id_cliente):

    cliente = get_object_or_404(
        Cliente,
        id_cliente=id_cliente
    )
    nombre = cliente.nombre
    cliente.delete()

    messages.success(
        request,
        f"El cliente '{nombre}' fue eliminado correctamente."
    )
    return redirect("gestion:clientes_lista")


# =========================================
# 9.8 ADMINISTRACION DEL SLIDER
# =========================================

@administrador_requerido
def slider_lista(request):

    sliders = Slider.objects.all().order_by(
        "orden",
        "id_slider"
    )

    contexto = {
        "seccion_activa": "slider",
        "sliders": sliders,
    }

    return render(
        request,
        "gestion/panel/slider_lista.html",
        contexto
    )


@administrador_requerido
def slider_crear(request):

    if request.method == "POST":
        form = SliderForm(request.POST, request.FILES)
        if form.is_valid():
            slider = form.save()
            messages.success(
                request,
                f"El banner '{slider}' fue registrado correctamente."
            )
            return redirect("gestion:slider_lista")
    else:
        form = SliderForm()

    contexto = {
        "seccion_activa": "slider",
        "form": form,
        "titulo_formulario": "Registrar Nueva Imagen del Slider",
        "es_edicion": False,
    }

    return render(
        request,
        "gestion/panel/slider_form.html",
        contexto
    )


@administrador_requerido
def slider_editar(request, id_slider):

    slider = get_object_or_404(
        Slider,
        id_slider=id_slider
    )

    if request.method == "POST":
        form = SliderForm(
            request.POST,
            request.FILES,
            instance=slider
        )
        if form.is_valid():
            slider = form.save()
            messages.success(
                request,
                f"El banner '{slider}' fue actualizado correctamente."
            )
            return redirect("gestion:slider_lista")
    else:
        form = SliderForm(instance=slider)

    contexto = {
        "seccion_activa": "slider",
        "form": form,
        "slider": slider,
        "titulo_formulario": f"Editar Banner del Slider #{slider.id_slider}",
        "es_edicion": True,
    }

    return render(
        request,
        "gestion/panel/slider_form.html",
        contexto
    )


@administrador_requerido
@require_POST
def slider_eliminar(request, id_slider):

    slider = get_object_or_404(
        Slider,
        id_slider=id_slider
    )
    nombre = str(slider)
    slider.delete()

    messages.success(
        request,
        f"El banner '{nombre}' fue eliminado del slider."
    )
    return redirect("gestion:slider_lista")
