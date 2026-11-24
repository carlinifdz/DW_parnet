from unittest.mock import patch
from django.test import SimpleTestCase, RequestFactory
from django.http import HttpResponse
from django.urls import resolve
from core.middleware import RegistroVisitasMiddleware
from core.context_processors import contador_visitas


class VisitasTest(SimpleTestCase):

    def setUp(self):

        super().setUp()

        self.factory = RequestFactory()

        # Simular el registro de actividad

        parche_usuarios = patch(
            "core.middleware.registrar_usuario_conectado"
        )

        self.usuarios_mock = parche_usuarios.start()

        self.addCleanup(parche_usuarios.stop)


    def crear_solicitud(self, ruta="/", metodo="GET"):

        solicitud = self.factory.generic(
            metodo,
            ruta
        )

        solicitud.resolver_match = resolve(ruta)

        return solicitud


    def ejecutar_middleware(
        self,
        solicitud,
        estado=200,
        tipo="text/html"
    ):

        def respuesta(request):

            return HttpResponse(
                "Respuesta de prueba",
                status=estado,
                content_type=tipo
            )

        middleware = RegistroVisitasMiddleware(
            respuesta
        )

        return middleware(solicitud)


    # =========================================
    # REGISTRAR PAGINA PRINCIPAL
    # =========================================

    @patch("core.middleware.Visita")
    def test_registrar_visita(self, visita_mock):

        solicitud = self.crear_solicitud("/")

        respuesta = self.ejecutar_middleware(
            solicitud
        )

        self.assertEqual(
            respuesta.status_code,
            200
        )

        visita_mock.objects.create.assert_called_once_with(
            pagina="/"
        )

    # =========================================
    # REGISTRAR PAGINA DE CLIENTES
    # =========================================

    @patch("core.middleware.Visita")
    def test_registrar_clientes(self, visita_mock):

        solicitud = self.crear_solicitud(
            "/clientes/"
        )

        self.ejecutar_middleware(solicitud)

        visita_mock.objects.create.assert_called_once_with(
            pagina="/clientes/"
        )

    # =========================================
    # EXCLUIR ADMINISTRACION
    # =========================================

    @patch("core.middleware.Visita")
    def test_excluir_admin(self, visita_mock):

        solicitud = self.crear_solicitud(
            "/admin/"
        )

        self.ejecutar_middleware(solicitud)

        visita_mock.objects.create.assert_not_called()

    # =========================================
    # EXCLUIR SOLICITUDES POST
    # =========================================

    @patch("core.middleware.Visita")
    def test_excluir_post(self, visita_mock):

        solicitud = self.crear_solicitud(
            "/",
            metodo="POST"
        )

        self.ejecutar_middleware(solicitud)

        visita_mock.objects.create.assert_not_called()

    # =========================================
    # EXCLUIR RESPUESTAS FALLIDAS
    # =========================================

    @patch("core.middleware.Visita")
    def test_excluir_error_404(self, visita_mock):

        solicitud = self.crear_solicitud(
            "/noticias/999/"
        )

        self.ejecutar_middleware(
            solicitud,
            estado=404
        )

        visita_mock.objects.create.assert_not_called()

    # =========================================
    # EXCLUIR RESPUESTAS NO HTML
    # =========================================

    @patch("core.middleware.Visita")
    def test_excluir_json(self, visita_mock):

        solicitud = self.crear_solicitud("/")

        self.ejecutar_middleware(
            solicitud,
            tipo="application/json"
        )

        visita_mock.objects.create.assert_not_called()

    # =========================================
    # EXCLUIR ARCHIVOS ESTATICOS
    # =========================================

    @patch("core.middleware.Visita")
    def test_excluir_archivos_estaticos(
        self,
        visita_mock
    ):

        solicitud = self.factory.get(
            "/static/css/estilos.css"
        )

        solicitud.resolver_match = None

        self.ejecutar_middleware(
            solicitud,
            tipo="text/css"
        )

        visita_mock.objects.create.assert_not_called()

    # =========================================
    # CONSULTAR TOTAL DE VISITAS
    # =========================================

    @patch("core.context_processors.Visita")
    def test_contador_visitas(self, visita_mock):

        visita_mock.objects.count.return_value = 25

        solicitud = self.crear_solicitud("/")

        contexto = contador_visitas(solicitud)

        self.assertEqual(
            contexto["total_visitas"],
            26
        )

        visita_mock.objects.count.assert_called_once_with()


    # =========================================
    # CONTADOR SIN REGISTROS
    # =========================================

    @patch("core.context_processors.Visita")
    def test_contador_inicial(self, visita_mock):

        visita_mock.objects.count.return_value = 0

        solicitud = self.crear_solicitud("/")

        contexto = contador_visitas(solicitud)

        self.assertEqual(
            contexto["total_visitas"],
            1
        )

    # =========================================
    # NO CONSULTAR CONTADOR EN ADMIN
    # =========================================

    @patch("core.context_processors.Visita")
    def test_contador_admin(self, visita_mock):

        solicitud = self.crear_solicitud(
            "/admin/"
        )

        contexto = contador_visitas(solicitud)

        self.assertEqual(
            contexto["total_visitas"],
            0
        )

        visita_mock.objects.count.assert_not_called()