from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from django.contrib.auth.models import AnonymousUser
from django.contrib.staticfiles import finders
from django.core.exceptions import PermissionDenied, ValidationError
from django.http import HttpResponse
from django.test import RequestFactory, SimpleTestCase
from django.urls import reverse
from django.views import View
from django_recaptcha.client import RecaptchaResponse

from core.tests import PruebaPublicaBase, simular_noticias
from gestion.autenticacion.forms import LoginAdministradorForm
from gestion.autenticacion.permisos import (
    AdministradorRequeridoMixin,
    PermisoAdministrativoMixin,
    administrador_requerido,
    es_administrador,
    permiso_requerido,
)


def crear_usuario_simulado(
    username="admin",
    is_authenticated=True,
    is_active=True,
    is_staff=True,
    is_superuser=False,
    permisos=None,
):
    permisos_set = set(permisos or [])

    def has_perm(perm):
        return is_superuser or perm in permisos_set

    def has_perms(perms):
        return is_superuser or all(p in permisos_set for p in perms)

    return SimpleNamespace(
        pk=1,
        id=1,
        username=username,
        is_authenticated=is_authenticated,
        is_active=is_active,
        is_staff=is_staff,
        is_superuser=is_superuser,
        get_username=lambda: username,
        get_full_name=lambda: "Administrador ParNet",
        has_perm=has_perm,
        has_perms=has_perms,
    )


class PermisosAdministrativosTest(SimpleTestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_es_administrador_con_staff(self):
        usuario = crear_usuario_simulado(is_staff=True)
        self.assertTrue(es_administrador(usuario))

    def test_es_administrador_rechaza_usuario_comun(self):
        usuario = crear_usuario_simulado(is_staff=False, is_superuser=False)
        self.assertFalse(es_administrador(usuario))

    def test_es_administrador_rechaza_anonimo(self):
        self.assertFalse(es_administrador(AnonymousUser()))

    def test_decorador_administrador_redirige_anonimo(self):
        @administrador_requerido
        def vista_privada(request):
            return HttpResponse("privado")

        request = self.factory.get("/gestion/panel/")
        request.user = AnonymousUser()

        respuesta = vista_privada(request)
        self.assertEqual(respuesta.status_code, 302)
        self.assertIn(reverse("autenticacion:iniciar_sesion"), respuesta.url)

    def test_decorador_administrador_bloquea_no_staff(self):
        @administrador_requerido
        def vista_privada(request):
            return HttpResponse("privado")

        request = self.factory.get("/gestion/panel/")
        request.user = crear_usuario_simulado(is_staff=False)

        with self.assertRaises(PermissionDenied):
            vista_privada(request)

    def test_decorador_administrador_permite_staff(self):
        @administrador_requerido
        def vista_privada(request):
            return HttpResponse("ok")

        request = self.factory.get("/gestion/panel/")
        request.user = crear_usuario_simulado(is_staff=True)

        respuesta = vista_privada(request)
        self.assertEqual(respuesta.status_code, 200)

    def test_decorador_permiso_requerido_verifica_permiso(self):
        @permiso_requerido("productos.change_producto")
        def editar_producto(request):
            return HttpResponse("editado")

        request = self.factory.get("/gestion/productos/editar/")
        request.user = crear_usuario_simulado(is_staff=True, permisos=[])

        with self.assertRaises(PermissionDenied):
            editar_producto(request)

        request.user = crear_usuario_simulado(
            is_staff=True,
            permisos=["productos.change_producto"],
        )
        respuesta = editar_producto(request)
        self.assertEqual(respuesta.status_code, 200)

    def test_mixin_administrador_requerido(self):
        class VistaPanel(AdministradorRequeridoMixin, View):
            def get(self, request):
                return HttpResponse("panel")

        vista = VistaPanel.as_view()

        req_anon = self.factory.get("/gestion/")
        req_anon.user = AnonymousUser()
        resp_anon = vista(req_anon)
        self.assertEqual(resp_anon.status_code, 302)

        req_no_staff = self.factory.get("/gestion/")
        req_no_staff.user = crear_usuario_simulado(is_staff=False)
        with self.assertRaises(PermissionDenied):
            vista(req_no_staff)

        req_staff = self.factory.get("/gestion/")
        req_staff.user = crear_usuario_simulado(is_staff=True)
        resp_staff = vista(req_staff)
        self.assertEqual(resp_staff.status_code, 200)

    def test_mixin_permiso_administrativo(self):
        class VistaEliminar(PermisoAdministrativoMixin, View):
            permission_required = "productos.delete_producto"

            def get(self, request):
                return HttpResponse("eliminado")

        vista = VistaEliminar.as_view()

        req_sin_permiso = self.factory.get("/gestion/eliminar/")
        req_sin_permiso.user = crear_usuario_simulado(is_staff=True, permisos=[])
        with self.assertRaises(PermissionDenied):
            vista(req_sin_permiso)

        req_con_permiso = self.factory.get("/gestion/eliminar/")
        req_con_permiso.user = crear_usuario_simulado(
            is_staff=True,
            permisos=["productos.delete_producto"],
        )
        self.assertEqual(vista(req_con_permiso).status_code, 200)


class AutenticacionVistasTest(PruebaPublicaBase):
    def setUp(self):
        super().setUp()
        parche_noticias = patch("core.context_processors.Noticia")
        self.noticias_mock = parche_noticias.start()
        self.addCleanup(parche_noticias.stop)
        simular_noticias(self.noticias_mock)

    def test_pagina_iniciar_sesion_carga_correctamente(self):
        respuesta = self.client.get(reverse("autenticacion:iniciar_sesion"))
        self.assertEqual(respuesta.status_code, 200)
        self.assertTemplateUsed(
            respuesta,
            "gestion/autenticacion/iniciar_sesion.html",
        )
        self.assertContains(respuesta, "Control de Acceso PARNET")
        self.assertContains(respuesta, "g-recaptcha")

    def test_formulario_incluye_captcha_y_rechaza_no_staff(self):
        form = LoginAdministradorForm()
        self.assertIn("captcha", form.fields)

        usuario_no_staff = crear_usuario_simulado(is_staff=False, is_superuser=False)
        with self.assertRaises(ValidationError):
            form.confirm_login_allowed(usuario_no_staff)

    @patch("django_recaptcha.fields.client.submit")
    @patch("django.contrib.auth.forms.authenticate")
    def test_inicio_sesion_credenciales_invalidas(self, auth_mock, captcha_mock):
        captcha_mock.return_value = RecaptchaResponse(is_valid=True)
        auth_mock.return_value = None

        respuesta = self.client.post(
            reverse("autenticacion:iniciar_sesion"),
            {
                "username": "admin",
                "password": "incorrecta",
                "g-recaptcha-response": "token-prueba",
            },
        )
        self.assertEqual(respuesta.status_code, 200)
        self.assertContains(respuesta, "Las credenciales ingresadas no son válidas")

    def test_cerrar_sesion_requiere_post(self):
        respuesta_get = self.client.get(reverse("autenticacion:cerrar_sesion"))
        self.assertEqual(respuesta_get.status_code, 405)

    @patch("django.contrib.auth.views.auth_logout")
    def test_cerrar_sesion_post_redirige_a_login(self, logout_mock):
        respuesta = self.client.post(reverse("autenticacion:cerrar_sesion"))
        self.assertEqual(respuesta.status_code, 302)
        self.assertEqual(
            respuesta.url,
            reverse("autenticacion:iniciar_sesion"),
        )
        logout_mock.assert_called_once()

    def test_archivo_css_autenticacion_existe(self):
        self.assertIsNotNone(finders.find("css/autenticacion.css"))
