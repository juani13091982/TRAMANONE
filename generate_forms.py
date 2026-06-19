"""
AGM Performance — 3 diseños de Ficha de Service
Generador correcto: fondo dibujado ANTES del contenido via callbacks.
"""

import os
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm, mm
from reportlab.lib.colors import HexColor, white, black
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import (SimpleDocTemplate, Table, TableStyle,
                                 Paragraph, Spacer, Image)
from reportlab.pdfgen import canvas as pdfcanvas

LOGO = '/home/user/TRAMANONE/LOGO TRAMA.JPG.jpeg'
W, H = A4   # 595.27 x 841.89 pts

# ─── helpers de estilo ───────────────────────────────────────────────────────

def ps(name, font='Helvetica', size=8, color=black, align=TA_LEFT,
       leading=None, bold=False):
    return ParagraphStyle(name,
        fontName='Helvetica-Bold' if bold else font,
        fontSize=size, textColor=color,
        alignment=align, leading=leading or size + 3)

def p(text, style): return Paragraph(text, style)

def field(label, value='', style_label=None, style_value=None):
    """Par label / línea de valor."""
    sl = style_label or ps('lbl', size=7, color=HexColor('#888888'))
    sv = style_value or ps('val', size=9)
    return [p(label, sl), p(value or ('─' * 40), sv)]

# ─── DISEÑO 1: DARK RACING ───────────────────────────────────────────────────
# Fondo negro, texto blanco, acentos rojo-dorado. Fondo pintado con callback.

def bg_dark(c, doc):
    """Callback: fondo dark racing para Diseño 1."""
    # Fondo negro total
    c.setFillColor(HexColor('#0D0D0D'))
    c.rect(0, 0, W, H, fill=1, stroke=0)
    # Barras laterales rojas
    c.setFillColor(HexColor('#CC0000'))
    c.rect(0, 0, 5, H, fill=1, stroke=0)
    c.rect(W - 5, 0, 5, H, fill=1, stroke=0)
    # Header oscuro
    c.setFillColor(HexColor('#1A1A1A'))
    c.rect(5, H - 42*mm, W - 10, 42*mm, fill=1, stroke=0)
    # Banda roja bajo header
    c.setFillColor(HexColor('#CC0000'))
    c.rect(5, H - 43.2*mm, W - 10, 2.2*mm, fill=1, stroke=0)
    # Banda dorada bajo roja
    c.setFillColor(HexColor('#D4AF37'))
    c.rect(5, H - 44*mm, W - 10, 0.8*mm, fill=1, stroke=0)
    # Logo
    if os.path.exists(LOGO):
        c.drawImage(LOGO, 9*mm, H - 40*mm, width=36*mm, height=30*mm,
                    preserveAspectRatio=True, mask='auto')
    # Título
    c.setFillColor(white)
    c.setFont('Helvetica-Bold', 20)
    c.drawString(50*mm, H - 16*mm, 'AGM PERFORMANCE')
    c.setFillColor(HexColor('#CC0000'))
    c.setFont('Helvetica-Bold', 10)
    c.drawString(50*mm, H - 23*mm, 'SERVICE  ·  CHIPTUNNING  ·  DIAGNÓSTICO')
    c.setFillColor(HexColor('#D4AF37'))
    c.rect(50*mm, H - 25*mm, 115*mm, 0.6*mm, fill=1, stroke=0)
    c.setFillColor(HexColor('#AAAAAA'))
    c.setFont('Helvetica', 8.5)
    c.drawString(50*mm, H - 30*mm, 'FICHA DE SERVICE Y DIAGNÓSTICO DE MOTOCICLETAS')
    # Info derecha
    c.setFillColor(HexColor('#777777'))
    c.setFont('Helvetica', 7.5)
    c.drawRightString(W - 9*mm, H - 14*mm, 'FORM-SRV-001 · Rev.2025')
    c.drawRightString(W - 9*mm, H - 21*mm, 'www.agmperformance.com.ar')
    # QR placeholder
    c.setStrokeColor(HexColor('#444444'))
    c.setLineWidth(0.5)
    c.rect(W - 28*mm, H - 40*mm, 18*mm, 18*mm, fill=0, stroke=1)
    c.setFillColor(HexColor('#555555'))
    c.setFont('Helvetica-Bold', 6)
    c.drawCentredString(W - 19*mm, H - 31*mm, 'CÓDIGO QR')
    c.drawCentredString(W - 19*mm, H - 34.5*mm, 'DEL TALLER')
    # Footer
    c.setFillColor(HexColor('#1A1A1A'))
    c.rect(5, 0, W - 10, 12*mm, fill=1, stroke=0)
    c.setFillColor(HexColor('#CC0000'))
    c.rect(5, 12*mm, W - 10, 1*mm, fill=1, stroke=0)
    c.setFillColor(HexColor('#777777'))
    c.setFont('Helvetica', 7)
    c.drawCentredString(W/2, 4*mm,
        'AGM Performance Service Chiptunning  ·  Documento de service para el cliente')
    # Marca de agua tenue
    c.saveState()
    c.setFillColor(HexColor('#181818'))
    c.setFont('Helvetica-Bold', 60)
    c.translate(W/2, H/2)
    c.rotate(40)
    c.drawCentredString(0, 0, 'AGM PERFORMANCE')
    c.restoreState()


def build_design1():
    """Diseño 1: Dark Racing."""
    out = '/home/user/TRAMANONE/DISEÑO1_DarkRacing.pdf'
    doc = SimpleDocTemplate(out, pagesize=A4,
                            leftMargin=1.2*cm, rightMargin=1.2*cm,
                            topMargin=4.8*cm, bottomMargin=1.8*cm)

    RED   = HexColor('#CC0000')
    GOLD  = HexColor('#D4AF37')
    W_    = HexColor('#FFFFFF')
    LG    = HexColor('#AAAAAA')
    DG    = HexColor('#888888')
    BG1   = HexColor('#111111')
    BG2   = HexColor('#181818')
    BGSH  = HexColor('#222222')
    BGSH2 = HexColor('#1A1A1A')
    GR    = HexColor('#2A2A2A')

    TW = W - (1.2*cm)*2      # total content width
    c2 = TW / 2
    c3 = TW / 3
    c4 = TW / 4

    els = []

    # ── helpers locales ───────────────────────────────────────────
    def sh(title, sub=''):
        """Section header."""
        txt = f'<font color="#CC0000">▐</font>  <b>{title}</b>'
        if sub: txt += f'  <font size="7" color="#777777">{sub}</font>'
        t = Table([[p(txt, ps('sh', size=9.5, color=W_, bold=True, leading=13))]],
                  colWidths=[TW])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0),(-1,-1), BGSH),
            ('TOPPADDING', (0,0),(-1,-1), 5),
            ('BOTTOMPADDING',(0,0),(-1,-1),5),
            ('LEFTPADDING',(0,0),(-1,-1),8),
            ('LINEABOVE',(0,0),(-1,0), 1.8, RED),
            ('LINEBELOW',(0,0),(-1,-1),0.5, GOLD),
        ]))
        els.append(t)
        els.append(Spacer(1, 1.5*mm))

    def mf(label, val=''):
        """Mini field cell."""
        return p(f'<font color="#888888" size="7">{label}</font><br/>'
                 f'<font color="#FFFFFF" size="9">{val or ("─"*38)}</font>',
                 ps('mf', color=W_, leading=13))

    def cb(text):
        return p(f'<font color="#CC0000" size="9">☐</font> '
                 f'<font color="#CCCCCC" size="8.5">{text}</font>',
                 ps('cb', color=W_, leading=12))

    def cell_style(rows, n_cols, widths, alts=None):
        """Genera tabla con filas y estilo dark."""
        a1 = alts[0] if alts else BG1
        a2 = alts[1] if alts else BG2
        t = Table(rows, colWidths=widths)
        styles = [
            ('LEFTPADDING', (0,0),(-1,-1), 7),
            ('RIGHTPADDING',(0,0),(-1,-1), 7),
            ('TOPPADDING',  (0,0),(-1,-1), 5),
            ('BOTTOMPADDING',(0,0),(-1,-1),6),
            ('GRID',        (0,0),(-1,-1), 0.3, GR),
        ]
        for i in range(len(rows)):
            styles.append(('BACKGROUND',(0,i),(-1,i), a1 if i%2==0 else a2))
        t.setStyle(TableStyle(styles))
        return t

    # ── BANDA DE ORDEN ─────────────────────────────────────────────
    ord_row = [[
        p('<font color="#888888" size="7">N° DE ORDEN</font><br/>'
          '<font color="#FF2222" size="22"><b>__________</b></font>',
          ps('ord', color=W_, leading=26, bold=True)),
        p('<font color="#888888" size="7">FECHA INGRESO</font><br/>'
          '<font color="#FFFFFF" size="11"><b>___ / ___ / ______</b></font>',
          ps('dt', color=W_, leading=15)),
        p('<font color="#888888" size="7">HORA</font><br/>'
          '<font color="#FFFFFF" size="11"><b>_____ : _____</b></font>',
          ps('hr', color=W_, leading=15)),
        p('<font color="#888888" size="7">ENTREGA ESTIMADA</font><br/>'
          '<font color="#FFFFFF" size="11"><b>___ / ___ / ______</b></font>',
          ps('ent', color=W_, leading=15)),
        p('<font color="#888888" size="7">PRIORIDAD</font><br/>'
          '<font color="#D4AF37" size="8">☐ URGENTE</font><br/>'
          '<font color="#22AA44" size="8">☐ NORMAL</font>',
          ps('pri', color=W_, leading=11)),
    ]]
    t_ord = Table(ord_row, colWidths=[TW*0.20, TW*0.22, TW*0.16, TW*0.26, TW*0.16])
    t_ord.setStyle(TableStyle([
        ('BACKGROUND',(0,0),(-1,-1), BGSH2),
        ('LINEABOVE',(0,0),(-1,0), 2, RED),
        ('LINEBELOW',(0,0),(-1,-1), 2, RED),
        ('LEFTPADDING',(0,0),(-1,-1),8),
        ('RIGHTPADDING',(0,0),(-1,-1),8),
        ('TOPPADDING',(0,0),(-1,-1),5),
        ('BOTTOMPADDING',(0,0),(-1,-1),6),
        ('VALIGN',(0,0),(-1,-1),'MIDDLE'),
        ('GRID',(0,0),(-1,-1),0.3, GR),
    ]))
    els.append(t_ord)
    els.append(Spacer(1, 3*mm))

    # ── CLIENTE ───────────────────────────────────────────────────
    sh('DATOS DEL CLIENTE')
    cli = cell_style([
        [mf('NOMBRE Y APELLIDO'), mf('D.N.I. / C.U.I.T.')],
        [mf('TELÉFONO / CELULAR'), mf('E-MAIL')],
        [mf('DIRECCIÓN'), mf('CIUDAD')],
    ], 2, [c2+5*mm, c2-5*mm])
    els.append(cli); els.append(Spacer(1,3*mm))

    # ── MOTO ──────────────────────────────────────────────────────
    sh('DATOS DE LA MOTOCICLETA')
    moto = cell_style([
        [mf('MARCA'), mf('MODELO'), mf('AÑO')],
        [mf('DOMINIO / PATENTE'), mf('KILOMETRAJE'), mf('TIPO DE USO')],
        [mf('N° DE CHASIS (VIN)'), mf('N° DE MOTOR'), mf('COLOR')],
    ], 3, [c3, c3, c3])
    els.append(moto); els.append(Spacer(1,3*mm))

    # ── TRABAJOS ──────────────────────────────────────────────────
    sh('TRABAJOS SOLICITADOS', '(marcar con ✓)')
    trab_items = [
        ['☐ Service General',          '☐ Cambio de Aceite Motor',     '☐ Filtro de Aceite'],
        ['☐ Filtro de Aire',            '☐ Cambio de Bujías',            '☐ Regulación de Válvulas'],
        ['☐ Diagnóstico Electrónico',   '☐ Reprogramación ECU / Mapa',  '☐ Banco de Potencia (Dyno)'],
        ['☐ Control de Frenos',         '☐ Control de Transmisión',      '☐ Control de Suspensiones'],
        ['☐ Revisión Eléctrica',        '☐ Lavado / Detailing',          '☐ Otro: ___________________'],
    ]
    trab_rows = [[cb(c.replace('☐','').strip()) for c in row] for row in trab_items]
    trab = cell_style(trab_rows, 3, [c3, c3, c3])
    els.append(trab); els.append(Spacer(1,3*mm))

    # ── INSPECCIÓN ────────────────────────────────────────────────
    sh('INSPECCIÓN TÉCNICA GENERAL')
    items = [
        ('Aceite Motor',             'Pastillas Freno Del.'),
        ('Refrigerante/Liq. Frenos', 'Pastillas Freno Tras.'),
        ('Kit de Transmisión',       'Neumático Delantero'),
        ('Neumático Trasero',        'Batería / Carga'),
        ('Luces',                    'Suspensión Delantera'),
        ('Suspensión Trasera',       'Filtro de Combustible'),
    ]
    estado = ('<font color="#22AA44" size="8">☐ Bueno</font>  '
              '<font color="#FFAA00" size="8">☐ Regular</font>  '
              '<font color="#CC0000" size="8">☐ Cambiar</font>')
    hdr = [
        p('<b><font color="#D4AF37" size="8">COMPONENTE</font></b>',
          ps('ih', color=GOLD, bold=True)),
        p('<b><font color="#D4AF37" size="8">ESTADO</font></b>',
          ps('ih2', color=GOLD, bold=True)),
        p('<b><font color="#D4AF37" size="8">COMPONENTE</font></b>',
          ps('ih3', color=GOLD, bold=True)),
        p('<b><font color="#D4AF37" size="8">ESTADO</font></b>',
          ps('ih4', color=GOLD, bold=True)),
    ]
    insp_rows = [hdr]
    for l, r in items:
        insp_rows.append([
            p(f'<font color="#DDDDDD" size="8.5">{l}</font>', ps('il', color=W_)),
            p(estado, ps('ie', color=W_, leading=11)),
            p(f'<font color="#DDDDDD" size="8.5">{r}</font>', ps('ir2', color=W_)),
            p(estado, ps('ie2', color=W_, leading=11)),
        ])
    c_i1 = TW*0.22; c_i2 = TW*0.28
    t_insp = Table(insp_rows, colWidths=[c_i1, c_i2, c_i1, c_i2])
    is_ = [
        ('BACKGROUND',(0,0),(-1,0), BGSH),
        ('LINEBELOW',(0,0),(-1,0),1,RED),
        ('LINEBEFORE',(2,0),(2,-1),0.8,RED),
        ('LEFTPADDING',(0,0),(-1,-1),7),
        ('RIGHTPADDING',(0,0),(-1,-1),5),
        ('TOPPADDING',(0,0),(-1,-1),4),
        ('BOTTOMPADDING',(0,0),(-1,-1),4),
        ('GRID',(0,0),(-1,-1),0.3,GR),
    ]
    for i in range(1, len(insp_rows)):
        is_.append(('BACKGROUND',(0,i),(-1,i), BG1 if i%2==0 else BG2))
    t_insp.setStyle(TableStyle(is_))
    els.append(t_insp); els.append(Spacer(1,3*mm))

    # ── PERFORMANCE ───────────────────────────────────────────────
    sh('PERFORMANCE & REPROGRAMACIÓN ECU')
    perf = [
        [
            p('<font color="#888888" size="7">ECU ORIGINAL LEÍDA</font><br/>'
              '<font color="#22AA44" size="9">☐ SÍ</font>  '
              '<font color="#CC0000" size="9">☐ NO</font>',
              ps('pe1', color=W_, leading=13)),
            p('<font color="#888888" size="7">BACKUP REALIZADO</font><br/>'
              '<font color="#22AA44" size="9">☐ SÍ</font>  '
              '<font color="#CC0000" size="9">☐ NO</font>',
              ps('pe2', color=W_, leading=13)),
            mf('MAPA / CALIBRACIÓN APLICADA'),
            mf('HERRAMIENTA / SOFTWARE'),
        ],
        [
            p('<font color="#888888" size="7">POTENCIA ORIGINAL</font><br/>'
              '<font color="#FFFFFF" size="10">_______ HP  /  _______ Nm</font>',
              ps('hp1', color=W_, leading=13)),
            p('<font color="#888888" size="7">POTENCIA FINAL (Dyno)</font><br/>'
              '<font color="#FF3333" size="13"><b>_______ HP  /  _______ Nm</b></font>',
              ps('hp2', color=HexColor('#FF3333'), bold=True, leading=16)),
            p('<font color="#888888" size="7">GANANCIA PERFORMANCE</font><br/>'
              '<font color="#D4AF37" size="16"><b>+ _______ HP</b></font>',
              ps('hp3', color=GOLD, bold=True, leading=19)),
            mf('TÉCNICO RESPONSABLE'),
        ],
    ]
    t_perf = Table(perf, colWidths=[c4,c4,c4,c4])
    t_perf.setStyle(TableStyle([
        ('GRID',(0,0),(-1,-1),0.3,GR),
        ('LEFTPADDING',(0,0),(-1,-1),8),('RIGHTPADDING',(0,0),(-1,-1),8),
        ('TOPPADDING',(0,0),(-1,-1),6),('BOTTOMPADDING',(0,0),(-1,-1),8),
        ('BACKGROUND',(0,0),(-1,0), BG1),
        ('BACKGROUND',(0,1),(-1,1), BG2),
        ('BACKGROUND',(1,1),(1,1), HexColor('#1A0000')),
        ('BACKGROUND',(2,1),(2,1), HexColor('#141200')),
    ]))
    els.append(t_perf); els.append(Spacer(1,3*mm))

    # ── OBSERVACIONES ─────────────────────────────────────────────
    sh('OBSERVACIONES TÉCNICAS DEL MECÁNICO')
    obs_txt = '<br/>'.join(
        [f'<font color="#2A2A2A" size="8">{"─"*110}</font><br/>'] * 4
    )
    t_obs = Table([[p(obs_txt, ps('obs', color=W_, leading=18))]], colWidths=[TW])
    t_obs.setStyle(TableStyle([
        ('BACKGROUND',(0,0),(-1,-1),BG1),
        ('LEFTPADDING',(0,0),(-1,-1),8),('RIGHTPADDING',(0,0),(-1,-1),8),
        ('TOPPADDING',(0,0),(-1,-1),6),('BOTTOMPADDING',(0,0),(-1,-1),6),
    ]))
    els.append(t_obs); els.append(Spacer(1,3*mm))

    # ── PRESUPUESTO ───────────────────────────────────────────────
    sh('DETALLE DE TRABAJOS Y PRESUPUESTO')
    p_hdr = [
        p('<b><font color="#D4AF37" size="8">N°</font></b>',    ps('ph0',color=GOLD,bold=True,align=TA_CENTER)),
        p('<b><font color="#D4AF37" size="8">DESCRIPCIÓN DEL TRABAJO / REPUESTO</font></b>', ps('ph1',color=GOLD,bold=True)),
        p('<b><font color="#D4AF37" size="8">CANT.</font></b>', ps('ph2',color=GOLD,bold=True,align=TA_CENTER)),
        p('<b><font color="#D4AF37" size="8">P. UNITARIO</font></b>', ps('ph3',color=GOLD,bold=True,align=TA_RIGHT)),
        p('<b><font color="#D4AF37" size="8">TOTAL</font></b>', ps('ph4',color=GOLD,bold=True,align=TA_RIGHT)),
    ]
    p_rows = [p_hdr]
    for i in range(5):
        p_rows.append([
            p(f'<font color="#666666" size="8">{i+1:02d}</font>', ps(f'pn{i}',color=W_,align=TA_CENTER)),
            p(f'<font color="#2A2A2A" size="8">{"─"*60}</font>', ps(f'pd{i}',color=W_)),
            p('<font color="#2A2A2A" size="8">───</font>', ps(f'pc{i}',color=W_,align=TA_CENTER)),
            p('<font color="#2A2A2A" size="8">$ ────────</font>', ps(f'pu{i}',color=W_,align=TA_RIGHT)),
            p('<font color="#2A2A2A" size="8">$ ────────</font>', ps(f'pt{i}',color=W_,align=TA_RIGHT)),
        ])
    p_rows += [
        ['','','', p('<b><font color="#AAAAAA" size="8">SUBTOTAL</font></b>', ps('sub',color=LG,bold=True,align=TA_RIGHT)),
                   p('<font color="#FFFFFF" size="9"><b>$ ────────────</b></font>', ps('subv',color=W_,bold=True,align=TA_RIGHT))],
        ['','','', p('<b><font color="#D4AF37" size="9">TOTAL A PAGAR</font></b>', ps('tot',color=GOLD,bold=True,align=TA_RIGHT)),
                   p('<font color="#FF3333" size="13"><b>$ ────────────</b></font>', ps('totv',color=HexColor('#FF3333'),bold=True,align=TA_RIGHT))],
    ]
    cw = [TW*0.05, TW*0.50, TW*0.10, TW*0.18, TW*0.17]
    t_pres = Table(p_rows, colWidths=cw)
    ps_ = [
        ('BACKGROUND',(0,0),(-1,0), BGSH),
        ('LINEBELOW',(0,0),(-1,0),1,RED),
        ('LEFTPADDING',(0,0),(-1,-1),6),('RIGHTPADDING',(0,0),(-1,-1),6),
        ('TOPPADDING',(0,0),(-1,-1),4),('BOTTOMPADDING',(0,0),(-1,-1),5),
        ('GRID',(0,1),(-1,-3),0.3,GR),
        ('BACKGROUND',(0,-2),(-1,-2), BGSH2),
        ('BACKGROUND',(0,-1),(-1,-1), HexColor('#1A0000')),
        ('LINEABOVE',(0,-2),(-1,-2),0.5,GOLD),
        ('LINEABOVE',(0,-1),(-1,-1),1.5,RED),
        ('SPAN',(0,-2),(2,-2)),('SPAN',(0,-1),(2,-1)),
    ]
    for i in range(1, len(p_rows)-2):
        ps_.append(('BACKGROUND',(0,i),(-1,i), BG1 if i%2==0 else BG2))
    t_pres.setStyle(TableStyle(ps_))
    els.append(t_pres); els.append(Spacer(1,3*mm))

    # ── FIRMAS ────────────────────────────────────────────────────
    sh('CONFORMIDAD Y FIRMAS')
    firma = [[
        p('<font color="#888888" size="7">FIRMA Y ACLARACIÓN DEL CLIENTE</font>'
          '<br/><br/><br/><br/>'
          '<font color="#CC0000">────────────────────────────────</font><br/>'
          '<font color="#555555" size="7">Acepto los trabajos y el presupuesto</font>',
          ps('fc', color=W_, leading=11, align=TA_CENTER)),
        p('<font color="#888888" size="7">TÉCNICO — AGM PERFORMANCE</font>'
          '<br/><br/><br/><br/>'
          '<font color="#CC0000">────────────────────────────────</font><br/>'
          '<font color="#555555" size="7">Firma y legajo del mecánico</font>',
          ps('ft', color=W_, leading=11, align=TA_CENTER)),
        p('<font color="#888888" size="7">SELLO OFICIAL DEL TALLER</font>'
          '<br/><br/><br/><br/>'
          '<font color="#CC0000">────────────────────────────────</font><br/>'
          '<font color="#555555" size="7">AGM Performance Service</font>',
          ps('fs', color=W_, leading=11, align=TA_CENTER)),
    ]]
    t_firma = Table(firma, colWidths=[c3,c3,c3])
    t_firma.setStyle(TableStyle([
        ('BACKGROUND',(0,0),(-1,-1),BG1),
        ('GRID',(0,0),(-1,-1),0.3,GR),
        ('LEFTPADDING',(0,0),(-1,-1),8),('RIGHTPADDING',(0,0),(-1,-1),8),
        ('TOPPADDING',(0,0),(-1,-1),6),('BOTTOMPADDING',(0,0),(-1,-1),10),
        ('ALIGN',(0,0),(-1,-1),'CENTER'),
        ('VALIGN',(0,0),(-1,-1),'BOTTOM'),
    ]))
    els.append(t_firma)

    doc.build(els, onFirstPage=bg_dark, onLaterPages=bg_dark)
    print(f'✅ {out}')
    return out


# ─── DISEÑO 2: PROFESSIONAL WHITE ───────────────────────────────────────────
# Fondo blanco, encabezado oscuro, acentos rojo. Ideal para imprimir en B&N.

def bg_white(c, doc):
    """Callback: fondo blanco profesional para Diseño 2."""
    c.setFillColor(white)
    c.rect(0, 0, W, H, fill=1, stroke=0)
    # Header oscuro
    c.setFillColor(HexColor('#1A1A1A'))
    c.rect(0, H - 40*mm, W, 40*mm, fill=1, stroke=0)
    # Banda roja bajo header
    c.setFillColor(HexColor('#CC0000'))
    c.rect(0, H - 41.5*mm, W, 1.5*mm, fill=1, stroke=0)
    # Logo
    if os.path.exists(LOGO):
        c.drawImage(LOGO, 8*mm, H - 38*mm, width=34*mm, height=28*mm,
                    preserveAspectRatio=True, mask='auto')
    # Título
    c.setFillColor(white)
    c.setFont('Helvetica-Bold', 20)
    c.drawString(47*mm, H - 14*mm, 'AGM PERFORMANCE')
    c.setFillColor(HexColor('#CC0000'))
    c.setFont('Helvetica-Bold', 9.5)
    c.drawString(47*mm, H - 21*mm, 'SERVICE  ·  CHIPTUNNING  ·  DIAGNÓSTICO')
    c.setFillColor(HexColor('#AAAAAA'))
    c.setFont('Helvetica', 8.5)
    c.drawString(47*mm, H - 28.5*mm, 'FICHA DE SERVICE Y DIAGNÓSTICO DE MOTOCICLETAS')
    # Info derecha
    c.setFillColor(HexColor('#AAAAAA'))
    c.setFont('Helvetica', 7.5)
    c.drawRightString(W - 8*mm, H - 12*mm, 'FORM-SRV-001 · Rev.2025')
    c.drawRightString(W - 8*mm, H - 19.5*mm, 'www.agmperformance.com.ar')
    c.drawRightString(W - 8*mm, H - 27*mm, '──────────────────')
    # Líneas grises de fondo (efecto formulario)
    c.setStrokeColor(HexColor('#F0F0F0'))
    c.setLineWidth(0.5)
    for y in range(int(H - 50*mm), int(15*mm), -6):
        c.line(8*mm, y, W - 8*mm, y)
    # Footer
    c.setFillColor(HexColor('#CC0000'))
    c.rect(0, 0, W, 10*mm, fill=1, stroke=0)
    c.setFillColor(white)
    c.setFont('Helvetica-Bold', 7)
    c.drawCentredString(W/2, 3.5*mm,
        'AGM Performance Service Chiptunning  ·  Este comprobante es válido como recibo de service')


def build_design2():
    """Diseño 2: Professional White."""
    out = '/home/user/TRAMANONE/DISEÑO2_ProfessionalWhite.pdf'
    doc = SimpleDocTemplate(out, pagesize=A4,
                            leftMargin=1.0*cm, rightMargin=1.0*cm,
                            topMargin=4.5*cm, bottomMargin=1.5*cm)

    RED   = HexColor('#CC0000')
    DARK  = HexColor('#1A1A1A')
    MID   = HexColor('#444444')
    LGRAY = HexColor('#888888')
    BGSH  = HexColor('#CC0000')
    BG1   = HexColor('#FFFFFF')
    BG2   = HexColor('#F9F9F9')
    BGALT = HexColor('#FFF5F5')

    TW = W - 2*cm
    c2 = TW / 2
    c3 = TW / 3
    c4 = TW / 4

    els = []

    def sh(title, sub=''):
        txt = f'<font color="#FFFFFF"><b>{title}</b></font>'
        if sub: txt += f'  <font size="7" color="#FFAAAA">{sub}</font>'
        t = Table([[p(txt, ps('sh2', size=9.5, color=white, bold=True, leading=13))]],
                  colWidths=[TW])
        t.setStyle(TableStyle([
            ('BACKGROUND',(0,0),(-1,-1), RED),
            ('TOPPADDING',(0,0),(-1,-1),5),
            ('BOTTOMPADDING',(0,0),(-1,-1),5),
            ('LEFTPADDING',(0,0),(-1,-1),10),
        ]))
        els.append(t)
        els.append(Spacer(1, 1.5*mm))

    def mf(label, val=''):
        return p(f'<font color="#888888" size="7"><b>{label}</b></font><br/>'
                 f'<font color="#222222" size="9">{val or ("─"*38)}</font>',
                 ps('mf2', color=DARK, leading=13))

    def cb(text):
        return p(f'<font color="#CC0000" size="9">☐</font> '
                 f'<font color="#333333" size="8.5">{text}</font>',
                 ps('cb2', color=DARK, leading=12))

    def stable(rows, widths):
        t = Table(rows, colWidths=widths)
        styles = [
            ('LEFTPADDING',(0,0),(-1,-1),7),('RIGHTPADDING',(0,0),(-1,-1),7),
            ('TOPPADDING',(0,0),(-1,-1),5),('BOTTOMPADDING',(0,0),(-1,-1),6),
            ('GRID',(0,0),(-1,-1),0.5,HexColor('#DDDDDD')),
            ('LINEBELOW',(0,-1),(-1,-1),1,RED),
        ]
        for i in range(len(rows)):
            styles.append(('BACKGROUND',(0,i),(-1,i), BG1 if i%2==0 else BG2))
        t.setStyle(TableStyle(styles))
        return t

    # Banda de orden
    ord_row = [[
        p('<font color="#888888" size="7"><b>N° DE ORDEN</b></font><br/>'
          '<font color="#CC0000" size="22"><b>__________</b></font>',
          ps('ord2', color=DARK, leading=26, bold=True)),
        p('<font color="#888888" size="7"><b>FECHA INGRESO</b></font><br/>'
          '<font color="#222222" size="11"><b>___ / ___ / ______</b></font>',
          ps('dt2', color=DARK, leading=15)),
        p('<font color="#888888" size="7"><b>HORA</b></font><br/>'
          '<font color="#222222" size="11"><b>_____ : _____</b></font>',
          ps('hr2', color=DARK, leading=15)),
        p('<font color="#888888" size="7"><b>ENTREGA ESTIMADA</b></font><br/>'
          '<font color="#222222" size="11"><b>___ / ___ / ______</b></font>',
          ps('ent2', color=DARK, leading=15)),
        p('<font color="#888888" size="7"><b>PRIORIDAD</b></font><br/>'
          '<font color="#CC0000" size="8">☐ URGENTE</font><br/>'
          '<font color="#228844" size="8">☐ NORMAL</font>',
          ps('pri2', color=DARK, leading=11)),
    ]]
    t_ord = Table(ord_row, colWidths=[TW*0.20, TW*0.22, TW*0.16, TW*0.26, TW*0.16])
    t_ord.setStyle(TableStyle([
        ('BACKGROUND',(0,0),(-1,-1), HexColor('#F5F5F5')),
        ('LINEABOVE',(0,0),(-1,0),2,RED),
        ('LINEBELOW',(0,0),(-1,-1),2,DARK),
        ('LEFTPADDING',(0,0),(-1,-1),8),('RIGHTPADDING',(0,0),(-1,-1),8),
        ('TOPPADDING',(0,0),(-1,-1),5),('BOTTOMPADDING',(0,0),(-1,-1),6),
        ('VALIGN',(0,0),(-1,-1),'MIDDLE'),
        ('GRID',(0,0),(-1,-1),0.5,HexColor('#DDDDDD')),
    ]))
    els.append(t_ord); els.append(Spacer(1,3*mm))

    sh('DATOS DEL CLIENTE')
    els.append(stable([
        [mf('NOMBRE Y APELLIDO'), mf('D.N.I. / C.U.I.T.')],
        [mf('TELÉFONO / CELULAR'), mf('E-MAIL')],
        [mf('DIRECCIÓN'), mf('CIUDAD')],
    ], [c2+5*mm, c2-5*mm])); els.append(Spacer(1,3*mm))

    sh('DATOS DE LA MOTOCICLETA')
    els.append(stable([
        [mf('MARCA'), mf('MODELO'), mf('AÑO')],
        [mf('DOMINIO / PATENTE'), mf('KILOMETRAJE'), mf('TIPO DE USO')],
        [mf('N° DE CHASIS (VIN)'), mf('N° DE MOTOR'), mf('COLOR')],
    ], [c3,c3,c3])); els.append(Spacer(1,3*mm))

    sh('TRABAJOS SOLICITADOS', '(marcar con ✓)')
    trab_items = [
        ['Service General', 'Cambio de Aceite Motor', 'Filtro de Aceite'],
        ['Filtro de Aire', 'Cambio de Bujías', 'Regulación de Válvulas'],
        ['Diagnóstico Electrónico', 'Reprogramación ECU / Mapa', 'Banco de Potencia (Dyno)'],
        ['Control de Frenos', 'Control de Transmisión', 'Control de Suspensiones'],
        ['Revisión Eléctrica', 'Lavado / Detailing', 'Otro: ___________________'],
    ]
    trab_rows = [[cb(c) for c in row] for row in trab_items]
    els.append(stable(trab_rows, [c3,c3,c3])); els.append(Spacer(1,3*mm))

    sh('INSPECCIÓN TÉCNICA GENERAL')
    items = [
        ('Aceite Motor','Pastillas Freno Del.'),
        ('Refrigerante/Liq. Frenos','Pastillas Freno Tras.'),
        ('Kit de Transmisión','Neumático Delantero'),
        ('Neumático Trasero','Batería / Carga'),
        ('Luces','Suspensión Delantera'),
        ('Suspensión Trasera','Filtro de Combustible'),
    ]
    estado = ('<font color="#228844" size="8">☐ Bueno</font>  '
              '<font color="#CC8800" size="8">☐ Regular</font>  '
              '<font color="#CC0000" size="8">☐ Cambiar</font>')
    hdr2 = [
        p('<b><font color="#FFFFFF" size="8">COMPONENTE</font></b>', ps('ih2w',color=white,bold=True)),
        p('<b><font color="#FFFFFF" size="8">ESTADO</font></b>',     ps('ie2w',color=white,bold=True)),
        p('<b><font color="#FFFFFF" size="8">COMPONENTE</font></b>', ps('ih2w2',color=white,bold=True)),
        p('<b><font color="#FFFFFF" size="8">ESTADO</font></b>',     ps('ie2w2',color=white,bold=True)),
    ]
    insp2 = [hdr2]
    for l, r in items:
        insp2.append([
            p(f'<font color="#333333" size="8.5">{l}</font>', ps('il2',color=DARK)),
            p(estado, ps('ie2x',color=DARK,leading=11)),
            p(f'<font color="#333333" size="8.5">{r}</font>', ps('ir2x',color=DARK)),
            p(estado, ps('ie2y',color=DARK,leading=11)),
        ])
    c_i1 = TW*0.22; c_i2 = TW*0.28
    t_i2 = Table(insp2, colWidths=[c_i1,c_i2,c_i1,c_i2])
    is2 = [
        ('BACKGROUND',(0,0),(-1,0), DARK),
        ('LINEBELOW',(0,0),(-1,0),1,RED),
        ('LINEBEFORE',(2,0),(2,-1),0.8,RED),
        ('LEFTPADDING',(0,0),(-1,-1),7),('RIGHTPADDING',(0,0),(-1,-1),5),
        ('TOPPADDING',(0,0),(-1,-1),4),('BOTTOMPADDING',(0,0),(-1,-1),4),
        ('GRID',(0,0),(-1,-1),0.5,HexColor('#DDDDDD')),
    ]
    for i in range(1, len(insp2)):
        is2.append(('BACKGROUND',(0,i),(-1,i), BG1 if i%2==0 else BG2))
    t_i2.setStyle(TableStyle(is2))
    els.append(t_i2); els.append(Spacer(1,3*mm))

    sh('PERFORMANCE & REPROGRAMACIÓN ECU')
    perf2 = [
        [
            p('<font color="#888888" size="7"><b>ECU ORIGINAL LEÍDA</b></font><br/>'
              '<font color="#228844" size="9">☐ SÍ</font>  <font color="#CC0000" size="9">☐ NO</font>',
              ps('pe2a',color=DARK,leading=13)),
            p('<font color="#888888" size="7"><b>BACKUP REALIZADO</b></font><br/>'
              '<font color="#228844" size="9">☐ SÍ</font>  <font color="#CC0000" size="9">☐ NO</font>',
              ps('pe2b',color=DARK,leading=13)),
            mf('MAPA / CALIBRACIÓN APLICADA'),
            mf('HERRAMIENTA / SOFTWARE'),
        ],
        [
            p('<font color="#888888" size="7"><b>POTENCIA ORIGINAL</b></font><br/>'
              '<font color="#333333" size="10">_______ HP  /  _______ Nm</font>',
              ps('hp2a',color=DARK,leading=13)),
            p('<font color="#888888" size="7"><b>POTENCIA FINAL (Dyno)</b></font><br/>'
              '<font color="#CC0000" size="13"><b>_______ HP  /  _______ Nm</b></font>',
              ps('hp2b',color=RED,bold=True,leading=16)),
            p('<font color="#888888" size="7"><b>GANANCIA</b></font><br/>'
              '<font color="#CC8800" size="16"><b>+ _______ HP</b></font>',
              ps('hp2c',color=HexColor('#CC8800'),bold=True,leading=19)),
            mf('TÉCNICO RESPONSABLE'),
        ],
    ]
    t_p2 = Table(perf2, colWidths=[c4,c4,c4,c4])
    t_p2.setStyle(TableStyle([
        ('GRID',(0,0),(-1,-1),0.5,HexColor('#DDDDDD')),
        ('LEFTPADDING',(0,0),(-1,-1),8),('RIGHTPADDING',(0,0),(-1,-1),8),
        ('TOPPADDING',(0,0),(-1,-1),6),('BOTTOMPADDING',(0,0),(-1,-1),8),
        ('BACKGROUND',(0,0),(-1,0),BG2),
        ('BACKGROUND',(0,1),(-1,1),BGALT),
        ('LINEABOVE',(0,0),(-1,0),0.5,HexColor('#CCCCCC')),
    ]))
    els.append(t_p2); els.append(Spacer(1,3*mm))

    sh('OBSERVACIONES TÉCNICAS DEL MECÁNICO')
    obs2 = Table([[p(
        '<br/>'.join(['<font color="#DDDDDD" size="8">'+('─'*110)+'</font><br/>'] * 4),
        ps('obs2',color=DARK,leading=18)
    )]], colWidths=[TW])
    obs2.setStyle(TableStyle([
        ('BACKGROUND',(0,0),(-1,-1),BG2),
        ('LEFTPADDING',(0,0),(-1,-1),8),('RIGHTPADDING',(0,0),(-1,-1),8),
        ('TOPPADDING',(0,0),(-1,-1),6),('BOTTOMPADDING',(0,0),(-1,-1),6),
        ('BOX',(0,0),(-1,-1),0.5,HexColor('#CCCCCC')),
    ]))
    els.append(obs2); els.append(Spacer(1,3*mm))

    sh('DETALLE DE TRABAJOS Y PRESUPUESTO')
    ph2 = [
        p('<b><font color="#FFFFFF" size="8">N°</font></b>',  ps('ph20',color=white,bold=True,align=TA_CENTER)),
        p('<b><font color="#FFFFFF" size="8">DESCRIPCIÓN DEL TRABAJO / REPUESTO</font></b>', ps('ph21',color=white,bold=True)),
        p('<b><font color="#FFFFFF" size="8">CANT.</font></b>', ps('ph22',color=white,bold=True,align=TA_CENTER)),
        p('<b><font color="#FFFFFF" size="8">P. UNITARIO</font></b>', ps('ph23',color=white,bold=True,align=TA_RIGHT)),
        p('<b><font color="#FFFFFF" size="8">TOTAL</font></b>', ps('ph24',color=white,bold=True,align=TA_RIGHT)),
    ]
    pr2 = [ph2]
    for i in range(5):
        pr2.append([
            p(f'<font color="#999999" size="8">{i+1:02d}</font>', ps(f'pn2{i}',color=DARK,align=TA_CENTER)),
            p(f'<font color="#DDDDDD" size="8">{"─"*60}</font>', ps(f'pd2{i}',color=DARK)),
            p('<font color="#DDDDDD" size="8">───</font>', ps(f'pc2{i}',color=DARK,align=TA_CENTER)),
            p('<font color="#DDDDDD" size="8">$ ────────</font>', ps(f'pu2{i}',color=DARK,align=TA_RIGHT)),
            p('<font color="#DDDDDD" size="8">$ ────────</font>', ps(f'pt2{i}',color=DARK,align=TA_RIGHT)),
        ])
    pr2 += [
        ['','','', p('<b>SUBTOTAL</b>', ps('sub2',color=MID,bold=True,align=TA_RIGHT)),
                   p('<b>$ ────────────</b>', ps('subv2',color=DARK,bold=True,align=TA_RIGHT))],
        ['','','', p('<b>TOTAL A PAGAR</b>', ps('tot2',color=white,bold=True,align=TA_RIGHT)),
                   p('<b>$ ────────────</b>', ps('totv2',color=white,bold=True,align=TA_RIGHT))],
    ]
    cw2 = [TW*0.05, TW*0.50, TW*0.10, TW*0.18, TW*0.17]
    t_pr2 = Table(pr2, colWidths=cw2)
    ps2_ = [
        ('BACKGROUND',(0,0),(-1,0),DARK),
        ('LEFTPADDING',(0,0),(-1,-1),6),('RIGHTPADDING',(0,0),(-1,-1),6),
        ('TOPPADDING',(0,0),(-1,-1),4),('BOTTOMPADDING',(0,0),(-1,-1),5),
        ('GRID',(0,1),(-1,-3),0.5,HexColor('#DDDDDD')),
        ('BACKGROUND',(0,-2),(-1,-2),HexColor('#F5F5F5')),
        ('BACKGROUND',(0,-1),(-1,-1),DARK),
        ('LINEABOVE',(0,-2),(-1,-2),0.5,HexColor('#CCCCCC')),
        ('LINEABOVE',(0,-1),(-1,-1),2,RED),
        ('SPAN',(0,-2),(2,-2)),('SPAN',(0,-1),(2,-1)),
    ]
    for i in range(1, len(pr2)-2):
        ps2_.append(('BACKGROUND',(0,i),(-1,i), BG1 if i%2==0 else BG2))
    t_pr2.setStyle(TableStyle(ps2_))
    els.append(t_pr2); els.append(Spacer(1,3*mm))

    sh('CONFORMIDAD Y FIRMAS')
    f2 = [[
        p('<font color="#888888" size="7"><b>FIRMA DEL CLIENTE</b></font>'
          '<br/><br/><br/><br/>'
          '<font color="#CC0000">─────────────────────────────</font><br/>'
          '<font color="#888888" size="7">Nombre y aclaración</font>',
          ps('fc2',color=DARK,leading=11,align=TA_CENTER)),
        p('<font color="#888888" size="7"><b>TÉCNICO AGM PERFORMANCE</b></font>'
          '<br/><br/><br/><br/>'
          '<font color="#CC0000">─────────────────────────────</font><br/>'
          '<font color="#888888" size="7">Firma y legajo</font>',
          ps('ft2',color=DARK,leading=11,align=TA_CENTER)),
        p('<font color="#888888" size="7"><b>SELLO OFICIAL DEL TALLER</b></font>'
          '<br/><br/><br/><br/>'
          '<font color="#CC0000">─────────────────────────────</font><br/>'
          '<font color="#888888" size="7">AGM Performance</font>',
          ps('fs2',color=DARK,leading=11,align=TA_CENTER)),
    ]]
    t_f2 = Table(f2, colWidths=[c3,c3,c3])
    t_f2.setStyle(TableStyle([
        ('BACKGROUND',(0,0),(-1,-1),BG2),
        ('GRID',(0,0),(-1,-1),0.5,HexColor('#DDDDDD')),
        ('LEFTPADDING',(0,0),(-1,-1),8),('RIGHTPADDING',(0,0),(-1,-1),8),
        ('TOPPADDING',(0,0),(-1,-1),6),('BOTTOMPADDING',(0,0),(-1,-1),10),
        ('ALIGN',(0,0),(-1,-1),'CENTER'),
        ('VALIGN',(0,0),(-1,-1),'BOTTOM'),
    ]))
    els.append(t_f2)

    doc.build(els, onFirstPage=bg_white, onLaterPages=bg_white)
    print(f'✅ {out}')
    return out


# ─── DISEÑO 3: CARBON PREMIUM ────────────────────────────────────────────────
# Header negro con dorado, cuerpo gris muy claro con líneas azul-acero.
# Estilo premium internacional.

def bg_carbon(c, doc):
    """Callback: diseño carbon premium para Diseño 3."""
    # Fondo blanco roto / gris muy claro
    c.setFillColor(HexColor('#F4F4F4'))
    c.rect(0, 0, W, H, fill=1, stroke=0)
    # Header premium negro
    c.setFillColor(HexColor('#0A0A0A'))
    c.rect(0, H - 43*mm, W, 43*mm, fill=1, stroke=0)
    # Franja dorada bajo header
    c.setFillColor(HexColor('#D4AF37'))
    c.rect(0, H - 44.5*mm, W, 1.5*mm, fill=1, stroke=0)
    # Franja acero delgada
    c.setFillColor(HexColor('#8899AA'))
    c.rect(0, H - 45.2*mm, W, 0.7*mm, fill=1, stroke=0)
    # Logo
    if os.path.exists(LOGO):
        c.drawImage(LOGO, 8*mm, H - 41*mm, width=36*mm, height=30*mm,
                    preserveAspectRatio=True, mask='auto')
    # Título
    c.setFillColor(white)
    c.setFont('Helvetica-Bold', 21)
    c.drawString(49*mm, H - 15*mm, 'AGM PERFORMANCE')
    c.setFillColor(HexColor('#D4AF37'))
    c.setFont('Helvetica-Bold', 10)
    c.drawString(49*mm, H - 22.5*mm, 'SERVICE  ·  CHIPTUNNING  ·  DIAGNÓSTICO')
    # Línea dorada
    c.setFillColor(HexColor('#D4AF37'))
    c.rect(49*mm, H - 24.5*mm, 110*mm, 0.7*mm, fill=1, stroke=0)
    c.setFillColor(HexColor('#AAAAAA'))
    c.setFont('Helvetica', 8.5)
    c.drawString(49*mm, H - 30*mm, 'FICHA DE SERVICE Y DIAGNÓSTICO DE MOTOCICLETAS')
    # Info der
    c.setFillColor(HexColor('#777777'))
    c.setFont('Helvetica', 7.5)
    c.drawRightString(W - 8*mm, H - 13*mm, 'FORM-SRV-001 · Rev.2025')
    c.drawRightString(W - 8*mm, H - 20.5*mm, 'www.agmperformance.com.ar')
    # QR marco dorado
    c.setStrokeColor(HexColor('#D4AF37'))
    c.setLineWidth(1)
    c.rect(W - 28*mm, H - 42*mm, 18*mm, 18*mm, fill=0, stroke=1)
    c.setFillColor(HexColor('#555555'))
    c.setFont('Helvetica-Bold', 5.5)
    c.drawCentredString(W - 19*mm, H - 33*mm, 'CÓDIGO QR')
    c.drawCentredString(W - 19*mm, H - 36*mm, 'DEL TALLER')
    # Barra lateral izquierda dorada
    c.setFillColor(HexColor('#D4AF37'))
    c.rect(0, 0, 3.5, H - 45.2*mm, fill=1, stroke=0)
    # Footer
    c.setFillColor(HexColor('#0A0A0A'))
    c.rect(0, 0, W, 11*mm, fill=1, stroke=0)
    c.setFillColor(HexColor('#D4AF37'))
    c.rect(0, 11*mm, W, 0.8*mm, fill=1, stroke=0)
    c.setFillColor(white)
    c.setFont('Helvetica-Bold', 7)
    c.drawCentredString(W/2, 4*mm,
        'AGM Performance Service Chiptunning  ·  Comprobante de service para el cliente')


def build_design3():
    """Diseño 3: Carbon Premium (negro/dorado/acero)."""
    out = '/home/user/TRAMANONE/DISEÑO3_CarbonPremium.pdf'
    doc = SimpleDocTemplate(out, pagesize=A4,
                            leftMargin=0.9*cm, rightMargin=0.9*cm,
                            topMargin=5.0*cm, bottomMargin=1.6*cm)

    GOLD  = HexColor('#D4AF37')
    DARK  = HexColor('#1A1A1A')
    STEEL = HexColor('#4A6070')
    MID   = HexColor('#555555')
    LGRAY = HexColor('#888888')
    BG1   = HexColor('#FFFFFF')
    BG2   = HexColor('#F0F2F4')
    BGH   = HexColor('#0A0A0A')
    GR    = HexColor('#CCCCCC')

    TW = W - 1.8*cm
    c2 = TW / 2
    c3 = TW / 3
    c4 = TW / 4

    els = []

    def sh(title, sub=''):
        txt = f'<font color="#D4AF37"><b>◆</b></font>  <font color="#FFFFFF"><b>{title}</b></font>'
        if sub: txt += f'  <font size="7" color="#AAAAAA">{sub}</font>'
        t = Table([[p(txt, ps('sh3', size=9.5, color=white, bold=True, leading=13))]],
                  colWidths=[TW])
        t.setStyle(TableStyle([
            ('BACKGROUND',(0,0),(-1,-1), BGH),
            ('TOPPADDING',(0,0),(-1,-1),5),
            ('BOTTOMPADDING',(0,0),(-1,-1),5),
            ('LEFTPADDING',(0,0),(-1,-1),10),
            ('LINEABOVE',(0,0),(-1,0),1.5,GOLD),
            ('LINEBELOW',(0,0),(-1,-1),0.5,STEEL),
        ]))
        els.append(t)
        els.append(Spacer(1, 1.5*mm))

    def mf(label, val=''):
        return p(f'<font color="#777777" size="7"><b>{label}</b></font><br/>'
                 f'<font color="#1A1A1A" size="9">{val or ("─"*38)}</font>',
                 ps('mf3', color=DARK, leading=13))

    def cb(text):
        return p(f'<font color="#D4AF37" size="9">☐</font> '
                 f'<font color="#333333" size="8.5">{text}</font>',
                 ps('cb3', color=DARK, leading=12))

    def stable3(rows, widths):
        t = Table(rows, colWidths=widths)
        styles = [
            ('LEFTPADDING',(0,0),(-1,-1),8),('RIGHTPADDING',(0,0),(-1,-1),8),
            ('TOPPADDING',(0,0),(-1,-1),5),('BOTTOMPADDING',(0,0),(-1,-1),6),
            ('GRID',(0,0),(-1,-1),0.4,GR),
        ]
        for i in range(len(rows)):
            styles.append(('BACKGROUND',(0,i),(-1,i), BG1 if i%2==0 else BG2))
        t.setStyle(TableStyle(styles))
        return t

    # Banda de orden
    ord3 = [[
        p('<font color="#777777" size="7"><b>N° DE ORDEN</b></font><br/>'
          '<font color="#D4AF37" size="22"><b>__________</b></font>',
          ps('ord3', color=DARK, leading=26, bold=True)),
        p('<font color="#777777" size="7"><b>FECHA INGRESO</b></font><br/>'
          '<font color="#1A1A1A" size="11"><b>___ / ___ / ______</b></font>',
          ps('dt3', color=DARK, leading=15)),
        p('<font color="#777777" size="7"><b>HORA</b></font><br/>'
          '<font color="#1A1A1A" size="11"><b>_____ : _____</b></font>',
          ps('hr3', color=DARK, leading=15)),
        p('<font color="#777777" size="7"><b>ENTREGA ESTIMADA</b></font><br/>'
          '<font color="#1A1A1A" size="11"><b>___ / ___ / ______</b></font>',
          ps('ent3', color=DARK, leading=15)),
        p('<font color="#777777" size="7"><b>PRIORIDAD</b></font><br/>'
          '<font color="#D4AF37" size="8">☐ URGENTE</font><br/>'
          '<font color="#228844" size="8">☐ NORMAL</font>',
          ps('pri3', color=DARK, leading=11)),
    ]]
    t_o3 = Table(ord3, colWidths=[TW*0.20, TW*0.22, TW*0.16, TW*0.26, TW*0.16])
    t_o3.setStyle(TableStyle([
        ('BACKGROUND',(0,0),(-1,-1), BG2),
        ('LINEABOVE',(0,0),(-1,0),2,GOLD),
        ('LINEBELOW',(0,0),(-1,-1),2,DARK),
        ('LEFTPADDING',(0,0),(-1,-1),8),('RIGHTPADDING',(0,0),(-1,-1),8),
        ('TOPPADDING',(0,0),(-1,-1),5),('BOTTOMPADDING',(0,0),(-1,-1),6),
        ('VALIGN',(0,0),(-1,-1),'MIDDLE'),
        ('GRID',(0,0),(-1,-1),0.5,GR),
    ]))
    els.append(t_o3); els.append(Spacer(1,3*mm))

    sh('DATOS DEL CLIENTE')
    els.append(stable3([
        [mf('NOMBRE Y APELLIDO'), mf('D.N.I. / C.U.I.T.')],
        [mf('TELÉFONO / CELULAR'), mf('E-MAIL')],
        [mf('DIRECCIÓN'), mf('CIUDAD')],
    ], [c2+5*mm, c2-5*mm])); els.append(Spacer(1,3*mm))

    sh('DATOS DE LA MOTOCICLETA')
    els.append(stable3([
        [mf('MARCA'), mf('MODELO'), mf('AÑO')],
        [mf('DOMINIO / PATENTE'), mf('KILOMETRAJE'), mf('TIPO DE USO')],
        [mf('N° DE CHASIS (VIN)'), mf('N° DE MOTOR'), mf('COLOR')],
    ], [c3,c3,c3])); els.append(Spacer(1,3*mm))

    sh('TRABAJOS SOLICITADOS', '(marcar con ✓)')
    trab_items3 = [
        ['Service General', 'Cambio de Aceite Motor', 'Filtro de Aceite'],
        ['Filtro de Aire', 'Cambio de Bujías', 'Regulación de Válvulas'],
        ['Diagnóstico Electrónico', 'Reprogramación ECU / Mapa', 'Banco de Potencia (Dyno)'],
        ['Control de Frenos', 'Control de Transmisión', 'Control de Suspensiones'],
        ['Revisión Eléctrica', 'Lavado / Detailing', 'Otro: ___________________'],
    ]
    els.append(stable3([[cb(c) for c in row] for row in trab_items3], [c3,c3,c3]))
    els.append(Spacer(1,3*mm))

    sh('INSPECCIÓN TÉCNICA GENERAL')
    items3 = [
        ('Aceite Motor','Pastillas Freno Del.'),
        ('Refrigerante/Liq. Frenos','Pastillas Freno Tras.'),
        ('Kit de Transmisión','Neumático Delantero'),
        ('Neumático Trasero','Batería / Carga'),
        ('Luces','Suspensión Delantera'),
        ('Suspensión Trasera','Filtro de Combustible'),
    ]
    estado3 = ('<font color="#228844" size="8">☐ Bueno</font>  '
               '<font color="#AA6600" size="8">☐ Regular</font>  '
               '<font color="#AA0000" size="8">☐ Cambiar</font>')
    hdr3_row = [
        p('<b><font color="#D4AF37" size="8">COMPONENTE</font></b>', ps('ih3a',color=GOLD,bold=True)),
        p('<b><font color="#D4AF37" size="8">ESTADO</font></b>',     ps('ie3a',color=GOLD,bold=True)),
        p('<b><font color="#D4AF37" size="8">COMPONENTE</font></b>', ps('ih3b',color=GOLD,bold=True)),
        p('<b><font color="#D4AF37" size="8">ESTADO</font></b>',     ps('ie3b',color=GOLD,bold=True)),
    ]
    insp3 = [hdr3_row]
    for l, r in items3:
        insp3.append([
            p(f'<font color="#333333" size="8.5">{l}</font>', ps('il3',color=DARK)),
            p(estado3, ps('ie3x',color=DARK,leading=11)),
            p(f'<font color="#333333" size="8.5">{r}</font>', ps('ir3',color=DARK)),
            p(estado3, ps('ie3y',color=DARK,leading=11)),
        ])
    c_i1 = TW*0.22; c_i2 = TW*0.28
    t_i3 = Table(insp3, colWidths=[c_i1,c_i2,c_i1,c_i2])
    is3 = [
        ('BACKGROUND',(0,0),(-1,0),BGH),
        ('LINEBELOW',(0,0),(-1,0),1,GOLD),
        ('LINEBEFORE',(2,0),(2,-1),0.8,GOLD),
        ('LEFTPADDING',(0,0),(-1,-1),7),('RIGHTPADDING',(0,0),(-1,-1),5),
        ('TOPPADDING',(0,0),(-1,-1),4),('BOTTOMPADDING',(0,0),(-1,-1),4),
        ('GRID',(0,0),(-1,-1),0.4,GR),
    ]
    for i in range(1, len(insp3)):
        is3.append(('BACKGROUND',(0,i),(-1,i), BG1 if i%2==0 else BG2))
    t_i3.setStyle(TableStyle(is3))
    els.append(t_i3); els.append(Spacer(1,3*mm))

    sh('PERFORMANCE & REPROGRAMACIÓN ECU')
    perf3 = [
        [
            p('<font color="#777777" size="7"><b>ECU ORIGINAL LEÍDA</b></font><br/>'
              '<font color="#228844" size="9">☐ SÍ</font>  <font color="#AA0000" size="9">☐ NO</font>',
              ps('pe3a',color=DARK,leading=13)),
            p('<font color="#777777" size="7"><b>BACKUP REALIZADO</b></font><br/>'
              '<font color="#228844" size="9">☐ SÍ</font>  <font color="#AA0000" size="9">☐ NO</font>',
              ps('pe3b',color=DARK,leading=13)),
            mf('MAPA / CALIBRACIÓN APLICADA'),
            mf('HERRAMIENTA / SOFTWARE'),
        ],
        [
            p('<font color="#777777" size="7"><b>POTENCIA ORIGINAL</b></font><br/>'
              '<font color="#333333" size="10">_______ HP  /  _______ Nm</font>',
              ps('hp3a',color=DARK,leading=13)),
            p('<font color="#777777" size="7"><b>POTENCIA FINAL (Dyno)</b></font><br/>'
              '<font color="#AA0000" size="13"><b>_______ HP  /  _______ Nm</b></font>',
              ps('hp3b',color=HexColor('#AA0000'),bold=True,leading=16)),
            p('<font color="#777777" size="7"><b>GANANCIA</b></font><br/>'
              '<font color="#D4AF37" size="16"><b>+ _______ HP</b></font>',
              ps('hp3c',color=GOLD,bold=True,leading=19)),
            mf('TÉCNICO RESPONSABLE'),
        ],
    ]
    t_p3 = Table(perf3, colWidths=[c4,c4,c4,c4])
    t_p3.setStyle(TableStyle([
        ('GRID',(0,0),(-1,-1),0.4,GR),
        ('LEFTPADDING',(0,0),(-1,-1),8),('RIGHTPADDING',(0,0),(-1,-1),8),
        ('TOPPADDING',(0,0),(-1,-1),6),('BOTTOMPADDING',(0,0),(-1,-1),8),
        ('BACKGROUND',(0,0),(-1,0),BG2),
        ('BACKGROUND',(0,1),(-1,1),BG1),
        ('BACKGROUND',(1,1),(1,1),HexColor('#FFF0F0')),
        ('BACKGROUND',(2,1),(2,1),HexColor('#FFFDE8')),
    ]))
    els.append(t_p3); els.append(Spacer(1,3*mm))

    sh('OBSERVACIONES TÉCNICAS DEL MECÁNICO')
    obs3 = Table([[p(
        '<br/>'.join(['<font color="#CCCCCC" size="8">'+('─'*110)+'</font><br/>'] * 4),
        ps('obs3',color=DARK,leading=18)
    )]], colWidths=[TW])
    obs3.setStyle(TableStyle([
        ('BACKGROUND',(0,0),(-1,-1),BG2),
        ('LEFTPADDING',(0,0),(-1,-1),8),('RIGHTPADDING',(0,0),(-1,-1),8),
        ('TOPPADDING',(0,0),(-1,-1),6),('BOTTOMPADDING',(0,0),(-1,-1),6),
        ('BOX',(0,0),(-1,-1),0.5,GR),
    ]))
    els.append(obs3); els.append(Spacer(1,3*mm))

    sh('DETALLE DE TRABAJOS Y PRESUPUESTO')
    ph3 = [
        p('<b><font color="#D4AF37" size="8">N°</font></b>',  ps('ph30',color=GOLD,bold=True,align=TA_CENTER)),
        p('<b><font color="#D4AF37" size="8">DESCRIPCIÓN DEL TRABAJO / REPUESTO</font></b>', ps('ph31',color=GOLD,bold=True)),
        p('<b><font color="#D4AF37" size="8">CANT.</font></b>', ps('ph32',color=GOLD,bold=True,align=TA_CENTER)),
        p('<b><font color="#D4AF37" size="8">P. UNITARIO</font></b>', ps('ph33',color=GOLD,bold=True,align=TA_RIGHT)),
        p('<b><font color="#D4AF37" size="8">TOTAL</font></b>', ps('ph34',color=GOLD,bold=True,align=TA_RIGHT)),
    ]
    pr3 = [ph3]
    for i in range(5):
        pr3.append([
            p(f'<font color="#AAAAAA" size="8">{i+1:02d}</font>', ps(f'pn3{i}',color=DARK,align=TA_CENTER)),
            p(f'<font color="#CCCCCC" size="8">{"─"*60}</font>', ps(f'pd3{i}',color=DARK)),
            p('<font color="#CCCCCC" size="8">───</font>', ps(f'pc3{i}',color=DARK,align=TA_CENTER)),
            p('<font color="#CCCCCC" size="8">$ ────────</font>', ps(f'pu3{i}',color=DARK,align=TA_RIGHT)),
            p('<font color="#CCCCCC" size="8">$ ────────</font>', ps(f'pt3{i}',color=DARK,align=TA_RIGHT)),
        ])
    pr3 += [
        ['','','', p('<b>SUBTOTAL</b>', ps('sub3',color=MID,bold=True,align=TA_RIGHT)),
                   p('<b>$ ────────────</b>', ps('subv3',color=DARK,bold=True,align=TA_RIGHT))],
        ['','','', p('<b><font color="#D4AF37">TOTAL A PAGAR</font></b>', ps('tot3',color=GOLD,bold=True,align=TA_RIGHT)),
                   p('<b><font color="#D4AF37" size="13">$ ────────────</font></b>', ps('totv3',color=GOLD,bold=True,align=TA_RIGHT))],
    ]
    cw3 = [TW*0.05, TW*0.50, TW*0.10, TW*0.18, TW*0.17]
    t_pr3 = Table(pr3, colWidths=cw3)
    ps3_ = [
        ('BACKGROUND',(0,0),(-1,0),BGH),
        ('LINEBELOW',(0,0),(-1,0),1,GOLD),
        ('LEFTPADDING',(0,0),(-1,-1),6),('RIGHTPADDING',(0,0),(-1,-1),6),
        ('TOPPADDING',(0,0),(-1,-1),4),('BOTTOMPADDING',(0,0),(-1,-1),5),
        ('GRID',(0,1),(-1,-3),0.4,GR),
        ('BACKGROUND',(0,-2),(-1,-2),BG2),
        ('BACKGROUND',(0,-1),(-1,-1),BGH),
        ('LINEABOVE',(0,-2),(-1,-2),0.5,GR),
        ('LINEABOVE',(0,-1),(-1,-1),1.5,GOLD),
        ('SPAN',(0,-2),(2,-2)),('SPAN',(0,-1),(2,-1)),
    ]
    for i in range(1, len(pr3)-2):
        ps3_.append(('BACKGROUND',(0,i),(-1,i), BG1 if i%2==0 else BG2))
    t_pr3.setStyle(TableStyle(ps3_))
    els.append(t_pr3); els.append(Spacer(1,3*mm))

    sh('CONFORMIDAD Y FIRMAS')
    f3 = [[
        p('<font color="#777777" size="7"><b>FIRMA DEL CLIENTE</b></font>'
          '<br/><br/><br/><br/>'
          '<font color="#D4AF37">─────────────────────────────</font><br/>'
          '<font color="#888888" size="7">Nombre y aclaración</font>',
          ps('fc3',color=DARK,leading=11,align=TA_CENTER)),
        p('<font color="#777777" size="7"><b>TÉCNICO AGM PERFORMANCE</b></font>'
          '<br/><br/><br/><br/>'
          '<font color="#D4AF37">─────────────────────────────</font><br/>'
          '<font color="#888888" size="7">Firma y legajo</font>',
          ps('ft3',color=DARK,leading=11,align=TA_CENTER)),
        p('<font color="#777777" size="7"><b>SELLO OFICIAL DEL TALLER</b></font>'
          '<br/><br/><br/><br/>'
          '<font color="#D4AF37">─────────────────────────────</font><br/>'
          '<font color="#888888" size="7">AGM Performance</font>',
          ps('fs3',color=DARK,leading=11,align=TA_CENTER)),
    ]]
    t_f3 = Table(f3, colWidths=[c3,c3,c3])
    t_f3.setStyle(TableStyle([
        ('BACKGROUND',(0,0),(-1,-1),BG2),
        ('GRID',(0,0),(-1,-1),0.4,GR),
        ('LEFTPADDING',(0,0),(-1,-1),8),('RIGHTPADDING',(0,0),(-1,-1),8),
        ('TOPPADDING',(0,0),(-1,-1),6),('BOTTOMPADDING',(0,0),(-1,-1),10),
        ('ALIGN',(0,0),(-1,-1),'CENTER'),
        ('VALIGN',(0,0),(-1,-1),'BOTTOM'),
    ]))
    els.append(t_f3)

    doc.build(els, onFirstPage=bg_carbon, onLaterPages=bg_carbon)
    print(f'✅ {out}')
    return out


if __name__ == '__main__':
    os.chdir('/home/user/TRAMANONE')
    build_design1()
    build_design2()
    build_design3()
    print('\n🏁 Los 3 diseños fueron generados correctamente.')
