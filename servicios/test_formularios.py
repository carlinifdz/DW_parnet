from unittest.mock import patch
from django.test import SimpleTestCase, RequestFactory
from django.urls import reverse, resolve
from django.contrib.staticfiles import finders
from django import forms
from django_recaptcha.fields import ReCaptchaField
from servicios.forms import SolicitudServicioForm
from servicios.models import AreaServicio, SolicitudServicio
from servicios.views import solicitar_servicio

class SolicitudServicioFormTest(SimpleTestCase):

    def setUp(self):

        super().setUp()

        self.factory = RequestFactory()

        # Simular consulta de areas sin acceder a MySQL

        parche_areas = patch(
            "servicios.forms.areas_activas"
        )

        self.areas_mock = parche_areas.start()

        self.addCleanup(parche_areas.stop)

        self.areas_mock.return_value = (
            AreaServicio.objects.none()
        )


    # =========================================
    # COMPROBAR MODELFORM
    # =========================================

    def test_tipo_formulario(self):

        formulario = SolicitudServicioForm()

        self.assertIsInstance(
            formulario,
            forms.ModelForm
        )


    # =========================================
    # COMPROBAR MODELO
    # =========================================

    def test_modelo_formulario(self):

        formulario = SolicitudServicioForm()

        self.assertEqual(
            formulario._meta.model,
            SolicitudServicio
        )


    # =========================================
    # COMPROBAR CAMPOS
    # =========================================

    def test_campos_formulario(self):

        formulario = SolicitudServicioForm()

        campos_esperados = {

            "area",
            "nombre",
            "empresa",
            "correo",
            "telefono",
            "detalle",
            "captcha",

        }

        self.assertEqual(

            set(formulario.fields.keys()),

            campos_esperados

        )


    # =========================================
    # EXCLUIR CAMPOS ADMINISTRATIVOS
    # =========================================

    def test_excluir_campos_administrativos(self):

        formulario = SolicitudServicioForm()

        self.assertNotIn(
            "id_solicitud",
            formulario.fields
        )

        self.assertNotIn(
            "estatus",
            formulario.fields
        )

        self.assertNotIn(
            "fecha_solicitud",
            formulario.fields
        )


    # =========================================
    # COMPROBAR CAPTCHA
    # =========================================

    def test_captcha_formulario(self):

        formulario = SolicitudServicioForm()

        self.assertIsInstance(

            formulario.fields["captcha"],

            ReCaptchaField

        )

        self.assertTrue(
            formulario.fields["captcha"].required
        )


    # =========================================
    # COMPROBAR CONSULTA DE AREAS
    # =========================================

    def test_consulta_areas_activas(self):

        formulario = SolicitudServicioForm()

        self.areas_mock.assert_called_once()

        self.assertEqual(

            formulario.fields["area"].queryset.model,

            AreaServicio

        )


    # =========================================
    # COMPROBAR SELECTOR DE AREAS
    # =========================================

    def test_selector_areas(self):

        formulario = SolicitudServicioForm()

        self.assertEqual(

            formulario.fields["area"].empty_label,

            "Seleccione un área de servicio"

        )


    # =========================================
    # COMPROBAR RUTA
    # =========================================

    def test_ruta_solicitud(self):

        ruta = reverse("servicios:solicitar")

        self.assertEqual(
            ruta,
            "/servicios/solicitar/"
        )

        self.assertEqual(

            resolve(ruta).view_name,

            "servicios:solicitar"

        )


    # =========================================
    # COMPROBAR VISTA Y PLANTILLA
    # =========================================

    @patch("servicios.views.render")
    def test_vista_solicitud(self, render_mock):

        solicitud = self.factory.get(

            reverse("servicios:solicitar")

        )

        solicitar_servicio(solicitud)

        render_mock.assert_called_once()

        argumentos = render_mock.call_args.args

        self.assertEqual(

            argumentos[1],

            "servicios/solicitud.html"

        )

        contexto = argumentos[2]

        self.assertIsInstance(

            contexto["formulario"],

            SolicitudServicioForm

        )


    # =========================================
    # RECHAZAR POST TEMPORALMENTE
    # =========================================

# =========================================
# RECHAZAR METODOS NO PERMITIDOS
# =========================================

    def test_metodo_no_permitido(self):

        solicitud = self.factory.put(

            reverse("servicios:solicitar")

        )

        respuesta = solicitar_servicio(solicitud)

        self.assertEqual(

            respuesta.status_code,

            405

        )


    # =========================================
    # COMPROBAR ARCHIVO CSS
    # =========================================

    def test_archivo_css(self):

        self.assertIsNotNone(

            finders.find("css/solicitudes.css")

        )