import tempfile
from pathlib import Path
from unittest.mock import patch

from django.contrib.staticfiles import finders
from django.urls import reverse

from core.tests import PruebaPublicaBase, simular_noticias
from multimedia.recursos import VideoInstitucional


class MultimediaTest(PruebaPublicaBase):
    def setUp(self):
        super().setUp()
        parche_noticias = patch("core.context_processors.Noticia")
        self.noticias_mock = parche_noticias.start()
        self.addCleanup(parche_noticias.stop)
        simular_noticias(self.noticias_mock)

    def test_pagina_quienes_somos_carga_correctamente(self):
        respuesta = self.client.get(reverse("multimedia:quienes_somos"))
        self.assertEqual(respuesta.status_code, 200)
        self.assertTemplateUsed(respuesta, "multimedia/quienes_somos.html")
        self.assertContains(respuesta, "Acerca de ParNet Ingeniería")
        self.assertContains(respuesta, "Misión")
        self.assertContains(respuesta, "Visión")

    def test_pagina_casos_exito_carga_correctamente(self):
        respuesta = self.client.get(reverse("multimedia:casos_exito"))
        self.assertEqual(respuesta.status_code, 200)
        self.assertTemplateUsed(respuesta, "multimedia/casos_exito.html")
        self.assertContains(respuesta, "Proyectos y Casos de Éxito")

    def test_pagina_socios_carga_correctamente(self):
        respuesta = self.client.get(reverse("multimedia:socios"))
        self.assertEqual(respuesta.status_code, 200)
        self.assertTemplateUsed(respuesta, "multimedia/socios.html")
        self.assertContains(respuesta, "Socios Tecnológicos y Alianzas")
        self.assertContains(respuesta, "PANDUIT")

    def test_pagina_video_sin_archivo_muestra_espacio_preparado(self):
        respuesta = self.client.get(reverse("multimedia:video"))
        self.assertEqual(respuesta.status_code, 200)
        self.assertTemplateUsed(respuesta, "multimedia/video.html")
        self.assertContains(respuesta, "Video Institucional en Preparación")
        self.assertContains(respuesta, "media/multimedia/video-institucional.mp4")

    def test_clase_video_institucional_detecta_archivo_mp4(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            carpeta = Path(tmp_dir) / "multimedia"
            carpeta.mkdir(parents=True, exist_ok=True)
            archivo_mp4 = carpeta / "video-institucional.mp4"
            archivo_mp4.write_bytes(b"fake-mp4-data")

            recurso = VideoInstitucional(directorio_media=tmp_dir, url_media="/media/")
            ctx = recurso.obtener_contexto()
            self.assertTrue(ctx["disponible"])
            self.assertTrue(ctx["tiene_archivo_local"])
            self.assertEqual(
                ctx["url_mp4"],
                "/media/multimedia/video-institucional.mp4",
            )

    def test_archivos_estaticos_multimedia(self):
        self.assertIsNotNone(finders.find("css/multimedia.css"))
        self.assertIsNotNone(finders.find("js/multimedia.js"))
