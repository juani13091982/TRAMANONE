"""
AGM Performance - Ficha de Service Premium
Generador de PDF de nivel MotoGP
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm, mm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor, Color
from reportlab.platypus.flowables import Flowable
import os

# ─── PALETA DE COLORES ─────────────────────────────────────────────────────────
C_BLACK      = HexColor('#0A0A0A')
C_DARK       = HexColor('#111111')
C_DARKGRAY   = HexColor('#1C1C1C')
C_MIDGRAY    = HexColor('#2A2A2A')
C_GRAY       = HexColor('#3A3A3A')
C_LIGHTGRAY  = HexColor('#888888')
C_SILVER     = HexColor('#C0C0C0')
C_WHITE      = HexColor('#FFFFFF')
C_RED        = HexColor('#CC0000')
C_RED_DARK   = HexColor('#8B0000')
C_RED_LIGHT  = HexColor('#FF2222')
C_GOLD       = HexColor('#D4AF37')
C_ORANGE     = HexColor('#FF6600')

PAGE_W, PAGE_H = A4

# ─── CLASE DE CANVAS PERSONALIZADO ─────────────────────────────────────────────
class ServiceFormCanvas(canvas.Canvas):
    def __init__(self, filename, **kw):
        super().__init__(filename, **kw)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_background()
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_page_background(self):
        w, h = PAGE_W, PAGE_H

        # Fondo negro total
        self.setFillColor(C_BLACK)
        self.rect(0, 0, w, h, fill=1, stroke=0)

        # Línea lateral izquierda (roja)
        self.setFillColor(C_RED)
        self.rect(0, 0, 4*mm, h, fill=1, stroke=0)

        # Línea lateral derecha (roja)
        self.rect(w - 4*mm, 0, 4*mm, h, fill=1, stroke=0)

        # Banda superior degradada simulada
        self.setFillColor(C_DARKGRAY)
        self.rect(4*mm, h - 38*mm, w - 8*mm, 38*mm, fill=1, stroke=0)

        # Línea roja separadora del header
        self.setFillColor(C_RED)
        self.rect(4*mm, h - 39*mm, w - 8*mm, 1.5*mm, fill=1, stroke=0)

        # Línea dorada bajo la roja
        self.setFillColor(C_GOLD)
        self.rect(4*mm, h - 40.5*mm, w - 8*mm, 0.6*mm, fill=1, stroke=0)

        # Footer
        self.setFillColor(C_DARKGRAY)
        self.rect(4*mm, 0, w - 8*mm, 12*mm, fill=1, stroke=0)

        self.setFillColor(C_RED)
        self.rect(4*mm, 12*mm, w - 8*mm, 0.8*mm, fill=1, stroke=0)

        # Texto footer
        self.setFillColor(C_LIGHTGRAY)
        self.setFont('Helvetica', 7)
        self.drawCentredString(w/2, 4.5*mm,
            'AGM PERFORMANCE SERVICE CHIPTUNNING  |  Documento confidencial — uso interno del taller')
        self.setFillColor(C_RED)
        self.drawRightString(w - 8*mm, 4.5*mm, '▶')
        self.drawString(8*mm, 4.5*mm, '◀')

        # Marca de agua diagonal tenue
        self.saveState()
        self.setFillColor(HexColor('#1A1A1A'))
        self.setFont('Helvetica-Bold', 55)
        self.translate(w/2, h/2)
        self.rotate(45)
        self.drawCentredString(0, 0, 'AGM PERFORMANCE')
        self.restoreState()


def draw_section_header(elements, title, subtitle=None):
    """Encabezado de sección con estilo racing."""
    data = [[Paragraph(
        f'<font color="#CC0000">▌</font> <font color="#FFFFFF"><b>{title}</b></font>'
        + (f'  <font color="#888888" size="8">{subtitle}</font>' if subtitle else ''),
        ParagraphStyle('sh', fontName='Helvetica-Bold', fontSize=10,
                       textColor=C_WHITE, leading=14, spaceAfter=0)
    )]]
    t = Table(data, colWidths=[PAGE_W - 8*mm - 2*cm])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), C_MIDGRAY),
        ('TOPPADDING',    (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING',   (0,0), (-1,-1), 8),
        ('LINEABOVE',  (0,0), (-1,0), 2, C_RED),
        ('LINEBELOW',  (0,0), (-1,-1), 0.5, C_GOLD),
    ]))
    elements.append(t)
    elements.append(Spacer(1, 2*mm))


def field_row(label, width=None, double=False):
    """Genera una fila de campo."""
    line = '─' * 28
    return f'<font color="#888888" size="8">{label}</font><br/>' \
           f'<font color="#333333" size="7">{line}</font>'


def checkbox_cell(text):
    return Paragraph(
        f'<font color="#CC0000">◻</font> <font color="#CCCCCC" size="8">{text}</font>',
        ParagraphStyle('cb', fontName='Helvetica', fontSize=8,
                       textColor=C_WHITE, leading=11)
    )


def status_checkboxes():
    return [
        Paragraph('<font color="#22AA44">◻</font> <font color="#CCCCCC" size="7.5">BUENO</font>  '
                  '<font color="#FFAA00">◻</font> <font color="#CCCCCC" size="7.5">REGULAR</font>  '
                  '<font color="#CC0000">◻</font> <font color="#CCCCCC" size="7.5">CAMBIAR</font>',
                  ParagraphStyle('sc', fontName='Helvetica', fontSize=7.5,
                                 textColor=C_WHITE, leading=10))
    ]


def label_style(size=8):
    return ParagraphStyle('lbl', fontName='Helvetica-Bold', fontSize=size,
                          textColor=HexColor('#AAAAAA'), leading=11, spaceAfter=1)

def value_style(size=9):
    return ParagraphStyle('val', fontName='Helvetica', fontSize=size,
                          textColor=C_WHITE, leading=12)

def make_field(label, lines=1):
    underline = '\n' + ('─' * 35)
    content = (label + '\n') + ('_' * 40 + '\n') * lines
    return Paragraph(
        f'<font color="#999999" size="7.5">{label}</font><br/>'
        f'<font color="#333333" size="8">{"─" * 38}</font>',
        ParagraphStyle('fld', fontName='Helvetica', fontSize=8.5,
                       textColor=C_WHITE, leading=13, spaceAfter=2)
    )


def generate_pdf(output_path='AGM_Ficha_Service_PREMIUM.pdf'):
    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        leftMargin=1.2*cm,
        rightMargin=1.2*cm,
        topMargin=4.2*cm,
        bottomMargin=1.8*cm,
    )

    styles = getSampleStyleSheet()
    elements = []

    col_w = (PAGE_W - 8*mm - 2.4*cm) / 2
    col3_w = (PAGE_W - 8*mm - 2.4*cm) / 3

    # ── ENCABEZADO (dibujado en background) ─────────────────────────
    # El logo y título van en el canvas de fondo via draw_header_overlay
    # Agregamos espacio para el header del canvas
    elements.append(Spacer(1, 2*mm))

    # ── DATOS DE ORDEN ───────────────────────────────────────────────
    orden_data = [
        [
            Paragraph('<font color="#999999" size="7.5">N° DE ORDEN</font><br/>'
                      '<font color="#FF2222" size="18"><b>__________</b></font>',
                      ParagraphStyle('ord', fontName='Helvetica-Bold', fontSize=9,
                                     textColor=C_WHITE, leading=22)),
            Paragraph('<font color="#999999" size="7.5">FECHA DE INGRESO</font><br/>'
                      '<font color="#FFFFFF" size="10"><b>___ / ___ / ______</b></font>',
                      ParagraphStyle('dt', fontName='Helvetica', fontSize=9,
                                     textColor=C_WHITE, leading=14)),
            Paragraph('<font color="#999999" size="7.5">HORA DE INGRESO</font><br/>'
                      '<font color="#FFFFFF" size="10"><b>_____ : _____</b></font>',
                      ParagraphStyle('hr', fontName='Helvetica', fontSize=9,
                                     textColor=C_WHITE, leading=14)),
            Paragraph('<font color="#999999" size="7.5">FECHA ESTIMADA ENTREGA</font><br/>'
                      '<font color="#FFFFFF" size="10"><b>___ / ___ / ______</b></font>',
                      ParagraphStyle('fe', fontName='Helvetica', fontSize=9,
                                     textColor=C_WHITE, leading=14)),
        ]
    ]
    t_orden = Table(orden_data, colWidths=[col_w*0.6, col_w*0.7, col_w*0.55, col_w*0.8])
    t_orden.setStyle(TableStyle([
        ('BACKGROUND',    (0,0), (-1,-1), C_DARKGRAY),
        ('LINEABOVE',     (0,0), (-1,0), 2, C_RED),
        ('LINEBELOW',     (0,0), (-1,-1), 2, C_RED),
        ('LEFTPADDING',   (0,0), (-1,-1), 8),
        ('RIGHTPADDING',  (0,0), (-1,-1), 8),
        ('TOPPADDING',    (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('VALIGN',        (0,0), (-1,-1), 'MIDDLE'),
        ('GRID',          (0,0), (-1,-1), 0.3, C_GRAY),
    ]))
    elements.append(t_orden)
    elements.append(Spacer(1, 4*mm))

    # ── SECCIÓN 1: DATOS DEL CLIENTE ─────────────────────────────────
    draw_section_header(elements, 'DATOS DEL CLIENTE')

    cliente_data = [
        [make_field('NOMBRE Y APELLIDO'), make_field('D.N.I. / C.U.I.T.')],
        [make_field('TELÉFONO / CELULAR'), make_field('E-MAIL')],
        [make_field('DIRECCIÓN'), make_field('CIUDAD / LOCALIDAD')],
    ]
    t_cliente = Table(cliente_data, colWidths=[col_w + 5*mm, col_w - 5*mm])
    t_cliente.setStyle(TableStyle([
        ('BACKGROUND',    (0,0), (-1,-1), C_DARK),
        ('LEFTPADDING',   (0,0), (-1,-1), 8),
        ('RIGHTPADDING',  (0,0), (-1,-1), 8),
        ('TOPPADDING',    (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 7),
        ('GRID',          (0,0), (-1,-1), 0.3, C_GRAY),
        ('ROWBACKGROUNDS',(0,0), (-1,-1), [C_DARK, HexColor('#161616')]),
    ]))
    elements.append(t_cliente)
    elements.append(Spacer(1, 4*mm))

    # ── SECCIÓN 2: DATOS DE LA MOTOCICLETA ───────────────────────────
    draw_section_header(elements, 'DATOS DE LA MOTOCICLETA')

    moto_row1 = [
        make_field('MARCA'),
        make_field('MODELO'),
        make_field('AÑO'),
    ]
    moto_row2 = [
        make_field('DOMINIO / PATENTE'),
        make_field('KILOMETRAJE ACTUAL'),
        make_field('TIPO DE USO  (calle / ruta / pista)'),
    ]
    moto_row3 = [
        make_field('N° DE CHASIS / VIN'),
        make_field('N° DE MOTOR'),
        make_field('COLOR'),
    ]

    t_moto = Table(
        [moto_row1, moto_row2, moto_row3],
        colWidths=[col3_w, col3_w, col3_w]
    )
    t_moto.setStyle(TableStyle([
        ('BACKGROUND',    (0,0), (-1,-1), C_DARK),
        ('LEFTPADDING',   (0,0), (-1,-1), 8),
        ('RIGHTPADDING',  (0,0), (-1,-1), 8),
        ('TOPPADDING',    (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 7),
        ('GRID',          (0,0), (-1,-1), 0.3, C_GRAY),
        ('ROWBACKGROUNDS',(0,0), (-1,-1), [C_DARK, HexColor('#161616'), C_DARK]),
    ]))
    elements.append(t_moto)
    elements.append(Spacer(1, 4*mm))

    # ── SECCIÓN 3: TRABAJOS SOLICITADOS ──────────────────────────────
    draw_section_header(elements, 'TRABAJOS SOLICITADOS', '(marcar con ✓)')

    trabajos = [
        ['Service General', 'Cambio de Aceite Motor', 'Cambio de Filtro de Aceite'],
        ['Cambio de Filtro de Aire', 'Cambio de Bujías', 'Regulación de Válvulas'],
        ['Diagnóstico Electrónico', 'Reprogramación ECU / Mapa', 'Banco de Potencia (Dyno)'],
        ['Control y Ajuste de Frenos', 'Control de Transmisión', 'Control de Suspensiones'],
        ['Revisión Eléctrica', 'Lavado y Detailing', 'Otro (ver Observaciones)'],
    ]

    trab_rows = []
    for row in trabajos:
        trab_rows.append([checkbox_cell(t) for t in row])

    t_trabajos = Table(trab_rows, colWidths=[col3_w, col3_w, col3_w])
    t_trabajos.setStyle(TableStyle([
        ('BACKGROUND',    (0,0), (-1,-1), C_DARK),
        ('LEFTPADDING',   (0,0), (-1,-1), 10),
        ('RIGHTPADDING',  (0,0), (-1,-1), 8),
        ('TOPPADDING',    (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('GRID',          (0,0), (-1,-1), 0.3, C_GRAY),
        ('ROWBACKGROUNDS',(0,0), (-1,-1), [C_DARK, HexColor('#161616'),
                                            C_DARK, HexColor('#161616'), C_DARK]),
    ]))
    elements.append(t_trabajos)
    elements.append(Spacer(1, 4*mm))

    # ── SECCIÓN 4: INSPECCIÓN GENERAL ────────────────────────────────
    draw_section_header(elements, 'INSPECCIÓN TÉCNICA GENERAL', '(evaluación previa al service)')

    items_insp = [
        ('Aceite Motor', 'CAMBIAR'),
        ('Refrigerante / Líquido de Frenos', 'RELLENAR'),
        ('Pastillas de Freno Delanteras', 'CAMBIAR'),
        ('Pastillas de Freno Traseras', 'CAMBIAR'),
        ('Disco de Freno Delantero', 'REVISAR'),
        ('Disco de Freno Trasero', 'REVISAR'),
        ('Kit de Transmisión (cadena+piñones)', 'CAMBIAR'),
        ('Neumático Delantero', 'CAMBIAR'),
        ('Neumático Trasero', 'CAMBIAR'),
        ('Batería / Sistema de Carga', 'CAMBIAR'),
        ('Luces (delantera / trasera / giros)', 'REPARAR'),
        ('Suspensión Delantera (horquilla)', 'REVISAR'),
        ('Suspensión Trasera (amortiguador)', 'REVISAR'),
        ('Filtro de Combustible', 'CAMBIAR'),
        ('Sistema de Escape', 'REVISAR'),
    ]

    estado_header = Paragraph(
        '<font color="#CC0000" size="7.5"><b>◻</b></font> <font color="#22AA44" size="7.5"><b>BUENO</b></font>   '
        '<font color="#FFAA00" size="7.5">◻</font> <font color="#FFAA00" size="7.5"><b>REGULAR</b></font>   '
        '<font color="#CC0000" size="7.5">◻</font> <font color="#CC0000" size="7.5"><b>CAMBIAR/REP.</b></font>',
        ParagraphStyle('eh', fontName='Helvetica-Bold', fontSize=7.5,
                       textColor=C_WHITE, leading=10)
    )

    insp_header = [
        [
            Paragraph('<b><font color="#AAAAAA" size="8">COMPONENTE</font></b>',
                      ParagraphStyle('ih', fontName='Helvetica-Bold', fontSize=8,
                                     textColor=HexColor('#AAAAAA'), leading=10)),
            Paragraph('<b><font color="#AAAAAA" size="8">ESTADO</font></b>',
                      ParagraphStyle('ih2', fontName='Helvetica-Bold', fontSize=8,
                                     textColor=HexColor('#AAAAAA'), leading=10)),
            Paragraph('<b><font color="#AAAAAA" size="8">OBSERVACIÓN</font></b>',
                      ParagraphStyle('ih3', fontName='Helvetica-Bold', fontSize=8,
                                     textColor=HexColor('#AAAAAA'), leading=10)),
        ]
    ]

    insp_rows = insp_header[:]
    for i, (item, accion) in enumerate(items_insp):
        bg = C_DARK if i % 2 == 0 else HexColor('#161616')
        insp_rows.append([
            Paragraph(f'<font color="#DDDDDD" size="8">{item}</font>',
                      ParagraphStyle('ir', fontName='Helvetica', fontSize=8,
                                     textColor=C_WHITE, leading=10)),
            Paragraph(
                '<font color="#22AA44">◻</font> <font color="#BBBBBB" size="7.5">Bueno</font>  '
                '<font color="#FFAA00">◻</font> <font color="#BBBBBB" size="7.5">Regular</font>  '
                '<font color="#CC0000">◻</font> <font color="#BBBBBB" size="7.5">Cambiar</font>',
                ParagraphStyle('ck', fontName='Helvetica', fontSize=7.5,
                               textColor=C_WHITE, leading=10)),
            Paragraph(f'<font color="#444444" size="7">{"─" * 30}</font>',
                      ParagraphStyle('obs', fontName='Helvetica', fontSize=7,
                                     textColor=C_WHITE, leading=10)),
        ])

    col_insp_1 = col_w * 0.72
    col_insp_2 = col_w * 0.65
    col_insp_3 = (PAGE_W - 8*mm - 2.4*cm) - col_insp_1 - col_insp_2

    t_insp = Table(insp_rows, colWidths=[col_insp_1, col_insp_2, col_insp_3])
    row_styles = [
        ('BACKGROUND',    (0,0), (-1,0),   C_MIDGRAY),
        ('TEXTCOLOR',     (0,0), (-1,0),   C_GOLD),
        ('LEFTPADDING',   (0,0), (-1,-1),  8),
        ('RIGHTPADDING',  (0,0), (-1,-1),  6),
        ('TOPPADDING',    (0,0), (-1,-1),  4),
        ('BOTTOMPADDING', (0,0), (-1,-1),  4),
        ('GRID',          (0,0), (-1,-1),  0.3, C_GRAY),
        ('LINEBELOW',     (0,0), (-1,0),   1, C_RED),
    ]
    for i in range(1, len(insp_rows)):
        bg = C_DARK if i % 2 == 0 else HexColor('#161616')
        row_styles.append(('BACKGROUND', (0, i), (-1, i), bg))

    t_insp.setStyle(TableStyle(row_styles))
    elements.append(t_insp)
    elements.append(Spacer(1, 4*mm))

    # ── SECCIÓN 5: PERFORMANCE / REPROGRAMACIÓN ───────────────────────
    draw_section_header(elements, 'DIAGNÓSTICO PERFORMANCE & REPROGRAMACIÓN ECU')

    perf_row1 = [
        [
            Paragraph('<font color="#999999" size="7.5">ECU ORIGINAL LEÍDA</font>',
                      ParagraphStyle('pl', fontName='Helvetica', fontSize=7.5,
                                     textColor=HexColor('#999999'), leading=10)),
            Paragraph('<font color="#22AA44">◻</font> <font color="#CCCCCC" size="8"> SÍ</font>   '
                      '<font color="#CC0000">◻</font> <font color="#CCCCCC" size="8"> NO</font>',
                      ParagraphStyle('pv', fontName='Helvetica', fontSize=8,
                                     textColor=C_WHITE, leading=11)),
        ],
        [
            Paragraph('<font color="#999999" size="7.5">BACKUP REALIZADO</font>',
                      ParagraphStyle('pl2', fontName='Helvetica', fontSize=7.5,
                                     textColor=HexColor('#999999'), leading=10)),
            Paragraph('<font color="#22AA44">◻</font> <font color="#CCCCCC" size="8"> SÍ</font>   '
                      '<font color="#CC0000">◻</font> <font color="#CCCCCC" size="8"> NO</font>',
                      ParagraphStyle('pv2', fontName='Helvetica', fontSize=8,
                                     textColor=C_WHITE, leading=11)),
        ],
    ]

    # Tabla de performance en 2 columnas
    perf_data = [
        [
            Paragraph('<font color="#999999" size="7.5">ECU ORIGINAL LEÍDA</font><br/>'
                      '<font color="#22AA44">◻</font> <font color="#CCCCCC" size="9"> SÍ</font>   '
                      '<font color="#CC0000">◻</font> <font color="#CCCCCC" size="9"> NO</font>',
                      ParagraphStyle('pf1', fontName='Helvetica', fontSize=9,
                                     textColor=C_WHITE, leading=13)),
            Paragraph('<font color="#999999" size="7.5">BACKUP REALIZADO</font><br/>'
                      '<font color="#22AA44">◻</font> <font color="#CCCCCC" size="9"> SÍ</font>   '
                      '<font color="#CC0000">◻</font> <font color="#CCCCCC" size="9"> NO</font>',
                      ParagraphStyle('pf2', fontName='Helvetica', fontSize=9,
                                     textColor=C_WHITE, leading=13)),
            make_field('MAPA / CALIBRACIÓN APLICADA'),
        ],
        [
            Paragraph('<font color="#999999" size="7.5">POTENCIA ORIGINAL (Dyno)</font><br/>'
                      '<font color="#FFFFFF" size="9">____________  HP  /  ____________  Nm</font>',
                      ParagraphStyle('hp1', fontName='Helvetica', fontSize=9,
                                     textColor=C_WHITE, leading=13)),
            Paragraph('<font color="#999999" size="7.5">POTENCIA FINAL (Dyno)</font><br/>'
                      '<font color="#FF2222" size="11"><b>____________  HP  /  ____________  Nm</b></font>',
                      ParagraphStyle('hp2', fontName='Helvetica-Bold', fontSize=11,
                                     textColor=C_RED_LIGHT, leading=14)),
            Paragraph('<font color="#999999" size="7.5">GANANCIA PERFORMANCE</font><br/>'
                      '<font color="#D4AF37" size="13"><b>+ _________ HP</b></font>',
                      ParagraphStyle('hp3', fontName='Helvetica-Bold', fontSize=13,
                                     textColor=C_GOLD, leading=16)),
        ],
        [
            make_field('HERRAMIENTA / SOFTWARE UTILIZADO'),
            make_field('VERSIÓN FIRMWARE ECU'),
            make_field('TÉCNICO RESPONSABLE'),
        ],
    ]

    t_perf = Table(perf_data, colWidths=[col3_w, col3_w, col3_w])
    t_perf.setStyle(TableStyle([
        ('BACKGROUND',    (0,0), (-1,-1), C_DARK),
        ('LEFTPADDING',   (0,0), (-1,-1), 8),
        ('RIGHTPADDING',  (0,0), (-1,-1), 8),
        ('TOPPADDING',    (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('GRID',          (0,0), (-1,-1), 0.3, C_GRAY),
        ('ROWBACKGROUNDS',(0,0), (-1,-1), [C_DARK, HexColor('#161616'), C_DARK]),
        ('BACKGROUND',    (1,1), (1,1),   HexColor('#1A0000')),
        ('BACKGROUND',    (2,1), (2,1),   HexColor('#1A1500')),
    ]))
    elements.append(t_perf)
    elements.append(Spacer(1, 4*mm))

    # ── SECCIÓN 6: OBSERVACIONES TÉCNICAS ────────────────────────────
    draw_section_header(elements, 'OBSERVACIONES TÉCNICAS DEL MECÁNICO')

    obs_lines = ['<font color="#333333" size="8">' + '─' * 95 + '</font>'] * 4
    obs_content = '<br/>'.join(['<br/>'.join([''] + [line]) for line in obs_lines])

    obs_data = [[
        Paragraph(
            '<font color="#333333" size="8">' + ('─' * 95 + '<br/>' * 2) * 4 + '</font>',
            ParagraphStyle('obs2', fontName='Helvetica', fontSize=8,
                           textColor=C_WHITE, leading=18, spaceAfter=0)
        )
    ]]
    t_obs = Table(obs_data, colWidths=[PAGE_W - 8*mm - 2.4*cm])
    t_obs.setStyle(TableStyle([
        ('BACKGROUND',    (0,0), (-1,-1), C_DARK),
        ('LEFTPADDING',   (0,0), (-1,-1), 8),
        ('RIGHTPADDING',  (0,0), (-1,-1), 8),
        ('TOPPADDING',    (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LINEBELOW',     (0,0), (-1,-1), 0.5, C_GOLD),
    ]))
    elements.append(t_obs)
    elements.append(Spacer(1, 4*mm))

    # ── SECCIÓN 7: PRESUPUESTO ────────────────────────────────────────
    draw_section_header(elements, 'DETALLE DE TRABAJOS Y PRESUPUESTO')

    pres_header = ['N°', 'DESCRIPCIÓN DEL TRABAJO / REPUESTO', 'CANT.', 'P. UNIT.', 'TOTAL']
    pres_rows = [pres_header]
    for i in range(6):
        pres_rows.append([
            Paragraph(f'<font color="#666666" size="8">{i+1:02d}</font>',
                      ParagraphStyle('pn', fontName='Helvetica', fontSize=8,
                                     textColor=C_WHITE, leading=10)),
            Paragraph('<font color="#333333" size="8">' + '─' * 55 + '</font>',
                      ParagraphStyle('pd', fontName='Helvetica', fontSize=8,
                                     textColor=C_WHITE, leading=10)),
            Paragraph('<font color="#333333" size="8">─ ─ ─</font>',
                      ParagraphStyle('pc', fontName='Helvetica', fontSize=8,
                                     textColor=C_WHITE, leading=10)),
            Paragraph('<font color="#333333" size="8">$ ─────</font>',
                      ParagraphStyle('pu', fontName='Helvetica', fontSize=8,
                                     textColor=C_WHITE, leading=10)),
            Paragraph('<font color="#333333" size="8">$ ─────</font>',
                      ParagraphStyle('pt', fontName='Helvetica', fontSize=8,
                                     textColor=C_WHITE, leading=10)),
        ])

    # Totales
    pres_rows.append([
        '', '', '',
        Paragraph('<font color="#AAAAAA" size="8"><b>SUBTOTAL</b></font>',
                  ParagraphStyle('sub', fontName='Helvetica-Bold', fontSize=8,
                                 textColor=HexColor('#AAAAAA'), leading=10)),
        Paragraph('<font color="#FFFFFF" size="9"><b>$ ─────────</b></font>',
                  ParagraphStyle('subv', fontName='Helvetica-Bold', fontSize=9,
                                 textColor=C_WHITE, leading=11)),
    ])
    pres_rows.append([
        '', '', '',
        Paragraph('<font color="#D4AF37" size="9"><b>TOTAL A PAGAR</b></font>',
                  ParagraphStyle('tot', fontName='Helvetica-Bold', fontSize=9,
                                 textColor=C_GOLD, leading=11)),
        Paragraph('<font color="#FF2222" size="12"><b>$ ─────────</b></font>',
                  ParagraphStyle('totv', fontName='Helvetica-Bold', fontSize=12,
                                 textColor=C_RED_LIGHT, leading=14)),
    ])

    total_w = PAGE_W - 8*mm - 2.4*cm
    t_pres = Table(pres_rows,
                   colWidths=[total_w*0.05, total_w*0.50, total_w*0.10,
                               total_w*0.18, total_w*0.17])
    pres_styles = [
        ('BACKGROUND',    (0,0), (-1,0),   C_MIDGRAY),
        ('TEXTCOLOR',     (0,0), (-1,0),   C_GOLD),
        ('FONTNAME',      (0,0), (-1,0),   'Helvetica-Bold'),
        ('FONTSIZE',      (0,0), (-1,0),   8),
        ('ALIGN',         (0,0), (-1,0),   'CENTER'),
        ('LINEBELOW',     (0,0), (-1,0),   1, C_RED),
        ('LEFTPADDING',   (0,0), (-1,-1),  6),
        ('RIGHTPADDING',  (0,0), (-1,-1),  6),
        ('TOPPADDING',    (0,0), (-1,-1),  4),
        ('BOTTOMPADDING', (0,0), (-1,-1),  5),
        ('GRID',          (0,1), (-1,-3),  0.3, C_GRAY),
        ('BACKGROUND',    (0,-2), (-1,-2), C_DARKGRAY),
        ('BACKGROUND',    (0,-1), (-1,-1), HexColor('#1A0000')),
        ('LINEABOVE',     (0,-2), (-1,-2), 1, C_GOLD),
        ('LINEABOVE',     (0,-1), (-1,-1), 1.5, C_RED),
    ]
    for i in range(1, len(pres_rows) - 2):
        bg = C_DARK if i % 2 == 0 else HexColor('#161616')
        pres_styles.append(('BACKGROUND', (0, i), (-1, i), bg))

    t_pres.setStyle(TableStyle(pres_styles))
    elements.append(t_pres)
    elements.append(Spacer(1, 4*mm))

    # ── SECCIÓN 8: CONFORMIDAD / FIRMAS ──────────────────────────────
    draw_section_header(elements, 'CONFORMIDAD Y FIRMAS')

    firma_data = [[
        Paragraph(
            '<font color="#999999" size="7.5">FIRMA Y ACLARACIÓN DEL CLIENTE</font><br/><br/><br/>'
            '<font color="#CC0000" size="7.5">────────────────────────────────────────</font><br/>'
            '<font color="#666666" size="7">Acepto los trabajos realizados y el presupuesto</font>',
            ParagraphStyle('fc', fontName='Helvetica', fontSize=7.5,
                           textColor=C_WHITE, leading=11, alignment=TA_CENTER)
        ),
        Paragraph(
            '<font color="#999999" size="7.5">TÉCNICO RESPONSABLE — AGM PERFORMANCE</font><br/><br/><br/>'
            '<font color="#CC0000" size="7.5">────────────────────────────────────────</font><br/>'
            '<font color="#666666" size="7">Responsable del servicio prestado</font>',
            ParagraphStyle('ft', fontName='Helvetica', fontSize=7.5,
                           textColor=C_WHITE, leading=11, alignment=TA_CENTER)
        ),
        Paragraph(
            '<font color="#999999" size="7.5">SELLO DEL TALLER</font><br/><br/><br/><br/>'
            '<font color="#333333" size="7">□ □ □ □ □ □ □ □ □ □ □<br/>□ □ □ □ □ □ □ □ □ □ □</font>',
            ParagraphStyle('fs', fontName='Helvetica', fontSize=7.5,
                           textColor=C_WHITE, leading=11, alignment=TA_CENTER)
        ),
    ]]

    t_firma = Table(firma_data, colWidths=[col3_w, col3_w, col3_w])
    t_firma.setStyle(TableStyle([
        ('BACKGROUND',    (0,0), (-1,-1), C_DARK),
        ('LEFTPADDING',   (0,0), (-1,-1), 8),
        ('RIGHTPADDING',  (0,0), (-1,-1), 8),
        ('TOPPADDING',    (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 10),
        ('GRID',          (0,0), (-1,-1), 0.3, C_GRAY),
        ('ALIGN',         (0,0), (-1,-1), 'CENTER'),
        ('VALIGN',        (0,0), (-1,-1), 'BOTTOM'),
    ]))
    elements.append(t_firma)

    # ── GENERAR CON CANVAS PERSONALIZADO ─────────────────────────────
    doc.build(elements, canvasmaker=ServiceFormCanvas)
    print(f"✅ PDF generado: {output_path}")


# ── OVERLAY DEL HEADER (logo + título) ─────────────────────────────────────────
class HeaderOverlay(ServiceFormCanvas):
    """Canvas que además dibuja logo y texto del header."""

    LOGO_PATH = '/home/user/TRAMANONE/LOGO TRAMA.JPG.jpeg'

    def draw_page_background(self):
        super().draw_page_background()
        w, h = PAGE_W, PAGE_H

        # LOGO
        if os.path.exists(self.LOGO_PATH):
            logo_w = 38*mm
            logo_h = 28*mm
            self.drawImage(self.LOGO_PATH,
                           8*mm, h - 36*mm,
                           width=logo_w, height=logo_h,
                           preserveAspectRatio=True, mask='auto')

        # TÍTULO PRINCIPAL
        self.setFillColor(C_WHITE)
        self.setFont('Helvetica-Bold', 18)
        self.drawString(52*mm, h - 16*mm, 'AGM PERFORMANCE')

        self.setFillColor(C_RED)
        self.setFont('Helvetica-Bold', 10)
        self.drawString(52*mm, h - 23*mm, 'SERVICE  ·  CHIPTUNNING  ·  DIAGNÓSTICO')

        # Línea decorativa
        self.setFillColor(C_GOLD)
        self.rect(52*mm, h - 25.5*mm, 120*mm, 0.5*mm, fill=1, stroke=0)

        # Subtítulo formulario
        self.setFillColor(C_LIGHTGRAY)
        self.setFont('Helvetica', 8.5)
        self.drawString(52*mm, h - 30*mm,
                        'FICHA DE SERVICE Y DIAGNÓSTICO DE MOTOCICLETAS')

        # Número de versión / código QR placeholder
        self.setFillColor(C_GRAY)
        self.setFont('Helvetica', 7)
        self.drawRightString(w - 8*mm, h - 14*mm, 'FORM-SRV-001 · Rev.2025')
        self.drawRightString(w - 8*mm, h - 19*mm, 'www.agmperformance.com.ar')
        self.drawRightString(w - 8*mm, h - 24*mm, 'Tel: ___________________')

        # Marco del QR placeholder
        self.setStrokeColor(C_GRAY)
        self.setLineWidth(0.5)
        self.rect(w - 28*mm, h - 37*mm, 18*mm, 18*mm, fill=0, stroke=1)
        self.setFillColor(HexColor('#333333'))
        self.setFont('Helvetica', 5.5)
        self.drawCentredString(w - 19*mm, h - 30*mm, 'QR')
        self.drawCentredString(w - 19*mm, h - 33.5*mm, 'TALLER')


def generate_premium_pdf(output_path='AGM_Ficha_Service_PREMIUM.pdf'):
    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        leftMargin=1.2*cm,
        rightMargin=1.2*cm,
        topMargin=4.3*cm,
        bottomMargin=1.8*cm,
    )

    styles = getSampleStyleSheet()
    elements = []

    col_w = (PAGE_W - 8*mm - 2.4*cm) / 2
    col3_w = (PAGE_W - 8*mm - 2.4*cm) / 3

    elements.append(Spacer(1, 2*mm))

    # ── DATOS DE ORDEN ──────────────────────────────────────────────
    orden_data = [[
        Paragraph('<font color="#999999" size="7.5">N° DE ORDEN</font><br/>'
                  '<font color="#FF2222" size="20"><b>__________</b></font>',
                  ParagraphStyle('ord', fontName='Helvetica-Bold', fontSize=9,
                                 textColor=C_WHITE, leading=24)),
        Paragraph('<font color="#999999" size="7.5">FECHA DE INGRESO</font><br/>'
                  '<font color="#FFFFFF" size="11"><b>___ / ___ / ______</b></font>',
                  ParagraphStyle('dt', fontName='Helvetica', fontSize=9,
                                 textColor=C_WHITE, leading=14)),
        Paragraph('<font color="#999999" size="7.5">HORA</font><br/>'
                  '<font color="#FFFFFF" size="11"><b>_____ : _____</b></font>',
                  ParagraphStyle('hr', fontName='Helvetica', fontSize=9,
                                 textColor=C_WHITE, leading=14)),
        Paragraph('<font color="#999999" size="7.5">ENTREGA ESTIMADA</font><br/>'
                  '<font color="#FFFFFF" size="11"><b>___ / ___ / ______</b></font>',
                  ParagraphStyle('fe', fontName='Helvetica', fontSize=9,
                                 textColor=C_WHITE, leading=14)),
        Paragraph('<font color="#999999" size="7.5">PRIORIDAD</font><br/>'
                  '<font color="#D4AF37">◻</font> <font color="#CCCCCC" size="8">URGENTE</font><br/>'
                  '<font color="#22AA44">◻</font> <font color="#CCCCCC" size="8">NORMAL</font>',
                  ParagraphStyle('pr', fontName='Helvetica', fontSize=8,
                                 textColor=C_WHITE, leading=11)),
    ]]
    total_content_w = PAGE_W - 8*mm - 2.4*cm
    t_orden = Table(orden_data,
                    colWidths=[total_content_w*0.20, total_content_w*0.22,
                                total_content_w*0.16, total_content_w*0.26,
                                total_content_w*0.16])
    t_orden.setStyle(TableStyle([
        ('BACKGROUND',    (0,0), (-1,-1), C_DARKGRAY),
        ('LINEABOVE',     (0,0), (-1,0), 2, C_RED),
        ('LINEBELOW',     (0,0), (-1,-1), 2, C_RED),
        ('LEFTPADDING',   (0,0), (-1,-1), 8),
        ('RIGHTPADDING',  (0,0), (-1,-1), 8),
        ('TOPPADDING',    (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('VALIGN',        (0,0), (-1,-1), 'MIDDLE'),
        ('GRID',          (0,0), (-1,-1), 0.3, C_GRAY),
    ]))
    elements.append(t_orden)
    elements.append(Spacer(1, 3.5*mm))

    # ── DATOS DEL CLIENTE ───────────────────────────────────────────
    draw_section_header(elements, 'DATOS DEL CLIENTE')
    cliente_data = [
        [make_field('NOMBRE Y APELLIDO'), make_field('D.N.I. / C.U.I.T.')],
        [make_field('TELÉFONO / CELULAR'), make_field('E-MAIL')],
        [make_field('DIRECCIÓN COMPLETA'), make_field('CIUDAD / LOCALIDAD')],
    ]
    t_cli = Table(cliente_data, colWidths=[col_w + 5*mm, col_w - 5*mm])
    t_cli.setStyle(TableStyle([
        ('BACKGROUND',    (0,0), (-1,-1), C_DARK),
        ('LEFTPADDING',   (0,0), (-1,-1), 8),
        ('RIGHTPADDING',  (0,0), (-1,-1), 8),
        ('TOPPADDING',    (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 7),
        ('GRID',          (0,0), (-1,-1), 0.3, C_GRAY),
        ('ROWBACKGROUNDS',(0,0), (-1,-1), [C_DARK, HexColor('#161616'), C_DARK]),
    ]))
    elements.append(t_cli)
    elements.append(Spacer(1, 3.5*mm))

    # ── DATOS DE LA MOTO ────────────────────────────────────────────
    draw_section_header(elements, 'DATOS DE LA MOTOCICLETA')
    moto_data = [
        [make_field('MARCA'), make_field('MODELO'), make_field('AÑO')],
        [make_field('DOMINIO / PATENTE'), make_field('KILOMETRAJE'), make_field('TIPO DE USO')],
        [make_field('N° DE CHASIS (VIN)'), make_field('N° DE MOTOR'), make_field('COLOR / DESCRIPCIÓN')],
    ]
    t_moto = Table(moto_data, colWidths=[col3_w, col3_w, col3_w])
    t_moto.setStyle(TableStyle([
        ('BACKGROUND',    (0,0), (-1,-1), C_DARK),
        ('LEFTPADDING',   (0,0), (-1,-1), 8),
        ('RIGHTPADDING',  (0,0), (-1,-1), 8),
        ('TOPPADDING',    (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 7),
        ('GRID',          (0,0), (-1,-1), 0.3, C_GRAY),
        ('ROWBACKGROUNDS',(0,0), (-1,-1), [C_DARK, HexColor('#161616'), C_DARK]),
    ]))
    elements.append(t_moto)
    elements.append(Spacer(1, 3.5*mm))

    # ── TRABAJOS SOLICITADOS ────────────────────────────────────────
    draw_section_header(elements, 'TRABAJOS SOLICITADOS', '(marcar con ✓)')
    trabajos = [
        ['Service General', 'Cambio de Aceite Motor', 'Cambio de Filtro de Aceite'],
        ['Cambio de Filtro de Aire', 'Cambio de Bujías', 'Regulación de Válvulas'],
        ['Diagnóstico Electrónico', 'Reprogramación ECU / Mapa', 'Banco de Potencia (Dyno)'],
        ['Control y Ajuste de Frenos', 'Control de Transmisión', 'Control de Suspensiones'],
        ['Revisión Sistema Eléctrico', 'Lavado / Detailing', 'Otro: ___________________'],
    ]
    trab_rows = [[checkbox_cell(t) for t in row] for row in trabajos]
    t_trab = Table(trab_rows, colWidths=[col3_w, col3_w, col3_w])
    t_trab.setStyle(TableStyle([
        ('BACKGROUND',    (0,0), (-1,-1), C_DARK),
        ('LEFTPADDING',   (0,0), (-1,-1), 10),
        ('RIGHTPADDING',  (0,0), (-1,-1), 8),
        ('TOPPADDING',    (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('GRID',          (0,0), (-1,-1), 0.3, C_GRAY),
        ('ROWBACKGROUNDS',(0,0), (-1,-1), [C_DARK, HexColor('#161616'),
                                            C_DARK, HexColor('#161616'), C_DARK]),
    ]))
    elements.append(t_trab)
    elements.append(Spacer(1, 3.5*mm))

    # ── INSPECCIÓN TÉCNICA ──────────────────────────────────────────
    draw_section_header(elements, 'INSPECCIÓN TÉCNICA GENERAL')
    items_insp = [
        'Aceite Motor', 'Refrigerante / Líquido de Frenos',
        'Pastillas Freno Delanteras', 'Pastillas Freno Traseras',
        'Kit de Transmisión', 'Neumático Delantero',
        'Neumático Trasero', 'Batería / Carga',
        'Luces', 'Suspensión Delantera',
        'Suspensión Trasera', 'Filtro de Combustible',
    ]

    insp_header_row = [
        Paragraph('<b><font color="#D4AF37" size="8">COMPONENTE</font></b>',
                  ParagraphStyle('ih', fontName='Helvetica-Bold', fontSize=8,
                                 textColor=C_GOLD, leading=10)),
        Paragraph('<b><font color="#D4AF37" size="8">ESTADO</font></b>',
                  ParagraphStyle('ih2', fontName='Helvetica-Bold', fontSize=8,
                                 textColor=C_GOLD, leading=10)),
        Paragraph('<b><font color="#D4AF37" size="8">COMPONENTE</font></b>',
                  ParagraphStyle('ih3', fontName='Helvetica-Bold', fontSize=8,
                                 textColor=C_GOLD, leading=10)),
        Paragraph('<b><font color="#D4AF37" size="8">ESTADO</font></b>',
                  ParagraphStyle('ih4', fontName='Helvetica-Bold', fontSize=8,
                                 textColor=C_GOLD, leading=10)),
    ]

    insp_rows = [insp_header_row]
    mid = len(items_insp) // 2
    for i in range(mid):
        left_item = items_insp[i]
        right_item = items_insp[i + mid] if i + mid < len(items_insp) else ''
        estado = ('<font color="#22AA44">◻</font> <font color="#AAAAAA" size="7.5">Bueno</font>  '
                  '<font color="#FFAA00">◻</font> <font color="#AAAAAA" size="7.5">Regular</font>  '
                  '<font color="#CC0000">◻</font> <font color="#AAAAAA" size="7.5">Cambiar</font>')
        insp_rows.append([
            Paragraph(f'<font color="#DDDDDD" size="8">{left_item}</font>',
                      ParagraphStyle('ir', fontName='Helvetica', fontSize=8,
                                     textColor=C_WHITE, leading=10)),
            Paragraph(estado, ParagraphStyle('ck', fontName='Helvetica', fontSize=7.5,
                                              textColor=C_WHITE, leading=10)),
            Paragraph(f'<font color="#DDDDDD" size="8">{right_item}</font>',
                      ParagraphStyle('ir2', fontName='Helvetica', fontSize=8,
                                     textColor=C_WHITE, leading=10)),
            Paragraph(estado, ParagraphStyle('ck2', fontName='Helvetica', fontSize=7.5,
                                              textColor=C_WHITE, leading=10)),
        ])

    c1 = total_content_w * 0.22
    c2 = total_content_w * 0.28
    t_insp = Table(insp_rows, colWidths=[c1, c2, c1, c2])
    insp_styles = [
        ('BACKGROUND',    (0,0), (-1,0),   C_MIDGRAY),
        ('LINEBELOW',     (0,0), (-1,0),   1, C_RED),
        ('LEFTPADDING',   (0,0), (-1,-1),  7),
        ('RIGHTPADDING',  (0,0), (-1,-1),  5),
        ('TOPPADDING',    (0,0), (-1,-1),  4),
        ('BOTTOMPADDING', (0,0), (-1,-1),  4),
        ('GRID',          (0,0), (-1,-1),  0.3, C_GRAY),
        ('LINEBEFORE',    (2,0), (2,-1),   1, C_RED),
    ]
    for i in range(1, len(insp_rows)):
        bg = C_DARK if i % 2 == 0 else HexColor('#161616')
        insp_styles.append(('BACKGROUND', (0,i), (-1,i), bg))
    t_insp.setStyle(TableStyle(insp_styles))
    elements.append(t_insp)
    elements.append(Spacer(1, 3.5*mm))

    # ── PERFORMANCE ─────────────────────────────────────────────────
    draw_section_header(elements, 'DIAGNÓSTICO PERFORMANCE & ECU')
    perf_data = [
        [
            Paragraph('<font color="#999999" size="7.5">ECU ORIGINAL LEÍDA</font><br/>'
                      '<font color="#22AA44">◻</font><font color="#CCCCCC" size="9"> SÍ</font>   '
                      '<font color="#CC0000">◻</font><font color="#CCCCCC" size="9"> NO</font>',
                      ParagraphStyle('pe1', fontName='Helvetica', fontSize=9,
                                     textColor=C_WHITE, leading=13)),
            Paragraph('<font color="#999999" size="7.5">BACKUP REALIZADO</font><br/>'
                      '<font color="#22AA44">◻</font><font color="#CCCCCC" size="9"> SÍ</font>   '
                      '<font color="#CC0000">◻</font><font color="#CCCCCC" size="9"> NO</font>',
                      ParagraphStyle('pe2', fontName='Helvetica', fontSize=9,
                                     textColor=C_WHITE, leading=13)),
            make_field('MAPA / CALIBRACIÓN APLICADA'),
            make_field('HERRAMIENTA / SOFTWARE'),
        ],
        [
            Paragraph('<font color="#999999" size="7.5">POTENCIA ORIGINAL</font><br/>'
                      '<font color="#FFFFFF" size="10">_______ HP / _______ Nm</font>',
                      ParagraphStyle('hp1', fontName='Helvetica', fontSize=10,
                                     textColor=C_WHITE, leading=13)),
            Paragraph('<font color="#999999" size="7.5">POTENCIA FINAL (Dyno)</font><br/>'
                      '<font color="#FF2222" size="12"><b>_______ HP / _______ Nm</b></font>',
                      ParagraphStyle('hp2', fontName='Helvetica-Bold', fontSize=12,
                                     textColor=C_RED_LIGHT, leading=15)),
            Paragraph('<font color="#999999" size="7.5">GANANCIA</font><br/>'
                      '<font color="#D4AF37" size="14"><b>+ _______ HP</b></font>',
                      ParagraphStyle('hp3', fontName='Helvetica-Bold', fontSize=14,
                                     textColor=C_GOLD, leading=17)),
            make_field('TÉCNICO RESPONSABLE'),
        ],
    ]
    c_perf = total_content_w / 4
    t_perf = Table(perf_data, colWidths=[c_perf, c_perf, c_perf, c_perf])
    t_perf.setStyle(TableStyle([
        ('BACKGROUND',    (0,0), (-1,-1), C_DARK),
        ('LEFTPADDING',   (0,0), (-1,-1), 8),
        ('RIGHTPADDING',  (0,0), (-1,-1), 8),
        ('TOPPADDING',    (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('GRID',          (0,0), (-1,-1), 0.3, C_GRAY),
        ('BACKGROUND',    (1,1), (1,1),   HexColor('#1A0000')),
        ('BACKGROUND',    (2,1), (2,1),   HexColor('#1A1400')),
        ('ROWBACKGROUNDS',(0,0), (-1,-1), [C_DARK, HexColor('#161616')]),
    ]))
    elements.append(t_perf)
    elements.append(Spacer(1, 3.5*mm))

    # ── OBSERVACIONES ───────────────────────────────────────────────
    draw_section_header(elements, 'OBSERVACIONES TÉCNICAS')
    obs_data = [[
        Paragraph(
            ('<font color="#333333" size="8">' + '─' * 95 + '</font><br/><br/>') * 3 +
            '<font color="#333333" size="8">' + '─' * 95 + '</font>',
            ParagraphStyle('obs', fontName='Helvetica', fontSize=8,
                           textColor=C_WHITE, leading=18)
        )
    ]]
    t_obs = Table(obs_data, colWidths=[total_content_w])
    t_obs.setStyle(TableStyle([
        ('BACKGROUND',    (0,0), (-1,-1), C_DARK),
        ('LEFTPADDING',   (0,0), (-1,-1), 8),
        ('RIGHTPADDING',  (0,0), (-1,-1), 8),
        ('TOPPADDING',    (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
    ]))
    elements.append(t_obs)
    elements.append(Spacer(1, 3.5*mm))

    # ── PRESUPUESTO ─────────────────────────────────────────────────
    draw_section_header(elements, 'DETALLE DE TRABAJOS Y PRESUPUESTO')
    pres_header_row = [
        Paragraph('<b><font color="#D4AF37" size="8">N°</font></b>',
                  ParagraphStyle('ph0', fontName='Helvetica-Bold', fontSize=8,
                                 textColor=C_GOLD, leading=10, alignment=TA_CENTER)),
        Paragraph('<b><font color="#D4AF37" size="8">DESCRIPCIÓN DEL TRABAJO / REPUESTO</font></b>',
                  ParagraphStyle('ph1', fontName='Helvetica-Bold', fontSize=8,
                                 textColor=C_GOLD, leading=10)),
        Paragraph('<b><font color="#D4AF37" size="8">CANT.</font></b>',
                  ParagraphStyle('ph2', fontName='Helvetica-Bold', fontSize=8,
                                 textColor=C_GOLD, leading=10, alignment=TA_CENTER)),
        Paragraph('<b><font color="#D4AF37" size="8">P. UNIT.</font></b>',
                  ParagraphStyle('ph3', fontName='Helvetica-Bold', fontSize=8,
                                 textColor=C_GOLD, leading=10, alignment=TA_CENTER)),
        Paragraph('<b><font color="#D4AF37" size="8">TOTAL</font></b>',
                  ParagraphStyle('ph4', fontName='Helvetica-Bold', fontSize=8,
                                 textColor=C_GOLD, leading=10, alignment=TA_CENTER)),
    ]
    pres_rows = [pres_header_row]
    for i in range(5):
        pres_rows.append([
            Paragraph(f'<font color="#666666" size="8">{i+1:02d}</font>',
                      ParagraphStyle('pn', fontName='Helvetica', fontSize=8,
                                     textColor=C_WHITE, leading=10, alignment=TA_CENTER)),
            Paragraph('<font color="#2A2A2A" size="8">' + '─' * 55 + '</font>',
                      ParagraphStyle('pd', fontName='Helvetica', fontSize=8,
                                     textColor=C_WHITE, leading=10)),
            Paragraph('<font color="#2A2A2A" size="8">───</font>',
                      ParagraphStyle('pc', fontName='Helvetica', fontSize=8,
                                     textColor=C_WHITE, leading=10, alignment=TA_CENTER)),
            Paragraph('<font color="#2A2A2A" size="8">$ ──────</font>',
                      ParagraphStyle('pu', fontName='Helvetica', fontSize=8,
                                     textColor=C_WHITE, leading=10, alignment=TA_RIGHT)),
            Paragraph('<font color="#2A2A2A" size="8">$ ──────</font>',
                      ParagraphStyle('pt', fontName='Helvetica', fontSize=8,
                                     textColor=C_WHITE, leading=10, alignment=TA_RIGHT)),
        ])
    pres_rows.append([
        '', '', '',
        Paragraph('<font color="#AAAAAA" size="8"><b>SUBTOTAL</b></font>',
                  ParagraphStyle('sub', fontName='Helvetica-Bold', fontSize=8,
                                 textColor=HexColor('#AAAAAA'), leading=10, alignment=TA_RIGHT)),
        Paragraph('<font color="#FFFFFF" size="9"><b>$ ──────────</b></font>',
                  ParagraphStyle('subv', fontName='Helvetica-Bold', fontSize=9,
                                 textColor=C_WHITE, leading=11, alignment=TA_RIGHT)),
    ])
    pres_rows.append([
        '', '', '',
        Paragraph('<font color="#D4AF37" size="9"><b>TOTAL A PAGAR</b></font>',
                  ParagraphStyle('tot', fontName='Helvetica-Bold', fontSize=9,
                                 textColor=C_GOLD, leading=11, alignment=TA_RIGHT)),
        Paragraph('<font color="#FF2222" size="13"><b>$ ──────────</b></font>',
                  ParagraphStyle('totv', fontName='Helvetica-Bold', fontSize=13,
                                 textColor=C_RED_LIGHT, leading=14, alignment=TA_RIGHT)),
    ])

    t_pres = Table(pres_rows,
                   colWidths=[total_content_w*0.05, total_content_w*0.50,
                               total_content_w*0.10, total_content_w*0.18,
                               total_content_w*0.17])
    pres_styles = [
        ('BACKGROUND',    (0,0), (-1,0),   C_MIDGRAY),
        ('LINEBELOW',     (0,0), (-1,0),   1, C_RED),
        ('LEFTPADDING',   (0,0), (-1,-1),  6),
        ('RIGHTPADDING',  (0,0), (-1,-1),  6),
        ('TOPPADDING',    (0,0), (-1,-1),  4),
        ('BOTTOMPADDING', (0,0), (-1,-1),  5),
        ('GRID',          (0,1), (-1,-3),  0.3, C_GRAY),
        ('BACKGROUND',    (0,-2), (-1,-2), C_DARKGRAY),
        ('BACKGROUND',    (0,-1), (-1,-1), HexColor('#1A0000')),
        ('LINEABOVE',     (0,-2), (-1,-2), 0.5, C_GOLD),
        ('LINEABOVE',     (0,-1), (-1,-1), 1.5, C_RED),
        ('SPAN',          (0,-2), (2,-2)),
        ('SPAN',          (0,-1), (2,-1)),
    ]
    for i in range(1, len(pres_rows) - 2):
        bg = C_DARK if i % 2 == 0 else HexColor('#161616')
        pres_styles.append(('BACKGROUND', (0,i), (-1,i), bg))
    t_pres.setStyle(TableStyle(pres_styles))
    elements.append(t_pres)
    elements.append(Spacer(1, 3.5*mm))

    # ── FIRMAS ──────────────────────────────────────────────────────
    draw_section_header(elements, 'CONFORMIDAD Y FIRMAS')
    firma_data = [[
        Paragraph(
            '<font color="#999999" size="7.5">FIRMA Y ACLARACIÓN DEL CLIENTE</font>'
            '<br/><br/><br/><br/>'
            '<font color="#CC0000" size="7.5">──────────────────────────────────</font><br/>'
            '<font color="#666666" size="7">Acepto los trabajos y el presupuesto presentado</font>',
            ParagraphStyle('fc', fontName='Helvetica', fontSize=7.5,
                           textColor=C_WHITE, leading=11, alignment=TA_CENTER)
        ),
        Paragraph(
            '<font color="#999999" size="7.5">TÉCNICO RESPONSABLE — AGM PERFORMANCE</font>'
            '<br/><br/><br/><br/>'
            '<font color="#CC0000" size="7.5">──────────────────────────────────</font><br/>'
            '<font color="#666666" size="7">Firma y legajo del mecánico responsable</font>',
            ParagraphStyle('ft', fontName='Helvetica', fontSize=7.5,
                           textColor=C_WHITE, leading=11, alignment=TA_CENTER)
        ),
        Paragraph(
            '<font color="#999999" size="7.5">SELLO OFICIAL DEL TALLER</font>'
            '<br/><br/><br/><br/>'
            '<font color="#CC0000" size="7.5">──────────────────────────────────</font><br/>'
            '<font color="#666666" size="7">AGM Performance Service Chiptunning</font>',
            ParagraphStyle('fs', fontName='Helvetica', fontSize=7.5,
                           textColor=C_WHITE, leading=11, alignment=TA_CENTER)
        ),
    ]]
    t_firma = Table(firma_data, colWidths=[col3_w, col3_w, col3_w])
    t_firma.setStyle(TableStyle([
        ('BACKGROUND',    (0,0), (-1,-1), C_DARK),
        ('LEFTPADDING',   (0,0), (-1,-1), 8),
        ('RIGHTPADDING',  (0,0), (-1,-1), 8),
        ('TOPPADDING',    (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 10),
        ('GRID',          (0,0), (-1,-1), 0.3, C_GRAY),
        ('ALIGN',         (0,0), (-1,-1), 'CENTER'),
        ('VALIGN',        (0,0), (-1,-1), 'BOTTOM'),
    ]))
    elements.append(t_firma)

    # BUILD
    doc.build(elements, canvasmaker=HeaderOverlay)
    print(f"✅ PDF Premium generado: {output_path}")


if __name__ == '__main__':
    os.chdir('/home/user/TRAMANONE')
    generate_premium_pdf('AGM_Ficha_Service_PREMIUM.pdf')
