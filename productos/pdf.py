import textwrap
from datetime import datetime

from core.patrones.singleton import ConfiguracionSistema


def _escapar_pdf(texto):
    if texto is None:
        return ""

    cadena = str(texto)

    # Codificar en latin-1 compatible con Type1 Helvetica
    cadena_latin = cadena.encode(
        "latin-1",
        errors="replace"
    ).decode("latin-1")

    return (
        cadena_latin
        .replace("\\", "\\\\")
        .replace("(", "\\(")
        .replace(")", "\\)")
    )


def _dividir_lineas(texto, ancho=82):
    if not texto:
        return ["No especificada"]

    resultado = []

    for parrafo in str(texto).splitlines():
        limpio = parrafo.strip()
        if not limpio:
            resultado.append("")
            continue

        envuelto = textwrap.wrap(
            limpio,
            width=ancho,
            break_long_words=True,
            replace_whitespace=False
        )
        resultado.extend(envuelto or [""])

    return resultado or ["No especificada"]


def generar_ficha_tecnica_pdf(producto):
    """
    Genera un documento PDF (estándar PDF 1.4) con la
    ficha técnica institucional del producto.
    """
    config = ConfiguracionSistema()

    nombre_categoria = (
        producto.categoria.nombre
        if getattr(producto, "categoria", None)
        else "General"
    )

    marca = producto.marca or "No especificada"
    modelo = producto.modelo or "No especificado"
    precio_texto = f"${producto.precio:,.2f} {config.moneda}"
    estatus = producto.estatus
    fecha_emision = datetime.now().strftime("%d/%m/%Y %H:%M")

    comandos = []

    # Encabezado institucional con fondo azul marino ParNet (#063b7b)
    comandos.append("0.024 0.231 0.482 rg")
    comandos.append("45 735 522 65 re f")

    # Linea decorativa amarilla (#ffee00)
    comandos.append("1 0.933 0 rg")
    comandos.append("45 732 522 3 re f")

    # Titulo del encabezado en blanco
    comandos.append("1 1 1 rg")
    comandos.append("BT /F2 18 Tf 60 773 Td")
    comandos.append(
        f"({_escapar_pdf(config.nombre_empresa.upper())} - FICHA TECNICA) Tj ET"
    )

    comandos.append("BT /F1 10 Tf 60 750 Td")
    comandos.append(
        f"({_escapar_pdf(config.descripcion)} | Fecha: {fecha_emision}) Tj ET"
    )

    # Nombre principal del producto
    comandos.append("0.024 0.231 0.482 rg")
    comandos.append("BT /F2 15 Tf 45 702 Td")
    comandos.append(
        f"({_escapar_pdf(producto.nombre)}) Tj ET"
    )

    # Caja de especificaciones generales
    comandos.append("0.94 0.97 0.99 rg")
    comandos.append("45 555 522 132 re f")
    comandos.append("0.259 0.596 0.773 RG 1 w")
    comandos.append("45 555 522 132 re S")

    datos_tabla = [
        ("Codigo del producto:", producto.codigo),
        ("Categoria:", nombre_categoria),
        ("Marca:", marca),
        ("Modelo:", modelo),
        ("Precio unitario:", precio_texto),
        ("Existencias / Estatus:", f"{producto.stock} unidades ({estatus})"),
    ]

    y_actual = 668
    for etiqueta, valor in datos_tabla:
        comandos.append("0.024 0.231 0.482 rg")
        comandos.append(f"BT /F2 10 Tf 60 {y_actual} Td")
        comandos.append(f"({_escapar_pdf(etiqueta)}) Tj ET")

        comandos.append("0.1 0.1 0.1 rg")
        comandos.append(f"BT /F1 10 Tf 210 {y_actual} Td")
        comandos.append(f"({_escapar_pdf(valor)}) Tj ET")

        y_actual -= 19

    # Seccion: Descripcion del producto
    y_actual = 525
    comandos.append("0.024 0.231 0.482 rg")
    comandos.append(f"BT /F2 12 Tf 45 {y_actual} Td")
    comandos.append("(DESCRIPCION GENERAL) Tj ET")

    comandos.append("0.259 0.596 0.773 RG 1 w")
    comandos.append(f"45 {y_actual - 5} m 567 {y_actual - 5} l S")

    y_actual -= 22
    comandos.append("0.1 0.1 0.1 rg")

    lineas_descripcion = _dividir_lineas(
        producto.descripcion or "Sin descripcion registrada.",
        ancho=82
    )[:10]

    for linea in lineas_descripcion:
        comandos.append(f"BT /F1 10 Tf 45 {y_actual} Td")
        comandos.append(f"({_escapar_pdf(linea)}) Tj ET")
        y_actual -= 15

    # Seccion: Especificaciones de Ficha Tecnica
    y_actual -= 15
    comandos.append("0.024 0.231 0.482 rg")
    comandos.append(f"BT /F2 12 Tf 45 {y_actual} Td")
    comandos.append("(ESPECIFICACIONES TECNICAS) Tj ET")

    comandos.append("0.259 0.596 0.773 RG 1 w")
    comandos.append(f"45 {y_actual - 5} m 567 {y_actual - 5} l S")

    y_actual -= 22
    comandos.append("0.1 0.1 0.1 rg")

    lineas_ficha = _dividir_lineas(
        producto.ficha_tecnica
        or "Ficha tecnica estandar de catalogo industrial.",
        ancho=82
    )[:18]

    for linea in lineas_ficha:
        if y_actual < 75:
            break
        comandos.append(f"BT /F1 10 Tf 45 {y_actual} Td")
        comandos.append(f"({_escapar_pdf(linea)}) Tj ET")
        y_actual -= 15

    # Pie de pagina institucional
    comandos.append("0.259 0.596 0.773 RG 0.8 w")
    comandos.append("45 55 m 567 55 l S")

    comandos.append("0.35 0.35 0.35 rg")
    comandos.append("BT /F1 9 Tf 45 40 Td")
    comandos.append(
        f"({_escapar_pdf(config.nombre_empresa)} | "
        f"Contacto: {_escapar_pdf(config.correo_contacto)} | "
        f"Documento informativo de catalogo) Tj ET"
    )

    contenido_stream = "\n".join(comandos).encode("latin-1")

    objetos = [
        b"1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n",
        b"2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n",
        (
            b"3 0 obj\n<< /Type /Page /Parent 2 0 R "
            b"/MediaBox [0 0 612 842] "
            b"/Resources << /Font << /F1 4 0 R /F2 5 0 R >> >> "
            b"/Contents 6 0 R >>\nendobj\n"
        ),
        (
            b"4 0 obj\n<< /Type /Font /Subtype /Type1 "
            b"/BaseFont /Helvetica /Encoding /WinAnsiEncoding >>\nendobj\n"
        ),
        (
            b"5 0 obj\n<< /Type /Font /Subtype /Type1 "
            b"/BaseFont /Helvetica-Bold /Encoding /WinAnsiEncoding >>\nendobj\n"
        ),
        (
            f"6 0 obj\n<< /Length {len(contenido_stream)} >>\nstream\n"
            .encode("latin-1")
            + contenido_stream
            + b"\nendstream\nendobj\n"
        ),
    ]

    pdf = bytearray(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")
    posiciones = []

    for obj in objetos:
        posiciones.append(len(pdf))
        pdf.extend(obj)

    inicio_xref = len(pdf)
    total_objs = len(objetos) + 1

    pdf.extend(f"xref\n0 {total_objs}\n".encode("latin-1"))
    pdf.extend(b"0000000000 65535 f \n")

    for pos in posiciones:
        pdf.extend(f"{pos:010d} 00000 n \n".encode("latin-1"))

    pdf.extend(
        (
            f"trailer\n<< /Size {total_objs} /Root 1 0 R >>\n"
            f"startxref\n{inicio_xref}\n%%EOF\n"
        ).encode("latin-1")
    )

    return bytes(pdf)
