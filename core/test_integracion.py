from unittest.mock import patch
from django.test import SimpleTestCase
from django.urls import reverse
from django.contrib.staticfiles import finders

class IntegracionTest(SimpleTestCase):

    def setUp(self):

        super().setUp()

        parches = {

            "slider": "core.views.Slider",

            "noticias": "core.context_processors.Noticia",

            "listado_noticias": "core.views.Noticia",

            "clientes": "core.views.Cliente",

            "areas": "core.context_processors.areas_activas",

            "listado_servicios": "servicios.views.areas_activas",

            "contador": "core.context_processors.Visita",

            "registro": "core.middleware.Visita",

            "usuarios": (
                "core.middleware.registrar_usuario_conectado"
            ),

            "conectados": (
                "core.context_processors.contar_usuarios_conectados"
            ),

        }

        self.mocks = {}

        for nombre, destino in parches.items():

            parche = patch(destino)

            self.mocks[nombre] = parche.start()

            self.addCleanup(parche.stop)

        self.mocks["slider"].objects.filter.return_value \
            .exclude.return_value \
            .order_by.return_value = []

        self.mocks["noticias"].objects.filter.return_value \
            .order_by.return_value = []

        self.mocks["listado_noticias"].objects.filter.return_value \
            .order_by.return_value = []

        self.mocks["clientes"].objects.filter.return_value \
            .order_by.return_value = []

        self.mocks["areas"].return_value = []

        self.mocks["listado_servicios"].return_value = []

        self.mocks["contador"].objects.count.return_value = 25

        self.mocks["conectados"].return_value = 2

    # =========================================
    # PAGINAS PUBLICAS
    # =========================================

    def test_paginas_publicas(self):

        rutas = [

            "core:inicio",

            "core:listado_noticias",

            "core:listado_clientes",

            "servicios:listado",

        ]

        for ruta in rutas:

            with self.subTest(ruta=ruta):

                respuesta = self.client.get(
                    reverse(ruta)
                )

                self.assertEqual(
                    respuesta.status_code,
                    200
                )

    # =========================================
    # PLANTILLA BASE COMPARTIDA
    # =========================================

    def test_plantilla_base_compartida(self):

        rutas = [

            "core:inicio",

            "core:listado_noticias",

            "core:listado_clientes",

            "servicios:listado",

        ]

        for ruta in rutas:

            with self.subTest(ruta=ruta):

                respuesta = self.client.get(
                    reverse(ruta)
                )

                self.assertTemplateUsed(
                    respuesta,
                    "base.html"
                )

    # =========================================
    # COMPONENTES COMPARTIDOS
    # =========================================

    def test_componentes_compartidos(self):

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

    # =========================================
    # ENLACES DE NAVEGACION
    # =========================================

    def test_enlaces_navegacion(self):

        respuesta = self.client.get(
            reverse("core:inicio")
        )

        rutas = [

            "core:inicio",

            "core:listado_noticias",

            "core:listado_clientes",

            "servicios:listado",

        ]

        for ruta in rutas:

            direccion = reverse(ruta)

            self.assertContains(

                respuesta,

                f'href="{direccion}"'

            )

    # =========================================
    # CONTADORES COMPARTIDOS
    # =========================================

    def test_contadores_compartidos(self):

        respuesta = self.client.get(
            reverse("core:listado_clientes")
        )

        self.assertContains(
            respuesta,
            'id="usuarios-conectados"'
        )

        self.assertContains(
            respuesta,
            'id="contador-visitas"'
        )

        self.assertContains(
            respuesta,
            'aria-label="26 visitas"'
        )

        self.assertEqual(
            respuesta.context["usuarios_conectados"],
            2
        )

    # =========================================
    # REGISTRO DE VISITA Y ACTIVIDAD
    # =========================================

    def test_registro_visita_y_actividad(self):

        ruta = reverse("servicios:listado")

        respuesta = self.client.get(ruta)

        self.assertEqual(
            respuesta.status_code,
            200
        )

        self.mocks["registro"].objects.create \
            .assert_called_once_with(pagina=ruta)

        self.mocks["usuarios"].assert_called_once()

    # =========================================
    # ARCHIVOS ESTATICOS
    # =========================================

    def test_archivos_estaticos(self):

        archivos = [

            "css/estilos.css",

            "css/encabezado.css",

            "css/sidebar.css",

            "css/contenido.css",

            "css/slider.css",

            "css/noticias.css",

            "css/clientes.css",

            "css/servicios.css",

            "css/footer.css",

            "css/responsive.css",

            "js/main.js",

            "js/contadores.js",

        ]

        for archivo in archivos:

            with self.subTest(archivo=archivo):

                self.assertIsNotNone(
                    finders.find(archivo)
                )

    # =========================================
    # CONFIGURACION DE API
    # =========================================

    def test_configuracion_api_contadores(self):

        respuesta = self.client.get(
            reverse("core:inicio")
        )

        direccion = reverse(
            "core:api_estadisticas"
        )

        self.assertContains(
            respuesta,
            f'data-api-url="{direccion}"'
        )

        self.assertContains(
            respuesta,
            'name="csrfmiddlewaretoken"'
        )

        self.assertContains(
            respuesta,
            "js/contadores.js"
        )