from datetime import datetime
from io import BytesIO
from xml.sax.saxutils import escape
import zipfile

from core.patrones.singleton import ConfiguracionSistema


# =========================================
# UTILIDADES PARA GENERACION DE PDF (%PDF-1.4)
# =========================================

def _escapar_pdf(texto):
    if texto is None:
        return ""

    cadena = str(texto)

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


def _recortar(texto, maximo):
    cadena = str(texto or "").strip()
    if len(cadena) <= maximo:
        return cadena
    return cadena[: max(1, maximo - 3)] + "..."


def _construir_pdf_multipagina(titulo_reporte, subtitulo, encabezados, filas):
    """
    Construye un documento PDF 1.4 multipágina con encabezado institucional
    de ParNet Ingeniería y tabla estructurada.
    """
    config = ConfiguracionSistema()
    fecha_emision = datetime.now().strftime("%d/%m/%Y %H:%M")

    filas_por_pagina = 22
    bloques = [
        filas[i: i + filas_por_pagina]
        for i in range(0, len(filas), filas_por_pagina)
    ] or [[]]

    streams_paginas = []
    total_paginas = len(bloques)

    for indice_pagina, bloque_filas in enumerate(bloques, start=1):
        comandos = []

        # Encabezado azul marino ParNet (#063b7b)
        comandos.append("0.024 0.231 0.482 rg")
        comandos.append("36 742 540 62 re f")

        # Barra amarilla inferior (#ffee00)
        comandos.append("1 0.933 0 rg")
        comandos.append("36 739 540 3 re f")

        # Titulo del reporte
        comandos.append("1 1 1 rg")
        comandos.append("BT /F2 15 Tf 48 778 Td")
        comandos.append(
            f"({_escapar_pdf(config.nombre_empresa.upper())} - {_escapar_pdf(titulo_reporte)}) Tj ET"
        )

        comandos.append("BT /F1 9 Tf 48 756 Td")
        comandos.append(
            f"({_escapar_pdf(subtitulo)} | Emision: {fecha_emision} | Pagina {indice_pagina} de {total_paginas}) Tj ET"
        )

        # Cabecera de la tabla
        y_tabla = 710
        comandos.append("0.035 0.388 0.553 rg")
        comandos.append(f"36 {y_tabla - 6} 540 22 re f")

        comandos.append("1 0.933 0 rg")
        for x_col, texto_col in encabezados:
            comandos.append(f"BT /F2 9 Tf {x_col} {y_tabla} Td")
            comandos.append(f"({_escapar_pdf(texto_col)}) Tj ET")

        y_fila = y_tabla - 24

        if not bloque_filas:
            comandos.append("0.15 0.15 0.15 rg")
            comandos.append(f"BT /F1 10 Tf 48 {y_fila} Td")
            comandos.append("(No existen registros disponibles para este reporte.) Tj ET")
        else:
            for idx_fila, celdas in enumerate(bloque_filas):
                if idx_fila % 2 == 0:
                    comandos.append("0.945 0.973 0.992 rg")
                    comandos.append(f"36 {y_fila - 6} 540 20 re f")

                comandos.append("0.1 0.1 0.1 rg")
                for (x_col, _), valor_celda in zip(encabezados, celdas):
                    comandos.append(f"BT /F1 8.5 Tf {x_col} {y_fila} Td")
                    comandos.append(f"({_escapar_pdf(valor_celda)}) Tj ET")

                comandos.append("0.78 0.87 0.93 RG 0.5 w")
                comandos.append(f"36 {y_fila - 6} m 576 {y_fila - 6} l S")

                y_fila -= 22

        # Pie de pagina
        comandos.append("0.259 0.596 0.773 RG 0.8 w")
        comandos.append("36 52 m 576 52 l S")

        comandos.append("0.35 0.35 0.35 rg")
        comandos.append("BT /F1 8.5 Tf 36 38 Td")
        comandos.append(
            f"({_escapar_pdf(config.nombre_empresa)} | Total de registros: {len(filas)}) Tj ET"
        )

        streams_paginas.append("\n".join(comandos).encode("latin-1"))

    # Ensamblar objetos PDF
    # 1: Catalog, 2: Pages, 3: Font Helvetica, 4: Font Helvetica-Bold
    # Luego por cada pagina: Page object y Content stream object
    objetos = []
    ids_paginas = []

    proximo_id = 5
    for _ in streams_paginas:
        ids_paginas.append(proximo_id)
        proximo_id += 2

    kids_ref = " ".join(f"{pid} 0 R" for pid in ids_paginas)

    objetos.append(b"1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n")
    objetos.append(
        f"2 0 obj\n<< /Type /Pages /Kids [{kids_ref}] /Count {len(ids_paginas)} >>\nendobj\n"
        .encode("latin-1")
    )
    objetos.append(
        b"3 0 obj\n<< /Type /Font /Subtype /Type1 "
        b"/BaseFont /Helvetica /Encoding /WinAnsiEncoding >>\nendobj\n"
    )
    objetos.append(
        b"4 0 obj\n<< /Type /Font /Subtype /Type1 "
        b"/BaseFont /Helvetica-Bold /Encoding /WinAnsiEncoding >>\nendobj\n"
    )

    id_actual = 5
    for stream in streams_paginas:
        id_pagina = id_actual
        id_contenido = id_actual + 1
        id_actual += 2

        obj_pagina = (
            f"{id_pagina} 0 obj\n<< /Type /Page /Parent 2 0 R "
            f"/MediaBox [0 0 612 842] "
            f"/Resources << /Font << /F1 3 0 R /F2 4 0 R >> >> "
            f"/Contents {id_contenido} 0 R >>\nendobj\n"
        ).encode("latin-1")

        obj_contenido = (
            f"{id_contenido} 0 obj\n<< /Length {len(stream)} >>\nstream\n"
            .encode("latin-1")
            + stream
            + b"\nendstream\nendobj\n"
        )

        objetos.append(obj_pagina)
        objetos.append(obj_contenido)

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


# =========================================
# UTILIDADES PARA GENERACION DE EXCEL (.XLSX)
# =========================================

def _columna_excel(indice):
    """
    Convierte un índice base 1 a letra de columna Excel (1 -> A, 2 -> B, ...).
    """
    letras = ""
    while indice > 0:
        indice, resto = divmod(indice - 1, 26)
        letras = chr(65 + resto) + letras
    return letras


def _construir_xlsx(nombre_hoja, encabezados, filas):
    """
    Construye un archivo Excel OpenXML (.xlsx) válido en memoria
    sin depender de librerías externas compiladas.
    """
    todas_las_filas = [encabezados, *filas]
    xml_filas = []

    for idx_fila, fila in enumerate(todas_las_filas, start=1):
        celdas_xml = []
        estilo = "1" if idx_fila == 1 else "0"

        for idx_col, valor in enumerate(fila, start=1):
            ref_celda = f"{_columna_excel(idx_col)}{idx_fila}"

            if isinstance(valor, (int, float)) and not isinstance(valor, bool):
                celdas_xml.append(
                    f'<c r="{ref_celda}" s="{estilo}"><v>{valor}</v></c>'
                )
            else:
                texto_limpio = escape(str(valor if valor is not None else ""))
                celdas_xml.append(
                    f'<c r="{ref_celda}" s="{estilo}" t="inlineStr">'
                    f'<is><t>{texto_limpio}</t></is></c>'
                )

        xml_filas.append(
            f'<row r="{idx_fila}">{"".join(celdas_xml)}</row>'
        )

    sheet_xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
        f'<sheetData>{"".join(xml_filas)}</sheetData>'
        '</worksheet>'
    )

    nombre_hoja_limpio = escape(nombre_hoja[:31] or "Reporte")

    workbook_xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" '
        'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">'
        '<sheets>'
        f'<sheet name="{nombre_hoja_limpio}" sheetId="1" r:id="rId1"/>'
        '</sheets>'
        '</workbook>'
    )

    styles_xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<styleSheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
        '<fonts count="2">'
        '<font><sz val="11"/><name val="Calibri"/></font>'
        '<font><b/><sz val="11"/><color rgb="FFFFFFFF"/><name val="Calibri"/></font>'
        '</fonts>'
        '<fills count="3">'
        '<fill><patternFill patternType="none"/></fill>'
        '<fill><patternFill patternType="gray125"/></fill>'
        '<fill><patternFill patternType="solid"><fgColor rgb="FF063B7B"/></patternFill></fill>'
        '</fills>'
        '<borders count="1"><border><left/><right/><top/><bottom/><diagonal/></border></borders>'
        '<cellStyleXfs count="1"><xf numFmtId="0" fontId="0" fillId="0" borderId="0"/></cellStyleXfs>'
        '<cellXfs count="2">'
        '<xf numFmtId="0" fontId="0" fillId="0" borderId="0" xfId="0"/>'
        '<xf numFmtId="0" fontId="1" fillId="2" borderId="0" xfId="0" applyFont="1" applyFill="1"/>'
        '</cellXfs>'
        '</styleSheet>'
    )

    content_types_xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
        '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
        '<Default Extension="xml" ContentType="application/xml"/>'
        '<Override PartName="/xl/workbook.xml" '
        'ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>'
        '<Override PartName="/xl/worksheets/sheet1.xml" '
        'ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>'
        '<Override PartName="/xl/styles.xml" '
        'ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.styles+xml"/>'
        '</Types>'
    )

    root_rels_xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        '<Relationship Id="rId1" '
        'Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" '
        'Target="xl/workbook.xml"/>'
        '</Relationships>'
    )

    workbook_rels_xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        '<Relationship Id="rId1" '
        'Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" '
        'Target="worksheets/sheet1.xml"/>'
        '<Relationship Id="rId2" '
        'Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" '
        'Target="styles.xml"/>'
        '</Relationships>'
    )

    buffer = BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as archivo_zip:
        archivo_zip.writestr("[Content_Types].xml", content_types_xml)
        archivo_zip.writestr("_rels/.rels", root_rels_xml)
        archivo_zip.writestr("xl/workbook.xml", workbook_xml)
        archivo_zip.writestr("xl/_rels/workbook.xml.rels", workbook_rels_xml)
        archivo_zip.writestr("xl/styles.xml", styles_xml)
        archivo_zip.writestr("xl/worksheets/sheet1.xml", sheet_xml)

    return buffer.getvalue()


# =========================================
# EXPORTACION DE REPORTE DE INVENTARIO (10.3)
# =========================================

def generar_inventario_pdf(productos):
    encabezados = [
        (42, "CODIGO"),
        (110, "PRODUCTO"),
        (255, "CATEGORIA"),
        (365, "MARCA"),
        (435, "PRECIO"),
        (495, "STOCK"),
        (530, "ESTATUS"),
    ]

    filas = []
    for prod in productos:
        nombre_cat = (
            prod.categoria.nombre
            if getattr(prod, "categoria", None)
            else "Sin categoria"
        )
        filas.append([
            _recortar(prod.codigo, 11),
            _recortar(prod.nombre, 26),
            _recortar(nombre_cat, 19),
            _recortar(prod.marca or "-", 12),
            f"${float(prod.precio):,.2f}",
            str(prod.stock),
            prod.estatus,
        ])

    return _construir_pdf_multipagina(
        titulo_reporte="REPORTE DE INVENTARIO",
        subtitulo="Clasificacion general de existencias de productos",
        encabezados=encabezados,
        filas=filas,
    )


def generar_inventario_excel(productos):
    encabezados = [
        "ID",
        "Código",
        "Producto",
        "Categoría",
        "Marca",
        "Modelo",
        "Precio (MXN)",
        "Stock",
        "Estatus",
        "Activo",
    ]

    filas = []
    for prod in productos:
        nombre_cat = (
            prod.categoria.nombre
            if getattr(prod, "categoria", None)
            else "Sin categoría"
        )
        filas.append([
            prod.id_producto,
            prod.codigo,
            prod.nombre,
            nombre_cat,
            prod.marca or "",
            prod.modelo or "",
            float(prod.precio),
            int(prod.stock),
            prod.estatus,
            "Sí" if prod.activo else "No",
        ])

    return _construir_xlsx(
        nombre_hoja="Inventario",
        encabezados=encabezados,
        filas=filas,
    )


# =========================================
# EXPORTACION DE SUGERENCIAS A EXCEL Y PDF (10.4, 10.5)
# =========================================

def generar_sugerencias_excel(sugerencias):
    encabezados = [
        "ID",
        "Nombre",
        "Correo Electrónico",
        "Mensaje / Sugerencia",
        "Estado",
        "Fecha de Registro",
    ]

    filas = []
    for sug in sugerencias:
        fecha_txt = (
            sug.fecha_registro.strftime("%d/%m/%Y %H:%M")
            if getattr(sug, "fecha_registro", None)
            else ""
        )
        filas.append([
            sug.id_sugerencia,
            sug.nombre,
            sug.correo,
            sug.mensaje,
            "Leída" if sug.leida else "No leída",
            fecha_txt,
        ])

    return _construir_xlsx(
        nombre_hoja="Sugerencias",
        encabezados=encabezados,
        filas=filas,
    )


def generar_sugerencias_pdf(sugerencias):
    encabezados = [
        (42, "ID"),
        (72, "NOMBRE"),
        (185, "CORREO"),
        (310, "MENSAJE"),
        (475, "ESTADO"),
        (525, "FECHA"),
    ]

    filas = []
    for sug in sugerencias:
        fecha_txt = (
            sug.fecha_registro.strftime("%d/%m/%Y")
            if getattr(sug, "fecha_registro", None)
            else "-"
        )
        filas.append([
            str(sug.id_sugerencia),
            _recortar(sug.nombre, 20),
            _recortar(sug.correo, 22),
            _recortar(sug.mensaje, 30),
            "Leida" if sug.leida else "Pendiente",
            fecha_txt,
        ])

    return _construir_pdf_multipagina(
        titulo_reporte="REPORTE DE SUGERENCIAS",
        subtitulo="Listado de sugerencias y comentarios recibidos",
        encabezados=encabezados,
        filas=filas,
    )
