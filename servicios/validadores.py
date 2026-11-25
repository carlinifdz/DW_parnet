import re
from django.core.exceptions import ValidationError

# =========================================
# VALIDAR NOMBRE DEL SOLICITANTE
# =========================================

def validar_nombre(nombre):

    nombre = " ".join(nombre.split())

    if len(nombre) < 3:

        raise ValidationError(
            "El nombre debe contener al menos "
            "3 caracteres."
        )

    caracteres_permitidos = " -'’."

    for caracter in nombre:

        if (
            not caracter.isalpha()
            and caracter not in caracteres_permitidos
        ):

            raise ValidationError(
                "El nombre solamente puede contener "
                "letras, espacios, puntos, guiones "
                "y apóstrofes."
            )

    cantidad_letras = sum(
        caracter.isalpha()
        for caracter in nombre
    )

    if cantidad_letras < 2:

        raise ValidationError(
            "Ingresa un nombre válido."
        )

    return nombre

# =========================================
# VALIDAR NUMERO TELEFONICO
# =========================================

def validar_telefono(telefono):

    telefono = telefono.strip()

    if not telefono:
        return telefono

    # Permitir formatos nacionales e internacionales

    patron = r"\+?[0-9()\s\-]+"

    if not re.fullmatch(patron, telefono):

        raise ValidationError(
            "Ingresa un número telefónico válido."
        )

    digitos = re.sub(
        r"[^0-9]",
        "",
        telefono
    )

    if not 7 <= len(digitos) <= 15:

        raise ValidationError(
            "El teléfono debe contener entre "
            "7 y 15 dígitos."
        )

    return telefono

# =========================================
# VALIDAR DETALLE DE LA SOLICITUD
# =========================================

def validar_detalle(detalle):

    detalle = detalle.strip()

    if len(detalle) < 10:

        raise ValidationError(
            "Describe el servicio que necesitas "
            "con al menos 10 caracteres."
        )

    if len(detalle) > 2000:

        raise ValidationError(
            "El detalle no puede superar "
            "los 2000 caracteres."
        )

    return detalle