from unittest.mock import patch

from django.test import (
    SimpleTestCase,
    RequestFactory,
)

from django.urls import reverse, resolve

from django.http import HttpResponse

from django.template.loader import get_template

from servicios.views import confirmacion_solicitud


# =========================================
# PRUEBAS DE CONFIRMACION
# =========================================

class ConfirmacionSolicitudTest(SimpleTestCase):

    def setUp(self):

        super().setUp()

        self.factory = RequestFactory()

        self.datos = {

            "folio": "SOL-000100",

            "area": "Fibra Óptica",

            "fecha": "24/11/2026 20:15",

            "estatus": "Pendiente",

        }


    # =========================================
    # GENERAR PETICION CON SESION
    # =========================================

    def crear_peticion(self, con_confirmacion=True):

        request = self.factory.get(

            "/servicios/confirmacion/"

        )

        request.session = {}

        if con_confirmacion:

            request.session[
                "confirmacion_solicitud"
            ] = self.datos.copy()

        return request


    # =========================================
    # COMPROBAR RUTA
    # =========================================

    def test_ruta_confirmacion(self):

        ruta = reverse(
            "servicios:confirmacion"
        )

        self.assertEqual(

            ruta,

            "/servicios/confirmacion/"

        )


    # =========================================
    # COMPROBAR VISTA ASOCIADA
    # =========================================

    def test_resolver_ruta(self):

        ruta = resolve(
            "/servicios/confirmacion/"
        )

        self.assertEqual(

            ruta.view_name,

            "servicios:confirmacion"

        )


    # =========================================
    # RECHAZAR ACCESO SIN CONFIRMACION
    # =========================================

    def test_acceso_sin_confirmacion(self):

        request = self.crear_peticion(
            con_confirmacion=False
        )

        respuesta = confirmacion_solicitud(
            request
        )

        self.assertEqual(
            respuesta.status_code,
            302
        )

        self.assertEqual(

            respuesta.url,

            "/servicios/solicitar/"

        )


    # =========================================
    # MOSTRAR PLANTILLA CORRECTA
    # =========================================

    @patch("servicios.views.render")
    def test_plantilla_confirmacion(self, render_mock):

        render_mock.return_value = HttpResponse()

        request = self.crear_peticion()

        confirmacion_solicitud(request)

        argumentos = render_mock.call_args.args

        self.assertEqual(

            argumentos[1],

            "servicios/confirmacion.html"

        )


    # =========================================
    # ENVIAR DATOS A LA PLANTILLA
    # =========================================

    @patch("servicios.views.render")
    def test_contexto_confirmacion(self, render_mock):

        render_mock.return_value = HttpResponse()

        request = self.crear_peticion()

        confirmacion_solicitud(request)

        contexto = render_mock.call_args.args[2]

        self.assertEqual(

            contexto["confirmacion"],

            self.datos

        )


    # =========================================
    # CONSERVAR CONFIRMACION AL RECARGAR
    # =========================================

    @patch("servicios.views.render")
    def test_recargar_confirmacion(self, render_mock):

        render_mock.return_value = HttpResponse()

        request = self.crear_peticion()

        confirmacion_solicitud(request)

        confirmacion_solicitud(request)

        self.assertEqual(

            render_mock.call_count,

            2

        )

        self.assertEqual(

            request.session[
                "confirmacion_solicitud"
            ],

            self.datos

        )


    # =========================================
    # RECHAZAR PETICIONES POST
    # =========================================

    def test_rechazar_post(self):

        request = self.factory.post(

            "/servicios/confirmacion/"

        )

        respuesta = confirmacion_solicitud(
            request
        )

        self.assertEqual(

            respuesta.status_code,

            405

        )


    # =========================================
    # EVITAR ALMACENAMIENTO EN CACHE
    # =========================================

    @patch("servicios.views.render")
    def test_no_cache(self, render_mock):

        render_mock.return_value = HttpResponse()

        request = self.crear_peticion()

        respuesta = confirmacion_solicitud(
            request
        )

        self.assertIn(

            "no-store",

            respuesta["Cache-Control"]

        )


    # =========================================
    # COMPROBAR EXISTENCIA DE PLANTILLA
    # =========================================

    def test_existencia_plantilla(self):

        plantilla = get_template(
            "servicios/confirmacion.html"
        )

        self.assertIsNotNone(plantilla)