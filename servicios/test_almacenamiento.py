from unittest.mock import patch, MagicMock

from datetime import datetime, timezone as tz

from django.test import (
    SimpleTestCase,
    RequestFactory,
)

from django.db import DatabaseError

from servicios.views import solicitar_servicio


# =========================================
# PRUEBAS DE ALMACENAMIENTO
# =========================================

class AlmacenamientoSolicitudTest(SimpleTestCase):

    def setUp(self):

        super().setUp()

        self.factory = RequestFactory()

        self.datos = {

            "area": "1",

            "nombre": "Carlos Hernández",

            "empresa": "Empresa de prueba",

            "correo": "contacto@example.com",

            "telefono": "8441234567",

            "detalle": (
                "Solicito información sobre "
                "la instalación de fibra óptica."
            ),

            "g-recaptcha-response": "token_de_prueba",

        }

        self.fecha = datetime(

            2026, 1, 1, 12, 0,

            tzinfo=tz.utc

        )

        # Simular formulario

        parche_formulario = patch(
            "servicios.views.SolicitudServicioForm"
        )

        self.formulario_mock = (
            parche_formulario.start()
        )

        self.addCleanup(
            parche_formulario.stop
        )

        self.formulario = (
            self.formulario_mock.return_value
        )

        self.formulario.is_valid.return_value = True

        # Simular instancia del modelo

        self.solicitud = MagicMock()

        self.solicitud.pk = 100

        self.solicitud.area.nombre = "Fibra Óptica"

        self.formulario.save.return_value = (
            self.solicitud
        )

        # Simular transaccion

        parche_transaccion = patch(
            "servicios.views.transaction.atomic"
        )

        self.transaccion = (
            parche_transaccion.start()
        )

        self.addCleanup(
            parche_transaccion.stop
        )

        # Simular renderizado

        parche_render = patch(
            "servicios.views.render"
        )

        self.render_mock = parche_render.start()

        self.addCleanup(
            parche_render.stop
        )

        # Simular fecha actual

        parche_fecha = patch(
            "servicios.views.timezone.now",
            return_value=self.fecha
        )

        parche_fecha.start()

        self.addCleanup(
            parche_fecha.stop
        )

    # =========================================
    # COMPROBAR DATOS DE CONFIRMACION
    # =========================================

    def test_datos_confirmacion(self):

        self.enviar_formulario()

        confirmacion = self.request.session[
            "confirmacion_solicitud"
        ]

        self.assertEqual(

            confirmacion["folio"],

            "SOL-000100"

        )

        self.assertEqual(

            confirmacion["area"],

            "Fibra Óptica"

        )

        self.assertEqual(

            confirmacion["estatus"],

            "Pendiente"

        )

        self.assertTrue(
            confirmacion["fecha"]
        )

    # =========================================
    # GENERAR PETICION POST
    # =========================================

    def enviar_formulario(self):

        request = self.factory.post(

            "/servicios/solicitar/",

            self.datos

        )

        # Simular la sesion de Django

        request.session = {}

        self.request = request

        return solicitar_servicio(request)


    # =========================================
    # VALIDAR ANTES DE ALMACENAR
    # =========================================

    def test_validar_formulario(self):

        self.enviar_formulario()

        self.formulario.is_valid.assert_called_once()


    # =========================================
    # CREAR INSTANCIA SIN GUARDAR
    # =========================================

    def test_crear_instancia(self):

        self.enviar_formulario()

        self.formulario.save.assert_called_once_with(

            commit=False

        )


    # =========================================
    # GUARDAR SOLICITUD
    # =========================================

    def test_guardar_solicitud(self):

        self.enviar_formulario()

        self.solicitud.save.assert_called_once()


    # =========================================
    # ASIGNAR ESTADO INICIAL
    # =========================================

    def test_estado_inicial(self):

        self.enviar_formulario()

        self.assertEqual(

            self.solicitud.estatus,

            "Pendiente"

        )


    # =========================================
    # ASIGNAR FECHA
    # =========================================

    def test_fecha_solicitud(self):

        self.enviar_formulario()

        self.assertEqual(

            self.solicitud.fecha_solicitud,

            self.fecha

        )


    # =========================================
    # UTILIZAR TRANSACCION
    # =========================================

    def test_transaccion(self):

        self.enviar_formulario()

        self.transaccion.assert_called_once()


    # =========================================
    # REDIRECCION DESPUES DE GUARDAR
    # =========================================

    def test_redireccion_exitosa(self):

        respuesta = self.enviar_formulario()

        self.assertEqual(

            respuesta.status_code,

            302

        )

        self.assertEqual(

            respuesta.url,

            "/servicios/confirmacion/"

        )

    # =========================================
    # NO GUARDAR FORMULARIO INVALIDO
    # =========================================

    def test_formulario_invalido(self):

        self.formulario.is_valid.return_value = False

        self.enviar_formulario()

        self.formulario.save.assert_not_called()

        self.solicitud.save.assert_not_called()

        self.transaccion.assert_not_called()

        self.assertNotIn(

            "confirmacion_solicitud",

            self.request.session

        )

        self.render_mock.assert_called_once()


    # =========================================
    # CONTROLAR ERRORES DE BASE DE DATOS
    # =========================================

    @patch("servicios.views.logger.exception")
    def test_error_base_datos(self, logger_mock):

        self.solicitud.save.side_effect = (
            DatabaseError("Error simulado")
        )

        self.enviar_formulario()

        self.formulario.add_error.assert_called_once_with(

            None,

            "No fue posible registrar tu solicitud. "
            "Inténtalo nuevamente."

        )

        self.assertNotIn(

            "confirmacion_solicitud",

            self.request.session

        )

        self.render_mock.assert_called_once()

        logger_mock.assert_called_once()


    # =========================================
    # NO GUARDAR MEDIANTE GET
    # =========================================

    def test_get_no_guarda_solicitud(self):

        request = self.factory.get(
            "/servicios/solicitar/"
        )

        solicitar_servicio(request)

        self.formulario.save.assert_not_called()

        self.solicitud.save.assert_not_called()

        self.render_mock.assert_called_once()


    # =========================================
    # IGNORAR ESTADO ENVIADO POR VISITANTE
    # =========================================

    def test_estado_manipulado(self):

        self.datos["estatus"] = "Atendida"

        self.enviar_formulario()

        self.assertEqual(

            self.solicitud.estatus,

            "Pendiente"

        )