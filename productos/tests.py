from decimal import Decimal
from unittest.mock import patch

from django.contrib.staticfiles import finders
from django.http import Http404
from django.test import SimpleTestCase
from django.urls import reverse

from core.patrones.singleton import ConfiguracionSistema

from .models import CategoriaProducto, Producto
from .pdf import generar_ficha_tecnica_pdf


class ProductosTest(SimpleTestCase):

    def setUp(self):

        super().setUp()

        # Simular noticias de la barra lateral
        parche_noticias = patch(
            "core.context_processors.Noticia"
        )
        self.noticias_mock = parche_noticias.start()
        self.addCleanup(parche_noticias.stop)
        self.noticias_mock.objects.filter.return_value \
            .order_by.return_value = []

        # Simular areas de la barra lateral
        parche_areas = patch(
            "core.context_processors.areas_activas"
        )
        self.areas_mock = parche_areas.start()
        self.addCleanup(parche_areas.stop)
        self.areas_mock.return_value = []

        # Simular contador de visitas
        parche_contador = patch(
            "core.context_processors.Visita"
        )
        self.contador_mock = parche_contador.start()
        self.addCleanup(parche_contador.stop)
        self.contador_mock.objects.count.return_value = 0

        # Simular registro de visitas
        parche_registro = patch(
            "core.middleware.Visita"
        )
        self.registro_mock = parche_registro.start()
        self.addCleanup(parche_registro.stop)

        # Simular registro de usuarios conectados
        parche_usuarios = patch(
            "core.middleware.registrar_usuario_conectado"
        )
        self.usuarios_mock = parche_usuarios.start()
        self.addCleanup(parche_usuarios.stop)

        # Simular contador de usuarios conectados
        parche_conectados = patch(
            "core.context_processors.contar_usuarios_conectados"
        )
        self.conectados_mock = parche_conectados.start()
        self.addCleanup(parche_conectados.stop)
        self.conectados_mock.return_value = 0

        # Objetos de prueba en memoria
        self.categoria = CategoriaProducto(
            id_categoria=1,
            nombre="Material eléctrico",
            descripcion="Componentes eléctricos industriales",
            activo=True
        )

        self.categoria_automatizacion = CategoriaProducto(
            id_categoria=2,
            nombre="Automatización",
            descripcion="Equipos de automatización industrial",
            activo=True
        )

        self.producto = Producto(
            id_producto=1,
            categoria=self.categoria,
            codigo="PROD-001",
            nombre="Interruptor termomagnético",
            descripcion="Interruptor para protección eléctrica",
            marca="Siemens",
            modelo="MOD-001",
            precio=Decimal("450.00"),
            stock=25,
            imagen="productos/interruptor.jpg",
            ficha_tecnica="Corriente nominal 32A, 240V AC.",
            activo=True
        )

        self.producto_agotado = Producto(
            id_producto=4,
            categoria=self.categoria_automatizacion,
            codigo="PROD-004",
            nombre="Casco de seguridad",
            descripcion="Casco de protección industrial",
            marca="3M",
            modelo="MOD-004",
            precio=Decimal("350.00"),
            stock=0,
            imagen="productos/casco.jpg",
            ficha_tecnica="Norma NOM-115-STPS.",
            activo=True
        )

    # =========================================
    # MODELOS Y PROPIEDADES
    # =========================================

    def test_estatus_producto_existencia_y_agotado(self):

        self.assertEqual(
            self.producto.estatus,
            "Existencia"
        )

        self.assertEqual(
            self.producto_agotado.estatus,
            "Agotado"
        )

    def test_imagen_url_producto(self):

        self.assertEqual(
            self.producto.imagen_url,
            "/media/productos/interruptor.jpg"
        )

        producto_sin_img = Producto(
            id_producto=9,
            categoria=self.categoria,
            codigo="PROD-009",
            nombre="Sin imagen",
            imagen=""
        )

        self.assertEqual(
            producto_sin_img.imagen_url,
            ""
        )

    # =========================================
    # CATALOGO DINAMICO DE PRODUCTOS (5.2)
    # =========================================

    @patch("productos.views.productos_activos")
    @patch("productos.views.categorias_activas")
    def test_listado_productos(
        self,
        categorias_mock,
        productos_mock
    ):

        categorias_mock.return_value = [self.categoria]
        productos_mock.return_value = [
            self.producto,
            self.producto_agotado
        ]

        respuesta = self.client.get(
            reverse("productos:listado")
        )

        self.assertEqual(
            respuesta.status_code,
            200
        )

        self.assertTemplateUsed(
            respuesta,
            "productos/listado.html"
        )

        self.assertContains(
            respuesta,
            "Interruptor termomagnético"
        )

        self.assertContains(
            respuesta,
            "productos/interruptor.jpg"
        )

        self.assertContains(
            respuesta,
            "Existencia"
        )

        self.assertContains(
            respuesta,
            "Agotado"
        )

    @patch("productos.views.productos_activos")
    @patch("productos.views.categorias_activas")
    def test_listado_vacio(
        self,
        categorias_mock,
        productos_mock
    ):

        categorias_mock.return_value = []
        productos_mock.return_value = []

        respuesta = self.client.get(
            reverse("productos:listado")
        )

        self.assertEqual(
            respuesta.status_code,
            200
        )

        self.assertContains(
            respuesta,
            "No se encontraron productos disponibles"
        )

    # =========================================
    # BUSCADOR Y FILTROS POR CATEGORIAS (5.3)
    # =========================================

    @patch("productos.views.productos_activos")
    @patch("productos.views.categorias_activas")
    def test_buscador_y_filtro_categoria(
        self,
        categorias_mock,
        productos_mock
    ):

        categorias_mock.return_value = [
            self.categoria,
            self.categoria_automatizacion
        ]
        productos_mock.return_value = [self.producto]

        respuesta = self.client.get(
            reverse("productos:listado"),
            {"q": "Siemens", "categoria": "1"}
        )

        self.assertEqual(
            respuesta.status_code,
            200
        )

        productos_mock.assert_called_once_with(
            busqueda="Siemens",
            id_categoria=1
        )

        self.assertEqual(
            respuesta.context["busqueda"],
            "Siemens"
        )

        self.assertEqual(
            respuesta.context["categoria_actual"],
            1
        )

    # =========================================
    # PAGINACION DEL CATALOGO (5.5)
    # =========================================

    @patch("productos.views.productos_activos")
    @patch("productos.views.categorias_activas")
    def test_paginacion_catalogo(
        self,
        categorias_mock,
        productos_mock
    ):

        categorias_mock.return_value = [self.categoria]

        lista_productos = [
            Producto(
                id_producto=i,
                categoria=self.categoria,
                codigo=f"PROD-{i:03d}",
                nombre=f"Producto industrial {i}",
                precio=Decimal("100.00"),
                stock=5,
                activo=True
            )
            for i in range(1, 15)
        ]

        productos_mock.return_value = lista_productos

        config = ConfiguracionSistema()
        valor_original = config.registros_por_pagina

        try:
            config.registros_por_pagina = 10

            respuesta_p1 = self.client.get(
                reverse("productos:listado")
            )

            self.assertEqual(
                len(respuesta_p1.context["pagina"].object_list),
                10
            )
            self.assertContains(
                respuesta_p1,
                "Página 1"
            )

            respuesta_p2 = self.client.get(
                reverse("productos:listado"),
                {"page": 2}
            )

            self.assertEqual(
                len(respuesta_p2.context["pagina"].object_list),
                4
            )
        finally:
            config.registros_por_pagina = valor_original

    # =========================================
    # PAGINA DE DETALLE DE PRODUCTO (5.4)
    # =========================================

    @patch("productos.views.get_object_or_404")
    def test_detalle_producto(self, obtener_mock):

        obtener_mock.return_value = self.producto

        respuesta = self.client.get(
            reverse(
                "productos:detalle",
                kwargs={"id_producto": 1}
            )
        )

        self.assertEqual(
            respuesta.status_code,
            200
        )

        self.assertTemplateUsed(
            respuesta,
            "productos/detalle.html"
        )

        self.assertContains(
            respuesta,
            "Interruptor termomagnético"
        )

        self.assertContains(
            respuesta,
            "Corriente nominal 32A"
        )

        self.assertContains(
            respuesta,
            reverse(
                "productos:ficha_pdf",
                kwargs={"id_producto": 1}
            )
        )

    @patch("productos.views.get_object_or_404")
    def test_detalle_producto_no_disponible(
        self,
        obtener_mock
    ):

        obtener_mock.side_effect = Http404

        respuesta = self.client.get(
            reverse(
                "productos:detalle",
                kwargs={"id_producto": 999}
            )
        )

        self.assertEqual(
            respuesta.status_code,
            404
        )

    # =========================================
    # GENERACION DE FICHA TECNICA EN PDF (5.6)
    # =========================================

    def test_generador_pdf_estructura_valida(self):

        pdf_bytes = generar_ficha_tecnica_pdf(
            self.producto
        )

        self.assertTrue(
            pdf_bytes.startswith(b"%PDF-1.4")
        )

        self.assertIn(
            b"PROD-001",
            pdf_bytes
        )

        self.assertIn(
            b"Siemens",
            pdf_bytes
        )

        self.assertTrue(
            pdf_bytes.strip().endswith(b"%%EOF")
        )

    @patch("productos.views.get_object_or_404")
    def test_descarga_ficha_tecnica_pdf(
        self,
        obtener_mock
    ):

        obtener_mock.return_value = self.producto

        respuesta = self.client.get(
            reverse(
                "productos:ficha_pdf",
                kwargs={"id_producto": 1}
            )
        )

        self.assertEqual(
            respuesta.status_code,
            200
        )

        self.assertEqual(
            respuesta["Content-Type"],
            "application/pdf"
        )

        self.assertIn(
            'attachment; filename="ficha_tecnica_prod-001.pdf"',
            respuesta["Content-Disposition"]
        )

        self.assertTrue(
            respuesta.content.startswith(b"%PDF-1.4")
        )

    # =========================================
    # API REST DE PRODUCTOS Y CATEGORIAS (5.7)
    # =========================================

    @patch("productos.views.productos_activos")
    def test_api_listado_productos(
        self,
        productos_mock
    ):

        productos_mock.return_value = [self.producto]

        respuesta = self.client.get(
            reverse("productos:api_productos"),
            {"q": "Interruptor", "categoria": "1"}
        )

        self.assertEqual(
            respuesta.status_code,
            200
        )

        self.assertEqual(
            respuesta["Content-Type"],
            "application/json"
        )

        datos = respuesta.json()

        self.assertEqual(
            datos["total"],
            1
        )

        item = datos["resultados"][0]
        self.assertEqual(item["codigo"], "PROD-001")
        self.assertEqual(item["estatus"], "Existencia")
        self.assertEqual(
            item["categoria"]["nombre"],
            "Material eléctrico"
        )

    @patch("productos.views.get_object_or_404")
    def test_api_detalle_producto(
        self,
        obtener_mock
    ):

        obtener_mock.return_value = self.producto

        respuesta = self.client.get(
            reverse(
                "productos:api_detalle_producto",
                kwargs={"id_producto": 1}
            )
        )

        self.assertEqual(
            respuesta.status_code,
            200
        )

        datos = respuesta.json()
        self.assertEqual(datos["id_producto"], 1)
        self.assertEqual(datos["codigo"], "PROD-001")
        self.assertEqual(datos["marca"], "Siemens")

    @patch("productos.views.categorias_activas")
    def test_api_categorias(self, categorias_mock):

        categorias_mock.return_value = [
            self.categoria,
            self.categoria_automatizacion
        ]

        respuesta = self.client.get(
            reverse("productos:api_categorias")
        )

        self.assertEqual(
            respuesta.status_code,
            200
        )

        datos = respuesta.json()
        self.assertEqual(datos["total"], 2)
        self.assertEqual(
            datos["resultados"][0]["nombre"],
            "Material eléctrico"
        )

    # =========================================
    # ARCHIVOS ESTATICOS Y MENU PRINCIPAL
    # =========================================

    def test_archivos_estaticos_productos(self):

        self.assertIsNotNone(
            finders.find("css/productos.css")
        )

        self.assertIsNotNone(
            finders.find("js/productos.js")
        )
