import os
from pathlib import Path

from django.conf import settings


class VideoInstitucional:
    """
    Clase orientada a objetos encargada de localizar y preparar los recursos
    del video institucional de ParNet Ingeniería (Parte 11.5).

    Permite que el sitio funcione antes y después de subir el archivo de video
    a `media/multimedia/` sin necesidad de modificar el código fuente.
    """

    CARPETA_RELATIVA = "multimedia"
    ARCHIVO_MP4 = "video-institucional.mp4"
    ARCHIVO_WEBM = "video-institucional.webm"
    ARCHIVO_POSTER = "video-institucional-poster.jpg"
    ARCHIVO_SUBTITULOS = "video-institucional.vtt"

    def __init__(self, directorio_media=None, url_media=None):
        self.directorio_media = Path(directorio_media or settings.MEDIA_ROOT)
        self.url_media = (url_media or settings.MEDIA_URL).rstrip("/")
        self.titulo = "Video Institucional — ParNet Ingeniería"
        self.duracion_recomendada = "2 a 4 minutos"
        self.descripcion = (
            "Conoce nuestra página"
        )

    def _ruta_archivo(self, nombre_archivo):
        return self.directorio_media / self.CARPETA_RELATIVA / nombre_archivo

    def _url_archivo(self, nombre_archivo):
        return f"{self.url_media}/{self.CARPETA_RELATIVA}/{nombre_archivo}"

    @property
    def tiene_mp4(self):
        return self._ruta_archivo(self.ARCHIVO_MP4).is_file()

    @property
    def tiene_webm(self):
        return self._ruta_archivo(self.ARCHIVO_WEBM).is_file()

    @property
    def tiene_poster(self):
        return self._ruta_archivo(self.ARCHIVO_POSTER).is_file()

    @property
    def tiene_subtitulos(self):
        return self._ruta_archivo(self.ARCHIVO_SUBTITULOS).is_file()

    @property
    def url_externa(self):
        return (os.getenv("VIDEO_INSTITUCIONAL_URL") or "").strip()

    @property
    def disponible(self):
        return bool(self.tiene_mp4 or self.tiene_webm or self.url_externa)

    def obtener_contexto(self):
        return {
            "titulo": self.titulo,
            "descripcion": self.descripcion,
            "duracion_recomendada": self.duracion_recomendada,
            "disponible": self.disponible,
            "tiene_archivo_local": bool(self.tiene_mp4 or self.tiene_webm),
            "url_mp4": self._url_archivo(self.ARCHIVO_MP4) if self.tiene_mp4 else "",
            "url_webm": self._url_archivo(self.ARCHIVO_WEBM) if self.tiene_webm else "",
            "url_poster": (
                self._url_archivo(self.ARCHIVO_POSTER) if self.tiene_poster else ""
            ),
            "url_subtitulos": (
                self._url_archivo(self.ARCHIVO_SUBTITULOS)
                if self.tiene_subtitulos
                else ""
            ),
            "url_externa": self.url_externa,
            "ruta_esperada": f"media/{self.CARPETA_RELATIVA}/{self.ARCHIVO_MP4}",
        }
