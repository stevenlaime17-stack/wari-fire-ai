from pathlib import Path
import pandas as pd
import streamlit as st

BASE = Path(__file__).resolve().parent
CSV = BASE / 'data' / 'investigaciones.csv'
st.set_page_config(page_title='WARI FIRE AI | Wari Teams', page_icon='🔥', layout='wide')
st.markdown('''<style>
.stApp {background:#07101e;color:#e6f2ff}
h1,h2,h3 {color:#62def7 !important}
[data-testid="stMetricValue"] {color:#ffc35a}
.stAlert p {color:#14263c !important}
</style>''', unsafe_allow_html=True)

logo = BASE / 'assets' / 'logo.png'
left, right = st.columns([1, 4], vertical_alignment='center')
with left:
    if logo.exists(): st.image(str(logo), width=160)
with right:
    st.title('WARI FIRE AI')
    st.markdown('**Wari Teams · Ayacucho, Perú · NASA Space Apps Challenge 2026**')
    st.caption('Microgravity Combustion Intelligence Platform')

st.info('Biblioteca científica en construcción. El catálogo contiene descripciones y enlaces; aún no incluye mediciones originales de NASA PSI ni IA remota.')

@st.cache_data

def cargar_catalogo():
    if not CSV.is_file():
        return None, 'No existe data/investigaciones.csv en GitHub.'
    try:
        tabla = pd.read_csv(CSV, encoding='utf-8-sig', dtype=str).fillna('')
    except Exception as exc:
        return None, f'No se pudo leer el CSV: {exc}'
    tabla.columns = [str(c).strip().lower() for c in tabla.columns]
    obligatorias = ['experimento', 'area', 'combustible', 'descripcion', 'fuente']
    faltantes = [c for c in obligatorias if c not in tabla.columns]
    if faltantes:
        return None, 'Faltan columnas: ' + ', '.join(faltantes)
    tabla = tabla[obligatorias].copy()
    for c in obligatorias:
        tabla[c] = tabla[c].astype(str).str.strip()
    return tabla, None

catalogo, error = cargar_catalogo()
if error:
    st.error(error)
    st.caption('Revisa la ruta, los nombres de las columnas y que cada registro tenga cinco campos separados por comas.')
    st.stop()

t1, t2, t3, t4 = st.tabs(['🔎 Explorador', '📚 Biblioteca NASA', '📊 Comparador', '🤖 WARI AI'])
with t1:
    st.subheader('Explorador de investigaciones')
    c1, c2 = st.columns([2, 1])
    with c1:
        q = st.text_input('Buscar experimento, combustible o descripción', placeholder='Ejemplo: BASS')
    with c2:
        areas = ['Todas'] + sorted(x for x in catalogo['area'].unique() if x)
        area = st.selectbox('Área de seguridad', areas)
    filtro = catalogo.copy()
    if area != 'Todas':
        filtro = filtro[filtro['area'] == area]
    if q.strip():
        busqueda = filtro[['experimento', 'area', 'combustible', 'descripcion']].agg(' '.join, axis=1)
        filtro = filtro[busqueda.str.contains(q.strip(), case=False, regex=False)]
    st.metric('Investigaciones encontradas', len(filtro))
    st.dataframe(filtro[['experimento', 'area', 'combustible', 'descripcion']], use_container_width=True, hide_index=True)
    if filtro.empty:
        st.warning('No se encontraron investigaciones con esos filtros.')
    else:
        st.markdown('#### Fichas con fuentes')
        for i, r in filtro.iterrows():
            with st.expander(f"{r['experimento']} · {r['area']}"):
                st.write('**Combustible:**', r['combustible'])
                st.write('**Descripción:**', r['descripcion'])
                if r['fuente'].startswith(('https://', 'http://')):
                    st.link_button('Abrir fuente NASA', r['fuente'])
                else:
                    st.warning('Esta investigación todavía no tiene un enlace válido.')
with t2:
    st.subheader('Biblioteca NASA')
    st.write('Fuentes de referencia asociadas al catálogo actual:')
    for _, r in catalogo.iterrows():
        st.markdown(f"**{r['experimento']}** — {r['descripcion']}")
        if r['fuente'].startswith(('https://', 'http://')):
            st.link_button(f"Consultar: {r['experimento']}", r['fuente'], key=f"source_{_}")
    st.caption('Los enlaces no implican descarga ni lectura automática. Los resultados numéricos se incorporarán desde archivos NASA verificables.')
with t3:
    st.subheader('Comparador científico')
    st.warning('Todavía no tenemos ensayos con mediciones numéricas verificadas. No mostraremos gráficos inventados.')
    opciones = catalogo['experimento'].tolist()
    seleccion = st.multiselect('Selecciona investigaciones para comparar sus descripciones', opciones, default=opciones[:2])
    if seleccion:
        st.dataframe(catalogo[catalogo['experimento'].isin(seleccion)][['experimento', 'area', 'combustible', 'descripcion']], hide_index=True, use_container_width=True)
    st.caption('Esto es una comparación descriptiva, no experimental. Más adelante añadiremos condiciones y resultados medidos por ensayo.')
with t4:
    st.subheader('WARI AI — asistente científico')
    st.warning('La IA pública todavía no está conectada. Esta fase se habilitará después de consolidar los datos y sus referencias.')
    st.write('La versión actual no requiere API ni Ollama para explorar las investigaciones.')

st.divider()
st.caption('Wari Teams · Herramienta educativa y de investigación; no certifica seguridad contra incendios.')
