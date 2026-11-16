"""WARI FIRE AI — guided, evidence-grounded Space Apps jury demonstration.

No predictive claims: measured BASS-II readings are descriptively compared.
"""
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from reports import _records, create_pdf, TEXT as REPORT_TEXT

SOURCE = "https://psi.nasa.gov/physci/repo/data/investigations/PSI-25"

WORDS = {
    "Español": {
        "title":"🚀 Modo jurado · Demostración guiada",
        "intro":"Una demostración reproducible para explicar qué problema aborda WARI FIRE AI, qué datos usa y qué resultados puede demostrar.",
        "warning":"**Alcance:** WARI FIRE AI es un prototipo educativo y de consulta científica. No predice incendios, no calcula riesgos certificados y no sustituye ensayos de seguridad.",
        "step":"Etapa de la demostración", "labels":["1 · Problema y propuesta", "2 · Fuente y ensayos", "3 · Comparación experimental", "4 · Informe descargable", "5 · Defensa ante jurados"],
        "next":"Siguiente etapa →", "back":"← Etapa anterior", "progress":"Avance de la demostración", "start":"Reiniciar recorrido",
        "problem":"¿Cuál es el problema?", "problem_text":"Los experimentos de combustión en microgravedad contienen datos valiosos, pero interpretarlos es difícil para estudiantes y personas no especialistas. El reto es hacerlos accesibles sin perder su procedencia y sus limitaciones.",
        "proposal":"¿Qué propone WARI FIRE AI?", "proposal_text":"Una plataforma bilingüe que reúne aprendizaje visual, exploración de datos BASS-II, comparación de ensayos, consultas documentadas y elaboración de informes.",
        "benefit":"Aporte demostrable", "benefit_text":"Acorta el recorrido desde una tabla experimental hasta una comparación comprensible y un informe trazable. Esto es una mejora de acceso y comunicación de evidencia; no es una prueba de que mejore por sí mismo la seguridad operacional.",
        "roadmap":"Flujo completo", "source":"Fuente original", "source_text":"Las cifras proceden de la tabla experimental BASS-II conservada en el proyecto. Los gráficos no son predicciones de comportamiento de llamas.",
        "total":"Registros BASS-II", "numeric":"Pares numéricos O₂", "sample":"Ensayos de demostración", "material":"Material", "pi":"Investigador", "test":"Ensayo", "missing":"No disponible", "gas":"Gas a comparar", "initial":"Inicial", "final":"Final", "delta":"Final − inicial", "unit":"Unidad", "reading":"Lecturas registradas", "chart":"Comparación de las lecturas", "interpretation":"Interpretación responsable", "disclaimer":"El contraste entre valores no indica por sí solo la causa del cambio, la inflamabilidad del material ni la seguridad de una misión.", "ambig":"Los campos ausentes o no numéricos se mantienen como no disponibles.",
        "report":"Genera la evidencia para el jurado", "report_info":"Este PDF usa únicamente los ensayos escogidos y documenta las limitaciones metodológicas.", "download":"Descargar informe PDF de esta demostración", "csv":"Descargar datos de esta comparación (CSV)",
        "pitch":"Guion breve de presentación (aprox. 90 segundos)", "pitch_text":"Somos Wari Teams, de Ayacucho, Perú. WARI FIRE AI aborda un desafío clave de la investigación espacial: facilitar la comprensión de los experimentos de combustión en microgravedad. Nuestra plataforma transforma registros reales de NASA PSI en consultas, gráficos y explicaciones bilingües. Aquí seleccionamos dos ensayos BASS-II, consultamos sus mediciones de oxígeno y comprobamos las diferencias sin alterar datos originales. Después generamos un informe con fuente y advertencias. El valor de nuestra propuesta está en la trazabilidad y la accesibilidad: permite pasar de los datos a una explicación verificable, tanto para estudiantes como para investigadores. Nuestro prototipo no predice incendios ni certifica materiales; creemos que la siguiente etapa es validar su utilidad con usuarios y especialistas.",
        "questions":"Preguntas difíciles del jurado", "qa":[
            ("¿Esto no lo puede hacer ChatGPT?", "Un modelo general puede resumir tablas, pero aquí la persona interactúa con un conjunto identificado de ensayos, comprueba números originales, observa valores faltantes y descarga el procedimiento. Nuestra diferenciación está en integrar un flujo reproducible de datos y enseñanza, no en afirmar que inventamos la inteligencia artificial."),
            ("¿Cómo beneficia a NASA?", "Puede servir como prototipo de herramienta de divulgación y exploración preliminar de resultados PSI. Aún no hay evidencia de adopción, validación operativa ni impacto directo sobre decisiones de seguridad de NASA."),
            ("¿Sus gráficos prueban un riesgo de incendio?", "No. Las diferencias de O₂, CO₂ y CO describen las lecturas de esos ensayos. Sin diseño experimental, contexto instrumental y un modelo validado no determinan una probabilidad de incendio."),
            ("¿En qué se diferencia la simulación de los datos?", "Las llamas del módulo educativo son ilustraciones conceptuales. La sección Datos NASA y esta demostración muestran valores de un CSV experimental. Ambas partes están identificadas por separado."),
            ("¿Se puede ampliar?", "Sí, si se incorporan otros conjuntos PSI con trazabilidad, controles de calidad por experimento y validación con expertos. Integrar una base adicional no equivale por sí solo a validar una predicción.")
        ],
        "go":"Abrir módulo relacionado", "linked":{"simulator":"🔥 Simulador", "explorer":"📈 Explorador", "compare":"⚖️ Comparación", "reports":"📄 Informes", "assistant":"🤖 Asistente"}, "no_data":"No fue posible cargar la tabla BASS-II; revisa la carpeta data.", "select":"Selecciona dos ensayos distintos para comparar.", "good":"Valores originales usados solo cuando son numéricos inequívocos.", "notes":"Propuesta para el jurado: muestra un ensayo con una celda ausente y explica por qué no la inventamos.", "nasa":"Abrir registro fuente NASA PSI"
    },
    "English": {
        "title":"🚀 Jury mode · Guided demonstration", "intro":"A reproducible walkthrough showing the problem WARI FIRE AI addresses, its data source and the conclusions it can support.",
        "warning":"**Scope:** WARI FIRE AI is an educational and scientific data-exploration prototype. It does not predict fires, provide certified risk estimates, or replace safety testing.",
        "step":"Demonstration stage", "labels":["1 · Problem and approach", "2 · Source and tests", "3 · Experimental comparison", "4 · Downloadable report", "5 · Jury questions"],
        "next":"Next stage →", "back":"← Previous stage", "progress":"Demonstration progress", "start":"Restart walkthrough",
        "problem":"What is the problem?", "problem_text":"Microgravity combustion experiments contain valuable data, but they can be difficult for students and nonspecialists to interpret. The challenge is to make them accessible without losing provenance or caveats.",
        "proposal":"What does WARI FIRE AI offer?", "proposal_text":"A bilingual platform combining visual learning, BASS-II data exploration, experiment comparison, evidence-based queries and report generation.",
        "benefit":"Demonstrable value", "benefit_text":"It shortens the path from an experimental table to an understandable comparison and a traceable report. This improves access to evidence, but is not proof of improved operational safety.",
        "roadmap":"End-to-end workflow", "source":"Original data source", "source_text":"The numbers come from the original BASS-II experimental table retained in this project. Charts are not fire-behavior predictions.",
        "total":"BASS-II records", "numeric":"Numeric O₂ pairs", "sample":"Demo test selection", "material":"Material", "pi":"Principal investigator", "test":"Test", "missing":"Unavailable", "gas":"Gas to compare", "initial":"Initial", "final":"Final", "delta":"Final − initial", "unit":"Unit", "reading":"Recorded measurements", "chart":"Reading comparison", "interpretation":"Responsible interpretation", "disclaimer":"Differences alone do not establish causation, flammability, or mission safety.", "ambig":"Missing or nonnumeric values remain unavailable.",
        "report":"Generate evidence for the jury", "report_info":"This PDF uses only your selected tests and documents methodological limitations.", "download":"Download demo PDF report", "csv":"Download comparison data (CSV)",
        "pitch":"Short presentation script (about 90 seconds)", "pitch_text":"We are Wari Teams, from Ayacucho, Peru. WARI FIRE AI tackles a key challenge in space research: making microgravity combustion experiments easier to understand. Our platform turns real NASA PSI records into bilingual queries, charts and explanations. Here we select two BASS-II tests, inspect oxygen measurements and compare differences without changing the original data. We then generate a report with its source and caveats. Our contribution is traceability and accessibility: moving from experimental data to verifiable explanations for students and researchers alike. Our prototype does not predict fires or certify materials; our next step is to evaluate usability with users and specialists.",
        "questions":"Tough jury questions", "qa":[
            ("Couldn't ChatGPT do this?", "A general model can summarize tables. Here, users inspect a specific set of tests, verify the raw numbers, see missing data and export a traceable report. Our differentiation is the reproducible evidence-and-learning workflow, not a claim to have invented AI."),
            ("How does this benefit NASA?", "It may be useful as a prototype for public communication and preliminary exploration of PSI results. No operational adoption, validation or direct NASA safety impact has yet been established."),
            ("Do your charts prove fire risk?", "No. O₂, CO₂ and CO differences describe recorded readings. Without the experimental context and a validated model, they do not quantify fire probability."),
            ("How is the simulator different from the data?", "Flame illustrations in the educational module are conceptual. The NASA Data tab and this demonstration use measurements from an experimental CSV. The two are clearly separated."),
            ("Can it scale?", "Yes, by adding other traceable PSI datasets, experiment-specific quality checks and expert review. Adding more data is not the same as validating a prediction.")
        ],
        "go":"Open related module", "linked":{"simulator":"🔥 Simulator", "explorer":"📈 Explorer", "compare":"⚖️ Comparison", "reports":"📄 Reports", "assistant":"🤖 Assistant"}, "no_data":"Could not load the BASS-II table; check the data directory.", "select":"Choose two different tests to compare.", "good":"Original values are used only when unambiguously numeric.", "notes":"Tip for your jury: pick a test with a missing cell and explain why the app never invents it.", "nasa":"Open NASA PSI source record"
    }
}

def _safe_num(row, col):
    if not col:
        return None
    try:
        raw = str(row[col]).strip()
        if not raw or raw.lower() in {'none','nan','n/a','--','-'}:
            return None
        import re
        if not re.fullmatch(r'[+-]?(?:\d+(?:[.,]\d*)?|[.,]\d+)', raw):
            return None
        return float(raw.replace(',','.'))
    except (ValueError,TypeError,KeyError):
        return None

def _display(x):
    return '—' if x is None else f'{x:g}'

def _go(section):
    st.session_state['section_choice']=section

def render_jury_demo(bass, cols, language):
    t=WORDS.get(language,WORDS['Español'])
    st.title(t['title'])
    st.caption(t['intro'])
    st.warning(t['warning'])
    if bass is None or bass.empty or not cols.get('test'):
        st.error(t['no_data']);return
    if 'jury_step' not in st.session_state:st.session_state.jury_step=0
    step=st.selectbox(t['step'],list(range(5)),format_func=lambda n:t['labels'][n],key='jury_step')
    st.progress((step+1)/5,text=f"{t['progress']}: {step+1}/5")
    c1,c2,c3=st.columns([1,1,1])
    with c1:st.button(t['back'],disabled=step==0,on_click=lambda:st.session_state.update(jury_step=max(0,st.session_state.jury_step-1)),use_container_width=True)
    with c2:st.button(t['start'],on_click=lambda:st.session_state.update(jury_step=0),use_container_width=True)
    with c3:st.button(t['next'],disabled=step==4,on_click=lambda:st.session_state.update(jury_step=min(4,st.session_state.jury_step+1)),use_container_width=True)

    ids=bass['_test_key'].astype(str).tolist()
    default1='B1' if 'B1' in ids else ids[0]
    default2='B4' if 'B4' in ids else (ids[1] if len(ids)>1 else ids[0])
    if 'jury_a' not in st.session_state or st.session_state.jury_a not in ids: st.session_state.jury_a=default1
    if 'jury_b' not in st.session_state or st.session_state.jury_b not in ids: st.session_state.jury_b=default2

    if step==0:
        st.subheader(t['problem']);st.write(t['problem_text'])
        st.subheader(t['proposal']);st.write(t['proposal_text'])
        st.subheader(t['benefit']);st.write(t['benefit_text'])
        st.subheader(t['roadmap'])
        st.markdown(('**NASA PSI → BASS-II → Comparación → Explicación → PDF con fuentes**' if language=='Español' else '**NASA PSI → BASS-II → Comparison → Explanation → Traceable PDF**'))
        st.info(t['notes'])
    elif step==1:
        st.subheader(t['source']);st.write(t['source_text'])
        st.link_button(t['nasa'],SOURCE)
        o2i,o2f=cols.get('O2_i'),cols.get('O2_f')
        valid=0
        if o2i and o2f:
            valid=sum(_safe_num(row,o2i) is not None and _safe_num(row,o2f) is not None for _,row in bass.iterrows())
        a,b=st.columns(2)
        a.metric(t['total'],len(bass));b.metric(t['numeric'],valid)
        st.subheader(t['sample'])
        d1,d2=st.columns(2)
        with d1:st.selectbox(t['test']+' A',ids,key='jury_a')
        with d2:st.selectbox(t['test']+' B',ids,key='jury_b')
        sample=bass[bass['_test_key'].isin([st.session_state.jury_a,st.session_state.jury_b])]
        fields=[('_test_key',t['test']),(cols.get('material'),t['material']),(cols.get('pi'),t['pi'])]
        data=pd.DataFrame({label:sample[col].astype(str).values for col,label in fields if col})
        st.dataframe(data,hide_index=True,use_container_width=True)
        st.caption(t['good'])
    elif step==2:
        st.subheader(t['chart'])
        c1,c2=st.columns(2)
        with c1:st.selectbox(t['test']+' A',ids,key='jury_a')
        with c2:st.selectbox(t['test']+' B',ids,key='jury_b')
        gas=st.radio(t['gas'],['O2','CO2','CO'],horizontal=True,key='jury_gas')
        if st.session_state.jury_a==st.session_state.jury_b:
            st.warning(t['select']);return
        if not cols.get(gas+'_i') or not cols.get(gas+'_f'):
            st.warning(t['missing']);return
        rows=[]
        for tid in (st.session_state.jury_a,st.session_state.jury_b):
            row=bass.loc[bass['_test_key']==tid].iloc[0]
            ini=_safe_num(row,cols[gas+'_i']);final=_safe_num(row,cols[gas+'_f'])
            rows.append({t['test']:tid,t['initial']:ini,t['final']:final,t['delta']:final-ini if ini is not None and final is not None else None})
        table=pd.DataFrame(rows)
        st.markdown('#### '+t['reading'])
        st.dataframe(table,hide_index=True,use_container_width=True)
        fig=go.Figure()
        for key,color in ((t['initial'],'#46D9FF'),(t['final'],'#FF9D62')):
            fig.add_bar(x=table[t['test']],y=table[key],name=key,marker_color=color)
        fig.update_layout(template='plotly_dark',barmode='group',height=360,paper_bgcolor='#101A2A',plot_bgcolor='#101A2A',yaxis_title='ppm' if gas=='CO' else '% vol.')
        st.plotly_chart(fig,use_container_width=True)
        st.subheader(t['interpretation'])
        st.info(t['disclaimer']);st.caption(t['ambig']);st.link_button(t['nasa'],SOURCE)
    elif step==3:
        st.subheader(t['report']);st.write(t['report_info'])
        c1,c2=st.columns(2)
        with c1:st.selectbox(t['test']+' A',ids,key='jury_a')
        with c2:st.selectbox(t['test']+' B',ids,key='jury_b')
        if st.session_state.jury_a==st.session_state.jury_b:
            st.warning(t['select']);return
        t_report=REPORT_TEXT[language]
        export=_records(bass,cols,[st.session_state.jury_a,st.session_state.jury_b],['O2','CO2','CO'],t_report)
        if export.empty:
            st.warning(t['missing']);return
        st.dataframe(export,hide_index=True,use_container_width=True)
        pdf=create_pdf(export,['O2','CO2','CO'],language,'Wari Teams · Jury demonstration')
        st.download_button(t['download'],pdf,'WARI_FIRE_AI_JURY_BASS_II.pdf','application/pdf',use_container_width=True)
        st.download_button(t['csv'],export.to_csv(index=False).encode('utf-8-sig'),'WARI_FIRE_AI_JURY_BASS_II.csv','text/csv',use_container_width=True)
        st.warning(t['disclaimer'])
    else:
        st.subheader(t['pitch']);st.text_area(t['pitch'],t['pitch_text'],height=220,key=f'jury_pitch_{language}')
        st.subheader(t['questions'])
        for question,answer in t['qa']:
            with st.expander(question):st.write(answer)
        st.caption(t['source_text'])
    if step in (0,4):
        st.markdown('#### '+t['go'])
        columns=st.columns(5)
        for col,(key,text) in zip(columns,t['linked'].items()):
            col.button(text,key='jury_jump_'+key,on_click=_go,args=(key,),use_container_width=True)
