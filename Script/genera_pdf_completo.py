#!/usr/bin/env python3
"""
GENERATORE REPORT PDF COMPLETO FIGB 2017-2025
Con grafici integrati e analisi dettagliate
"""

import pandas as pd
import json
from pathlib import Path
from datetime import datetime
from weasyprint import HTML, CSS
import base64
import os
import google.generativeai as genai
from dotenv import load_dotenv

# Carica API key
load_dotenv()
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))

# Directory
BASE_DIR = Path(__file__).parent.parent
OUTPUT_DIR = BASE_DIR / 'output'
CHARTS_DIR = OUTPUT_DIR / 'charts_v2'
RESULTS_DIR = OUTPUT_DIR / 'results_v2'

print("=" * 100)
print("GENERAZIONE REPORT PDF COMPLETO FIGB 2017-2025")
print("=" * 100)

# ============================================================================
# CARICAMENTO DATI E METRICHE
# ============================================================================
print("\n[1/5] Caricamento dati e metriche...")

# Carica metriche JSON
with open(RESULTS_DIR / 'metriche_complete_v2.json', 'r', encoding='utf-8') as f:
    metriche = json.load(f)

# Carica tutti i CSV
cat_dist = pd.read_csv(RESULTS_DIR / 'distribuzione_categorie.csv')
progressione = pd.read_csv(RESULTS_DIR / 'progressione_categorie.csv')
matrice = pd.read_csv(RESULTS_DIR / 'matrice_transizione.csv')
regioni = pd.read_csv(RESULTS_DIR / 'regioni_summary.csv')
retention_reg = pd.read_csv(RESULTS_DIR / 'retention_regionale.csv')
circoli_v = pd.read_csv(RESULTS_DIR / 'circoli_virtuosi.csv')
circoli_c = pd.read_csv(RESULTS_DIR / 'circoli_critici.csv')
circoli_conv = pd.read_csv(RESULTS_DIR / 'circoli_conversione_sb.csv')
profili = pd.read_csv(RESULTS_DIR / 'profili_giocatori.csv')
sb_analisi = pd.read_csv(RESULTS_DIR / 'scuola_bridge_analisi.csv')
churn = pd.read_csv(RESULTS_DIR / 'churn_segmentato.csv')
churn_summary = pd.read_csv(RESULTS_DIR / 'churn_summary.csv')
ltv = pd.read_csv(RESULTS_DIR / 'lifetime_value.csv')
selettivi = pd.read_csv(RESULTS_DIR / 'selettivi_per_categoria.csv')

print(f"   Caricati {len([f for f in RESULTS_DIR.glob('*.csv')])} file CSV")

# ============================================================================
# FUNZIONE PER EMBEDDING IMMAGINI
# ============================================================================
def embed_image(img_path):
    """Converte immagine in base64 per embedding HTML"""
    with open(img_path, 'rb') as f:
        data = base64.b64encode(f.read()).decode('utf-8')
    return f"data:image/png;base64,{data}"

# ============================================================================
# GENERAZIONE TESTO CON GEMINI
# ============================================================================
print("\n[2/5] Generazione analisi con Gemini AI...")

model = genai.GenerativeModel('gemini-2.0-flash')

# Prepara contesto dati per Gemini
contesto_dati = f"""
DATI TESSERAMENTO FIGB 2017-2025:

METRICHE GENERALI:
- Tesserati 2025: {metriche['anno_2025']['tesserati']:,}
- Circoli attivi: {metriche['anno_2025']['circoli_attivi']}
- Eta media: {metriche['anno_2025']['eta_media']} anni
- Under 40: {metriche['anno_2025']['under_40_pct']}%
- Over 70: {metriche['anno_2025']['over_70_pct']}%
- Maschi: {metriche['anno_2025']['maschi_pct']}%

CATEGORIE:
- NC (non classificati): {metriche['categorie']['nc_pct']}%
- Terza categoria: {metriche['categorie']['terza_pct']}%
- Master: {metriche['categorie']['master_pct']}%
- Media giocatori saliti di categoria: {metriche['categorie']['progressione_media_saliti']}%
- Media giocatori stabili: {metriche['categorie']['progressione_media_stabili']}%

RETENTION:
- Media globale: {metriche['retention']['media_globale']}%
- Migliore regione: {metriche['retention']['migliore_regione']}
- Peggiore regione: {metriche['retention']['peggiore_regione']}

SCUOLA BRIDGE:
- Tasso successo medio: {metriche['scuola_bridge']['tasso_successo_medio']}%
- Tasso conversione medio: {metriche['scuola_bridge']['tasso_conversione_medio']}%
- Tasso churn medio: {metriche['scuola_bridge']['tasso_churn_medio']}%
- Correlazione gare-retention: {metriche['scuola_bridge']['correlazione_gare_retention']}

CHURN:
- Churn totale: {metriche['churn']['totale']:,}
- Stima decessi: {metriche['churn']['stima_decessi']:,}
- Stima infermi: {metriche['churn']['stima_infermi']:,}
- Churn recuperabile: {metriche['churn']['recuperabile']:,}
- % recuperabile: {metriche['churn']['pct_recuperabile']}%

LTV:
- Valore totale: €{metriche['ltv']['totale_milioni']}M
- LTV medio per tesserato: €{metriche['ltv']['ltv_medio']}
- Segmento piu prezioso: fascia {metriche['ltv']['segmento_oro']}

REGIONI TOP 5:
{regioni.nlargest(5, 'Tesserati2025')[['Regione', 'Tesserati2025', 'RetentionMedia']].to_string(index=False)}

CIRCOLI VIRTUOSI (top 5):
{circoli_v.head(5).to_string(index=False)}

CIRCOLI CRITICI (top 5):
{circoli_c.head(5).to_string(index=False)}

ANALISI SCUOLA BRIDGE:
{sb_analisi.to_string(index=False)}

LIFETIME VALUE PER FASCIA ETA:
{ltv.to_string(index=False)}
"""

# Genera sezioni del report
sezioni = {}

# 1. Sommario Esecutivo
prompt_sommario = f"""
Sei un analista sportivo esperto. Scrivi un SOMMARIO ESECUTIVO (max 400 parole) per il report FIGB 2017-2025.

DATI:
{contesto_dati}

Il sommario deve:
- Evidenziare i numeri chiave (tesserati 2025, trend, retention)
- Sottolineare le criticita (eta media elevata, bassa percentuale under 40)
- Indicare i punti di forza (recovery post-COVID, Scuola Bridge efficace)
- Anticipare le raccomandazioni strategiche

Scrivi in italiano formale, stile relazione aziendale. NO markdown, testo puro.
"""

sezioni['sommario'] = model.generate_content(prompt_sommario).text
print("   - Sommario esecutivo generato")

# 2. Analisi Temporale
prompt_temporale = f"""
Scrivi l'ANALISI TEMPORALE (max 350 parole) del tesseramento FIGB 2017-2025.

DATI:
- 2017: ~17,500 tesserati
- 2018: ~19,800 (picco pre-COVID)
- 2019: ~19,500
- 2020: ~15,500 (impatto COVID)
- 2021: ~11,600 (minimo storico)
- 2022: ~12,600 (inizio recovery)
- 2023: ~13,100
- 2024: ~13,450
- 2025: 13,662

Analizza:
- Trend pre-COVID (crescita)
- Impatto pandemia (crollo)
- Recovery post-COVID (graduale ripresa)
- Proiezioni future

Scrivi in italiano formale. NO markdown.
"""

sezioni['temporale'] = model.generate_content(prompt_temporale).text
print("   - Analisi temporale generata")

# 3. Analisi Categorie
prompt_categorie = f"""
Scrivi l'ANALISI DELLA PIRAMIDE CATEGORIE (max 400 parole) FIGB.

STRUTTURA CATEGORIE (dal basso):
- NC (Non Classificati): {metriche['categorie']['nc_pct']}%
- Quarta categoria (4F, 4Q, 4C, 4P): dopo NC
- Terza categoria (3F, 3Q, 3C, 3P): {metriche['categorie']['terza_pct']}%
- Seconda categoria (2F, 2Q, 2C, 2P)
- Prima categoria (1F, 1Q, 1C, 1P)
- Honor (HJ, HQ, HK, HA): fante, dama, re, asso
- Master (MS, LM, GM): Master Series, Life Master, Grand Master {metriche['categorie']['master_pct']}%

PROGRESSIONE:
- Media saliti di livello: {metriche['categorie']['progressione_media_saliti']}%
- Media stabili: {metriche['categorie']['progressione_media_stabili']}%

PROBLEMA CRITICO: La piramide e "bloccata" - pochi salgono di categoria.
Analizza le cause e proponi soluzioni.

Scrivi in italiano formale. NO markdown.
"""

sezioni['categorie'] = model.generate_content(prompt_categorie).text
print("   - Analisi categorie generata")

# 4. Analisi Scuola Bridge
prompt_sb = f"""
Scrivi l'ANALISI SCUOLA BRIDGE (max 400 parole).

DATI SCUOLA BRIDGE:
- Tasso successo medio: {metriche['scuola_bridge']['tasso_successo_medio']}%
- Tasso conversione (passa altra tessera): {metriche['scuola_bridge']['tasso_conversione_medio']}%
- Tasso churn: {metriche['scuola_bridge']['tasso_churn_medio']}%
- Correlazione gare giocate-retention: {metriche['scuola_bridge']['correlazione_gare_retention']}

LOGICA CORRETTA:
- Rimanere in Scuola Bridge = POSITIVO (corso triennale)
- Passare ad altra tessera = POSITIVO (completamento)
- Non ritesserarsi = NEGATIVO (churn reale)

FATTORI DI SUCCESSO:
- Gare giocate (correlazione alta)
- Circolo di appartenenza
- Eta del giocatore

Analizza cosa MANTIENE gli allievi e cosa li FA ANDARE VIA.
Proponi best practices.

Scrivi in italiano formale. NO markdown.
"""

sezioni['scuola_bridge'] = model.generate_content(prompt_sb).text
print("   - Analisi Scuola Bridge generata")

# 5. Analisi Circoli
prompt_circoli = f"""
Scrivi l'ANALISI DEI CIRCOLI (max 400 parole).

CIRCOLI VIRTUOSI (alta retention e conversione):
{circoli_v.head(10).to_string(index=False)}

CIRCOLI CRITICI (bassa retention):
{circoli_c.head(10).to_string(index=False)}

CONVERSIONE SCUOLA BRIDGE PER CIRCOLO:
{circoli_conv.nlargest(5, 'ConversionePct')[['GrpName', 'TotSB', 'Convertiti', 'ConversionePct']].to_string(index=False)}

Analizza:
- Cosa fanno diversamente i circoli virtuosi
- Perche alcuni circoli perdono tesserati
- Best practices da replicare
- Azioni correttive per circoli critici

Scrivi in italiano formale. NO markdown.
"""

sezioni['circoli'] = model.generate_content(prompt_circoli).text
print("   - Analisi circoli generata")

# 6. Analisi Regionale
prompt_regioni = f"""
Scrivi l'ANALISI REGIONALE (max 400 parole).

DATI REGIONALI:
{regioni[['Regione', 'Tesserati2025', 'Trend', 'RetentionMedia', 'EtaMedia']].to_string(index=False)}

TOP REGIONI:
1. Lombardia: leader per numeri assoluti
2. Lazio: forte presenza Roma
3. Emilia-Romagna: alta retention

DISPARITA TERRITORIALI:
- Nord vs Sud
- Grandi citta vs province
- Regioni in crescita vs declino

Analizza le differenze e proponi strategie per ridurre il gap.

Scrivi in italiano formale. NO markdown.
"""

sezioni['regioni'] = model.generate_content(prompt_regioni).text
print("   - Analisi regionale generata")

# 7. Analisi Churn
prompt_churn = f"""
Scrivi l'ANALISI DEL CHURN (max 350 parole).

DATI CHURN:
- Churn totale: {metriche['churn']['totale']:,}
- Stima decessi (over 85): {metriche['churn']['stima_decessi']:,}
- Stima infermi (80-85 non ritesserati): {metriche['churn']['stima_infermi']:,}
- Churn recuperabile: {metriche['churn']['recuperabile']:,} ({metriche['churn']['pct_recuperabile']}%)

SEGMENTAZIONE:
{churn_summary.to_string(index=False)}

INSIGHT CHIAVE:
- Circa meta del churn e "strutturale" (eta avanzata)
- L'altra meta e RECUPERABILE con azioni mirate

Proponi strategie per ridurre il churn recuperabile.

Scrivi in italiano formale. NO markdown.
"""

sezioni['churn'] = model.generate_content(prompt_churn).text
print("   - Analisi churn generata")

# 8. Lifetime Value
prompt_ltv = f"""
Scrivi l'ANALISI DEL LIFETIME VALUE (max 300 parole).

DATI LTV:
{ltv.to_string(index=False)}

TOTALI:
- Valore totale base tesserati: €{metriche['ltv']['totale_milioni']}M
- LTV medio per tesserato: €{metriche['ltv']['ltv_medio']}
- Segmento piu prezioso: 60-70 anni (alta partecipazione, anni residui)

Analizza:
- Quale fascia di eta genera piu valore
- Dove investire per massimizzare il ROI
- Paradosso eta (giovani = alto LTV potenziale, anziani = alto LTV attuale)

Scrivi in italiano formale. NO markdown.
"""

sezioni['ltv'] = model.generate_content(prompt_ltv).text
print("   - Analisi LTV generata")

# 9. Raccomandazioni
prompt_raccomandazioni = f"""
Scrivi le RACCOMANDAZIONI STRATEGICHE (max 500 parole).

Basandoti su tutti i dati:
{contesto_dati}

Proponi 8-10 raccomandazioni CONCRETE con:
1. Priorita (Alta/Media/Bassa)
2. Azione specifica
3. KPI di monitoraggio
4. Impatto atteso

AREE CHIAVE:
- Reclutamento giovani (under 40 solo {metriche['anno_2025']['under_40_pct']}%)
- Retention (attuale {metriche['retention']['media_globale']}%)
- Progressione categorie (solo {metriche['categorie']['progressione_media_saliti']}% sale)
- Scuola Bridge (ottimizzare conversione)
- Riduzione disparita regionali
- Digitalizzazione servizi

Scrivi in italiano formale. NO markdown.
"""

sezioni['raccomandazioni'] = model.generate_content(prompt_raccomandazioni).text
print("   - Raccomandazioni generate")

# ============================================================================
# GENERAZIONE HTML
# ============================================================================
print("\n[3/5] Generazione HTML con grafici embedded...")

# Lista grafici per sezione
grafici_sommario = ['01_trend_tesseramenti.png', '02_piramide_eta.png']
grafici_categorie = ['04_piramide_categorie.png', '05_progressione_categorie.png', '06_matrice_transizione.png']
grafici_retention = ['03_retention_per_eta.png', '08_heatmap_retention_regionale.png']
grafici_circoli = ['09_circoli_virtuosi_critici.png']
grafici_sb = ['11_scuola_bridge_esiti.png', '12_fattori_successo_sb.png']
grafici_regioni = ['07_top_regioni.png']
grafici_churn = ['13_churn_segmentato.png']
grafici_ltv = ['14_ltv_per_eta.png']
grafici_extra = ['15_tipologie_tessera.png', '26_confronto_covid.png', '27_distribuzione_gare.png',
                 '28_genere_per_eta.png', '29_matrice_priorita.png', '30_proiezioni_2030.png']

# Grafici regionali
grafici_regionali = [f for f in CHARTS_DIR.glob('*_regione_*.png')]

def grafici_html(file_list, width="100%"):
    """Genera HTML per lista grafici"""
    html = '<div class="charts-container">'
    for f in file_list:
        img_path = CHARTS_DIR / f
        if img_path.exists():
            html += f'<img src="{embed_image(img_path)}" style="width:{width}; margin: 10px 0;">'
    html += '</div>'
    return html

# HTML Template
html_content = f"""
<!DOCTYPE html>
<html lang="it">
<head>
    <meta charset="UTF-8">
    <title>Relazione Completa FIGB 2017-2025</title>
    <style>
        @page {{
            size: A4;
            margin: 2cm;
            @top-center {{
                content: "FIGB - Relazione Tesseramento 2017-2025";
                font-size: 10px;
                color: #666;
            }}
            @bottom-center {{
                content: "Pagina " counter(page) " di " counter(pages);
                font-size: 10px;
                color: #666;
            }}
        }}

        body {{
            font-family: 'Helvetica Neue', Arial, sans-serif;
            font-size: 11pt;
            line-height: 1.6;
            color: #333;
            max-width: 100%;
        }}

        h1 {{
            color: #1E3A5F;
            font-size: 24pt;
            text-align: center;
            border-bottom: 3px solid #4A90D9;
            padding-bottom: 15px;
            margin-top: 30px;
        }}

        h2 {{
            color: #2E5984;
            font-size: 16pt;
            border-left: 4px solid #4A90D9;
            padding-left: 15px;
            margin-top: 30px;
            page-break-after: avoid;
        }}

        h3 {{
            color: #4A90D9;
            font-size: 13pt;
            margin-top: 20px;
        }}

        .cover {{
            text-align: center;
            page-break-after: always;
            padding: 50px 0;
        }}

        .cover h1 {{
            font-size: 32pt;
            margin-bottom: 20px;
        }}

        .cover .subtitle {{
            font-size: 18pt;
            color: #666;
            margin-bottom: 40px;
        }}

        .cover .meta {{
            font-size: 12pt;
            color: #888;
            margin-top: 60px;
        }}

        .summary-box {{
            background: linear-gradient(135deg, #1E3A5F 0%, #4A90D9 100%);
            color: white;
            padding: 25px;
            border-radius: 10px;
            margin: 20px 0;
        }}

        .summary-box h3 {{
            color: white;
            margin-top: 0;
        }}

        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 15px;
            margin: 20px 0;
        }}

        .metric-card {{
            background: #f8f9fa;
            border-left: 4px solid #4A90D9;
            padding: 15px;
            text-align: center;
        }}

        .metric-value {{
            font-size: 24pt;
            font-weight: bold;
            color: #1E3A5F;
        }}

        .metric-label {{
            font-size: 10pt;
            color: #666;
            text-transform: uppercase;
        }}

        .section {{
            margin: 30px 0;
        }}

        .chart-container {{
            text-align: center;
            margin: 20px 0;
            page-break-inside: avoid;
        }}

        .chart-container img {{
            max-width: 100%;
            height: auto;
            border: 1px solid #ddd;
            border-radius: 5px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }}

        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 15px 0;
            font-size: 10pt;
        }}

        th {{
            background: #1E3A5F;
            color: white;
            padding: 10px;
            text-align: left;
        }}

        td {{
            padding: 8px 10px;
            border-bottom: 1px solid #ddd;
        }}

        tr:nth-child(even) {{
            background: #f8f9fa;
        }}

        .highlight {{
            background: #fff3cd;
            padding: 15px;
            border-radius: 5px;
            margin: 15px 0;
            border-left: 4px solid #ffc107;
        }}

        .alert {{
            background: #f8d7da;
            padding: 15px;
            border-radius: 5px;
            margin: 15px 0;
            border-left: 4px solid #dc3545;
        }}

        .success {{
            background: #d4edda;
            padding: 15px;
            border-radius: 5px;
            margin: 15px 0;
            border-left: 4px solid #28a745;
        }}

        .toc {{
            page-break-after: always;
        }}

        .toc h2 {{
            border: none;
            text-align: center;
        }}

        .toc ul {{
            list-style: none;
            padding: 0;
        }}

        .toc li {{
            padding: 8px 0;
            border-bottom: 1px dotted #ccc;
        }}

        .page-break {{
            page-break-after: always;
        }}

        .two-columns {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
        }}
    </style>
</head>
<body>

<!-- COPERTINA -->
<div class="cover">
    <h1>RELAZIONE ANALISI TESSERAMENTO</h1>
    <div class="subtitle">FEDERAZIONE ITALIANA GIOCO BRIDGE</div>
    <div class="subtitle" style="font-size: 24pt; color: #1E3A5F;">2017 - 2025</div>

    <div style="margin: 60px 0;">
        <img src="{embed_image(CHARTS_DIR / '01_trend_tesseramenti.png')}" style="width: 80%;">
    </div>

    <div class="meta">
        <p><strong>Data:</strong> {datetime.now().strftime('%d %B %Y')}</p>
        <p><strong>Analisi statistica:</strong> Python (pandas, matplotlib, seaborn)</p>
        <p><strong>Generazione testo:</strong> Google Gemini AI</p>
        <p><strong>Grafici:</strong> {metriche['grafici_generati']} visualizzazioni</p>
    </div>
</div>

<!-- INDICE -->
<div class="toc">
    <h2>INDICE</h2>
    <ul>
        <li><strong>PARTE I - PANORAMICA GENERALE</strong></li>
        <li style="padding-left: 20px;">1. Sommario Esecutivo</li>
        <li style="padding-left: 20px;">2. Metriche Chiave</li>
        <li style="padding-left: 20px;">3. Analisi Temporale 2017-2025</li>
        <li><strong>PARTE II - ANALISI SPECIALISTICHE</strong></li>
        <li style="padding-left: 20px;">4. Piramide delle Categorie</li>
        <li style="padding-left: 20px;">5. Analisi Scuola Bridge</li>
        <li style="padding-left: 20px;">6. Analisi dei Circoli</li>
        <li style="padding-left: 20px;">7. Analisi Regionale</li>
        <li style="padding-left: 20px;">8. Giocatori Selettivi (Campionati vs Tornei)</li>
        <li style="padding-left: 20px;">9. Analisi del Churn</li>
        <li style="padding-left: 20px;">10. Lifetime Value (LTV)</li>
        <li><strong>PARTE III - CONCLUSIONI</strong></li>
        <li style="padding-left: 20px;">11. Raccomandazioni Strategiche</li>
        <li style="padding-left: 20px;">12. Nota Metodologica</li>
    </ul>
</div>

<!-- PARTE I: PANORAMICA -->
<h1>PARTE I - PANORAMICA GENERALE</h1>

<!-- 1. Sommario Esecutivo -->
<div class="section">
    <h2>1. Sommario Esecutivo</h2>

    <div class="summary-box">
        <h3>Highlights 2025</h3>
        <div class="metrics-grid" style="color: white;">
            <div>
                <div class="metric-value" style="color: white;">{metriche['anno_2025']['tesserati']:,}</div>
                <div class="metric-label" style="color: #ccc;">Tesserati</div>
            </div>
            <div>
                <div class="metric-value" style="color: white;">{metriche['anno_2025']['circoli_attivi']}</div>
                <div class="metric-label" style="color: #ccc;">Circoli Attivi</div>
            </div>
            <div>
                <div class="metric-value" style="color: white;">{metriche['retention']['media_globale']}%</div>
                <div class="metric-label" style="color: #ccc;">Retention</div>
            </div>
            <div>
                <div class="metric-value" style="color: white;">{metriche['anno_2025']['eta_media']}</div>
                <div class="metric-label" style="color: #ccc;">Eta Media</div>
            </div>
        </div>
    </div>

    <p>{sezioni['sommario']}</p>
</div>

<!-- 2. Metriche Chiave -->
<div class="section">
    <h2>2. Metriche Chiave</h2>

    <div class="metrics-grid">
        <div class="metric-card">
            <div class="metric-value">{metriche['anno_2025']['under_40_pct']}%</div>
            <div class="metric-label">Under 40</div>
        </div>
        <div class="metric-card">
            <div class="metric-value">{metriche['anno_2025']['over_70_pct']}%</div>
            <div class="metric-label">Over 70</div>
        </div>
        <div class="metric-card">
            <div class="metric-value">{metriche['anno_2025']['scuola_bridge']}</div>
            <div class="metric-label">Scuola Bridge</div>
        </div>
        <div class="metric-card">
            <div class="metric-value">{metriche['anno_2025']['agonisti']}</div>
            <div class="metric-label">Agonisti</div>
        </div>
    </div>

    <div class="two-columns">
        <div class="chart-container">
            <img src="{embed_image(CHARTS_DIR / '02_piramide_eta.png')}" style="width: 100%;">
        </div>
        <div class="chart-container">
            <img src="{embed_image(CHARTS_DIR / '28_genere_per_eta.png')}" style="width: 100%;">
        </div>
    </div>

    <div class="alert">
        <strong>ATTENZIONE:</strong> Solo il {metriche['anno_2025']['under_40_pct']}% dei tesserati ha meno di 40 anni,
        mentre il {metriche['anno_2025']['over_70_pct']}% supera i 70 anni. La sostenibilita a lungo termine richiede
        interventi urgenti sul reclutamento giovanile.
    </div>
</div>

<div class="page-break"></div>

<!-- 3. Analisi Temporale -->
<div class="section">
    <h2>3. Analisi Temporale 2017-2025</h2>

    <div class="chart-container">
        <img src="{embed_image(CHARTS_DIR / '01_trend_tesseramenti.png')}" style="width: 100%;">
    </div>

    <p>{sezioni['temporale']}</p>

    <div class="chart-container">
        <img src="{embed_image(CHARTS_DIR / '26_confronto_covid.png')}" style="width: 90%;">
    </div>

    <div class="success">
        <strong>SEGNALE POSITIVO:</strong> Il trend di recupero post-COVID e confermato.
        Dal minimo storico del 2021 (11,655 tesserati) siamo tornati a 13,662 nel 2025 (+17.2%).
    </div>
</div>

<div class="page-break"></div>

<!-- PARTE II: ANALISI SPECIALISTICHE -->
<h1>PARTE II - ANALISI SPECIALISTICHE</h1>

<!-- 4. Piramide Categorie -->
<div class="section">
    <h2>4. Piramide delle Categorie</h2>

    <div class="chart-container">
        <img src="{embed_image(CHARTS_DIR / '04_piramide_categorie.png')}" style="width: 100%;">
    </div>

    <p>{sezioni['categorie']}</p>

    <h3>Progressione tra Categorie</h3>
    <div class="two-columns">
        <div class="chart-container">
            <img src="{embed_image(CHARTS_DIR / '05_progressione_categorie.png')}" style="width: 100%;">
        </div>
        <div class="chart-container">
            <img src="{embed_image(CHARTS_DIR / '06_matrice_transizione.png')}" style="width: 100%;">
        </div>
    </div>

    <div class="highlight">
        <strong>PROBLEMA PIRAMIDABILITA:</strong> Solo il {metriche['categorie']['progressione_media_saliti']}% dei giocatori
        sale di categoria ogni anno. La maggioranza ({metriche['categorie']['progressione_media_stabili']}%) rimane stabile.
        La "piramide" e di fatto bloccata.
    </div>
</div>

<div class="page-break"></div>

<!-- 5. Scuola Bridge -->
<div class="section">
    <h2>5. Analisi Scuola Bridge</h2>

    <div class="summary-box">
        <h3>Performance Scuola Bridge</h3>
        <div class="metrics-grid" style="color: white;">
            <div>
                <div class="metric-value" style="color: white;">{metriche['scuola_bridge']['tasso_successo_medio']}%</div>
                <div class="metric-label" style="color: #ccc;">Tasso Successo</div>
            </div>
            <div>
                <div class="metric-value" style="color: white;">{metriche['scuola_bridge']['tasso_conversione_medio']}%</div>
                <div class="metric-label" style="color: #ccc;">Conversione</div>
            </div>
            <div>
                <div class="metric-value" style="color: white;">{metriche['scuola_bridge']['tasso_churn_medio']}%</div>
                <div class="metric-label" style="color: #ccc;">Churn Reale</div>
            </div>
            <div>
                <div class="metric-value" style="color: white;">{metriche['scuola_bridge']['correlazione_gare_retention']}</div>
                <div class="metric-label" style="color: #ccc;">Corr. Gare-Ret.</div>
            </div>
        </div>
    </div>

    <p>{sezioni['scuola_bridge']}</p>

    <div class="two-columns">
        <div class="chart-container">
            <img src="{embed_image(CHARTS_DIR / '11_scuola_bridge_esiti.png')}" style="width: 100%;">
        </div>
        <div class="chart-container">
            <img src="{embed_image(CHARTS_DIR / '12_fattori_successo_sb.png')}" style="width: 100%;">
        </div>
    </div>

    <div class="success">
        <strong>BEST PRACTICE:</strong> La correlazione tra numero di gare giocate e retention e forte ({metriche['scuola_bridge']['correlazione_gare_retention']}).
        Incentivare la partecipazione alle gare e la strategia piu efficace per mantenere gli allievi.
    </div>
</div>

<div class="page-break"></div>

<!-- 6. Analisi Circoli -->
<div class="section">
    <h2>6. Analisi dei Circoli</h2>

    <div class="chart-container">
        <img src="{embed_image(CHARTS_DIR / '09_circoli_virtuosi_critici.png')}" style="width: 100%;">
    </div>

    <p>{sezioni['circoli']}</p>

    <h3>Circoli Virtuosi (Top Retention)</h3>
    <table>
        <tr>
            <th>Circolo</th>
            <th>Regione</th>
            <th>Tesserati</th>
            <th>Retention</th>
            <th>Conv. SB</th>
        </tr>
        {''.join([f"<tr><td>{row['GrpName']}</td><td>{row['Regione']}</td><td>{row['Tesserati']}</td><td>{row['Retention']}%</td><td>{row.get('ConvSB', 'N/A')}%</td></tr>" for _, row in circoli_v.head(10).iterrows()])}
    </table>

    <h3>Circoli Critici (Bassa Retention)</h3>
    <table>
        <tr>
            <th>Circolo</th>
            <th>Regione</th>
            <th>Tesserati</th>
            <th>Retention</th>
        </tr>
        {''.join([f"<tr><td>{row['GrpName']}</td><td>{row['Regione']}</td><td>{row['Tesserati']}</td><td>{row['Retention']}%</td></tr>" for _, row in circoli_c.head(10).iterrows()])}
    </table>
</div>

<div class="page-break"></div>

<!-- 7. Analisi Regionale -->
<div class="section">
    <h2>7. Analisi Regionale</h2>

    <div class="chart-container">
        <img src="{embed_image(CHARTS_DIR / '07_top_regioni.png')}" style="width: 100%;">
    </div>

    <p>{sezioni['regioni']}</p>

    <div class="chart-container">
        <img src="{embed_image(CHARTS_DIR / '08_heatmap_retention_regionale.png')}" style="width: 100%;">
    </div>

    <h3>Riepilogo Regionale</h3>
    <table>
        <tr>
            <th>Regione</th>
            <th>Tesserati 2025</th>
            <th>Trend</th>
            <th>Retention</th>
            <th>Eta Media</th>
        </tr>
        {''.join([f"<tr><td>{row['Regione']}</td><td>{row['Tesserati2025']}</td><td>{row['Trend']}</td><td>{row['RetentionMedia']:.1f}%</td><td>{row['EtaMedia']:.1f}</td></tr>" for _, row in regioni.iterrows()])}
    </table>
</div>

<div class="page-break"></div>

<!-- Focus Regionali -->
<div class="section">
    <h2>7.1 Focus sulle Regioni Principali</h2>

    <div class="two-columns">
        <div class="chart-container">
            <img src="{embed_image(CHARTS_DIR / '16_regione_lombardia.png')}" style="width: 100%;">
        </div>
        <div class="chart-container">
            <img src="{embed_image(CHARTS_DIR / '17_regione_lazio.png')}" style="width: 100%;">
        </div>
    </div>

    <div class="two-columns">
        <div class="chart-container">
            <img src="{embed_image(CHARTS_DIR / '18_regione_emilia-romagna.png')}" style="width: 100%;">
        </div>
        <div class="chart-container">
            <img src="{embed_image(CHARTS_DIR / '19_regione_piemonte.png')}" style="width: 100%;">
        </div>
    </div>

    <div class="two-columns">
        <div class="chart-container">
            <img src="{embed_image(CHARTS_DIR / '20_regione_toscana.png')}" style="width: 100%;">
        </div>
        <div class="chart-container">
            <img src="{embed_image(CHARTS_DIR / '21_regione_veneto.png')}" style="width: 100%;">
        </div>
    </div>
</div>

<div class="page-break"></div>

<!-- 8. Giocatori Selettivi -->
<div class="section">
    <h2>8. Giocatori Selettivi: Campionati vs Tornei</h2>

    <div class="chart-container">
        <img src="{embed_image(CHARTS_DIR / '10_profili_giocatori.png')}" style="width: 100%;">
    </div>

    <h3>Profili Giocatori</h3>
    <table>
        <tr>
            <th>Profilo</th>
            <th>Giocatori</th>
            <th>%</th>
            <th>Gare Medie</th>
            <th>Descrizione</th>
        </tr>
        {''.join([f"<tr><td>{row['Profilo']}</td><td>{row['Giocatori']:,}</td><td>{row['%']:.1f}%</td><td>{row['GareMedie']:.1f}</td><td>{row['Descrizione']}</td></tr>" for _, row in profili.iterrows()])}
    </table>

    <h3>Selettivi per Categoria</h3>
    <table>
        <tr>
            <th>Categoria</th>
            <th>Giocatori</th>
            <th>Selettivi</th>
            <th>% Selettivi</th>
            <th>Gare Medie</th>
        </tr>
        {''.join([f"<tr><td>{row['Livello']}</td><td>{row['Giocatori']}</td><td>{row['Selettivi']}</td><td>{row['PctSelettivi']:.1f}%</td><td>{row['GareMedie']:.1f}</td></tr>" for _, row in selettivi.iterrows()])}
    </table>

    <div class="highlight">
        <strong>INSIGHT:</strong> I giocatori che partecipano ai campionati (selettivi) hanno un tasso di retention
        significativamente superiore. La partecipazione a gare competitive e un forte fattore di fidelizzazione.
    </div>
</div>

<div class="page-break"></div>

<!-- 9. Analisi Churn -->
<div class="section">
    <h2>9. Analisi del Churn</h2>

    <div class="chart-container">
        <img src="{embed_image(CHARTS_DIR / '13_churn_segmentato.png')}" style="width: 100%;">
    </div>

    <p>{sezioni['churn']}</p>

    <div class="summary-box">
        <h3>Segmentazione Churn</h3>
        <div class="metrics-grid" style="color: white;">
            <div>
                <div class="metric-value" style="color: white;">{metriche['churn']['totale']:,}</div>
                <div class="metric-label" style="color: #ccc;">Churn Totale</div>
            </div>
            <div>
                <div class="metric-value" style="color: white;">{metriche['churn']['stima_decessi']:,}</div>
                <div class="metric-label" style="color: #ccc;">Stima Decessi</div>
            </div>
            <div>
                <div class="metric-value" style="color: white;">{metriche['churn']['stima_infermi']:,}</div>
                <div class="metric-label" style="color: #ccc;">Stima Infermi</div>
            </div>
            <div>
                <div class="metric-value" style="color: white;">{metriche['churn']['recuperabile']:,}</div>
                <div class="metric-label" style="color: #ccc;">Recuperabile</div>
            </div>
        </div>
    </div>

    <div class="alert">
        <strong>CHURN RECUPERABILE:</strong> Il {metriche['churn']['pct_recuperabile']}% del churn (circa {metriche['churn']['recuperabile']:,} persone)
        e potenzialmente recuperabile con azioni mirate di retention.
    </div>
</div>

<div class="page-break"></div>

<!-- 10. Lifetime Value -->
<div class="section">
    <h2>10. Analisi Lifetime Value (LTV)</h2>

    <div class="chart-container">
        <img src="{embed_image(CHARTS_DIR / '14_ltv_per_eta.png')}" style="width: 100%;">
    </div>

    <p>{sezioni['ltv']}</p>

    <h3>LTV per Fascia di Eta</h3>
    <table>
        <tr>
            <th>Fascia Eta</th>
            <th>Giocatori</th>
            <th>Retention</th>
            <th>Anni Residui</th>
            <th>LTV Individuale</th>
            <th>Valore Totale</th>
        </tr>
        {''.join([f"<tr><td>{row['FasciaEta']}</td><td>{row['Giocatori']:,}</td><td>{row['RetentionMedia']}%</td><td>{row['AnniVitaResidui']}</td><td>€{row['LTV']:,.0f}</td><td>€{row['ValoreTotale']:,.0f}</td></tr>" for _, row in ltv.iterrows()])}
    </table>

    <div class="success">
        <strong>VALORE TOTALE BASE TESSERATI:</strong> €{metriche['ltv']['totale_milioni']}M.
        Il segmento 60-70 anni rappresenta il miglior equilibrio tra valore attuale e anni residui.
    </div>
</div>

<div class="page-break"></div>

<!-- PARTE III: CONCLUSIONI -->
<h1>PARTE III - CONCLUSIONI E RACCOMANDAZIONI</h1>

<!-- 11. Raccomandazioni -->
<div class="section">
    <h2>11. Raccomandazioni Strategiche</h2>

    <div class="chart-container">
        <img src="{embed_image(CHARTS_DIR / '29_matrice_priorita.png')}" style="width: 100%;">
    </div>

    <p>{sezioni['raccomandazioni']}</p>

    <div class="chart-container">
        <img src="{embed_image(CHARTS_DIR / '30_proiezioni_2030.png')}" style="width: 100%;">
    </div>
</div>

<!-- 12. Nota Metodologica -->
<div class="section">
    <h2>12. Nota Metodologica</h2>

    <h3>Fonti Dati</h3>
    <ul>
        <li>Dati ufficiali tesseramento FIGB 2017-2025</li>
        <li>Record totali analizzati: {metriche['dati_base']['record_totali']:,}</li>
        <li>Giocatori unici: {metriche['dati_base']['giocatori_unici']:,}</li>
        <li>Periodo: {metriche['dati_base']['periodo']}</li>
    </ul>

    <h3>Metodologia di Analisi</h3>
    <ul>
        <li><strong>Analisi statistica:</strong> Python 3.12 con pandas, numpy, matplotlib, seaborn</li>
        <li><strong>Generazione testo:</strong> Google Gemini AI (gemini-2.0-flash)</li>
        <li><strong>Generazione PDF:</strong> WeasyPrint</li>
        <li><strong>Grafici generati:</strong> {metriche['grafici_generati']}</li>
    </ul>

    <h3>Definizioni Chiave</h3>
    <ul>
        <li><strong>Retention Rate:</strong> % tesserati anno N-1 che si ritesserano anno N</li>
        <li><strong>Scuola Bridge - Progressione:</strong> Rimane in SB (esito positivo, corso triennale)</li>
        <li><strong>Scuola Bridge - Conversione:</strong> Passa ad altra tessera (esito positivo, completamento)</li>
        <li><strong>Scuola Bridge - Churn:</strong> Non si ritessera (esito negativo)</li>
        <li><strong>Giocatore Selettivo:</strong> > 50% punti da campionati</li>
        <li><strong>LTV:</strong> Valore economico atteso del tesserato nel ciclo di vita residuo</li>
    </ul>

    <h3>Limitazioni</h3>
    <ul>
        <li>Le stime di decessi/infermita sono basate su modelli statistici, non su dati effettivi</li>
        <li>I dati pre-2017 non sono disponibili per confronti di lungo periodo</li>
        <li>Alcune metriche potrebbero essere influenzate da variazioni nei criteri di registrazione</li>
    </ul>
</div>

<!-- Footer -->
<div style="text-align: center; margin-top: 50px; padding: 20px; border-top: 2px solid #1E3A5F;">
    <p style="color: #666; font-size: 10pt;">
        Relazione generata automaticamente il {datetime.now().strftime('%d/%m/%Y alle %H:%M')}<br>
        Powered by Google Gemini AI | Analisi con Python | PDF con WeasyPrint<br>
        <strong>FIGB - Federazione Italiana Gioco Bridge</strong>
    </p>
</div>

</body>
</html>
"""

print(f"   HTML generato ({len(html_content):,} caratteri)")

# ============================================================================
# GENERAZIONE PDF
# ============================================================================
print("\n[4/5] Generazione PDF...")

pdf_path = OUTPUT_DIR / f'Relazione_Completa_FIGB_2017_2025_{datetime.now().strftime("%Y%m%d")}.pdf'

HTML(string=html_content).write_pdf(
    pdf_path,
    stylesheets=[CSS(string='@page { size: A4; margin: 1.5cm; }')]
)

print(f"   PDF salvato: {pdf_path}")

# ============================================================================
# SALVATAGGIO HTML (backup)
# ============================================================================
print("\n[5/5] Salvataggio HTML...")

html_path = OUTPUT_DIR / f'Relazione_Completa_FIGB_2017_2025_{datetime.now().strftime("%Y%m%d")}.html'
with open(html_path, 'w', encoding='utf-8') as f:
    f.write(html_content)

print(f"   HTML salvato: {html_path}")

# ============================================================================
# RIEPILOGO FINALE
# ============================================================================
print("\n" + "=" * 100)
print("REPORT PDF COMPLETATO")
print("=" * 100)
print(f"\nFile generati:")
print(f"  - PDF: {pdf_path}")
print(f"  - HTML: {html_path}")
print(f"\nContenuto:")
print(f"  - {metriche['grafici_generati']} grafici integrati")
print(f"  - 12 sezioni di analisi")
print(f"  - Testo generato con Gemini AI")
print("=" * 100)
