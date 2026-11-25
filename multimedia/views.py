from django.shortcuts import render

from .recursos import VideoInstitucional


# =========================================
# QUIENES SOMOS (CON VIDEO INSTITUCIONAL)
# =========================================

def quienes_somos(request):
    recurso_video = VideoInstitucional()
    contexto = {
        "video": recurso_video.obtener_contexto(),
    }
    return render(request, "multimedia/quienes_somos.html", contexto)


# =========================================
# CASOS DE EXITO
# =========================================

def casos_exito(request):
    casos = [
        {
            "titulo": "Red de Fibra Óptica y Backbone Industrial",
            "sector": "Manufactura Automotriz",
            "resumen": (
                "Diseño, tendido, fusión y certificación de enlaces de fibra "
                "óptica monomodo y multimodo para interconectar naves "
                "industriales con redundancia de alta disponibilidad."
            ),
            "resultados": [
                "Certificación del 100% de los enlaces bajo estándares TIA/EIA.",
                "Incremento de velocidad de transmisión a 10 Gbps en planta.",
                "Reducción del 95% en interrupciones de comunicación.",
            ],
            "icono": "bi-hdd-network-fill",
        },
        {
            "titulo": "Cableado Estructurado Categoría 6A en Corporativo",
            "sector": "Servicios Corporativos y Financieros",
            "resumen": (
                "Instalación de más de 320 nodos de voz y datos con canalización "
                "organizada, racks de telecomunicaciones y paneles de parcheo "
                "de alto desempeño."
            ),
            "resultados": [
                "Infraestructura escalable con garantía extendida.",
                "Documentación y etiquetado normalizado punto a punto.",
                "Integración limpia con telefonía IP y puntos de acceso Wi-Fi.",
            ],
            "icono": "bi-diagram-3-fill",
        },
        {
            "titulo": "Modernización de Tableros y Red Eléctrica Regulada",
            "sector": "Centro de Datos y Operaciones",
            "resumen": (
                "Adecuación de sistema eléctrico de fuerza, tierras físicas y "
                "respaldo mediante UPS para proteger servidores críticos y "
                "equipos de telecomunicaciones."
            ),
            "resultados": [
                "Continuidad operativa ante variaciones de voltaje.",
                "Cumplimiento de normas de seguridad eléctrica industrial.",
                "Monitoreo preventivo de cargas y balanceo de fases.",
            ],
            "icono": "bi-lightning-charge-fill",
        },
        {
            "titulo": "Sistema Integral de Videovigilancia IP y Control",
            "sector": "Logística y Almacenes",
            "resumen": (
                "Implementación de circuito cerrado de televisión (CCTV) de alta "
                "definición con grabación centralizada y monitoreo remoto seguro."
            ),
            "resultados": [
                "Cobertura perimetral y de andenes las 24 horas.",
                "Almacenamiento optimizado con detección inteligente.",
                "Acceso seguro para supervisión en tiempo real.",
            ],
            "icono": "bi-camera-video-fill",
        },
    ]
    contexto = {
        "casos": casos,
    }
    return render(request, "multimedia/casos_exito.html", contexto)


# =========================================
# SOCIOS TECNOLOGICOS
# =========================================

def socios(request):
    socios_lista = [
        {
            "nombre": "PANDUIT™",
            "especialidad": "Infraestructura Física y Cableado Estructurado",
            "descripcion": (
                "Líder mundial en el diseño y fabricación de soluciones de "
                "cableado estructurado, fibra óptica, gabinetes y sistemas de "
                "identificación para centros de datos y entornos industriales."
            ),
            "sitio_web": "https://www.panduit.com/",
            "icono": "bi-ethernet",
        },
        {
            "nombre": "Cisco Systems",
            "especialidad": "Redes Empresariales, Seguridad y Telecomunicaciones",
            "descripcion": (
                "Referente global en conmutación, enrutamiento, redes inalámbricas, "
                "comunicaciones unificadas y ciberseguridad para empresas de "
                "alta exigencia."
            ),
            "sitio_web": "https://www.cisco.com/",
            "icono": "bi-router-fill",
        },
        {
            "nombre": "Fluke Networks",
            "especialidad": "Certificación, Diagnóstico y Pruebas de Red",
            "descripcion": (
                "Equipos de precisión para la certificación, validación y "
                "resolución de problemas en enlaces de cobre y fibra óptica "
                "bajo estándares internacionales."
            ),
            "sitio_web": "https://www.flukenetworks.com/",
            "icono": "bi-speedometer2",
        },
        {
            "nombre": "Schneider Electric",
            "especialidad": "Gestión de Energía y Respaldo Eléctrico",
            "descripcion": (
                "Soluciones de distribución eléctrica, tableros de control, "
                "protección y sistemas de energía ininterrumpida (UPS) para "
                "instalaciones críticas."
            ),
            "sitio_web": "https://www.se.com/",
            "icono": "bi-plug-fill",
        },
    ]
    contexto = {
        "socios": socios_lista,
    }
    return render(request, "multimedia/socios.html", contexto)


# =========================================
# PAGINA DEDICADA DEL VIDEO INSTITUCIONAL
# =========================================

def video_institucional(request):
    recurso_video = VideoInstitucional()
    contexto = {
        "video": recurso_video.obtener_contexto(),
    }
    return render(request, "multimedia/video.html", contexto)
