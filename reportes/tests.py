from decimal import Decimal
from io import BytesIO
from unittest.mock import MagicMock, patch
import zipfile

from django.contrib.staticfiles import finders
from django.test import SimpleTestCase
from django.urls import reverse
from django.utils import timezone

from comunicacion.models import Sugerencia
from productos.models import CategoriaProducto, Producto

from .consultas import resumen_inventario
from .exportacion import (
    generar_inventario_excel,
    generar_inventario_pdf,
    generar_sugerencias_excel,
    generar_sugerencias_pdf,
)


def _crear_admin_mock():
    usuario = MagicMock()
    usuario.is_authenticated = True
    usuario.is_active = True
    usuario.is_staff = True
    usuario.is_superuser = False
    return usuario


def _crear_no_admin_mock():
    usuario = MagicMock()
    usuario.is_authenticated = True
    usuario.is_active = True
    usuario.is_staff = False
    usuario.is_superuser = False
    return usuario


class ReportesTest(SimpleTestCase):

    def setUp(self):

        super().setUp()

        parche_noticias = patch(
            "core.context_processors.Noticia"
        )
        self.noticias_mock = parche_noticias.start()
        self.addCleanup(parche_noticias.stop)
        self.noticias_mock.objects.filter.return_value \
            .order_by.return_value = []

        parche_areas = patch(
            "core.context_processors.areas_activas"
        )
        self.areas_mock = parche_areas.start()
        self.addCleanup(parche_areas.stop)
        self.areas_mock.return_value = []

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
            activo=True
        )

        self.prod_existencia = Producto(
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

        self.prod_agotado = Producto(
            id_producto=4,
            categoria=self.categoria,
            codigo="PROD-004",
            nombre="Casco de seguridad",
            marca="3M",
            modelo="MOD-004",
            precio=Decimal("350.00"),
            stock=0,
            activo=True
        )

        self.sugerencia = Sugerencia(
            id_sugerencia=1,
            nombre="Usuario de prueba",
            correo="usuario@example.com",
            mensaje="Agregar más información de productos",
            leida=False,
            fecha_registro=timezone.now()
        )

        self.datos_servicios = [
            {
                "id_area": 1,
                "servicio": "Ingeniería eléctrica",
                "total": 3,
            },
            {
                "id_area": 2,
                "servicio": "Automatización industrial",
                "total": 5,
            },
        ]

        self.datos_productos = [
            {
                "id_categoria": 1,
                "categoria": "Material eléctrico",
                "total": 4,
            },
            {
                "id_categoria": 2,
                "categoria": "Automatización",
                "total": 2,
            },
        ]

    # =========================================
    # PROTECCION MEDIANTE PERMISOS ADMINISTRATIVOS
    # =========================================

    def test_acceso_denegado_visitante_anonimo(self):

        rutas = [
            "reportes:panel",
            "reportes:inventario",
            "reportes:inventario_pdf",
            "reportes:inventario_excel",
            "reportes:sugerencias_excel",
            "reportes:sugerencias_pdf",
            "reportes:dashboard_servicios",
            "reportes:dashboard_productos",
            "reportes:api_dashboards",
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
    def test_acceso_denegado_usuario_sin_rol_admin(
        self,
        get_user_mock
    ):

        get_user_mock.return_value = _crear_no_admin_mock()

        respuesta = self.client.get(
            reverse("reportes:inventario")
        )

        self.assertEqual(
            respuesta.status_code,
            403
        )

    # =========================================
    # REPORTE DE INVENTARIO Y CLASIFICACION (10.1, 10.2)
    # =========================================

    def test_resumen_y_clasificacion_existencias(self):

        productos = [
            self.prod_existencia,
            self.prod_agotado
        ]

        metricas = resumen_inventario(productos)

        self.assertEqual(metricas["total_productos"], 2)
        self.assertEqual(metricas["en_existencia"], 1)
        self.assertEqual(metricas["agotados"], 1)
        self.assertEqual(metricas["unidades_totales"], 25)

        self.assertEqual(
            self.prod_existencia.estatus,
            "Existencia"
        )
        self.assertEqual(
            self.prod_agotado.estatus,
            "Agotado"
        )

    @patch("django.contrib.auth.middleware.get_user")
    @patch("reportes.views.categorias_activas")
    @patch("reportes.views.obtener_reporte_inventario")
    def test_vista_reporte_inventario(
        self,
        inventario_mock,
        categorias_mock,
        get_user_mock
    ):

        get_user_mock.return_value = _crear_admin_mock()
        categorias_mock.return_value = [self.categoria]
        inventario_mock.return_value = [
            self.prod_existencia,
            self.prod_agotado
        ]

        respuesta = self.client.get(
            reverse("reportes:inventario")
        )

        self.assertEqual(
            respuesta.status_code,
            200
        )

        self.assertTemplateUsed(
            respuesta,
            "reportes/inventario.html"
        )

        self.assertContains(
            respuesta,
            "Interruptor termomagnético"
        )
        self.assertContains(
            respuesta,
            "Casco de seguridad"
        )
        self.assertContains(
            respuesta,
            "Existencia"
        )
        self.assertContains(
            respuesta,
            "Agotado"
        )

    # =========================================
    # EXPORTACION DE INVENTARIO (10.3)
    # =========================================

    def test_generacion_archivos_inventario(self):

        productos = [
            self.prod_existencia,
            self.prod_agotado
        ]

        pdf_bytes = generar_inventario_pdf(productos)
        self.assertTrue(pdf_bytes.startswith(b"%PDF-1.4"))
        self.assertIn(b"PROD-001", pdf_bytes)
        self.assertIn(b"Existencia", pdf_bytes)
        self.assertIn(b"Agotado", pdf_bytes)

        xlsx_bytes = generar_inventario_excel(productos)
        with zipfile.ZipFile(BytesIO(xlsx_bytes), "r") as zf:
            hoja = zf.read("xl/worksheets/sheet1.xml").decode("utf-8")
            self.assertIn("PROD-001", hoja)
            self.assertIn("Existencia", hoja)
            self.assertIn("Agotado", hoja)

    @patch("django.contrib.auth.middleware.get_user")
    @patch("reportes.views.obtener_reporte_inventario")
    def test_descarga_inventario_pdf_y_excel(
        self,
        inventario_mock,
        get_user_mock
    ):

        get_user_mock.return_value = _crear_admin_mock()
        inventario_mock.return_value = [self.prod_existencia]

        resp_pdf = self.client.get(
            reverse("reportes:inventario_pdf")
        )
        self.assertEqual(resp_pdf.status_code, 200)
        self.assertEqual(
            resp_pdf["Content-Type"],
            "application/pdf"
        )
        self.assertTrue(
            resp_pdf.content.startswith(b"%PDF-1.4")
        )

        resp_xlsx = self.client.get(
            reverse("reportes:inventario_excel")
        )
        self.assertEqual(resp_xlsx.status_code, 200)
        self.assertIn(
            "spreadsheetml.sheet",
            resp_xlsx["Content-Type"]
        )

    # =========================================
    # EXPORTACION DE SUGERENCIAS A EXCEL Y PDF (10.4, 10.5)
    # =========================================

    def test_generacion_sugerencias_excel_y_pdf(self):

        xlsx_bytes = generar_sugerencias_excel([self.sugerencia])
        with zipfile.ZipFile(BytesIO(xlsx_bytes), "r") as zf:
            hoja = zf.read("xl/worksheets/sheet1.xml").decode("utf-8")
            self.assertIn("Usuario de prueba", hoja)
            self.assertIn("usuario@example.com", hoja)

        pdf_bytes = generar_sugerencias_pdf([self.sugerencia])
        self.assertTrue(pdf_bytes.startswith(b"%PDF-1.4"))
        self.assertIn(b"Usuario de prueba", pdf_bytes)

    @patch("django.contrib.auth.middleware.get_user")
    @patch("reportes.views.obtener_sugerencias_reporte")
    def test_descarga_sugerencias_excel_y_pdf(
        self,
        sugerencias_mock,
        get_user_mock
    ):

        get_user_mock.return_value = _crear_admin_mock()
        sugerencias_mock.return_value = [self.sugerencia]

        resp_excel = self.client.get(
            reverse("reportes:sugerencias_excel")
        )
        self.assertEqual(resp_excel.status_code, 200)
        self.assertIn(
            "reporte_sugerencias_parnet.xlsx",
            resp_excel["Content-Disposition"]
        )

        resp_pdf = self.client.get(
            reverse("reportes:sugerencias_pdf")
        )
        self.assertEqual(resp_pdf.status_code, 200)
        self.assertEqual(
            resp_pdf["Content-Type"],
            "application/pdf"
        )
        self.assertIn(
            "reporte_sugerencias_parnet.pdf",
            resp_pdf["Content-Disposition"]
        )

    # =========================================
    # DASHBOARDS DE SERVICIOS Y PRODUCTOS (10.6, 10.7)
    # =========================================

    @patch("django.contrib.auth.middleware.get_user")
    @patch("reportes.views.obtener_dashboard_servicios")
    def test_dashboard_servicios(
        self,
        servicios_mock,
        get_user_mock
    ):

        get_user_mock.return_value = _crear_admin_mock()
        servicios_mock.return_value = [
            dict(item) for item in self.datos_servicios
        ]

        respuesta = self.client.get(
            reverse("reportes:dashboard_servicios")
        )

        self.assertEqual(respuesta.status_code, 200)
        self.assertTemplateUsed(
            respuesta,
            "reportes/dashboard_servicios.html"
        )
        self.assertContains(
            respuesta,
            "Automatización industrial"
        )
        self.assertEqual(
            respuesta.context["total_solicitudes"],
            8
        )

    @patch("django.contrib.auth.middleware.get_user")
    @patch("reportes.views.obtener_dashboard_productos")
    def test_dashboard_productos(
        self,
        productos_mock,
        get_user_mock
    ):

        get_user_mock.return_value = _crear_admin_mock()
        productos_mock.return_value = [
            dict(item) for item in self.datos_productos
        ]

        respuesta = self.client.get(
            reverse("reportes:dashboard_productos")
        )

        self.assertEqual(respuesta.status_code, 200)
        self.assertTemplateUsed(
            respuesta,
            "reportes/dashboard_productos.html"
        )
        self.assertContains(
            respuesta,
            "Material eléctrico"
        )
        self.assertEqual(
            respuesta.context["total_productos"],
            6
        )

    @patch("django.contrib.auth.middleware.get_user")
    @patch("reportes.views.obtener_dashboard_productos")
    @patch("reportes.views.obtener_dashboard_servicios")
    def test_api_dashboards(
        self,
        servicios_mock,
        productos_mock,
        get_user_mock
    ):

        get_user_mock.return_value = _crear_admin_mock()
        servicios_mock.return_value = [
            dict(item) for item in self.datos_servicios
        ]
        productos_mock.return_value = [
            dict(item) for item in self.datos_productos
        ]

        respuesta = self.client.get(
            reverse("reportes:api_dashboards")
        )

        self.assertEqual(respuesta.status_code, 200)
        datos = respuesta.json()
        self.assertEqual(
            datos["servicios"]["valores"],
            [3, 5]
        )
        self.assertEqual(
            datos["productos"]["valores"],
            [4, 2]
        )

    def test_archivos_estaticos_reportes(self):

        self.assertIsNotNone(
            finders.find("css/reportes.css")
        )
        self.assertIsNotNone(
            finders.find("js/reportes.js")
        )
