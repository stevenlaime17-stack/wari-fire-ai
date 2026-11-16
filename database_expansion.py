"""Biblioteca ampliada NASA PSI. No fusiona familias experimentales heterogéneas."""
from pathlib import Path
import pandas as pd
import streamlit as st

DIR=Path(__file__).resolve().parent / 'data'

def render_database_expansion(lang='Español'):
    en=(lang=='English')
    catalog=DIR/'psi_investigaciones_detalle.csv'
    trace=DIR/'bass_ii_indice_trazabilidad.csv'
    if not catalog.exists():
        st.error('Extended catalog not found.' if en else 'No se encontró el catálogo ampliado.')
        return
    df=pd.read_csv(catalog).fillna('')
    st.title('🗃️ NASA PSI Data Atlas' if en else '🗃️ Atlas de datos NASA PSI')
    st.write(('Official NASA investigation index + local measurement inventory. This is **not** a count of newly downloaded experimental tests.' if en else 'Índice de investigaciones NASA verificadas + inventario de mediciones locales. **No** equivale a nuevos ensayos experimentales descargados.'))
    c1,c2,c3=st.columns(3)
    c1.metric('Investigations' if en else 'Investigaciones',len(df))
    c2.metric('Experimental rows' if en else 'Filas experimentales',129)
    c3.metric('Families with raw data' if en else 'Familias con datos crudos',1)
    st.info(('17 investigations have verified names in NASA’s official directory. Only BASS-II has locally incorporated original test rows; all other families are metadata-only.' if en else 'Las 17 investigaciones están documentadas en el índice oficial NASA. Solo BASS-II contiene ensayos originales integrados; las otras son fichas documentales.'))
    search=st.text_input('Search investigation or topic' if en else 'Buscar investigación o tema',placeholder='FLEX, SAFFIRE, SAME, BASS...')
    areas=sorted(df['area_en' if en else 'area_es'].dropna().unique())
    picked=st.multiselect('Research area' if en else 'Área de investigación',areas,default=areas)
    view=df[df['area_en' if en else 'area_es'].isin(picked)].copy()
    if search.strip():
        keys=['investigacion','descripcion_en','descripcion_es','area_en','area_es','tipo_en','tipo_es']
        view=view[view[keys].fillna('').astype(str).agg(' '.join,axis=1).str.contains(search,case=False,regex=False,na=False)]
    shown=pd.DataFrame({
      ('Investigation' if en else 'Investigación'):view['investigacion'],
      ('Area' if en else 'Área'):view['area_en' if en else 'area_es'],
      ('Fuel / sample' if en else 'Combustible / muestra'):view['tipo_en' if en else 'tipo_es'],
      ('Description' if en else 'Descripción'):view['descripcion_en' if en else 'descripcion_es'],
      ('Local experiment rows' if en else 'Ensayos locales'):view['filas_locales'],
      ('NASA catalog' if en else 'Catálogo NASA'):view['fuente_catalogo'],
    })
    st.dataframe(shown,hide_index=True,use_container_width=True,column_config={( 'NASA catalog' if en else 'Catálogo NASA'):st.column_config.LinkColumn('NASA' if en else 'Fuente',display_text='NASA')})
    st.download_button('Download investigation index (CSV)' if en else 'Descargar índice de investigaciones (CSV)',
      data=view.to_csv(index=False).encode('utf-8-sig'),file_name='wari_psi_investigations.csv',mime='text/csv')
    st.divider()
    st.subheader('Evidence & data provenance' if en else 'Evidencia y trazabilidad')
    st.write(('The BASS-II source file is retained without replacing values. A companion row index includes original CSV row numbers and SHA-256 fingerprint.' if en else 'Se conserva el CSV original BASS-II, sin sustituir valores. Un índice auxiliar registra el número de fila y una huella SHA-256 del archivo.'))
    if trace.exists():
        prov=pd.read_csv(trace).fillna('')
        st.metric('Traceable BASS-II rows' if en else 'Filas BASS-II trazables',len(prov))
        st.dataframe(prov[['registro_local','ensayo_original','material_original','fila_csv_origen','pagina_nasa']].head(15),hide_index=True,use_container_width=True)
        st.download_button('Download provenance index' if en else 'Descargar índice de procedencia',data=trace.read_bytes(),file_name='bass_ii_indice_trazabilidad.csv',mime='text/csv')
    with st.expander('How to add more real NASA test data' if en else 'Cómo ampliar los ensayos experimentales reales'):
        if en:
            st.markdown('1. Open the official NASA PSI data repository.\n2. Choose an investigation, open **Data / Experimental table**, download the original file, and retain its DOI and units.\n3. Keep each original dataset in its own file; do not append FLEX, SAME or SAFFIRE columns to BASS-II.\n4. Validate definitions, identifiers, units and missing values before implementing family-specific charts.')
        else:
            st.markdown('1. Abra el repositorio oficial NASA PSI.\n2. Seleccione una investigación, entre a **Data / Experimental table** y descargue el archivo original conservando DOI y unidades.\n3. Mantenga cada conjunto experimental en su propio archivo; no mezcle columnas de FLEX, SAME o SAFFIRE con BASS-II.\n4. Valide definiciones, identificadores, unidades y datos ausentes antes de generar gráficos por familia.')
        st.link_button('NASA PSI Repository', 'https://psi.nasa.gov/physci/repo/search?data_source=psi&data_type=investigation')
    st.caption(('Source: official NASA investigations by research area; original BASS-II PSI-25 CSV already in project. This research prototype is not a fire-safety certification system.' if en else 'Fuentes: índice oficial NASA por áreas de investigación y CSV original BASS-II PSI-25 del proyecto. Esta herramienta no certifica seguridad contra incendios.'))
