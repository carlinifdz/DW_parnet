import os
from threading import Lock


class ConfiguracionSistema:
    """
    Implementación del patrón de diseño Singleton.

    Centraliza la configuración general de ParNet Ingeniería
    mediante una única instancia por proceso.
    """

    _instancia = None
    _bloqueo = Lock()

    def __new__(cls):

        with cls._bloqueo:

            if cls._instancia is None:

                instancia = super().__new__(cls)
                instancia._cargar_configuracion()

                cls._instancia = instancia

        return cls._instancia

    def _cargar_configuracion(self):

        self.nombre_empresa = "ParNet Ingeniería"

        self.descripcion = (
            "Soluciones y servicios de ingeniería industrial"
        )

        self.version = "1.0.0"

        self.registros_por_pagina = 10

        self.tiempo_usuario_activo = 5

        self.correo_contacto = os.getenv(
            "CORREO_CONTACTO",
            "contacto@example.com"
        )

        self.moneda = "MXN"

        self.idioma = "es-mx"

        self.zona_horaria = "America/Monterrey"

    def obtener_configuracion(self):

        return {
            "nombre_empresa": self.nombre_empresa,
            "descripcion": self.descripcion,
            "version": self.version,
            "registros_por_pagina": self.registros_por_pagina,
            "tiempo_usuario_activo": self.tiempo_usuario_activo,
            "correo_contacto": self.correo_contacto,
            "moneda": self.moneda,
            "idioma": self.idioma,
            "zona_horaria": self.zona_horaria,
        }

    def __str__(self):

        return f"{self.nombre_empresa} - v{self.version}"