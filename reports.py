"""WARI FIRE AI — Scientific PDF report maker (Phase 12).

Uses only the original BASS-II CSV and the parsed, non-imputed measurements.
This is an educational/research summary, NOT a safety certification.
"""
from io import BytesIO
from datetime import datetime, timezone
from pathlib import Path
from xml.sax.saxutils import escape as xml_escape

import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer, KeepTogether, PageBreak
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.graphics.shapes import Drawing, Rect, String

NASA_LINK="https://psi.nasa.gov/physci/repo/data/investigations/PSI-25"
SRC_FILE="PSI-25_Experimental table_BASS-II.csv"
VARIABLES={"O2":("O₂","% vol."),"CO2":("CO₂","% vol."),"CO":("CO","ppm")}
DARK=colors.HexColor("#121E30")
CYAN=colors.HexColor("#087FAB")
GREY=colors.HexColor("#5A6979")
LIGHT=colors.HexColor("#EAF2F8")

TEXT={
 "Español":{
 "title":"Informe científico BASS-II", "caption":"Selecciona hasta seis ensayos reales, revisa sus mediciones y descarga un informe trazable.",
 "intro":"Este módulo describe únicamente mediciones disponibles en NASA PSI. No predice incendios ni determina seguridad de materiales.",
 "tests":"Ensayos a incluir", "variables":"Gases que deseas analizar", "author":"Nombre del autor del informe (opcional)",
 "preview":"Vista previa de las mediciones", "missing":"Dato no disponible", "initial":"Inicial", "final":"Final",
 "delta":"Diferencia (final - inicial)","download_pdf":"Descargar informe científico PDF", "download_csv":"Descargar tabla de datos CSV",
 "report":"INFORME DE DATOS EXPERIMENTALES", "subtitle":"WARI FIRE AI | NASA PSI | BASS-II",
 "selection":"Selección y procedencia", "notes":"Alcances y limitaciones", "source":"Fuente y trazabilidad",
 "samples":"Ensayos seleccionados", "date":"Fecha de generación", "authorlabel":"Elaborado por", "variable":"Variable",
 "unavailable":"No se identificaron pares de columnas para los gases seleccionados.",
 "insuff":"No hay datos suficientes para generar el informe. Verifica el CSV y los ensayos seleccionados.",
 "notverified":"Celdas vacías o ambiguas se muestran como no disponibles, sin imputaciones.",
 "interpret":"Las diferencias son cálculos descriptivos (final - inicial); no demuestran causalidad ni riesgo de incendio.",
 "caution":"Las condiciones y resultados de microgravedad no se pueden extrapolar directamente a hábitats lunares o marcianos.",
 "fan":"Las columnas Fan display y Air display son lecturas del equipo, no velocidades físicas calibradas.",
 "overview":"Resumen de la selección", "raw":"Tabla de mediciones", "chart":"Comparación visual (solo valores disponibles)",
 "source_note":"Documento asociado: registro NASA PSI-25. El archivo CSV original es la fuente de las mediciones.",
 "warning":"No usar para seleccionar materiales, certificar sistemas ni establecer límites de seguridad.",
 "none":"Ninguno", "measurements":"Mediciones", "all":"Registros disponibles", "optional":"Opcional", "disclaimer":"Informe descriptivo; no es una evaluación de seguridad.",
 "label":"Ensayo", "material":"Material registrado", "pi":"Investigador (PI)", "created":"Generado automáticamente por WARI FIRE AI",
 "num":"Valores numéricos disponibles", "out":"Observación", "caution_cell":"Faltan mediciones para una comparación completa",
 "complete":"Par inicial/final disponible", "notcomplete":"Par incompleto", "scientific":"Precauciones científicas",
 "source_line":"URL del registro", "filename":"Archivo de origen", "legend":"Barras azules: inicial; barras naranjas: final", "empty":"No hay datos para graficar",
 },
 "English":{
 "title":"BASS-II scientific report", "caption":"Select up to six real tests, inspect measurements, and download a traceable report.",
 "intro":"This module describes NASA PSI measurements only. It does not predict fires or determine material safety.",
 "tests":"Tests to include", "variables":"Gases to analyze", "author":"Report author (optional)",
 "preview":"Measurement preview", "missing":"Not available", "initial":"Initial", "final":"Final",
 "delta":"Difference (final - initial)","download_pdf":"Download scientific PDF report", "download_csv":"Download data table CSV",
 "report":"EXPERIMENTAL DATA REPORT", "subtitle":"WARI FIRE AI | NASA PSI | BASS-II",
 "selection":"Selection and provenance", "notes":"Scope and limitations", "source":"Source and traceability",
 "samples":"Selected tests", "date":"Generated on", "authorlabel":"Prepared by", "variable":"Variable",
 "unavailable":"No initial/final gas columns were detected.",
 "insuff":"Insufficient data to generate the report. Check the CSV and selection.",
 "notverified":"Missing or ambiguous values are shown as unavailable without imputation.",
 "interpret":"Differences are descriptive calculations (final - initial); they do not demonstrate causality or fire risk.",
 "caution":"Microgravity findings cannot be directly extrapolated to lunar or Martian habitats.",
 "fan":"Fan display and Air display are instrument readouts, not calibrated physical velocities.",
 "overview":"Selection summary", "raw":"Measurement table", "chart":"Visual comparison (available values only)",
 "source_note":"Related document: NASA PSI-25 record. The original CSV supplies the measurements.",
 "warning":"Do not use for material selection, system certification, or establishing safety thresholds.",
 "none":"None", "measurements":"Measurements", "all":"Available records", "optional":"Optional", "disclaimer":"Descriptive report, not a safety assessment.",
 "label":"Test", "material":"Recorded material", "pi":"Principal investigator (PI)", "created":"Automatically generated by WARI FIRE AI",
 "num":"Available numeric values", "out":"Observation", "caution_cell":"Measurements missing for full comparison",
 "complete":"Initial/final pair available", "notcomplete":"Incomplete pair", "scientific":"Scientific cautions",
 "source_line":"Source record URL", "filename":"Source file", "legend":"Blue bars: initial; orange bars: final", "empty":"No data to plot",
 },
}


def _font():
    normal="Helvetica"; bold="Helvetica-Bold"
    search=[
      ("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf","/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"),
      ("/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf","/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf"),
    ]
    for reg,b in search:
        if Path(reg).exists() and Path(b).exists():
            if "WariRegular" not in pdfmetrics.getRegisteredFontNames():
                pdfmetrics.registerFont(TTFont("WariRegular",reg))
                pdfmetrics.registerFont(TTFont("WariBold",b))
            return "WariRegular","WariBold"
    return normal,bold


def _fmt(v):
    if v is None or pd.isna(v):return "—"
    try:return f"{float(v):.3f}".rstrip("0").rstrip(".")
    except (TypeError,ValueError):return str(v)


def _clean(v):
    if v is None or pd.isna(v):return "—"
    return str(v).replace("\n"," ").strip() or "—"


def _records(bass,cols,selected,variables,t):
    chosen=bass[bass['_test_key'].isin(selected)].copy()
    ordered={v:i for i,v in enumerate(selected)}
    chosen['_order']=chosen['_test_key'].map(ordered)
    chosen=chosen.sort_values('_order')
    rows=[]
    for _,r in chosen.iterrows():
      for gas in variables:
        a=r.get(gas+'_i_num',float('nan'))
        b=r.get(gas+'_f_num',float('nan'))
        if pd.notna(a) and pd.notna(b):
            delta=b-a; status=t['complete']
        else:
            delta=float('nan');status=t['notcomplete']
        rows.append({
            t['label']:str(r['_test_key']),
            t['material']:_clean(r[cols['material']]) if cols.get('material') else '—',
            t['pi']:_clean(r[cols['pi']]) if cols.get('pi') else '—',
            t['variable']:gas+' ('+VARIABLES[gas][1]+')',
            t['initial']:float(a) if pd.notna(a) else float('nan'),
            t['final']:float(b) if pd.notna(b) else float('nan'),
            t['delta']:float(delta) if pd.notna(delta) else float('nan'),
            t['out']:status,
        })
    return pd.DataFrame(rows)


def _styles(normal,bold):
    ss=getSampleStyleSheet()
    ss.add(ParagraphStyle(name='WTitle',fontName=bold,fontSize=16,leading=20,textColor=DARK,spaceAfter=8))
    ss.add(ParagraphStyle(name='WHead',fontName=bold,fontSize=11,leading=15,textColor=DARK,spaceBefore=12,spaceAfter=7))
    ss.add(ParagraphStyle(name='WBody',fontName=normal,fontSize=8.5,leading=13,textColor=DARK,spaceAfter=5))
    ss.add(ParagraphStyle(name='WSmall',fontName=normal,fontSize=7.1,leading=10,textColor=GREY,spaceAfter=5))
    ss.add(ParagraphStyle(name='WCell',fontName=normal,fontSize=7,leading=9,textColor=DARK))
    ss.add(ParagraphStyle(name='WCellBold',fontName=bold,fontSize=7,leading=9,textColor=colors.white))
    return ss


def _report_table(data,headers,widths,ss):
    P=lambda x,style:Paragraph(xml_escape(str(x)),ss[style])
    matrix=[[P(x,'WCellBold') for x in headers]]+[[P(x,'WCell') for x in row] for row in data]
    table=Table(matrix,colWidths=widths,repeatRows=1,hAlign='LEFT')
    table.setStyle(TableStyle([
      ('BACKGROUND',(0,0),(-1,0),DARK),('VALIGN',(0,0),(-1,-1),'TOP'),
      ('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.white,LIGHT]),
      ('BOTTOMPADDING',(0,0),(-1,-1),8),('TOPPADDING',(0,0),(-1,-1),8),
      ('LEFTPADDING',(0,0),(-1,-1),6),('RIGHTPADDING',(0,0),(-1,-1),6),
      ('LINEBELOW',(0,-1),(-1,-1),0.3,colors.HexColor('#CBD5E1')),
    ]))
    return table


def _chart_for_gas(df,gas,t):
    sub=df[df[t['variable']].str.startswith(gas+' (')].copy()
    labels=sub[t['label']].astype(str).tolist()
    if not labels:return None
    # horizontal mini-bars in discrete rows; each gas gets its own chart, never mix CO ppm with percentages
    width=450;h=25*len(labels)+36
    dr=Drawing(width,h)
    values=list(sub[t['initial']].dropna())+list(sub[t['final']].dropna())
    positive=[float(v) for v in values if pd.notna(v) and float(v)>=0]
    if not positive:return None
    maximum=max(positive) or 1
    bar_space=265
    for i,(_,r) in enumerate(sub.iterrows()):
      y=h-25*(i+1)
      dr.add(String(0,y+7,str(r[t['label']])[:17],fontName='Helvetica',fontSize=8,fillColor=DARK))
      for j,(key,color) in enumerate(((t['initial'],CYAN),(t['final'],colors.HexColor('#EC8B49')))):
        val=r[key]
        if pd.isna(val) or val<0:continue
        bw=max(0.2,float(val)/maximum*bar_space)
        dr.add(Rect(77,y+9-j*8,bw,6,fillColor=color,strokeColor=None))
        dr.add(String(min(77+bw+4,405),y+9-j*8,_fmt(val),fontSize=7,fillColor=DARK))
    dr.add(String(0,5,t['legend'],fontSize=7,fillColor=GREY))
    return dr


def _footer(canvas,doc,normal):
    canvas.saveState();canvas.setStrokeColor(colors.HexColor('#CCD7E2'))
    canvas.line(1.6*cm,1.4*cm,A4[0]-1.6*cm,1.4*cm)
    canvas.setFont(normal,7)
    canvas.setFillColor(GREY)
    canvas.drawString(1.6*cm,1.05*cm,'WARI FIRE AI | NASA PSI | BASS-II')
    canvas.drawRightString(A4[0]-1.6*cm,1.05*cm,str(doc.page))
    canvas.restoreState()


def create_pdf(df,variables,language,author):
    t=TEXT[language];normal,bold=_font();ss=_styles(normal,bold)
    buf=BytesIO()
    doc=SimpleDocTemplate(buf,pagesize=A4,rightMargin=1.6*cm,leftMargin=1.6*cm,
         topMargin=1.6*cm,bottomMargin=1.8*cm,title='WARI FIRE AI - BASS-II',author='Wari Teams')
    story=[]
    story.append(Paragraph(t['report'],ss['WTitle']))
    story.append(Paragraph(t['subtitle'],ss['WBody']))
    story.append(Paragraph(xml_escape(t['created']+' • '+datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')),ss['WSmall']))
    if author.strip():story.append(Paragraph(xml_escape(t['authorlabel']+': '+author[:90]),ss['WBody']))
    story.append(Paragraph(t['selection'],ss['WHead']))
    tests=list(dict.fromkeys(df[t['label']].tolist()))
    story.append(Paragraph(xml_escape(t['samples']+': '+', '.join(tests)),ss['WBody']))
    story.append(Paragraph(xml_escape(t['measurements']+': '+', '.join(variables)),ss['WBody']))
    story.append(Paragraph(t['raw'],ss['WHead']))
    data=[]
    for _,row in df.iterrows():
        data.append([str(row[t['label']]),str(row[t['variable']]),_fmt(row[t['initial']]),_fmt(row[t['final']]),_fmt(row[t['delta']]),str(row[t['out']])])
    story.append(_report_table(data,[t['label'],t['variable'],t['initial'],t['final'],'Δ',t['out']],
       [2.2*cm,3.4*cm,2.1*cm,2.1*cm,2.0*cm,5.0*cm],ss))
    story.append(Spacer(1,.3*cm))
    story.append(Paragraph(t['chart'],ss['WHead']))
    for gas in variables:
        chart=_chart_for_gas(df,gas,t)
        if chart:
            story.append(KeepTogether([Paragraph(gas+' ('+VARIABLES[gas][1]+')',ss['WBody']),chart,Spacer(1,.2*cm)]))
    story.append(Paragraph(t['scientific'],ss['WHead']))
    for msg in [t['notverified'],t['interpret'],t['fan'],t['caution'],t['warning']]:
        story.append(Paragraph('• '+xml_escape(msg),ss['WBody']))
    story.append(Paragraph(t['source'],ss['WHead']))
    story.append(Paragraph(xml_escape(t['source_note']),ss['WBody']))
    story.append(Paragraph(xml_escape(t['filename']+': '+SRC_FILE),ss['WBody']))
    story.append(Paragraph(xml_escape(t['source_line']+': '+NASA_LINK),ss['WSmall']))
    doc.build(story,onFirstPage=lambda c,d:_footer(c,d,normal),onLaterPages=lambda c,d:_footer(c,d,normal))
    return buf.getvalue()


def render_reports(bass,cols,language):
    t=TEXT[language]
    st.title('📄 '+t['title'])
    st.caption(t['caption'])
    st.info(t['intro'])
    if bass is None or bass.empty:
        st.error(t['insuff']);return
    var_opts=[g for g in VARIABLES if cols.get(g+'_i') and cols.get(g+'_f')]
    if not var_opts:
        st.error(t['unavailable']);return
    ids=bass['_test_key'].astype(str).tolist()
    c1,c2=st.columns([1.7,1.3])
    with c1:
        selected=st.multiselect(t['tests'],ids,default=ids[:min(2,len(ids))],max_selections=6,key='report_selected')
    with c2:
        variables=st.multiselect(t['variables'],var_opts,default=var_opts,key='report_variables')
    author=st.text_input(t['author'],max_chars=90)
    if not selected or not variables:
        st.warning(t['insuff']);return
    df=_records(bass,cols,selected,variables,t)
    if df.empty:
        st.warning(t['insuff']);return
    c1,c2,c3=st.columns(3)
    c1.metric(t['samples'],len(set(df[t['label']])))
    c2.metric(t['measurements'],len(df))
    c3.metric(t['num'],sum(pd.notna(df[t['initial']]) & pd.notna(df[t['final']])))
    st.subheader(t['preview'])
    st.dataframe(df,use_container_width=True,hide_index=True)
    gas=st.selectbox(t['variable'],variables,key='report_gas')
    visible=df[df[t['variable']].str.startswith(gas+' (')].copy()
    if not visible.empty:
        fig=go.Figure()
        fig.add_bar(x=visible[t['label']],y=visible[t['initial']],name=t['initial'],marker_color='#46D9FF')
        fig.add_bar(x=visible[t['label']],y=visible[t['final']],name=t['final'],marker_color='#FF9D62')
        fig.update_layout(template='plotly_dark',barmode='group',height=330,
                          xaxis_title=t['label'],yaxis_title=VARIABLES[gas][1],
                          paper_bgcolor='#101A2A',plot_bgcolor='#101A2A')
        st.plotly_chart(fig,use_container_width=True)
    st.warning(t['interpret']+' '+t['notverified'])
    st.caption(t['source_note']+' '+NASA_LINK)
    pdf_bytes=create_pdf(df,variables,language,author)
    left,right=st.columns(2)
    left.download_button('📄 '+t['download_pdf'],data=pdf_bytes,
       file_name='WARI_FIRE_AI_BASSII_Report.pdf',mime='application/pdf',use_container_width=True)
    right.download_button('📊 '+t['download_csv'],
       data=df.to_csv(index=False).encode('utf-8-sig'),file_name='WARI_FIRE_AI_BASSII_Selection.csv',
       mime='text/csv',use_container_width=True)
