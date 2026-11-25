from unittest.mock import patch
from django.test import SimpleTestCase, RequestFactory
from django.urls import reverse, resolve
from django.http import Http404
from servicios.models import AreaServicio
from servicios.forms import SolicitudServicioForm
from servicios.views import solicitar_servicio

class SeleccionAreaTest(SimpleTestCase):

    def setUp(self):

        super().setUp()

        self.factory = RequestFactory()

        # Area de prueba

        self.area = AreaServicio(

            id_area=1,

            nombre="Fibra Óptica",

            descripcion="Servicio de prueba",

            activo=True

        )

        # Evitar consultas reales a MySQL

        parche_areas = patch(
            "servicios.forms.areas_activas"
        )

        self.areas_mock = parche_areas.start()

        self.addCleanup(parche_areas.stop)

        self.areas_mock.return_value = (
            AreaServicio.objects.none()
        )

    # =========================================
    # RUTA GENERAL
    # =========================================

    def test_ruta_general(self):

        ruta = reverse(
            "servicios:solicitar"
        )

        self.assertEqual(

            ruta,

            "/servicios/solicitar/"

        )

    # =========================================
    # RUTA CON AREA ESPECIFICA
    # =========================================

    def test_ruta_area_especifica(self):

        ruta = reverse(

            "servicios:solicitar_area",

            kwargs={"id_area": 1}

        )

        self.assertEqual(

            ruta,

            "/servicios/solicitar/1/"

        )

    # =========================================
    # COMPROBAR IDENTIFICADOR DE RUTA
    # =========================================

    def test_identificador_ruta(self):

        ruta = resolve(
            "/servicios/solicitar/1/"
        )

        self.assertEqual(

            ruta.view_name,

            "servicios:solicitar_area"

        )

        self.assertEqual(

            ruta.kwargs["id_area"],

            1

        )

    # =========================================
    # FORMULARIO SIN AREA SELECCIONADA
    # =========================================

    @patch("servicios.views.render")
    def test_formulario_general(self, render_mock):

        solicitud = self.factory.get(
            "/servicios/solicitar/"
        )

        solicitar_servicio(solicitud)

        contexto = render_mock.call_args.args[2]

        formulario = contexto["formulario"]

        self.assertIsInstance(

            formulario,

            SolicitudServicioForm

        )

        self.assertIsNone(

            contexto["area_seleccionada"]

        )

        self.assertNotIn(

            "area",

            formulario.initial

        )

    # =========================================
    # PRESELECCIONAR AREA
    # =========================================

    @patch("servicios.views.render")
    @patch("servicios.views.get_object_or_404")
    def test_preseleccionar_area(

        self,

        area_mock,

        render_mock

    ):

        area_mock.return_value = self.area

        solicitud = self.factory.get(
            "/servicios/solicitar/1/"
        )

        solicitar_servicio(

            solicitud,

            id_area=1

        )

        contexto = render_mock.call_args.args[2]

        formulario = contexto["formulario"]

        self.assertEqual(

            formulario.initial["area"],

            self.area.pk

        )

        self.assertEqual(

            contexto["area_seleccionada"],

            self.area

        )

    # =========================================
    # CONSULTAR SOLAMENTE AREAS ACTIVAS
    # =========================================

    @patch("servicios.views.render")
    @patch("servicios.views.get_object_or_404")
    def test_consultar_area_activa(

        self,

        area_mock,

        render_mock

    ):

        area_mock.return_value = self.area

        solicitud = self.factory.get(
            "/servicios/solicitar/1/"
        )

        solicitar_servicio(

            solicitud,

            id_area=1

        )

        area_mock.assert_called_once_with(

            AreaServicio,

            id_area=1,

            activo=True

        )

    # =========================================
    # RECHAZAR AREA INEXISTENTE
    # =========================================

    @patch("servicios.views.get_object_or_404")
    def test_area_inexistente(self, area_mock):

        area_mock.side_effect = Http404

        solicitud = self.factory.get(
            "/servicios/solicitar/999999/"
        )

        with self.assertRaises(Http404):

            solicitar_servicio(

                solicitud,

                id_area=999999

            )

    # =========================================
    # RECHAZAR AREA INACTIVA
    # =========================================

    @patch("servicios.views.get_object_or_404")
    def test_area_inactiva(self, area_mock):

        area_mock.side_effect = Http404

        solicitud = self.factory.get(
            "/servicios/solicitar/1/"
        )

        with self.assertRaises(Http404):

            solicitar_servicio(

                solicitud,

                id_area=1

            )

        area_mock.assert_called_once_with(

            AreaServicio,

            id_area=1,

            activo=True

        )

    # =========================================
    # PERMITIR CAMBIAR AREA
    # =========================================

    def test_selector_editable(self):

        formulario = SolicitudServicioForm(

            initial={"area": self.area.pk}

        )

        self.assertFalse(

            formulario.fields["area"].disabled

        )