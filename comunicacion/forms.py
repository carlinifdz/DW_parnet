from django import forms

from core.seguridad.captcha import crear_captcha
from .models import Sugerencia


class ContactoForm(forms.Form):
    """
    Formulario de contacto por correo electrónico de ParNet Ingeniería.
    Realiza validaciones del lado del servidor sobre los datos ingresados.
    """

    nombre = forms.CharField(
        label="Nombre completo",
        max_length=150,
        min_length=3,
        widget=forms.TextInput(
            attrs={
                "class": "form-control campo-parnet",
                "placeholder": "Ej. Ing. Roberto Garza",
                "maxlength": "150",
            }
        ),
        error_messages={
            "required": "El nombre completo es obligatorio.",
            "min_length": "El nombre debe tener al menos 3 caracteres.",
            "max_length": "El nombre no puede exceder 150 caracteres.",
        },
    )

    correo = forms.EmailField(
        label="Correo electrónico",
        max_length=150,
        widget=forms.EmailInput(
            attrs={
                "class": "form-control campo-parnet",
                "placeholder": "ejemplo@empresa.com",
                "maxlength": "150",
            }
        ),
        error_messages={
            "required": "El correo electrónico es obligatorio.",
            "invalid": "Ingresa una dirección de correo electrónico válida.",
        },
    )

    telefono = forms.CharField(
        label="Teléfono (opcional)",
        max_length=20,
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "form-control campo-parnet",
                "placeholder": "Ej. 844 123 4567",
                "maxlength": "20",
            }
        ),
    )

    asunto = forms.CharField(
        label="Asunto",
        max_length=150,
        min_length=4,
        widget=forms.TextInput(
            attrs={
                "class": "form-control campo-parnet",
                "placeholder": "Cotización o información de soluciones",
                "maxlength": "150",
            }
        ),
        error_messages={
            "required": "El asunto es obligatorio.",
            "min_length": "El asunto debe tener al menos 4 caracteres.",
        },
    )

    mensaje = forms.CharField(
        label="Mensaje",
        min_length=10,
        max_length=2000,
        widget=forms.Textarea(
            attrs={
                "class": "form-control campo-parnet",
                "rows": 4,
                "placeholder": "Describe tu requerimiento o consulta...",
                "maxlength": "2000",
                "data-contador-max": "2000",
            }
        ),
        error_messages={
            "required": "El mensaje es obligatorio.",
            "min_length": "El mensaje debe contener al menos 10 caracteres.",
        },
    )

    def clean_nombre(self):
        nombre = (self.cleaned_data.get("nombre") or "").strip()
        if len(nombre) < 3:
            raise forms.ValidationError(
                "El nombre debe tener al menos 3 caracteres válidos."
            )
        return nombre

    def clean_asunto(self):
        asunto = (self.cleaned_data.get("asunto") or "").strip()
        if len(asunto) < 4:
            raise forms.ValidationError(
                "El asunto debe tener al menos 4 caracteres válidos."
            )
        return asunto

    def clean_mensaje(self):
        mensaje = (self.cleaned_data.get("mensaje") or "").strip()
        if len(mensaje) < 10:
            raise forms.ValidationError(
                "El mensaje debe contener al menos 10 caracteres válidos."
            )
        return mensaje


class SugerenciaForm(forms.ModelForm):
    """
    Formulario para el buzón interno de sugerencias de ParNet Ingeniería.
    Almacena en la tabla `sugerencias` mediante el ORM de Django y valida CAPTCHA.
    """

    nombre = forms.CharField(
        label="Nombre completo",
        max_length=150,
        min_length=3,
        widget=forms.TextInput(
            attrs={
                "class": "form-control campo-parnet",
                "placeholder": "Tu nombre completo",
                "maxlength": "150",
            }
        ),
        error_messages={
            "required": "Debes indicar tu nombre.",
            "min_length": "El nombre debe tener al menos 3 caracteres.",
        },
    )

    correo = forms.EmailField(
        label="Correo electrónico",
        max_length=150,
        widget=forms.EmailInput(
            attrs={
                "class": "form-control campo-parnet",
                "placeholder": "tucorreo@dominio.com",
                "maxlength": "150",
            }
        ),
        error_messages={
            "required": "Debes ingresar tu correo electrónico.",
            "invalid": "Ingresa un correo electrónico válido.",
        },
    )

    mensaje = forms.CharField(
        label="Sugerencia o comentario",
        min_length=10,
        max_length=2000,
        widget=forms.Textarea(
            attrs={
                "class": "form-control campo-parnet",
                "rows": 4,
                "placeholder": "Comparte tu sugerencia para mejorar nuestros servicios...",
                "maxlength": "2000",
                "data-contador-max": "2000",
            }
        ),
        error_messages={
            "required": "Debes escribir tu sugerencia.",
            "min_length": "La sugerencia debe contener al menos 10 caracteres.",
        },
    )

    captcha = crear_captcha()

    class Meta:
        model = Sugerencia
        fields = ["nombre", "correo", "mensaje"]

    def clean_nombre(self):
        nombre = (self.cleaned_data.get("nombre") or "").strip()
        if len(nombre) < 3:
            raise forms.ValidationError(
                "El nombre debe tener al menos 3 caracteres válidos."
            )
        return nombre

    def clean_mensaje(self):
        mensaje = (self.cleaned_data.get("mensaje") or "").strip()
        if len(mensaje) < 10:
            raise forms.ValidationError(
                "La sugerencia debe contener al menos 10 caracteres válidos."
            )
        return mensaje
