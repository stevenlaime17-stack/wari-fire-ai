
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
from simulator import render_simulator
from assistant_evidence import render_assistant
from reports import render_reports
from jury_demo import render_jury_demo

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
WHITE = "#FFFFFF"
SOFT_BG = "#070B16"
SOFT_CARD = "#101A2A"
BORDER = "#344961"
TEXT = "#F6F9FF"
MUTED = "#D0DEED"
CHARCOAL = "#17263A"
WARM = "#33455A"
BEIGE = "#BAB7B6"
CYAN = "#46D9FF"
ORANGE = "#FF9D62"
GOLD = "#FFCF67"
VIOLET = "#C0A2FF"
GREEN = "#6DE5AE"
RED = "#FF818F"

ACCENTS = [CYAN, ORANGE, GOLD, VIOLET, GREEN]

st.set_page_config(
    page_title="WARI FIRE AI",
    page_icon="🔥",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
<style>
:root {
  --space:#070b16; --panel:#101a2a; --panel-hi:#17263a; --border:#33455a;
  --text:#f6f9ff; --muted:#d0deed; --cyan:#46d9ff; --gold:#ffcf67;
  --orange:#ff9d62; --violet:#c0a2ff; --green:#6de5ae; --red:#ff818f;
}
/* Cielo nocturno: puntos estelares discretos, completamente estáticos.
   El patrón va en el fondo, nunca encima de los controles. */
[data-testid="stAppViewContainer"] {
  color: var(--text);
  background-color: var(--space) !important;
  background-image:
    radial-gradient(circle, rgba(255,255,255,.62) 1px, transparent 1.5px),
    radial-gradient(circle, rgba(255,255,255,.38) 1px, transparent 1.6px),
    radial-gradient(circle, rgba(128,204,255,.40) 1px, transparent 1.7px),
    radial-gradient(ellipse at 85% 5%, rgba(23,77,136,.32), transparent 52%),
    linear-gradient(145deg,#070b16 5%,#0a1323 54%,#09101b 100%) !important;
  background-size: 171px 163px, 239px 211px, 317px 283px, cover, cover;
  background-position: 17px 13px, 78px 116px, 151px 37px, center, center;
  background-attachment: fixed;
}
[data-testid="stAppViewContainer"] > .main {background:transparent;}
.block-container {max-width:1240px;padding-top:1.45rem;padding-bottom:3rem;}
[data-testid="stHeader"] {background:rgba(7,11,22,.93) !important;}
[data-testid="stToolbar"] {color:var(--text);}
[data-testid="stSidebar"] {
  background-color:#0b1423 !important;
  background-image:radial-gradient(circle at 18% 9%,rgba(70,217,255,.12),transparent 35%),
                   linear-gradient(180deg,#111e31 0%,#080f1d 100%) !important;
  border-right:1px solid #31445d;
}
[data-testid="stSidebar"] * {color:var(--text);}
[data-testid="stSidebar"] .stCaption, [data-testid="stSidebar"] small {color:var(--muted) !important;}
[data-testid="stSidebar"] .stRadio label p {color:var(--text) !important;font-size:.96rem;font-weight:650;}
[data-testid="stSidebar"] [role="radiogroup"] label {padding:.25rem .22rem;border-radius:9px;}
[data-testid="stSidebar"] [role="radiogroup"] label:hover {background:rgba(70,217,255,.09);}
[data-testid="stSidebar"] section {background:transparent !important;}
hr {border:0;border-top:1px solid #354459;margin:1.1rem 0;}
h1,h2,h3,h4,h5,h6,.stMarkdown h1,.stMarkdown h2,.stMarkdown h3 {color:var(--text)!important;}
p,li,label,.stCaption,.stMarkdown p,.stMarkdown li {color:var(--text);}
[data-testid="stCaptionContainer"] p {color:var(--muted)!important;}
.section-title {margin:.2rem 0;font-size:clamp(1.5rem,2.5vw,2rem);color:#ffffff!important;font-weight:850;}
.section-subtitle {color:var(--muted)!important;margin:.3rem 0 1.15rem;line-height:1.65;}
.hero {
  color:#fff;
  background:
    radial-gradient(circle at 89% 20%,rgba(70,217,255,.16),transparent 38%),
    linear-gradient(112deg,#101b2c 0%,#11263c 68%,#163e58 100%);
  border:1px solid #355873;border-left:5px solid var(--cyan);
  border-radius:22px;padding:31px 33px;margin-bottom:24px;
  box-shadow:0 15px 44px rgba(0,0,0,.33);position:relative;overflow:hidden;
}
.hero:before {
  content:"";position:absolute;inset:0;pointer-events:none;opacity:.65;
  background-image:radial-gradient(circle,#fff 1px,transparent 1.8px),
                   radial-gradient(circle,#9adfff 1px,transparent 1.8px);
  background-size:129px 113px,181px 163px;background-position:11px 9px,64px 37px;
}
.hero > * {position:relative;z-index:1;}
.hero .eyebrow {font-size:.77rem;letter-spacing:.13em;font-weight:850;color:#c1eaff!important;}
.hero h1 {color:#fff!important;font-size:clamp(2rem,3.6vw,3.2rem);margin:.25rem 0 .7rem;line-height:1.13;}
.hero p {color:#f3f8ff!important;font-size:1.06rem;line-height:1.7;max-width:930px;margin-bottom:.65rem;}
.hero-badges {display:flex;flex-wrap:wrap;gap:.5rem;margin-top:1rem;}
.hero-badge {display:inline-block;background:rgba(5,13,27,.66);border:1px solid #5e8098;
  color:#f6f9ff;border-radius:999px;padding:.35rem .7rem;font-size:.79rem;font-weight:700;}
.card,.card-soft,.card-accent,.mini-step,.kpi,.sidebar-block {
  background:rgba(16,26,42,.96)!important;
  border:1px solid #344961;border-radius:16px;
  box-shadow:0 9px 28px rgba(0,0,0,.22);
  color:var(--text)!important;
}
.card,.card-soft,.card-accent {padding:20px;}
.card-soft {background:linear-gradient(155deg,#111c2d,#17263a)!important;}
.card-accent {border-left:5px solid var(--cyan);}
.card h4,.card-soft h4,.card-accent h4,.mini-step h4 {color:#fff!important;}
.card p,.card li,.card-soft p,.card-soft li,.card-accent p,.card-accent li,.mini-step p,.mini-step li {
  color:var(--muted)!important;line-height:1.65;
}
.kpi {padding:17px 19px;min-height:108px;position:relative;overflow:hidden;}
.kpi:before {content:"";position:absolute;inset:0 0 auto;height:4px;
  background:linear-gradient(90deg,var(--cyan),var(--violet),var(--gold));}
.kpi .l {color:#b4d2ed;font-size:.75rem;font-weight:800;letter-spacing:.06em;text-transform:uppercase;}
.kpi .v {color:#fff;font-size:1.9rem;font-weight:850;margin-top:.27rem;overflow-wrap:anywhere;}
.kpi .n {color:var(--muted);font-size:.83rem;margin-top:.3rem;}
.mini-step {padding:17px;min-height:170px;}
.mini-step .num {display:inline-flex;width:34px;height:34px;align-items:center;justify-content:center;
  background:#1767b9;color:#fff;border-radius:50%;font-weight:900;font-size:.95rem;margin-bottom:.75rem;}
.mini-step p,.mini-step li {font-size:.91rem;}
.mini-step ul {padding-left:1.15rem;margin:.3rem 0 0;}
.sidebar-block {padding:13px 14px;margin:.7rem 0 1rem;background:#15263b!important;}
.sidebar-title {color:#fff!important;font-weight:850;margin:.2rem 0 .45rem;}
.sidebar-text {color:#d1dfec!important;font-size:.89rem;line-height:1.65;}
.source {color:#c2d5e8!important;font-size:.84rem;margin:.6rem 0;}
.info-pill {display:inline-block;border-radius:999px;padding:.32rem .72rem;
  font-size:.79rem;font-weight:750;margin:.2rem .3rem .2rem 0;}
.pill-cyan{color:#a9eeff;background:#13334b;border:1px solid #286888;}
.pill-orange{color:#ffd2aa;background:#3c271b;border:1px solid #916241;}
.pill-gold{color:#ffe2a0;background:#39301b;border:1px solid #857137;}
.pill-violet{color:#ddccff;background:#2a2249;border:1px solid #6a55a6;}
.pill-green{color:#b8f8d6;background:#183c2c;border:1px solid #347f58;}
.pill-red{color:#ffc5ca;background:#472531;border:1px solid #985361;}
.pill-gray{color:#d9e0eb;background:#253040;border:1px solid #586577;}
.note-box,.warn-box,.danger-box,.success-box {
  padding:15px 17px;border-radius:12px;line-height:1.65;color:var(--text)!important;
  background:#16243a;border:1px solid #37516d;
}
.note-box {border-left:5px solid var(--cyan);}
.warn-box {background:#322b1d;border:1px solid #63502c;border-left:5px solid var(--gold);}
.danger-box {background:#38212c;border:1px solid #754353;border-left:5px solid var(--red);}
.success-box {background:#173329;border:1px solid #396b56;border-left:5px solid var(--green);}
.note-box b,.warn-box b,.danger-box b,.success-box b {color:#fff;}
/* Controles: texto visible en todos los estados */
[data-baseweb="input"] > div,[data-baseweb="select"] > div,textarea,
.stTextInput input,.stTextArea textarea {
  background:#172338!important;color:#f7fbff!important;border-color:#516a84!important;
  border-radius:10px!important;
}
[data-baseweb="input"] input,[data-baseweb="select"] input {color:#fff!important;}
input::placeholder,textarea::placeholder {color:#b1c4d9!important;opacity:1!important;}
[data-baseweb="select"] [role="combobox"],[data-baseweb="select"] [role="combobox"] * {
  color:#fff!important;
}
[data-baseweb="tag"] {background:#245d89!important;border:1px solid #468cc0!important;}
[data-baseweb="tag"] * {color:#fff!important;}
[data-baseweb="popover"] {background:#18273b!important;}
[data-baseweb="popover"] li {color:#f5f8ff!important;}
.stButton button,.stDownloadButton button {background:#153c5b;color:#f6fbff!important;
  border:1px solid #36759e;border-radius:10px;font-weight:750;}
.stButton button:hover,.stDownloadButton button:hover {background:#20567e;border-color:#56cfff;}
.stTabs [data-baseweb="tab-list"] {gap:.35rem;flex-wrap:wrap;}
.stTabs [data-baseweb="tab"] {
  background:#18283d!important;color:#e1efff!important;
  border:1px solid #344a62!important;border-radius:10px 10px 0 0;
  padding:.55rem .85rem;font-weight:750;
}
.stTabs [data-baseweb="tab"][aria-selected="true"] {
  background:#234363!important;color:#fff!important;border-top:3px solid var(--cyan)!important;
}
.stTabs [data-baseweb="tab"] p {color:inherit!important;}
.stTabs [data-baseweb="tab-panel"] {background:transparent;}
[data-testid="stDataFrame"] {border:1px solid #42607f;border-radius:11px;overflow:hidden;}
div[data-testid="stMetric"] {background:#142235;border:1px solid #344961;border-radius:12px;padding:10px 14px;}
@media (max-width:850px) {
  .hero {padding:22px 19px;}
  .mini-step {min-height:initial;}
  .block-container {padding-left:1rem;padding-right:1rem;}
}
@media (prefers-reduced-motion:reduce) {*,*:before,*:after {animation:none!important;transition:none!important;}}

/* ETAPA 1 · diseño visual y navegación del producto */
.block-container {max-width:1360px !important;padding-top:1.0rem !important;}
[data-testid="stSidebar"] {background:linear-gradient(180deg,#13171d,#090c12)!important;border-right:1px solid #51505a!important;}
[data-testid="stAppViewContainer"] {
 background-color:#090b10!important;
 background-image:radial-gradient(circle,rgba(255,255,255,.42) 1px,transparent 1.4px),radial-gradient(circle,rgba(255,255,255,.2) 1px,transparent 1.4px),linear-gradient(145deg,#080a0e,#141920 75%,#111318)!important;
 background-size:201px 177px,317px 283px,cover!important;
 background-position:21px 12px,93px 144px,center!important;
}
.hero-v6{position:relative;overflow:hidden;min-height:292px;border-radius:22px;border:1px solid #64616b;
 background:linear-gradient(105deg,rgba(9,12,19,.97) 0%,rgba(25,28,35,.94) 62%,rgba(40,41,48,.94) 100%);
 box-shadow:0 16px 40px #0006;padding:30px 34px;display:flex;align-items:center;}
.hero-v6 .content{position:relative;z-index:3;max-width:67%;}
.hero-v6 .tag{color:#dfdedc;font-size:.73rem;letter-spacing:.14em;font-weight:800;text-transform:uppercase;}
.hero-v6 .headline{color:#fff;font-size:clamp(2.05rem,4.5vw,3.8rem);line-height:1.13;font-weight:900;margin:10px 0 8px;}
.hero-v6 .headline em{font-style:normal;color:#ff914d;}
.hero-v6 p{color:#eae8e5!important;max-width:690px;font-size:1.05rem;line-height:1.66;}
.hero-v6 .orbit{position:absolute;right:-70px;bottom:-220px;width:490px;height:490px;border-radius:50%;
 background:radial-gradient(circle at 44% 25%,#879bb0 0%,#3c556d 18%,#152638 42%,#040a12 67%);
 border:2px solid rgba(181,192,208,.35);box-shadow:0 0 60px rgba(255,255,255,.12),0 0 14px #8eaec5 inset;}
.hero-v6 .orbit:before{content:"";position:absolute;top:-25px;left:-28px;right:-28px;bottom:-25px;border:1px solid #8c9ba555;border-radius:50%;transform:rotate(-25deg) scale(1,.65);}
.hero-v6 .microflame{position:absolute;right:155px;top:45px;font-size:68px;filter:drop-shadow(0 0 20px #ff8e4880);}
.hero-v6 .stars{position:absolute;inset:0;background-image:radial-gradient(circle,#fff 1px,transparent 1.8px),radial-gradient(circle,#bdbdc5 1px,transparent 1.8px);background-size:103px 91px,169px 147px;opacity:.35;}
.accent-top{margin:0;padding:4px 0 12px;color:#e8e5e2;letter-spacing:.15em;font-size:.76rem;font-weight:800;}
.panel-v6{min-height:145px;padding:17px 18px;border:1px solid #55525a;border-radius:15px;background:linear-gradient(135deg,#22242b,#34343b);box-shadow:0 6px 17px #0004;}
.panel-v6 .k{color:#c5c3c3;font-size:.78rem;font-weight:800;text-transform:uppercase;letter-spacing:.04em;}
.panel-v6 .v{font-size:2.1rem;font-weight:900;color:#fff;margin:.5rem 0 .25rem;}
.panel-v6 .small{font-size:.83rem;color:#dedbdd;line-height:1.4;}
.feature-v6{padding:18px 17px;min-height:182px;background:linear-gradient(180deg,#27272d,#181c23);
 border:1px solid #66626a;border-top:3px solid #ff9152;border-radius:16px;color:#fff;box-shadow:0 8px 20px #0005;}
.feature-v6 h4{color:#fff!important;font-size:1.09rem;margin:7px 0!important;}
.feature-v6 p{color:#dedcde!important;font-size:.9rem;line-height:1.6;margin-bottom:5px;}
.feature-v6 .ico{font-size:1.75rem;line-height:1.3;}
.section-v6{color:#fff!important;font-weight:850;margin:24px 0 10px;font-size:1.45rem;}
.v6-progress{background:#20252e;border:1px solid #575862;border-radius:14px;padding:15px 19px;color:#e6e4e5;margin:15px 0;line-height:1.7;}
.v6-progress strong{color:#fff;}
.v6-fine{color:#c1c1c6;font-size:.83rem;}
[data-testid="stSidebar"] [role="radiogroup"] label{padding:5px 8px;border-radius:9px;}
[data-testid="stSidebar"] [role="radiogroup"] label:hover{background:#3e3c43;}
[data-testid="stSidebar"] [role="radiogroup"] label p{color:#fff!important;}
.stButton button{background:#e7e2de!important;color:#171719!important;border:1px solid #eee9e6!important;border-radius:10px!important;font-weight:800!important;}
.stButton button:hover{background:#ffb17f!important;color:#161616!important;}
[data-baseweb="tab"] p{color:#fff!important;}
@media(max-width:820px){.hero-v6{padding:21px;min-height:320px}.hero-v6 .content{max-width:100%}.hero-v6 .orbit{opacity:.18}.hero-v6 .microflame{opacity:.15}.feature-v6{min-height:initial}}
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
        xaxis=dict(gridcolor="#2A3A50", linecolor=BORDER, zerolinecolor="#2A3A50"),
        yaxis=dict(gridcolor="#2A3A50", linecolor=BORDER, zerolinecolor="#2A3A50"),
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
    prefix = "Source" if st.session_state.get("language", "Español") == "English" else "Fuente"
    st.markdown(f'<div class="source">{prefix}: {escape(text)}</div>', unsafe_allow_html=True)


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
# Multilingual user interface — all captions, actions and scientific explanations
# -----------------------------------------------------------------------------
I18N = {
"Español": {
"language":"Idioma / Language", "navigation":"Navegación", "welcome":"Inicio", "library":"Biblioteca NASA", "explorer":"Explorador BASS-II", "compare":"Comparación científica", "space":"Seguridad espacial", "method":"Metodología",
"sidebar_desc":"Plataforma científica para explorar datos NASA PSI y comprender la combustión en microgravedad.","sidebar_help":"Recorrido: Biblioteca → Explorador → Comparación → Seguridad espacial.",
"hero_text":"De datos complejos a evidencia comprensible: explora investigaciones NASA PSI, compara ensayos BASS-II y reconoce los límites de la seguridad contra incendios en el espacio.",
"hero_1":"Datos NASA PSI", "hero_2":"129 ensayos BASS-II", "hero_3":"Análisis trazable", "hero_4":"Prototipo educativo",
"studies":"Investigaciones", "tests":"Ensayos BASS-II", "researchers":"Investigadores", "alerts":"Alertas de calidad", "records":"Registros experimentales", "catalog":"Catálogo inicial", "review":"Requieren revisión; no implican errores", "scientists":"Autores del conjunto",
"what":"¿Qué es WARI FIRE AI?", "intro":"Es una plataforma web educativa que organiza investigaciones de combustión en microgravedad. Permite consultar un catálogo científico, analizar las mediciones iniciales y finales de gases de BASS-II y comparar ensayos sin inventar resultados.",
"path":"Aprende a usar la plataforma", "step1":"Explora investigaciones", "step1d":"Busca BASS, SAME o FLEX y revisa la fuente oficial.", "step2":"Visualiza datos", "step2d":"Filtra los ensayos y compara O₂, CO₂ o CO.", "step3":"Compara ensayos", "step3d":"Identifica coincidencias y diferencias, sin afirmar causalidad.", "step4":"Evalúa los límites", "step4d":"Consulta alertas y diferencias entre microgravedad y la Luna o Marte.",
"no_ai":"Esta versión analiza y presenta datos; todavía no incluye un asistente de IA pública ni un predictor de incendios.",
"lib_title":"Biblioteca científica NASA PSI", "lib_desc":"Busca investigaciones por su área de seguridad, combustible o palabra clave.","search":"Buscar investigación", "search_example":"Ejemplo: BASS, humo, extinción...", "area":"Área de seguridad", "fuel":"Tipo de combustible", "found":"Investigaciones encontradas", "areas":"Áreas activas", "fuels":"Tipos activos", "open_source":"Abrir fuente", "source_catalog":"Catálogo inicial de Wari Teams basado en NASA PSI; los enlaces de SAME y FLEX apuntan al índice general.", "empty":"No hay resultados para estos filtros.",
"exp_title":"Explorador de mediciones BASS-II", "exp_desc":"Consulta 129 registros de ensayos y compara las lecturas iniciales y finales de O₂, CO₂ o CO.", "guide":"1. Filtra por investigador o material. 2. Selecciona una variable. 3. Elige hasta 20 ensayos. 4. Revisa la ficha y las alertas antes de interpretar.","pi":"Investigador principal", "material_filter":"Buscar material", "material_hint":"PMMA, film, algodón...", "visible":"Ensayos visibles", "unique":"Identificadores únicos", "chart_tab":"Gráficos", "test_tab":"Ficha de ensayo", "quality_tab":"Control de calidad", "raw_tab":"Datos originales", "select_gas":"Variable a visualizar", "select_tests":"Selecciona hasta 20 ensayos", "too_many":"Se grafican solo los primeros 20 ensayos seleccionados.", "no_numbers":"No hay valores numéricos para los ensayos seleccionados.", "plot_title":"Mediciones iniciales y finales", "test_axis":"Identificador de ensayo", "initial":"Inicial", "final":"Final", "delta":"Diferencia (final − inicial)", "calc_title":"Comparación numérica de lecturas", "download_data":"Descargar tabla filtrada CSV", "caution":"La diferencia entre lecturas no determina por sí sola la inflamabilidad o seguridad de un material.","select_test":"Selecciona un ensayo", "material":"Material", "date":"Fecha", "field":"Variable", "raw_i":"Inicial (original)", "raw_f":"Final (original)", "missing":"No disponible", "quality_warning":"Este ensayo tiene alertas automáticas; revisa los valores originales.", "quality_ok":"Sin alertas automáticas. Esto no equivale a validación científica.","fan_note":"Fan display y Air display son lecturas del equipo; no equivalen necesariamente a velocidad física de aire.","quality_intro":"Las alertas son indicaciones estadísticas o de formato. No se corrigen ni eliminan los valores originales.", "alert_type":"Tipo de alerta", "visible_alerts":"Alertas visibles", "download_alerts":"Descargar alertas CSV", "original_note":"Los nombres de columna se mantienen como los publicó NASA para conservar la trazabilidad.",
"compare_title":"Comparación científica de dos ensayos", "compare_desc":"Contrasta las condiciones registradas y los cambios de O₂, CO₂ y CO, sin atribuir diferencias a una causa no demostrada.", "test_a":"Ensayo A", "test_b":"Ensayo B", "different_tests":"Selecciona dos ensayos diferentes.", "equal":"Igual", "different":"Diferente", "absent":"Dato faltante", "status":"Estado", "same_count":"Campos iguales", "different_count":"Campos diferentes", "missing_count":"Campos incompletos", "delta_comp":"Comparación de cambios numéricos", "allowed":"Qué podemos afirmar", "allowed_body":"Podemos señalar coincidencias, diferencias y operaciones aritméticas documentadas. Esto no demuestra causalidad.", "not_allowed":"Qué no podemos afirmar", "not_allowed_body":"No certifica inflamabilidad, no predice incendios y no extrapola directamente los ensayos a la Luna o Marte.",
"space_title":"Aplicación a seguridad espacial", "space_desc":"Explora cómo podrían orientar la investigación sobre prevención, detección y supresión de incendios en hábitats espaciales.", "scene":"Entorno de interés", "station":"Estación orbital (microgravedad)", "moon":"Hábitat lunar", "mars":"Hábitat marciano", "scene_station":"Estos datos se obtuvieron en condiciones de microgravedad; aun así, deben revisarse el combustible y las condiciones atmosféricas de cada ensayo.","scene_other":"Los resultados de microgravedad no permiten predecir directamente qué sucederá bajo gravedad lunar o marciana.", "relevance":"Investigaciones por área", "interpretation":"Interpretación responsable", "space_yes":"Útil para localizar estudios y condiciones relevantes para diseñar futuras pruebas de seguridad.", "space_no":"No constituye un simulador, una certificación ni una predicción de incendio.",
"method_title":"Metodología y límites científicos", "method_desc":"Conoce el origen de las mediciones, el tratamiento de los datos y cómo se identifican las incertidumbres.","method1":"Datos originales", "method1d":"El CSV experimental BASS-II se conserva intacto. Solo números aislados y claros participan en los cálculos.", "method2":"Cálculos", "method2d":"Se presentan diferencias entre lecturas iniciales y finales, no tasas de combustión ni causalidad.", "method3":"Calidad", "method3d":"Se señalan celdas ausentes, textos ambiguos y valores atípicos (IQR), sin eliminarlos.","method4":"Extrapolación", "method4d":"Los datos de microgravedad no equivalen a pruebas de gravedad lunar o marciana.", "method_source":"Fuente principal: NASA Physical Sciences Informatics (PSI), tabla experimental BASS-II, PSI-25_Experimental table_BASS-II.csv.",
"cat_exp":"Experimento", "cat_area":"Área", "cat_fuel":"Combustible", "cat_desc":"Descripción", "cat_source":"Fuente", "no_file":"No se encontró el archivo requerido.", "raw_note":"Los datos científicos originales no se traducen ni modifican; se traducen las etiquetas y explicaciones de la interfaz.",
"oxygen":"Oxígeno (O₂)", "carbon_dioxide":"Dióxido de carbono (CO₂)", "carbon_monoxide":"Monóxido de carbono (CO)", "gas_unit":"% en volumen", "co_unit":"ppm", "source":"Fuente"
},
"English": {
"language":"Language / Idioma", "navigation":"Navigation", "welcome":"Home", "library":"NASA Library", "explorer":"BASS-II Explorer", "compare":"Scientific comparison", "space":"Space fire safety", "method":"Methodology",
"sidebar_desc":"Scientific platform for exploring NASA PSI data and understanding combustion in microgravity.","sidebar_help":"Guide: Library → Explorer → Comparison → Space safety.",
"hero_text":"From complex data to understandable evidence: explore NASA PSI studies, compare BASS-II tests, and understand the limits of fire safety research in space.",
"hero_1":"NASA PSI data", "hero_2":"129 BASS-II tests", "hero_3":"Traceable analysis", "hero_4":"Educational prototype",
"studies":"Investigations", "tests":"BASS-II tests", "researchers":"Researchers", "alerts":"Quality flags", "records":"Experimental records", "catalog":"Initial catalog", "review":"Flagged for review; not necessarily errors", "scientists":"Contributors in the dataset",
"what":"What is WARI FIRE AI?", "intro":"An educational web platform that organizes microgravity combustion research. It offers a searchable catalog, initial and final gas measurements from BASS-II, and test comparisons without inventing results.",
"path":"How to use the platform", "step1":"Browse research", "step1d":"Search for BASS, SAME or FLEX and check the official source.", "step2":"Explore measurements", "step2d":"Filter tests and compare O₂, CO₂ or CO.", "step3":"Compare tests", "step3d":"Identify similarities and differences without claiming causation.", "step4":"Check limitations", "step4d":"Review flags and differences between microgravity, the Moon and Mars.",
"no_ai":"This version presents and analyzes data; it does not yet offer public generative AI or fire prediction.",
"lib_title":"NASA PSI Research Library", "lib_desc":"Search by safety area, fuel type or keyword.","search":"Search investigations", "search_example":"e.g., BASS, smoke, extinction...", "area":"Safety area", "fuel":"Fuel type", "found":"Investigations found", "areas":"Selected areas", "fuels":"Selected fuel types", "open_source":"Open source", "source_catalog":"Wari Teams' initial catalog based on NASA PSI; SAME and FLEX links lead to the general index.", "empty":"No matching records for these filters.",
"exp_title":"BASS-II Measurements Explorer", "exp_desc":"Browse 129 test records and compare initial and final O₂, CO₂ and CO measurements.", "guide":"1. Filter by researcher or material. 2. Select a gas. 3. Choose up to 20 tests. 4. Check test details and quality flags.","pi":"Principal investigator", "material_filter":"Search material", "material_hint":"PMMA, film, cotton...", "visible":"Visible tests", "unique":"Unique test IDs", "chart_tab":"Charts", "test_tab":"Test details", "quality_tab":"Quality control", "raw_tab":"Original data", "select_gas":"Measurement to display", "select_tests":"Choose up to 20 tests", "too_many":"Only the first 20 selected tests are shown.", "no_numbers":"The selected tests have no usable numeric measurements.", "plot_title":"Initial and final measurements", "test_axis":"Test ID", "initial":"Initial", "final":"Final", "delta":"Difference (final − initial)", "calc_title":"Numerical comparison of measurements", "download_data":"Download filtered CSV", "caution":"The difference between measurements alone does not determine a material's flammability or safety.","select_test":"Select a test", "material":"Material", "date":"Date", "field":"Variable", "raw_i":"Initial (original)", "raw_f":"Final (original)", "missing":"Unavailable", "quality_warning":"This test has automatic quality flags; examine the original values.", "quality_ok":"No automatic flags were found. This is not full scientific validation.","fan_note":"Fan display and Air display are instrument readings, not necessarily physical airflow velocities.","quality_intro":"Flags describe statistical or formatting issues; original values are never changed or removed.", "alert_type":"Flag category", "visible_alerts":"Visible flags", "download_alerts":"Download flags CSV", "original_note":"Original NASA column names are retained for scientific traceability.",
"compare_title":"Scientific comparison of two tests", "compare_desc":"Compare recorded conditions and changes in O₂, CO₂ and CO without attributing differences to unproven causes.", "test_a":"Test A", "test_b":"Test B", "different_tests":"Please select two different tests.", "equal":"Same", "different":"Different", "absent":"Missing data", "status":"Status", "same_count":"Matching fields", "different_count":"Different fields", "missing_count":"Incomplete fields", "delta_comp":"Comparison of numerical changes", "allowed":"What the data supports", "allowed_body":"We can report matching fields, differences and documented arithmetic calculations. This does not demonstrate causation.", "not_allowed":"What the data does not support", "not_allowed_body":"It does not certify flammability, predict real fires, or directly extrapolate tests to the Moon or Mars.",
"space_title":"Applications to space fire safety", "space_desc":"Explore how research may inform future studies on fire prevention, detection and suppression in crewed habitats.", "scene":"Environment of interest", "station":"Orbital station (microgravity)", "moon":"Lunar habitat", "mars":"Martian habitat", "scene_station":"These records come from microgravity experiments. Fuel and atmospheric test conditions must still be checked.","scene_other":"Microgravity results do not directly predict fire behavior under lunar or Martian gravity.", "relevance":"Investigations by safety area", "interpretation":"Responsible interpretation", "space_yes":"Useful for identifying studies and conditions relevant to future safety testing.", "space_no":"This is not a simulator, a certification tool, or a fire prediction system.",
"method_title":"Methods and scientific limitations", "method_desc":"Learn where the measurements came from, how they are processed, and how uncertainty is handled.","method1":"Original data", "method1d":"The original BASS-II CSV is preserved. Only unambiguous, single numeric values are used for calculations.", "method2":"Calculations", "method2d":"Final-minus-initial differences are shown, not combustion rates or causal effects.", "method3":"Quality", "method3d":"Missing cells, ambiguous text and IQR outliers are flagged but not deleted.","method4":"Extrapolation", "method4d":"Microgravity data are not equivalent to experiments in lunar or Martian gravity.", "method_source":"Main source: NASA Physical Sciences Informatics (PSI), BASS-II experimental table, PSI-25_Experimental table_BASS-II.csv.",
"cat_exp":"Investigation", "cat_area":"Safety area", "cat_fuel":"Fuel", "cat_desc":"Description", "cat_source":"Source", "no_file":"The required file could not be found.", "raw_note":"Original scientific data are neither translated nor changed; only interface labels and explanations are localized.",
"oxygen":"Oxygen (O₂)", "carbon_dioxide":"Carbon dioxide (CO₂)", "carbon_monoxide":"Carbon monoxide (CO)", "gas_unit":"% by volume", "co_unit":"ppm", "source":"Source"
}
}

AREA_EN = {"Prevención":"Prevention", "Detección":"Detection", "Supresión":"Suppression"}
FUEL_EN = {"Sólidos":"Solids", "Líquidos":"Liquids", "Aerosoles":"Aerosols"}
DESC_EN = {
  "BASS":"Solid-material burning and suppression in microgravity.",
  "SAME":"Smoke and aerosol measurements in microgravity.",
  "FLEX":"Liquid-fuel droplet flame extinction studies."
}

# Navigation and language state
if "language" not in st.session_state:
    st.session_state.language = "Español"
if "section_choice" not in st.session_state:
    st.session_state.section_choice = "home"

ADDITIONAL = {
    "Español": {
        "dashboard":"📊 Panel general", "assistant":"🤖 Asistente WARI AI",
        "nav_home":"🏠 Página de inicio", "welcome":"Inicio", "quick":"Acceso directo a los módulos",
        "hero_tag":"WARI TEAMS · NASA SPACE APPS CHALLENGE 2026",
        "hero_title":"Inteligencia para la <em>seguridad espacial</em>",
        "hero_desc":"Explora datos de combustión en microgravedad, compara ensayos reales de NASA PSI y descubre qué evidencia puede contribuir a la prevención, detección y supresión de incendios en futuras misiones.",
        "go_explore":"Explorar BASS-II", "go_library":"Ver investigaciones", "go_dashboard":"Ver panel general",
        "metrics_title":"Panorama de la investigación", "modules_title":"Explora la plataforma",
        "method_note":"Los datos son originales de NASA PSI. Las métricas corresponden al catálogo cargado, no a toda la investigación de la NASA.",
        "journey_title":"Cómo funciona WARI FIRE AI", "journey_desc":"Un recorrido desde la evidencia hasta una comparación verificable.",
        "stage1":"1 · Descubre", "stage1d":"Busca investigaciones sobre combustión y revisa la fuente.",
        "stage2":"2 · Explora", "stage2d":"Selecciona ensayos y variables O₂, CO₂ y CO.",
        "stage3":"3 · Compara", "stage3d":"Observa diferencias reales y datos faltantes.",
        "stage4":"4 · Interpreta", "stage4d":"Comprueba alcances y límites científicos.",
        "dashboard_title":"Panel general", "dashboard_sub":"Resumen de los archivos realmente cargados y acceso a los análisis.",
        "research_count":"Estudios catalogados", "test_count":"Ensayos BASS-II", "pi_count":"Investigadores", "quality_count":"Alertas de calidad",
        "briefs":"Documentos y mediciones", "ready":"Archivos de datos disponibles", "missing_files":"Archivos faltantes",
        "assistant_title":"Asistente WARI AI", "assistant_sub":"Módulo planificado: preguntas científicas con citas y verificación de fuentes.",
        "assistant_status":"La IA pública aún no está conectada. En esta etapa no generamos respuestas automáticas ni simulamos una conexión real.",
        "assistant_future":"La siguiente etapa implementará búsqueda documental verificable y respuestas sustentadas en fuentes NASA PSI.",
        "module_desc":["Encuentra BASS, SAME y FLEX con sus enlaces.","Visualiza mediciones de los 129 ensayos BASS-II.","Contrasta dos ensayos y sus diferencias.","Consulta posibles aplicaciones con cautela científica.","Conoce el tratamiento de los datos y sus límites.","Asistente documental con IA: próximo desarrollo."],
        "help_nav":"Selecciona una sección o usa los accesos de Inicio.",
        "test_progress":"Probado: catálogo y datos BASS-II; el resto continúa en desarrollo.",
    },
    "English": {
        "dashboard":"📊 Dashboard", "assistant":"🤖 WARI AI Assistant",
        "nav_home":"🏠 Home", "welcome":"Home", "quick":"Open a module",
        "hero_tag":"WARI TEAMS · NASA SPACE APPS CHALLENGE 2026",
        "hero_title":"Evidence for <em>space fire safety</em>",
        "hero_desc":"Explore microgravity combustion data, compare real NASA PSI tests, and discover which evidence may inform fire prevention, detection, and suppression in future space missions.",
        "go_explore":"Explore BASS-II", "go_library":"Browse research", "go_dashboard":"Open dashboard",
        "metrics_title":"Research overview", "modules_title":"Explore the platform",
        "method_note":"Data come from NASA PSI. Metrics describe the loaded catalog only, not the entire NASA research archive.",
        "journey_title":"How WARI FIRE AI works", "journey_desc":"A guided path from research evidence to traceable comparison.",
        "stage1":"1 · Discover", "stage1d":"Search combustion studies and review their sources.",
        "stage2":"2 · Explore", "stage2d":"Select tests and O₂, CO₂ or CO variables.",
        "stage3":"3 · Compare", "stage3d":"Inspect observed differences and missing data.",
        "stage4":"4 · Interpret", "stage4d":"Review scientific scope and limitations.",
        "dashboard_title":"Research dashboard", "dashboard_sub":"Summary of data files actually loaded and links to analysis modules.",
        "research_count":"Cataloged studies", "test_count":"BASS-II tests", "pi_count":"Researchers", "quality_count":"Quality flags",
        "briefs":"Studies and measurements", "ready":"Data files available", "missing_files":"Missing files",
        "assistant_title":"WARI AI Assistant", "assistant_sub":"Planned module: evidence-grounded scientific questions and cited answers.",
        "assistant_status":"Public AI is not connected yet. This stage does not generate automatic responses or pretend a remote AI is running.",
        "assistant_future":"A later stage will add verifiable document search and answers grounded in NASA PSI sources.",
        "module_desc":["Browse BASS, SAME and FLEX with source links.","Visualize measurements across 129 BASS-II test records.","Compare two tests and inspect differences.","Review possible applications with scientific caveats.","Understand data processing and limitations.","Evidence-based AI assistant: coming later."],
        "help_nav":"Choose a section or use shortcuts from Home.",
        "test_progress":"Validated: research catalog and BASS-II data; other features are in development.",
    },
}

with st.sidebar:
    if LOGO.exists():
        st.image(str(LOGO), width=136)
    st.markdown("### WARI FIRE AI")
    st.caption("Flame in Freefall · NASA Space Apps Challenge 2026")
    st.selectbox("🌐 Language / Idioma", ["Español", "English"], key="language")
    tr = I18N[st.session_state.language]
    tx = ADDITIONAL[st.session_state.language]
    OPTIONS = [
        ("home",tx["nav_home"]),
        ("dashboard",tx["dashboard"]),
        ("library","📚 "+tr["library"]),
        ("explorer","📈 "+tr["explorer"]),
        ("compare","⚖️ "+tr["compare"]),
        ("simulator","🔥 Simulador educativo" if st.session_state.language == "Español" else "🔥 Educational Simulator"),
        ("space","🛰️ "+tr["space"]),
        ("assistant",tx["assistant"]),
        ("reports","📄 Informes científicos" if st.session_state.language=="Español" else "📄 Scientific reports"),
        ("jury","🚀 Modo jurado" if st.session_state.language=="Español" else "🚀 Jury demo"),
        ("method","🧪 "+tr["method"]),
    ]
    labels = dict(OPTIONS)
    page = st.radio(tr["navigation"], [key for key,_ in OPTIONS],format_func=lambda key:labels[key],key="section_choice")
    st.caption(tx["help_nav"])
    st.divider()
    st.caption("Wari Teams · Ayacucho, Perú")
    st.caption("Research prototype · Not a certified safety tool")

tr = I18N[st.session_state.language]
tx = ADDITIONAL[st.session_state.language]
en = st.session_state.language == "English"


def go_to(section):
    st.session_state.section_choice=section


if page == "home":
    st.markdown(f"""
    <div class="hero-v6">
       <div class="stars"></div><div class="orbit"></div><div class="microflame">🔥</div>
       <div class="content"><div class="tag">{escape(tx['hero_tag'])}</div>
       <h1 class="headline">WARI FIRE AI<br>{tx['hero_title']}</h1>
       <p>{escape(tx['hero_desc'])}</p></div>
    </div>""",unsafe_allow_html=True)
    x,y,z=st.columns([1,1,1])
    x.button("🚀 "+tx["go_explore"], on_click=go_to, args=("explorer",), use_container_width=True)
    y.button("📚 "+tx["go_library"], on_click=go_to, args=("library",), use_container_width=True)
    z.button("📊 "+tx["go_dashboard"], on_click=go_to, args=("dashboard",), use_container_width=True)
    st.button("🔥 Simulador educativo / Educational Simulator", on_click=go_to, args=("simulator",), use_container_width=True)
else:
    st.markdown(f'<div class="accent-top">WARI FIRE AI · FLAME IN FREEFALL · NASA PSI · {"ENGLISH" if en else "ESPAÑOL"}</div>',unsafe_allow_html=True)


def localized_catalog(df):
    result = df.copy()
    if en:
        result["area"] = result["area"].replace(AREA_EN)
        result["combustible"] = result["combustible"].replace(FUEL_EN)
        result["descripcion"] = result.apply(lambda row: DESC_EN.get(str(row["experimento"]), str(row["descripcion"])),axis=1)
    result = result.rename(columns={
        "experimento": tr["cat_exp"], "area": tr["cat_area"],
        "combustible": tr["cat_fuel"],"descripcion":tr["cat_desc"],"fuente":tr["cat_source"]
    })
    return result


def local_qc(df):
    x = df.copy()
    if en:
        reasons = {
         "Dato ausente":"Missing value",
         "Texto ambiguo; no se transformó en medición":"Ambiguous text; not converted to a measurement",
         "Fuera del rango 0–100 % vol.":"Outside physical 0–100% volume range",
         "Valor estadísticamente atípico (IQR)":"Statistical outlier (IQR)"
        }
        x["Alerta"] = x["Alerta"].replace(reasons)
        x["Variable"] = x["Variable"].str.replace(" inicial"," initial", regex=False).str.replace(" final"," final", regex=False)
    return x.rename(columns={"Ensayo":tr["tests"],"Variable":tr["field"],"Valor original":tr["raw_i"],"Alerta":tr["alert_type"]})


def unavailable_data():
    st.error(tr["no_file"])


def metrics():
    c1,c2,c3,c4=st.columns(4)
    kpi(c1,tx["research_count"], len(catalog) if catalog is not None else "—")
    kpi(c2,tx["test_count"],len(bass) if bass is not None else "—")
    kpi(c3,tx["pi_count"],bass[cols["pi"]].nunique() if bass is not None and cols.get("pi") else "—")
    kpi(c4,tx["quality_count"],len(qc))


def module_cards():
    items=[("library","📚",tr["library"]), ("explorer","📈",tr["explorer"]),
           ("compare","⚖️",tr["compare"]), ("space","🛰️",tr["space"]),
           ("method","🧪",tr["method"]), ("assistant","🤖",tx["assistant"])]
    for row_start in (0,3):
        columns=st.columns(3)
        for i,(code,icon,title) in enumerate(items[row_start:row_start+3]):
            col=columns[i]
            with col:
                st.markdown(f'<div class="feature-v6"><div class="ico">{icon}</div><h4>{escape(title)}</h4><p>{escape(tx["module_desc"][row_start+i])}</p></div>',unsafe_allow_html=True)
                st.button(("Open / Abrir ↗" if en else "Abrir módulo ↗"),key=f"module_{code}",use_container_width=True,on_click=go_to,args=(code,))
        st.write("")


if page == "home":
    st.markdown(f'<h2 class="section-v6">{escape(tx["metrics_title"])}</h2>',unsafe_allow_html=True)
    metrics()
    st.caption(tx["method_note"])
    st.markdown(f'<h2 class="section-v6">{escape(tx["modules_title"])}</h2>',unsafe_allow_html=True)
    module_cards()
    st.markdown(f'<h2 class="section-v6">{escape(tx["journey_title"])}</h2>',unsafe_allow_html=True)
    st.caption(tx["journey_desc"])
    steps=st.columns(4)
    for i in range(1,5):
        step_card(steps[i-1],i,tx[f"stage{i}"],tx[f"stage{i}d"],[],[CYAN,ORANGE,GOLD,VIOLET][i-1])
    st.write("")
    st.markdown(f'<div class="v6-progress"><strong>{escape(tx["test_progress"])}</strong><br>{escape(tr["no_ai"])}</div>',unsafe_allow_html=True)
    if missing: st.error(tx["missing_files"]+": "+", ".join(missing))

elif page == "dashboard":
    section_header(tx["dashboard_title"],tx["dashboard_sub"])
    metrics()
    st.caption(tx["method_note"])
    if bass is not None and cols.get("pi"):
        st.write("")
        c1,c2=st.columns([1.3,1])
        with c1:
            st.markdown("### "+( "Tests by investigator" if en else "Ensayos por investigador"))
            counts=bass[cols["pi"]].fillna("Unknown" if en else "Sin identificar").astype(str).value_counts()
            fig=go.Figure(go.Bar(x=counts.values,y=counts.index,orientation="h",marker_color="#ff9d62"))
            fig.update_layout(yaxis_title="",xaxis_title=("Tests" if en else "Ensayos"),height=335)
            show_plot(fig)
        with c2:
            st.markdown("### "+("Data provenance" if en else "Trazabilidad de datos"))
            st.markdown(f'<div class="v6-progress"><strong>{escape(SRC_BASS2)}</strong><br>{escape(tx["method_note"])}</div>',unsafe_allow_html=True)
            st.button("🚀 "+tx["go_explore"],on_click=go_to,args=("explorer",),use_container_width=True)
            st.button("📚 "+tx["go_library"],on_click=go_to,args=("library",),use_container_width=True)
    if missing: st.error(tx["missing_files"]+": "+", ".join(missing))

elif page == "jury":
    render_jury_demo(bass,cols,st.session_state.language)

elif page == "reports":
    render_reports(bass,cols,st.session_state.language)

elif page == "assistant":
    render_assistant(bass, cols, catalog, st.session_state.language)

elif page == "library":
    section_header(tr["lib_title"],tr["lib_desc"])
    if catalog is None:
        unavailable_data()
    else:
        cat = localized_catalog(catalog)
        a,b,c = st.columns([2,1,1])
        query = a.text_input(tr["search"],placeholder=tr["search_example"])
        areas = sorted(cat[tr["cat_area"]].dropna().unique())
        area_sel = b.multiselect(tr["area"],areas,default=areas)
        fuels = sorted(cat[tr["cat_fuel"]].dropna().unique())
        fuel_sel = c.multiselect(tr["fuel"],fuels,default=fuels)
        result = cat[cat[tr["cat_area"]].isin(area_sel)&cat[tr["cat_fuel"]].isin(fuel_sel)]
        if query:
            result = result[result.apply(lambda r: query.casefold() in " ".join(map(str,r.values)).casefold(),axis=1)]
        a,b,c = st.columns(3)
        kpi(a,tr["found"],len(result))
        kpi(b,tr["areas"],len(area_sel))
        kpi(c,tr["fuels"],len(fuel_sel))
        if result.empty: st.info(tr["empty"])
        else:
            show_df(result,column_config={tr["cat_source"]:st.column_config.LinkColumn(tr["cat_source"],display_text=tr["open_source"])})
        source_caption(tr["source_catalog"])

elif page == "explorer":
    section_header(tr["exp_title"],tr["exp_desc"])
    st.info(tr["guide"])
    if bass is None:
        unavailable_data()
        st.stop()
    with st.sidebar:
        pis=sorted(bass[cols["pi"]].dropna().astype(str).unique()) if cols.get("pi") else []
        pis_sel=st.multiselect(tr["pi"],pis,default=pis)
        material_query=st.text_input(tr["material_filter"],placeholder=tr["material_hint"])
    filtered = bass.copy()
    if cols.get("pi"):
        filtered=filtered[filtered[cols["pi"]].astype(str).isin(pis_sel)]
    if material_query and cols.get("material"):
        filtered=filtered[filtered[cols["material"]].astype(str).str.contains(material_query,case=False,na=False)]
    if filtered.empty:
        st.info(tr["empty"])
        st.stop()
    a,b=st.columns(2)
    kpi(a,tr["visible"],len(filtered))
    kpi(b,tr["unique"],filtered["_test"].nunique())
    tabs=st.tabs([tr["chart_tab"],tr["test_tab"],tr["quality_tab"],tr["raw_tab"]])
    with tabs[0]:
        var_names={"O2":tr["oxygen"],"CO2":tr["carbon_dioxide"],"CO":tr["carbon_monoxide"]}
        avail=[v for v in ("O2","CO2","CO") if cols.get(f"{v}_i") and cols.get(f"{v}_f")]
        if not avail:
            st.error(tr["no_numbers"])
        else:
            gas=st.radio(tr["select_gas"],avail,format_func=lambda x:var_names[x],horizontal=True)
            ids=filtered["_test_key"].tolist()
            chosen=st.multiselect(tr["select_tests"],ids,default=ids[:min(8,len(ids))])
            if len(chosen)>MAX_TESTS:
                st.warning(tr["too_many"])
                chosen=chosen[:MAX_TESTS]
            sub=filtered[filtered["_test_key"].isin(chosen)].copy()
            visible=sub.dropna(subset=[f"{gas}_i_num",f"{gas}_f_num"],how="all")
            if visible.empty: st.info(tr["no_numbers"])
            else:
                fig=go.Figure()
                fig.add_bar(x=visible["_test_key"],y=visible[f"{gas}_i_num"],name=tr["initial"],marker_color=CYAN)
                fig.add_bar(x=visible["_test_key"],y=visible[f"{gas}_f_num"],name=tr["final"],marker_color=ORANGE)
                fig.update_layout(barmode="group",title=f'{tr["plot_title"]}: {var_names[gas]}',xaxis_title=tr["test_axis"],yaxis_title=tr["co_unit"] if gas=="CO" else tr["gas_unit"])
                show_plot(fig)
                summary=pd.DataFrame({tr["test_axis"]:visible["_test_key"],tr["initial"]:visible[f"{gas}_i_num"],tr["final"]:visible[f"{gas}_f_num"]})
                summary[tr["delta"]]=(summary[tr["final"]]-summary[tr["initial"]]).round(3)
                st.markdown("#### "+tr["calc_title"])
                show_df(summary)
                st.caption(tr["caution"])
                source_caption()
                st.download_button(tr["download_data"],data=summary.to_csv(index=False).encode("utf-8-sig"),file_name=f"wari_{gas}_{'en' if en else 'es'}.csv",mime="text/csv")
    with tabs[1]:
        selected_test=st.selectbox(tr["select_test"],filtered["_test_key"].tolist())
        row=filtered[filtered["_test_key"]==selected_test].iloc[0]
        a,b,c=st.columns(3)
        kpi(a,tr["material"],row[cols["material"]] if cols.get("material") else "—")
        kpi(b,tr["pi"],row[cols["pi"]] if cols.get("pi") else "—")
        kpi(c,tr["date"],row[cols["date"]] if cols.get("date") else "—")
        details=[]
        for gas in ("O2","CO2","CO"):
            if cols.get(f"{gas}_i") and cols.get(f"{gas}_f"):
                ai,bf=row[f"{gas}_i_num"],row[f"{gas}_f_num"]
                details.append({tr["field"]:gas,tr["raw_i"]:row[cols[f"{gas}_i"]],tr["raw_f"]:row[cols[f"{gas}_f"]],tr["delta"]:round(bf-ai,3) if pd.notna(ai) and pd.notna(bf) else tr["missing"]})
        show_df(pd.DataFrame(details))
        subset=qc[qc["Ensayo"]==row["_test"]] if not qc.empty else qc
        if not subset.empty:
            st.warning(tr["quality_warning"])
            show_df(local_qc(subset))
        else: st.success(tr["quality_ok"])
        st.caption(tr["fan_note"])
        source_caption()
    with tabs[2]:
        st.info(tr["quality_intro"])
        if not qc.empty:
            flags=local_qc(qc)
            kinds=sorted(flags[tr["alert_type"]].unique())
            chosen_kinds=st.multiselect(tr["alert_type"],kinds,default=kinds)
            subset=flags[flags[tr["alert_type"]].isin(chosen_kinds)]
            kpi(st.columns(1)[0],tr["visible_alerts"],len(subset))
            show_df(subset)
            st.download_button(tr["download_alerts"],data=subset.to_csv(index=False).encode("utf-8-sig"),file_name="wari_quality_flags.csv",mime="text/csv")
        source_caption()
    with tabs[3]:
        st.caption(tr["original_note"])
        raw_cols=[str(c).strip() for c in pd.read_csv(BASS2_FILE,nrows=0).columns]
        show_df(filtered[[c for c in raw_cols if c in filtered.columns]])
        source_caption()

elif page == "compare":
    # Comparación científica de DOS registros reales de BASS-II.
    # Este módulo no inventa valores ni extrae números de celdas ambiguas.
    section_header(tr["compare_title"], tr["compare_desc"])
    if bass is None or bass.empty:
        unavailable_data()
        st.stop()
    if len(bass) < 2:
        st.warning("Se necesitan al menos dos ensayos." if not en else "At least two tests are required.")
        st.stop()

    st.markdown("""
    <style>
    .compare-panel {background:linear-gradient(135deg,#142138,#0e1b30);border:1px solid #38516d;
      border-radius:16px;padding:17px 20px;margin:10px 0 15px;box-shadow:0 8px 24px rgba(0,0,0,.17)}
    .compare-panel h3 {font-size:1.15rem;color:#fff!important;margin:2px 0 9px}
    .compare-panel p {color:#d9e8f8!important;margin:4px 0;line-height:1.55}
    .compare-chip {display:inline-block;border:1px solid #55718c;color:#dcf6ff;background:#1e3049;
      border-radius:99px;font-size:.8rem;padding:4px 9px;margin:4px 5px 0 0}
    </style>""",unsafe_allow_html=True)

    def display(v):
        return "—" if pd.isna(v) else str(v).strip()

    def raw(row, col):
        return row[col] if col is not None and col in row.index else None

    def status(va, vb):
        if va is None or vb is None or pd.isna(va) or pd.isna(vb) or str(va).strip().lower() in {"", "none", "nan", "n/a"} or str(vb).strip().lower() in {"", "none", "nan", "n/a"}:
            return "missing"
        return "same" if str(va).strip() == str(vb).strip() else "different"

    def val_num(row, key):
        name = f"{key}_num"
        return row[name] if name in row.index and pd.notna(row[name]) else None

    ids = bass["_test_key"].tolist()
    ca, cb = st.columns(2, gap="medium")
    ida = ca.selectbox("🔹 Ensayo A" if not en else "🔹 Test A", ids, index=0, key="compare_test_a")
    idb = cb.selectbox("🔸 Ensayo B" if not en else "🔸 Test B", ids, index=1, key="compare_test_b")
    if ida == idb:
        st.warning(tr["different_tests"])
        st.stop()
    ra = bass.loc[bass["_test_key"] == ida].iloc[0]
    rb = bass.loc[bass["_test_key"] == idb].iloc[0]

    def test_card(row, test_id, accent):
        material=escape(display(raw(row,cols.get("material"))))
        pi=escape(display(raw(row,cols.get("pi"))))
        date=escape(display(raw(row,cols.get("date"))))
        return f"""<div class="compare-panel" style="border-left:5px solid {accent}">
          <h3>{escape(test_id)}</h3>
          <p><strong>{'Material' if not en else 'Material'}:</strong> {material}</p>
          <p><strong>{'Investigador' if not en else 'Researcher'}:</strong> {pi}</p>
          <p><strong>{'Fecha' if not en else 'Date'}:</strong> {date}</p>
          <span class="compare-chip">BASS-II · NASA PSI</span></div>"""
    ca.markdown(test_card(ra,ida,CYAN),unsafe_allow_html=True)
    cb.markdown(test_card(rb,idb,ORANGE),unsafe_allow_html=True)

    # Metadatos NO se usan para inferir equivalencia experimental.
    fields=[
        ("material", "Material" if not en else "Material"),
        ("fan", "Lectura del ventilador" if not en else "Fan display"),
        ("air", "Lectura de aire" if not en else "Air display"),
        ("O2_i", "O₂ inicial (% vol.)" if not en else "Initial O₂ (% vol.)"),
        ("O2_f", "O₂ final (% vol.)" if not en else "Final O₂ (% vol.)"),
        ("CO2_i", "CO₂ inicial (% vol.)" if not en else "Initial CO₂ (% vol.)"),
        ("CO2_f", "CO₂ final (% vol.)" if not en else "Final CO₂ (% vol.)"),
        ("CO_i", "CO inicial (ppm)" if not en else "Initial CO (ppm)"),
        ("CO_f", "CO final (ppm)" if not en else "Final CO (ppm)"),
    ]
    rows=[]
    counts={"same":0,"different":0,"missing":0}
    for code,label in fields:
        colname=cols.get(code)
        if colname is None or colname not in bass.columns:
            continue
        va=raw(ra,colname)
        vb=raw(rb,colname)
        result=status(va,vb)
        counts[result]+=1
        icon={"same":"✓","different":"≠","missing":"—"}[result]
        word=( {"same":"Coincide", "different":"Diferente", "missing":"Falta dato"} if not en else
               {"same":"Match", "different":"Different", "missing":"Missing"})[result]
        rows.append({"Variable" if not en else "Variable":label,
                     "Ensayo A" if not en else "Test A":display(va),
                     "Ensayo B" if not en else "Test B":display(vb),
                     "Estado" if not en else "Status":f"{icon} {word}"})

    k1,k2,k3,k4=st.columns(4)
    kpi(k1,"Coincidencias" if not en else "Matching fields", counts["same"])
    kpi(k2,"Diferencias" if not en else "Different fields", counts["different"])
    kpi(k3,"Datos faltantes" if not en else "Missing fields", counts["missing"])
    kpi(k4,"Variables comparadas" if not en else "Compared variables",len(rows))

    st.markdown("### 📋 "+("Condiciones y mediciones registradas" if not en else "Recorded conditions and measurements"))
    if rows:
        show_df(pd.DataFrame(rows))
    else:
        st.warning("No hay columnas comparables disponibles." if not en else "No comparable columns found.")

    st.markdown("### 📊 "+("Gráfico comparativo de mediciones" if not en else "Measurement comparison chart"))
    c1,c2=st.columns([1,2])
    with c1:
        gas=st.selectbox("Selecciona un gas" if not en else "Select a gas",["O2","CO2","CO"],format_func=lambda x:{"O2":"Oxígeno (O₂)","CO2":"Dióxido de carbono (CO₂)","CO":"Monóxido de carbono (CO)"}[x] if not en else {"O2":"Oxygen (O₂)","CO2":"Carbon dioxide (CO₂)","CO":"Carbon monoxide (CO)"}[x])
        unit="ppm" if gas=="CO" else "% vol."
        st.caption(("Lecturas originales convertidas únicamente cuando la celda contiene un número inequívoco. Unidad: " if not en else "Only unambiguous numeric values are plotted. Unit: ")+unit)
    with c2:
        ai=val_num(ra,f"{gas}_i")
        af=val_num(ra,f"{gas}_f")
        bi=val_num(rb,f"{gas}_i")
        bf=val_num(rb,f"{gas}_f")
        if all(v is None for v in (ai,af,bi,bf)):
            st.info("No hay datos numéricos para graficar este gas." if not en else "No numeric values available for this gas.")
        else:
            fig=go.Figure()
            fig.add_bar(name=f"{ida}",x=["Inicial","Final"] if not en else ["Initial","Final"],y=[ai,af],marker_color=CYAN)
            fig.add_bar(name=f"{idb}",x=["Inicial","Final"] if not en else ["Initial","Final"],y=[bi,bf],marker_color=ORANGE)
            fig.update_layout(barmode="group",title=("Comparación de " if not en else "Comparison of ")+gas,yaxis_title=unit,xaxis_title="")
            show_plot(fig)

    st.markdown("### 🧪 "+("Cambios entre mediciones iniciales y finales" if not en else "Changes between initial and final readings"))
    delta_rows=[]
    for v,unit in [("O2","% vol."),("CO2","% vol."),("CO","ppm")]:
        a0,a1=val_num(ra,f"{v}_i"),val_num(ra,f"{v}_f")
        b0,b1=val_num(rb,f"{v}_i"),val_num(rb,f"{v}_f")
        da=a1-a0 if a0 is not None and a1 is not None else None
        db=b1-b0 if b0 is not None and b1 is not None else None
        delta_rows.append({"Variable":f"{v} ({unit})", "Δ A":round(da,3) if da is not None else "—",
                           "Δ B":round(db,3) if db is not None else "—",
                           "Δ B − Δ A":round(db-da,3) if da is not None and db is not None else "—"})
    show_df(pd.DataFrame(delta_rows))

    # Resumen automático sin atribuir causalidad.
    ai,af=val_num(ra,"O2_i"),val_num(ra,"O2_f")
    bi,bf=val_num(rb,"O2_i"),val_num(rb,"O2_f")
    da=af-ai if ai is not None and af is not None else None
    db=bf-bi if bi is not None and bf is not None else None
    if da is not None and db is not None:
        compare_abs=(f"En {ida}, el cambio de O₂ fue {da:+.3f} puntos porcentuales; en {idb}, {db:+.3f}. "
                     if not en else f"O₂ changed by {da:+.3f} percentage points in {ida} and by {db:+.3f} in {idb}. ")
        compare_abs += ("Estos son cambios observados; no demuestran por sí solos una causa ni un riesgo de incendio."
                        if not en else "These are observed differences; they do not establish causation or fire risk on their own.")
    else:
        compare_abs=("No hay suficientes mediciones de O₂ para comparar ambos cambios."
                     if not en else "Insufficient O₂ readings to compare both changes.")

    st.markdown("### 💡 "+("Interpretación guiada" if not en else "Guided interpretation"))
    st.markdown(f'<div class="compare-panel" style="border-left:5px solid {GOLD}"><h3>{"Resumen descriptivo" if not en else "Descriptive summary"}</h3><p>{escape(compare_abs)}</p></div>',unsafe_allow_html=True)
    left,right=st.columns(2)
    with left:
        st.success(("**Qué sí podemos afirmar**\\n\\n- Identificar coincidencias entre materiales y lecturas registradas.\\n- Calcular diferencias inicial/final cuando existen ambos números.\\n- Mostrar qué datos faltan o requieren revisión."
                    if not en else "**What we can conclude**\\n\\n- Identify matching materials and recorded readings.\\n- Calculate initial/final differences where both numbers are valid.\\n- Identify missing values and quality concerns.").replace("\\n","\n"))
    with right:
        st.warning(("**Qué NO podemos afirmar**\\n\\n- Que una variable causó la diferencia observada.\\n- Que un material es universalmente más seguro.\\n- Que los datos predicen incendios en la Luna o Marte."
                    if not en else "**What we cannot conclude**\\n\\n- That one variable caused the observed difference.\\n- That one material is universally safer.\\n- That these results predict fires on the Moon or Mars.").replace("\\n","\n"))

    st.info("**"+("Trazabilidad científica" if not en else "Scientific traceability")+"** · "+SRC_BASS2+
            ". "+("Las lecturas de ventilación son indicadores del equipo; no velocidades calibradas." if not en else "Fan and air displays are instrument readouts, not calibrated velocities."))
    source_caption()

elif page == "simulator":
    render_simulator(st.session_state.language)

elif page == "space":
    section_header(tr["space_title"],tr["space_desc"])
    choices=["station","moon","mars"]
    scenario=st.selectbox(tr["scene"],choices,format_func=lambda x:tr[x])
    st.info(tr["scene_station"] if scenario=="station" else tr["scene_other"])
    st.markdown("#### "+tr["relevance"])
    if catalog is None: unavailable_data()
    else:
        cat=localized_catalog(catalog)
        for area in sorted(cat[tr["cat_area"]].dropna().unique()):
            with st.expander(str(area),expanded=True):
                sub=cat[cat[tr["cat_area"]]==area]
                show_df(sub,column_config={tr["cat_source"]:st.column_config.LinkColumn(tr["cat_source"],display_text=tr["open_source"])})
    st.markdown("#### "+tr["interpretation"])
    a,b=st.columns(2)
    a.success(tr["space_yes"])
    b.warning(tr["space_no"])

elif page == "method":
    section_header(tr["method_title"],tr["method_desc"])
    for code in ("method1","method2","method3","method4"):
        with st.expander(tr[code],expanded=True):
            st.write(tr[code+"d"])
    st.info(tr["method_source"])
    st.caption(tr["raw_note"])
    st.markdown("https://github.com/stevenlaime17-stack/wari-fire-ai")
