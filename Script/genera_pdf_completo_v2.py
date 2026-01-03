#!/usr/bin/env python3
"""
GENERATORE REPORT PDF COMPLETO FIGB 2017-2025
Con analisi churn approfondita integrata
"""

import pandas as pd
import json
from pathlib import Path
from datetime import datetime
from fpdf import FPDF
import requests

# API Gemini
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', '')
GEMINI_MODEL = 'gemini-2.5-flash-preview-05-20'

def call_gemini(prompt):
    """Chiama Gemini API via REST"""
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}"
    response = requests.post(url, json={
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.7, "maxOutputTokens": 2000}
    })
    if response.status_code == 200:
        return response.json()['candidates'][0]['content']['parts'][0]['text']
    else:
        return f"Errore API: {response.status_code}"

# Directory
BASE_DIR = Path(__file__).parent.parent
OUTPUT_DIR = BASE_DIR / 'output'
CHARTS_DIR = OUTPUT_DIR / 'charts_v2'
CHARTS_CHURN = OUTPUT_DIR / 'charts_churn'
RESULTS_DIR = OUTPUT_DIR / 'results_v2'
RESULTS_CHURN = OUTPUT_DIR / 'results_churn'

print("=" * 100)
print("GENERAZIONE REPORT PDF COMPLETO FIGB 2017-2025")
print("Con analisi churn approfondita integrata")
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
            self.set_text_color(30, 58, 95)
            self.ln(10)
        else:
            self.set_font('Helvetica', 'B', 14)
            self.set_text_color(46, 89, 132)
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
        text_clean = text.encode('latin-1', 'replace').decode('latin-1')
        self.multi_cell(0, 6, text_clean)
        self.ln(3)

    def add_metric_box(self, value, label, x, y, w=40):
        self.set_xy(x, y)
        self.set_fill_color(248, 249, 250)
        self.set_draw_color(74, 144, 217)
        self.rect(x, y, w, 25, 'DF')
        self.line(x, y, x, y + 25)
        self.line(x + 0.5, y, x + 0.5, y + 25)
        self.line(x + 1, y, x + 1, y + 25)
        self.set_xy(x + 3, y + 3)
        self.set_font('Helvetica', 'B', 14)
        self.set_text_color(30, 58, 95)
        self.cell(w - 6, 10, str(value), align='C')
        self.set_xy(x + 3, y + 14)
        self.set_font('Helvetica', '', 7)
        self.set_text_color(100, 100, 100)
        label_clean = label.upper().encode('latin-1', 'replace').decode('latin-1')
        self.cell(w - 6, 8, label_clean, align='C')

    def add_chart(self, img_path, width=180):
        if Path(img_path).exists():
            self.ln(5)
            x = (210 - width) / 2
            self.image(str(img_path), x=x, w=width)
            self.ln(5)
        else:
            self.set_font('Helvetica', 'I', 10)
            self.set_text_color(150, 150, 150)
            self.cell(0, 10, f'[Grafico non disponibile: {img_path.name}]', align='C')
            self.ln()

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
        self.rect(10, start_y, 190, 22, 'DF')
        self.line(10, start_y, 10, start_y + 22)
        self.line(10.5, start_y, 10.5, start_y + 22)
        self.line(11, start_y, 11, start_y + 22)
        self.set_xy(15, start_y + 4)
        self.set_font('Helvetica', '', 9)
        self.set_text_color(50, 50, 50)
        text_clean = text.encode('latin-1', 'replace').decode('latin-1')
        self.multi_cell(180, 5, text_clean)
        self.ln(5)

    def add_table(self, headers, rows, col_widths=None):
        if col_widths is None:
            col_widths = [190 / len(headers)] * len(headers)
        self.set_font('Helvetica', 'B', 9)
        self.set_fill_color(30, 58, 95)
        self.set_text_color(255, 255, 255)
        for i, h in enumerate(headers):
            self.cell(col_widths[i], 8, str(h), border=1, fill=True, align='C')
        self.ln()
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
# CARICAMENTO DATI
# ============================================================================
print("\n[1/6] Caricamento dati...")

with open(RESULTS_DIR / 'metriche_complete_v2.json', 'r', encoding='utf-8') as f:
    metriche = json.load(f)

# CSV base
regioni = pd.read_csv(RESULTS_DIR / 'regioni_summary.csv')
circoli_v = pd.read_csv(RESULTS_DIR / 'circoli_virtuosi.csv')
circoli_c = pd.read_csv(RESULTS_DIR / 'circoli_critici.csv')
profili = pd.read_csv(RESULTS_DIR / 'profili_giocatori.csv')
ltv = pd.read_csv(RESULTS_DIR / 'lifetime_value.csv')
selettivi = pd.read_csv(RESULTS_DIR / 'selettivi_per_categoria.csv')

# CSV churn approfondito
cluster_churn = pd.read_csv(RESULTS_CHURN / 'cluster_churn_profili.csv')
confronto_churn = pd.read_csv(RESULTS_CHURN / 'confronto_churned_vs_attivi.csv')
soglie_churn = pd.read_csv(RESULTS_CHURN / 'soglie_critiche_churn.csv')
campionati_cat = pd.read_csv(RESULTS_CHURN / 'campionati_per_categoria.csv')
churn_macro = pd.read_csv(RESULTS_CHURN / 'churn_per_macroregione.csv')

print(f"   Dati caricati")

# ============================================================================
# GENERAZIONE TESTO CON GEMINI
# ============================================================================
print("\n[2/6] Generazione analisi con Gemini AI...")

# Contesto dati arricchito
contesto = f"""
DATI TESSERAMENTO FIGB 2017-2025:
- Tesserati 2025: {metriche['anno_2025']['tesserati']:,}
- Eta media: {metriche['anno_2025']['eta_media']} anni
- Under 40: {metriche['anno_2025']['under_40_pct']}%
- Over 70: {metriche['anno_2025']['over_70_pct']}%

CHURN PROFONDO:
- Giocatori churned totali: 17,433 (56.1%)
- Recuperabili: 14,426 (82.8% del churn)
- Priorita alta: 4,462 giocatori attivi persi

SOGLIE CRITICHE:
- < 10 gare/anno: churn 78% (vs 42%)
- < 3 anni presenza: churn 78% (vs 36%)
- Nessuna progressione: churn 66% (vs 36%)

MACROREGIONI:
- Nord-Ovest: 58.7% churn (peggiore)
- Nord-Est: 50.5% churn (migliore)
"""

sezioni = {}

prompt_sommario = f"""
Scrivi un SOMMARIO ESECUTIVO (max 300 parole) per il report FIGB 2017-2025.
{contesto}
Focus su: criticita demografiche, analisi churn approfondita, opportunita di recupero.
Stile formale. NO markdown.
"""
sezioni['sommario'] = call_gemini(prompt_sommario)
print("   - Sommario esecutivo")

prompt_churn = f"""
Scrivi l'ANALISI APPROFONDITA DEL CHURN (max 350 parole).
{contesto}

CLUSTER IDENTIFICATI:
1. Giocatori occasionali (57.6%) - media recuperabilita
2. Giocatori attivi persi (21.1%) - ALTA recuperabilita
3. Abbandono precoce (16.5%) - mai ingaggiati
4. Super-attivi persi (4.7%) - >100 gare/anno persi
5. Anziani/deceduti - non recuperabili

FATTORI CRITICI:
- Chi fa campionati ha 20% meno churn
- Chi fa >20 gare/anno ha 30% meno churn
- I primi 3 anni sono critici

Spiega perche smettono e come recuperarli. NO markdown.
"""
sezioni['churn_profondo'] = call_gemini(prompt_churn)
print("   - Analisi churn profonda")

prompt_categorie = f"""
Scrivi l'ANALISI DELLA PIRAMIDE CATEGORIE (max 250 parole).
Struttura: NC -> Quarta (F/Q/C/P) -> Terza -> Seconda -> Prima -> Honor (J/Q/K/A) -> Master (MS/LM/GM)

PROBLEMA: La piramide NON e pulita!
- Terza Fiori ha 8,908 giocatori - piu di tutte le Quarte
- Solo il 25% sale di categoria ogni anno
- Le transizioni tra sottocategorie sono irregolari

Analizza le anomalie e proponi soluzioni. NO markdown.
"""
sezioni['categorie'] = call_gemini(prompt_categorie)
print("   - Analisi categorie")

prompt_raccomandazioni = f"""
Scrivi 8 RACCOMANDAZIONI STRATEGICHE PRIORITIZZATE (max 400 parole).
{contesto}

PRIORITA:
1. Recuperare i 4,462 giocatori attivi persi (priorita ALTA)
2. Migliorare onboarding primi 3 anni
3. Incentivare partecipazione campionati
4. Ridurre churn Nord-Ovest
5. Programma mentoring per nuovi
6. Eventi sociali regionali

Per ogni raccomandazione: azione, KPI, impatto atteso.
NO markdown, numera le raccomandazioni.
"""
sezioni['raccomandazioni'] = call_gemini(prompt_raccomandazioni)
print("   - Raccomandazioni")

# ============================================================================
# CREAZIONE PDF
# ============================================================================
print("\n[3/6] Creazione PDF...")

pdf = ReportPDF()
pdf.set_title('Relazione Completa FIGB 2017-2025')
pdf.set_author('FIGB - Analisi Automatica')

# === COPERTINA ===
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
pdf.ln(10)
pdf.add_chart(CHARTS_DIR / '01_trend_tesseramenti.png', width=160)
pdf.ln(15)
pdf.set_font('Helvetica', '', 11)
pdf.set_text_color(100, 100, 100)
pdf.cell(0, 8, f"Data: {datetime.now().strftime('%d %B %Y')}", align='C')
pdf.ln(6)
pdf.cell(0, 8, "Analisi approfondita churn e pattern di gioco", align='C')

# === INDICE ===
pdf.add_page()
pdf.chapter_title('INDICE', 1)
pdf.set_font('Helvetica', '', 11)
indice = [
    "PARTE I - PANORAMICA GENERALE",
    "   1. Sommario Esecutivo",
    "   2. Metriche Chiave 2025",
    "   3. Analisi Temporale",
    "PARTE II - ANALISI APPROFONDITE",
    "   4. Piramide Categorie (con sottocategorie)",
    "   5. Analisi Circoli",
    "   6. Analisi Regionale e Macroregionale",
    "   7. Giocatori Selettivi",
    "PARTE III - ANALISI CHURN PROFONDA",
    "   8. Clustering Giocatori Churned",
    "   9. Perche Smettono vs Perche Restano",
    "   10. Soglie Critiche e Fattori di Retention",
    "   11. Lifetime Value",
    "PARTE IV - CONCLUSIONI",
    "   12. Raccomandazioni Strategiche",
    "   13. Piano di Azione Anti-Churn",
]
for item in indice:
    if item.startswith("PARTE"):
        pdf.set_font('Helvetica', 'B', 11)
    else:
        pdf.set_font('Helvetica', '', 11)
    pdf.cell(0, 8, item)
    pdf.ln()

# === PARTE I ===
pdf.add_page()
pdf.chapter_title('PARTE I - PANORAMICA GENERALE', 1)

# 1. Sommario
pdf.chapter_title('1. Sommario Esecutivo', 2)
y = pdf.get_y()
pdf.add_metric_box(f"{metriche['anno_2025']['tesserati']:,}", 'Tesserati 2025', 12, y, 42)
pdf.add_metric_box(f"{metriche['anno_2025']['circoli_attivi']}", 'Circoli', 58, y, 42)
pdf.add_metric_box("56.1%", 'Churn Storico', 104, y, 42)
pdf.add_metric_box("14,426", 'Recuperabili', 150, y, 42)
pdf.ln(32)
pdf.add_text(sezioni['sommario'])

# 2. Metriche Chiave
pdf.add_page()
pdf.chapter_title('2. Metriche Chiave 2025', 2)
y = pdf.get_y()
pdf.add_metric_box(f"{metriche['anno_2025']['under_40_pct']}%", 'Under 40', 12, y, 42)
pdf.add_metric_box(f"{metriche['anno_2025']['over_70_pct']}%", 'Over 70', 58, y, 42)
pdf.add_metric_box(f"{metriche['anno_2025']['eta_media']}", 'Eta Media', 104, y, 42)
pdf.add_metric_box(f"{metriche['anno_2025']['agonisti']}", 'Agonisti', 150, y, 42)
pdf.ln(35)
pdf.add_chart(CHARTS_DIR / '02_piramide_eta.png', width=175)
pdf.add_highlight(
    f"CRITICITA: Solo {metriche['anno_2025']['under_40_pct']}% under 40, mentre {metriche['anno_2025']['over_70_pct']}% over 70. "
    "Urgente attrarre giovani per sostenibilita.",
    'danger'
)

# 3. Analisi Temporale
pdf.add_page()
pdf.chapter_title('3. Analisi Temporale 2017-2025', 2)
pdf.add_chart(CHARTS_DIR / '01_trend_tesseramenti.png', width=175)
pdf.add_chart(CHARTS_DIR / '26_confronto_covid.png', width=165)
pdf.add_highlight(
    "RECOVERY POST-COVID: Da 11,655 (2021) a 13,662 (2025) = +17.2%. "
    "Trend positivo ma ancora sotto i livelli pre-pandemia (19,800 nel 2018).",
    'success'
)

# === PARTE II ===
pdf.add_page()
pdf.chapter_title('PARTE II - ANALISI APPROFONDITE', 1)

# 4. Piramide Categorie
pdf.chapter_title('4. Piramide Categorie con Sottocategorie', 2)
pdf.add_chart(CHARTS_CHURN / '03_piramide_dettagliata.png', width=180)
pdf.add_text(sezioni['categorie'])

pdf.add_page()
pdf.chapter_title('4.1 Matrice Transizioni Sottocategorie', 2)
pdf.add_chart(CHARTS_CHURN / '04_matrice_transizioni_dettagliata.png', width=180)
pdf.add_highlight(
    "ANOMALIA PIRAMIDE: Terza Fiori (3F) ha 8,908 giocatori - piu di tutte le Quarte insieme! "
    "Le transizioni tra sottocategorie non seguono un pattern logico.",
    'warning'
)

# 5. Circoli
pdf.add_page()
pdf.chapter_title('5. Analisi dei Circoli', 2)
pdf.add_chart(CHARTS_DIR / '09_circoli_virtuosi_critici.png', width=180)

pdf.chapter_title('5.1 Circoli Virtuosi (Top 10)', 2)
headers = ['Circolo', 'Regione', 'Allievi', 'Successo']
rows = [[r['NomeCircolo'][:28], r['Regione'][:10], r['AllievoSB'], f"{r['TassoSuccesso']:.0f}%"]
        for _, r in circoli_v.head(10).iterrows()]
pdf.add_table(headers, rows, [85, 35, 30, 30])

pdf.chapter_title('5.2 Circoli Critici (Top 10)', 2)
rows = [[r['NomeCircolo'][:28], r['Regione'][:10], r['AllievoSB'], f"{r['TassoChurn']:.0f}%"]
        for _, r in circoli_c.head(10).iterrows()]
headers = ['Circolo', 'Regione', 'Allievi', 'Churn']
pdf.add_table(headers, rows, [85, 35, 30, 30])

# 6. Analisi Regionale
pdf.add_page()
pdf.chapter_title('6. Analisi Regionale e Macroregionale', 2)
pdf.add_chart(CHARTS_DIR / '07_top_regioni.png', width=175)

pdf.chapter_title('6.1 Churn per Macroregione', 2)
pdf.add_chart(CHARTS_CHURN / '05_pattern_macroregionali.png', width=180)

headers = ['Macroregione', 'Giocatori', 'Churn Rate', 'Gare Medie']
rows = [[r['Macroregione'], f"{r['Giocatori']:,}", f"{r['ChurnRate']:.1f}%", f"{r['GareMedie']:.1f}"]
        for _, r in churn_macro.iterrows() if r['Macroregione'] not in ['Altro', 'Nazionale']]
pdf.add_table(headers, rows, [50, 45, 45, 45])

pdf.add_highlight(
    "DIFFERENZA TERRITORIALE: Nord-Est ha il churn piu basso (50.5%) e fa piu gare (34/anno). "
    "Nord-Ovest ha il churn piu alto (58.7%) nonostante i numeri maggiori.",
    'info'
)

# 7. Giocatori Selettivi
pdf.add_page()
pdf.chapter_title('7. Giocatori Selettivi: Campionati vs Tornei', 2)
pdf.add_chart(CHARTS_DIR / '10_profili_giocatori.png', width=175)

headers = ['Profilo', 'Giocatori', '%', 'Gare Medie']
rows = [[r['Profilo'], f"{r['Giocatori']:,}", f"{r['%']:.1f}%", f"{r['GareMedie']:.1f}"]
        for _, r in profili.iterrows()]
pdf.add_table(headers, rows, [60, 45, 40, 45])

pdf.add_highlight(
    "CHI FA CAMPIONATI RESTA: I giocatori che partecipano ai campionati hanno "
    "churn 20% inferiore. Incentivare la partecipazione competitiva.",
    'success'
)

# === PARTE III - CHURN PROFONDO ===
pdf.add_page()
pdf.chapter_title('PARTE III - ANALISI CHURN PROFONDA', 1)

# 8. Clustering
pdf.chapter_title('8. Clustering Giocatori Churned', 2)
pdf.add_chart(CHARTS_CHURN / '01_clustering_churn.png', width=180)

y = pdf.get_y()
pdf.add_metric_box("17,433", 'Tot. Churned', 12, y, 42)
pdf.add_metric_box("14,426", 'Recuperabili', 58, y, 42)
pdf.add_metric_box("4,462", 'Priorita Alta', 104, y, 42)
pdf.add_metric_box("82.8%", '% Recuper.', 150, y, 42)
pdf.ln(35)

pdf.chapter_title('8.1 Profili Cluster', 2)
# Calcola recuperabilita
def get_recup(nome):
    if 'recuperabil' in nome.lower() or 'attivi persi' in nome.lower():
        return 'ALTA'
    elif 'occasional' in nome.lower() or 'Scuola' in nome:
        return 'MEDIA'
    else:
        return 'BASSA'

headers = ['Cluster', 'Giocatori', '%', 'Recuper.']
rows = [[r['NomeCluster'][:30], f"{r['Numerosita']:,}", f"{r['Percentuale']:.1f}%", get_recup(r['NomeCluster'])]
        for _, r in cluster_churn.iterrows()]
pdf.add_table(headers, rows, [80, 35, 30, 40])

# 9. Confronto
pdf.add_page()
pdf.chapter_title('9. Perche Smettono vs Perche Restano', 2)
pdf.add_chart(CHARTS_CHURN / '02_confronto_churned_attivi.png', width=180)
pdf.add_text(sezioni['churn_profondo'])

# 10. Soglie Critiche
pdf.add_page()
pdf.chapter_title('10. Soglie Critiche e Fattori di Retention', 2)
pdf.add_chart(CHARTS_CHURN / '06_fattori_retention.png', width=180)

pdf.chapter_title('10.1 Soglie Critiche Identificate', 2)
headers = ['Fattore', 'Soglia', 'Churn Sotto', 'Churn Sopra', 'Diff.']
rows = [[r['Fattore'], r['Soglia'], f"{r['ChurnSotto']:.1f}%", f"{r['ChurnSopra']:.1f}%", f"+{r['Differenza']:.1f}%"]
        for _, r in soglie_churn.head(8).iterrows()]
pdf.add_table(headers, rows, [40, 30, 35, 35, 35])

pdf.add_highlight(
    "SOGLIE CRITICHE: Chi fa meno di 10 gare/anno ha churn 78% (vs 42%). "
    "I primi 3 anni sono decisivi: churn 78% vs 36% dopo.",
    'danger'
)

# 11. LTV
pdf.add_page()
pdf.chapter_title('11. Lifetime Value per Segmento', 2)
pdf.add_chart(CHARTS_DIR / '14_ltv_per_eta.png', width=175)

headers = ['Fascia Eta', 'Giocatori', 'LTV', 'Valore Totale']
rows = [[r['FasciaEta'], f"{r['Giocatori']:,}", f"EUR {r['LTV']:,.0f}", f"EUR {r['ValoreTotale']:,.0f}"]
        for _, r in ltv.iterrows()]
pdf.add_table(headers, rows, [40, 40, 50, 55])

pdf.add_highlight(
    f"VALORE TOTALE BASE TESSERATI: EUR {metriche['ltv']['totale_milioni']}M. "
    "Segmento 60-70 ha miglior equilibrio tra valore attuale e anni residui.",
    'success'
)

# === PARTE IV - CONCLUSIONI ===
pdf.add_page()
pdf.chapter_title('PARTE IV - CONCLUSIONI', 1)

# 12. Raccomandazioni
pdf.chapter_title('12. Raccomandazioni Strategiche', 2)
pdf.add_chart(CHARTS_DIR / '29_matrice_priorita.png', width=175)
pdf.add_text(sezioni['raccomandazioni'])

# 13. Piano Anti-Churn
pdf.add_page()
pdf.chapter_title('13. Piano di Azione Anti-Churn', 2)
pdf.add_chart(CHARTS_CHURN / '07_raccomandazioni_actionable.png', width=180)

pdf.set_font('Helvetica', 'B', 11)
pdf.cell(0, 8, 'AZIONI IMMEDIATE (0-3 mesi):')
pdf.ln()
pdf.set_font('Helvetica', '', 10)
pdf.multi_cell(0, 6, """
- Contattare i 4,462 giocatori attivi persi (lista disponibile in CSV)
- Offerta "ritorno" con sconto tessera 30%
- Evento di benvenuto per chi rientra
""")

pdf.set_font('Helvetica', 'B', 11)
pdf.cell(0, 8, 'AZIONI BREVE TERMINE (3-6 mesi):')
pdf.ln()
pdf.set_font('Helvetica', '', 10)
pdf.multi_cell(0, 6, """
- Programma mentoring per nuovi iscritti (primi 3 anni critici)
- Tornei "bridge facile" per principianti
- Target: almeno 10 gare nel primo anno
""")

pdf.set_font('Helvetica', 'B', 11)
pdf.cell(0, 8, 'KPI DA MONITORARE:')
pdf.ln()
pdf.set_font('Helvetica', '', 10)
pdf.multi_cell(0, 6, """
- Tasso recupero priorita alta (target: 15%)
- Retention primo anno (target: 70%)
- Gare medie nuovi iscritti (target: 15+)
- Partecipazione campionati (target: +10%)
""")

# Nota metodologica
pdf.add_page()
pdf.chapter_title('Nota Metodologica', 2)
pdf.set_font('Helvetica', '', 10)
pdf.multi_cell(0, 6, f"""
FONTI DATI:
- Dati ufficiali tesseramento FIGB 2017-2025
- Record totali: {metriche['generali']['tesseramenti_totali']:,}
- Giocatori unici: {metriche['generali']['giocatori_unici']:,}

METODOLOGIA:
- Clustering K-Means per segmentazione churn
- Analisi correlazioni per fattori retention
- Analisi transizioni per progressione categorie

STRUMENTI:
- Python 3.12 (pandas, scikit-learn, matplotlib)
- Google Gemini AI per generazione testo
- FPDF2 per generazione PDF

GRAFICI GENERATI: 37 (30 base + 7 churn approfondito)
""")

# Footer
pdf.ln(20)
pdf.set_font('Helvetica', 'I', 9)
pdf.set_text_color(100, 100, 100)
pdf.cell(0, 8, f"Report generato il {datetime.now().strftime('%d/%m/%Y alle %H:%M')}", align='C')
pdf.ln()
pdf.cell(0, 8, "FIGB - Federazione Italiana Gioco Bridge", align='C')

# ============================================================================
# SALVATAGGIO
# ============================================================================
print("\n[4/6] Salvataggio PDF...")

pdf_path = OUTPUT_DIR / f'Relazione_Completa_FIGB_2017_2025_{datetime.now().strftime("%Y%m%d")}.pdf'
pdf.output(str(pdf_path))

print(f"   PDF salvato: {pdf_path}")
print(f"   Pagine: {pdf.page_no()}")

print("\n" + "=" * 100)
print("REPORT PDF COMPLETATO")
print("=" * 100)
print(f"File: {pdf_path}")
print(f"Pagine: {pdf.page_no()}")
print("=" * 100)
