import streamlit as st
import pandas as pd
from pathlib import Path

st.set_page_config(page_title="WARI FIRE AI | Wari Teams", page_icon="🔥", layout="wide")
st.markdown("""<style>
.stApp {background:#07101e;color:#e6f2ff}
h1,h2,h3 {color:#62def7 !important}
[data-testid="stMetricValue"] {color:#ffc35a}
.stAlert p {color:#14263c !important}
</style>""", unsafe_allow_html=True)

left,right=st.columns([1,4],vertical_alignment="center")
with left:
    logo=Path(__file__).parent / "assets" / "logo.png"
    if logo.exists(): st.image(str(logo),width=160)
with right:
    st.title("WARI FIRE AI")
    st.markdown("**Wari Teams · Ayacucho, Perú · NASA Space Apps Challenge 2026**")
    st.caption("Microgravity Combustion Intelligence Platform")

st.info("🚧 Versión pública inicial. El catálogo contiene descripciones generales y enlaces; todavía no contiene mediciones originales ni una IA remota conectada.")

catalog=pd.DataFrame([
    {"Experimento":"BASS / BASS-II","Área":"Prevención","Fenómeno":"Combustión y supresión de sólidos","Combustible":"Sólido"},
    {"Experimento":"SAME / SAME-R","Área":"Detección","Fenómeno":"Humo y aerosoles","Combustible":"Aerosoles"},
    {"Experimento":"FLEX / FLEX-2","Área":"Supresión","Fenómeno":"Combustión y extinción de gotas","Combustible":"Líquido"},
    {"Experimento":"Saffire","Área":"Prevención","Fenómeno":"Incendios en entornos de nave espacial","Combustible":"Sólido"},
    {"Experimento":"ACME","Área":"Investigación","Fenómeno":"Fenómenos de llamas y combustión","Combustible":"Gaseoso"},
])
t1,t2,t3,t4=st.tabs(["🔎 Explorar", "📊 Comparar", "📚 Fuentes NASA", "🤖 WARI AI"])
with t1:
    st.subheader("Explorador de investigaciones")
    area=st.selectbox("Filtrar por área",["Todas"]+sorted(catalog["Área"].unique().tolist()))
    q=st.text_input("Buscar por nombre o fenómeno")
    rows=catalog if area=="Todas" else catalog[catalog["Área"]==area]
    if q: rows=rows[rows.apply(lambda r:q.casefold() in " ".join(map(str,r.values)).casefold(),axis=1)]
    st.dataframe(rows,use_container_width=True,hide_index=True)
    st.caption("Información descriptiva preliminar: verificar y ampliar con el registro original de cada investigación.")
with t2:
    st.subheader("Comparador de condiciones experimentales")
    st.write("Este módulo incorporará mediciones originales de NASA PSI con unidades, identificador de ensayo y fuente.")
    st.warning("No se muestran gráficos numéricos hasta contar con un conjunto de datos verificado. Esto evita inventar resultados.")
    st.dataframe(catalog[["Experimento","Área","Combustible","Fenómeno"]],use_container_width=True,hide_index=True)
with t3:
    st.subheader("Biblioteca de fuentes NASA")
    st.markdown("- [NASA Physical Sciences Informatics (PSI)](https://psi.nasa.gov/physci/repo/search?data_source=psi&data_type=investigation)\n- [Catálogo oficial de investigaciones por área](https://www.nasa.gov/physical-sciences-informatics-psi/psi-investigations-by-research-area/)\n- [Recursos del desafío Flame in Freefall](https://www.spaceappschallenge.org/2026/challenges/flame-in-freefall/?tab=resources)")
    st.caption("Los enlaces son referencias, no una importación automática ni una lectura de los documentos.")
with t4:
    st.subheader("WARI AI — asistente científico")
    st.warning("El asistente remoto todavía no está conectado. La versión pública inicial funciona sin Ollama ni claves de API.")
    st.write("Próxima fase: búsqueda de fragmentos documentales, respuesta fundamentada y citas verificables.")
    st.text_area("Pregunta de ejemplo",value="¿Qué estudios de NASA informan sobre la inflamabilidad de materiales sólidos en microgravedad?",disabled=True)

st.divider()
st.caption("Wari Teams · Prototipo de investigación y educación, no certificado para decisiones de seguridad")
