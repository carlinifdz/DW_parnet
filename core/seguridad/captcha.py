from django_recaptcha.fields import ReCaptchaField
from django_recaptcha.widgets import ReCaptchaV2Checkbox

# =========================================
# CAMPO RECAPTCHA REUTILIZABLE
# =========================================

def crear_captcha():

    return ReCaptchaField(

        label="Verificación de seguridad",

        required=True,

        widget=ReCaptchaV2Checkbox(

            attrs={

                "data-theme": "light",

                "data-size": "normal",

            },

            api_params={

                "hl": "es",

            }

        ),

        error_messages={

            "required": (
                "Debes completar la verificación de seguridad."
            ),

            "captcha_invalid": (
                "La verificación CAPTCHA no es válida."
            ),

            "captcha_error": (
                "No fue posible verificar el CAPTCHA. "
                "Inténtalo nuevamente."
            ),

        }

    )