from unittest.mock import patch

from django.contrib.staticfiles import finders
from django.test import SimpleTestCase
from django.urls import reverse
from django.utils import timezone

from core.models import Noticia, Slider, Cliente
from core.patrones.singleton import ConfiguracionSistema


def simular_slider(mock, imagenes=None):
    mock.objects.filter.return_value.exclude.return_value.order_by.return_value = (
        [] if imagenes is None else imagenes
    )


def simular_noticias(mock, noticias=None):
    mock.objects.filter.return_value.order_by.return_value = (
        [] if noticias is None else noticias
    )


# =========================================
# PATRON SINGLETON
# =========================================

class ConfiguracionSistemaTest(SimpleTestCase):

    def test_instancia_unica(self):
        self.assertIs(ConfiguracionSistema(), ConfiguracionSistema())

    def test_nombre_empresa(self):
        self.assertEqual(
            ConfiguracionSistema().nombre_empresa,
            "ParNet Ingeniería",
        )

    def test_configuracion_compartida(self):
        config1 = ConfiguracionSistema()
        config2 = ConfiguracionSistema()
        valor_original = config1.registros_por_pagina

        try:
            config1.registros_por_pagina = 25
            self.assertEqual(config2.registros_por_pagina, 25)
        finally:
            config1.registros_por_pagina = valor_original

    def test_obtener_configuracion(self):
        datos = ConfiguracionSistema().obtener_configuracion()
        self.assertIsInstance(datos, dict)
        for clave in ("nombre_empresa", "version", "moneda"):
            self.assertIn(clave, datos)

    @patch("core.context_processors.Noticia")
    @patch("core.views.Slider")
    def test_context_processor(self, slider_mock, noticia_mock):
        simular_slider(slider_mock)
        simular_noticias(noticia_mock)
        respuesta = self.client.get(reverse("core:inicio"))
        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(
            respuesta.context["configuracion_sistema"]["nombre_empresa"],
            "ParNet Ingeniería",
        )
        self.assertContains(respuesta, "ParNet Ingeniería")


# =========================================
# FRONTEND
# =========================================

class FrontendTest(SimpleTestCase):

    def setUp(self):
        super().setUp()
        parche_slider = patch("core.views.Slider")
        self.slider_mock = parche_slider.start()
        self.addCleanup(parche_slider.stop)
        simular_slider(self.slider_mock)

        parche_noticias = patch("core.context_processors.Noticia")
        self.noticias_mock = parche_noticias.start()
        self.addCleanup(parche_noticias.stop)
        simular_noticias(self.noticias_mock)

    def test_pagina_inicio_disponible(self):
        respuesta = self.client.get(reverse("core:inicio"))
        self.assertEqual(respuesta.status_code, 200)

    def test_plantilla_inicio(self):
        respuesta = self.client.get(reverse("core:inicio"))
        self.assertTemplateUsed(respuesta, "inicio.html")

    def test_plantilla_base(self):
        respuesta = self.client.get(reverse("core:inicio"))
        self.assertTemplateUsed(respuesta, "base.html")

    def test_componentes_principales(self):
        respuesta = self.client.get(reverse("core:inicio"))
        componentes = [
            "componentes/encabezado.html",
            "componentes/navbar.html",
            "componentes/sidebar.html",
            "componentes/slider.html",
            "componentes/footer.html",
        ]
        for componente in componentes:
            with self.subTest(componente=componente):
                self.assertTemplateUsed(respuesta, componente)

    def test_meta_viewport(self):
        respuesta = self.client.get(reverse("core:inicio"))
        self.assertContains(respuesta, 'name="viewport"')

    def test_menu_principal(self):
        respuesta = self.client.get(reverse("core:inicio"))
        self.assertContains(respuesta, 'id="menuParnet"')

    def test_archivos_css(self):
        archivos = [
            "css/estilos.css",
            "css/encabezado.css",
            "css/sidebar.css",
            "css/contenido.css",
            "css/slider.css",
            "css/noticias.css",
            "css/footer.css",
            "css/responsive.css",
        ]
        for archivo in archivos:
            with self.subTest(archivo=archivo):
                self.assertIsNotNone(finders.find(archivo))

    def test_archivo_javascript(self):
        self.assertIsNotNone(finders.find("js/main.js"))

    def test_imagenes_principales(self):
        imagenes = [
            "img/logo-parnet.png",
            "img/logo-pie.png",
            "img/antenas.jpg",
            "img/oficina.jpg",
            "img/tablero-electrico.jpg",
        ]
        for imagen in imagenes:
            with self.subTest(imagen=imagen):
                self.assertIsNotNone(finders.find(imagen))


# =========================================
# SLIDER DINAMICO
# =========================================

class SliderTest(SimpleTestCase):

    def setUp(self):
        super().setUp()
        parche = patch("core.context_processors.Noticia")
        self.noticias_mock = parche.start()
        self.addCleanup(parche.stop)
        simular_noticias(self.noticias_mock)

    @patch("core.views.Slider")
    def test_slider_sin_imagenes(self, slider_mock):
        simular_slider(slider_mock)
        respuesta = self.client.get(reverse("core:inicio"))
        self.assertEqual(respuesta.status_code, 200)
        self.assertContains(respuesta, "slider/ingenieria.jpg")

    @patch("core.views.Slider")
    def test_slider_con_imagenes(self, slider_mock):
        imagenes = [
            Slider(
                id_slider=1,
                titulo="Telecomunicaciones",
                imagen="slider/ingenieria.jpg",
                orden=1,
                activo=True,
            ),
            Slider(
                id_slider=2,
                titulo="Productos",
                imagen="slider/productos.jpg",
                orden=2,
                activo=True,
            ),
        ]
        simular_slider(slider_mock, imagenes)
        respuesta = self.client.get(reverse("core:inicio"))
        self.assertEqual(respuesta.status_code, 200)
        self.assertTemplateUsed(respuesta, "componentes/slider.html")
        self.assertContains(respuesta, 'id="sliderParnet"')
        self.assertContains(respuesta, "slider/productos.jpg")
        slider_mock.objects.filter.assert_called_once_with(activo=True)


# =========================================
# NOTICIAS DINAMICAS
# =========================================

class NoticiasTest(SimpleTestCase):

    def setUp(self):
        super().setUp()
        parche_sidebar = patch("core.context_processors.Noticia")
        self.sidebar_mock = parche_sidebar.start()
        self.addCleanup(parche_sidebar.stop)
        simular_noticias(self.sidebar_mock)

        self.noticia = Noticia(
            id_noticia=1,
            titulo="Noticia de prueba",
            resumen="Resumen de prueba",
            contenido="Contenido de prueba",
            fecha_publicacion=timezone.now(),
            activo=True,
        )

    @patch("core.views.Noticia")
    def test_listado_noticias(self, noticia_mock):
        simular_noticias(noticia_mock, [self.noticia])
        respuesta = self.client.get(reverse("core:listado_noticias"))
        self.assertEqual(respuesta.status_code, 200)
        self.assertContains(respuesta, "Noticia de prueba")
        self.assertTemplateUsed(respuesta, "noticias/listado.html")
        noticia_mock.objects.filter.assert_called_once_with(activo=True)

    @patch("core.views.get_object_or_404")
    def test_detalle_noticia(self, obtener_mock):
        obtener_mock.return_value = self.noticia
        respuesta = self.client.get(
            reverse("core:detalle_noticia", args=[1])
        )
        self.assertEqual(respuesta.status_code, 200)
        self.assertContains(respuesta, "Contenido de prueba")
        self.assertTemplateUsed(respuesta, "noticias/detalle.html")
        obtener_mock.assert_called_once_with(
            Noticia, id_noticia=1, activo=True
        )

    @patch("core.views.Noticia")
    def test_listado_sin_noticias(self, noticia_mock):
        simular_noticias(noticia_mock)
        respuesta = self.client.get(reverse("core:listado_noticias"))
        self.assertEqual(respuesta.status_code, 200)
        self.assertContains(respuesta, "No hay noticias disponibles")

    @patch("core.views.Slider")
    def test_noticias_en_sidebar(self, slider_mock):
        simular_slider(slider_mock)
        simular_noticias(self.sidebar_mock, [self.noticia])
        respuesta = self.client.get(reverse("core:inicio"))
        self.assertEqual(respuesta.status_code, 200)
        self.assertContains(respuesta, "Noticia de prueba")
        self.sidebar_mock.objects.filter.assert_called_once_with(activo=True)

# =========================================
# MODULO DE CLIENTES
# =========================================

class ClientesTest(SimpleTestCase):

    def setUp(self):

        super().setUp()

        parche_noticias = patch(
            "core.context_processors.Noticia"
        )

        self.noticias_mock = parche_noticias.start()

        self.addCleanup(parche_noticias.stop)

        simular_noticias(self.noticias_mock)

        self.empresa = Cliente(
            id_cliente=1,
            nombre="Empresa de prueba",
            logo="clientes/prueba.png",
            sitio_web="https://example.com/",
            descripcion="Descripción de prueba",
            activo=True
        )

    @patch("core.views.Cliente")
    def test_pagina_clientes(self, cliente_mock):

        cliente_mock.objects.filter.return_value \
            .order_by.return_value = [self.empresa]

        respuesta = self.client.get(
            reverse("core:listado_clientes")
        )

        self.assertEqual(
            respuesta.status_code,
            200
        )

        self.assertTemplateUsed(
            respuesta,
            "clientes/listado.html"
        )

        self.assertContains(
            respuesta,
            "Empresa de prueba"
        )

    @patch("core.views.Cliente")
    def test_clientes_activos(self, cliente_mock):

        cliente_mock.objects.filter.return_value \
            .order_by.return_value = [self.empresa]

        self.client.get(
            reverse("core:listado_clientes")
        )

        cliente_mock.objects.filter.assert_called_once_with(
            activo=True
        )

        cliente_mock.objects.filter.return_value \
            .order_by.assert_called_once_with(
                "nombre",
                "id_cliente"
            )

    @patch("core.views.Cliente")
    def test_logo_cliente(self, cliente_mock):

        cliente_mock.objects.filter.return_value \
            .order_by.return_value = [self.empresa]

        respuesta = self.client.get(
            reverse("core:listado_clientes")
        )

        self.assertContains(
            respuesta,
            "clientes/prueba.png"
        )

    @patch("core.views.Cliente")
    def test_sitio_web_cliente(self, cliente_mock):

        cliente_mock.objects.filter.return_value \
            .order_by.return_value = [self.empresa]

        respuesta = self.client.get(
            reverse("core:listado_clientes")
        )

        self.assertContains(
            respuesta,
            'href="https://example.com/"'
        )

        self.assertContains(
            respuesta,
            'target="_blank"'
        )

        self.assertContains(
            respuesta,
            'rel="noopener noreferrer"'
        )

    @patch("core.views.Cliente")
    def test_listado_sin_clientes(self, cliente_mock):

        cliente_mock.objects.filter.return_value \
            .order_by.return_value = []

        respuesta = self.client.get(
            reverse("core:listado_clientes")
        )

        self.assertEqual(
            respuesta.status_code,
            200
        )

        self.assertContains(
            respuesta,
            "No hay clientes disponibles"
        )

    def test_archivo_css_clientes(self):

        self.assertIsNotNone(
            finders.find("css/clientes.css")
        )