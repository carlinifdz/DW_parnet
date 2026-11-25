from unittest.mock import patch, MagicMock

from django.test import (
    SimpleTestCase,
    RequestFactory,
)

from django.urls import reverse

from django.http import HttpResponse

from django.utils import timezone

from django.middleware.csrf import CsrfViewMiddleware

from django.template.loader import get_template

from django_recaptcha.client import RecaptchaResponse

from servicios.forms import SolicitudServicioForm

from servicios.models import AreaServicio

from servicios.views import (
    solicitar_servicio,
    confirmacion_solicitud,
)


# =========================================
# PRUEBAS DE INTEGRACION DE SOLICITUDES
# =========================================

class IntegracionSolicitudesTest(SimpleTestCase):

    def setUp(self):

        super().setUp()

        self.factory = RequestFactory()

        self.datos = {

            "area": "1",

            "nombre": "Usuario de Prueba",

            "empresa": "Empresa de prueba",

            "correo": "contacto@example.com",

            "telefono": "8441234567",

            "detalle": (
                "Solicito información sobre "
                "la instalación de fibra óptica."
            ),

            "g-recaptcha-response": "token_prueba",

        }

        self.area = AreaServicio(

            id_area=1,

            nombre="Fibra Óptica",

            activo=True

        )


    # =========================================
    # COMPROBAR EXISTENCIA DEL FORMULARIO
    # =========================================

    def test_plantilla_formulario(self):

        plantilla = get_template(
            "servicios/solicitud.html"
        )

        self.assertIsNotNone(plantilla)


    # =========================================
    # COMPROBAR PLANTILLA DE CONFIRMACION
    # =========================================

    def test_plantilla_confirmacion(self):

        plantilla = get_template(
            "servicios/confirmacion.html"
        )

        self.assertIsNotNone(plantilla)


    # =========================================
    # COMPROBAR FORMULARIO SIN CAPTCHA
    # =========================================

    @patch("servicios.forms.areas_activas")
    def test_formulario_sin_captcha(

        self,

        areas_mock

    ):

        areas_mock.return_value = (
            AreaServicio.objects.none()
        )

        formulario = SolicitudServicioForm()

        campo = formulario.fields["captcha"]

        self.assertTrue(
            campo.required
        )

        from django.core.exceptions import ValidationError

        with self.assertRaises(ValidationError):

            campo.clean("")


    # =========================================
    # COMPROBAR CAPTCHA INVALIDO
    # =========================================

    @patch("django_recaptcha.fields.client.submit")
    @patch("servicios.forms.areas_activas")
    def test_captcha_invalido(

        self,

        areas_mock,

        captcha_mock

    ):

        areas_mock.return_value = (
            AreaServicio.objects.none()
        )

        captcha_mock.return_value = RecaptchaResponse(

            is_valid=False,

            error_codes=["invalid-input-response"]

        )

        formulario = SolicitudServicioForm()

        from django.core.exceptions import ValidationError

        with self.assertRaises(ValidationError):

            formulario.fields["captcha"].clean(
                "token_invalido"
            )


    # =========================================
    # COMPROBAR CAPTCHA VALIDO
    # =========================================

    @patch("django_recaptcha.fields.client.submit")
    @patch("servicios.forms.areas_activas")
    def test_captcha_valido(

        self,

        areas_mock,

        captcha_mock

    ):

        areas_mock.return_value = (
            AreaServicio.objects.none()
        )

        captcha_mock.return_value = RecaptchaResponse(
            is_valid=True
        )

        formulario = SolicitudServicioForm()

        resultado = formulario.fields["captcha"].clean(
            "token_prueba"
        )

        self.assertEqual(

            resultado,

            "token_prueba"

        )


    # =========================================
    # COMPROBAR FLUJO DE REGISTRO Y CONFIRMACION
    # =========================================

    @patch("servicios.views.transaction.atomic")
    @patch("servicios.views.SolicitudServicioForm")
    @patch("servicios.views.render")
    def test_flujo_completo(

        self,

        render_mock,

        formulario_mock,

        transaccion_mock

    ):

        formulario = formulario_mock.return_value

        formulario.is_valid.return_value = True

        solicitud = MagicMock()

        solicitud.pk = 250

        solicitud.area = self.area

        formulario.save.return_value = solicitud

        render_mock.return_value = HttpResponse()

        # Enviar solicitud

        request_post = self.factory.post(

            reverse("servicios:solicitar"),

            self.datos

        )

        request_post.session = {}

        respuesta = solicitar_servicio(
            request_post
        )

        # Comprobar almacenamiento

        solicitud.save.assert_called_once()

        self.assertEqual(

            solicitud.estatus,

            "Pendiente"

        )

        # Comprobar redireccion

        self.assertEqual(

            respuesta.status_code,

            302

        )

        self.assertEqual(

            respuesta.url,

            reverse("servicios:confirmacion")

        )

        # Consultar confirmacion

        request_get = self.factory.get(
            respuesta.url
        )

        request_get.session = request_post.session

        respuesta_final = confirmacion_solicitud(
            request_get
        )

        self.assertEqual(

            respuesta_final.status_code,

            200

        )

        contexto = render_mock.call_args.args[2]

        self.assertEqual(

            contexto["confirmacion"]["folio"],

            "SOL-000250"

        )

        self.assertEqual(

            contexto["confirmacion"]["area"],

            "Fibra Óptica"

        )


    # =========================================
    # COMPROBAR AISLAMIENTO DE SESIONES
    # =========================================

    @patch("servicios.views.render")
    def test_aislamiento_sesiones(self, render_mock):

        render_mock.return_value = HttpResponse()

        visitante_a = self.factory.get(
            reverse("servicios:confirmacion")
        )

        visitante_a.session = {

            "confirmacion_solicitud": {

                "folio": "SOL-000250",

                "area": "Fibra Óptica",

                "fecha": "24/11/2026 20:00",

                "estatus": "Pendiente",

            }

        }

        visitante_b = self.factory.get(
            reverse("servicios:confirmacion")
        )

        visitante_b.session = {}

        respuesta_a = confirmacion_solicitud(
            visitante_a
        )

        respuesta_b = confirmacion_solicitud(
            visitante_b
        )

        self.assertEqual(

            respuesta_a.status_code,

            200

        )

        self.assertEqual(

            respuesta_b.status_code,

            302

        )

        self.assertEqual(

            respuesta_b.url,

            reverse("servicios:solicitar")

        )


    # =========================================
    # COMPROBAR PROTECCION CSRF
    # =========================================

    def test_post_sin_csrf(self):

        request = self.factory.post(

            reverse("servicios:solicitar"),

            self.datos

        )

        middleware = CsrfViewMiddleware(

            lambda request: HttpResponse()

        )

        with patch(
            "servicios.views.SolicitudServicioForm"
        ) as formulario_mock:

            respuesta = middleware.process_view(

                request,

                solicitar_servicio,

                (),

                {}

            )

            self.assertIsNotNone(respuesta)

            self.assertEqual(

                respuesta.status_code,

                403

            )

            formulario_mock.assert_not_called()


    # =========================================
    # COMPROBAR QUE NO SE GUARDAN DATOS INVALIDOS
    # =========================================

    @patch("servicios.views.render")
    @patch("servicios.views.SolicitudServicioForm")
    def test_no_guardar_datos_invalidos(

        self,

        formulario_mock,

        render_mock

    ):

        formulario = formulario_mock.return_value

        formulario.is_valid.return_value = False

        render_mock.return_value = HttpResponse()

        request = self.factory.post(

            reverse("servicios:solicitar"),

            {"nombre": "123"}

        )

        request.session = {}

        respuesta = solicitar_servicio(request)

        self.assertEqual(

            respuesta.status_code,

            200

        )

        formulario.save.assert_not_called()

        self.assertNotIn(

            "confirmacion_solicitud",

            request.session

        )


    # =========================================
    # COMPROBAR QUE RECARGAR NO GUARDA OTRA SOLICITUD
    # =========================================

    @patch("servicios.views.render")
    @patch("servicios.views.SolicitudServicioForm")
    def test_recarga_sin_duplicados(

        self,

        formulario_mock,

        render_mock

    ):

        render_mock.return_value = HttpResponse()

        request = self.factory.get(

            reverse("servicios:confirmacion")

        )

        request.session = {

            "confirmacion_solicitud": {

                "folio": "SOL-000250",

                "area": "Fibra Óptica",

                "fecha": "24/11/2026 20:00",

                "estatus": "Pendiente",

            }

        }

        confirmacion_solicitud(request)

        confirmacion_solicitud(request)

        formulario_mock.assert_not_called()

        self.assertEqual(

            render_mock.call_count,

            2

        )