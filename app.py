
"""
WARI FIRE AI — Interfaz interactiva v5.0
Wari Teams · Ayacucho, Perú · NASA International Space Apps Challenge 2026
Desafío: Flame in Freefall
"""

import re
from pathlib import Path
from html import escape

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

# -----------------------------------------------------------------------------
# Configuración general
# -----------------------------------------------------------------------------
BASE = Path(__file__).parent
DATA_DIR = BASE / "data"
LOGO = BASE / "assets" / "logo.png"
CATALOG_FILE = DATA_DIR / "investigaciones.csv"
BASS2_FILE = DATA_DIR / "bass_ii_experimental.csv"
SRC_BASS2 = "NASA PSI · BASS-II · PSI-25_Experimental table_BASS-II.csv"
MAX_TESTS = 20

# Paleta neutra + acentos científicos
WHITE = "#F7F5F2"
SOFT_BG = "#161515"
SOFT_CARD = "#242222"
BORDER = "#4D4B4B"
TEXT = "#F7F5F2"
MUTED = "#D7CFCC"
CHARCOAL = "#333232"
WARM = "#4D4B4B"
BEIGE = "#BAB7B6"
CYAN = "#00D1FF"
ORANGE = "#FF8A00"
GOLD = "#FFC300"
VIOLET = "#A970FF"
GREEN = "#39D98A"
RED = "#FF5A5F"

ACCENTS = [CYAN, ORANGE, GOLD, VIOLET, GREEN]

st.set_page_config(
    page_title="WARI FIRE AI",
    page_icon="🔥",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    f"""
<style>
:root {{
  --bg:{SOFT_BG};
  --card:{WHITE};
  --soft:{SOFT_CARD};
  --border:{BORDER};
  --text:{TEXT};
  --muted:{MUTED};
  --charcoal:{CHARCOAL};
  --warm:{WARM};
  --beige:{BEIGE};
  --cyan:{CYAN};
  --orange:{ORANGE};
  --gold:{GOLD};
  --violet:{VIOLET};
  --green:{GREEN};
  --red:{RED};
}}
html, body, [class*="css"] {{ color:var(--text); }}
[data-testid="stAppViewContainer"] {{ background:var(--bg); }}
.block-container {{ max-width:1280px; padding-top:1.3rem; padding-bottom:3rem; }}
[data-testid="stSidebar"] {{ background:linear-gradient(180deg,#FFFFFF 0%, #F5F1EE 100%); border-right:1px solid var(--border); }}
section[data-testid="stSidebar"] .block-container {{ padding-top:1.1rem; }}
[data-testid="stSidebar"] label, [data-testid="stSidebar"] p, [data-testid="stSidebar"] span, [data-testid="stSidebar"] div {{ color: var(--text); }}
hr {{ border:none; border-top:1px solid var(--border); margin:1rem 0; }}

/* Tarjetas y bloques */
.hero {{
  background:linear-gradient(135deg, rgba(51,50,50,1) 0%, rgba(77,75,75,1) 50%, rgba(0,182,255,0.85) 100%);
  color:white; border-radius:24px; padding:30px 32px; margin-bottom:24px;
  box-shadow: 0 18px 36px rgba(0,0,0,.10); position:relative; overflow:hidden;
}}
.hero::after {{ content:""; position:absolute; inset:auto -40px -40px auto; width:190px; height:190px;
  background:radial-gradient(circle, rgba(255,255,255,.18) 0%, rgba(255,255,255,0) 70%); border-radius:50%; }}
.hero .eyebrow {{ font-size:.78rem; text-transform:uppercase; letter-spacing:.14em; font-weight:800; color:#F5F4F3; }}
.hero h1 {{ margin:.35rem 0 .45rem 0; color:white !important; font-size:clamp(2rem,3.5vw,3.35rem); line-height:1.05; }}
.hero p {{ font-size:1.08rem; line-height:1.7; color:#F4F1EE !important; margin-bottom:.35rem; max-width:920px; }}
.hero-badges {{ margin-top:1rem; display:flex; gap:.5rem; flex-wrap:wrap; }}
.hero-badge {{ background:rgba(255,255,255,.10); border:1px solid rgba(255,255,255,.20); color:white; border-radius:999px; padding:.35rem .7rem; font-size:.8rem; font-weight:700; }}

.section-title {{ margin:0; color:var(--charcoal); font-weight:900; font-size:2rem; }}
.section-subtitle {{ color:var(--muted); margin-top:.25rem; margin-bottom:1rem; line-height:1.6; }}

.card {{ background:var(--card); border:1px solid var(--border); border-radius:18px; padding:18px; box-shadow:0 10px 24px rgba(0,0,0,.25); }}
.card-soft {{ background:linear-gradient(180deg,#242222 0%, #2C2929 100%); border:1px solid var(--border); border-radius:18px; padding:18px; box-shadow:0 10px 24px rgba(0,0,0,.22); }}
.card-accent {{ background:var(--card); border:1px solid var(--border); border-left:6px solid var(--cyan); border-radius:18px; padding:18px; box-shadow:0 10px 24px rgba(0,0,0,.22); color:var(--text); }}
.kpi {{ background:var(--card); border:1px solid var(--border); border-radius:18px; padding:14px 16px; min-height:102px; box-shadow:0 10px 24px rgba(0,0,0,.22); position:relative; overflow:hidden; }}
.kpi::before {{ content:""; position:absolute; left:0; top:0; width:100%; height:5px; background:linear-gradient(90deg, var(--cyan), var(--orange), var(--gold), var(--violet)); }}
.kpi .l {{ color:var(--muted); font-size:.76rem; font-weight:800; letter-spacing:.06em; text-transform:uppercase; }}
.kpi .v {{ color:var(--text); font-size:2rem; font-weight:900; margin-top:.25rem; }}
.kpi .n {{ color:var(--muted); font-size:.85rem; margin-top:.25rem; }}
.info-pill {{ display:inline-block; border-radius:999px; padding:.3rem .7rem; font-size:.78rem; font-weight:700; margin:.18rem .3rem .18rem 0; }}
.pill-cyan{{background:rgba(0,182,255,.12); color:#075c7a; border:1px solid rgba(0,182,255,.25);}}
.pill-orange{{background:rgba(255,122,0,.12); color:#934600; border:1px solid rgba(255,122,0,.25);}}
.pill-gold{{background:rgba(255,183,3,.13); color:#866100; border:1px solid rgba(255,183,3,.25);}}
.pill-violet{{background:rgba(124,77,255,.12); color:#4b34a6; border:1px solid rgba(124,77,255,.25);}}
.pill-green{{background:rgba(47,191,113,.12); color:#1d6a46; border:1px solid rgba(47,191,113,.25);}}
.pill-red{{background:rgba(230,72,77,.1); color:#9a1e26; border:1px solid rgba(230,72,77,.2);}}
.pill-gray{{background:#F2EEEC; color:#4D4B4B; border:1px solid #DDD6D3;}}

.mini-step {{ background:var(--card); border:1px solid var(--border); border-radius:16px; padding:16px; min-height:160px; box-shadow:0 10px 24px rgba(0,0,0,.22); }}
.mini-step .num {{ display:inline-flex; width:32px; height:32px; align-items:center; justify-content:center; border-radius:50%; color:white; font-weight:900; font-size:.95rem; margin-bottom:.6rem; }}
.mini-step h4 {{ margin:.1rem 0 .45rem; color:var(--charcoal); }}
.mini-step p, .mini-step li {{ color:var(--muted); line-height:1.55; font-size:.94rem; }}
.mini-step ul {{ padding-left:1.2rem; margin:.35rem 0 0; }}

.source {{ color:var(--muted); font-size:.85rem; margin:.55rem 0; }}
label, .stMarkdown p, .stMarkdown li, .stCaption, .stText, .st-emotion-cache-10trblm, .st-emotion-cache-16idsys p {{ color: var(--text); }}
h1, h2, h3, h4, h5, h6 {{ color: var(--text) !important; }}
.stSelectbox label, .stMultiSelect label, .stTextInput label, .stTextArea label, .stRadio label {{ color: var(--text) !important; font-weight: 700; }}
[data-baseweb="select"] > div, [data-baseweb="input"] > div, textarea {{ background: #242222 !important; color: var(--text) !important; border:1px solid var(--border)!important; }}
[data-baseweb="select"] * {{ color: var(--text) !important; }}
.stTabs [data-baseweb="tab-panel"] {{ background:transparent; }}
[data-testid="stDataFrame"] {{ border:1px solid var(--border); border-radius:12px; overflow:hidden; }}
[data-testid="stMetric"] {{ background:#242222; border:1px solid var(--border); color:var(--text); }}
.note-box {{ background:rgba(0,182,255,.08); border:1px solid rgba(0,182,255,.2); border-left:5px solid var(--cyan); border-radius:14px; padding:14px 16px; }}
.warn-box {{ background:rgba(255,183,3,.12); border:1px solid rgba(255,183,3,.25); border-left:5px solid var(--gold); border-radius:14px; padding:14px 16px; }}
.danger-box {{ background:rgba(230,72,77,.08); border:1px solid rgba(230,72,77,.2); border-left:5px solid var(--red); border-radius:14px; padding:14px 16px; }}
.success-box {{ background:rgba(47,191,113,.10); border:1px solid rgba(47,191,113,.2); border-left:5px solid var(--green); border-radius:14px; padding:14px 16px; }}

.sidebar-block {{ background:#FFFFFF; border:1px solid var(--border); border-radius:16px; padding:14px; margin-bottom:.9rem; box-shadow:0 4px 12px rgba(0,0,0,.04); }}
.sidebar-title {{ color:var(--charcoal); font-weight:900; margin:.25rem 0; }}
.sidebar-text {{ color:var(--muted); font-size:.9rem; line-height:1.55; }}

/* Widgets */
.stTabs [data-baseweb="tab-list"] {{ gap:.35rem; }}
.stTabs [data-baseweb="tab"] {{ background:#EEE7E2; border-radius:12px 12px 0 0; padding:.55rem .8rem; font-weight:700; color:#4A4543; }}
.stTabs [aria-selected="true"] {{ background:#FFFFFF !important; color:#171717 !important; border-top:3px solid var(--orange); }}
.stMultiSelect [data-baseweb="select"], .stSelectbox [data-baseweb="select"], .stTextInput [data-baseweb="input"], .stTextArea textarea {{ background:white !important; border-radius:12px !important; }}

/* Subtle improvements */
div[data-testid="stMetric"] {{ background:#fff; border:1px solid var(--border); border-radius:14px; padding:10px 12px; }}
#MainMenu, footer {{ visibility: hidden; }}
</style>
""",
    unsafe_allow_html=True,
)


# -----------------------------------------------------------------------------
# Helpers UI
# -----------------------------------------------------------------------------
def show_df(df, **kwargs):
    df = df.copy()
    for c in df.columns:
        if df[c].dtype == object:
            df[c] = df[c].map(lambda v: "" if pd.isna(v) else str(v))
    try:
        st.dataframe(df, width="stretch", hide_index=True, **kwargs)
    except TypeError:
        st.dataframe(df, use_container_width=True, hide_index=True, **kwargs)


def show_plot(fig):
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor=SOFT_CARD,
        plot_bgcolor=SOFT_CARD,
        margin=dict(l=10, r=10, t=50, b=10),
        legend=dict(orientation="h", y=1.12, x=0),
        font=dict(color=TEXT),
        xaxis=dict(gridcolor="#3A3737", linecolor=BORDER, zerolinecolor="#3A3737"),
        yaxis=dict(gridcolor="#3A3737", linecolor=BORDER, zerolinecolor="#3A3737"),
    )
    try:
        st.plotly_chart(fig, width="stretch")
    except TypeError:
        st.plotly_chart(fig, use_container_width=True)


def kpi(col, label, value, note=""):
    col.markdown(
        f'<div class="kpi"><div class="l">{escape(str(label))}</div>'
        f'<div class="v">{escape(str(value))}</div>'
        f'<div class="n">{escape(str(note))}</div></div>',
        unsafe_allow_html=True,
    )


def pill(text, variant="gray"):
    st.markdown(f'<span class="info-pill pill-{variant}">{escape(text)}</span>', unsafe_allow_html=True)


def pills(items):
    html = "".join(f'<span class="info-pill pill-{v}">{escape(t)}</span>' for t, v in items)
    st.markdown(html, unsafe_allow_html=True)


def section_header(title, subtitle=""):
    st.markdown(f'<h2 class="section-title">{escape(title)}</h2>', unsafe_allow_html=True)
    if subtitle:
        st.markdown(f'<p class="section-subtitle">{escape(subtitle)}</p>', unsafe_allow_html=True)


def info_box(text, kind="note"):
    classes = {"note": "note-box", "warn": "warn-box", "danger": "danger-box", "success": "success-box"}
    st.markdown(f'<div class="{classes.get(kind, "note-box")}">{text}</div>', unsafe_allow_html=True)


def step_card(col, n, title, text, bullets, color):
    bullets_html = "".join(f"<li>{escape(b)}</li>" for b in bullets)
    col.markdown(
        f'<div class="mini-step"><div class="num" style="background:{color};">{n}</div>'
        f'<h4>{escape(title)}</h4><p>{escape(text)}</p><ul>{bullets_html}</ul></div>',
        unsafe_allow_html=True,
    )


def source_caption(text=SRC_BASS2):
    st.markdown(f'<div class="source">Fuente: {escape(text)}</div>', unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# Data helpers
# -----------------------------------------------------------------------------
def _tokens(name: str) -> set:
    return set(re.sub(r"[^a-z0-9]+", " ", str(name).lower()).split())


def find_col(df, must=(), none_of=()):
    for c in df.columns:
        t = _tokens(c)
        if all(m in t for m in must) and not any(n in t for n in none_of):
            return c
    return None


STRICT_NUMBER = re.compile(r"^[+-]?(?:\d+(?:[.,]\d*)?|[.,]\d+)$")


def parse_number(value):
    if value is None or pd.isna(value):
        return float("nan"), "vacío"
    raw = str(value).strip()
    if not raw or raw.lower() in {"nan", "none", "n/a", "na", "-", "--", "null"}:
        return float("nan"), "vacío"
    if not STRICT_NUMBER.fullmatch(raw):
        return float("nan"), "ambiguo/no numérico"
    return float(raw.replace(",", ".")), "ok"


@st.cache_data(show_spinner=False)
def load_catalog():
    if not CATALOG_FILE.exists():
        return None
    df = pd.read_csv(CATALOG_FILE)
    required = {"experimento", "area", "combustible", "descripcion", "fuente"}
    if not required.issubset(df.columns):
        return None
    return df


@st.cache_data(show_spinner=False)
def load_bass2():
    if not BASS2_FILE.exists():
        return None, {}
    df = pd.read_csv(BASS2_FILE)
    df.columns = [str(c).strip() for c in df.columns]

    cols = {
        "test": find_col(df, ("test",)),
        "pi": find_col(df, ("pi",)),
        "date": find_col(df, ("date",)),
        "material": find_col(df, ("fuel", "material")),
        "fan": find_col(df, ("fan",)),
        "air": find_col(df, ("air",)),
        "O2_i": find_col(df, ("o2", "initial")),
        "O2_f": find_col(df, ("o2", "final")),
        "CO2_i": find_col(df, ("co2", "initial")),
        "CO2_f": find_col(df, ("co2", "final")),
        "CO_i": find_col(df, ("co", "initial"), none_of=("co2", "o2")),
        "CO_f": find_col(df, ("co", "final"), none_of=("co2", "o2")),
    }
    if cols["test"] is None:
        raise ValueError("No se encontró la columna Test # del CSV BASS-II.")

    df["_test"] = df[cols["test"]].astype(str).str.strip()
    if df["_test"].duplicated().any():
        df["_test_key"] = [f"{t} · fila {i+2}" for i, t in enumerate(df["_test"])]
    else:
        df["_test_key"] = df["_test"]

    for key in ("O2_i", "O2_f", "CO2_i", "CO2_f", "CO_i", "CO_f"):
        c = cols[key]
        if c is None:
            continue
        parsed = df[c].apply(parse_number)
        df[f"{key}_num"] = parsed.apply(lambda x: x[0])
        df[f"{key}_flag"] = parsed.apply(lambda x: x[1])
    return df, cols


def quality_report(df, cols):
    rows = []
    for var in ("O2", "CO2", "CO"):
        for phase, label in (("i", "inicial"), ("f", "final")):
            key = f"{var}_{phase}"
            if cols.get(key) is None:
                continue
            num, flags = df[f"{key}_num"], df[f"{key}_flag"]
            valid = num.dropna()
            if len(valid):
                q1, q3 = valid.quantile(.25), valid.quantile(.75)
                spread = q3 - q1
                lo, hi = q1 - 1.5 * spread, q3 + 1.5 * spread
            else:
                spread = pd.NA
                lo = hi = pd.NA
            for idx in df.index:
                value, flag = num.loc[idx], flags.loc[idx]
                motives = []
                if flag == "vacío":
                    motives.append("Dato ausente")
                elif flag != "ok":
                    motives.append("Texto ambiguo; no se transformó en medición")
                if pd.notna(value):
                    if var in ("O2", "CO2") and not (0 <= value <= 100):
                        motives.append("Fuera del rango 0–100 % vol.")
                    if pd.notna(spread) and spread > 0 and not (lo <= value <= hi):
                        motives.append("Valor estadísticamente atípico (IQR)")
                for motive in motives:
                    rows.append({
                        "Ensayo": df.loc[idx, "_test"],
                        "Variable": f"{var} {label}",
                        "Valor original": df.loc[idx, cols[key]],
                        "Alerta": motive,
                    })
    return pd.DataFrame(rows, columns=["Ensayo", "Variable", "Valor original", "Alerta"])


def test_summary(row):
    parts = []
    if cols.get("material"):
        parts.append(f"Material: {row[cols['material']]}")
    if cols.get("pi"):
        parts.append(f"PI: {row[cols['pi']]}")
    if cols.get("date"):
        parts.append(f"Fecha: {row[cols['date']]}")
    return " · ".join(parts)


# -----------------------------------------------------------------------------
# Data load
# -----------------------------------------------------------------------------
catalog = load_catalog()
bass, cols = load_bass2()
qc = quality_report(bass, cols) if bass is not None else pd.DataFrame()

missing = [p for p, f in (("investigaciones.csv", CATALOG_FILE), ("bass_ii_experimental.csv", BASS2_FILE)) if not f.exists()]

# -----------------------------------------------------------------------------
# Sidebar
# -----------------------------------------------------------------------------
with st.sidebar:
    if LOGO.exists():
        st.image(str(LOGO), width=148)
    st.markdown('<div class="sidebar-title">WARI FIRE AI</div>', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-text">Plataforma didáctica para explorar y comparar investigaciones de combustión en microgravedad con trazabilidad científica.</div>', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-block"><div class="sidebar-title">Módulos</div></div>', unsafe_allow_html=True)
    page = st.radio(
        "Ir a",
        [
            "🏠 Inicio",
            "📚 Biblioteca científica",
            "📈 Explorador BASS-II",
            "⚖️ Comparación científica",
            "🛰️ Seguridad espacial",
            "🧪 Metodología",
        ],
        label_visibility="collapsed",
    )
    st.markdown('<div class="sidebar-block"><div class="sidebar-title">Qué hace la app</div><div class="sidebar-text">• Ordena investigaciones NASA PSI.<br>• Visualiza mediciones BASS-II.<br>• Señala límites y alertas.<br>• Facilita explicar el proyecto al jurado.</div></div>', unsafe_allow_html=True)
    pills([("Datos verificables", "green"), ("Comparaciones", "cyan"), ("Uso educativo", "orange")])
    st.divider()
    st.caption("Wari Teams · Ayacucho, Perú")
    st.caption("NASA Space Apps 2026 · Flame in Freefall")

# -----------------------------------------------------------------------------
# Hero
# -----------------------------------------------------------------------------
st.markdown(
    """
<div class="hero">
  <div class="eyebrow">WARI TEAMS · NASA SPACE APPS CHALLENGE 2026</div>
  <h1>🔥 WARI FIRE AI</h1>
  <p>Convierte datos de combustión en microgravedad en información clara, comparativa y didáctica.
  La app organiza el catálogo NASA PSI, explora la tabla experimental BASS-II y deja explícitos los límites científicos de cada interpretación.</p>
  <div class="hero-badges">
    <span class="hero-badge">Visualización científica</span>
    <span class="hero-badge">Comparación de ensayos</span>
    <span class="hero-badge">Control de calidad</span>
    <span class="hero-badge">Explicación para jurado</span>
  </div>
</div>
""",
    unsafe_allow_html=True,
)

# =============================================================================
# INICIO
# =============================================================================
if page.startswith("🏠"):
    c1, c2, c3, c4 = st.columns(4)
    kpi(c1, "Investigaciones en catálogo", len(catalog) if catalog is not None else "—", "Catálogo general NASA PSI")
    kpi(c2, "Ensayos BASS-II", len(bass) if bass is not None else "—", "Registros experimentales")
    kpi(c3, "Investigadores (PI)", bass[cols["pi"]].nunique() if bass is not None and cols.get("pi") else "—", "Autores de los ensayos")
    kpi(c4, "Hallazgos de calidad", len(qc) if bass is not None else "—", "Alertas automáticas descriptivas")

    st.write("")
    section_header("Resumen rápido de la app", "WARI FIRE AI no inventa resultados: organiza, visualiza y explica datos existentes para apoyar la comprensión de la seguridad contra incendios en el espacio.")
    col_a, col_b = st.columns([1.25, 1])
    with col_a:
        info_box(
            "<b>Funcionamiento general:</b> primero consultas el catálogo de investigaciones; luego exploras ensayos BASS-II; después comparas dos registros; y finalmente revisas qué conclusiones son válidas y cuáles son solo extrapolaciones.",
            "note",
        )
        st.markdown("#### ¿Qué problema resuelve?")
        st.write(
            "Ayuda a que estudiantes, jurados y visitantes entiendan rápidamente qué investiga la NASA sobre combustión en microgravedad, cómo se registran algunas mediciones y qué tan lejos se puede llegar con esas evidencias sin exagerar las conclusiones."
        )
        pills([
            ("Exploración guiada", "cyan"),
            ("Interpretación responsable", "gold"),
            ("Presentación más clara", "violet"),
        ])
    with col_b:
        st.markdown('<div class="card-accent"><h4 style="margin-top:0">Ruta recomendada</h4><ol style="line-height:1.8; color:#5F5A58;"><li>Empieza en <b>Biblioteca científica</b>.</li><li>Continúa con <b>Explorador BASS-II</b>.</li><li>Usa <b>Comparación científica</b> para evidencias lado a lado.</li><li>Cierra con <b>Seguridad espacial</b> y <b>Metodología</b>.</li></ol></div>', unsafe_allow_html=True)

    st.write("")
    step_cols = st.columns(4)
    step_card(step_cols[0], 1, "Biblioteca", "Encuentra estudios y abre la fuente original.", ["Busca BASS, SAME o FLEX", "Filtra por área y combustible"], CYAN)
    step_card(step_cols[1], 2, "Explorador", "Observa registros y variables del ensayo.", ["Elige O₂, CO₂ o CO", "Filtra por PI o material"], ORANGE)
    step_card(step_cols[2], 3, "Comparación", "Contrasta dos ensayos sin inventar causas.", ["Mira coincidencias y diferencias", "Consulta limitaciones"], GOLD)
    step_card(step_cols[3], 4, "Metodología", "Explica al jurado cómo se construyó el análisis.", ["Datos vs cálculos", "Alcances y límites"], VIOLET)

    st.write("")
    section_header("Lo que mejora esta versión", "La interfaz ahora es más visual, más guiada y más útil para una demostración pública.")
    m1, m2, m3 = st.columns(3)
    with m1:
        st.markdown('<div class="card-soft"><h4>Más didáctica</h4><p>Incluye recorridos de uso, resúmenes breves y cajas de interpretación para que cualquiera pueda entender la plataforma.</p></div>', unsafe_allow_html=True)
    with m2:
        st.markdown('<div class="card-soft"><h4>Más interactiva</h4><p>Destaca filtros, comparaciones, descargas y alertas; además mejora la jerarquía visual entre bloques.</p></div>', unsafe_allow_html=True)
    with m3:
        st.markdown('<div class="card-soft"><h4>Más presentable</h4><p>Combina la paleta neutra con colores de acento que hacen la experiencia más viva sin perder seriedad científica.</p></div>', unsafe_allow_html=True)

    if missing:
        info_box("<b>Archivos faltantes:</b> " + ", ".join(missing) + ". Revisa la carpeta <code>data/</code> antes de continuar.", "danger")
    else:
        info_box("<b>Estado:</b> la app tiene los archivos base necesarios y está lista para continuar con la siguiente fase de desarrollo.", "success")

# =============================================================================
# BIBLIOTECA
# =============================================================================
elif page.startswith("📚"):
    section_header("Biblioteca científica", "Explora el catálogo general de investigaciones NASA PSI relacionadas con seguridad contra incendios en el espacio.")
    info_box("<b>Cómo usarla:</b> escribe una palabra clave, filtra por área de seguridad y combustible, y abre la fuente para revisar la investigación original.", "note")

    if catalog is None:
        info_box("No se encontró <code>data/investigaciones.csv</code>.", "danger")
    else:
        c1, c2, c3 = st.columns([2, 1, 1])
        q = c1.text_input("Buscar investigación", placeholder="Ejemplo: BASS, humo, extinción, aerosoles…")
        areas = sorted(catalog["area"].dropna().unique())
        sel_areas = c2.multiselect("Área de seguridad", areas, default=areas)
        fuels = sorted(catalog["combustible"].dropna().unique())
        sel_fuels = c3.multiselect("Combustible", fuels, default=fuels)

        out = catalog.copy()
        if sel_areas:
            out = out[out["area"].isin(sel_areas)]
        if sel_fuels:
            out = out[out["combustible"].isin(sel_fuels)]
        if q:
            mask = out.apply(lambda r: q.lower() in " ".join(map(str, r.values)).lower(), axis=1)
            out = out[mask]

        c1, c2, c3 = st.columns(3)
        kpi(c1, "Resultados filtrados", len(out), "Investigaciones visibles")
        kpi(c2, "Áreas activas", len(sel_areas), "Prevención, detección, supresión")
        kpi(c3, "Combustibles activos", len(sel_fuels), "Tipos de materiales")

        cfg = {"fuente": st.column_config.LinkColumn("fuente", display_text="Abrir fuente")} if "fuente" in out.columns else {}
        show_df(out, column_config=cfg)
        source_caption("Catálogo del equipo Wari Teams elaborado a partir de NASA PSI")
        pills([("Datos de catálogo", "green"), ("Fuentes consultables", "cyan")])

# =============================================================================
# EXPLORADOR BASS-II
# =============================================================================
elif page.startswith("📈"):
    section_header("Explorador BASS-II", "Visualiza ensayos experimentales, filtra registros y comprende mejor qué datos fueron medidos y cuáles solo pueden calcularse.")
    info_box("<b>Uso recomendado:</b> selecciona un investigador o material, elige la variable de interés y luego interpreta el gráfico junto con la ficha del ensayo y el control de calidad.", "note")

    if bass is None:
        info_box("No se encontró <code>data/bass_ii_experimental.csv</code>.", "danger")
        st.stop()

    # filtros globales
    with st.sidebar:
        st.markdown('<div class="sidebar-block"><div class="sidebar-title">Filtros BASS-II</div></div>', unsafe_allow_html=True)
        pis = sorted(bass[cols["pi"]].dropna().astype(str).unique()) if cols.get("pi") else []
        sel_pi = st.multiselect("Investigador principal", pis, default=pis)
        txt = st.text_input("Material contiene", placeholder="PMMA, film, cotton…")

    f = bass.copy()
    if cols.get("pi") and sel_pi:
        f = f[f[cols["pi"]].astype(str).isin(sel_pi)]
    if txt and cols.get("material"):
        f = f[f[cols["material"]].astype(str).str.contains(txt, case=False, na=False)]

    if f.empty:
        info_box("No hay ensayos con esos filtros. Modifica el investigador o el material.", "warn")
        st.stop()

    s1, s2, s3 = st.columns(3)
    kpi(s1, "Ensayos visibles", len(f), "Después de filtros")
    kpi(s2, "PI visibles", f[cols["pi"]].nunique() if cols.get("pi") else "—", "Autores en pantalla")
    kpi(s3, "Identificadores", f["_test"].nunique(), "Test # únicos")

    tab_graf, tab_ficha, tab_qc, tab_tabla = st.tabs(["📊 Gráficos por ensayo", "🧾 Ficha de ensayo", "🛠️ Control de calidad", "📋 Tabla original"])

    with tab_graf:
        avail = [v for v in ("O2", "CO2", "CO") if cols.get(f"{v}_i") and cols.get(f"{v}_f")]
        if not avail:
            info_box("No se detectaron pares válidos de columnas para O₂, CO₂ o CO.", "danger")
            st.stop()

        var_labels = {
            "O2": ("Oxígeno (O₂)", "% vol.", CYAN, "Representa el porcentaje volumétrico de oxígeno registrado al inicio y al final del ensayo."),
            "CO2": ("Dióxido de carbono (CO₂)", "% vol.", ORANGE, "Muestra el comportamiento del CO₂ medido al inicio y al final del ensayo."),
            "CO": ("Monóxido de carbono (CO)", "ppm", GOLD, "Indica concentraciones de CO, útiles para interpretar productos de combustión."),
        }
        v1, v2 = st.columns([1.2, 2.2])
        with v1:
            var = st.radio("Variable a visualizar", avail, horizontal=True, format_func=lambda x: var_labels[x][0])
            st.markdown(f'<div class="card-soft"><h4 style="margin-top:0">¿Qué estás viendo?</h4><p>{escape(var_labels[var][3])}</p><p><b>Unidad:</b> {escape(var_labels[var][1])}</p></div>', unsafe_allow_html=True)
        with v2:
            tests = f["_test_key"].tolist()
            default = tests[: min(8, len(tests))]
            chosen = st.multiselect(f"Ensayos a comparar (máx. {MAX_TESTS})", tests, default=default)

        if len(chosen) > MAX_TESTS:
            st.warning(f"Se mostrarán solo los primeros {MAX_TESTS} ensayos seleccionados.")
            chosen = chosen[:MAX_TESTS]

        sub = f[f["_test_key"].isin(chosen)]
        ok = sub.dropna(subset=[f"{var}_i_num", f"{var}_f_num"], how="all")
        excluded = len(sub) - len(ok)
        if excluded:
            info_box(f"{excluded} ensayo(s) seleccionados no tienen medición numérica utilizable para {var_labels[var][0]}.", "warn")
        if ok.empty:
            info_box("Selecciona ensayos con mediciones numéricas disponibles.", "warn")
        else:
            fig = go.Figure()
            fig.add_bar(x=ok["_test_key"], y=ok[f"{var}_i_num"], name="Inicial", marker_color=var_labels[var][2])
            fig.add_bar(x=ok["_test_key"], y=ok[f"{var}_f_num"], name="Final", marker_color=CHARCOAL)
            fig.update_layout(
                barmode="group",
                title=f"{var_labels[var][0]} inicial vs. final",
                xaxis_title="Identificador del ensayo",
                yaxis_title=var_labels[var][1],
                xaxis=dict(type="category"),
            )
            show_plot(fig)

            d1, d2, d3 = st.columns(3)
            avg_i = round(ok[f"{var}_i_num"].dropna().mean(), 3) if ok[f"{var}_i_num"].notna().any() else "—"
            avg_f = round(ok[f"{var}_f_num"].dropna().mean(), 3) if ok[f"{var}_f_num"].notna().any() else "—"
            delta = round((ok[f"{var}_f_num"] - ok[f"{var}_i_num"]).dropna().mean(), 3) if (ok[f"{var}_f_num"] - ok[f"{var}_i_num"]).notna().any() else "—"
            kpi(d1, "Promedio inicial", avg_i, var_labels[var][1])
            kpi(d2, "Promedio final", avg_f, var_labels[var][1])
            kpi(d3, "Δ promedio", delta, "final − inicial")

            calc = ok[["_test_key"]].rename(columns={"_test_key": "Ensayo"}).copy()
            calc["Inicial"] = ok[f"{var}_i_num"].values
            calc["Final"] = ok[f"{var}_f_num"].values
            calc["Diferencia (final − inicial)"] = (calc["Final"] - calc["Inicial"]).round(3)
            st.markdown("#### Tabla de diferencias")
            show_df(calc)
            source_caption()
            pills([("Dato medido", "green"), ("Diferencia calculada", "gold")])
            st.download_button(
                "⬇️ Descargar tabla filtrada (CSV)",
                calc.to_csv(index=False).encode("utf-8"),
                file_name=f"wari_bass2_{var}.csv",
                mime="text/csv",
            )

    with tab_ficha:
        t = st.selectbox("Selecciona un ensayo", f["_test_key"].tolist())
        row = bass[bass["_test_key"] == t].iloc[0]
        a, b, c = st.columns(3)
        kpi(a, "Material", row[cols["material"]] if cols.get("material") else "—", "Muestra o material")
        kpi(b, "Investigador", row[cols["pi"]] if cols.get("pi") else "—", "PI responsable")
        kpi(c, "Fecha", row[cols["date"]] if cols.get("date") else "—", "Registro del ensayo")

        st.markdown(f'<div class="card-soft"><h4 style="margin-top:0">Resumen del ensayo</h4><p>{escape(test_summary(row))}</p></div>', unsafe_allow_html=True)
        rows = []
        for v in ("O2", "CO2", "CO"):
            if cols.get(f"{v}_i") and cols.get(f"{v}_f"):
                a_num, b_num = row[f"{v}_i_num"], row[f"{v}_f_num"]
                rows.append({
                    "Variable": v,
                    "Inicial (original)": row[cols[f"{v}_i"]],
                    "Final (original)": row[cols[f"{v}_f"]],
                    "Diferencia calculada": round(b_num - a_num, 3) if pd.notna(a_num) and pd.notna(b_num) else "No disponible",
                })
        show_df(pd.DataFrame(rows))
        hall = qc[qc["Ensayo"] == row["_test"]] if not qc.empty else qc
        if len(hall):
            info_box("<b>Hallazgos de calidad detectados:</b> este ensayo contiene una o más alertas automáticas descriptivas. Revísalas antes de comunicar una conclusión.", "warn")
            show_df(hall)
        else:
            info_box("No se detectaron alertas automáticas para este ensayo. Eso no equivale a validación científica completa.", "success")
        source_caption()

    with tab_qc:
        info_box("<b>Importante:</b> los valores no se corrigen ni se eliminan. Las alertas ayudan a revisar el archivo, no a afirmar que existe un error físico real.", "warn")
        if qc.empty:
            info_box("No se detectaron hallazgos de calidad.", "success")
        else:
            motivos = sorted(qc["Alerta"].unique())
            sel = st.multiselect("Filtrar por tipo de alerta", motivos, default=motivos)
            qcf = qc[qc["Alerta"].isin(sel)]
            c1, c2 = st.columns(2)
            kpi(c1, "Alertas visibles", len(qcf), "Filtradas por usuario")
            kpi(c2, "Tipos de alerta", len(sel), "Categorías activas")
            show_df(qcf)
            st.download_button(
                "⬇️ Descargar hallazgos (CSV)",
                qc.to_csv(index=False).encode("utf-8"),
                file_name="wari_bass2_control_calidad.csv",
                mime="text/csv",
            )
            source_caption()
            pills([("Resultado calculado", "gold"), ("Dato no disponible", "gray")])

    with tab_tabla:
        original_cols = [str(c).strip() for c in pd.read_csv(BASS2_FILE, nrows=0).columns]
        show_df(f[original_cols])
        source_caption()
        info_box("Esta tabla conserva la información original filtrada por investigador y material. Sirve para contrastar cualquier resumen con el archivo de base.", "note")

# =============================================================================
# COMPARACIÓN CIENTÍFICA
# =============================================================================
elif page.startswith("⚖️"):
    section_header("Comparación científica", "Compara dos ensayos BASS-II lado a lado para identificar coincidencias, diferencias y límites de interpretación.")
    info_box("<b>Regla de oro:</b> esta sección describe lo que está registrado en dos ensayos; no prueba causas ni jerarquiza materiales sin un análisis experimental adicional.", "note")

    if bass is None:
        info_box("No se encontró <code>data/bass_ii_experimental.csv</code>.", "danger")
        st.stop()

    tests = bass["_test_key"].tolist()
    c1, c2 = st.columns(2)
    ta = c1.selectbox("Ensayo A", tests, index=0)
    tb = c2.selectbox("Ensayo B", tests, index=min(1, len(tests)-1))
    if ta == tb:
        info_box("Elige dos ensayos distintos para comparar.", "warn")
        st.stop()

    ra = bass[bass["_test_key"] == ta].iloc[0]
    rb = bass[bass["_test_key"] == tb].iloc[0]
    original_cols = [str(c).strip() for c in pd.read_csv(BASS2_FILE, nrows=0).columns]

    left, right = st.columns(2)
    left.markdown(f'<div class="card-soft"><h4 style="margin-top:0">Ensayo A</h4><p>{escape(test_summary(ra))}</p></div>', unsafe_allow_html=True)
    right.markdown(f'<div class="card-soft"><h4 style="margin-top:0">Ensayo B</h4><p>{escape(test_summary(rb))}</p></div>', unsafe_allow_html=True)

    iguales, diferentes, faltan = [], [], []
    tabla = []
    for c in original_cols:
        va, vb = ra[c], rb[c]
        na, nb = pd.isna(va), pd.isna(vb)
        if na or nb:
            estado = "Falta dato"
            faltan.append(c)
        elif str(va).strip() == str(vb).strip():
            estado = "Igual"
            iguales.append(c)
        else:
            estado = "Diferente"
            diferentes.append(c)
        tabla.append({"Variable": c, f"A ({ta})": va, f"B ({tb})": vb, "Estado": estado})

    c1, c2, c3 = st.columns(3)
    kpi(c1, "Campos iguales", len(iguales), "Coinciden exactamente")
    kpi(c2, "Campos diferentes", len(diferentes), "No tienen el mismo valor")
    kpi(c3, "Campos incompletos", len(faltan), "Al menos un dato ausente")

    show_df(pd.DataFrame(tabla))
    source_caption()

    st.markdown("#### Comparación numérica de cambios")
    comp = []
    for v in ("O2", "CO2", "CO"):
        if cols.get(f"{v}_i") and cols.get(f"{v}_f"):
            da = ra[f"{v}_f_num"] - ra[f"{v}_i_num"]
            db = rb[f"{v}_f_num"] - rb[f"{v}_i_num"]
            comp.append({
                "Variable": v,
                "Δ Ensayo A": round(da, 3) if pd.notna(da) else "No disponible",
                "Δ Ensayo B": round(db, 3) if pd.notna(db) else "No disponible",
                "Δ B − Δ A": round(db - da, 3) if pd.notna(da) and pd.notna(db) else "—",
            })
    comp_df = pd.DataFrame(comp)
    show_df(comp_df)
    pills([("Descripción comparativa", "cyan"), ("Operación aritmética", "gold")])

    left, right = st.columns(2)
    with left:
        info_box("<b>Sí se puede concluir:</b><br>• qué variables están registradas en ambos ensayos;<br>• si un valor final es mayor o menor que el inicial;<br>• qué campos del CSV son iguales o diferentes.", "success")
    with right:
        info_box("<b>No se puede concluir directamente:</b><br>• qué material es más seguro en general;<br>• causalidad física solo por una diferencia numérica;<br>• comportamiento bajo gravedad lunar o marciana a partir de microgravedad.", "danger")

# =============================================================================
# SEGURIDAD ESPACIAL
# =============================================================================
elif page.startswith("🛰️"):
    section_header("Seguridad espacial", "Conecta las investigaciones del catálogo con escenarios de aplicación, dejando claros los límites de extrapolación.")
    esc = st.selectbox(
        "Selecciona un escenario",
        ["Estación espacial en órbita (microgravedad)", "Hábitat lunar", "Hábitat marciano"],
    )
    if esc.startswith("Estación"):
        info_box("Este escenario es el más cercano a las condiciones de microgravedad usadas en varias investigaciones del catálogo.", "success")
    else:
        info_box("Los resultados de microgravedad no se transfieren de forma directa a gravedad lunar o marciana. Esta sección solo orienta qué estudios podrían servir como punto de partida.", "warn")

    if catalog is None:
        info_box("No se encontró <code>data/investigaciones.csv</code>.", "danger")
    else:
        cards = st.columns(3)
        for i, area in enumerate(sorted(catalog["area"].dropna().unique())):
            sub = catalog[catalog["area"] == area]
            cards[i % 3].markdown(
                f'<div class="card-soft"><h4 style="margin-top:0">{escape(area)}</h4><p style="color:#5F5A58">{len(sub)} investigación(es) asociadas a esta línea de seguridad.</p></div>',
                unsafe_allow_html=True,
            )
        st.write("")
        for area in sorted(catalog["area"].dropna().unique()):
            with st.expander(f"{area}", expanded=True):
                sub = catalog[catalog["area"] == area]
                cfg = {"fuente": st.column_config.LinkColumn("fuente", display_text="Abrir fuente")} if "fuente" in sub.columns else {}
                show_df(sub, column_config=cfg)

    st.markdown("#### Lectura responsable")
    a, b = st.columns(2)
    with a:
        info_box("<b>Útil para:</b><br>• identificar estudios por prevención, detección y supresión;<br>• elegir referencias para el pitch;<br>• justificar por qué el problema es relevante para la seguridad espacial.", "note")
    with b:
        info_box("<b>No sustituye:</b><br>• ensayos en gravedad lunar o marciana;<br>• certificaciones de materiales;<br>• modelos de predicción de incendios reales.", "danger")

# =============================================================================
# METODOLOGÍA
# =============================================================================
else:
    section_header("Metodología y límites científicos", "Explica cómo se construyó la aplicación y cómo deben interpretarse sus resultados frente a un jurado o un usuario externo.")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<div class="card-soft"><h4 style="margin-top:0">¿Cómo funciona la app?</h4><ol style="color:#5F5A58; line-height:1.75;"><li>Carga un catálogo de investigaciones y una tabla experimental BASS-II.</li><li>Detecta columnas relevantes de forma flexible.</li><li>Usa solo mediciones numéricas claras para cálculos.</li><li>Separa datos originales, operaciones y extrapolaciones.</li></ol></div>', unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="card-soft"><h4 style="margin-top:0">¿Qué se corrigió en esta versión?</h4><ul style="color:#5F5A58; line-height:1.75;"><li>Mejor jerarquía visual.</li><li>Más color y navegación más clara.</li><li>Explicaciones breves por módulo.</li><li>Resumen funcional para el jurado.</li></ul></div>', unsafe_allow_html=True)

    st.markdown("#### Clasificación de resultados")
    pills([
        ("Dato experimental", "green"),
        ("Resultado calculado", "gold"),
        ("Interpretación", "cyan"),
        ("Extrapolación", "violet"),
        ("Dato no disponible", "gray"),
    ])
    st.write("")
    info_box("<b>Dato experimental:</b> medición registrada en la fuente.<br><b>Resultado calculado:</b> operación como final − inicial.<br><b>Interpretación:</b> explicación respaldada por el registro.<br><b>Extrapolación:</b> aplicación tentativa a otro contexto.<br><b>Dato no disponible:</b> no pudo verificarse o no existe en el archivo.", "note")
    info_box("<b>Reglas del tratamiento de datos:</b> no se imputan valores faltantes; no se convierten textos ambiguos en números; los atípicos se marcan pero no se eliminan; y los fan/air display no se leen como velocidad física sin calibración documentada.", "warn")
    st.markdown("#### Fuentes base")
    st.markdown(
        "- NASA Physical Sciences Informatics (PSI)\n"
        "- Tabla experimental BASS-II: <code>PSI-25_Experimental table_BASS-II.csv</code>\n"
        "- Repositorio público del proyecto: <code>github.com/stevenlaime17-stack/wari-fire-ai</code>",
        unsafe_allow_html=True,
    )
    st.caption("Equipo: Wari Teams · Ayacucho, Perú · NASA International Space Apps Challenge 2026")
