from django.test import SimpleTestCase

from core.patrones.singleton import ConfiguracionSistema


class ConfiguracionSistemaTest(SimpleTestCase):

    def test_instancia_unica(self):

        config1 = ConfiguracionSistema()
        config2 = ConfiguracionSistema()

        self.assertIs(config1, config2)

    def test_nombre_empresa(self):

        configuracion = ConfiguracionSistema()

        self.assertEqual(
            configuracion.nombre_empresa,
            "ParNet Ingeniería"
        )

    def test_configuracion_compartida(self):

        config1 = ConfiguracionSistema()
        config2 = ConfiguracionSistema()

        valor_original = config1.registros_por_pagina

        try:

            config1.registros_por_pagina = 25

            self.assertEqual(
                config2.registros_por_pagina,
                25
            )

        finally:

            config1.registros_por_pagina = valor_original

    def test_obtener_configuracion(self):

        configuracion = ConfiguracionSistema()

        datos = configuracion.obtener_configuracion()

        self.assertIsInstance(datos, dict)

        self.assertIn("nombre_empresa", datos)

        self.assertIn("version", datos)

        self.assertIn("moneda", datos)

    def test_context_processor(self):

        respuesta = self.client.get("/")

        self.assertEqual(respuesta.status_code, 200)

        self.assertContains(
            respuesta,
            "ParNet Ingeniería"
        )

from django.urls import reverse
from django.contrib.staticfiles import finders


class FrontendTest(SimpleTestCase):

    def test_pagina_inicio_disponible(self):

        respuesta = self.client.get(
            reverse("core:inicio")
        )

        self.assertEqual(
            respuesta.status_code,
            200
        )

    def test_plantilla_inicio(self):

        respuesta = self.client.get(
            reverse("core:inicio")
        )

        self.assertTemplateUsed(
            respuesta,
            "inicio.html"
        )

    def test_plantilla_base(self):

        respuesta = self.client.get(
            reverse("core:inicio")
        )

        self.assertTemplateUsed(
            respuesta,
            "base.html"
        )

    def test_componentes_principales(self):

        respuesta = self.client.get(
            reverse("core:inicio")
        )

        componentes = [
            "componentes/encabezado.html",
            "componentes/navbar.html",
            "componentes/sidebar.html",
            "componentes/footer.html",
        ]

        for componente in componentes:

            with self.subTest(componente=componente):

                self.assertTemplateUsed(
                    respuesta,
                    componente
                )

    def test_meta_viewport(self):

        respuesta = self.client.get(
            reverse("core:inicio")
        )

        self.assertContains(
            respuesta,
            'name="viewport"'
        )

    def test_menu_principal(self):

        respuesta = self.client.get(
            reverse("core:inicio")
        )

        self.assertContains(
            respuesta,
            'id="menuParnet"'
        )

    def test_archivos_css(self):

        archivos = [
            "css/estilos.css",
            "css/encabezado.css",
            "css/sidebar.css",
            "css/contenido.css",
            "css/footer.css",
            "css/responsive.css",
        ]

        for archivo in archivos:

            with self.subTest(archivo=archivo):

                self.assertIsNotNone(
                    finders.find(archivo)
                )

    def test_archivo_javascript(self):

        self.assertIsNotNone(
            finders.find("js/main.js")
        )

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

                self.assertIsNotNone(
                    finders.find(imagen)
                )