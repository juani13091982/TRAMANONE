"""Genera el PDF de la Ficha de Service (Diseño 2: Professional White) desde un servicio."""
import os, json
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm, mm
from reportlab.lib.colors import HexColor, white, black
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.pdfgen import canvas as pdfcanvas

LOGO = os.path.join(os.path.dirname(__file__), 'logo.jpg')
W, H = A4

RED   = HexColor('#CC0000')
DARK  = HexColor('#1A1A1A')
LG    = HexColor('#888888')
BG1   = HexColor('#FFFFFF')
BG2   = HexColor('#F9F9F9')
GR    = HexColor('#DDDDDD')


def ps(name, font='Helvetica', size=8, color=black, align=TA_LEFT, leading=None, bold=False):
    return ParagraphStyle(name,
        fontName='Helvetica-Bold' if bold else font,
        fontSize=size, textColor=color,
        alignment=align, leading=leading or size + 3)


def p(text, style): return Paragraph(text, style)


def bg_white(c, doc, srv):
    c.setFillColor(white)
    c.rect(0, 0, W, H, fill=1, stroke=0)
    c.setFillColor(HexColor('#1A1A1A'))
    c.rect(0, H - 40*mm, W, 40*mm, fill=1, stroke=0)
    c.setFillColor(RED)
    c.rect(0, H - 41.5*mm, W, 1.5*mm, fill=1, stroke=0)
    if os.path.exists(LOGO):
        c.drawImage(LOGO, 8*mm, H - 38*mm, width=34*mm, height=28*mm,
                    preserveAspectRatio=True, mask='auto')
    c.setFillColor(white)
    c.setFont('Helvetica-Bold', 20)
    c.drawString(47*mm, H - 14*mm, 'AGM PERFORMANCE')
    c.setFillColor(RED)
    c.setFont('Helvetica-Bold', 9.5)
    c.drawString(47*mm, H - 21*mm, 'SERVICE  ·  CHIPTUNNING  ·  DIAGNÓSTICO')
    c.setFillColor(HexColor('#AAAAAA'))
    c.setFont('Helvetica', 8.5)
    c.drawString(47*mm, H - 28.5*mm, 'FICHA DE SERVICE Y DIAGNÓSTICO DE MOTOCICLETAS')
    c.setFillColor(HexColor('#AAAAAA'))
    c.setFont('Helvetica', 7.5)
    c.drawRightString(W - 8*mm, H - 12*mm, f'FORM N° {srv.get("numero_orden","---")}')
    c.drawRightString(W - 8*mm, H - 19.5*mm, 'www.agmperformance.com.ar')
    # Grid lines
    c.setStrokeColor(HexColor('#F0F0F0'))
    c.setLineWidth(0.5)
    for y in range(int(H - 50*mm), int(13*mm), -6):
        c.line(8*mm, y, W - 8*mm, y)
    # Footer
    c.setFillColor(RED)
    c.rect(0, 0, W, 10*mm, fill=1, stroke=0)
    c.setFillColor(white)
    c.setFont('Helvetica-Bold', 7)
    c.drawCentredString(W/2, 3.5*mm,
        'AGM Performance Service Chiptunning  ·  Comprobante de service para el cliente')


def mf(label, val=''):
    return p(f'<font color="#888888" size="7"><b>{label}</b></font><br/>'
             f'<font color="#222222" size="9">{val or "─" * 32}</font>',
             ps('mf_pdf', color=DARK, leading=13))


def cb_check(text, checked=False):
    mark = '☑' if checked else '☐'
    color = '#CC0000' if checked else '#CC0000'
    return p(f'<font color="{color}" size="9">{mark}</font> '
             f'<font color="#333333" size="8.5">{text}</font>',
             ps('cb_pdf', color=DARK, leading=12))


def insp_estado(val):
    opts = {'Bueno': ('#228844', 'Bueno'), 'Regular': ('#CC8800', 'Regular'),
            'Cambiar': ('#CC0000', 'Cambiar'), 'Reparar': ('#CC0000', 'Reparar')}
    color, label = opts.get(val, ('#BBBBBB', val or '─'))
    return p(f'<font color="{color}" size="9"><b>{label}</b></font>',
             ps('ie_pdf', color=DARK, leading=11))


def sh(title, TW):
    t = Table([[p(f'<font color="#FFFFFF"><b>{title}</b></font>',
                  ps('sh_pdf', size=9.5, color=white, bold=True, leading=13))]],
              colWidths=[TW])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0),(-1,-1), DARK),
        ('TOPPADDING', (0,0),(-1,-1), 5), ('BOTTOMPADDING',(0,0),(-1,-1),5),
        ('LEFTPADDING',(0,0),(-1,-1),10),
        ('LINEABOVE',(0,0),(-1,0),1.5,RED),
    ]))
    return t


def stable(rows, widths):
    t = Table(rows, colWidths=widths)
    styles = [
        ('LEFTPADDING',(0,0),(-1,-1),7), ('RIGHTPADDING',(0,0),(-1,-1),7),
        ('TOPPADDING',(0,0),(-1,-1),5),  ('BOTTOMPADDING',(0,0),(-1,-1),6),
        ('GRID',(0,0),(-1,-1),0.5,GR),  ('LINEBELOW',(0,-1),(-1,-1),1,RED),
    ]
    for i in range(len(rows)):
        styles.append(('BACKGROUND',(0,i),(-1,i), BG1 if i%2==0 else BG2))
    t.setStyle(TableStyle(styles))
    return t


def generate_pdf(srv: dict, cliente: dict, moto: dict, output_path: str):
    """
    srv     – dict del servicio (row de BD)
    cliente – dict del cliente
    moto    – dict de la moto
    output_path – ruta destino del PDF
    """
    doc = SimpleDocTemplate(output_path, pagesize=A4,
                            leftMargin=1.0*cm, rightMargin=1.0*cm,
                            topMargin=4.5*cm, bottomMargin=1.5*cm)

    TW = W - 2*cm
    c2 = TW / 2
    c3 = TW / 3
    c4 = TW / 4
    els = []

    # Callback con datos del servicio inyectados
    def _bg(c, doc): bg_white(c, doc, srv)

    # ── ORDEN ────────────────────────────────────────────────────────
    ord_row = [[
        p(f'<font color="#888888" size="7"><b>N° DE ORDEN</b></font><br/>'
          f'<font color="#CC0000" size="18"><b>{srv.get("numero_orden","")}</b></font>',
          ps('ord_p', color=DARK, leading=22, bold=True)),
        p(f'<font color="#888888" size="7"><b>FECHA INGRESO</b></font><br/>'
          f'<font color="#222222" size="11"><b>{srv.get("fecha_ingreso","")}</b></font>',
          ps('dt_p', color=DARK, leading=15)),
        p(f'<font color="#888888" size="7"><b>HORA</b></font><br/>'
          f'<font color="#222222" size="11"><b>{srv.get("hora_ingreso","")}</b></font>',
          ps('hr_p', color=DARK, leading=15)),
        p(f'<font color="#888888" size="7"><b>ENTREGA ESTIMADA</b></font><br/>'
          f'<font color="#222222" size="11"><b>{srv.get("fecha_entrega_est","")}</b></font>',
          ps('ent_p', color=DARK, leading=15)),
        p(f'<font color="#888888" size="7"><b>PRIORIDAD</b></font><br/>'
          f'<font color="#CC0000" size="9"><b>{srv.get("prioridad","Normal")}</b></font>',
          ps('pri_p', color=DARK, leading=13)),
    ]]
    t_ord = Table(ord_row, colWidths=[TW*0.20, TW*0.22, TW*0.16, TW*0.26, TW*0.16])
    t_ord.setStyle(TableStyle([
        ('BACKGROUND',(0,0),(-1,-1), HexColor('#F5F5F5')),
        ('LINEABOVE',(0,0),(-1,0),2,RED), ('LINEBELOW',(0,0),(-1,-1),2,DARK),
        ('LEFTPADDING',(0,0),(-1,-1),8),  ('RIGHTPADDING',(0,0),(-1,-1),8),
        ('TOPPADDING',(0,0),(-1,-1),5),   ('BOTTOMPADDING',(0,0),(-1,-1),6),
        ('VALIGN',(0,0),(-1,-1),'MIDDLE'), ('GRID',(0,0),(-1,-1),0.5,GR),
    ]))
    els += [t_ord, Spacer(1,3*mm)]

    # ── CLIENTE ───────────────────────────────────────────────────────
    els.append(sh('DATOS DEL CLIENTE', TW))
    els.append(Spacer(1,1.5*mm))
    els.append(stable([
        [mf('NOMBRE Y APELLIDO', cliente.get('nombre','')),
         mf('D.N.I. / C.U.I.T.', cliente.get('dni_cuit',''))],
        [mf('TELÉFONO / CELULAR', cliente.get('telefono','')),
         mf('E-MAIL', cliente.get('email',''))],
        [mf('DIRECCIÓN', cliente.get('direccion','')),
         mf('CIUDAD', cliente.get('ciudad',''))],
    ], [c2+5*mm, c2-5*mm]))
    els.append(Spacer(1,3*mm))

    # ── MOTO ──────────────────────────────────────────────────────────
    els.append(sh('DATOS DE LA MOTOCICLETA', TW))
    els.append(Spacer(1,1.5*mm))
    els.append(stable([
        [mf('MARCA', moto.get('marca','')),
         mf('MODELO', moto.get('modelo','')),
         mf('AÑO', str(moto.get('anio','') or ''))],
        [mf('DOMINIO / PATENTE', moto.get('dominio','')),
         mf('KILOMETRAJE', str(srv.get('kilometraje','') or '')),
         mf('TIPO DE USO', srv.get('tipo_uso',''))],
        [mf('N° DE CHASIS (VIN)', moto.get('vin','')),
         mf('N° DE MOTOR', moto.get('nro_motor','')),
         mf('COLOR', moto.get('color',''))],
    ], [c3,c3,c3]))
    els.append(Spacer(1,3*mm))

    # ── TRABAJOS ──────────────────────────────────────────────────────
    els.append(sh('TRABAJOS SOLICITADOS', TW))
    els.append(Spacer(1,1.5*mm))
    trab_map = [
        ('trab_service','Service General'), ('trab_aceite','Cambio de Aceite Motor'),
        ('trab_filtro_aceite','Filtro de Aceite'), ('trab_filtro_aire','Filtro de Aire'),
        ('trab_bujias','Cambio de Bujías'), ('trab_valvulas','Regulación de Válvulas'),
        ('trab_diagnostico','Diagnóstico Electrónico'), ('trab_ecu','Reprogramación ECU'),
        ('trab_dyno','Banco de Potencia (Dyno)'), ('trab_frenos','Control de Frenos'),
        ('trab_transmision','Control de Transmisión'), ('trab_suspension','Control Suspensiones'),
        ('trab_electrica','Revisión Eléctrica'), ('trab_lavado','Lavado / Detailing'),
        (None, f'Otro: {srv.get("trab_otro","") or ""}'),
    ]
    rows = []
    chunk = [trab_map[i:i+3] for i in range(0, len(trab_map), 3)]
    for group in chunk:
        r = []
        for key, label in group:
            checked = bool(srv.get(key, 0)) if key else bool(srv.get('trab_otro',''))
            r.append(cb_check(label, checked))
        while len(r) < 3: r.append(p('', ps('empty')))
        rows.append(r)
    t_trab = Table(rows, colWidths=[c3,c3,c3])
    t_trab.setStyle(TableStyle([
        ('LEFTPADDING',(0,0),(-1,-1),10), ('RIGHTPADDING',(0,0),(-1,-1),8),
        ('TOPPADDING',(0,0),(-1,-1),4),   ('BOTTOMPADDING',(0,0),(-1,-1),4),
        ('GRID',(0,0),(-1,-1),0.5,GR),
        *[('BACKGROUND',(0,i),(-1,i), BG1 if i%2==0 else BG2) for i in range(len(rows))]
    ]))
    els += [t_trab, Spacer(1,3*mm)]

    # ── INSPECCIÓN ────────────────────────────────────────────────────
    els.append(sh('INSPECCIÓN TÉCNICA GENERAL', TW))
    els.append(Spacer(1,1.5*mm))
    insp_items = [
        ('Aceite Motor',            'insp_aceite',       'Pastillas Freno Del.',   'insp_past_del'),
        ('Refrigerante/Liq. Fr.',   'insp_refrigerante', 'Pastillas Freno Tras.',  'insp_past_tras'),
        ('Kit de Transmisión',      'insp_transmision',  'Neumático Delantero',    'insp_neum_del'),
        ('Neumático Trasero',       'insp_neum_tras',    'Batería / Carga',        'insp_bateria'),
        ('Luces',                   'insp_luces',        'Suspensión Delantera',   'insp_susp_del'),
        ('Suspensión Trasera',      'insp_susp_tras',    'Filtro de Combustible',  'insp_filtro_comb'),
    ]
    hdr_i = [
        p('<b><font color="#FFFFFF" size="8">COMPONENTE</font></b>', ps('ihw',color=white,bold=True)),
        p('<b><font color="#FFFFFF" size="8">ESTADO</font></b>',     ps('iew',color=white,bold=True)),
        p('<b><font color="#FFFFFF" size="8">COMPONENTE</font></b>', ps('ihw2',color=white,bold=True)),
        p('<b><font color="#FFFFFF" size="8">ESTADO</font></b>',     ps('iew2',color=white,bold=True)),
    ]
    insp_rows = [hdr_i]
    for lname, lkey, rname, rkey in insp_items:
        insp_rows.append([
            p(f'<font color="#333333" size="8.5">{lname}</font>', ps('il_p',color=DARK)),
            insp_estado(srv.get(lkey,'')),
            p(f'<font color="#333333" size="8.5">{rname}</font>', ps('ir_p',color=DARK)),
            insp_estado(srv.get(rkey,'')),
        ])
    c_i = TW*0.22; c_e = TW*0.28
    t_i = Table(insp_rows, colWidths=[c_i,c_e,c_i,c_e])
    is_ = [
        ('BACKGROUND',(0,0),(-1,0),DARK), ('LINEBELOW',(0,0),(-1,0),1,RED),
        ('LINEBEFORE',(2,0),(2,-1),0.8,RED),
        ('LEFTPADDING',(0,0),(-1,-1),7),  ('RIGHTPADDING',(0,0),(-1,-1),5),
        ('TOPPADDING',(0,0),(-1,-1),4),   ('BOTTOMPADDING',(0,0),(-1,-1),4),
        ('GRID',(0,0),(-1,-1),0.5,GR),
        *[('BACKGROUND',(0,i),(-1,i), BG1 if i%2==0 else BG2) for i in range(1,len(insp_rows))],
    ]
    t_i.setStyle(TableStyle(is_))
    els += [t_i, Spacer(1,3*mm)]

    # ── PERFORMANCE ───────────────────────────────────────────────────
    ecu_s  = '☑ SÍ' if srv.get('ecu_leida')  else '☐ SÍ  ☑ NO' if srv.get('ecu_leida')==0 else '☐'
    bkp_s  = '☑ SÍ' if srv.get('backup_realizado') else '☐'
    hp_o   = srv.get('hp_original') or ''
    hp_f   = srv.get('hp_final') or ''
    nm_o   = srv.get('nm_original') or ''
    nm_f   = srv.get('nm_final') or ''
    ganancia = ''
    if hp_o and hp_f:
        try: ganancia = f'+{float(hp_f)-float(hp_o):.1f} HP'
        except: pass

    els.append(sh('PERFORMANCE & REPROGRAMACIÓN ECU', TW))
    els.append(Spacer(1,1.5*mm))
    perf = [
        [
            p(f'<font color="#888888" size="7"><b>ECU ORIGINAL LEÍDA</b></font><br/>'
              f'<font color="#228844" size="9">{"☑" if srv.get("ecu_leida") else "☐"} SÍ</font>  '
              f'<font color="#CC0000" size="9">{"☑" if not srv.get("ecu_leida") else "☐"} NO</font>',
              ps('pe_p',color=DARK,leading=13)),
            p(f'<font color="#888888" size="7"><b>BACKUP REALIZADO</b></font><br/>'
              f'<font color="#228844" size="9">{"☑" if srv.get("backup_realizado") else "☐"} SÍ</font>  '
              f'<font color="#CC0000" size="9">{"☑" if not srv.get("backup_realizado") else "☐"} NO</font>',
              ps('pb_p',color=DARK,leading=13)),
            mf('MAPA / CALIBRACIÓN', srv.get('mapa_aplicado','')),
            mf('HERRAMIENTA / SOFTWARE', srv.get('software_herramienta','')),
        ],
        [
            p(f'<font color="#888888" size="7"><b>POTENCIA ORIGINAL</b></font><br/>'
              f'<font color="#333333" size="10">{hp_o} HP  /  {nm_o} Nm</font>',
              ps('hpo_p',color=DARK,leading=13)),
            p(f'<font color="#888888" size="7"><b>POTENCIA FINAL (Dyno)</b></font><br/>'
              f'<font color="#CC0000" size="12"><b>{hp_f} HP  /  {nm_f} Nm</b></font>',
              ps('hpf_p',color=RED,bold=True,leading=15)),
            p(f'<font color="#888888" size="7"><b>GANANCIA</b></font><br/>'
              f'<font color="#CC8800" size="14"><b>{ganancia or "─"}</b></font>',
              ps('hpg_p',color=HexColor('#CC8800'),bold=True,leading=17)),
            mf('TÉCNICO RESPONSABLE', srv.get('tecnico','')),
        ],
    ]
    t_p = Table(perf, colWidths=[c4,c4,c4,c4])
    t_p.setStyle(TableStyle([
        ('GRID',(0,0),(-1,-1),0.5,GR),
        ('LEFTPADDING',(0,0),(-1,-1),8), ('RIGHTPADDING',(0,0),(-1,-1),8),
        ('TOPPADDING',(0,0),(-1,-1),6),  ('BOTTOMPADDING',(0,0),(-1,-1),8),
        ('BACKGROUND',(0,0),(-1,0),BG2), ('BACKGROUND',(0,1),(-1,1),HexColor('#FFF5F5')),
    ]))
    els += [t_p, Spacer(1,3*mm)]

    # ── OBSERVACIONES ────────────────────────────────────────────────
    obs_text = srv.get('observaciones','') or ''
    els.append(sh('OBSERVACIONES TÉCNICAS', TW))
    els.append(Spacer(1,1.5*mm))
    obs_t = Table([[p(obs_text or '─'*80,
                      ps('obs_p', color=DARK, leading=14, size=9))]],
                  colWidths=[TW])
    obs_t.setStyle(TableStyle([
        ('BACKGROUND',(0,0),(-1,-1),BG2),
        ('LEFTPADDING',(0,0),(-1,-1),10), ('RIGHTPADDING',(0,0),(-1,-1),10),
        ('TOPPADDING',(0,0),(-1,-1),8),   ('BOTTOMPADDING',(0,0),(-1,-1),20),
        ('BOX',(0,0),(-1,-1),0.5,GR),
    ]))
    els += [obs_t, Spacer(1,3*mm)]

    # ── PRESUPUESTO ───────────────────────────────────────────────────
    items = json.loads(srv.get('items_presupuesto','[]') or '[]')
    els.append(sh('DETALLE DE TRABAJOS Y PRESUPUESTO', TW))
    els.append(Spacer(1,1.5*mm))
    ph = [
        p('<b><font color="#FFFFFF" size="8">N°</font></b>',  ps('ph0p',color=white,bold=True,align=TA_CENTER)),
        p('<b><font color="#FFFFFF" size="8">DESCRIPCIÓN</font></b>',                  ps('ph1p',color=white,bold=True)),
        p('<b><font color="#FFFFFF" size="8">CANT.</font></b>',  ps('ph2p',color=white,bold=True,align=TA_CENTER)),
        p('<b><font color="#FFFFFF" size="8">P. UNIT.</font></b>',  ps('ph3p',color=white,bold=True,align=TA_RIGHT)),
        p('<b><font color="#FFFFFF" size="8">TOTAL</font></b>',  ps('ph4p',color=white,bold=True,align=TA_RIGHT)),
    ]
    pr = [ph]
    for i, it in enumerate(items):
        pr.append([
            p(f'<font color="#999999" size="8">{i+1:02d}</font>',  ps(f'pn{i}',color=DARK,align=TA_CENTER)),
            p(f'<font color="#333333" size="8.5">{it.get("desc","")}</font>', ps(f'pd{i}',color=DARK)),
            p(f'<font color="#333333" size="8.5">{it.get("cant","")}</font>', ps(f'pc{i}',color=DARK,align=TA_CENTER)),
            p(f'<font color="#333333" size="8.5">$ {it.get("precio","")}</font>', ps(f'pu{i}',color=DARK,align=TA_RIGHT)),
            p(f'<font color="#333333" size="8.5">$ {it.get("total","")}</font>', ps(f'pt{i}',color=DARK,align=TA_RIGHT)),
        ])
    # Rellenar hasta 5 filas mínimo
    for i in range(len(items), 5):
        pr.append([
            p(f'<font color="#CCCCCC" size="8">{i+1:02d}</font>', ps(f'pne{i}',color=DARK,align=TA_CENTER)),
            p('<font color="#EEEEEE" size="8">'+('─'*50)+'</font>', ps(f'pde{i}',color=DARK)),
            p('<font color="#EEEEEE" size="8">─</font>', ps(f'pce{i}',color=DARK,align=TA_CENTER)),
            p('<font color="#EEEEEE" size="8">$ ──</font>', ps(f'pue{i}',color=DARK,align=TA_RIGHT)),
            p('<font color="#EEEEEE" size="8">$ ──</font>', ps(f'pte{i}',color=DARK,align=TA_RIGHT)),
        ])
    subtotal  = float(srv.get('subtotal', 0) or 0)
    iva_pct   = float(srv.get('iva_porcentaje', 0) or 0)
    iva_monto = float(srv.get('iva_monto', 0) or 0)
    total     = float(srv.get('total', 0) or 0)

    pr.append(['','','',
        p('<b>SUBTOTAL</b>', ps('sub_p',color=LG,bold=True,align=TA_RIGHT)),
        p(f'<b>$ {subtotal:,.2f}</b>', ps('subv_p',color=DARK,bold=True,align=TA_RIGHT))])
    if iva_pct > 0:
        pr.append(['','','',
            p(f'<b>IVA ({iva_pct:.0f}%)</b>', ps('iva_p',color=LG,bold=True,align=TA_RIGHT)),
            p(f'<b>$ {iva_monto:,.2f}</b>', ps('ivav_p',color=DARK,bold=True,align=TA_RIGHT))])
    pr.append(['','','',
        p('<b>TOTAL A PAGAR</b>', ps('tot_p',color=white,bold=True,align=TA_RIGHT)),
        p(f'<b>$ {total:,.2f}</b>', ps('totv_p',color=white,bold=True,align=TA_RIGHT))])

    cw = [TW*0.05, TW*0.50, TW*0.10, TW*0.18, TW*0.17]
    t_pr = Table(pr, colWidths=cw)
    n_footer = 2 if iva_pct > 0 else 1  # filas de totales al final (sin contar TOTAL)
    ps_ = [
        ('BACKGROUND',(0,0),(-1,0),DARK), ('LINEBELOW',(0,0),(-1,0),1,RED),
        ('LEFTPADDING',(0,0),(-1,-1),6),  ('RIGHTPADDING',(0,0),(-1,-1),6),
        ('TOPPADDING',(0,0),(-1,-1),4),   ('BOTTOMPADDING',(0,0),(-1,-1),5),
        ('GRID',(0,1),(-1,-(n_footer+2)),0.5,GR),
        ('BACKGROUND',(0,-1),(-1,-1),DARK),
        ('LINEABOVE',(0,-1),(-1,-1),2,RED),
        ('SPAN',(0,-1),(2,-1)),
        *[('BACKGROUND',(0,-i-2),(-1,-i-2), HexColor('#F5F5F5')) for i in range(n_footer)],
        *[('SPAN',(0,-i-2),(2,-i-2)) for i in range(n_footer)],
        *[('BACKGROUND',(0,i),(-1,i), BG1 if i%2==0 else BG2) for i in range(1,len(pr)-n_footer-1)],
    ]
    t_pr.setStyle(TableStyle(ps_))
    els += [t_pr, Spacer(1,3*mm)]

    # ── FIRMAS ────────────────────────────────────────────────────────
    els.append(sh('CONFORMIDAD Y FIRMAS', TW))
    els.append(Spacer(1,1.5*mm))
    f = [[
        p('<font color="#888888" size="7"><b>FIRMA DEL CLIENTE</b></font>'
          '<br/><br/><br/><br/>'
          '<font color="#CC0000">─────────────────────────────</font><br/>'
          f'<font color="#888888" size="7">{cliente.get("nombre","")}</font>',
          ps('fc_p',color=DARK,leading=11,align=TA_CENTER)),
        p('<font color="#888888" size="7"><b>TÉCNICO AGM PERFORMANCE</b></font>'
          '<br/><br/><br/><br/>'
          '<font color="#CC0000">─────────────────────────────</font><br/>'
          f'<font color="#888888" size="7">{srv.get("tecnico","")}</font>',
          ps('ft_p',color=DARK,leading=11,align=TA_CENTER)),
        p('<font color="#888888" size="7"><b>SELLO OFICIAL DEL TALLER</b></font>'
          '<br/><br/><br/><br/>'
          '<font color="#CC0000">─────────────────────────────</font><br/>'
          '<font color="#888888" size="7">AGM Performance Service</font>',
          ps('fs_p',color=DARK,leading=11,align=TA_CENTER)),
    ]]
    t_f = Table(f, colWidths=[c3,c3,c3])
    t_f.setStyle(TableStyle([
        ('BACKGROUND',(0,0),(-1,-1),BG2),
        ('GRID',(0,0),(-1,-1),0.5,GR),
        ('LEFTPADDING',(0,0),(-1,-1),8), ('RIGHTPADDING',(0,0),(-1,-1),8),
        ('TOPPADDING',(0,0),(-1,-1),6),  ('BOTTOMPADDING',(0,0),(-1,-1),10),
        ('ALIGN',(0,0),(-1,-1),'CENTER'), ('VALIGN',(0,0),(-1,-1),'BOTTOM'),
    ]))
    els.append(t_f)

    doc.build(els, onFirstPage=_bg, onLaterPages=_bg)
