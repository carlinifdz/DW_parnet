from django.contrib import messages
from django.shortcuts import redirect, render

from core.patrones.singleton import ConfiguracionSistema
from .forms import ContactoForm, SugerenciaForm
from .servicios import ServicioCorreo


# =========================================
# PAGINA PRINCIPAL DE CONTACTO Y SUGERENCIAS
# =========================================

def contacto(request):
    """
    Muestra la página de contacto de ParNet Ingeniería con el formulario
    de contacto por correo electrónico y un acceso/formulario de sugerencias.
    """
    configuracion = ConfiguracionSistema()
    form_contacto = ContactoForm()
    form_sugerencia = SugerenciaForm()

    if request.method == "POST":
        form_contacto = ContactoForm(request.POST)
        if form_contacto.is_valid():
            servicio = ServicioCorreo()
            try:
                servicio.enviar_contacto(form_contacto.cleaned_data)
                messages.success(
                    request,
                    "Tu mensaje de contacto ha sido enviado correctamente. "
                    "Nuestro equipo se pondrá en comunicación contigo a la brevedad.",
                )
                return redirect("comunicacion:contacto")
            except Exception:
                messages.error(
                    request,
                    "Ocurrió un inconveniente al enviar el correo electrónico. "
                    "Por favor, inténtalo nuevamente más tarde.",
                )
        else:
            messages.error(
                request,
                "Por favor corrige los errores señalados en el formulario de contacto.",
            )

    contexto = {
        "form_contacto": form_contacto,
        "form_sugerencia": form_sugerencia,
        "correo_empresa": configuracion.correo_contacto,
    }
    return render(request, "comunicacion/contacto.html", contexto)


# =========================================
# BUZON DE SUGERENCIAS CON CAPTCHA
# =========================================

def sugerencias(request):
    """
    Gestiona el buzón interno de sugerencias con verificación CAPTCHA
    y almacenamiento en la tabla `sugerencias` mediante el ORM de Django.
    """
    if request.method == "POST":
        form_sugerencia = SugerenciaForm(request.POST)
        if form_sugerencia.is_valid():
            sugerencia = form_sugerencia.save(commit=False)
            sugerencia.leida = False
            sugerencia.save()
            messages.success(
                request,
                "¡Gracias por tu sugerencia! Ha quedado registrada en nuestro "
                "sistema para su revisión continua.",
            )
            return redirect("comunicacion:sugerencias")
        messages.error(
            request,
            "No fue posible registrar la sugerencia. Verifica los campos "
            "marcados y completa la verificación CAPTCHA.",
        )
    else:
        form_sugerencia = SugerenciaForm()

    contexto = {
        "form_sugerencia": form_sugerencia,
    }
    return render(request, "comunicacion/sugerencias.html", contexto)
