from unittest.mock import patch

from django.test import SimpleTestCase

from django.core.exceptions import ValidationError

from django_recaptcha.fields import ReCaptchaField

from django_recaptcha.widgets import ReCaptchaV2Checkbox

from django_recaptcha.client import RecaptchaResponse

from core.seguridad.captcha import crear_captcha


class CaptchaTest(SimpleTestCase):

    # =========================================
    # COMPROBAR TIPO DE CAMPO
    # =========================================

    def test_tipo_campo(self):

        campo = crear_captcha()

        self.assertIsInstance(
            campo,
            ReCaptchaField
        )


    # =========================================
    # COMPROBAR VERSION DEL CAPTCHA
    # =========================================

    def test_captcha_v2(self):

        campo = crear_captcha()

        self.assertIsInstance(
            campo.widget,
            ReCaptchaV2Checkbox
        )


    # =========================================
    # COMPROBAR CAMPO OBLIGATORIO
    # =========================================

    def test_captcha_obligatorio(self):

        campo = crear_captcha()

        self.assertTrue(
            campo.required
        )


    # =========================================
    # RECHAZAR CAPTCHA VACIO
    # =========================================

    def test_captcha_vacio(self):

        campo = crear_captcha()

        with self.assertRaises(ValidationError):

            campo.clean("")


    # =========================================
    # ACEPTAR CAPTCHA VALIDO
    # =========================================

    @patch("django_recaptcha.fields.client.submit")
    def test_captcha_valido(self, submit_mock):

        submit_mock.return_value = RecaptchaResponse(
            is_valid=True
        )

        campo = crear_captcha()

        resultado = campo.clean(
            "token_de_prueba"
        )

        self.assertEqual(
            resultado,
            "token_de_prueba"
        )

        submit_mock.assert_called_once()


    # =========================================
    # RECHAZAR CAPTCHA INVALIDO
    # =========================================

    @patch("django_recaptcha.fields.client.submit")
    def test_captcha_invalido(self, submit_mock):

        submit_mock.return_value = RecaptchaResponse(

            is_valid=False,

            error_codes=["invalid-input-response"]

        )

        campo = crear_captcha()

        with self.assertRaises(ValidationError):

            campo.clean(
                "token_invalido"
            )


    # =========================================
    # COMPROBAR IDIOMA
    # =========================================

    def test_idioma_captcha(self):

        campo = crear_captcha()

        self.assertEqual(

            campo.widget.api_params.get("hl"),

            "es"

        )