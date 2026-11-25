from django import forms

from core.seguridad.captcha import crear_captcha

from .models import SolicitudServicio

from .consultas import areas_activas

from .validadores import (
    validar_nombre,
    validar_telefono,
    validar_detalle,
)


# =========================================
# FORMULARIO DE SOLICITUD DE SERVICIO
# =========================================

class SolicitudServicioForm(forms.ModelForm):

    captcha = crear_captcha()


    class Meta:

        model = SolicitudServicio

        fields = [

            "area",
            "nombre",
            "empresa",
            "correo",
            "telefono",
            "detalle",

        ]

        labels = {

            "area": "Área de servicio",

            "nombre": "Nombre completo",

            "empresa": "Empresa",

            "correo": "Correo electrónico",

            "telefono": "Teléfono",

            "detalle": "Detalle de la solicitud",

        }

        widgets = {

            "area": forms.Select(

                attrs={
                    "class": "solicitud-control",
                }

            ),

            "nombre": forms.TextInput(

                attrs={
                    "class": "solicitud-control",
                    "placeholder": "Nombre del solicitante",
                    "autocomplete": "name",
                    "minlength": 3,
                }

            ),

            "empresa": forms.TextInput(

                attrs={
                    "class": "solicitud-control",
                    "placeholder": "Nombre de la empresa",
                    "autocomplete": "organization",
                }

            ),

            "correo": forms.EmailInput(

                attrs={
                    "class": "solicitud-control",
                    "placeholder": "correo@ejemplo.com",
                    "autocomplete": "email",
                }

            ),

            "telefono": forms.TextInput(

                attrs={
                    "class": "solicitud-control",
                    "type": "tel",
                    "placeholder": "Número telefónico",
                    "autocomplete": "tel",
                    "inputmode": "tel",
                }

            ),

            "detalle": forms.Textarea(

                attrs={
                    "class": "solicitud-control",
                    "placeholder": (
                        "Describa el servicio que necesita..."
                    ),
                    "rows": 6,
                    "minlength": 10,
                    "maxlength": 2000,
                }

            ),

        }

        error_messages = {

            "area": {

                "required": (
                    "Debes seleccionar un área de servicio."
                ),

                "invalid_choice": (
                    "El área seleccionada no existe "
                    "o no está disponible."
                ),

            },

            "nombre": {

                "required": (
                    "Debes ingresar tu nombre completo."
                ),

                "max_length": (
                    "El nombre supera la longitud permitida."
                ),

            },

            "empresa": {

                "max_length": (
                    "El nombre de la empresa supera "
                    "la longitud permitida."
                ),

            },

            "correo": {

                "required": (
                    "Debes ingresar un correo electrónico."
                ),

                "invalid": (
                    "Ingresa un correo electrónico válido."
                ),

                "max_length": (
                    "El correo electrónico supera "
                    "la longitud permitida."
                ),

            },

            "telefono": {

                "max_length": (
                    "El teléfono supera la longitud permitida."
                ),

            },

            "detalle": {

                "required": (
                    "Debes describir el servicio que necesitas."
                ),

            },

        }


    # =========================================
    # CONFIGURACION DEL FORMULARIO
    # =========================================

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        # Mostrar solamente areas activas

        self.fields["area"].queryset = areas_activas()

        self.fields["area"].empty_label = (
            "Seleccione un área de servicio"
        )

        # Campos obligatorios

        self.fields["area"].required = True

        self.fields["nombre"].required = True

        self.fields["correo"].required = True

        self.fields["detalle"].required = True

        # Campos opcionales

        self.fields["empresa"].required = False

        self.fields["telefono"].required = False

        # Textos de ayuda

        self.fields["telefono"].help_text = (
            "Puedes incluir la clave de país."
        )

        self.fields["detalle"].help_text = (
            "Describe tu solicitud utilizando "
            "entre 10 y 2000 caracteres."
        )


    # =========================================
    # VALIDAR NOMBRE
    # =========================================

    def clean_nombre(self):

        nombre = self.cleaned_data["nombre"]

        return validar_nombre(nombre)


    # =========================================
    # VALIDAR EMPRESA
    # =========================================

    def clean_empresa(self):

        empresa = self.cleaned_data.get(
            "empresa",
            ""
        )

        return " ".join(empresa.split())


    # =========================================
    # VALIDAR CORREO ELECTRONICO
    # =========================================

    def clean_correo(self):

        correo = self.cleaned_data["correo"].strip()

        usuario, dominio = correo.rsplit("@", 1)

        return f"{usuario}@{dominio.lower()}"


    # =========================================
    # VALIDAR TELEFONO
    # =========================================

    def clean_telefono(self):

        telefono = self.cleaned_data.get(
            "telefono",
            ""
        )

        return validar_telefono(telefono)


    # =========================================
    # VALIDAR DETALLE
    # =========================================

    def clean_detalle(self):

        detalle = self.cleaned_data["detalle"]

        return validar_detalle(detalle)