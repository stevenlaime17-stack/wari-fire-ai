from pathlib import Path
import pandas as pd
import streamlit as st

BASE = Path(__file__).resolve().parent
CATALOG = BASE / 'data' / 'investigaciones.csv'
BASS = BASE / 'data' / 'bass_ii_experimental.csv'
SOURCE = 'https://www.nasa.gov/physical-sciences-informatics-psi/psi-investigations-by-research-area/'

st.set_page_config(page_title='WARI FIRE AI | Wari Teams', page_icon='🔥', layout='wide')
st.markdown('''<style>
.stApp {background:#07101e;color:#e6f2ff}
h1,h2,h3 {color:#62def7 !important}
[data-testid="stMetricValue"] {color:#ffc35a}
.stAlert p {color:#14263c !important}
</style>''', unsafe_allow_html=True)

logo = BASE / 'assets' / 'logo.png'
col_logo, col_title = st.columns([1, 4], vertical_alignment='center')
with col_logo:
    if logo.exists():
        st.image(str(logo), width=160)
with col_title:
    st.title('WARI FIRE AI')
    st.markdown('**Wari Teams · Ayacucho, Perú · NASA Space Apps Challenge 2026**')
    st.caption('Microgravity Combustion Intelligence Platform')

@st.cache_data
def load_catalog():
    if not CATALOG.exists():
        return None, 'Falta data/investigaciones.csv.'
    try:
        df = pd.read_csv(CATALOG, encoding='utf-8-sig', dtype=str).fillna('')
    except Exception as e:
        return None, f'Error leyendo el catálogo: {e}'
    df.columns = df.columns.str.strip().str.lower()
    needed = ['experimento','area','combustible','descripcion','fuente']
    missing = [x for x in needed if x not in df.columns]
    if missing:
        return None, 'Faltan columnas en el catálogo: ' + ', '.join(missing)
    return df[needed], None

@st.cache_data
def load_bass():
    if not BASS.exists():
        return None, 'Falta data/bass_ii_experimental.csv.'
    try:
        df = pd.read_csv(BASS, encoding='utf-8-sig', dtype=str, keep_default_na=False)
    except Exception as e:
        return None, f'No se pudo leer el CSV experimental: {e}'
    df.columns = df.columns.str.strip()
    expected = ['PI', 'Test #', 'Fuel Sample Material',
                'Calibrated  initial O2 % by vol', 'Calibrated final O2 % by vol',
                'Initial CO2 % by vol', 'Final CO2 % by vol',
                'Initial CO (ppm)', 'Final CO (ppm)']
    # Column naming is matched after trimming whitespace only.
    missing = [c for c in expected if c not in df.columns]
    if missing:
        return None, 'Faltan encabezados del CSV original: ' + ', '.join(missing)
    metrics = {
        'Oxígeno (% vol.)': ('Calibrated  initial O2 % by vol', 'Calibrated final O2 % by vol', '% vol.'),
        'CO₂ (% vol.)': ('Initial CO2 % by vol', 'Final CO2 % by vol', '% vol.'),
        'CO (ppm)': ('Initial CO (ppm)', 'Final CO (ppm)', 'ppm'),
    }
    for before, after, unit in metrics.values():
        df[before + '_num'] = pd.to_numeric(df[before].str.strip(), errors='coerce')
        df[after + '_num'] = pd.to_numeric(df[after].str.strip(), errors='coerce')
    return df, None

catalog, error = load_catalog()
if error:
    st.error(error)
    st.stop()

st.info('Fuente experimental añadida: tabla BASS-II PSI-25. Se muestran registros originales sin corregir valores atípicos; no se calculan riesgos de incendio ni velocidades de llama.')
t1, t2, t3, t4 = st.tabs(['🔎 Explorador','📚 Biblioteca NASA','📊 Comparador experimental','🤖 WARI AI'])

with t1:
    st.subheader('Explorador de investigaciones')
    c1, c2 = st.columns([2,1])
    with c1:
        term = st.text_input('Buscar experimento, combustible o descripción', placeholder='BASS')
    with c2:
        group = st.selectbox('Área de seguridad', ['Todas'] + sorted(x for x in catalog['area'].dropna().unique() if x))
    filtered = catalog.copy()
    if group != 'Todas':
        filtered = filtered[filtered['area'] == group]
    if term.strip():
        text_search = filtered[['experimento','area','combustible','descripcion']].fillna('').agg(' '.join, axis=1)
        filtered = filtered[text_search.str.contains(term.strip(), case=False, regex=False)]
    st.metric('Investigaciones encontradas', len(filtered))
    st.dataframe(filtered[['experimento','area','combustible','descripcion']], width='stretch', hide_index=True)
    for n, r in filtered.iterrows():
        with st.expander(f"{r['experimento']} · {r['area']}"):
            st.write('**Combustible:**', r['combustible'])
            st.write('**Descripción:**', r['descripcion'])
            if str(r['fuente']).startswith(('https://','http://')):
                st.link_button('Abrir fuente', r['fuente'])

with t2:
    st.subheader('Biblioteca científica NASA')
    st.write('Investigaciones del catálogo y sus referencias:')
    for n, r in catalog.iterrows():
        with st.expander(f"{r['experimento']} — {r['area']}"):
            st.write(r['descripcion'])
            if str(r['fuente']).startswith(('https://','http://')):
                st.link_button('Abrir referencia', r['fuente'], key=f'catalog_{n}')
    st.markdown('### Tabla experimental BASS-II (PSI-25)')
    st.write('Datos aportados desde el archivo «PSI-25_Experimental table_BASS-II.csv»; se conservan los valores originales y los identificadores de ensayos.')
    st.link_button('Catálogo oficial NASA PSI', SOURCE)
    st.caption('El enlace al catálogo identifica la investigación, pero no sustituye la trazabilidad del archivo individual. Añade el enlace exacto de descarga o DOI verificado antes de la entrega final.')

with t3:
    st.subheader('BASS-II — Comparador de mediciones originales')
    df, err = load_bass()
    if err:
        st.warning(err)
        st.write('Sube el archivo CSV a la ruta **data/bass_ii_experimental.csv** en GitHub. No cambies sus encabezados ni valores.')
    else:
        a, b, c = st.columns(3)
        a.metric('Ensayos cargados', len(df))
        b.metric('Investigadores principales', df['PI'].nunique())
        c.metric('Identificadores de ensayo', df['Test #'].nunique())
        investigators = sorted(x for x in df['PI'].unique() if x)
        s1, s2 = st.columns([1,2])
        with s1:
            investigator = st.selectbox('Investigador principal (PI)', ['Todos'] + investigators)
        with s2:
            material_text = st.text_input('Filtrar descripción de material', placeholder='PMMA, SIBAL, etc.')
        d = df.copy()
        if investigator != 'Todos':
            d = d[d['PI'] == investigator]
        if material_text.strip():
            d = d[d['Fuel Sample Material'].str.contains(material_text.strip(), case=False, regex=False, na=False)]
        st.caption(f'{len(d)} ensayos después del filtro')
        show_cols = ['Test #','PI','Date','Fuel Sample Material','Fan display','Air display',
                     'Calibrated  initial O2 % by vol','Calibrated final O2 % by vol',
                     'Initial CO2 % by vol','Final CO2 % by vol', 'Initial CO (ppm)','Final CO (ppm)']
        st.dataframe(d[show_cols], width='stretch', hide_index=True)
        metric_defs = {
            'Oxígeno (% vol.)': ('Calibrated  initial O2 % by vol', 'Calibrated final O2 % by vol', '% vol.'),
            'CO₂ (% vol.)': ('Initial CO2 % by vol', 'Final CO2 % by vol', '% vol.'),
            'CO (ppm)': ('Initial CO (ppm)', 'Final CO (ppm)', 'ppm'),
        }
        chosen = st.selectbox('Medición para comparar', list(metric_defs))
        before, after, unit = metric_defs[chosen]
        plot_data = d[['Test #', before + '_num', after + '_num']].copy()
        plot_data = plot_data.rename(columns={before + '_num':'Inicial', after + '_num':'Final'})
        plot_data = plot_data.dropna(subset=['Inicial','Final'])
        st.write(f'**Inicial frente a final: {chosen}**')
        if plot_data.empty:
            st.warning('No hay pares numéricos completos con los filtros elegidos.')
        else:
            st.bar_chart(plot_data.set_index('Test #')[['Inicial','Final']], x_label='Identificador de ensayo', y_label=unit)
            st.caption(f'Se grafican {len(plot_data)} pares con valores numéricos iniciales y finales. No se imputaron datos faltantes.')
        st.warning('Control de calidad: existen celdas vacías, textos mezclados y valores potencialmente atípicos. En O₂ final aparecen 0.6 %, 0.9 %, 1.6 %, 39.1 % y 40.4 %. Son registros del CSV, NO valores validados; deben contrastarse con los documentos del experimento antes de obtener conclusiones.')
        with st.expander('Ver posibles valores atípicos de O₂ final'):
            o2 = df['Calibrated final O2 % by vol_num']
            anomalies = df[o2.notna() & ((o2 < 5) | (o2 > 30))]
            st.dataframe(anomalies[['Test #','PI','Fuel Sample Material','Calibrated  initial O2 % by vol','Calibrated final O2 % by vol']], width='stretch', hide_index=True)
        st.download_button('Descargar la tabla filtrada (CSV)', data=d[show_cols].to_csv(index=False).encode('utf-8-sig'), file_name='bass_ii_filtrado.csv', mime='text/csv')
        st.caption('Las columnas de ventilador y aire son lecturas del equipo; no equivalen automáticamente a velocidad de flujo calibrada. El CSV tampoco aporta directamente una medida de velocidad de propagación de llama.')

with t4:
    st.subheader('WARI AI — Próxima fase')
    st.info('La consulta remota con IA todavía no está habilitada en esta versión pública. El comparador y los datos verificados funcionan de manera independiente.')
    st.write('Próximo objetivo: recuperar fragmentos específicos del PDF de BASS-II e incorporar un modelo remoto con citas trazables.')

st.divider()
st.caption('Wari Teams · Prototipo científico educativo. No permite certificar materiales ni estimar riesgos reales de incendio.')
