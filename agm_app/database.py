"""
Base de datos AGM Performance Service.
Modo dual: SQLite local  ó  PostgreSQL nube (via DATABASE_URL en secrets).
"""
import os, json
from pathlib import Path
from datetime import datetime
from sqlalchemy import create_engine, text

# ── URL de conexión ───────────────────────────────────────────────────────────
def _db_url():
    url = ""
    try:
        import streamlit as st
        url = st.secrets.get("DATABASE_URL", "")
    except Exception:
        pass
    if not url:
        url = os.environ.get("DATABASE_URL", "")
    if not url:
        url = f"sqlite:///{Path(__file__).parent / 'agm_service.db'}"
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)
    return url

_engine = None

def _get_engine():
    global _engine
    if _engine is None:
        url = _db_url()
        kw = {}
        if "sqlite" in url:
            kw["connect_args"] = {"check_same_thread": False}
        else:
            # Supabase Transaction Pooler (port 6543) ya hace pooling propio;
            # connect_timeout evita que la app quede colgada si la BD está pausada.
            kw["connect_args"] = {"sslmode": "require", "connect_timeout": 10}
        _engine = create_engine(url, echo=False, pool_pre_ping=True, **kw)
    return _engine

def _is_pg():
    url = _db_url()
    return "postgresql" in url or "postgres" in url

def _rows(res):
    keys = list(res.keys())
    return [dict(zip(keys, r)) for r in res.fetchall()]

def _row(res):
    keys = list(res.keys())
    r = res.fetchone()
    return dict(zip(keys, r)) if r else None

def _last_id(conn, table):
    """Obtiene el último id insertado (compatible SQLite y PostgreSQL)."""
    r = _row(conn.execute(text(f"SELECT id FROM {table} ORDER BY id DESC LIMIT 1")))
    return r['id'] if r else None


# ── INIT DB ───────────────────────────────────────────────────────────────────
def init_db():
    pk = "SERIAL PRIMARY KEY" if _is_pg() else "INTEGER PRIMARY KEY AUTOINCREMENT"
    with _get_engine().begin() as conn:
        conn.execute(text(f"""
        CREATE TABLE IF NOT EXISTS clientes (
            id        {pk},
            nombre    TEXT NOT NULL,
            dni_cuit  TEXT DEFAULT '',
            telefono  TEXT DEFAULT '',
            email     TEXT DEFAULT '',
            direccion TEXT DEFAULT '',
            ciudad    TEXT DEFAULT '',
            created_at TEXT
        )"""))
        conn.execute(text(f"""
        CREATE TABLE IF NOT EXISTS motos (
            id         {pk},
            cliente_id INTEGER NOT NULL,
            marca      TEXT DEFAULT '',
            modelo     TEXT DEFAULT '',
            anio       INTEGER,
            dominio    TEXT DEFAULT '',
            vin        TEXT DEFAULT '',
            nro_motor  TEXT DEFAULT '',
            color      TEXT DEFAULT ''
        )"""))
        conn.execute(text(f"""
        CREATE TABLE IF NOT EXISTS servicios (
            id                   {pk},
            numero_orden         TEXT UNIQUE NOT NULL,
            fecha_ingreso        TEXT NOT NULL,
            hora_ingreso         TEXT DEFAULT '',
            fecha_entrega_est    TEXT DEFAULT '',
            fecha_completado     TEXT DEFAULT '',
            prioridad            TEXT DEFAULT 'Normal',
            estado               TEXT DEFAULT 'Pendiente',
            cliente_id           INTEGER NOT NULL,
            moto_id              INTEGER NOT NULL,
            kilometraje          INTEGER DEFAULT 0,
            tipo_uso             TEXT DEFAULT '',
            trab_service         INTEGER DEFAULT 0,
            trab_aceite          INTEGER DEFAULT 0,
            trab_filtro_aceite   INTEGER DEFAULT 0,
            trab_filtro_aire     INTEGER DEFAULT 0,
            trab_bujias          INTEGER DEFAULT 0,
            trab_valvulas        INTEGER DEFAULT 0,
            trab_diagnostico     INTEGER DEFAULT 0,
            trab_ecu             INTEGER DEFAULT 0,
            trab_dyno            INTEGER DEFAULT 0,
            trab_frenos          INTEGER DEFAULT 0,
            trab_transmision     INTEGER DEFAULT 0,
            trab_suspension      INTEGER DEFAULT 0,
            trab_electrica       INTEGER DEFAULT 0,
            trab_lavado          INTEGER DEFAULT 0,
            trab_otro            TEXT DEFAULT '',
            insp_aceite          TEXT DEFAULT '',
            insp_refrigerante    TEXT DEFAULT '',
            insp_past_del        TEXT DEFAULT '',
            insp_past_tras       TEXT DEFAULT '',
            insp_transmision     TEXT DEFAULT '',
            insp_neum_del        TEXT DEFAULT '',
            insp_neum_tras       TEXT DEFAULT '',
            insp_bateria         TEXT DEFAULT '',
            insp_luces           TEXT DEFAULT '',
            insp_susp_del        TEXT DEFAULT '',
            insp_susp_tras       TEXT DEFAULT '',
            insp_filtro_comb     TEXT DEFAULT '',
            ecu_leida            INTEGER DEFAULT 0,
            backup_realizado     INTEGER DEFAULT 0,
            mapa_aplicado        TEXT DEFAULT '',
            hp_original          FLOAT,
            hp_final             FLOAT,
            nm_original          FLOAT,
            nm_final             FLOAT,
            software_herramienta TEXT DEFAULT '',
            tecnico              TEXT DEFAULT '',
            observaciones        TEXT DEFAULT '',
            items_presupuesto    TEXT DEFAULT '[]',
            subtotal             FLOAT DEFAULT 0,
            iva_porcentaje       FLOAT DEFAULT 0,
            iva_monto            FLOAT DEFAULT 0,
            ganancia_total       FLOAT DEFAULT 0,
            total                FLOAT DEFAULT 0,
            created_at           TEXT
        )"""))
    # Migración: cada columna en su propia transacción (PostgreSQL requiere esto)
    for col_def in ["iva_porcentaje FLOAT DEFAULT 0", "iva_monto FLOAT DEFAULT 0",
                    "ganancia_total FLOAT DEFAULT 0"]:
        try:
            with _get_engine().begin() as _conn:
                _conn.execute(text(f"ALTER TABLE servicios ADD COLUMN {col_def}"))
        except Exception:
            pass


# ── CLIENTES ─────────────────────────────────────────────────────────────────
def upsert_cliente(nombre, dni_cuit='', telefono='', email='',
                   direccion='', ciudad=''):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with _get_engine().begin() as conn:
        r = _row(conn.execute(
            text("SELECT id FROM clientes WHERE nombre=:n AND dni_cuit=:d"),
            {"n": nombre, "d": dni_cuit or ''}))
        if r:
            cid = r['id']
            conn.execute(text(
                "UPDATE clientes SET telefono=:t, email=:e, direccion=:di, ciudad=:c WHERE id=:id"),
                {"t": telefono, "e": email, "di": direccion, "c": ciudad, "id": cid})
        else:
            conn.execute(text(
                """INSERT INTO clientes (nombre, dni_cuit, telefono, email, direccion, ciudad, created_at)
                   VALUES (:n, :d, :t, :e, :di, :c, :ca)"""),
                {"n": nombre, "d": dni_cuit, "t": telefono, "e": email,
                 "di": direccion, "c": ciudad, "ca": now})
            r2 = _row(conn.execute(
                text("SELECT id FROM clientes WHERE nombre=:n ORDER BY id DESC LIMIT 1"),
                {"n": nombre}))
            cid = r2['id'] if r2 else None
    return cid

def get_clientes():
    with _get_engine().connect() as conn:
        return _rows(conn.execute(text("SELECT * FROM clientes ORDER BY nombre")))

def get_cliente(cid):
    with _get_engine().connect() as conn:
        return _row(conn.execute(text("SELECT * FROM clientes WHERE id=:id"), {"id": cid}))


# ── MOTOS ─────────────────────────────────────────────────────────────────────
def upsert_moto(cliente_id, marca, modelo, anio, dominio,
                vin='', nro_motor='', color=''):
    with _get_engine().begin() as conn:
        r = _row(conn.execute(
            text("SELECT id FROM motos WHERE cliente_id=:c AND dominio=:d"),
            {"c": cliente_id, "d": dominio or ''}))
        if r:
            mid = r['id']
            conn.execute(text(
                """UPDATE motos SET marca=:ma, modelo=:mo, anio=:a,
                   vin=:v, nro_motor=:nm, color=:co WHERE id=:id"""),
                {"ma": marca, "mo": modelo, "a": anio,
                 "v": vin, "nm": nro_motor, "co": color, "id": mid})
        else:
            conn.execute(text(
                """INSERT INTO motos (cliente_id, marca, modelo, anio, dominio, vin, nro_motor, color)
                   VALUES (:ci, :ma, :mo, :a, :d, :v, :nm, :co)"""),
                {"ci": cliente_id, "ma": marca, "mo": modelo, "a": anio,
                 "d": dominio, "v": vin, "nm": nro_motor, "co": color})
            r2 = _row(conn.execute(
                text("SELECT id FROM motos WHERE dominio=:d ORDER BY id DESC LIMIT 1"),
                {"d": dominio}))
            mid = r2['id'] if r2 else None
    return mid

def get_motos_cliente(cliente_id):
    with _get_engine().connect() as conn:
        return _rows(conn.execute(
            text("SELECT * FROM motos WHERE cliente_id=:c"), {"c": cliente_id}))

def get_moto(mid):
    with _get_engine().connect() as conn:
        return _row(conn.execute(text("SELECT * FROM motos WHERE id=:id"), {"id": mid}))


# ── SERVICIOS ─────────────────────────────────────────────────────────────────
def next_orden():
    year = datetime.now().year
    with _get_engine().connect() as conn:
        r = _row(conn.execute(
            text("SELECT COUNT(*) AS n FROM servicios WHERE numero_orden LIKE :p"),
            {"p": f"AGM-{year}-%"}))
    n = (int(r['n']) if r and r.get('n') else 0) + 1
    return f"AGM-{year}-{n:04d}"

def insert_servicio(data: dict) -> int:
    data = dict(data)
    data.setdefault('created_at', datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    cols = ', '.join(data.keys())
    vals = ', '.join(f':{k}' for k in data.keys())
    orden = data.get('numero_orden', '')
    with _get_engine().begin() as conn:
        conn.execute(text(f"INSERT INTO servicios ({cols}) VALUES ({vals})"), data)
        r = _row(conn.execute(
            text("SELECT id FROM servicios WHERE numero_orden=:o"), {"o": orden}))
    return r['id'] if r else None

def update_servicio(sid: int, data: dict):
    sets = ', '.join(f"{k}=:{k}" for k in data)
    data = dict(data)
    data['_id'] = sid
    with _get_engine().begin() as conn:
        conn.execute(text(f"UPDATE servicios SET {sets} WHERE id=:_id"), data)

def get_servicio(sid):
    with _get_engine().connect() as conn:
        return _row(conn.execute(
            text("SELECT * FROM servicios WHERE id=:id"), {"id": sid}))

def get_servicios_full(limit=500):
    with _get_engine().connect() as conn:
        return _rows(conn.execute(text(f"""
            SELECT s.*,
                   cl.nombre   AS cliente_nombre,
                   cl.telefono AS cliente_tel,
                   cl.email    AS cliente_email,
                   m.marca, m.modelo, m.anio, m.dominio, m.color
            FROM servicios s
            JOIN clientes cl ON cl.id = s.cliente_id
            JOIN motos    m  ON m.id  = s.moto_id
            ORDER BY s.fecha_ingreso DESC, s.id DESC
            LIMIT {int(limit)}
        """)))

def get_stats_clientes():
    """Agrega servicios y facturación por cliente en SQL (evita cargar todos los registros)."""
    with _get_engine().connect() as conn:
        return _rows(conn.execute(text("""
            SELECT cliente_id,
                   COUNT(*) AS servicios,
                   SUM(COALESCE(total,0)) AS facturacion
            FROM servicios
            GROUP BY cliente_id
        """)))

def delete_servicio(sid: int):
    with _get_engine().begin() as conn:
        conn.execute(text("DELETE FROM servicios WHERE id=:id"), {"id": sid})

def get_stats():
    with _get_engine().connect() as conn:
        sm   = _rows(conn.execute(text("""
            SELECT substr(fecha_ingreso,1,7) AS mes,
                   COUNT(*) AS cantidad,
                   SUM(total) AS facturacion,
                   SUM(COALESCE(ganancia_total,0)) AS ganancia
            FROM servicios GROUP BY mes ORDER BY mes""")))
        tc   = _rows(conn.execute(text("""
            SELECT cl.nombre, COUNT(*) AS servicios,
                   SUM(s.total) AS total,
                   SUM(COALESCE(s.ganancia_total,0)) AS ganancia
            FROM servicios s JOIN clientes cl ON cl.id=s.cliente_id
            GROUP BY s.cliente_id, cl.nombre
            ORDER BY servicios DESC LIMIT 10""")))
        tc_gan = _rows(conn.execute(text("""
            SELECT cl.nombre, SUM(COALESCE(s.ganancia_total,0)) AS ganancia
            FROM servicios s JOIN clientes cl ON cl.id=s.cliente_id
            GROUP BY s.cliente_id, cl.nombre
            ORDER BY ganancia DESC LIMIT 10""")))
        tm   = _rows(conn.execute(text("""
            SELECT m.marca, m.modelo, COUNT(*) AS servicios
            FROM servicios s JOIN motos m ON m.id=s.moto_id
            GROUP BY m.marca, m.modelo ORDER BY servicios DESC LIMIT 10""")))
        marc = _rows(conn.execute(text("""
            SELECT m.marca, COUNT(*) AS cantidad
            FROM servicios s JOIN motos m ON m.id=s.moto_id
            GROUP BY m.marca ORDER BY cantidad DESC""")))
        est  = _rows(conn.execute(text(
            "SELECT estado, COUNT(*) AS n FROM servicios GROUP BY estado")))
        kpis = _row(conn.execute(text("""
            SELECT COUNT(*) AS total_servicios,
                   COUNT(DISTINCT cliente_id) AS total_clientes,
                   SUM(total) AS facturacion_total,
                   SUM(COALESCE(ganancia_total,0)) AS ganancia_total,
                   SUM(CASE WHEN estado='Completado' THEN 1 ELSE 0 END) AS completados,
                   SUM(CASE WHEN estado='Pendiente'  THEN 1 ELSE 0 END) AS pendientes,
                   AVG(CASE WHEN hp_final IS NOT NULL AND hp_original IS NOT NULL
                            THEN hp_final - hp_original END) AS ganancia_hp_avg
            FROM servicios""")))
        trab_row = _row(conn.execute(text("""
            SELECT
                COALESCE(SUM(trab_service),0)       AS trab_service,
                COALESCE(SUM(trab_aceite),0)        AS trab_aceite,
                COALESCE(SUM(trab_filtro_aceite),0) AS trab_filtro_aceite,
                COALESCE(SUM(trab_filtro_aire),0)   AS trab_filtro_aire,
                COALESCE(SUM(trab_bujias),0)        AS trab_bujias,
                COALESCE(SUM(trab_valvulas),0)      AS trab_valvulas,
                COALESCE(SUM(trab_diagnostico),0)   AS trab_diagnostico,
                COALESCE(SUM(trab_ecu),0)           AS trab_ecu,
                COALESCE(SUM(trab_dyno),0)          AS trab_dyno,
                COALESCE(SUM(trab_frenos),0)        AS trab_frenos,
                COALESCE(SUM(trab_transmision),0)   AS trab_transmision,
                COALESCE(SUM(trab_suspension),0)    AS trab_suspension,
                COALESCE(SUM(trab_electrica),0)     AS trab_electrica,
                COALESCE(SUM(trab_lavado),0)        AS trab_lavado
            FROM servicios""")))
        trab_labels = [
            ('trab_service','Service General'),('trab_aceite','Cambio Aceite'),
            ('trab_filtro_aceite','Filtro Aceite'),('trab_filtro_aire','Filtro Aire'),
            ('trab_bujias','Bujías'),('trab_valvulas','Válvulas'),
            ('trab_diagnostico','Diagnóstico'),('trab_ecu','ECU/Reprog.'),
            ('trab_dyno','Dyno'),('trab_frenos','Frenos'),
            ('trab_transmision','Transmisión'),('trab_suspension','Suspensión'),
            ('trab_electrica','Eléctrica'),('trab_lavado','Lavado'),
        ]
        trab = [{'trabajo': lbl, 'cantidad': int((trab_row or {}).get(col) or 0)}
                for col, lbl in trab_labels]
    return {
        'servicios_mes': sm, 'top_clientes': tc, 'top_clientes_ganancia': tc_gan,
        'top_motos': tm, 'marcas': marc, 'estados': est, 'trabajos': trab, 'kpis': kpis or {},
    }
