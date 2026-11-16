"""WARI FIRE AI — consultor documental verificable, sin API generativa.

El módulo usa únicamente archivos CSV entregados con el proyecto.
No consulta a NASA en tiempo real ni inventa mediciones.
"""
import re
import unicodedata
from html import escape

import pandas as pd
import streamlit as st
from llm_optional import configured, explain

NASAPSI = "https://www.nasa.gov/physical-sciences-informatics-psi/psi-investigations-by-research-area/"


def normalize(s):
    t = unicodedata.normalize("NFKD", str(s).casefold())
    return "".join(c for c in t if not unicodedata.combining(c))


def _record_number(row, key):
    val=row.get(f"{key}_num",float("nan"))
    return float(val) if pd.notna(val) else None


def _display(v):
    if pd.isna(v):
        return "—"
    if isinstance(v,float):
        return f"{v:.3f}".rstrip('0').rstrip('.')
    return str(v)


def lookup(question, bass, cols, catalog, en):
    """Deterministic, citation-backed retrieval. Return markdown text and relevant records."""
    q=normalize(question)
    ids=re.findall(r"\b([bmnopft]\d{1,3})\b",q,re.I)
    ids=[x.upper() for x in ids if x.upper() in set(bass['_test'].astype(str).str.upper())] if bass is not None else []
    gas="CO2" if re.search(r"\bco2\b|dioxido|carbon dioxide",q) else ("CO" if re.search(r"\bco\b|monoxido|monoxide",q) else "O2")
    mention_gas=bool(re.search(r"\bo2\b|oxigeno|oxygen|\bco2\b|dioxido|\bco\b|monoxido|monoxide",q))
    asked_compare=any(t in q for t in ("compar", "diferencia", "versus", " vs ","contrast"))
    asked_catalog=any(t in q for t in ("bass", "same", "flex", "investigacion", "research", "estudi", "study")) and not ids
    material="PMMA" if "pmma" in q else None

    if bass is None and not asked_catalog:
        return ("No se encontró el archivo de ensayos BASS-II." if not en else "BASS-II data file not found."),None

    subset=bass.copy() if bass is not None else None
    if ids:
        subset=subset[subset['_test'].str.upper().isin(ids)]
    elif material and cols.get('material'):
        subset=subset[subset[cols['material']].astype(str).str.contains('PMMA',case=False,na=False)]

    if ids and len(ids)>=2 and asked_compare:
        selected=[]
        for t in dict.fromkeys(ids[:2]):
            rr=subset[subset['_test'].str.upper()==t]
            if len(rr): selected.append(rr.iloc[0])
        if len(selected)==2:
            a,b=selected
            unit='ppm' if gas=='CO' else '% vol.'
            v=[]
            for row in (a,b):
                i=_record_number(row,f'{gas}_i')
                f=_record_number(row,f'{gas}_f')
                v.append((i,f,(f-i) if i is not None and f is not None else None))
            label=('Ensayo' if not en else 'Test')
            parts=[f"**{'Comparación' if not en else 'Comparison'} {gas}: {ids[0]} / {ids[1]}**",
                   f"| {label} | {'Inicial' if not en else 'Initial'} ({unit}) | {'Final' if not en else 'Final'} ({unit}) | Δ {'final − inicial' if not en else 'final − initial'} ({unit}) |",
                   '|---|---:|---:|---:|']
            for row,values in zip((a,b),v):
                parts.append(f"| {row['_test']} | {_display(values[0])} | {_display(values[1])} | {_display(values[2])} |")
            parts.append(('**Interpretación:** las diferencias son descriptivas y no prueban causalidad.' if not en else '**Interpretation:** these differences are descriptive and do not prove causation.'))
            parts.append(_citation(en))
            return '\n\n'.join(parts[:2])+ '\n'+'\n'.join(parts[2:]), subset

    if ids:
        rows=subset.head(5)
        if rows.empty:
            return ('No encontré esos identificadores en el CSV cargado.' if not en else 'Those IDs were not found in the loaded CSV.'),None
        parts=[]
        for _,r in rows.iterrows():
            meta = []
            for key, label in [('material','Material'),('pi','PI'),('date','Fecha' if not en else 'Date')]:
                if cols.get(key): meta.append(f"{label}: {_display(r[cols[key]])}")
            details=' · '.join(meta)
            parts.append(f"**{r['_test']}** — {details}")
            for g in ([gas] if mention_gas else ['O2','CO2','CO']):
                if cols.get(f'{g}_i') and cols.get(f'{g}_f'):
                    i=_record_number(r,f'{g}_i');f=_record_number(r,f'{g}_f')
                    if i is not None or f is not None:
                        u='ppm' if g=='CO' else '% vol.'
                        parts.append(f"{g}: {_display(i)} → {_display(f)} {u}; Δ = {_display(f-i if i is not None and f is not None else None)} {u}.")
        parts.append(_citation(en))
        return '\n\n'.join(parts),rows

    if material:
        rows=subset
        valid=rows.dropna(subset=[f'{gas}_i_num',f'{gas}_f_num']) if f'{gas}_i_num' in rows and f'{gas}_f_num' in rows else rows.iloc[:0]
        count=len(valid)
        intro=(f"Encontré **{len(rows)} ensayos** cuya descripción incluye PMMA. **{count}** tienen un par numérico inicial/final utilizable de {gas}." if not en else
               f"Found **{len(rows)} tests** whose material description includes PMMA. **{count}** have valid numeric initial/final {gas} pairs.")
        if rows.empty: return ('No hay ensayos con PMMA en el CSV cargado.' if not en else 'No PMMA tests found.'),None
        samples=', '.join(rows['_test'].head(12).astype(str))
        conclusion=('Estos son registros recuperados por descripción de material, no una clasificación experimental automática.' if not en else 'These records were retrieved from material descriptions; they are not an automatic experimental classification.')
        return f"{intro}\n\n**{'Ejemplos' if not en else 'Examples'}:** {samples}\n\n{conclusion}\n\n{_citation(en)}",rows

    if asked_catalog and catalog is not None:
        key = next((x for x in ('BASS','SAME','FLEX') if x.lower() in q),None)
        rows=catalog[catalog['experimento'].str.upper()==key] if key else catalog
        text=("Los siguientes registros son descripciones de catálogo. **No son mediciones experimentales.**" if not en else
              "The following records are catalog descriptions, **not experimental measurements**.")
        translations = {
            'BASS': 'Investigates burning and suppression of solid materials in microgravity.',
            'SAME': 'Studies smoke and aerosol characteristics in microgravity.',
            'FLEX': 'Investigates extinguishment of liquid fuel droplet flames in microgravity.',
        }
        for _,row in rows.iterrows():
            name = str(row['experimento']).upper()
            summary = translations.get(name, 'Catalog description not yet translated; consult the original source.') if en else str(row['descripcion'])
            text += f"\n\n**{row['experimento']}** — {summary}  \n[{'Fuente' if not en else 'Source'}]({row['fuente']})"
        return text,None

    if mention_gas and bass is not None:
        ini=f'{gas}_i_num';fin=f'{gas}_f_num'
        if ini not in bass or fin not in bass:
            return ('No encuentro esas columnas en el archivo cargado.' if not en else 'Required columns are absent.'),None
        valid=bass.dropna(subset=[ini,fin]).copy()
        intro=(f"En el CSV BASS-II hay **{len(valid)} pares numéricos** inicial/final para {gas} (de {len(bass)} registros)." if not en else
               f"The BASS-II CSV contains **{len(valid)} numeric initial/final pairs** for {gas} (of {len(bass)} records).")
        if valid.empty:return intro+'\n\n'+_citation(en),None
        valid['_delta']=valid[fin]-valid[ini]
        intro+=(f" La diferencia promedio final − inicial de esos pares es **{valid['_delta'].mean():.3f} {'ppm' if gas=='CO' else '% vol.'}**. Este promedio descriptivo no identifica causas." if not en else
                f" The mean final − initial difference in those pairs is **{valid['_delta'].mean():.3f} {'ppm' if gas=='CO' else '% vol.'}**. This descriptive mean cannot establish causes.")
        return intro+'\n\n'+_citation(en),valid

    return ("Puedo buscar **PMMA**, consultar un ensayo como **B2**, comparar **B2 y B4**, resumir mediciones de **O₂** o mostrar el catálogo **BASS, SAME y FLEX**. Para otras preguntas, todavía no tengo un modelo de lenguaje conectado ni evidencia documental suficiente."
            if not en else
            "I can search **PMMA**, retrieve a test such as **B2**, compare **B2 and B4**, summarize **O₂** measurements, or show catalog entries for **BASS, SAME and FLEX**. For other questions, no language model is connected yet and I may lack supporting evidence."),None


def _citation(en):
    return (f"**{'Fuente' if not en else 'Source'}:** NASA PSI, `PSI-25_Experimental table_BASS-II.csv`, "
            + ('columna `Test #` para identificar filas. ' if not en else 'column `Test #` identifies rows. ')
            + f"[{'Portal NASA PSI' if not en else 'NASA PSI portal'}]({NASAPSI}). "
            + ('La aplicación utiliza una copia local; no consulta NASA en tiempo real.' if not en else 'The app uses a local copy; it does not query NASA in real time.'))


def render_assistant(bass, cols, catalog, language):
    en = language == 'English'
    st.markdown('## 🤖 ' + ('Asistente WARI AI — Evidencia y explicación' if not en
                             else 'WARI AI — Evidence and explanations'))
    st.caption('Consulta nuestros registros BASS-II y su documentación, en tu idioma.' if not en
               else 'Explore our BASS-II records and documentation in your own language.')

    is_ready = configured(st.secrets)
    choice = st.radio('Modo de respuesta' if not en else 'Response mode',
        ['evidence', 'llm'] if is_ready else ['evidence'],
        format_func=lambda opt: (
            ('Datos verificables (sin IA generativa)' if not en else 'Verified data (no generative AI)')
            if opt == 'evidence' else
            ('Explicación con IA (experimental)' if not en else 'AI explanation (experimental)')),
        horizontal=True, key='wari_response_mode')
    if is_ready:
        st.info('La IA remota está configurada. Solo interpreta los datos recuperados; verifica siempre las fuentes.' if not en
                else 'Remote AI is configured. It only interprets retrieved data; always check source records.')
    else:
        st.info('Modo gratuito sin clave API: consultas reproducibles del CSV. La IA generativa se activará solo cuando el administrador configure un proveedor HTTPS compatible en Secrets.' if not en
                else 'Free mode without API key: reproducible CSV lookups. Generative AI is enabled only if an administrator configures a compatible HTTPS provider in Secrets.')

    presets = (["¿Qué ensayos contienen PMMA?", "Compara B2 y B4 en O2",
                "¿Qué mediciones de CO2 hay?", "¿Qué estudia SAME?"] if not en else
               ["Which tests contain PMMA?", "Compare B2 and B4 O2",
                "What CO2 measurements are available?", "What is SAME?"])
    st.markdown('#### ' + ('Prueba una pregunta' if not en else 'Try a question'))
    cc = st.columns(2)
    selected = None
    for i, prompt in enumerate(presets):
        if cc[i % 2].button(prompt, key='wari_example_' + str(i), use_container_width=True):
            selected = prompt

    # Do not display a previously generated Spanish answer when English is selected.
    history_key = 'wari_chat_v11_en' if en else 'wari_chat_v11_es'
    if history_key not in st.session_state:
        st.session_state[history_key] = []
    history = st.session_state[history_key]
    st.markdown('#### ' + ('Conversación' if not en else 'Conversation'))
    for msg in history[-14:]:
        with st.chat_message(msg['role']):
            st.markdown(msg['text'])

    question = st.chat_input('Ej.: Compara B2 y B4 en O2' if not en else 'e.g. Compare B2 and B4 O2',
                             max_chars=500, key='wari_question_input')
    if selected:
        question = selected
    if question:
        question = str(question).strip()[:500]
        history.append({'role': 'user', 'text': question})
        result, records = lookup(question, bass, cols, catalog, en)
        reply = result
        if choice == 'llm' and is_ready:
            # Only use well-founded retrieved results, not a generic fallback answer.
            if records is not None or any(x in normalize(question) for x in ('same', 'flex', 'bass')):
                try:
                    if st.session_state.get('wari_llm_requests', 0) >= 8:
                        raise RuntimeError('session limit')
                    st.session_state.wari_llm_requests = st.session_state.get('wari_llm_requests', 0) + 1
                    with st.spinner('Explicando evidencia...' if not en else 'Explaining evidence...'):
                        generated = explain(question, result, language, st.secrets)
                    reply = (('**Explicación de IA (revisar):**' if not en else '**AI explanation (review):**')
                             + '\n\n' + generated + '\n\n---\n'
                             + ('**Evidencia recuperada:**' if not en else '**Retrieved evidence:**')
                             + '\n\n' + result)
                except (RuntimeError, ValueError):
                    reply = (('No fue posible obtener una respuesta remota. Se muestran los datos originales.' if not en
                              else 'The remote response is unavailable. Showing original evidence instead.')
                             + '\n\n' + result)
        history.append({'role': 'assistant', 'text': reply})
        st.rerun()

    if history and st.button('🧹 ' + ('Borrar conversación' if not en else 'Clear conversation')):
        st.session_state[history_key] = []
        st.rerun()
    st.caption('Fuente de referencia: NASA PSI; copia local de BASS-II. Sin predicciones certificadas.' if not en
               else 'Reference source: NASA PSI; local BASS-II copy. No certified predictions.')
