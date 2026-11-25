from decimal import Decimal
from unittest.mock import MagicMock, patch

from django.contrib.staticfiles import finders
from django.test import SimpleTestCase
from django.urls import reverse
from django.utils import timezone

from comunicacion.models import Sugerencia
from core.models import Cliente, Noticia, Slider
from core.patrones.singleton import ConfiguracionSistema
from productos.models import CategoriaProducto, Producto
from servicios.models import AreaServicio, SolicitudServicio

from .forms import ProductoForm


def _crear_admin_mock():
    usuario = MagicMock()
    usuario.username = "admin"
    usuario.is_authenticated = True
    usuario.is_active = True
    usuario.is_staff = True
    usuario.is_superuser = False
    return usuario


def _crear_no_admin_mock():
    usuario = MagicMock()
    usuario.username = "visitante"
    usuario.is_authenticated = True
    usuario.is_active = True
    usuario.is_staff = False
    usuario.is_superuser = False
    return usuario


class PanelAdministrativoTest(SimpleTestCase):

    def setUp(self):

        super().setUp()

        parche_noticias = patch(
            "core.context_processors.Noticia"
        )
        self.noticias_cp_mock = parche_noticias.start()
        self.addCleanup(parche_noticias.stop)
        self.noticias_cp_mock.objects.filter.return_value \
            .order_by.return_value = []

        parche_areas = patch(
            "core.context_processors.areas_activas"
        )
        self.areas_cp_mock = parche_areas.start()
        self.addCleanup(parche_areas.stop)
        self.areas_cp_mock.return_value = []

        parche_contador = patch(
            "core.context_processors.Visita"
        )
        self.contador_mock = parche_contador.start()
        self.addCleanup(parche_contador.stop)
        self.contador_mock.objects.count.return_value = 0

        parche_registro = patch(
            "core.middleware.Visita"
        )
        self.registro_mock = parche_registro.start()
        self.addCleanup(parche_registro.stop)

        parche_usuarios = patch(
            "core.middleware.registrar_usuario_conectado"
        )
        self.usuarios_mock = parche_usuarios.start()
        self.addCleanup(parche_usuarios.stop)

        parche_conectados = patch(
            "core.context_processors.contar_usuarios_conectados"
        )
        self.conectados_mock = parche_conectados.start()
        self.addCleanup(parche_conectados.stop)
        self.conectados_mock.return_value = 0

        self.categoria = CategoriaProducto(
            id_categoria=1,
            nombre="Material eléctrico",
            descripcion="Componentes industriales",
            activo=True
        )

        self.producto = Producto(
            id_producto=1,
            categoria=self.categoria,
            codigo="PROD-001",
            nombre="Interruptor termomagnético",
            marca="Siemens",
            modelo="MOD-001",
            precio=Decimal("450.00"),
            stock=25,
            activo=True
        )

        self.area = AreaServicio(
            id_area=1,
            nombre="Ingeniería eléctrica",
            activo=True
        )

        self.solicitud = SolicitudServicio(
            id_solicitud=1,
            area=self.area,
            nombre="Juan Pérez",
            empresa="Empresa A",
            correo="juan@example.com",
            telefono="0000000001",
            detalle="Solicitud de instalación eléctrica",
            estatus=SolicitudServicio.Estatus.PENDIENTE,
            fecha_solicitud=timezone.now()
        )

        self.sugerencia = Sugerencia(
            id_sugerencia=1,
            nombre="Cliente de prueba",
            correo="cliente@example.com",
            mensaje="Ampliar catálogo de herramientas",
            leida=False,
            fecha_registro=timezone.now()
        )

        self.noticia = Noticia(
            id_noticia=1,
            titulo="Noticia institucional",
            resumen="Resumen de prueba",
            contenido="Contenido de noticia",
            fecha_publicacion=timezone.now(),
            activo=True
        )

        self.cliente = Cliente(
            id_cliente=1,
            nombre="FEMSA",
            logo="clientes/femsa.webp",
            sitio_web="https://femsa.com",
            activo=True
        )

        self.slider = Slider(
            id_slider=1,
            titulo="Soluciones de ingeniería",
            imagen="slider/ingenieria.jpg",
            enlace="/servicios/",
            orden=1,
            activo=True
        )

    # =========================================
    # PROTECCION DE RUTAS PRIVADAS DEL PANEL
    # =========================================

    def test_acceso_restringido_visitante_anonimo(self):

        rutas = [
            "gestion:panel",
            "gestion:productos_lista",
            "gestion:producto_crear",
            "gestion:categorias_lista",
            "gestion:categoria_crear",
            "gestion:solicitudes_lista",
            "gestion:sugerencias_lista",
            "gestion:noticias_lista",
            "gestion:clientes_lista",
            "gestion:slider_lista",
        ]

        for nombre_ruta in rutas:
            with self.subTest(ruta=nombre_ruta):
                respuesta = self.client.get(
                    reverse(nombre_ruta)
                )
                self.assertEqual(
                    respuesta.status_code,
                    302
                )
                self.assertIn(
                    reverse("autenticacion:iniciar_sesion"),
                    respuesta["Location"]
                )

    @patch("django.contrib.auth.middleware.get_user")
    def test_acceso_restringido_usuario_no_staff(
        self,
        get_user_mock
    ):

        get_user_mock.return_value = _crear_no_admin_mock()

        respuesta = self.client.get(
            reverse("gestion:panel")
        )

        self.assertEqual(respuesta.status_code, 403)

    # =========================================
    # 9.1 Y 9.9 DASHBOARD GENERAL E INTEGRACION
    # =========================================

    @patch("django.contrib.auth.middleware.get_user")
    @patch("gestion.views.Slider")
    @patch("gestion.views.Cliente")
    @patch("gestion.views.Noticia")
    @patch("gestion.views.Sugerencia")
    @patch("gestion.views.SolicitudServicio")
    @patch("gestion.views.CategoriaProducto")
    @patch("gestion.views.obtener_dashboard_productos")
    @patch("gestion.views.obtener_dashboard_servicios")
    @patch("gestion.views.obtener_reporte_inventario")
    def test_dashboard_panel_administrativo(
        self,
        inv_mock,
        dash_serv_mock,
        dash_prod_mock,
        cat_mock,
        sol_mock,
        sug_mock,
        not_mock,
        cli_mock,
        sli_mock,
        get_user_mock,
    ):

        get_user_mock.return_value = _crear_admin_mock()
        inv_mock.return_value = [self.producto]
        dash_serv_mock.return_value = [
            {"id_area": 1, "servicio": "Ingeniería eléctrica", "total": 4}
        ]
        dash_prod_mock.return_value = [
            {"id_categoria": 1, "categoria": "Material eléctrico", "total": 2}
        ]

        cat_mock.objects.count.return_value = 5
        sol_mock.objects.count.return_value = 4
        sol_mock.objects.filter.return_value.count.return_value = 2
        sug_mock.objects.count.return_value = 3
        sug_mock.objects.filter.return_value.count.return_value = 1
        not_mock.objects.count.return_value = 2
        cli_mock.objects.count.return_value = 2
        sli_mock.objects.count.return_value = 3

        respuesta = self.client.get(
            reverse("gestion:panel")
        )

        self.assertEqual(respuesta.status_code, 200)
        self.assertTemplateUsed(
            respuesta,
            "gestion/panel/dashboard.html"
        )
        self.assertContains(
            respuesta,
            "Dashboard Integrado: Solicitudes por Tipo de Servicio"
        )
        self.assertContains(
            respuesta,
            "Dashboard Integrado: Productos por Categoría"
        )

    # =========================================
    # 9.2 CRUD DE PRODUCTOS Y VALIDACIONES
    # =========================================

    @patch.object(ProductoForm, "validate_unique")
    def test_validacion_precio_y_stock_negativos(
        self,
        validate_unique_mock
    ):

        form = ProductoForm(
            data={
                "codigo": "PROD-999",
                "nombre": "Producto inválido",
                "precio": "-10.00",
                "stock": "-5",
            }
        )

        self.assertFalse(form.is_valid())
        self.assertIn("precio", form.errors)
        self.assertIn("stock", form.errors)

    @patch("django.contrib.auth.middleware.get_user")
    @patch("gestion.views.CategoriaProducto")
    @patch("gestion.views.Producto")
    def test_listado_administrativo_productos(
        self,
        prod_mock,
        cat_mock,
        get_user_mock
    ):

        get_user_mock.return_value = _crear_admin_mock()
        prod_mock.objects.select_related.return_value \
            .order_by.return_value = [self.producto]
        cat_mock.objects.order_by.return_value = [self.categoria]

        respuesta = self.client.get(
            reverse("gestion:productos_lista")
        )

        self.assertEqual(respuesta.status_code, 200)
        self.assertTemplateUsed(
            respuesta,
            "gestion/panel/productos_lista.html"
        )
        self.assertContains(
            respuesta,
            "Interruptor termomagnético"
        )

    @patch("django.contrib.auth.middleware.get_user")
    @patch("gestion.views.get_object_or_404")
    def test_eliminar_producto(
        self,
        obtener_mock,
        get_user_mock
    ):

        get_user_mock.return_value = _crear_admin_mock()
        prod_instancia = MagicMock()
        prod_instancia.nombre = "Interruptor termomagnético"
        obtener_mock.return_value = prod_instancia

        respuesta = self.client.post(
            reverse(
                "gestion:producto_eliminar",
                kwargs={"id_producto": 1}
            )
        )

        self.assertEqual(respuesta.status_code, 302)
        prod_instancia.delete.assert_called_once()

    # =========================================
    # 9.3 CRUD DE CATEGORIAS
    # =========================================

    @patch("django.contrib.auth.middleware.get_user")
    @patch("gestion.views.CategoriaProducto")
    def test_listado_administrativo_categorias(
        self,
        cat_mock,
        get_user_mock
    ):

        get_user_mock.return_value = _crear_admin_mock()
        cat_mock.objects.order_by.return_value = [self.categoria]

        respuesta = self.client.get(
            reverse("gestion:categorias_lista")
        )

        self.assertEqual(respuesta.status_code, 200)
        self.assertTemplateUsed(
            respuesta,
            "gestion/panel/categorias_lista.html"
        )
        self.assertContains(
            respuesta,
            "Material eléctrico"
        )

    # =========================================
    # 9.4 ADMINISTRACION DE SOLICITUDES DE SERVICIOS
    # =========================================

    @patch("django.contrib.auth.middleware.get_user")
    @patch("gestion.views.AreaServicio")
    @patch("gestion.views.SolicitudServicio")
    def test_listado_solicitudes_servicios(
        self,
        sol_mock,
        area_mock,
        get_user_mock
    ):

        get_user_mock.return_value = _crear_admin_mock()
        sol_mock.Estatus = SolicitudServicio.Estatus
        sol_mock.objects.select_related.return_value \
            .order_by.return_value = [self.solicitud]
        area_mock.objects.order_by.return_value = [self.area]

        respuesta = self.client.get(
            reverse("gestion:solicitudes_lista")
        )

        self.assertEqual(respuesta.status_code, 200)
        self.assertTemplateUsed(
            respuesta,
            "gestion/panel/solicitudes_lista.html"
        )
        self.assertContains(
            respuesta,
            "Juan Pérez"
        )

    @patch("django.contrib.auth.middleware.get_user")
    @patch("gestion.views.SolicitudServicioEstatusForm")
    @patch("gestion.views.get_object_or_404")
    def test_actualizar_estatus_solicitud(
        self,
        obtener_mock,
        form_mock,
        get_user_mock
    ):

        get_user_mock.return_value = _crear_admin_mock()
        obtener_mock.return_value = self.solicitud

        instancia_form = MagicMock()
        instancia_form.is_valid.return_value = True
        form_mock.return_value = instancia_form

        respuesta = self.client.post(
            reverse(
                "gestion:solicitud_detalle",
                kwargs={"id_solicitud": 1}
            ),
            {"estatus": "En proceso"}
        )

        self.assertEqual(respuesta.status_code, 302)
        instancia_form.save.assert_called_once()

    # =========================================
    # 9.5 ADMINISTRACION Y PAGINACION DE SUGERENCIAS
    # =========================================

    @patch("django.contrib.auth.middleware.get_user")
    @patch("gestion.views.Sugerencia")
    def test_paginacion_sugerencias(
        self,
        sug_mock,
        get_user_mock
    ):

        get_user_mock.return_value = _crear_admin_mock()

        lista_sugerencias = [
            Sugerencia(
                id_sugerencia=i,
                nombre=f"Visitante {i}",
                correo=f"visitante{i}@example.com",
                mensaje=f"Sugerencia número {i}",
                leida=False,
                fecha_registro=timezone.now()
            )
            for i in range(1, 14)
        ]

        sug_mock.objects.all.return_value \
            .order_by.return_value = lista_sugerencias

        config = ConfiguracionSistema()
        valor_original = config.registros_por_pagina

        try:
            config.registros_por_pagina = 10

            resp_p1 = self.client.get(
                reverse("gestion:sugerencias_lista")
            )
            self.assertEqual(resp_p1.status_code, 200)
            self.assertEqual(
                len(resp_p1.context["pagina"].object_list),
                10
            )
            self.assertContains(
                resp_p1,
                reverse("reportes:sugerencias_excel")
            )
            self.assertContains(
                resp_p1,
                reverse("reportes:sugerencias_pdf")
            )

            resp_p2 = self.client.get(
                reverse("gestion:sugerencias_lista"),
                {"page": 2}
            )
            self.assertEqual(
                len(resp_p2.context["pagina"].object_list),
                3
            )
        finally:
            config.registros_por_pagina = valor_original

    @patch("django.contrib.auth.middleware.get_user")
    @patch("gestion.views.get_object_or_404")
    def test_marcar_sugerencia_leida(
        self,
        obtener_mock,
        get_user_mock
    ):

        get_user_mock.return_value = _crear_admin_mock()
        sug_instancia = MagicMock()
        sug_instancia.id_sugerencia = 1
        sug_instancia.leida = False
        obtener_mock.return_value = sug_instancia

        respuesta = self.client.post(
            reverse(
                "gestion:sugerencia_marcar_leida",
                kwargs={"id_sugerencia": 1}
            )
        )

        self.assertEqual(respuesta.status_code, 302)
        self.assertTrue(sug_instancia.leida)
        sug_instancia.save.assert_called_once()

    # =========================================
    # 9.6, 9.7 Y 9.8 NOTICIAS, CLIENTES Y SLIDER
    # =========================================

    @patch("django.contrib.auth.middleware.get_user")
    @patch("gestion.views.Noticia")
    def test_listado_administrativo_noticias(
        self,
        noticia_mock,
        get_user_mock
    ):

        get_user_mock.return_value = _crear_admin_mock()
        noticia_mock.objects.all.return_value \
            .order_by.return_value = [self.noticia]

        respuesta = self.client.get(
            reverse("gestion:noticias_lista")
        )

        self.assertEqual(respuesta.status_code, 200)
        self.assertTemplateUsed(
            respuesta,
            "gestion/panel/noticias_lista.html"
        )
        self.assertContains(
            respuesta,
            "Noticia institucional"
        )

    @patch("django.contrib.auth.middleware.get_user")
    @patch("gestion.views.Cliente")
    def test_listado_administrativo_clientes(
        self,
        cliente_mock,
        get_user_mock
    ):

        get_user_mock.return_value = _crear_admin_mock()
        cliente_mock.objects.all.return_value \
            .order_by.return_value = [self.cliente]

        respuesta = self.client.get(
            reverse("gestion:clientes_lista")
        )

        self.assertEqual(respuesta.status_code, 200)
        self.assertTemplateUsed(
            respuesta,
            "gestion/panel/clientes_lista.html"
        )
        self.assertContains(respuesta, "FEMSA")

    @patch("django.contrib.auth.middleware.get_user")
    @patch("gestion.views.Slider")
    def test_listado_administrativo_slider(
        self,
        slider_mock,
        get_user_mock
    ):

        get_user_mock.return_value = _crear_admin_mock()
        slider_mock.objects.all.return_value \
            .order_by.return_value = [self.slider]

        respuesta = self.client.get(
            reverse("gestion:slider_lista")
        )

        self.assertEqual(respuesta.status_code, 200)
        self.assertTemplateUsed(
            respuesta,
            "gestion/panel/slider_lista.html"
        )
        self.assertContains(
            respuesta,
            "Soluciones de ingeniería"
        )

    def test_archivos_estaticos_gestion(self):

        self.assertIsNotNone(
            finders.find("css/gestion.css")
        )
        self.assertIsNotNone(
            finders.find("js/gestion.js")
        )
