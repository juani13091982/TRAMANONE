"""Base de datos SQLite para AGM Performance Service."""
import sqlite3
import json
from datetime import date, datetime
from pathlib import Path

DB_PATH = Path(__file__).parent / "agm_service.db"


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    conn = get_conn()
    c = conn.cursor()

    c.executescript("""
    CREATE TABLE IF NOT EXISTS clientes (
        id        INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre    TEXT NOT NULL,
        dni_cuit  TEXT,
        telefono  TEXT,
        email     TEXT,
        direccion TEXT,
        ciudad    TEXT,
        created_at TEXT DEFAULT (datetime('now','localtime'))
    );

    CREATE TABLE IF NOT EXISTS motos (
        id         INTEGER PRIMARY KEY AUTOINCREMENT,
        cliente_id INTEGER NOT NULL,
        marca      TEXT,
        modelo     TEXT,
        anio       INTEGER,
        dominio    TEXT,
        vin        TEXT,
        nro_motor  TEXT,
        color      TEXT,
        FOREIGN KEY (cliente_id) REFERENCES clientes(id)
    );

    CREATE TABLE IF NOT EXISTS servicios (
        id                   INTEGER PRIMARY KEY AUTOINCREMENT,
        numero_orden         TEXT UNIQUE NOT NULL,
        fecha_ingreso        TEXT NOT NULL,
        hora_ingreso         TEXT,
        fecha_entrega_est    TEXT,
        fecha_completado     TEXT,
        prioridad            TEXT DEFAULT 'Normal',
        estado               TEXT DEFAULT 'Pendiente',

        cliente_id           INTEGER NOT NULL,
        moto_id              INTEGER NOT NULL,
        kilometraje          INTEGER,
        tipo_uso             TEXT,

        -- trabajos (0/1)
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
        trab_otro            TEXT,

        -- inspección: 'Bueno' | 'Regular' | 'Cambiar'
        insp_aceite          TEXT,
        insp_refrigerante    TEXT,
        insp_past_del        TEXT,
        insp_past_tras       TEXT,
        insp_transmision     TEXT,
        insp_neum_del        TEXT,
        insp_neum_tras       TEXT,
        insp_bateria         TEXT,
        insp_luces           TEXT,
        insp_susp_del        TEXT,
        insp_susp_tras       TEXT,
        insp_filtro_comb     TEXT,

        -- performance
        ecu_leida            INTEGER DEFAULT 0,
        backup_realizado     INTEGER DEFAULT 0,
        mapa_aplicado        TEXT,
        hp_original          REAL,
        hp_final             REAL,
        nm_original          REAL,
        nm_final             REAL,
        software_herramienta TEXT,
        tecnico              TEXT,

        -- observaciones
        observaciones        TEXT,

        -- presupuesto items: JSON [{"desc":..,"cant":..,"precio":..,"total":..}]
        items_presupuesto    TEXT DEFAULT '[]',
        subtotal             REAL DEFAULT 0,
        total                REAL DEFAULT 0,

        created_at           TEXT DEFAULT (datetime('now','localtime'))
    );
    """)
    conn.commit()
    conn.close()


# ── CLIENTES ──────────────────────────────────────────────────────────────────

def upsert_cliente(nombre, dni_cuit='', telefono='', email='', direccion='', ciudad=''):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT id FROM clientes WHERE nombre=? AND dni_cuit=?", (nombre, dni_cuit))
    row = c.fetchone()
    if row:
        cid = row['id']
        c.execute("""UPDATE clientes SET telefono=?,email=?,direccion=?,ciudad=?
                     WHERE id=?""", (telefono, email, direccion, ciudad, cid))
    else:
        c.execute("""INSERT INTO clientes (nombre,dni_cuit,telefono,email,direccion,ciudad)
                     VALUES (?,?,?,?,?,?)""", (nombre, dni_cuit, telefono, email, direccion, ciudad))
        cid = c.lastrowid
    conn.commit()
    conn.close()
    return cid


def get_clientes():
    conn = get_conn()
    rows = conn.execute("SELECT * FROM clientes ORDER BY nombre").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_cliente(cid):
    conn = get_conn()
    row = conn.execute("SELECT * FROM clientes WHERE id=?", (cid,)).fetchone()
    conn.close()
    return dict(row) if row else None


# ── MOTOS ─────────────────────────────────────────────────────────────────────

def upsert_moto(cliente_id, marca, modelo, anio, dominio, vin='', nro_motor='', color=''):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT id FROM motos WHERE cliente_id=? AND dominio=?", (cliente_id, dominio))
    row = c.fetchone()
    if row:
        mid = row['id']
        c.execute("""UPDATE motos SET marca=?,modelo=?,anio=?,vin=?,nro_motor=?,color=?
                     WHERE id=?""", (marca, modelo, anio, vin, nro_motor, color, mid))
    else:
        c.execute("""INSERT INTO motos (cliente_id,marca,modelo,anio,dominio,vin,nro_motor,color)
                     VALUES (?,?,?,?,?,?,?,?)""",
                  (cliente_id, marca, modelo, anio, dominio, vin, nro_motor, color))
        mid = c.lastrowid
    conn.commit()
    conn.close()
    return mid


def get_motos_cliente(cliente_id):
    conn = get_conn()
    rows = conn.execute("SELECT * FROM motos WHERE cliente_id=?", (cliente_id,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_moto(mid):
    conn = get_conn()
    row = conn.execute("SELECT * FROM motos WHERE id=?", (mid,)).fetchone()
    conn.close()
    return dict(row) if row else None


# ── SERVICIOS ─────────────────────────────────────────────────────────────────

def next_orden():
    conn = get_conn()
    year = datetime.now().year
    c = conn.execute(
        "SELECT COUNT(*) as n FROM servicios WHERE numero_orden LIKE ?",
        (f"AGM-{year}-%",)
    )
    n = c.fetchone()['n'] + 1
    conn.close()
    return f"AGM-{year}-{n:04d}"


def insert_servicio(data: dict) -> int:
    conn = get_conn()
    c = conn.cursor()
    fields = list(data.keys())
    placeholders = ','.join('?' * len(fields))
    values = [data[f] for f in fields]
    sql = f"INSERT INTO servicios ({','.join(fields)}) VALUES ({placeholders})"
    c.execute(sql, values)
    sid = c.lastrowid
    conn.commit()
    conn.close()
    return sid


def update_servicio(sid: int, data: dict):
    conn = get_conn()
    sets = ', '.join(f"{k}=?" for k in data)
    values = list(data.values()) + [sid]
    conn.execute(f"UPDATE servicios SET {sets} WHERE id=?", values)
    conn.commit()
    conn.close()


def get_servicio(sid):
    conn = get_conn()
    row = conn.execute("SELECT * FROM servicios WHERE id=?", (sid,)).fetchone()
    conn.close()
    return dict(row) if row else None


def get_servicios_full(limit=500):
    """Retorna todos los servicios con datos de cliente y moto."""
    conn = get_conn()
    rows = conn.execute("""
        SELECT s.*,
               cl.nombre      AS cliente_nombre,
               cl.telefono    AS cliente_tel,
               cl.email       AS cliente_email,
               m.marca, m.modelo, m.anio, m.dominio, m.color
        FROM servicios s
        JOIN clientes cl ON cl.id = s.cliente_id
        JOIN motos    m  ON m.id  = s.moto_id
        ORDER BY s.fecha_ingreso DESC, s.id DESC
        LIMIT ?
    """, (limit,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_stats():
    """Retorna datos agregados para el dashboard."""
    conn = get_conn()

    servicios_mes = conn.execute("""
        SELECT strftime('%Y-%m', fecha_ingreso) AS mes,
               COUNT(*) AS cantidad,
               SUM(total) AS facturacion
        FROM servicios
        GROUP BY mes ORDER BY mes
    """).fetchall()

    top_clientes = conn.execute("""
        SELECT cl.nombre, COUNT(*) AS servicios, SUM(s.total) AS total
        FROM servicios s JOIN clientes cl ON cl.id=s.cliente_id
        GROUP BY s.cliente_id ORDER BY servicios DESC LIMIT 10
    """).fetchall()

    top_motos = conn.execute("""
        SELECT m.marca, m.modelo, COUNT(*) AS servicios
        FROM servicios s JOIN motos m ON m.id=s.moto_id
        GROUP BY m.marca, m.modelo ORDER BY servicios DESC LIMIT 10
    """).fetchall()

    marcas = conn.execute("""
        SELECT m.marca, COUNT(*) AS cantidad
        FROM servicios s JOIN motos m ON m.id=s.moto_id
        GROUP BY m.marca ORDER BY cantidad DESC
    """).fetchall()

    estados = conn.execute("""
        SELECT estado, COUNT(*) AS n FROM servicios GROUP BY estado
    """).fetchall()

    trabajos_cols = [
        ('trab_service','Service General'), ('trab_aceite','Cambio Aceite'),
        ('trab_filtro_aceite','Filtro Aceite'), ('trab_filtro_aire','Filtro Aire'),
        ('trab_bujias','Bujías'), ('trab_valvulas','Válvulas'),
        ('trab_diagnostico','Diagnóstico'), ('trab_ecu','ECU/Reprog.'),
        ('trab_dyno','Dyno'), ('trab_frenos','Frenos'),
        ('trab_transmision','Transmisión'), ('trab_suspension','Suspensión'),
        ('trab_electrica','Eléctrica'), ('trab_lavado','Lavado'),
    ]
    trabajos_data = []
    for col, label in trabajos_cols:
        row = conn.execute(f"SELECT SUM({col}) as n FROM servicios").fetchone()
        trabajos_data.append({'trabajo': label, 'cantidad': int(row['n'] or 0)})

    kpis = conn.execute("""
        SELECT COUNT(*) as total_servicios,
               COUNT(DISTINCT cliente_id) as total_clientes,
               SUM(total) as facturacion_total,
               SUM(CASE WHEN estado='Completado' THEN 1 ELSE 0 END) as completados,
               SUM(CASE WHEN estado='Pendiente'  THEN 1 ELSE 0 END) as pendientes,
               AVG(hp_final - hp_original) as ganancia_hp_avg
        FROM servicios
    """).fetchone()

    conn.close()
    return {
        'servicios_mes': [dict(r) for r in servicios_mes],
        'top_clientes':  [dict(r) for r in top_clientes],
        'top_motos':     [dict(r) for r in top_motos],
        'marcas':        [dict(r) for r in marcas],
        'estados':       [dict(r) for r in estados],
        'trabajos':      trabajos_data,
        'kpis':          dict(kpis),
    }
