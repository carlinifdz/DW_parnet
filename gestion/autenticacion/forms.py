from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import ValidationError

from core.seguridad.captcha import crear_captcha


class LoginAdministradorForm(AuthenticationForm):
    """
    Formulario de inicio de sesión para administradores de ParNet Ingeniería.
    Utiliza el sistema de autenticación de Django, verifica que el usuario
    tenga privilegios administrativos (is_staff) e integra CAPTCHA.
    """

    username = forms.CharField(
        label="Usuario",
        max_length=150,
        widget=forms.TextInput(
            attrs={
                "class": "form-control campo-parnet",
                "placeholder": "Ingresa tu nombre de usuario",
                "autocomplete": "username",
                "autofocus": True,
            }
        ),
        error_messages={
            "required": "Debes ingresar tu nombre de usuario.",
        },
    )

    password = forms.CharField(
        label="Contraseña",
        strip=False,
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control campo-parnet",
                "placeholder": "Ingresa tu contraseña",
                "autocomplete": "current-password",
            }
        ),
        error_messages={
            "required": "Debes ingresar tu contraseña.",
        },
    )

    captcha = crear_captcha()

    error_messages = {
        "invalid_login": (
            "Las credenciales ingresadas no son válidas. "
            "Verifica tu usuario y contraseña."
        ),
        "inactive": "Esta cuenta se encuentra desactivada.",
        "no_administrador": (
            "Acceso denegado. Esta cuenta no cuenta con permisos "
            "administrativos."
        ),
    }

    def confirm_login_allowed(self, user):
        super().confirm_login_allowed(user)
        if not (user.is_staff or user.is_superuser):
            raise ValidationError(
                self.error_messages["no_administrador"],
                code="no_administrador",
            )
