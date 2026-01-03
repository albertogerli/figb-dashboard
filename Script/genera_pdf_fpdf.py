#!/usr/bin/env python3
"""
GENERATORE REPORT PDF COMPLETO FIGB 2017-2025
Con grafici integrati - Versione FPDF2
"""

import pandas as pd
import json
from pathlib import Path
from datetime import datetime
from fpdf import FPDF
import requests

# API Gemini
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', '')
GEMINI_MODEL = 'gemini-3-flash-preview'

def call_gemini(prompt):
    """Chiama Gemini API via REST"""
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}"
    response = requests.post(url, json={
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.7, "maxOutputTokens": 1500}
    })
    if response.status_code == 200:
        return response.json()['candidates'][0]['content']['parts'][0]['text']
    else:
        return f"Errore API: {response.status_code}"

# Directory
BASE_DIR = Path(__file__).parent.parent
OUTPUT_DIR = BASE_DIR / 'output'
CHARTS_DIR = OUTPUT_DIR / 'charts_v2'
RESULTS_DIR = OUTPUT_DIR / 'results_v2'

print("=" * 100)
print("GENERAZIONE REPORT PDF COMPLETO FIGB 2017-2025")
print("Versione FPDF2")
print("=" * 100)

# ============================================================================
# CLASSE PDF PERSONALIZZATA
# ============================================================================
class ReportPDF(FPDF):
    def __init__(self):
        super().__init__()
        self.set_auto_page_break(auto=True, margin=20)

    def header(self):
        if self.page_no() > 1:
            self.set_font('Helvetica', 'I', 9)
            self.set_text_color(100, 100, 100)
            self.cell(0, 10, 'FIGB - Relazione Tesseramento 2017-2025', align='C')
            self.ln(5)
            self.line(10, 18, 200, 18)
            self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font('Helvetica', 'I', 8)
        self.set_text_color(100, 100, 100)
        self.cell(0, 10, f'Pagina {self.page_no()}', align='C')

    def chapter_title(self, title, level=1):
        if level == 1:
            self.set_font('Helvetica', 'B', 18)
            self.set_text_color(30, 58, 95)  # Primary color
            self.ln(10)
        else:
            self.set_font('Helvetica', 'B', 14)
            self.set_text_color(46, 89, 132)  # Secondary color
            self.ln(5)

        self.multi_cell(0, 10, title)
        self.ln(3)

        if level == 1:
            self.set_draw_color(74, 144, 217)
            self.line(10, self.get_y(), 200, self.get_y())
            self.ln(5)

    def add_text(self, text):
        self.set_font('Helvetica', '', 10)
        self.set_text_color(50, 50, 50)
        # Gestisci caratteri non-latin1
        text_clean = text.encode('latin-1', 'replace').decode('latin-1')
        self.multi_cell(0, 6, text_clean)
        self.ln(3)

    def add_metric_box(self, value, label, x, y, w=40):
        self.set_xy(x, y)
        self.set_fill_color(248, 249, 250)
        self.set_draw_color(74, 144, 217)
        self.rect(x, y, w, 25, 'DF')

        # Linea colorata a sinistra
        self.set_draw_color(74, 144, 217)
        self.line(x, y, x, y + 25)
        self.line(x + 0.5, y, x + 0.5, y + 25)
        self.line(x + 1, y, x + 1, y + 25)

        # Valore
        self.set_xy(x + 5, y + 3)
        self.set_font('Helvetica', 'B', 16)
        self.set_text_color(30, 58, 95)
        self.cell(w - 10, 10, str(value), align='C')

        # Label
        self.set_xy(x + 5, y + 14)
        self.set_font('Helvetica', '', 7)
        self.set_text_color(100, 100, 100)
        self.cell(w - 10, 8, label.upper(), align='C')

    def add_chart(self, img_path, width=180):
        if Path(img_path).exists():
            self.ln(5)
            x = (210 - width) / 2  # Centra
            self.image(str(img_path), x=x, w=width)
            self.ln(5)

    def add_highlight(self, text, color='warning'):
        colors = {
            'warning': (255, 243, 205),
            'danger': (248, 215, 218),
            'success': (212, 237, 218),
            'info': (217, 237, 247)
        }
        border_colors = {
            'warning': (255, 193, 7),
            'danger': (220, 53, 69),
            'success': (40, 167, 69),
            'info': (23, 162, 184)
        }

        bg = colors.get(color, colors['info'])
        border = border_colors.get(color, border_colors['info'])

        self.set_fill_color(*bg)
        self.set_draw_color(*border)

        start_y = self.get_y()
        self.rect(10, start_y, 190, 20, 'DF')
        self.line(10, start_y, 10, start_y + 20)
        self.line(10.5, start_y, 10.5, start_y + 20)
        self.line(11, start_y, 11, start_y + 20)

        self.set_xy(15, start_y + 5)
        self.set_font('Helvetica', '', 9)
        self.set_text_color(50, 50, 50)
        text_clean = text.encode('latin-1', 'replace').decode('latin-1')
        self.multi_cell(180, 5, text_clean)
        self.ln(3)

    def add_table(self, headers, rows, col_widths=None):
        if col_widths is None:
            col_widths = [190 / len(headers)] * len(headers)

        # Header
        self.set_font('Helvetica', 'B', 9)
        self.set_fill_color(30, 58, 95)
        self.set_text_color(255, 255, 255)

        for i, h in enumerate(headers):
            self.cell(col_widths[i], 8, str(h), border=1, fill=True, align='C')
        self.ln()

        # Rows
        self.set_font('Helvetica', '', 8)
        self.set_text_color(50, 50, 50)

        for row_idx, row in enumerate(rows):
            if row_idx % 2 == 0:
                self.set_fill_color(248, 249, 250)
            else:
                self.set_fill_color(255, 255, 255)

            for i, cell in enumerate(row):
                cell_str = str(cell).encode('latin-1', 'replace').decode('latin-1')
                self.cell(col_widths[i], 7, cell_str, border=1, fill=True, align='C')
            self.ln()

        self.ln(5)


# ============================================================================
# CARICAMENTO DATI E METRICHE
# ============================================================================
print("\n[1/5] Caricamento dati e metriche...")

with open(RESULTS_DIR / 'metriche_complete_v2.json', 'r', encoding='utf-8') as f:
    metriche = json.load(f)

# Carica CSV
cat_dist = pd.read_csv(RESULTS_DIR / 'distribuzione_categorie.csv')
progressione = pd.read_csv(RESULTS_DIR / 'progressione_categorie.csv')
regioni = pd.read_csv(RESULTS_DIR / 'regioni_summary.csv')
circoli_v = pd.read_csv(RESULTS_DIR / 'circoli_virtuosi.csv')
circoli_c = pd.read_csv(RESULTS_DIR / 'circoli_critici.csv')
profili = pd.read_csv(RESULTS_DIR / 'profili_giocatori.csv')
sb_analisi = pd.read_csv(RESULTS_DIR / 'scuola_bridge_analisi.csv')
churn_summary = pd.read_csv(RESULTS_DIR / 'churn_summary.csv')
ltv = pd.read_csv(RESULTS_DIR / 'lifetime_value.csv')
selettivi = pd.read_csv(RESULTS_DIR / 'selettivi_per_categoria.csv')

print(f"   Caricati dati e metriche")

# ============================================================================
# GENERAZIONE TESTO CON GEMINI
# ============================================================================
print("\n[2/5] Generazione analisi con Gemini AI...")

contesto_dati = f"""
DATI TESSERAMENTO FIGB 2017-2025:
- Tesserati 2025: {metriche['anno_2025']['tesserati']:,}
- Circoli attivi: {metriche['anno_2025']['circoli_attivi']}
- Eta media: {metriche['anno_2025']['eta_media']} anni
- Under 40: {metriche['anno_2025']['under_40_pct']}%
- Over 70: {metriche['anno_2025']['over_70_pct']}%
- Retention media: {metriche['retention']['media_globale']}%
- Scuola Bridge successo: {metriche['scuola_bridge']['tasso_successo_medio']}%
- Churn recuperabile: {metriche['churn']['pct_recuperabile']}%
"""

# Genera sezioni
sezioni = {}

prompt_sommario = f"""
Scrivi un SOMMARIO ESECUTIVO (max 250 parole) per il report FIGB 2017-2025.
{contesto_dati}
Stile: formale, aziendale. NO markdown, NO emoji, testo semplice.
"""
sezioni['sommario'] = call_gemini(prompt_sommario)
print("   - Sommario esecutivo")

prompt_temporale = f"""
Scrivi l'ANALISI TEMPORALE (max 200 parole) del tesseramento FIGB 2017-2025.
Trend: picco 2018 (~19,800), crollo COVID 2020-2021 (~11,600), recovery 2022-2025 (13,662).
NO markdown, testo semplice.
"""
sezioni['temporale'] = call_gemini(prompt_temporale)
print("   - Analisi temporale")

prompt_categorie = f"""
Scrivi l'ANALISI PIRAMIDE CATEGORIE (max 200 parole).
Struttura: NC -> Quarta -> Terza -> Seconda -> Prima -> Honor -> Master
Solo {metriche['categorie']['progressione_media_saliti']}% sale di categoria.
NO markdown.
"""
sezioni['categorie'] = call_gemini(prompt_categorie)
print("   - Analisi categorie")

prompt_sb = f"""
Scrivi l'ANALISI SCUOLA BRIDGE (max 200 parole).
Tasso successo: {metriche['scuola_bridge']['tasso_successo_medio']}%
Conversione: {metriche['scuola_bridge']['tasso_conversione_medio']}%
Correlazione gare-retention: {metriche['scuola_bridge']['correlazione_gare_retention']}
NO markdown.
"""
sezioni['scuola_bridge'] = call_gemini(prompt_sb)
print("   - Analisi Scuola Bridge")

prompt_circoli = f"""
Scrivi l'ANALISI DEI CIRCOLI (max 200 parole).
Evidenzia differenze tra circoli virtuosi (alta retention) e critici.
NO markdown.
"""
sezioni['circoli'] = call_gemini(prompt_circoli)
print("   - Analisi circoli")

prompt_raccomandazioni = f"""
Scrivi 6 RACCOMANDAZIONI STRATEGICHE (max 300 parole).
Focus: reclutamento giovani, retention, progressione categorie.
NO markdown, numera le raccomandazioni.
"""
sezioni['raccomandazioni'] = call_gemini(prompt_raccomandazioni)
print("   - Raccomandazioni")

# ============================================================================
# CREAZIONE PDF
# ============================================================================
print("\n[3/5] Creazione PDF...")

pdf = ReportPDF()
pdf.set_title('Relazione FIGB 2017-2025')
pdf.set_author('FIGB - Analisi Automatica')

# COPERTINA
pdf.add_page()
pdf.ln(30)
pdf.set_font('Helvetica', 'B', 28)
pdf.set_text_color(30, 58, 95)
pdf.cell(0, 15, 'RELAZIONE ANALISI TESSERAMENTO', align='C')
pdf.ln(15)
pdf.set_font('Helvetica', '', 18)
pdf.set_text_color(100, 100, 100)
pdf.cell(0, 10, 'FEDERAZIONE ITALIANA GIOCO BRIDGE', align='C')
pdf.ln(15)
pdf.set_font('Helvetica', 'B', 24)
pdf.set_text_color(74, 144, 217)
pdf.cell(0, 15, '2017 - 2025', align='C')

# Grafico copertina
pdf.ln(10)
pdf.add_chart(CHARTS_DIR / '01_trend_tesseramenti.png', width=160)

pdf.ln(20)
pdf.set_font('Helvetica', '', 11)
pdf.set_text_color(100, 100, 100)
pdf.cell(0, 8, f"Data: {datetime.now().strftime('%d %B %Y')}", align='C')
pdf.ln(6)
pdf.cell(0, 8, f"Grafici: {metriche['grafici_generati']} visualizzazioni", align='C')
pdf.ln(6)
pdf.cell(0, 8, "Powered by: Python + Google Gemini AI", align='C')

# INDICE
pdf.add_page()
pdf.chapter_title('INDICE', 1)
pdf.set_font('Helvetica', '', 11)

indice = [
    ("PARTE I - PANORAMICA GENERALE", ""),
    ("   1. Sommario Esecutivo", ""),
    ("   2. Metriche Chiave", ""),
    ("   3. Analisi Temporale 2017-2025", ""),
    ("PARTE II - ANALISI SPECIALISTICHE", ""),
    ("   4. Piramide delle Categorie", ""),
    ("   5. Analisi Scuola Bridge", ""),
    ("   6. Analisi dei Circoli", ""),
    ("   7. Analisi Regionale", ""),
    ("   8. Giocatori Selettivi", ""),
    ("   9. Analisi del Churn", ""),
    ("   10. Lifetime Value (LTV)", ""),
    ("PARTE III - CONCLUSIONI", ""),
    ("   11. Raccomandazioni Strategiche", ""),
    ("   12. Nota Metodologica", ""),
]

for item, _ in indice:
    if item.startswith("PARTE"):
        pdf.set_font('Helvetica', 'B', 11)
    else:
        pdf.set_font('Helvetica', '', 11)
    pdf.cell(0, 8, item)
    pdf.ln()

# PARTE I - PANORAMICA
pdf.add_page()
pdf.chapter_title('PARTE I - PANORAMICA GENERALE', 1)

# 1. Sommario Esecutivo
pdf.chapter_title('1. Sommario Esecutivo', 2)

# Metriche principali
y = pdf.get_y()
pdf.add_metric_box(f"{metriche['anno_2025']['tesserati']:,}", 'Tesserati 2025', 12, y, 42)
pdf.add_metric_box(f"{metriche['anno_2025']['circoli_attivi']}", 'Circoli Attivi', 58, y, 42)
pdf.add_metric_box(f"{metriche['retention']['media_globale']}%", 'Retention', 104, y, 42)
pdf.add_metric_box(f"{metriche['anno_2025']['eta_media']}", 'Eta Media', 150, y, 42)
pdf.ln(30)

pdf.add_text(sezioni['sommario'])

# 2. Metriche Chiave
pdf.add_page()
pdf.chapter_title('2. Metriche Chiave', 2)

y = pdf.get_y()
pdf.add_metric_box(f"{metriche['anno_2025']['under_40_pct']}%", 'Under 40', 12, y, 42)
pdf.add_metric_box(f"{metriche['anno_2025']['over_70_pct']}%", 'Over 70', 58, y, 42)
pdf.add_metric_box(f"{metriche['anno_2025']['scuola_bridge']}", 'Scuola Bridge', 104, y, 42)
pdf.add_metric_box(f"{metriche['anno_2025']['agonisti']}", 'Agonisti', 150, y, 42)
pdf.ln(35)

pdf.add_chart(CHARTS_DIR / '02_piramide_eta.png', width=170)

pdf.add_highlight(
    f"ATTENZIONE: Solo il {metriche['anno_2025']['under_40_pct']}% dei tesserati ha meno di 40 anni, "
    f"mentre il {metriche['anno_2025']['over_70_pct']}% supera i 70 anni.",
    'danger'
)

# 3. Analisi Temporale
pdf.add_page()
pdf.chapter_title('3. Analisi Temporale 2017-2025', 2)
pdf.add_chart(CHARTS_DIR / '01_trend_tesseramenti.png', width=175)
pdf.add_text(sezioni['temporale'])
pdf.add_chart(CHARTS_DIR / '26_confronto_covid.png', width=160)

pdf.add_highlight(
    "SEGNALE POSITIVO: Dal minimo storico del 2021 (11,655) siamo tornati a 13,662 nel 2025 (+17.2%).",
    'success'
)

# PARTE II - ANALISI SPECIALISTICHE
pdf.add_page()
pdf.chapter_title('PARTE II - ANALISI SPECIALISTICHE', 1)

# 4. Piramide Categorie
pdf.chapter_title('4. Piramide delle Categorie', 2)
pdf.add_chart(CHARTS_DIR / '04_piramide_categorie.png', width=170)
pdf.add_text(sezioni['categorie'])

pdf.add_page()
pdf.chapter_title('4.1 Progressione tra Categorie', 2)
pdf.add_chart(CHARTS_DIR / '05_progressione_categorie.png', width=170)
pdf.add_chart(CHARTS_DIR / '06_matrice_transizione.png', width=170)

pdf.add_highlight(
    f"PROBLEMA: Solo il {metriche['categorie']['progressione_media_saliti']}% sale di categoria ogni anno. "
    f"La piramide e bloccata.",
    'warning'
)

# 5. Scuola Bridge
pdf.add_page()
pdf.chapter_title('5. Analisi Scuola Bridge', 2)

y = pdf.get_y()
pdf.add_metric_box(f"{metriche['scuola_bridge']['tasso_successo_medio']}%", 'Tasso Successo', 12, y, 58)
pdf.add_metric_box(f"{metriche['scuola_bridge']['tasso_conversione_medio']}%", 'Conversione', 76, y, 58)
pdf.add_metric_box(f"{metriche['scuola_bridge']['tasso_churn_medio']}%", 'Churn Reale', 140, y, 58)
pdf.ln(35)

pdf.add_text(sezioni['scuola_bridge'])
pdf.add_chart(CHARTS_DIR / '11_scuola_bridge_esiti.png', width=160)
pdf.add_chart(CHARTS_DIR / '12_fattori_successo_sb.png', width=160)

pdf.add_highlight(
    f"BEST PRACTICE: Correlazione gare-retention = {metriche['scuola_bridge']['correlazione_gare_retention']}. "
    "Incentivare la partecipazione alle gare.",
    'success'
)

# 6. Circoli
pdf.add_page()
pdf.chapter_title('6. Analisi dei Circoli', 2)
pdf.add_chart(CHARTS_DIR / '09_circoli_virtuosi_critici.png', width=175)
pdf.add_text(sezioni['circoli'])

# Tabella circoli virtuosi
pdf.chapter_title('Circoli Virtuosi (Top 10)', 2)
headers = ['Circolo', 'Regione', 'Allievi SB', 'Successo']
rows = [[r['NomeCircolo'][:25], r['Regione'][:12], r['AllievoSB'], f"{r['TassoSuccesso']}%"]
        for _, r in circoli_v.head(10).iterrows()]
pdf.add_table(headers, rows, [80, 40, 30, 30])

# 7. Analisi Regionale
pdf.add_page()
pdf.chapter_title('7. Analisi Regionale', 2)
pdf.add_chart(CHARTS_DIR / '07_top_regioni.png', width=175)

# Tabella regioni
headers = ['Regione', 'Tesserati', 'Variazione', 'Retention', 'Eta Media']
rows = [[r['Regione'], r['Tesserati'], f"{r['VariazionePct']:.1f}%", f"{r['RetentionMedia']:.1f}%", f"{r['EtaMedia']:.1f}"]
        for _, r in regioni.iterrows()]
pdf.add_table(headers, rows, [50, 35, 35, 35, 35])

pdf.add_page()
pdf.chapter_title('7.1 Heatmap Retention Regionale', 2)
pdf.add_chart(CHARTS_DIR / '08_heatmap_retention_regionale.png', width=175)

# Focus regioni principali
pdf.add_page()
pdf.chapter_title('7.2 Focus Regioni Principali', 2)
pdf.add_chart(CHARTS_DIR / '16_regione_lombardia.png', width=165)
pdf.add_chart(CHARTS_DIR / '17_regione_lazio.png', width=165)

pdf.add_page()
pdf.add_chart(CHARTS_DIR / '18_regione_emilia-romagna.png', width=165)
pdf.add_chart(CHARTS_DIR / '19_regione_piemonte.png', width=165)

pdf.add_page()
pdf.add_chart(CHARTS_DIR / '20_regione_toscana.png', width=165)
pdf.add_chart(CHARTS_DIR / '21_regione_veneto.png', width=165)

# 8. Giocatori Selettivi
pdf.add_page()
pdf.chapter_title('8. Giocatori Selettivi: Campionati vs Tornei', 2)
pdf.add_chart(CHARTS_DIR / '10_profili_giocatori.png', width=170)

# Tabella profili
headers = ['Profilo', 'Giocatori', '%', 'Gare Medie']
rows = [[r['Profilo'], f"{r['Giocatori']:,}", f"{r['%']:.1f}%", f"{r['GareMedie']:.1f}"]
        for _, r in profili.iterrows()]
pdf.add_table(headers, rows, [60, 45, 40, 45])

pdf.add_highlight(
    "I giocatori che partecipano ai campionati hanno retention significativamente superiore.",
    'info'
)

# 9. Churn
pdf.add_page()
pdf.chapter_title('9. Analisi del Churn', 2)
pdf.add_chart(CHARTS_DIR / '13_churn_segmentato.png', width=170)

y = pdf.get_y()
pdf.add_metric_box(f"{metriche['churn']['totale']:,}", 'Churn Totale', 12, y, 42)
pdf.add_metric_box(f"{metriche['churn']['stima_decessi']:,}", 'Stima Decessi', 58, y, 42)
pdf.add_metric_box(f"{metriche['churn']['stima_infermi']:,}", 'Stima Infermi', 104, y, 42)
pdf.add_metric_box(f"{metriche['churn']['recuperabile']:,}", 'Recuperabile', 150, y, 42)
pdf.ln(35)

pdf.add_highlight(
    f"CHURN RECUPERABILE: Il {metriche['churn']['pct_recuperabile']}% del churn "
    f"(circa {metriche['churn']['recuperabile']:,} persone) e recuperabile con azioni mirate.",
    'warning'
)

# 10. LTV
pdf.add_page()
pdf.chapter_title('10. Analisi Lifetime Value (LTV)', 2)
pdf.add_chart(CHARTS_DIR / '14_ltv_per_eta.png', width=170)

# Tabella LTV
headers = ['Fascia Eta', 'Giocatori', 'Retention', 'Anni Residui', 'LTV', 'Valore Tot.']
rows = [[r['FasciaEta'], f"{r['Giocatori']:,}", f"{r['RetentionMedia']}%",
         r['AnniVitaResidui'], f"EUR{r['LTV']:,.0f}", f"EUR{r['ValoreTotale']:,.0f}"]
        for _, r in ltv.iterrows()]
pdf.add_table(headers, rows, [30, 30, 28, 28, 35, 39])

pdf.add_highlight(
    f"VALORE TOTALE: EUR{metriche['ltv']['totale_milioni']}M. "
    f"Il segmento 60-70 rappresenta il miglior equilibrio tra valore e anni residui.",
    'success'
)

# PARTE III - CONCLUSIONI
pdf.add_page()
pdf.chapter_title('PARTE III - CONCLUSIONI', 1)

# 11. Raccomandazioni
pdf.chapter_title('11. Raccomandazioni Strategiche', 2)
pdf.add_chart(CHARTS_DIR / '29_matrice_priorita.png', width=170)
pdf.add_text(sezioni['raccomandazioni'])

pdf.add_page()
pdf.chapter_title('11.1 Proiezioni 2030', 2)
pdf.add_chart(CHARTS_DIR / '30_proiezioni_2030.png', width=170)

# 12. Nota Metodologica
pdf.add_page()
pdf.chapter_title('12. Nota Metodologica', 2)

pdf.set_font('Helvetica', 'B', 11)
pdf.cell(0, 8, 'Fonti Dati')
pdf.ln()
pdf.set_font('Helvetica', '', 10)
pdf.multi_cell(0, 6, f"""
- Dati ufficiali tesseramento FIGB 2017-2025
- Record totali: {metriche['generali']['tesseramenti_totali']:,}
- Giocatori unici: {metriche['generali']['giocatori_unici']:,}
- Periodo: {metriche['generali']['periodo']}
""")

pdf.ln(5)
pdf.set_font('Helvetica', 'B', 11)
pdf.cell(0, 8, 'Metodologia')
pdf.ln()
pdf.set_font('Helvetica', '', 10)
pdf.multi_cell(0, 6, f"""
- Analisi statistica: Python 3.12 (pandas, numpy, matplotlib, seaborn)
- Generazione testo: Google Gemini AI (gemini-2.0-flash)
- Generazione PDF: FPDF2
- Grafici generati: {metriche['grafici_generati']}
""")

pdf.ln(5)
pdf.set_font('Helvetica', 'B', 11)
pdf.cell(0, 8, 'Definizioni Chiave')
pdf.ln()
pdf.set_font('Helvetica', '', 10)
pdf.multi_cell(0, 6, """
- Retention Rate: % tesserati anno N-1 che si ritesserano anno N
- Scuola Bridge Progressione: Rimane in SB (esito positivo)
- Scuola Bridge Conversione: Passa ad altra tessera (completamento)
- Giocatore Selettivo: >50% punti da campionati
- LTV: Valore economico atteso nel ciclo vita residuo
""")

# Footer finale
pdf.ln(20)
pdf.set_font('Helvetica', 'I', 9)
pdf.set_text_color(100, 100, 100)
pdf.cell(0, 8, f"Report generato il {datetime.now().strftime('%d/%m/%Y alle %H:%M')}", align='C')
pdf.ln()
pdf.cell(0, 8, "FIGB - Federazione Italiana Gioco Bridge", align='C')

# ============================================================================
# SALVATAGGIO
# ============================================================================
print("\n[4/5] Salvataggio PDF...")

pdf_path = OUTPUT_DIR / f'Relazione_Completa_FIGB_2017_2025_{datetime.now().strftime("%Y%m%d")}.pdf'
pdf.output(str(pdf_path))

print(f"   PDF salvato: {pdf_path}")

# ============================================================================
# RIEPILOGO
# ============================================================================
print("\n" + "=" * 100)
print("REPORT PDF COMPLETATO")
print("=" * 100)
print(f"\nFile generato: {pdf_path}")
print(f"Pagine: {pdf.page_no()}")
print(f"Grafici integrati: {metriche['grafici_generati']}")
print(f"Sezioni: 12")
print("=" * 100)
