"""WARI FIRE AI — app.py completo, edición de legibilidad y catálogo (Fase 14).
Requiere los otros módulos .py existentes en la carpeta principal.
Los gráficos BASS-II utilizan únicamente datos originales o diferencias descriptivas.
"""

import re
from html import escape
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from simulator import render_simulator
from assistant_evidence import render_assistant
from reports import render_reports
from jury_demo import render_jury_demo
from database_expansion import render_database_expansion
from expanded_experiments import render_expanded_experiments
from multi_study import render_multi_study, local_counts

BASE = Path(__file__).resolve().parent
DATA = BASE / "data"
CATALOG_FILE = DATA / "investigaciones.csv"
BASS_FILE = DATA / "bass_ii_experimental.csv"
LOGO = BASE / "assets" / "logo.png"
NASA_PSI = "https://psi.nasa.gov/physci/repo/search?data_source=psi&data_type=investigation"
NASA_BASS = "https://psi.nasa.gov/physci/repo/data/investigations/PSI-25"

st.set_page_config(page_title="WARI FIRE AI", page_icon="🔥", layout="wide", initial_sidebar_state="expanded")
st.markdown("""
<style>
:root{--bg:#080e1b;--card:#14253d;--line:#365473;--ink:#f8fbff;--muted:#b7cadf;
 --cyan:#46d9ff;--orange:#ff9852}
[data-testid="stAppViewContainer"]{background-color:var(--bg)!important;
 background-image:radial-gradient(circle,rgba(255,255,255,.43) 1px,transparent 1.8px),
 radial-gradient(circle,rgba(146,207,255,.26) 1px,transparent 1.8px),
 linear-gradient(125deg,#080e1b,#152237 75%,#0c1728)!important;
 background-size:191px 167px,299px 251px,cover!important;color:var(--ink)!important}
[data-testid="stHeader"]{background:rgba(8,14,27,.89)!important}
[data-testid="stSidebar"]{background:linear-gradient(160deg,#172237,#0b1321)!important;
 border-right:1px solid #344b68!important}
[data-testid="stSidebar"] *{color:var(--ink)}
.block-container{max-width:1320px!important;padding-top:3.9rem!important}
h1,h2,h3,h4,p,li,label{color:var(--ink)}
[data-testid="stCaptionContainer"] p{color:var(--muted)!important}
/* Control de contraste: reemplaza las reglas antiguas de botones blancos. */
div[data-testid="stButton"] button,div[data-testid="stDownloadButton"] button,
.stButton button,.stDownloadButton button,
div[data-testid="stLinkButton"] a{background:#163c5d!important;color:#fff!important;
 border:1px solid #49bfe5!important;border-radius:11px!important;font-weight:750!important}
div[data-testid="stButton"] button *,div[data-testid="stDownloadButton"] button *,
.stButton button *, .stDownloadButton button *,div[data-testid="stLinkButton"] a *{color:#fff!important}
div[data-testid="stButton"] button:hover,div[data-testid="stDownloadButton"] button:hover,
div[data-testid="stLinkButton"] a:hover{background:#245f87!important;border-color:#ff9852!important}
[data-testid="stTabs"] button{color:#eef8ff!important}
[data-testid="stMetric"]{background:rgba(19,38,65,.96);border:1px solid #365473;
 border-radius:12px;padding:15px}
[data-testid="stMetric"] *{color:#fff!important}
[data-testid="stDataFrame"]{border:1px solid #365473;border-radius:12px}
[data-baseweb="select"] [role="combobox"]{color:#fff!important}
[data-baseweb="select"] [role="combobox"] *{color:#fff!important}
.stTextInput input,.stTextArea textarea{background:#182b44!important;color:#fff!important;
 border:1px solid #53708a!important}
.hero-wari{position:relative;overflow:hidden;padding:36px 38px;border:1px solid #526d88;
 border-radius:22px;background:linear-gradient(115deg,#0e182a 0%,#182b45 69%,#244f72 100%);
 min-height:250px;box-shadow:0 15px 40px rgba(0,0,0,.28)}
.hero-wari:after{content:"";position:absolute;right:-115px;top:-130px;width:435px;height:435px;
 border-radius:50%;background:radial-gradient(circle at 40% 40%,#68a5dc,#183b60 47%,#091627 75%);
 box-shadow:0 0 45px #3b7fa344;border:1px solid #6792b077;opacity:.8}
.hero-wari>div{position:relative;z-index:2;max-width:75%}
.hero-wari h1{font-size:clamp(2.1rem,4.1vw,3.6rem);line-height:1.1;color:#fff!important;
 margin:10px 0!important;font-weight:900}
.hero-wari h1 em{color:#ff9446;font-style:normal}
.hero-wari p{color:#f1f6ff!important;font-size:1.06rem;max-width:740px;line-height:1.7}
.tag-wari{color:#abe9ff;letter-spacing:.11em;font-size:.75rem;font-weight:850}
.panel-wari{padding:16px 18px;border:1px solid #436283;border-radius:15px;
 background:#11223b;margin:8px 0;min-height:125px}
.panel-wari h3{margin:0 0 7px!important;color:#fff!important;font-size:1rem}
.panel-wari p{margin:0!important;color:#c9daeb!important;font-size:.88rem;line-height:1.55}
.notice-wari{padding:12px 17px;border:1px solid #455e76;border-left:4px solid #46d9ff;
 border-radius:12px;background:#14243b;margin:13px 0;color:#e8f5ff}
@media(max-width:850px){.hero-wari{padding:25px 21px;min-height:260px}
 .hero-wari>div{max-width:100%}.hero-wari:after{opacity:.18}.block-container{padding-top:3rem!important}}
</style>""", unsafe_allow_html=True)

LANG = {
 "Español": {
  "nav":"Navegación","home":"🏠 Página de inicio","dash":"📊 Panel general",
  "library":"📚 Biblioteca NASA","atlas":"🗃️ Atlas NASA PSI","expanded":"🧬 Experimentos ampliados","more":"🧪 Más experimentos NASA",
  "explorer":"📈 Explorador BASS-II","compare":"⚖️ Comparación científica",
  "sim":"🔥 Simulador educativo","space":"🛰️ Seguridad espacial",
  "assistant":"🤖 Asistente WARI AI","reports":"📄 Informes científicos",
  "jury":"🚀 Modo jurado","method":"🧪 Metodología",
  "hero":"Inteligencia para la <em>seguridad espacial</em>",
  "desc":"Explora datos originales de combustión en microgravedad, compara ensayos NASA PSI y aprende a distinguir observaciones de predicciones.",
  "cat":"Estudios catalogados","tests":"Ensayos BASS-II","pis":"Investigadores",
  "flags":"Alertas de calidad","summary":"Panorama de la investigación",
  "family":"Familias con mediciones locales","modules":"Explora la plataforma",
  "look":"Buscar por nombre, área o descripción","area":"Área de investigación",
  "fuel":"Tipo de combustible","material":"Buscar material","pi":"Investigador",
  "gas":"Gas registrado","choose":"Selecciona ensayos","source":"Fuente NASA",
  "init":"Inicial","end":"Final","delta":"Final − inicial",
  "chart":"Gráfico de mediciones iniciales y finales","table":"Tabla de valores",
  "quality":"Control de calidad","original":"Datos originales","details":"Ficha",
  "none":"No hay datos para esta selección.","limit":"Máximo 20 ensayos en el gráfico.",
  "disclaimer":"Las diferencias son descriptivas; no demuestran causalidad, inflamabilidad ni riesgo de incendio.",
  "missing":"Faltan archivos necesarios.","read":"Lecturas experimentales NASA PSI",
  "about":"Las llamas educativas son ilustraciones conceptuales. Los análisis numéricos usan mediciones originales BASS-II; no son simulaciones físicas validadas.",
  "download":"Descargar tabla CSV","compare_help":"Selecciona dos ensayos distintos y una variable.",
  "same":"Coincide","different":"Diferente","empty":"Sin dato",
  "guide":"Filtra por material o investigador, selecciona hasta 20 ensayos y compara sus lecturas.",
  "steps":"Metodología y transparencia","button_sim":"Abrir simulador educativo"
 },
 "English": {
  "nav":"Navigation","home":"🏠 Home","dash":"📊 Dashboard",
  "library":"📚 NASA Library","atlas":"🗃️ NASA PSI Data Atlas","expanded":"🧬 Expanded experiments","more":"🧪 More NASA experiments",
  "explorer":"📈 BASS-II Explorer","compare":"⚖️ Scientific Comparison",
  "sim":"🔥 Educational Simulator","space":"🛰️ Space Fire Safety",
  "assistant":"🤖 WARI AI Assistant","reports":"📄 Scientific Reports",
  "jury":"🚀 Jury Mode","method":"🧪 Methodology",
  "hero":"Intelligence for <em>space fire safety</em>",
  "desc":"Explore original microgravity combustion data, compare NASA PSI tests, and learn to distinguish observations from predictions.",
  "cat":"Cataloged studies","tests":"BASS-II tests","pis":"Researchers",
  "flags":"Quality flags","summary":"Research overview",
  "family":"Families with local measurements","modules":"Explore the platform",
  "look":"Search by name, field or description","area":"Research area",
  "fuel":"Fuel or sample type","material":"Search material","pi":"Researcher",
  "gas":"Recorded gas","choose":"Select tests","source":"NASA source",
  "init":"Initial","end":"Final","delta":"Final − initial",
  "chart":"Initial and final measurements","table":"Readings table",
  "quality":"Quality control","original":"Original data","details":"Test details",
  "none":"No data available for this selection.","limit":"Maximum 20 tests per chart.",
  "disclaimer":"Differences are descriptive; they do not establish causation, flammability, or fire risk.",
  "missing":"Required files are missing.","read":"NASA PSI experimental readings",
  "about":"Educational flame illustrations are conceptual. Numeric analyses use original BASS-II measurements, not validated physical simulations.",
  "download":"Download CSV table","compare_help":"Select two different tests and one measurement.",
  "same":"Match","different":"Different","empty":"Unavailable",
  "guide":"Filter by material or researcher, select up to 20 tests, and compare recorded readings.",
  "steps":"Methods and transparency","button_sim":"Open educational simulator"
 }
}

# Cargamos el catálogo en cada ejecución: 17 filas son ligeras y esto evita
# que Streamlit conserve los 3 registros antiguos en la caché.
def load_catalog():
    if not CATALOG_FILE.exists():
        return None
    df = pd.read_csv(CATALOG_FILE, encoding="utf-8-sig")
    required = {"experimento", "area", "combustible", "descripcion", "fuente"}
    if not required.issubset(df.columns):
        return None
    return df


def translated_catalog(df):
    """Read English research descriptions from the existing NASA PSI Atlas CSV."""
    if not english:
        return df.copy()
    path = DATA / "psi_investigaciones_detalle.csv"
    if not path.exists():
        return df.copy()
    details = pd.read_csv(path, encoding="utf-8-sig")
    required = {"investigacion", "area_en", "tipo_en", "descripcion_en"}
    if not required.issubset(details.columns):
        return df.copy()
    trans = details[["investigacion", "area_en", "tipo_en", "descripcion_en"]].copy()
    trans = trans.rename(columns={"investigacion": "experimento"})
    merged = df.merge(trans, on="experimento", how="left")
    for target, translated in (("area", "area_en"), ("combustible", "tipo_en"),
                               ("descripcion", "descripcion_en")):
        merged[target] = merged[translated].where(
            merged[translated].notna() & (merged[translated].astype(str).str.strip() != ""),
            merged[target])
    return merged[df.columns]


def col_matching(df, required, excluded=()):
    for col in df.columns:
        tokens = set(re.findall(r"[a-z0-9]+", col.casefold()))
        if all(w in tokens for w in required) and not any(w in tokens for w in excluded):
            return col
    return None


def strict_value(value):
    if pd.isna(value) or not str(value).strip():
        return float("nan"), "missing"
    raw = str(value).strip()
    if raw.casefold() in {"none", "na", "n/a", "null", "-", "--", "nan"}:
        return float("nan"), "missing"
    if not re.fullmatch(r"[+-]?(?:\d+(?:[.,]\d*)?|[.,]\d+)", raw):
        return float("nan"), "ambiguous"
    return float(raw.replace(",", ".")), "ok"


def load_bass():
    if not BASS_FILE.exists():
        return None, {}
    df = pd.read_csv(BASS_FILE, encoding="utf-8-sig")
    df.columns = [str(c).strip() for c in df.columns]
    cols = {
        "test": col_matching(df, ("test",)),
        "pi": col_matching(df, ("pi",)),
        "date": col_matching(df, ("date",)),
        "material": col_matching(df, ("fuel", "material")),
        "fan": col_matching(df, ("fan",)),
        "air": col_matching(df, ("air",)),
        "O2_i": col_matching(df, ("o2", "initial")),
        "O2_f": col_matching(df, ("o2", "final")),
        "CO2_i": col_matching(df, ("co2", "initial")),
        "CO2_f": col_matching(df, ("co2", "final")),
        "CO_i": col_matching(df, ("co", "initial"), ("co2", "o2")),
        "CO_f": col_matching(df, ("co", "final"), ("co2", "o2")),
    }
    if cols["test"] is None:
        st.error("Missing BASS-II test ID column / Falta el identificador de ensayos.")
        return None, cols
    df["_test"] = df[cols["test"]].astype(str).str.strip()
    df["_test_key"] = (df["_test"] if not df["_test"].duplicated().any()
                         else df["_test"] + " · row " + (df.index + 2).astype(str))
    for gas in ("O2", "CO2", "CO"):
        for phase in ("i", "f"):
            key = f"{gas}_{phase}"
            if cols.get(key):
                parsed = df[cols[key]].map(strict_value)
                df[f"{key}_num"] = parsed.map(lambda pair: pair[0])
                df[f"{key}_flag"] = parsed.map(lambda pair: pair[1])
    return df, cols


def get_alerts(df, cols):
    alerts = []
    if df is None:
        return pd.DataFrame(columns=["Ensayo", "Variable", "Valor original", "Alerta"])
    for gas in ("O2", "CO2", "CO"):
        for phase in ("i", "f"):
            key = f"{gas}_{phase}"
            if not cols.get(key):
                continue
            numeric = df[f"{key}_num"]
            valid = numeric.dropna()
            q1, q3 = (valid.quantile(.25), valid.quantile(.75)) if len(valid) else (0, 0)
            spread = q3 - q1
            lo, hi = q1 - 1.5 * spread, q3 + 1.5 * spread
            for idx in df.index:
                v = numeric.loc[idx]
                flag = df.loc[idx, f"{key}_flag"]
                notes = []
                if flag == "missing":
                    notes.append("Missing value" if english else "Dato ausente")
                elif flag == "ambiguous":
                    notes.append("Ambiguous text" if english else "Texto ambiguo")
                if pd.notna(v):
                    if gas != "CO" and not 0 <= v <= 100:
                        notes.append("Outside 0–100%" if english else "Fuera de 0–100 %")
                    if spread > 0 and not lo <= v <= hi:
                        notes.append("IQR outlier" if english else "Atípico (IQR)")
                for note in notes:
                    alerts.append({"Ensayo": df.loc[idx, "_test"], "Variable": key,
                                   "Valor original": df.loc[idx, cols[key]], "Alerta": note})
    return pd.DataFrame(alerts, columns=["Ensayo", "Variable", "Valor original", "Alerta"])


def textmetric(col, label, value):
    col.metric(label, value)


def display_frame(frame):
    try:
        st.dataframe(frame, hide_index=True, width="stretch")
    except TypeError:
        st.dataframe(frame, hide_index=True, use_container_width=True)


def graph(frame, gas, id_field="_test_key"):
    if frame.empty:
        st.info(t["none"])
        return
    fig = go.Figure()
    for phase, color, label in (("i", "#46d9ff", t["init"]),
                                ("f", "#ff9852", t["end"])):
        fig.add_bar(x=frame[id_field], y=frame[f"{gas}_{phase}_num"], name=label, marker_color=color)
    fig.update_layout(template="plotly_dark", barmode="group", height=380,
                      paper_bgcolor="#102038", plot_bgcolor="#102038",
                      xaxis_title=t["tests"], yaxis_title="ppm" if gas == "CO" else "% vol.")
    st.plotly_chart(fig, use_container_width=True)


with st.sidebar:
    if LOGO.exists():
        st.image(str(LOGO), width=112)
    st.markdown("### WARI FIRE AI")
    st.caption("Flame in Freefall · NASA Space Apps Challenge 2026")
    language = st.selectbox("🌐 Language / Idioma", ["Español", "English"], key="language")
    t = LANG[language]
    nav = {
        "home": t["home"], "dashboard": t["dash"], "library": t["library"],
        "database": t["atlas"],
        "expanded":t["expanded"], "more":t["more"], "explorer": t["explorer"], "compare": t["compare"],
        "simulator": t["sim"], "space": t["space"], "assistant": t["assistant"],
        "reports": t["reports"], "jury": t["jury"], "method": t["method"],
    }
    page = st.radio(t["nav"], list(nav), format_func=lambda p: nav[p], key="section_choice")
    st.divider()
    st.caption("Wari Teams · Ayacucho, Perú")
    st.caption("Prototype · Not a certified fire-safety system")

english = language == "English"
catalog = load_catalog()
bass, cols = load_bass()
qc = get_alerts(bass, cols)


def jump(section):
    st.session_state.section_choice = section


def metrics():
    # All totals refer to locally installed *source rows*, never invented experiments.
    bass_rows = len(bass) if bass is not None else 0
    flex_rows = 0
    try:
        from expanded_experiments import _load_local
        _, flex_df, _ = _load_local()
        if flex_df is not None:
            flex_rows = len(flex_df)
    except (OSError, ValueError, pd.errors.ParserError):
        pass
    extra_counts = local_counts()
    total_rows = bass_rows + flex_rows + sum(extra_counts.values())
    families = int(bass_rows > 0) + int(flex_rows > 0) + sum(int(x > 0) for x in extra_counts.values())
    a, b, c, d = st.columns(4)
    textmetric(a, t["cat"], len(catalog) if catalog is not None else "—")
    textmetric(b, "Filas locales / Local rows", total_rows)
    textmetric(c, "Familias con datos / Data families", families)
    textmetric(d, t["flags"] + " (BASS-II)", len(qc))


if page == "home":
    st.markdown(f"""<div class="hero-wari"><div><div class="tag-wari">WARI TEAMS · NASA PSI · 2026</div>
    <h1>WARI FIRE AI<br>{t['hero']}</h1><p>{escape(t['desc'])}</p></div></div>""", unsafe_allow_html=True)
    buttons = st.columns(4)
    for col, key in zip(buttons, ("explorer", "library", "dashboard", "simulator")):
        col.button(nav[key], on_click=jump, args=(key,), use_container_width=True)
    st.subheader(t["summary"])
    metrics()
    st.caption("NASA PSI · Local curated inventory; other catalog studies are metadata-only.")
    st.subheader(t["modules"])
    items = [("more", "🧪"), ("expanded", "🧬"), ("database", "NASA PSI"), ("explorer", "BASS-II"),
             ("simulator", "🔥"), ("reports", "PDF"),
             ("assistant", "🤖"), ("jury", "🚀")]
    for offset in (0, 3, 6):
        cc = st.columns(3)
        for j, (code, icon) in enumerate(items[offset:offset + 3]):
            with cc[j]:
                st.markdown(f'<div class="panel-wari"><h3>{icon} {escape(nav[code])}</h3>'
                            f'<p>{escape(t["about"] if code == "simulator" else t["desc"])}</p></div>',
                            unsafe_allow_html=True)
                st.button(nav[code], on_click=jump, args=(code,), use_container_width=True,
                          key="home_" + code)
    st.info(t["about"])

elif page == "dashboard":
    st.title(t["dash"])
    metrics()
    if bass is not None and cols.get("pi"):
        counts = bass[cols["pi"]].fillna("Unknown").astype(str).value_counts()
        fig = go.Figure(go.Bar(x=counts.values, y=counts.index, orientation="h", marker_color="#46d9ff"))
        fig.update_layout(template="plotly_dark", height=350, xaxis_title=t["tests"], yaxis_title="")
        st.plotly_chart(fig, use_container_width=True)
    st.link_button(t["source"], NASA_BASS)
    st.caption(t["about"])

elif page == "library":
    st.title(t["library"])
    if catalog is None:
        st.error(t["missing"] + " data/investigaciones.csv")
    else:
        query = st.text_input(t["look"], placeholder="FLEX, SAME, BASS, SAFFIRE...")
        subset = translated_catalog(catalog)
        areas = sorted(subset["area"].dropna().astype(str).unique())
        area_selected = st.multiselect(t["area"], areas, default=areas)
        subset = subset[subset["area"].isin(area_selected)]
        if query.strip():
            searchable = subset.astype(str).agg(" ".join, axis=1)
            subset = subset[searchable.str.contains(query, case=False, regex=False, na=False)]
        st.metric(t["cat"], len(subset))
        display_frame(subset)
        st.caption(("Descriptions are catalog metadata, not test measurements." if english else
                    "Las fichas bibliográficas no equivalen a mediciones experimentales."))
        st.download_button(t["download"], subset.to_csv(index=False).encode("utf-8-sig"),
                           "wari_catalogo.csv", "text/csv")

elif page == "database":
    render_database_expansion(language)

elif page == "expanded":
    render_expanded_experiments(language)

elif page == "more":
    render_multi_study(language)

elif page == "explorer":
    st.title(t["explorer"])
    st.info(t["guide"])
    if bass is None:
        st.error(t["missing"] + " data/bass_ii_experimental.csv")
    else:
        c1, c2 = st.columns(2)
        pis = sorted(bass[cols["pi"]].dropna().astype(str).unique()) if cols.get("pi") else []
        pi_selection = c1.multiselect(t["pi"], pis, default=pis)
        material_query = c2.text_input(t["material"], placeholder="PMMA...")
        subset = bass.copy()
        if cols.get("pi"):
            subset = subset[subset[cols["pi"]].astype(str).isin(pi_selection)]
        if material_query and cols.get("material"):
            subset = subset[subset[cols["material"]].astype(str).str.contains(
                material_query, case=False, regex=False, na=False)]
        a, b = st.columns(2)
        a.metric(t["tests"], len(subset))
        b.metric("IDs", subset["_test"].nunique())
        tabs = st.tabs([t["chart"], t["details"], t["quality"], t["original"]])
        with tabs[0]:
            gas = st.selectbox(t["gas"], ["O2", "CO2", "CO"])
            ids = subset["_test_key"].tolist()
            selected = st.multiselect(t["choose"], ids, default=ids[:min(8, len(ids))])
            if len(selected) > 20:
                st.warning(t["limit"])
                selected = selected[:20]
            sample = subset[subset["_test_key"].isin(selected)]
            if not sample.empty and f"{gas}_i_num" in sample and f"{gas}_f_num" in sample:
                graph(sample, gas)
                table = pd.DataFrame({"Test": sample["_test_key"],
                                      t["init"]: sample[f"{gas}_i_num"],
                                      t["end"]: sample[f"{gas}_f_num"]})
                table[t["delta"]] = (table[t["end"]] - table[t["init"]]).round(3)
                display_frame(table)
                st.download_button(t["download"], table.to_csv(index=False).encode("utf-8-sig"),
                                   f"wari_{gas}.csv", "text/csv")
                st.warning(t["disclaimer"])
            else:
                st.info(t["none"])
        with tabs[1]:
            ids = subset["_test_key"].tolist()
            if ids:
                test_id = st.selectbox(t["choose"], ids, key="detail_test")
                record = subset.loc[subset["_test_key"] == test_id].iloc[0]
                meta = {"Test": record["_test"],
                        "Material": record[cols["material"]] if cols.get("material") else "—",
                        "PI": record[cols["pi"]] if cols.get("pi") else "—"}
                st.json(meta)
                rows = []
                for gas in ("O2", "CO2", "CO"):
                    ki, kf = cols.get(gas + "_i"), cols.get(gas + "_f")
                    if ki and kf:
                        rows.append({"Gas": gas, t["init"]: record[ki], t["end"]: record[kf]})
                display_frame(pd.DataFrame(rows))
            else:
                st.info(t["none"])
        with tabs[2]:
            display_frame(qc[qc["Ensayo"].isin(subset["_test"])])
            st.caption("Quality flags are not certified errors." if english else
                       "Las alertas automáticas no son errores certificados.")
        with tabs[3]:
            original_columns = list(pd.read_csv(BASS_FILE, nrows=0, encoding="utf-8-sig").columns)
            display_frame(subset[[c for c in original_columns if c in subset.columns]])
        st.link_button(t["source"], NASA_BASS)

elif page == "compare":
    st.title(t["compare"])
    st.info(t["compare_help"])
    if bass is None or len(bass) < 2:
        st.error(t["missing"])
    else:
        ids = bass["_test_key"].tolist()
        left, right, third = st.columns([1, 1, .8])
        first = left.selectbox("A", ids, index=ids.index("B1") if "B1" in ids else 0)
        second = right.selectbox("B", ids, index=ids.index("B4") if "B4" in ids else 1)
        gas = third.selectbox(t["gas"], ["O2", "CO2", "CO"])
        if first == second:
            st.warning("Selecciona ensayos diferentes." if not english else "Choose different tests.")
        else:
            pair = bass[bass["_test_key"].isin([first, second])].copy()
            pair["_sort"] = pair["_test_key"].map({first: 0, second: 1})
            pair = pair.sort_values("_sort")
            rows = []
            for _, r in pair.iterrows():
                ini = r.get(gas + "_i_num", float("nan"))
                fin = r.get(gas + "_f_num", float("nan"))
                rows.append({"Test": r["_test"], "Material": r[cols["material"]] if cols.get("material") else "—",
                             t["init"]: ini, t["end"]: fin,
                             t["delta"]: fin - ini if pd.notna(ini) and pd.notna(fin) else float("nan")})
            display_frame(pd.DataFrame(rows))
            graph(pair, gas)
            st.warning(t["disclaimer"])
            st.link_button(t["source"], NASA_BASS)

elif page == "simulator":
    render_simulator(language)

elif page == "space":
    st.title(t["space"])
    st.warning(t["disclaimer"])
    scene = st.selectbox("Scenario / Escenario", ["Estación espacial / Space station",
                                                   "Luna / Moon", "Marte / Mars"])
    st.info(("Study fire detection, material behavior, oxygen and airflow. "
             "No predictions are provided for " if english else
             "Analiza detección, materiales, oxígeno y ventilación. No se predicen incendios para ") + scene)
    if catalog is not None:
        display_frame(catalog[["experimento", "area", "descripcion", "fuente"]])
    st.link_button(t["source"], NASA_PSI)

elif page == "assistant":
    render_assistant(bass, cols, catalog, language)

elif page == "reports":
    render_reports(bass, cols, language)

elif page == "jury":
    render_jury_demo(bass, cols, language)

elif page == "method":
    st.title(t["steps"])
    st.markdown("""**1. NASA PSI → 2. Original CSV → 3. Strict number parsing → 4. Charts and reports.**""")
    st.info(t["about"])
    st.warning(t["disclaimer"])
    if catalog is not None:
        st.metric(t["cat"], len(catalog))
    if bass is not None:
        st.metric(t["tests"], len(bass))
    st.link_button(t["source"], NASA_PSI)
    st.caption("WARI TEAMS · NASA Space Apps Challenge · Ayacucho, Perú")
