from datetime import timedelta
from unittest.mock import patch, MagicMock
from django.test import SimpleTestCase, RequestFactory
from django.urls import reverse, resolve
from django.utils import timezone
from django.contrib.staticfiles import finders
from django.middleware.csrf import get_token
from core.estadisticas import (
    registrar_usuario_conectado,
    contar_usuarios_conectados,
    limpiar_usuarios_inactivos,
)

from core.context_processors import contador_usuarios
from core.views import api_estadisticas

from hashlib import sha256

class UsuariosConectadosTest(SimpleTestCase):

    def setUp(self):

        super().setUp()

        self.factory = RequestFactory()

    # =========================================
    # REGISTRAR SESION NUEVA
    # =========================================

    @patch("core.estadisticas.UsuarioConectado")
    def test_registrar_sesion_nueva(self, usuario_mock):

        solicitud = self.factory.get("/")

        solicitud.session = MagicMock()

        solicitud.session.session_key = None

        def crear_sesion():

            solicitud.session.session_key = "sesion_nueva"

        solicitud.session.create.side_effect = crear_sesion

        resultado = registrar_usuario_conectado(
            solicitud
        )

        esperado = sha256(
            "sesion_nueva".encode("utf-8")
        ).hexdigest()

        self.assertEqual(
            resultado,
            esperado
        )

        self.assertEqual(
            len(resultado),
            64
        )

        solicitud.session.create.assert_called_once()

        usuario_mock.objects.update_or_create.assert_called_once()

        argumentos = (
            usuario_mock.objects.update_or_create
            .call_args.kwargs
        )

        self.assertEqual(
            argumentos["id_sesion"],
            esperado
        )

    # =========================================
    # REUTILIZAR SESION EXISTENTE
    # =========================================

    @patch("core.estadisticas.UsuarioConectado")
    def test_reutilizar_sesion(self, usuario_mock):

        solicitud = self.factory.get("/")

        solicitud.session = MagicMock()

        solicitud.session.session_key = "sesion_existente"

        resultado = registrar_usuario_conectado(
            solicitud
        )

        esperado = sha256(
            "sesion_existente".encode("utf-8")
        ).hexdigest()

        self.assertEqual(
            resultado,
            esperado
        )

        solicitud.session.create.assert_not_called()

        usuario_mock.objects.update_or_create.assert_called_once()

    # =========================================
    # CONTAR SESIONES ACTIVAS
    # =========================================

    @patch("core.estadisticas.UsuarioConectado")
    def test_contar_usuarios_activos(self, usuario_mock):

        usuario_mock.objects.filter.return_value \
            .count.return_value = 3

        resultado = contar_usuarios_conectados()

        self.assertEqual(
            resultado,
            3
        )

        usuario_mock.objects.filter.assert_called_once()

    # =========================================
    # TIEMPO LIMITE DE ACTIVIDAD
    # =========================================

    @patch("core.estadisticas.timezone.now")
    @patch("core.estadisticas.UsuarioConectado")
    def test_tiempo_limite(
        self,
        usuario_mock,
        tiempo_mock
    ):

        momento = timezone.now()

        tiempo_mock.return_value = momento

        contar_usuarios_conectados()

        limite = momento - timedelta(minutes=5)

        usuario_mock.objects.filter.assert_called_once_with(
            ultima_actividad__gte=limite
        )

    # =========================================
    # LIMPIAR SESIONES INACTIVAS
    # =========================================

    @patch("core.estadisticas.UsuarioConectado")
    def test_limpiar_inactivos(self, usuario_mock):

        usuario_mock.objects.filter.return_value \
            .delete.return_value = (2, {})

        resultado = limpiar_usuarios_inactivos()

        self.assertEqual(
            resultado,
            2
        )

        usuario_mock.objects.filter.return_value \
            .delete.assert_called_once_with()

    # =========================================
    # CONTADOR EN PAGINAS PUBLICAS
    # =========================================

    @patch(
        "core.context_processors.contar_usuarios_conectados"
    )
    def test_context_processor(self, contador_mock):

        contador_mock.return_value = 4

        solicitud = self.factory.get("/")

        solicitud.resolver_match = resolve("/")

        contexto = contador_usuarios(solicitud)

        self.assertEqual(

            contexto["usuarios_conectados"],

            4

        )

    # =========================================
    # EXCLUIR PANEL ADMINISTRATIVO
    # =========================================

    @patch(
        "core.context_processors.contar_usuarios_conectados"
    )
    def test_excluir_admin(self, contador_mock):

        solicitud = self.factory.get("/admin/")

        solicitud.resolver_match = resolve("/admin/")

        contexto = contador_usuarios(solicitud)

        self.assertEqual(

            contexto["usuarios_conectados"],

            0

        )

        contador_mock.assert_not_called()

    # =========================================
    # API DE ESTADISTICAS
    # =========================================

    @patch("core.views.Visita")
    @patch("core.views.contar_usuarios_conectados")
    @patch("core.views.limpiar_usuarios_inactivos")
    @patch("core.views.registrar_usuario_conectado")
    def test_api_estadisticas(

        self,

        registro_mock,

        limpieza_mock,

        contador_mock,

        visitas_mock

    ):

        contador_mock.return_value = 3

        visitas_mock.objects.count.return_value = 125

        respuesta = self.client.post(

            reverse("core:api_estadisticas")

        )

        self.assertEqual(
            respuesta.status_code,
            200
        )

        self.assertEqual(

            respuesta.json(),

            {
                "total_visitas": 125,
                "usuarios_conectados": 3
            }

        )

        registro_mock.assert_called_once()

        limpieza_mock.assert_called_once()

    # =========================================
    # API NO PERMITE GET
    # =========================================

    def test_api_rechaza_get(self):

        respuesta = self.client.get(

            reverse("core:api_estadisticas")

        )

        self.assertEqual(
            respuesta.status_code,
            405
        )

    # =========================================
    # PROTECCION CSRF
    # =========================================

    def test_api_requiere_csrf(self):

        from django.test import Client

        cliente = Client(
            enforce_csrf_checks=True
        )

        respuesta = cliente.post(

            reverse("core:api_estadisticas")

        )

        self.assertEqual(
            respuesta.status_code,
            403
        )

    # =========================================
    # API NO INCREMENTA LAS VISITAS
    # =========================================

    @patch("core.middleware.Visita")
    @patch("core.views.Visita")
    @patch("core.views.contar_usuarios_conectados")
    @patch("core.views.limpiar_usuarios_inactivos")
    @patch("core.views.registrar_usuario_conectado")
    def test_api_no_registra_visitas(

        self,

        registro_mock,

        limpieza_mock,

        contador_mock,

        visitas_mock,

        middleware_mock

    ):

        contador_mock.return_value = 1

        visitas_mock.objects.count.return_value = 10

        respuesta = self.client.post(

            reverse("core:api_estadisticas")

        )

        self.assertEqual(
            respuesta.status_code,
            200
        )

        middleware_mock.objects.create.assert_not_called()

    # =========================================
    # ARCHIVO JAVASCRIPT
    # =========================================

    def test_archivo_javascript_contadores(self):

        self.assertIsNotNone(

            finders.find("js/contadores.js")

        )