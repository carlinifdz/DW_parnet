from django.test import SimpleTestCase

from core.patrones.singleton import ConfiguracionSistema


class ConfiguracionSistemaTest(SimpleTestCase):

    def test_instancia_unica(self):

        config1 = ConfiguracionSistema()
        config2 = ConfiguracionSistema()

        self.assertIs(config1, config2)

    def test_nombre_empresa(self):

        configuracion = ConfiguracionSistema()

        self.assertEqual(
            configuracion.nombre_empresa,
            "ParNet Ingeniería"
        )

    def test_configuracion_compartida(self):

        config1 = ConfiguracionSistema()
        config2 = ConfiguracionSistema()

        valor_original = config1.registros_por_pagina

        try:

            config1.registros_por_pagina = 25

            self.assertEqual(
                config2.registros_por_pagina,
                25
            )

        finally:

            config1.registros_por_pagina = valor_original

    def test_obtener_configuracion(self):

        configuracion = ConfiguracionSistema()

        datos = configuracion.obtener_configuracion()

        self.assertIsInstance(datos, dict)

        self.assertIn("nombre_empresa", datos)

        self.assertIn("version", datos)

        self.assertIn("moneda", datos)

    def test_context_processor(self):

        respuesta = self.client.get("/")

        self.assertEqual(respuesta.status_code, 200)

        self.assertContains(
            respuesta,
            "ParNet Ingeniería"
        )