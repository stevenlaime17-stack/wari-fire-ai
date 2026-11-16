"""WARI FIRE AI / Experimental expansion.

Keep NASA BASS-II separate from FLEX. FLEX is sourced from NASA PSI-69
through NASA's public download endpoint, or clearly disclosed third-party
archive mirror if official retrieval is temporarily inaccessible.

Never claim that a test-table row is a validated flame-outcome observation.
"""
from __future__ import annotations

from io import BytesIO
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import re

import pandas as pd
import plotly.graph_objects as go
import requests
import streamlit as st

BASE = Path(__file__).resolve().parent
DATA = BASE / "data"
BASS_PATH = DATA / "bass_ii_experimental.csv"
FLEX_PATH = DATA / "flex_experimental.csv"
FLEX_META_PATH = DATA / "flex_provenance.json"
PSI_ID = "PSI-69"
PSI_URL = "https://psi.nasa.gov/physci/repo/data/investigations/PSI-69"
DOI = "10.60555/mbq8-0451"
PSI_API = "https://psi.nasa.gov/geode-py/ws"
NASA_FILENAME = "PSI-69_Experimental table_FLEX.csv"
MIRROR_URL = "https://raw.githubusercontent.com/Hekimovraiz/FIRE-X/main/Nasa_data/PSI-69_Experimental%20table_FLEX.csv"
MAX_BYTES = 2 * 1024 * 1024


def _lang(language: str) -> bool:
    return language.strip().lower() in {"en", "english", "inglés", "ingles"}


def _read_csv(blob: bytes) -> pd.DataFrame:
    if not blob or len(blob) > MAX_BYTES or blob.lstrip()[:32].lower().startswith((b"<!doctype", b"<html")):
        raise ValueError("Empty, oversized or non-CSV response")
    error = None
    for encoding in ("utf-8-sig", "cp1252", "latin-1"):
        try:
            df = pd.read_csv(BytesIO(blob), dtype=str, keep_default_na=False, encoding=encoding)
            df.columns = [str(c).strip().lstrip("\ufeff") for c in df.columns]
            if not (200 <= len(df) <= 500):
                raise ValueError(f"Unexpected FLEX table length: {len(df)}")
            h = " ".join(df.columns).casefold()
            if "fuel" not in h or "test" not in h or "droplet" not in h:
                raise ValueError("FLEX required columns not found")
            return df
        except (UnicodeError, pd.errors.ParserError, ValueError) as exc:
            error = exc
    raise ValueError(f"FLEX CSV validation failed: {error}")


def _http_bytes(url: str, timeout: float = 12) -> bytes:
    resp = requests.get(url, timeout=timeout, headers={"User-Agent":"WariFireAI-PSI-Research/1.0"})
    resp.raise_for_status()
    if len(resp.content) > MAX_BYTES:
        raise ValueError("Response exceeds size limit")
    return resp.content


def _official_download() -> bytes:
    """Best-effort official NASA Geode endpoint. Fails closed on bad payload."""
    errors = []
    for version in ("5", "4", "3"):
        try:
            resp = requests.get(
                f"{PSI_API}/studies/{PSI_ID}/download",
                params={"file": NASA_FILENAME, "version": version, "redirect": "false"},
                timeout=8,
                headers={"User-Agent":"WariFireAI-PSI-Research/1.0"},
            )
            resp.raise_for_status()
            blob = resp.content
            # Some API versions may return the CSV directly.
            try:
                _read_csv(blob)
                return blob
            except ValueError:
                pass
            txt = resp.text.strip().strip('"')
            try:
                payload = resp.json()
                if isinstance(payload, str):
                    txt = payload
                elif isinstance(payload, dict):
                    txt = next((payload[k] for k in ("url", "downloadUrl", "signedUrl", "link") if isinstance(payload.get(k), str)), txt)
            except ValueError:
                pass
            # Only NASA's HTTPS-signed AWS / Cloudfront file URLs are accepted.
            if txt.startswith("https://") and any(host in txt.lower() for host in ("amazonaws.com", "cloudfront.net", "psi.nasa.gov")):
                blob = _http_bytes(txt)
                _read_csv(blob)
                return blob
            errors.append(f"version {version}: unexpected response")
        except (requests.RequestException, ValueError) as exc:
            errors.append(f"version {version}: {str(exc)[:90]}")
    raise RuntimeError("Official NASA API unavailable: " + "; ".join(errors))


@st.cache_data(ttl=86400, show_spinner=False)
def fetch_flex():
    """Returns source bytes, provenance. Never substitutes invented measurements."""
    official_error = None
    try:
        blob = _official_download()
        _read_csv(blob)
        return blob, {
            "source_type": "NASA PSI official API",
            "retrieval_url": f"{PSI_API}/studies/{PSI_ID}/download",
            "source_page": PSI_URL,
            "doi": DOI,
            "sha256": hashlib.sha256(blob).hexdigest(),
            "retrieved_utc": datetime.now(timezone.utc).isoformat(),
            "official_checksum_compared": False,
        }
    except (RuntimeError, ValueError, requests.RequestException) as exc:
        official_error = str(exc)[:220]
    blob = _http_bytes(MIRROR_URL)
    _read_csv(blob)
    return blob, {
        "source_type": "Third-party GitHub mirror of NASA PSI table",
        "retrieval_url": MIRROR_URL,
        "source_page": PSI_URL,
        "doi": DOI,
        "sha256": hashlib.sha256(blob).hexdigest(),
        "retrieved_utc": datetime.now(timezone.utc).isoformat(),
        "official_checksum_compared": False,
        "note": "Mirror bytes have not been independently matched against NASA's original download.",
        "official_error": official_error,
    }


def _load_local():
    if not FLEX_PATH.is_file():
        return None, None, None
    blob = FLEX_PATH.read_bytes()
    df = _read_csv(blob)
    if FLEX_META_PATH.exists():
        try:
            prov = json.loads(FLEX_META_PATH.read_text(encoding="utf-8"))
        except (ValueError, OSError):
            prov = {}
    else:
        prov = {}
    prov["sha256_current"] = hashlib.sha256(blob).hexdigest()
    prov.setdefault("source_type", "Local FLEX CSV (origin needs verification)")
    prov.setdefault("source_page", PSI_URL)
    prov.setdefault("doi", DOI)
    return blob, df, prov


def _numeric_columns(df: pd.DataFrame):
    # Never treat numeric identifiers or date codes as physical observations.
    excluded = ("test #", "identifier", "test date", "test gmt", "test end", "timestamp", "file", "number")
    result = {}
    for name in df.columns:
        lower = name.casefold()
        if any(word in lower for word in excluded):
            continue
        series = pd.to_numeric(df[name].astype(str).str.strip().str.replace(",", ".", regex=False), errors="coerce")
        if series.notna().sum() >= max(4, int(.15 * len(df))):
            result[name] = series
    return result


def _select_col(df, fragment):
    return next((col for col in df if fragment.casefold() in col.casefold()), None)


def render_expanded_experiments(language="Español"):
    en = _lang(language)
    tr = lambda es, eng: eng if en else es
    st.title(tr("🧬 Biblioteca experimental ampliada", "🧬 Expanded experimental library"))
    st.caption(tr("WARI FIRE AI · BASS-II + FLEX · NASA Physical Sciences Informatics", "WARI FIRE AI · BASS-II + FLEX · NASA Physical Sciences Informatics"))
    st.info(tr(
        "La tabla de BASS-II no se modifica. FLEX utiliza gotas de combustible líquido y tiene otras variables; no se mezclan mediciones entre estudios.",
        "The BASS-II table is unchanged. FLEX studies liquid-fuel droplets with different variables; measurements are never pooled across studies."
    ))

    bass_n = 0
    if BASS_PATH.exists():
        try:
            bass_n = len(pd.read_csv(BASS_PATH, encoding="utf-8-sig", dtype=str))
        except (OSError, pd.errors.ParserError):
            pass

    blob = df = provenance = None
    try:
        blob, df, provenance = _load_local()
    except (OSError, ValueError) as exc:
        st.error(tr(f"El CSV FLEX local no pasó la validación: {exc}", f"Local FLEX CSV validation failed: {exc}"))

    if df is None and st.session_state.get("wari_flex_blob"):
        try:
            blob = st.session_state["wari_flex_blob"]
            df = _read_csv(blob)
            provenance = st.session_state["wari_flex_prov"]
        except (ValueError, KeyError) as exc:
            st.error(str(exc))

    if df is None:
        st.warning(tr(
            "Todavía no se ha descargado FLEX. Pulsa el botón para recuperar su tabla: primero intentará NASA PSI y, si no responde, una copia pública identificada como espejo.",
            "FLEX has not been fetched yet. Click to retrieve the table from NASA PSI, with a disclosed public mirror as fallback."
        ))
        if st.button(tr("🔄 Obtener registros FLEX", "🔄 Retrieve FLEX records"), type="primary"):
            try:
                with st.spinner(tr("Consultando fuente experimental...", "Retrieving experimental source...")):
                    blob, provenance = fetch_flex()
                    df = _read_csv(blob)
                    st.session_state["wari_flex_blob"] = blob
                    st.session_state["wari_flex_prov"] = provenance
                st.rerun()
            except (requests.RequestException, RuntimeError, ValueError) as exc:
                st.error(tr(f"No se pudo recuperar FLEX: {exc}", f"FLEX could not be retrieved: {exc}"))
                st.link_button(tr("Abrir NASA PSI-69", "Open NASA PSI-69"), PSI_URL)

    n_flex = len(df) if df is not None else 0
    a, b, c = st.columns(3)
    a.metric("BASS-II", bass_n)
    b.metric("FLEX", n_flex)
    c.metric(tr("Filas disponibles", "Available source rows"), bass_n + n_flex)
    if df is None:
        st.caption(tr("Objetivo potencial: 129 + 274 = 403 filas, pendiente de descarga y validación.", "Potential target: 129 + 274 = 403 rows, pending download and validation."))
        st.link_button("NASA PSI-69 (FLEX)", PSI_URL)
        return

    st.success(tr(f"FLEX cargado: {len(df)} filas y {len(df.columns)} columnas originales.", f"FLEX loaded: {len(df)} rows and {len(df.columns)} original columns."))
    if len(df) != 274:
        st.warning(tr("El número de filas difiere de la tabla FLEX de referencia (274); revisar la versión.", "Row count differs from the reference FLEX table (274); review the version."))
    if "mirror" in provenance.get("source_type", "").lower():
        st.warning(tr(
            "Procedencia: copia pública de GitHub. Aunque se identifica como tabla NASA PSI-69, todavía no se ha comparado su huella digital con el archivo oficial.",
            "Provenance: public GitHub mirror. The table is identified as NASA PSI-69, but its hash has not been compared against NASA's official file."
        ))

    tab1, tab2, tab3 = st.tabs([
        tr("🔎 Explorar FLEX", "🔎 Explore FLEX"),
        tr("📊 Visualizar mediciones", "📊 Plot measurements"),
        tr("🔗 Procedencia y exportar", "🔗 Provenance and export")
    ])
    with tab1:
        fuel_name = _select_col(df.columns, "fuel")
        subset = df.copy()
        if fuel_name:
            fuels = sorted(x for x in subset[fuel_name].dropna().unique() if str(x).strip())
            fuel_selection = st.multiselect(tr("Combustible", "Fuel"), fuels, default=fuels)
            subset = subset[subset[fuel_name].isin(fuel_selection)]
        q = st.text_input(tr("Buscar texto o identificador", "Search text or test identifier"), key="flex_search")
        if q.strip():
            mask = subset.astype(str).apply(lambda s: s.str.contains(q, case=False, regex=False, na=False)).any(axis=1)
            subset = subset[mask]
        st.metric(tr("Filas filtradas", "Filtered rows"), len(subset))
        st.dataframe(subset, use_container_width=True, hide_index=True)
        st.caption(tr("Se preservan las columnas y las unidades originales de FLEX.", "Original FLEX columns and their units are preserved."))
    with tab2:
        numeric = _numeric_columns(df)
        if not numeric:
            st.warning(tr("No se encontraron suficientes valores numéricos utilizables.", "No suitable numeric columns were found."))
        else:
            preferred = next((k for k in numeric if "burn time" in k.lower()), next(iter(numeric)))
            key = st.selectbox(tr("Variable experimental y unidad original", "Experimental variable and source unit"), list(numeric), index=list(numeric).index(preferred))
            test_col = _select_col(df.columns, "test #") or df.columns[0]
            view = df[[test_col]].copy()
            view["_y"] = numeric[key]
            view = view.dropna(subset=["_y"]).head(45)
            if view.empty:
                st.warning(tr("No existen valores numéricos para graficar.", "No numeric values available for plotting."))
            else:
                fig = go.Figure(go.Bar(x=view[test_col].astype(str), y=view["_y"], marker_color="#46d9ff"))
                fig.update_layout(template="plotly_dark", paper_bgcolor="#102038", plot_bgcolor="#102038", height=430, xaxis_title=test_col, yaxis_title=key)
                st.plotly_chart(fig, use_container_width=True)
                st.caption(tr("Gráfico descriptivo de las primeras 45 filas con valor numérico, sin inferencia causal.", "Descriptive plot of the first 45 numeric rows; no causal inference."))
    with tab3:
        st.json(provenance)
        st.link_button(tr("Fuente oficial NASA PSI-69", "Official NASA PSI-69 source"), PSI_URL)
        st.link_button(tr("Copia pública consultada", "Public mirrored source"), MIRROR_URL)
        st.download_button(tr("⬇️ Descargar FLEX CSV íntegro", "⬇️ Download full FLEX CSV"), data=blob, file_name="flex_experimental.csv", mime="text/csv", use_container_width=True)
        st.download_button(tr("⬇️ Descargar procedencia JSON", "⬇️ Download provenance JSON"), data=json.dumps(provenance, ensure_ascii=False, indent=2).encode("utf-8"), file_name="flex_provenance.json", mime="application/json", use_container_width=True)
        st.info(tr(
            "Para dejar los nuevos registros guardados en GitHub, sube estos dos archivos en la carpeta data/. Si no lo haces, FLEX se recuperará nuevamente desde internet cuando sea necesario.",
            "To keep these records in GitHub, upload both downloaded files into data/. Otherwise FLEX will be fetched again when needed."
        ))
    st.caption(tr(
        "Interpretación: 403 sería el total de filas de dos tablas experimentales, no 403 pruebas equivalentes ni 403 mediciones de peligro.",
        "Interpretation: 403 would be the total rows across two experimental tables, not 403 equivalent trials or 403 fire-hazard measurements."
    ))
