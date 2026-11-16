"""Fase 16 — Integración conservadora de tablas NASA PSI adicionales.
No inventa experimentos, fuentes ni mediciones. Los CSV solo se cuentan cuando existen.
"""
from __future__ import annotations
from pathlib import Path
from io import BytesIO
from datetime import datetime, timezone
import hashlib
import json
import re
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

BASE = Path(__file__).resolve().parent
DATA = BASE / "data"
MAX_BYTES = 5 * 1024 * 1024

STUDIES = {
    "BASS": {
        "id": "PSI-26", "filename": "bass_experimental.csv", "meta": "bass_provenance.json",
        "title_es": "BASS: combustión de sólidos", "title_en": "BASS: solid-fuel combustion",
        "expected": 121, "original": "PSI-26_Experimental table_BASS.csv",
        "fields": ("test",), "description_es": "Ensayos con materiales sólidos; la tabla de condiciones puede no incluir resultados finales de combustión.",
        "description_en": "Solid-material test conditions; the table may not contain combustion outcomes."
    },
    "SAME-R": {
        "id": "PSI-101", "filename": "same_r_experimental.csv", "meta": "same_r_provenance.json",
        "title_es": "SAME-R: aerosoles de humo", "title_en": "SAME-R: smoke aerosols",
        "expected": 109, "original": "PSI-101_Experimental table_SAME-R.csv",
        "fields": ("sample", "test"), "description_es": "Registros sobre generación, mezcla y transporte de partículas de humo, útiles para preguntas de detección.",
        "description_en": "Smoke generation, mixing and transport records, relevant to fire-detection research."
    },
    "CFI": {
        "id": "PSI-39", "filename": "cfi_experimental.csv", "meta": "cfi_provenance.json",
        "title_es": "CFI: investigación de llamas frías", "title_en": "CFI: cool flames investigation",
        "expected": 87, "original": "PSI-39_Experimental table_CFI.csv",
        "fields": ("fuel",), "description_es": "Condiciones y muestras relacionadas con combustión de gotas y llamas frías.",
        "description_en": "Droplet-combustion and cool-flame test conditions."
    }
}

def nasa_link(spec):
    return "https://psi.nasa.gov/physci/repo/data/investigations/" + spec["id"]

def _parse_csv(blob, spec):
    if not blob or len(blob) > MAX_BYTES:
        raise ValueError("Archivo vacío o demasiado grande (máximo 5 MB).")
    if blob[:256].lstrip().lower().startswith((b"<html", b"<!doctype", b"{", b"[")):
        raise ValueError("La respuesta no parece un archivo CSV.")
    errors=[]
    for encoding in ("utf-8-sig", "cp1252", "latin-1"):
        try:
            df=pd.read_csv(BytesIO(blob), encoding=encoding, dtype=str, keep_default_na=False)
            if df.empty or len(df.columns)<4 or len(df)>10000:
                raise ValueError("La tabla debe tener filas y al menos cuatro columnas.")
            df.columns=[str(c).strip().lstrip("\ufeff") for c in df.columns]
            header=" ".join(df.columns).lower()
            if not all(field in header for field in spec["fields"]):
                raise ValueError("Columnas esperadas ausentes; comprobar si descargó la tabla correcta de NASA PSI.")
            if any(not c or c.lower().startswith("unnamed:") for c in df.columns):
                # CSVs sometimes have unnamed index columns: preserve them, and warn in the UI.
                pass
            return df
        except (UnicodeError, pd.errors.ParserError, ValueError) as exc:
            errors.append(str(exc)[:140])
    raise ValueError("No se pudo validar el archivo: " + " / ".join(errors[-2:]))

def _local_source(key):
    spec=STUDIES[key]
    path=DATA/spec["filename"]
    if not path.is_file():
        return None, None, None
    blob=path.read_bytes()
    df=_parse_csv(blob,spec)
    source={
        "source_status":"local_file_not_independently_verified",
        "source_file":str(path.relative_to(BASE)),
        "sha256":hashlib.sha256(blob).hexdigest(),
        "source_page":nasa_link(spec),
        "filename_expected_at_nasa":spec["original"]
    }
    meta=DATA/spec["meta"]
    if meta.exists():
        try:
            saved=json.loads(meta.read_text(encoding="utf-8"))
            if isinstance(saved,dict):
                source.update(saved)
                source["sha256_actual"] = hashlib.sha256(blob).hexdigest()
                if source.get("sha256") != source["sha256_actual"]:
                    source["hash_mismatch"] = True
        except (ValueError,OSError):
            source["provenance_warning"]="Metadata JSON not readable"
    return blob, df, source

def local_counts():
    counts={}
    for key in STUDIES:
        try:
            _,df,_=_local_source(key)
            counts[key]=0 if df is None else len(df)
        except (OSError,ValueError,pd.errors.ParserError):
            counts[key]=0
    return counts

def _numeric_measures(df):
    # For charts use columns with a meaningful physical label; never numeric IDs, dates or codes.
    measures={}
    for col in df.columns:
        lower=col.casefold()
        if any(x in lower for x in ("test #", "test number", "identifier", "sample #", "date", "time of day", "gmt", "id", "flex number")):
            continue
        if not any(x in lower for x in ("oxygen", "pressure", "duration", "velocity", "flow", "diameter", "aging", "mixing", "temperature", "concentration", "he", "n2", "o2", "co2", "mm", "sec", "atm", "cm/s", "%", "r0")):
            continue
        series=pd.to_numeric(df[col].astype(str).str.strip().str.replace(",",".",regex=False), errors="coerce")
        if series.notna().sum() >= max(3, int(len(df)*.3)):
            measures[col]=series
    return measures

def _id_column(df):
    ranked=[]
    for c in df.columns:
        s=c.lower()
        if "test #" in s or "test number" in s or "same test" in s or "cir"==s or "test id" in s:
            ranked.append((0,c))
        elif "test" in s or "flex number" in s:
            ranked.append((1,c))
        elif "sample" in s:
            ranked.append((2,c))
    ranked.sort()
    return ranked[0][1] if ranked else None

def _tr(language, es, en):
    return en if str(language).strip().lower() in ("english","en","inglés","ingles") else es

def render_multi_study(language="Español"):
    tr=lambda es,en:_tr(language,es,en)
    st.title(tr("🧪 Más experimentos NASA PSI", "🧪 More NASA PSI experiments"))
    st.caption(tr("Fase 16 · BASS, SAME-R y CFI · Tablas experimentales independientes", "Phase 16 · BASS, SAME-R and CFI · Independent experimental tables"))
    st.info(tr(
        "Aquí se importan archivos CSV originales sin cambiar BASS-II ni FLEX. La cantidad de filas solo se actualiza cuando existe una tabla cargada y válida.",
        "Import original CSV files without changing BASS-II or FLEX. Counts change only when a valid table is actually loaded."
    ))
    counts=local_counts()
    cols=st.columns(3)
    for c,(key,spec) in zip(cols,STUDIES.items()):
        c.metric(key, counts[key], help=tr("Filas permanentes encontradas en data/", "Permanent rows found in data/"))
    label=tr("Selecciona investigación", "Choose investigation")
    key=st.selectbox(label,list(STUDIES.keys()),format_func=lambda k:STUDIES[k]["title_en"] if str(language).lower()=="english" else STUDIES[k]["title_es"])
    spec=STUDIES[key]
    st.markdown("**" + (spec["description_en"] if str(language).lower()=="english" else spec["description_es"]) + "**")
    st.link_button(tr("Abrir investigación oficial NASA PSI", "Open official NASA PSI investigation"), nasa_link(spec))
    st.caption(tr("Archivo a buscar en NASA: ", "NASA file to look for: ")+spec["original"])
    try:
        blob,df,prov=_local_source(key)
    except (OSError,ValueError) as exc:
        st.error(tr("Archivo guardado inválido: ", "Invalid committed file: ")+str(exc));blob=df=prov=None
    uploaded=st.file_uploader(tr("O carga aquí el CSV original descargado de NASA (máximo 5 MB)", "Or upload the original NASA CSV (max 5 MB)"),type=["csv"],key="wari_phase16_upload_"+key)
    if uploaded is not None:
        try:
            temp=uploaded.getvalue()
            parsed=_parse_csv(temp,spec)
            blob=temp
            df=parsed
            prov={
                "source_status":"user_supplied_not_independently_verified",
                "source_file":uploaded.name,
                "sha256":hashlib.sha256(blob).hexdigest(),
                "source_page":nasa_link(spec),
                "filename_expected_at_nasa":spec["original"],
                "retrieved_utc":datetime.now(timezone.utc).isoformat(),
                "note":"Uploaded by user; original NASA bytes have not been independently checked."
            }
            st.warning(tr("CSV cargado temporalmente: para conservarlo después de reiniciar, descarga el CSV y el JSON y súbelos a data/ de GitHub.", "Temporary CSV upload: download both the CSV and provenance JSON, then commit them to data/ on GitHub."))
        except (ValueError,OSError) as exc:
            st.error(tr("CSV rechazado: ","CSV rejected: ")+str(exc))
    if df is None:
        st.warning(tr("Todavía no se han incorporado mediciones de esta investigación. No se cuentan filas hipotéticas.","No measurements loaded for this investigation. Potential rows are not counted."))
        st.caption(tr(f"Referencia: {spec['expected']} filas en un inventario externo; confirmar con la versión oficial.",f"Reference: {spec['expected']} rows in an external inventory; verify against the official version."))
        return
    st.success(tr(f"Tabla cargada: {len(df)} filas, {len(df.columns)} columnas.",f"Table loaded: {len(df)} rows, {len(df.columns)} columns."))
    if len(df)!=spec["expected"]:
        st.warning(tr(f"La versión contiene {len(df)} filas; el inventario externo menciona {spec['expected']}. Comprueba si hay encabezados o filas de continuación.",f"This version has {len(df)} rows; an external inventory lists {spec['expected']}. Check version and continuation rows."))
    if prov.get("hash_mismatch"):
        st.error(tr("La huella del archivo no coincide con el JSON de procedencia.","The file hash differs from the provenance JSON."))
    ptab, ctab, stab = st.tabs([
        tr("🔎 Explorar tabla","🔎 Explore table"),
        tr("📈 Mediciones","📈 Measurements"),
        tr("🔗 Procedencia y guardar","🔗 Provenance and save")
    ])
    with ptab:
        q=st.text_input(tr("Buscar en todas las columnas","Search across all columns"),key="phase16_query_"+key)
        filtered=df
        if q.strip():
            mask=df.astype(str).apply(lambda s:s.str.contains(q,case=False,regex=False,na=False)).any(axis=1)
            filtered=df[mask]
        st.metric(tr("Filas filtradas","Filtered rows"),len(filtered))
        try:
            st.dataframe(filtered,hide_index=True,width="stretch")
        except TypeError:
            st.dataframe(filtered,hide_index=True,use_container_width=True)
        st.download_button(tr("Descargar tabla filtrada CSV","Download filtered CSV"),filtered.to_csv(index=False).encode("utf-8-sig"),file_name=key.lower().replace("-","_")+"_filtrado.csv",mime="text/csv",key="phase16_filtered_"+key)
    with ctab:
        measures=_numeric_measures(df)
        if not measures:
            st.info(tr("No se identificaron columnas numéricas físicas interpretables. Consulta la tabla original.","No suitable physical numeric columns were identified. Consult the original table."))
        else:
            measure=st.selectbox(tr("Variable (unidad según encabezado NASA)","Variable (unit as given in NASA header)"),list(measures),key="phase16_measure_"+key)
            series=measures[measure]
            numeric=series.dropna()
            a,b,c=st.columns(3)
            a.metric(tr("Mediciones válidas","Numeric readings"),len(numeric))
            b.metric(tr("Ausentes o textuales","Missing or textual"),len(df)-len(numeric))
            c.metric(tr("Filas totales","Total rows"),len(df))
            idc=_id_column(df)
            x=df[idc].astype(str) if idc else df.index.astype(str)
            chart=pd.DataFrame({"id":x,"value":series}).dropna().head(60)
            if not chart.empty:
                fig=go.Figure(go.Bar(x=chart["id"],y=chart["value"],marker_color="#46d9ff"))
                fig.update_layout(template="plotly_dark",height=400,paper_bgcolor="#102038",plot_bgcolor="#102038",xaxis_title=(idc or "row"),yaxis_title=measure)
                st.plotly_chart(fig,use_container_width=True)
            st.warning(tr("Gráfico descriptivo; valores faltantes no se imputan. El nombre de columna conserva la información de unidad original.","Descriptive chart; missing values are never imputed. The column label preserves original unit information."))
    with stab:
        st.json(prov)
        st.caption(tr("Verifica la fuente: un archivo cargado o una copia de terceros no implica que su identidad con NASA haya sido comprobada.","Verify provenance: uploaded files or mirrors are not automatically authenticated against NASA."))
        st.download_button(tr("1. Descargar CSV íntegro para data/","1. Download complete CSV for data/"),blob,file_name=spec["filename"],mime="text/csv",key="phase16_raw_"+key)
        meta_blob=json.dumps(prov,ensure_ascii=False,indent=2).encode("utf-8")
        st.download_button(tr("2. Descargar procedencia JSON","2. Download provenance JSON"),meta_blob,file_name=spec["meta"],mime="application/json",key="phase16_prov_"+key)
        st.code("data/"+spec["filename"]+"\ndata/"+spec["meta"],language="text")
