from django.conf import settings
from django.core.mail import EmailMessage

from core.patrones.singleton import ConfiguracionSistema


class ServicioCorreo:
    """
    Clase orientada a objetos encargada de construir y despachar los
    correos electrónicos de contacto de ParNet Ingeniería.
    """

    def __init__(self, destinatario=None, remitente=None):
        configuracion = ConfiguracionSistema()
        self.nombre_empresa = configuracion.nombre_empresa
        self.destinatario = destinatario or configuracion.correo_contacto
        self.remitente = remitente or getattr(
            settings,
            "DEFAULT_FROM_EMAIL",
            self.destinatario,
        )

    def construir_cuerpo(self, datos):
        telefono = datos.get("telefono") or "No especificado"
        lineas = [
            f"Nuevo mensaje de contacto recibido en {self.nombre_empresa}",
            "=" * 55,
            f"Nombre: {datos['nombre']}",
            f"Correo: {datos['correo']}",
            f"Teléfono: {telefono}",
            f"Asunto: {datos['asunto']}",
            "-" * 55,
            "Mensaje:",
            datos["mensaje"],
        ]
        return "\n".join(lineas)

    def enviar_contacto(self, datos):
        asunto_correo = f"[Contacto {self.nombre_empresa}] {datos['asunto']}"
        cuerpo = self.construir_cuerpo(datos)

        correo = EmailMessage(
            subject=asunto_correo,
            body=cuerpo,
            from_email=self.remitente,
            to=[self.destinatario],
            reply_to=[datos["correo"]],
        )
        return correo.send(fail_silently=False)
