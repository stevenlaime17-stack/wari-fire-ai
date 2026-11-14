"""WARI FIRE AI — Fase 4: análisis de ensayos NASA BASS-II (PSI-25).
No es una herramienta de evaluación certificada de riesgos de incendio.
"""
from pathlib import Path
import re
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

ROOT = Path(__file__).resolve().parent
CATALOG_PATH = ROOT / 'data' / 'investigaciones.csv'
BASS_PATH = ROOT / 'data' / 'bass_ii_experimental.csv'
PSI_CATALOG = 'https://www.nasa.gov/physical-sciences-informatics-psi/psi-investigations-by-research-area/'

# Se preservan los encabezados del archivo original; solo se eliminan espacios exteriores.
O2_I = 'Calibrated  initial O2 % by vol'
O2_F = 'Calibrated final O2 % by vol'
MEASURES = {
    'Oxígeno O₂ (% vol.)': (O2_I, O2_F, '% vol.'),
    'Dióxido de carbono CO₂ (% vol.)': ('Initial CO2 % by vol', 'Final CO2 % by vol', '% vol.'),
    'Monóxido de carbono CO (ppm)': ('Initial CO (ppm)', 'Final CO (ppm)', 'ppm'),
}
SHOW_COLS = ['Test #', 'PI', 'Date', 'Fuel Sample Material', 'Fan display', 'Air display',
             O2_I, O2_F, 'Initial CO2 % by vol', 'Final CO2 % by vol',
             'Initial CO (ppm)', 'Final CO (ppm)']

st.set_page_config(page_title='WARI FIRE AI | Wari Teams', page_icon='🔥', layout='wide')
st.markdown('''<style>
.stApp {background:#07152d;color:#f1f6fd}
h1,h2,h3 {color:#63e4fa !important}
[data-testid="stMetricValue"] {color:#ffd451}
[data-testid="stAlert"] p {color:inherit !important}
</style>''', unsafe_allow_html=True)

@st.cache_data
def load_catalog():
    if not CATALOG_PATH.exists():
        return None, 'No existe data/investigaciones.csv.'
    try:
        d = pd.read_csv(CATALOG_PATH, dtype=str, encoding='utf-8-sig').fillna('')
        d.columns = d.columns.str.strip().str.lower()
        required = ['experimento', 'area', 'combustible', 'descripcion', 'fuente']
        missing = [c for c in required if c not in d.columns]
        if missing:
            return None, 'Faltan columnas en investigaciones.csv: ' + ', '.join(missing)
        return d[required], None
    except Exception as exc:
        return None, f'No se pudo leer el catálogo: {exc}'

@st.cache_data
def load_bass():
    if not BASS_PATH.exists():
        return None, 'Falta data/bass_ii_experimental.csv.'
    try:
        d = pd.read_csv(BASS_PATH, dtype=str, encoding='utf-8-sig', keep_default_na=False)
        d.columns = d.columns.str.strip()
        required = list(dict.fromkeys(SHOW_COLS))
        missing = [c for c in required if c not in d.columns]
        if missing:
            return None, 'Al CSV le faltan estas columnas: ' + ', '.join(missing)
        for a, b, _ in MEASURES.values():
            d[a + '__numeric'] = pd.to_numeric(d[a].astype(str).str.strip(), errors='coerce')
            d[b + '__numeric'] = pd.to_numeric(d[b].astype(str).str.strip(), errors='coerce')
        return d, None
    except Exception as exc:
        return None, f'No se pudo leer el CSV de BASS-II: {exc}'

def natural_test_key(value):
    text = str(value)
    match = re.match(r'^([^0-9]*)([0-9]+)(.*)$', text)
    return (match.group(1), int(match.group(2)), match.group(3)) if match else (text, -1, '')

logo = ROOT / 'assets' / 'logo.png'
logo_col, title_col = st.columns([1, 5], vertical_alignment='center')
with logo_col:
    if logo.exists():
        st.image(str(logo), width=145)
with title_col:
    st.title('WARI FIRE AI')
    st.markdown('**Wari Teams · Ayacucho, Perú · NASA Space Apps Challenge 2026**')
    st.caption('Microgravity Combustion Intelligence Platform · Fase 4')

catalog, catalog_error = load_catalog()
if catalog_error:
    st.error(catalog_error)
    st.stop()
st.info('Datos experimentales BASS-II / PSI-25. Los gráficos muestran registros originales y diferencias aritméticas, no riesgos de incendio ni velocidades de propagación de llama.')

t1, t2, t3, t4 = st.tabs(['🔎 Explorador', '📚 Biblioteca NASA', '📊 Análisis BASS-II', '🤖 WARI AI'])

with t1:
    st.subheader('Explorador de investigaciones')
    c1, c2 = st.columns([2, 1])
    with c1:
        phrase = st.text_input('Buscar experimento, combustible o descripción', placeholder='BASS')
    with c2:
        area = st.selectbox('Área de seguridad', ['Todas'] + sorted(x for x in catalog['area'].unique() if x))
    show = catalog.copy()
    if area != 'Todas':
        show = show[show['area'] == area]
    if phrase.strip():
        combined = show[['experimento', 'area', 'combustible', 'descripcion']].agg(' '.join, axis=1)
        show = show[combined.str.contains(phrase.strip(), case=False, regex=False)]
    st.metric('Investigaciones encontradas', len(show))
    st.dataframe(show[['experimento','area','combustible','descripcion']], width='stretch', hide_index=True)
    for ix, row in show.iterrows():
        with st.expander(f"{row['experimento']} — {row['area']}"):
            st.write(row['descripcion'])
            if row['fuente'].startswith(('https://', 'http://')):
                st.link_button('Abrir fuente', row['fuente'], key=f'explorer_{ix}')

with t2:
    st.subheader('Biblioteca NASA')
    st.write('Referencias del catálogo utilizado por WARI FIRE AI:')
    for ix, row in catalog.iterrows():
        with st.expander(f"{row['experimento']} — {row['area']}"):
            st.write(f"**Combustible:** {row['combustible']}")
            st.write(row['descripcion'])
            if row['fuente'].startswith(('https://', 'http://')):
                st.link_button('Consultar referencia', row['fuente'], key=f'library_{ix}')
    st.markdown('### Conjunto experimental BASS-II (PSI-25)')
    st.write('Archivo integrado: `data/bass_ii_experimental.csv`, derivado del archivo facilitado «PSI-25_Experimental table_BASS-II.csv».')
    st.link_button('Consultar catálogo oficial NASA PSI', PSI_CATALOG)
    st.caption('Este enlace lleva al catálogo general. Para trazabilidad completa, adjuntar el enlace persistente exacto del conjunto original cuando se verifique. No atribuir números de página sin verificarlos.')

with t3:
    st.subheader('BASS-II — Análisis por ensayo y control de calidad')
    df, error = load_bass()
    if error:
        st.error(error)
        st.stop()
    a, b, c = st.columns(3)
    a.metric('Registros cargados', len(df))
    b.metric('Investigadores principales', df['PI'].nunique())
    c.metric('Identificadores de prueba', df['Test #'].nunique())

    x1, x2 = st.columns([1, 2])
    with x1:
        pi = st.selectbox('Filtrar por investigador (PI)', ['Todos'] + sorted(v for v in df['PI'].unique() if v))
    with x2:
        material_query = st.text_input('Filtrar material combustible', placeholder='PMMA, SIBAL...')
    filtered = df.copy()
    if pi != 'Todos':
        filtered = filtered[filtered['PI'] == pi]
    if material_query.strip():
        filtered = filtered[filtered['Fuel Sample Material'].str.contains(material_query.strip(), case=False, regex=False)]
    st.caption(f'{len(filtered)} registros disponibles con los filtros actuales.')
    if filtered.empty:
        st.warning('No se encontraron ensayos con esos filtros. Borra la búsqueda o cambia el investigador.')
    else:
        st.dataframe(filtered[SHOW_COLS], width='stretch', hide_index=True)
        st.download_button('Descargar tabla filtrada (CSV)',
            data=filtered[SHOW_COLS].to_csv(index=False).encode('utf-8-sig'),
            file_name='wari_bass_ii_filtrado.csv', mime='text/csv')
        st.divider()
        st.markdown('### 1. Comparar un grupo pequeño de ensayos')
        measure_name = st.selectbox('Variable experimental', list(MEASURES.keys()))
        initial_col, final_col, unit = MEASURES[measure_name]
        available_tests = sorted(filtered['Test #'].dropna().astype(str).unique().tolist(), key=natural_test_key)
        default_tests = available_tests[:min(8, len(available_tests))]
        chosen_tests = st.multiselect('Selecciona de 1 a 20 ensayos para el gráfico', available_tests, default=default_tests)
        if len(chosen_tests) > 20:
            st.warning('Selecciona como máximo 20 ensayos para mantener el gráfico legible.')
        elif not chosen_tests:
            st.info('Selecciona al menos un ensayo para visualizar las mediciones.')
        else:
            selected = filtered[filtered['Test #'].isin(chosen_tests)].copy()
            selected['__order'] = pd.Categorical(selected['Test #'], categories=chosen_tests, ordered=True)
            selected = selected.sort_values('__order')
            pairs = selected.dropna(subset=[initial_col + '__numeric', final_col + '__numeric']).copy()
            if pairs.empty:
                st.warning('No hay mediciones iniciales y finales numéricas completas en la selección.')
            else:
                fig = go.Figure()
                for label, col, color in [('Inicial', initial_col, '#2b83ff'), ('Final', final_col, '#6be7ec')]:
                    fig.add_trace(go.Bar(x=pairs['Test #'], y=pairs[col + '__numeric'], name=label,
                                         marker_color=color, hovertemplate='Ensayo %{x}<br>' + label + ': %{y:.4g} ' + unit + '<extra></extra>'))
                fig.update_layout(barmode='group', title=f'{measure_name} — valores iniciales y finales',
                                  xaxis_title='Identificador del ensayo', yaxis_title=unit,
                                  template='plotly_dark', paper_bgcolor='#07152d', plot_bgcolor='#10213a',
                                  legend_title_text='Lectura', margin=dict(l=30,r=20,t=65,b=20))
                st.plotly_chart(fig, width='stretch', config={'displaylogo': False})
                st.caption(f'{len(pairs)} ensayos con ambos valores numéricos completos. Barras agrupadas, no apiladas. Se excluyen del gráfico los pares incompletos, pero no del CSV.')
                delta = pairs[['Test #', initial_col + '__numeric', final_col + '__numeric']].copy()
                delta.columns = ['Ensayo', f'Inicial ({unit})', f'Final ({unit})']
                delta[f'Diferencia final - inicial ({unit})'] = delta.iloc[:, 2] - delta.iloc[:, 1]
                st.dataframe(delta, width='stretch', hide_index=True)
                st.caption('Diferencia = lectura final − lectura inicial; no equivale a consumo de oxígeno, tasa de combustión ni efecto causal aislado.')

        st.divider()
        st.markdown('### 2. Ficha de un ensayo')
        specific_test = st.selectbox('Selecciona un ensayo para inspeccionarlo', available_tests)
        item = filtered[filtered['Test #'] == specific_test].iloc[0]
        st.write(f"**Ensayo:** {item['Test #']}  ·  **Investigador:** {item['PI']}  ·  **Fecha registrada:** {item['Date']}")
        st.write(f"**Descripción literal del material:** {item['Fuel Sample Material'] or 'No disponible'}")
        st.write(f"**Lecturas de equipo (sin conversión a velocidad):** Fan display = `{item['Fan display']}`; Air display = `{item['Air display']}`")
        metrics_rows = []
        for name, (init, final, u) in MEASURES.items():
            vi = item[init + '__numeric']
            vf = item[final + '__numeric']
            metrics_rows.append({'Variable': name, 'Inicial (literal)': item[init], 'Final (literal)': item[final],
                                 'Diferencia numérica': round(float(vf - vi), 4) if pd.notna(vi) and pd.notna(vf) else None,
                                 'Unidad de la diferencia': u})
        st.dataframe(pd.DataFrame(metrics_rows), width='stretch', hide_index=True)
        st.caption('Las lecturas literales se conservan; cuando el valor no es numérico, no se calcula diferencia.')

        st.divider()
        st.markdown('### 3. Control de calidad y trazabilidad')
        st.write('**Regla orientativa de revisión:** señalar O₂ final inferior a 5 % o superior a 30 %. Este umbral es una regla de cribado creada para el prototipo; NO es un criterio oficial NASA ni demuestra errores en las mediciones.')
        o2_final = df[O2_F + '__numeric']
        flagged = df[o2_final.notna() & ((o2_final < 5) | (o2_final > 30))]
        missing_pairs = sum((df[O2_I + '__numeric'].isna()) | (df[O2_F + '__numeric'].isna()))
        m1, m2 = st.columns(2)
        m1.metric('Registros señalados para revisión', len(flagged))
        m2.metric('Pares O₂ inicial/final incompletos', int(missing_pairs))
        with st.expander('Mostrar registros señalados (sin modificar)'):
            st.dataframe(flagged[['Test #','PI','Fuel Sample Material',O2_I,O2_F]], width='stretch', hide_index=True)
        st.warning('Antes de interpretar valores inusuales, comprobar la documentación experimental y las condiciones de medición. Las lecturas de ventilador y aire no representan velocidades calibradas de manera automática.')
        st.markdown('**Procedencia:** Tabla experimental BASS-II, investigación NASA PSI-25; archivo local `data/bass_ii_experimental.csv`.')
        st.link_button('Abrir catálogo NASA PSI para localizar la fuente original', PSI_CATALOG)
        st.caption('Los cálculos y alertas de calidad son derivados por WARI FIRE AI a partir del CSV; no son conclusiones oficiales de NASA. No se realiza extrapolación a la gravedad lunar.')

with t4:
    st.subheader('WARI AI — Preparación de la siguiente fase')
    st.info('La aplicación pública no tiene todavía un modelo remoto conectado. El análisis numérico de esta fase funciona sin inteligencia artificial y está basado en el CSV disponible.')
    st.write('Siguiente etapa: incorporar recuperación de fragmentos de documentos originales y un servicio de IA público que cite sus fuentes.')

st.divider()
st.caption('Wari Teams · Ayacucho, Perú · Prototipo científico exploratorio. No certificado para decisiones de seguridad.')
