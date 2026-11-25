from unittest.mock import patch

from django.test import SimpleTestCase, RequestFactory

from django.core.exceptions import ValidationError

from servicios.validadores import (
    validar_nombre,
    validar_telefono,
    validar_detalle,
)

from servicios.forms import SolicitudServicioForm

from servicios.models import AreaServicio

from servicios.views import solicitar_servicio


# =========================================
# PRUEBAS DE VALIDADORES
# =========================================

class ValidadoresSolicitudTest(SimpleTestCase):

    def test_nombre_valido(self):

        resultado = validar_nombre(
            "Carlos Hernández"
        )

        self.assertEqual(
            resultado,
            "Carlos Hernández"
        )


    def test_nombre_con_acentos(self):

        resultado = validar_nombre(
            "María José López"
        )

        self.assertEqual(
            resultado,
            "María José López"
        )


    def test_nombre_con_guion(self):

        resultado = validar_nombre(
            "Jean-Pierre"
        )

        self.assertEqual(
            resultado,
            "Jean-Pierre"
        )


    def test_nombre_con_numeros(self):

        with self.assertRaises(ValidationError):

            validar_nombre("Carlos123")


    def test_nombre_demasiado_corto(self):

        with self.assertRaises(ValidationError):

            validar_nombre("A")


    def test_nombre_con_simbolos(self):

        with self.assertRaises(ValidationError):

            validar_nombre("@#$%")


    def test_normalizar_espacios_nombre(self):

        resultado = validar_nombre(
            "  Carlos    Hernández  "
        )

        self.assertEqual(
            resultado,
            "Carlos Hernández"
        )


    def test_telefono_nacional(self):

        resultado = validar_telefono(
            "8441234567"
        )

        self.assertEqual(
            resultado,
            "8441234567"
        )


    def test_telefono_internacional(self):

        resultado = validar_telefono(
            "+52 844 123 4567"
        )

        self.assertEqual(
            resultado,
            "+52 844 123 4567"
        )


    def test_telefono_con_parentesis(self):

        resultado = validar_telefono(
            "(844) 123-4567"
        )

        self.assertEqual(
            resultado,
            "(844) 123-4567"
        )


    def test_telefono_con_letras(self):

        with self.assertRaises(ValidationError):

            validar_telefono("844ABC4567")


    def test_telefono_demasiado_corto(self):

        with self.assertRaises(ValidationError):

            validar_telefono("123")


    def test_telefono_demasiado_largo(self):

        with self.assertRaises(ValidationError):

            validar_telefono(
                "1234567890123456"
            )


    def test_telefono_opcional(self):

        self.assertEqual(
            validar_telefono(""),
            ""
        )


    def test_detalle_valido(self):

        detalle = (
            "Solicito información sobre "
            "la instalación de fibra óptica."
        )

        self.assertEqual(
            validar_detalle(detalle),
            detalle
        )


    def test_detalle_demasiado_corto(self):

        with self.assertRaises(ValidationError):

            validar_detalle("Ayuda")


    def test_detalle_demasiado_largo(self):

        with self.assertRaises(ValidationError):

            validar_detalle("A" * 2001)


    def test_normalizar_espacios_detalle(self):

        resultado = validar_detalle(
            "  Solicito información del servicio.  "
        )

        self.assertEqual(
            resultado,
            "Solicito información del servicio."
        )


# =========================================
# PRUEBAS DE CAMPOS DEL FORMULARIO
# =========================================

class ValidacionFormularioTest(SimpleTestCase):

    def setUp(self):

        super().setUp()

        parche = patch(
            "servicios.forms.areas_activas"
        )

        self.areas_mock = parche.start()

        self.addCleanup(parche.stop)

        self.areas_mock.return_value = (
            AreaServicio.objects.none()
        )

        self.formulario = SolicitudServicioForm()


    def test_campos_obligatorios(self):

        campos = [

            "area",

            "nombre",

            "correo",

            "detalle",

            "captcha",

        ]

        for campo in campos:

            with self.subTest(campo=campo):

                self.assertTrue(

                    self.formulario.fields[campo].required

                )


    def test_campos_opcionales(self):

        self.assertFalse(

            self.formulario.fields["empresa"].required

        )

        self.assertFalse(

            self.formulario.fields["telefono"].required

        )


    def test_correo_invalido(self):

        campo = self.formulario.fields["correo"]

        with self.assertRaises(ValidationError):

            campo.clean("correo-invalido")


    def test_correo_valido(self):

        campo = self.formulario.fields["correo"]

        resultado = campo.clean(
            "correo@example.com"
        )

        self.assertEqual(
            resultado,
            "correo@example.com"
        )


    def test_normalizar_correo(self):

        self.formulario.cleaned_data = {

            "correo": "Usuario@EXAMPLE.COM"

        }

        resultado = (
            self.formulario.clean_correo()
        )

        self.assertEqual(

            resultado,

            "Usuario@example.com"

        )


    def test_normalizar_empresa(self):

        self.formulario.cleaned_data = {

            "empresa": "  Empresa    Ejemplo  "

        }

        resultado = (
            self.formulario.clean_empresa()
        )

        self.assertEqual(

            resultado,

            "Empresa Ejemplo"

        )


    def test_area_inexistente(self):

        campo = self.formulario.fields["area"]

        with self.assertRaises(ValidationError):

            campo.clean("999999")
