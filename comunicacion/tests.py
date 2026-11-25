from unittest.mock import patch

from django.contrib.staticfiles import finders
from django.core import mail
from django.test import override_settings
from django.urls import reverse
from django_recaptcha.client import RecaptchaResponse

from comunicacion.forms import ContactoForm, SugerenciaForm
from comunicacion.servicios import ServicioCorreo
from core.tests import PruebaPublicaBase, simular_noticias


@override_settings(
    EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend"
)
class ComunicacionTest(PruebaPublicaBase):
    def setUp(self):
        super().setUp()
        parche_noticias = patch("core.context_processors.Noticia")
        self.noticias_mock = parche_noticias.start()
        self.addCleanup(parche_noticias.stop)
        simular_noticias(self.noticias_mock)

    # =========================================
    # CONTACTO POR CORREO ELECTRONICO
    # =========================================

    def test_pagina_contacto_carga_correctamente(self):
        respuesta = self.client.get(reverse("comunicacion:contacto"))
        self.assertEqual(respuesta.status_code, 200)
        self.assertTemplateUsed(respuesta, "comunicacion/contacto.html")
        self.assertContains(respuesta, "Formulario de Contacto por Correo Electrónico")

    def test_envio_contacto_valido_despacha_correo(self):
        datos = {
            "nombre": "Carlos Hernández",
            "correo": "carlos@empresa.com",
            "telefono": "8441234567",
            "asunto": "Cotización de cableado estructurado",
            "mensaje": "Solicito información y cotización para 40 nodos de red.",
        }
        respuesta = self.client.post(reverse("comunicacion:contacto"), datos)
        self.assertRedirects(respuesta, reverse("comunicacion:contacto"))
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("Cotización de cableado estructurado", mail.outbox[0].subject)
        self.assertEqual(mail.outbox[0].reply_to, ["carlos@empresa.com"])

    def test_contacto_datos_invalidos_muestra_errores(self):
        datos = {
            "nombre": "A",
            "correo": "correo-invalido",
            "asunto": "Sol",
            "mensaje": "Corto",
        }
        respuesta = self.client.post(reverse("comunicacion:contacto"), datos)
        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(len(mail.outbox), 0)
        self.assertContains(
            respuesta,
            "Por favor corrige los errores señalados en el formulario de contacto.",
        )

    def test_servicio_correo_construye_cuerpo(self):
        servicio = ServicioCorreo(destinatario="destino@parnet.com.mx")
        cuerpo = servicio.construir_cuerpo(
            {
                "nombre": "Ana López",
                "correo": "ana@cliente.com",
                "telefono": "",
                "asunto": "Soporte",
                "mensaje": "Requerimos mantenimiento preventivo.",
            }
        )
        self.assertIn("Ana López", cuerpo)
        self.assertIn("No especificado", cuerpo)

    # =========================================
    # BUZON DE SUGERENCIAS CON CAPTCHA
    # =========================================

    def test_pagina_sugerencias_carga_con_captcha(self):
        respuesta = self.client.get(reverse("comunicacion:sugerencias"))
        self.assertEqual(respuesta.status_code, 200)
        self.assertTemplateUsed(respuesta, "comunicacion/sugerencias.html")
        self.assertContains(respuesta, "Buzón de Sugerencias")
        self.assertContains(respuesta, "g-recaptcha")

    @patch("comunicacion.forms.Sugerencia.save")
    @patch("django_recaptcha.fields.client.submit")
    def test_guardar_sugerencia_valida_en_mysql(self, captcha_mock, save_mock):
        captcha_mock.return_value = RecaptchaResponse(is_valid=True)

        datos = {
            "nombre": "María Fernanda",
            "correo": "maria@correo.com",
            "mensaje": "Excelente atención técnica en la instalación de fibra óptica.",
            "g-recaptcha-response": "token-valido",
        }
        respuesta = self.client.post(reverse("comunicacion:sugerencias"), datos)
        self.assertRedirects(respuesta, reverse("comunicacion:sugerencias"))
        save_mock.assert_called_once()

    def test_sugerencia_sin_captcha_es_rechazada(self):
        form = SugerenciaForm(
            data={
                "nombre": "Pedro Gómez",
                "correo": "pedro@correo.com",
                "mensaje": "Sugerencia válida con más de diez caracteres.",
            }
        )
        self.assertFalse(form.is_valid())
        self.assertIn("captcha", form.errors)

    def test_archivos_estaticos_comunicacion(self):
        self.assertIsNotNone(finders.find("css/comunicacion.css"))
        self.assertIsNotNone(finders.find("js/comunicacion.js"))
