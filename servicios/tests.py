from unittest.mock import patch

from django.test import SimpleTestCase
from django.urls import reverse
from django.http import Http404
from django.contrib.staticfiles import finders

from .models import AreaServicio


class ServiciosTest(SimpleTestCase):

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

        # Simular consulta del contador de visitas

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

        # Crear un objeto de prueba sin guardarlo en MySQL

        self.area = AreaServicio(

            id_area=1,

            nombre="Telecomunicaciones",

            descripcion="Servicio de prueba",

            activo=True

        )


    @patch("servicios.views.areas_activas")
    def test_listado_servicios(self, consulta_mock):

        consulta_mock.return_value = [
            self.area
        ]

        respuesta = self.client.get(
            reverse("servicios:listado")
        )

        self.assertEqual(
            respuesta.status_code,
            200
        )

        self.assertTemplateUsed(
            respuesta,
            "servicios/listado.html"
        )

        self.assertContains(
            respuesta,
            "Telecomunicaciones"
        )

        consulta_mock.assert_called_once_with()


    @patch("servicios.views.get_object_or_404")
    def test_detalle_area(self, obtener_mock):

        obtener_mock.return_value = self.area

        respuesta = self.client.get(

            reverse(
                "servicios:detalle",
                kwargs={"id_area": 1}
            )

        )

        self.assertEqual(
            respuesta.status_code,
            200
        )

        self.assertTemplateUsed(
            respuesta,
            "servicios/detalle.html"
        )

        self.assertContains(
            respuesta,
            "Servicio de prueba"
        )

        obtener_mock.assert_called_once_with(
            AreaServicio,
            id_area=1,
            activo=True
        )


    @patch("servicios.views.get_object_or_404")
    def test_area_no_disponible(self, obtener_mock):

        obtener_mock.side_effect = Http404

        respuesta = self.client.get(

            reverse(
                "servicios:detalle",
                kwargs={"id_area": 999}
            )

        )

        self.assertEqual(
            respuesta.status_code,
            404
        )


    @patch("servicios.views.areas_activas")
    def test_listado_vacio(self, consulta_mock):

        consulta_mock.return_value = []

        respuesta = self.client.get(
            reverse("servicios:listado")
        )

        self.assertContains(
            respuesta,
            "No hay servicios disponibles"
        )


    @patch("core.views.Slider")
    def test_areas_en_sidebar(self, slider_mock):

        slider_mock.objects.filter.return_value \
            .exclude.return_value \
            .order_by.return_value = []

        self.areas_mock.return_value = [
            self.area
        ]

        respuesta = self.client.get(
            reverse("core:inicio")
        )

        self.assertEqual(
            respuesta.status_code,
            200
        )

        self.assertContains(
            respuesta,
            "Telecomunicaciones"
        )

        enlace = reverse(
            "servicios:detalle",
            kwargs={"id_area": 1}
        )

        self.assertContains(
            respuesta,
            f'href="{enlace}"'
        )


    def test_archivo_css_servicios(self):

        self.assertIsNotNone(
            finders.find("css/servicios.css")
        )