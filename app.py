"""
WARI FIRE AI — Microgravity Combustion Intelligence Platform
Wari Teams · Ayacucho, Perú · NASA International Space Apps Challenge 2026
Desafío: Flame in Freefall

Estructura esperada del repositorio:
    app.py
    requirements.txt
    assets/logo.png                  (opcional)
    data/investigaciones.csv
    data/bass_ii_experimental.csv
    .streamlit/config.toml
"""

import re
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

# ----------------------------------------------------------------------------
# Configuración general
# ----------------------------------------------------------------------------
BASE = Path(__file__).parent
DATA_DIR = BASE / "data"
LOGO = BASE / "assets" / "logo.png"

CATALOG_FILE = DATA_DIR / "investigaciones.csv"
BASS2_FILE = DATA_DIR / "bass_ii_experimental.csv"

SRC_BASS2 = "NASA PSI · BASS-II · PSI-25_Experimental table_BASS-II.csv (datos de ensayos)"
MAX_TESTS = 20

# Paleta Wari / retablo ayacuchano
CYAN, GOLD, MAGENTA, GREEN, RED = "#00D9FF", "#F5B700", "#E63E8B", "#3DDC97", "#FF5A4F"
BG, CARD, LINE = "#080D1B", "#152238", "#24344F"

st.set_page_config(
    page_title="WARI FIRE AI",
    page_icon="🔥",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    f"""
<style>
.block-container {{ padding-top: 1.4rem; max-width: 1300px; }}
.hero {{
    background: linear-gradient(120deg, {BG} 0%, #10244a 55%, #1b3d6e 100%);
    border: 1px solid {LINE}; border-left: 6px solid {GOLD};
    border-radius: 16px; padding: 24px 30px; margin-bottom: 18px;
}}
.hero h1 {{ margin:0; font-size:2rem; color:#fff; letter-spacing:.03em; }}
.hero p  {{ margin:6px 0 0; color:#b9cbe6; }}
.kpi {{ background:{CARD}; border:1px solid {LINE}; border-radius:14px; padding:14px 18px; }}
.kpi .l {{ color:#8fa3c4; font-size:.74rem; text-transform:uppercase; letter-spacing:.07em; }}
.kpi .v {{ color:#fff; font-size:1.7rem; font-weight:700; line-height:1.25; }}
.chip {{ display:inline-block; padding:3px 11px; border-radius:999px; font-size:.78rem;
        font-weight:700; margin-right:6px; border:1px solid; }}
.chip.dato   {{ color:{CYAN};    border-color:{CYAN};    background:rgba(0,217,255,.08); }}
.chip.calc   {{ color:{GOLD};    border-color:{GOLD};    background:rgba(245,183,0,.08); }}
.chip.interp {{ color:{GREEN};   border-color:{GREEN};   background:rgba(61,220,151,.08); }}
.chip.extra  {{ color:{MAGENTA}; border-color:{MAGENTA}; background:rgba(230,62,139,.08); }}
.chip.nd     {{ color:#9aa7bd;   border-color:#9aa7bd;   background:rgba(154,167,189,.08); }}
.source {{ color:#8fa3c4; font-size:.8rem; margin-top:-6px; }}
.warn {{ background:rgba(245,183,0,.08); border:1px solid {GOLD}; border-radius:12px;
        padding:12px 16px; color:#ffe8a3; }}
div[data-testid="stSidebar"] {{ border-right:1px solid {LINE}; }}
footer, #MainMenu {{ visibility:hidden; }}
</style>
""",
    unsafe_allow_html=True,
)


# ----------------------------------------------------------------------------
# Utilidades de interfaz (compatibles con versiones nuevas y antiguas de Streamlit)
# ----------------------------------------------------------------------------
def show_df(df, **kwargs):
    # Columnas con números y texto mezclados: se muestran como texto (el dato original no cambia).
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
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=10, r=10, t=50, b=10),
        legend=dict(orientation="h", y=1.12, x=0),
    )
    try:
        st.plotly_chart(fig, width="stretch")
    except TypeError:
        st.plotly_chart(fig, use_container_width=True)


def kpi(col, label, value):
    col.markdown(
        f'<div class="kpi"><div class="l">{label}</div><div class="v">{value}</div></div>',
        unsafe_allow_html=True,
    )


TAGS = {
    "dato": ("Dato experimental", "dato"),
    "calc": ("Resultado calculado", "calc"),
    "interp": ("Interpretación", "interp"),
    "extra": ("Extrapolación", "extra"),
    "nd": ("Dato no disponible", "nd"),
}


def chips(*keys):
    html = "".join(f'<span class="chip {TAGS[k][1]}">{TAGS[k][0]}</span>' for k in keys)
    st.markdown(html, unsafe_allow_html=True)


def source_caption(text=SRC_BASS2):
    st.markdown(f'<div class="source">Fuente: {text}</div>', unsafe_allow_html=True)


# ----------------------------------------------------------------------------
# Carga y limpieza de datos
# ----------------------------------------------------------------------------
def _tokens(name: str) -> set:
    return set(re.sub(r"[^a-z0-9]+", " ", str(name).lower()).split())


def find_col(df, must=(), none_of=()):
    """Primera columna cuyos tokens contienen todos los de `must` y ninguno de `none_of`."""
    for c in df.columns:
        t = _tokens(c)
        if all(m in t for m in must) and not any(n in t for n in none_of):
            return c
    return None


STRICT_NUMBER = re.compile(r"^[+-]?(?:\d+(?:[.,]\d*)?|[.,]\d+)$")

def parse_number(value):
    """Solo admite UNA medición numérica. Nunca extrae cifras de texto ambiguo."""
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
        # Distinguir filas repetidas sin alterar el identificador del archivo.
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
    """Conserva originales; genera alertas descriptivas, no diagnósticos físicos."""
    rows = []
    for var in ("O2", "CO2", "CO"):
        for phase, label in (("i", "inicial"), ("f", "final")):
            key = f"{var}_{phase}"
            if cols.get(key) is None:
                continue
            num, flags = df[f"{key}_num"], df[f"{key}_flag"]
            valid = num.dropna()
            q1, q3 = valid.quantile(.25), valid.quantile(.75)
            spread = q3 - q1
            lo, hi = q1 - 1.5 * spread, q3 + 1.5 * spread
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


# ----------------------------------------------------------------------------
# Carga inicial
# ----------------------------------------------------------------------------
catalog = load_catalog()
bass, cols = load_bass2()
qc = quality_report(bass, cols) if bass is not None else pd.DataFrame()

# ----------------------------------------------------------------------------
# Sidebar / navegación
# ----------------------------------------------------------------------------
with st.sidebar:
    if LOGO.exists():
        st.image(str(LOGO), width=150)
    st.markdown("### WARI FIRE AI")
    st.caption("Microgravity Combustion Intelligence Platform")
    page = st.radio(
        "Navegación",
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
    st.divider()
    st.caption("Wari Teams · Ayacucho, Perú\nNASA Space Apps 2026 · Flame in Freefall")

st.markdown(
    """
<div class="hero">
  <h1>🔥 WARI FIRE AI</h1>
  <p>Organiza, compara e interpreta investigaciones de combustión en microgravedad de NASA PSI,
  con fuentes verificables y límites científicos explícitos.</p>
</div>
""",
    unsafe_allow_html=True,
)

# ============================================================================
# INICIO
# ============================================================================
if page.startswith("🏠"):
    c1, c2, c3, c4 = st.columns(4)
    kpi(c1, "Investigaciones en catálogo", len(catalog) if catalog is not None else "—")
    kpi(c2, "Ensayos BASS-II", len(bass) if bass is not None else "—")
    kpi(c3, "Investigadores (PI)", bass[cols["pi"]].nunique() if bass is not None and cols["pi"] else "—")
    kpi(c4, "Hallazgos de calidad", len(qc) if bass is not None else "—")

    st.write("")
    st.info("Esta versión es un analizador documental y estadístico; todavía NO incluye IA generativa pública ni pronóstico de incendios.")
    st.markdown("#### Cómo usar la plataforma")
    st.markdown(
        """
1. **Biblioteca científica**: busca investigaciones de prevención, detección y supresión.
2. **Explorador BASS-II**: elige hasta 20 ensayos y compara O₂, CO₂ y CO inicial/final.
3. **Comparación científica**: enfrenta dos ensayos y ve qué es igual, qué es distinto y qué conclusión **sí** está respaldada.
4. **Seguridad espacial**: consulta qué investigaciones son relevantes para un escenario y qué **no** se puede extrapolar.
        """
    )
    st.markdown("#### Tipos de información")
    st.caption("Cada resultado de la plataforma se etiqueta con una de estas categorías:")
    chips("dato", "calc", "interp", "extra", "nd")

    missing = [p for p, f in (("investigaciones.csv", CATALOG_FILE), ("bass_ii_experimental.csv", BASS2_FILE)) if not f.exists()]
    if missing:
        st.error("Faltan archivos en `data/`: " + ", ".join(missing))

# ============================================================================
# BIBLIOTECA
# ============================================================================
elif page.startswith("📚"):
    st.subheader("Biblioteca científica NASA PSI")
    if catalog is None:
        st.error("No se encontró `data/investigaciones.csv`.")
    else:
        c1, c2, c3 = st.columns([2, 1, 1])
        q = c1.text_input("Buscar (experimento o descripción)", placeholder="BASS, humo, extinción…")
        areas = sorted(catalog["area"].dropna().unique()) if "area" in catalog else []
        sel_areas = c2.multiselect("Área de seguridad", areas, default=areas)
        fuels = sorted(catalog["combustible"].dropna().unique()) if "combustible" in catalog else []
        sel_fuels = c3.multiselect("Combustible", fuels, default=fuels)

        out = catalog.copy()
        if sel_areas and "area" in out:
            out = out[out["area"].isin(sel_areas)]
        if sel_fuels and "combustible" in out:
            out = out[out["combustible"].isin(sel_fuels)]
        if q:
            mask = out.apply(lambda r: q.lower() in " ".join(map(str, r.values)).lower(), axis=1)
            out = out[mask]

        st.caption(f"{len(out)} investigación(es)")
        cfg = {}
        if "fuente" in out.columns:
            cfg["fuente"] = st.column_config.LinkColumn("fuente", display_text="Abrir fuente")
        show_df(out, column_config=cfg)
        chips("dato")
        st.markdown('<div class="source">Fuente: catálogo del equipo Wari Teams a partir de NASA PSI.</div>', unsafe_allow_html=True)

# ============================================================================
# EXPLORADOR BASS-II
# ============================================================================
elif page.startswith("📈"):
    st.subheader("Explorador BASS-II")
    if bass is None:
        st.error("No se encontró `data/bass_ii_experimental.csv`.")
        st.stop()

    tab_graf, tab_ficha, tab_qc, tab_tabla = st.tabs(
        ["Gráficos por ensayo", "Ficha de ensayo", "Control de calidad", "Tabla original"]
    )

    # ---- Filtros globales
    with st.sidebar:
        st.markdown("**Filtros BASS-II**")
        pis = sorted(bass[cols["pi"]].dropna().astype(str).unique()) if cols["pi"] else []
        sel_pi = st.multiselect("Investigador principal", pis, default=pis)
        txt = st.text_input("Material (texto)", placeholder="p. ej. cotton")
    f = bass.copy()
    if cols["pi"]:
        f = f[f[cols["pi"]].astype(str).isin(sel_pi)]
    if txt and cols["material"]:
        f = f[f[cols["material"]].astype(str).str.contains(txt, case=False, na=False)]

    if f.empty:
        st.info("No hay ensayos para esos filtros. Cambia el investigador o material.")
        st.stop()

    # ---- Gráficos agrupados
    with tab_graf:
        avail = [v for v in ("O2", "CO2", "CO") if cols.get(f"{v}_i") and cols.get(f"{v}_f")]
        if not avail:
            st.error("No se detectaron pares de columnas de gases. Revisa el CSV original.")
            st.stop()
        var = st.radio("Variable", avail, horizontal=True)
        tests = f["_test_key"].tolist()
        default = tests[: min(8, len(tests))]
        chosen = st.multiselect(f"Ensayos a comparar (máx. {MAX_TESTS})", tests, default=default)
        if len(chosen) > MAX_TESTS:
            st.warning(f"Se muestran solo los primeros {MAX_TESTS} ensayos seleccionados.")
            chosen = chosen[:MAX_TESTS]

        sub = f[f["_test_key"].isin(chosen)]
        ok = sub.dropna(subset=[f"{var}_i_num", f"{var}_f_num"], how="all")
        excluded = len(sub) - len(ok)
        if excluded:
            st.caption(f"{excluded} ensayo(s) seleccionados no tienen medición numérica para esta variable.")
        if ok.empty:
            st.info("Selecciona ensayos con mediciones disponibles.")
        else:
            fig = go.Figure()
            fig.add_bar(x=ok["_test_key"], y=ok[f"{var}_i_num"], name="Inicial", marker_color=CYAN)
            fig.add_bar(x=ok["_test_key"], y=ok[f"{var}_f_num"], name="Final", marker_color=GOLD)
            fig.update_layout(
                barmode="group",
                title=f"{var} inicial vs. final por ensayo",
                xaxis_title="Ensayo (Test #)",
                yaxis_title="% en volumen" if var != "CO" else "CO (ppm)",
                xaxis=dict(type="category"),
            )
            show_plot(fig)
            chips("dato")
            source_caption()

            calc = ok[["_test_key"]].rename(columns={"_test_key": "Ensayo"}).copy()
            calc["Inicial"] = ok[f"{var}_i_num"].values
            calc["Final"] = ok[f"{var}_f_num"].values
            calc["Diferencia (final − inicial)"] = (calc["Final"] - calc["Inicial"]).round(3)
            st.markdown("**Diferencias aritméticas**")
            chips("calc")
            show_df(calc)
            st.caption("Valores ambiguos se excluyen de los cálculos, pero permanecen en la tabla original. La diferencia NO demuestra inflamabilidad.")
            st.download_button(
                "⬇️ Descargar tabla filtrada (CSV)",
                calc.to_csv(index=False).encode("utf-8"),
                file_name=f"wari_bass2_{var}.csv",
                mime="text/csv",
            )

    # ---- Ficha individual
    with tab_ficha:
        t = st.selectbox("Ensayo", f["_test_key"].tolist())
        row = bass[bass["_test_key"] == t].iloc[0]
        c1, c2, c3 = st.columns(3)
        kpi(c1, "Material", row[cols["material"]] if cols["material"] else "—")
        kpi(c2, "Investigador", row[cols["pi"]] if cols["pi"] else "—")
        kpi(c3, "Fecha", row[cols["date"]] if cols["date"] else "—")
        st.write("")
        rows = []
        for v in ("O2", "CO2", "CO"):
            if cols.get(f"{v}_i") and cols.get(f"{v}_f"):
                a, b = row[f"{v}_i_num"], row[f"{v}_f_num"]
                rows.append(
                    {
                        "Variable": v,
                        "Inicial (original)": row[cols[f"{v}_i"]],
                        "Final (original)": row[cols[f"{v}_f"]],
                        "Diferencia calculada": round(b - a, 3) if pd.notna(a) and pd.notna(b) else "No disponible",
                    }
                )
        show_df(pd.DataFrame(rows))
        chips("dato", "calc")
        hall = qc[qc["Ensayo"] == row["_test"]] if not qc.empty else qc
        if len(hall):
            st.warning("Este ensayo tiene hallazgos de calidad:")
            show_df(hall)
        else:
            st.info("No se detectaron alertas automáticas; esto no equivale a validación científica del ensayo.")
        st.markdown(
            '<div class="warn">Fan display y Air display son lecturas de pantalla. No deben interpretarse '
            "como velocidad física del aire sin conocer la calibración del instrumento.</div>",
            unsafe_allow_html=True,
        )
        source_caption()

    # ---- Control de calidad
    with tab_qc:
        st.markdown("Los valores **no se corrigen ni se eliminan**. Los textos ambiguos quedan fuera de cálculos. Las alertas estadísticas no prueban un error físico.")
        if qc.empty:
            st.success("No se detectaron hallazgos.")
        else:
            motivos = sorted(qc["Alerta"].unique())
            sel = st.multiselect("Tipo de alerta", motivos, default=motivos)
            show_df(qc[qc["Alerta"].isin(sel)])
            st.download_button(
                "⬇️ Descargar hallazgos (CSV)",
                qc.to_csv(index=False).encode("utf-8"),
                file_name="wari_bass2_control_calidad.csv",
                mime="text/csv",
            )
        chips("calc", "nd")
        source_caption()

    # ---- Tabla original
    with tab_tabla:
        original_cols = [str(c).strip() for c in pd.read_csv(BASS2_FILE, nrows=0).columns]
        show_df(f[original_cols])
        chips("dato")
        source_caption()

# ============================================================================
# COMPARACIÓN CIENTÍFICA
# ============================================================================
elif page.startswith("⚖️"):
    st.subheader("WARI Scientific Comparison")
    st.caption("Compara dos ensayos y separa lo respaldado de lo que no se puede concluir.")
    if bass is None:
        st.error("No se encontró `data/bass_ii_experimental.csv`.")
        st.stop()

    tests = bass["_test_key"].tolist()
    c1, c2 = st.columns(2)
    ta = c1.selectbox("Ensayo A", tests, index=0)
    tb = c2.selectbox("Ensayo B", tests, index=min(1, len(tests) - 1))
    if ta == tb:
        st.info("Elige dos ensayos distintos.")
        st.stop()

    ra = bass[bass["_test_key"] == ta].iloc[0]
    rb = bass[bass["_test_key"] == tb].iloc[0]
    original_cols = [str(c).strip() for c in pd.read_csv(BASS2_FILE, nrows=0).columns]

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
    show_df(pd.DataFrame(tabla))
    chips("dato")
    source_caption()

    # Estas cifras describen campos del CSV, no condiciones físicas controladas.
    condition_cols = [cols.get(k) for k in ("material", "fan", "air") if cols.get(k)]
    condition_equal = [c for c in condition_cols if c in iguales]
    condition_different = [c for c in condition_cols if c in diferentes]
    m1, m2, m3 = st.columns(3)
    kpi(m1, "Condiciones registradas iguales", len(condition_equal))
    kpi(m2, "Condiciones registradas distintas", len(condition_different))
    kpi(m3, "Campos incompletos (total)", len(faltan))
    st.caption("Condiciones consideradas: material, Fan display y Air display. No se incluye Test #, fecha ni PI como condiciones controladas. No supone comparabilidad física.")

    st.markdown("#### Qué resultados se pueden comparar numéricamente")
    comp = []
    for v in ("O2", "CO2", "CO"):
        if cols.get(f"{v}_i") and cols.get(f"{v}_f"):
            da = ra[f"{v}_f_num"] - ra[f"{v}_i_num"]
            db = rb[f"{v}_f_num"] - rb[f"{v}_i_num"]
            if pd.notna(da) and pd.notna(db):
                comp.append({"Variable": v, f"Δ A": round(da, 3), f"Δ B": round(db, 3), "Δ B − Δ A": round(db - da, 3)})
            else:
                comp.append({"Variable": v, "Δ A": "No disponible", "Δ B": "No disponible", "Δ B − Δ A": "—"})
    show_df(pd.DataFrame(comp))
    chips("calc")

    st.markdown("#### Qué conclusiones están respaldadas")
    chips("interp")
    st.markdown(
        "- Las diferencias aritméticas de la tabla anterior (resultado calculado a partir de datos originales).\n"
        "- Qué campos coinciden y cuáles difieren; no se infiere causalidad."
    )

    st.markdown("#### Qué limitaciones impiden una comparación directa")
    lim = []
    if cols["material"] and cols["material"] in diferentes:
        lim.append("Los materiales difieren: si además cambian otras condiciones, la diferencia no puede atribuirse solo al material.")
    if cols["pi"] and cols["pi"] in diferentes:
        lim.append("Los ensayos provienen de investigadores distintos: pueden usar procedimientos diferentes.")
    if cols["date"] and cols["date"] in diferentes:
        lim.append("Los ensayos se hicieron en fechas distintas: no se puede asumir un mismo montaje o calibración.")
    if faltan:
        lim.append("Faltan datos en: " + ", ".join(faltan[:6]) + (" …" if len(faltan) > 6 else "") + ".")
    lim.append("Fan/Air display no son velocidades físicas sin calibración documentada.")
    lim.append("La variación entre O₂ inicial y final no demuestra cuál material es más inflamable.")
    lim.append("Estos resultados corresponden a microgravedad: no se extrapolan directamente a gravedad lunar o marciana.")
    for item in lim:
        st.markdown(f"- {item}")
    chips("extra")

# ============================================================================
# SEGURIDAD ESPACIAL
# ============================================================================
elif page.startswith("🛰️"):
    st.subheader("Módulo de seguridad espacial")
    esc = st.selectbox(
        "Escenario",
        ["Hábitat lunar", "Estación espacial en órbita (microgravedad)", "Hábitat marciano"],
    )
    st.markdown(
        '<div class="warn"><b>Aviso científico:</b> los experimentos de microgravedad NO predicen directamente '
        "la combustión bajo gravedad lunar (≈1/6 g) o marciana (≈3/8 g). Esta sección indica qué investigaciones "
        "del catálogo son un punto de partida, no resultados validados para el escenario.</div>",
        unsafe_allow_html=True,
    )
    st.write("")
    if esc.startswith("Estación"):
        st.caption("Escenario con condiciones más cercanas a las de los experimentos (microgravedad).")
    else:
        chips("extra")
        st.caption("Toda aplicación a este escenario es una extrapolación que requiere justificación adicional.")

    if catalog is None:
        st.error("No se encontró `data/investigaciones.csv`.")
    else:
        st.markdown("#### Investigaciones del catálogo por área de seguridad")
        for area in sorted(catalog["area"].dropna().unique()):
            with st.expander(f"{area}", expanded=True):
                sub = catalog[catalog["area"] == area]
                cfg = {}
                if "fuente" in sub.columns:
                    cfg["fuente"] = st.column_config.LinkColumn("fuente", display_text="Abrir fuente")
                show_df(sub, column_config=cfg)
        chips("dato")

    st.markdown("#### Qué se puede y qué no se puede concluir")
    st.markdown(
        "- ✅ Identificar investigaciones NASA relacionadas con prevención, detección y supresión.\n"
        "- ✅ Consultar condiciones experimentales y mediciones originales de BASS-II.\n"
        "- ⚠️ Estimar inflamabilidad de un material lunar/marciano: requiere ensayos en esa gravedad.\n"
        "- ❌ Certificar materiales o predecir incendios reales sin validación científica."
    )

# ============================================================================
# METODOLOGÍA
# ============================================================================
else:
    st.subheader("Metodología y límites")
    st.markdown("**Clasificación de la información**")
    chips("dato")
    st.caption("Medición registrada en un archivo original de NASA PSI.")
    chips("calc")
    st.caption("Operación matemática (p. ej. final − inicial) sobre mediciones disponibles.")
    chips("interp")
    st.caption("Explicación sustentada en las condiciones registradas del experimento.")
    chips("extra")
    st.caption("Aplicación a otro entorno; requiere justificación adicional.")
    chips("nd")
    st.caption("Información que no puede recuperarse o verificarse.")

    st.markdown("**Tratamiento de datos**")
    st.markdown(
        "- Los valores originales se conservan. Solo números únicos claros se usan para calcular.\n"
        "- Celdas vacías, mixtas o ambiguas no se imputan ni se utilizan en cálculos.\n"
        "- Los atípicos se marcan (IQR y rango físico), no se eliminan.\n"
        "- Fan/Air display no se interpretan como velocidades físicas."
    )
    st.markdown("**Fuentes**")
    st.markdown(
        "- NASA Physical Sciences Informatics (PSI)\n"
        "- BASS-II: tabla experimental `PSI-25_Experimental table_BASS-II.csv`\n"
        "- Repositorio: https://github.com/stevenlaime17-stack/wari-fire-ai"
    )
    st.markdown("**Equipo:** Wari Teams · Ayacucho, Perú · NASA International Space Apps Challenge 2026")
