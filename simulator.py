"""WARI FIRE LAB 8.0 — módulo educativo bilingüe para WARI FIRE AI.

Visualización conceptual: NO es un solucionador físico o simulación NASA validada.
Los números experimentales se leen únicamente del archivo NASA PSI BASS-II.
"""
from pathlib import Path
import math
import re
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

HERE = Path(__file__).resolve().parent
CSV = HERE / "data" / "bass_ii_experimental.csv"
NASA_SOURCE = "NASA PSI · BASS-II · PSI-25_Experimental table_BASS-II.csv"
NASA_URL = "https://www.nasa.gov/physical-sciences-informatics-psi/psi-investigations-by-research-area/"
DARK = "#101621"
ORANGE = "#FF9B54"
BLUE = "#62D4FF"
GOLD = "#FFD58C"
WHITE = "#F5F7FC"
COL = {
    "id":"Test #", "pi":"PI", "date":"Date", "material":"Fuel Sample Material",
    "fan":"Fan display", "air":"Air display",
    "o2a":"Calibrated  initial O2 % by vol", "o2b":"Calibrated final O2 % by vol",
    "co2a":"Initial CO2 % by vol", "co2b":"Final CO2 % by vol",
    "coa":"Initial CO (ppm)", "cob":"Final CO (ppm)",
}
NUM = re.compile(r"^[+-]?(?:\d+(?:[.,]\d*)?|[.,]\d+)$")
T = {
 "es":{
  "hero":"WARI FIRE LAB", "subtitle":"Aprende cómo cambia la combustión en el espacio a través de comparaciones visuales y evidencia real de NASA PSI.",
  "intro":"Empieza desde cero. No necesitas saber química ni programación.",
  "warning":"La escena de llamas es una ILUSTRACIÓN EDUCATIVA, no una predicción física. Los gráficos de la pestaña Datos NASA se calculan exclusivamente con registros de BASS-II.",
  "tabs":["📖 1. Aprende","🔥 2. Experimenta","📊 3. Datos NASA","🎯 4. Misión de aprendizaje"],
  "learn_title":"¿Por qué el fuego cambia en el espacio?", "triangle":"Tres ingredientes importantes del fuego",
  "fuel":"Combustible", "fuel_desc":"Material que puede arder: por ejemplo, telas o ciertos plásticos.",
  "oxygen":"Oxígeno", "oxygen_desc":"Gas que participa en la combustión; no todos los materiales reaccionan igual.",
  "heat":"Calor", "heat_desc":"Debe existir una fuente de energía suficiente para iniciar una combustión.",
  "earth":"Tierra", "micro":"Microgravedad", "moon":"Luna", "mars":"Marte",
  "earth_caption":"La flotabilidad suele elevar los gases calientes. La llama puede verse alargada.",
  "micro_caption":"Al reducirse la flotabilidad, con flujo débil algunas llamas pueden ser más redondeadas.",
  "learn_q":"¿Por qué se ven diferentes?", "learn_a":"La gravedad terrestre genera convección natural por flotabilidad. En microgravedad ese mecanismo se reduce, y adquieren mayor importancia la difusión y la ventilación forzada. La forma también depende del combustible y de la atmósfera.",
  "science":"Dato clave: las llamas reales no tienen siempre la misma forma; las imágenes son esquemas, no grabaciones de un experimento.",
  "controls":"Controles de la escena", "gravity":"Entorno gravitacional", "oxygen_pct":"Oxígeno de la atmósfera (%)", "airflow":"Ventilación ilustrativa", "air_opts":["Baja","Media","Alta"],
  "run":"▶ Ejecutar visualización", "reset":"↺ Restablecer", "comparison":"Comparación visual de llamas", "results":"Resultados y explicación",
  "not_run":"Selecciona las condiciones y pulsa Ejecutar visualización.",
  "air_note":"La corriente de aire se representa con una ligera inclinación artística. No se calcula una velocidad real ni una tasa de combustión.",
  "o2_note":"El porcentaje de O₂ es un escenario seleccionado. No se usa para estimar temperatura, luminosidad, tamaño de llama o peligro de incendio.",
  "micro_why":"En microgravedad disminuye la convección por flotabilidad. La difusión y el flujo forzado pueden determinar el transporte de oxígeno y productos de combustión.",
  "earth_why":"En la Tierra, el ascenso de gases calientes contribuye a alargar la llama. No es una regla universal para todos los combustibles y flujos.",
  "moon_why":"En la Luna hay gravedad parcial. Este dibujo no reproduce datos lunares; no se pueden extrapolar directamente resultados de BASS-II.",
  "mars_why":"En Marte la gravedad es parcial. La atmósfera interior de un hábitat sería una condición esencial de cualquier análisis real.",
  "limit":"Este módulo no calcula inflamabilidad, probabilidad de incendio, temperatura, propagación ni tiempo de extinción.",
  "picked":"Escenario elegido", "visual":"Vista esquemática", "no_scale":"Ilustración · sin escala física",
  "nasa_title":"Ahora observa mediciones auténticas de NASA", "nasa_desc":"BASS-II contiene pruebas de combustión de sólidos en microgravedad. Aquí mostramos valores del CSV original, sin completar datos ausentes ni inventar mediciones.",
  "find":"Buscar material", "pi":"Investigador", "all":"Todos", "gas":"Gas a comparar", "test":"Selecciona hasta 2 ensayos", "table":"Datos originales del ensayo", "initial":"Inicial", "final":"Final", "change":"Cambio (final − inicial)", "missing":"No hay registros que coincidan con estos filtros.",
  "data_limit":"Una diferencia entre lecturas iniciales y finales no determina por sí sola inflamabilidad, causa física ni tasa de combustión. Fan display y Air display no equivalen automáticamente a m/s.",
  "source":"Fuente: NASA PSI · tabla BASS-II (CSV local procedente de PSI-25).", "download":"Descargar resultados seleccionados (.csv)",
  "mission":"Misión: investiga antes de recomendar", "scenario":"Tu equipo está preparando un estudio para un futuro hábitat lunar. Quiere saber qué se puede afirmar sobre un material a partir de BASS-II.",
  "question1":"¿Qué debes comprobar primero?", "options1":["Que la figura animada se vea realista.","Qué material y condiciones se registraron en los ensayos NASA.","Que una IA garantice que nunca habrá incendios."],
  "question2":"Si el oxígeno final es menor que el inicial, ¿qué conclusión es defendible?", "options2":["El material ya está certificado como peligroso.","Existe una diferencia registrada, pero hace falta más evidencia para explicar su causa.","La gravedad lunar produce exactamente ese cambio."],
  "question3":"¿Puede el dibujo del simulador predecir un incendio lunar?", "options3":["Sí, porque muestra una llama.","Sí, solo con seleccionar 30 % de oxígeno.","No, porque no incorpora un modelo validado para gravedad parcial."],
  "check":"Comprobar mis respuestas", "score":"Resultado del reto", "right":"¡Bien! Has diferenciado observaciones, explicaciones y extrapolaciones.", "retry":"Revisa las respuestas. Una imagen conceptual no sustituye las mediciones ni la validación científica.",
  "takeaway":"Lo que aprendiste", "takeaway_text":"El fuego necesita condiciones de combustión; la gravedad afecta el transporte de gases; NASA PSI permite estudiar registros reales, pero no garantiza la seguridad de un hábitat lunar.",
  "footer":"WARI Teams · NASA Space Apps Challenge 2026 · Herramienta educativa, no certificada para decisiones de seguridad.",
 },
 "en":{
  "hero":"WARI FIRE LAB", "subtitle":"Learn how combustion changes in space through visual comparisons and real NASA PSI evidence.",
  "intro":"Start from zero. No chemistry or programming background required.",
  "warning":"Flame scenes are EDUCATIONAL ILLUSTRATIONS, not physical predictions. NASA Data charts use BASS-II records only.",
  "tabs":["📖 1. Learn","🔥 2. Experiment","📊 3. NASA Data","🎯 4. Learning mission"],
  "learn_title":"Why does fire behave differently in space?", "triangle":"Three important ingredients for fire",
  "fuel":"Fuel", "fuel_desc":"A material that can burn, such as fabric or certain plastics.",
  "oxygen":"Oxygen", "oxygen_desc":"A gas involved in combustion; materials respond differently.",
  "heat":"Heat", "heat_desc":"Enough activation energy must be supplied to initiate combustion.",
  "earth":"Earth", "micro":"Microgravity", "moon":"Moon", "mars":"Mars",
  "earth_caption":"Buoyancy usually causes hot gases to rise. Flames can appear elongated.",
  "micro_caption":"With weak flow and little buoyancy, some flames can appear more rounded.",
  "learn_q":"Why do they look different?", "learn_a":"Earth gravity creates buoyancy-driven natural convection. In microgravity this effect is reduced, so diffusion and forced ventilation matter more. Flame shape also depends on fuel and atmosphere.",
  "science":"Key point: real flames do not always have the same shape. These illustrations are not experiment recordings.",
  "controls":"Scene controls", "gravity":"Gravity environment", "oxygen_pct":"Atmospheric oxygen (%)", "airflow":"Illustrative ventilation", "air_opts":["Low","Medium","High"],
  "run":"▶ Run visualization", "reset":"↺ Reset", "comparison":"Visual flame comparison", "results":"Results and explanation",
  "not_run":"Choose settings and press Run visualization.",
  "air_note":"Airflow is depicted by a slight artistic tilt; the system does not calculate velocity or burning rate.",
  "o2_note":"Selected O₂ is a scenario value, not used to calculate flame temperature, luminosity, size, or fire hazard.",
  "micro_why":"In microgravity, buoyancy-driven convection is greatly reduced. Diffusion and forced flow may govern the transport of oxygen and combustion products.",
  "earth_why":"On Earth, rising hot gases can make flames elongated. This is not universal across fuels and airflow settings.",
  "moon_why":"The Moon has partial gravity. This drawing does not reproduce lunar data, and BASS-II results cannot be extrapolated directly.",
  "mars_why":"Mars has partial gravity. A habitat's internal atmosphere would be essential for real fire research.",
  "limit":"This module cannot calculate flammability, fire probability, temperature, spread rate, or suppression time.",
  "picked":"Selected scenario", "visual":"Schematic view", "no_scale":"Illustration · not to physical scale",
  "nasa_title":"Now explore authentic NASA measurements", "nasa_desc":"BASS-II contains solid-combustion tests in microgravity. Original CSV values are shown without filling missing data or inventing measurements.",
  "find":"Search for material", "pi":"Principal investigator", "all":"All", "gas":"Gas to compare", "test":"Select up to 2 tests", "table":"Original test values", "initial":"Initial", "final":"Final", "change":"Change (final − initial)", "missing":"No records match these filters.",
  "data_limit":"Initial/final differences do not establish flammability, causality, or burning rate. Fan display and Air display are not automatically measured in m/s.",
  "source":"Source: NASA PSI · BASS-II table (local CSV sourced from PSI-25).", "download":"Download selected results (.csv)",
  "mission":"Mission: investigate before recommending", "scenario":"Your team is assessing evidence for a future lunar habitat. What can BASS-II actually establish about a material?",
  "question1":"What should you check first?", "options1":["Whether the flame illustration looks realistic.","What material and test conditions NASA recorded.","Whether AI guarantees fires will never occur."],
  "question2":"If final oxygen is lower than initial oxygen, what can you conclude?", "options2":["The material is certified as hazardous.","A difference was recorded, but more evidence is needed to explain its cause.","Lunar gravity causes exactly this change."],
  "question3":"Can the visualizer predict a lunar fire?", "options3":["Yes, because it displays a flame.","Yes, by setting oxygen to 30%.","No, because it lacks a validated partial-gravity model."],
  "check":"Check my answers", "score":"Challenge score", "right":"Great! You distinguished observations, explanations, and extrapolations.", "retry":"Review the answers. A conceptual image does not replace measurements or scientific validation.",
  "takeaway":"What you learned", "takeaway_text":"Fire requires combustion conditions; gravity changes gas transport; NASA PSI provides experimental evidence but does not certify lunar habitat safety.",
  "footer":"WARI Teams · NASA Space Apps Challenge 2026 · Educational tool, not certified for safety decisions.",
 }
}

def strict_num(value):
    text = str(value).strip()
    if not NUM.fullmatch(text): return float("nan")
    return float(text.replace(",", "."))

@st.cache_data(show_spinner=False)
def nasa_data():
    if not CSV.is_file(): return None
    df = pd.read_csv(CSV, dtype=str, keep_default_na=False)
    df.columns = [str(c).strip() for c in df.columns]
    missing = [value for value in COL.values() if value not in df.columns]
    if missing: raise ValueError("BASS-II CSV: missing columns: " + ", ".join(missing))
    df["_id"] = df[COL["id"]].str.strip()
    if df["_id"].duplicated().any():
        df["_key"] = [f"{n} · row {i+2}" for i,n in enumerate(df["_id"])]
    else: df["_key"] = df["_id"]
    for c in ("o2a","o2b","co2a","co2b","coa","cob"):
        df["_"+c] = df[COL[c]].apply(strict_num)
    return df

def flame_plot(gravity="earth", airflow=0, small=False):
    """Artistic 2D geometries. Not derived from combustion equations."""
    fig = go.Figure()
    if gravity == "micro":
        colors=[("#083C8B",.42,1.22),("#168DFF",.72,.91),("#9DEFFF",.9,.58)]
        for c,opacity,scale in colors:
            xs=[];ys=[]
            for i in range(121):
                angle = 2 * math.pi * i / 120
                y = 2.0 + 1.1 * scale * math.sin(angle)
                x = 0.0 + 1.15 * scale * math.cos(angle) + airflow * (y-1.6) * .035
                xs.append(x);ys.append(y)
            fig.add_trace(go.Scatter(x=xs,y=ys,mode="lines",fill="toself",fillcolor=c,
                line={"color":c,"width":1},opacity=opacity,hoverinfo="skip",showlegend=False))
    else:
        height={"earth":3.5,"moon":2.6,"mars":2.9}.get(gravity,3.5)
        for color,scale,opacity in [("#F15D22",1.0,.85),("#FFAD31",.75,.88),("#FFF1B6",.38,.98)]:
            xs=[];ys=[]
            for side in (1,-1):
                seq=range(121) if side==1 else range(120,-1,-1)
                for i in seq:
                    u=i/120
                    y=.25 + (height*u)
                    width=max(0.009,math.sin(math.pi*u)**.74)*(1-.40*u)*.90*scale
                    xs.append(side*width+airflow*u*.11)
                    ys.append(y)
            fig.add_trace(go.Scatter(x=xs,y=ys,mode="lines",fill="toself",fillcolor=color,
                line={"color":color,"width":1},opacity=opacity,hoverinfo="skip",showlegend=False))
    fig.add_trace(go.Scatter(x=[-2.5,2.5],y=[.16,.16],mode="lines",line={"color":"#748295","width":1},showlegend=False,hoverinfo="skip"))
    fig.update_layout(height=230 if small else 305, template="plotly_dark",paper_bgcolor=DARK,plot_bgcolor=DARK,
        margin=dict(l=5,r=5,t=5,b=5),showlegend=False,
        xaxis=dict(visible=False,range=[-2.6,2.6],fixedrange=True),
        yaxis=dict(visible=False,range=[-.25,4.6],fixedrange=True))
    return fig

def plot_comparison(frame, gas, words):
    gascols={"O₂":("o2a","o2b","% vol."),"CO₂":("co2a","co2b","% vol."),"CO":("coa","cob","ppm")}
    a,b,u=gascols[gas]
    tmp=frame[["_key","_"+a,"_"+b]].copy()
    tmp=tmp[tmp[["_"+a,"_"+b]].notna().any(axis=1)]
    fig=go.Figure()
    fig.add_bar(x=tmp["_key"],y=tmp["_"+a],marker_color=BLUE,name=words["initial"])
    fig.add_bar(x=tmp["_key"],y=tmp["_"+b],marker_color=ORANGE,name=words["final"])
    fig.update_layout(template="plotly_dark",paper_bgcolor=DARK,plot_bgcolor=DARK,barmode="group",height=340,
        font_color=WHITE,margin=dict(l=12,r=8,t=36,b=38),xaxis_title="Test #",yaxis_title=f"{gas} ({u})")
    return fig, a,b,u

def render_simulator(language):
    en=(language=="English")
    w=T["en" if en else "es"]
    st.markdown("""
    <style>
    .lab-banner{background:linear-gradient(110deg,#111927,#17263a 72%,#214363);border:1px solid #395672;border-left:5px solid #FF9B54;border-radius:16px;padding:22px 25px;margin-bottom:15px;}
    .lab-banner h2{color:white!important;margin:0 0 .3rem 0;font-size:1.9rem;font-weight:850;}
    .lab-banner p{color:#DAE7F5!important;margin:0;line-height:1.65;}
    .lab-note{border:1px solid #4A5C71;border-left:4px solid #62D4FF;background:#152235;border-radius:13px;padding:13px 16px;color:#F0F6FD;margin:12px 0;line-height:1.5;}
    .lab-tag{display:inline-block;color:#FFE1B5;font-size:.82rem;background:#30251d;border:1px solid #6F513B;padding:4px 9px;border-radius:999px;}
    </style>
    """,unsafe_allow_html=True)
    st.markdown(f'<div class="lab-banner"><span class="lab-tag">NASA Space Apps · Flame in Freefall</span><h2>🔥 {w["hero"]}</h2><p>{w["subtitle"]}</p></div>',unsafe_allow_html=True)
    st.caption(w["intro"])
    st.warning(w["warning"])
    a,b,c,d=st.tabs(w["tabs"])

    with a:
        st.subheader(w["learn_title"])
        st.markdown("#### "+w["triangle"])
        cards=st.columns(3)
        for col,title,desc,emoji in zip(cards,[w["fuel"],w["oxygen"],w["heat"]],[w["fuel_desc"],w["oxygen_desc"],w["heat_desc"]],["🪵","🫧","🌡️"]):
            with col:
                with st.container(border=True):
                    st.markdown(f"### {emoji} {title}")
                    st.write(desc)
        st.markdown("#### "+w["comparison"])
        left,right=st.columns(2)
        with left:
            st.markdown("**🌍 "+w["earth"]+"**")
            st.plotly_chart(flame_plot("earth",small=True),use_container_width=True,config={"displayModeBar":False},key="lab_earth_intro")
            st.caption(w["earth_caption"])
        with right:
            st.markdown("**🛰️ "+w["micro"]+"**")
            st.plotly_chart(flame_plot("micro",small=True),use_container_width=True,config={"displayModeBar":False},key="lab_micro_intro")
            st.caption(w["micro_caption"])
        st.info("**"+w["learn_q"]+"**  \n"+w["learn_a"])
        st.caption(w["science"])

    with b:
        left,center,right=st.columns([.95,1.15,1.1],gap="medium")
        with left:
            st.markdown("### 🎛️ "+w["controls"])
            environments=["earth","micro","moon","mars"]
            options={"earth":w["earth"],"micro":w["micro"],"moon":w["moon"],"mars":w["mars"]}
            grav=st.selectbox(w["gravity"],environments,format_func=lambda k:options[k],key="lab8_gravity")
            oxygen=st.slider(w["oxygen_pct"],15,40,21,key="lab8_oxygen")
            wind=st.select_slider(w["airflow"],options=[0,1,2],format_func=lambda x:w["air_opts"][x],value=1,key="lab8_air")
            run=st.button(w["run"],type="primary",use_container_width=True,key="lab8_run")
            if run:
                st.session_state["lab8_snapshot"]={"gravity":grav,"oxygen":oxygen,"wind":wind}
            if st.button(w["reset"],use_container_width=True,key="lab8_reset"):
                for k in ("lab8_snapshot","lab8_gravity","lab8_oxygen","lab8_air"):
                    st.session_state.pop(k,None)
                st.rerun()
        snapshot=st.session_state.get("lab8_snapshot")
        with center:
            st.markdown("### 🔥 "+w["comparison"])
            cols=st.columns(2)
            with cols[0]:
                st.markdown("**"+w["earth"]+"**")
                st.plotly_chart(flame_plot("earth",small=True),use_container_width=True,config={"displayModeBar":False},key="lab8_compare_earth")
            with cols[1]:
                other=(snapshot or {}).get("gravity","micro")
                st.markdown("**"+options[other]+"**")
                st.plotly_chart(flame_plot(other,airflow=(snapshot or {}).get("wind",0),small=True),use_container_width=True,config={"displayModeBar":False},key="lab8_compare_target")
            st.caption(w["no_scale"])
        with right:
            st.markdown("### 📚 "+w["results"])
            if snapshot is None:
                st.info(w["not_run"])
            else:
                selected=options[snapshot["gravity"]]
                st.success(f'**{w["picked"]}:** {selected} · O₂ {snapshot["oxygen"]}% · {w["air_opts"][snapshot["wind"]]}')
                st.write(w[snapshot["gravity"]+"_why"])
                st.caption(w["air_note"])
                st.caption(w["o2_note"])
            st.warning(w["limit"])

    with c:
        st.subheader(w["nasa_title"])
        st.write(w["nasa_desc"])
        try:
            data=nasa_data()
        except Exception as err:
            st.error("CSV NASA PSI / BASS-II: "+str(err));data=None
        if data is None:
            st.error("Archivo no encontrado / File not found: data/bass_ii_experimental.csv")
        else:
            c1,c2,c3=st.columns([1.1,1,1])
            mat=c1.text_input(w["find"],placeholder="PMMA",key="lab8_material")
            pi_names=sorted(x for x in data[COL["pi"]].unique() if x)
            pi=c2.selectbox(w["pi"],["*"]+pi_names,format_func=lambda x:w["all"] if x=="*" else x,key="lab8_pi")
            gas=c3.selectbox(w["gas"],["O₂","CO₂","CO"],key="lab8_gas")
            subset=data.copy()
            if mat.strip(): subset=subset[subset[COL["material"]].str.contains(mat.strip(),case=False,regex=False,na=False)]
            if pi!="*": subset=subset[subset[COL["pi"]]==pi]
            st.metric("BASS-II · "+("ensayos encontrados" if not en else "matching tests"),len(subset))
            if subset.empty:
                st.info(w["missing"])
            else:
                keys=subset["_key"].tolist()
                chosen=st.multiselect(w["test"],keys,default=keys[:min(2,len(keys))],max_selections=2,key="lab8_tests")
                if chosen:
                    tests=subset[subset["_key"].isin(chosen)].copy()
                    raw=[c for c in data.columns if not c.startswith("_")]
                    with st.expander(w["table"],expanded=True):
                        st.dataframe(tests[raw],hide_index=True,use_container_width=True)
                    fig,ga,gb,unit=plot_comparison(tests,gas,w)
                    st.plotly_chart(fig,use_container_width=True,key="lab8_chart")
                    table=pd.DataFrame({
                        "Test #":tests["_id"],
                        f'{gas} {w["initial"]} ({unit})':tests["_"+ga],
                        f'{gas} {w["final"]} ({unit})':tests["_"+gb],
                        f'{w["change"]} ({unit})':(tests["_"+gb]-tests["_"+ga]).round(3)
                    })
                    st.dataframe(table,hide_index=True,use_container_width=True)
                    st.download_button(w["download"],tests[raw].to_csv(index=False).encode("utf-8-sig"),
                        file_name="wari_bass2_selected.csv",mime="text/csv",key="lab8_export")
                else:st.info(w["test"])
            st.info(w["data_limit"])
            st.caption(w["source"])
            st.link_button("🔗 NASA PSI",NASA_URL)

    with d:
        st.subheader(w["mission"])
        st.info(w["scenario"])
        result=[]
        for index,answer in enumerate((1,1,2),start=1):
            choices=w[f"options{index}"]
            choice=st.radio(w[f"question{index}"],choices,index=None,key=f"lab8_quiz_{index}")
            result.append((choices.index(choice)==answer) if choice is not None else False)
        if st.button("✅ "+w["check"],key="lab8_quiz_check",type="primary"):
            st.metric(w["score"],f"{sum(result)}/3")
            if all(result):st.success(w["right"])
            else:st.warning(w["retry"])
        st.markdown("#### "+w["takeaway"])
        st.write(w["takeaway_text"])
    st.caption(w["footer"])
