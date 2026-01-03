#!/usr/bin/env python3
"""
GENERATORE REPORT PDF FINALE FIGB 2017-2025
Versione corretta con tutte le analisi
"""

import pandas as pd
import json
from pathlib import Path
from datetime import datetime
from fpdf import FPDF
import requests

# API Gemini - modello corretto
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', '')
GEMINI_MODEL = 'gemini-3-flash-preview'  # Ultimo modello

def call_gemini(prompt):
    """Chiama Gemini API via REST"""
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}"
    try:
        response = requests.post(url, json={
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": 0.7, "maxOutputTokens": 2000}
        }, timeout=30)
        if response.status_code == 200:
            return response.json()['candidates'][0]['content']['parts'][0]['text']
        else:
            return f"[Testo non disponibile - API error {response.status_code}]"
    except Exception as e:
        return f"[Testo non disponibile - {str(e)}]"

# Directory
BASE_DIR = Path(__file__).parent.parent
OUTPUT_DIR = BASE_DIR / 'output'
CHARTS_DIR = OUTPUT_DIR / 'charts_v2'
CHARTS_CHURN = OUTPUT_DIR / 'charts_churn'
CHARTS_INNOV = OUTPUT_DIR / 'charts_innovativi'
CHARTS_PRED = OUTPUT_DIR / 'charts_predittivi'
RESULTS_DIR = OUTPUT_DIR / 'results_v2'
RESULTS_CHURN = OUTPUT_DIR / 'results_churn'
RESULTS_INNOV = OUTPUT_DIR / 'results_innovativi'
RESULTS_PRED = OUTPUT_DIR / 'results_predittivi'

print("=" * 100)
print("GENERAZIONE REPORT PDF FINALE FIGB 2017-2025")
print("=" * 100)

# ============================================================================
# CLASSE PDF
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
        elif level == 2:
            self.set_font('Helvetica', 'B', 14)
            self.set_text_color(46, 89, 132)
            self.ln(5)
        else:
            self.set_font('Helvetica', 'B', 12)
            self.set_text_color(74, 144, 217)
            self.ln(3)
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

    def add_metric_box(self, value, label, x, y, w=45):
        self.set_xy(x, y)
        self.set_fill_color(248, 249, 250)
        self.set_draw_color(74, 144, 217)
        self.rect(x, y, w, 25, 'DF')
        self.line(x, y, x, y + 25)
        self.line(x + 0.5, y, x + 0.5, y + 25)
        self.set_xy(x + 2, y + 3)
        self.set_font('Helvetica', 'B', 13)
        self.set_text_color(30, 58, 95)
        self.cell(w - 4, 10, str(value), align='C')
        self.set_xy(x + 2, y + 14)
        self.set_font('Helvetica', '', 7)
        self.set_text_color(100, 100, 100)
        label_clean = label.upper().encode('latin-1', 'replace').decode('latin-1')
        self.cell(w - 4, 8, label_clean, align='C')

    def add_chart(self, img_path, width=180, caption=None):
        if Path(img_path).exists():
            self.ln(3)
            x = (210 - width) / 2
            self.image(str(img_path), x=x, w=width)
            if caption:
                self.set_font('Helvetica', 'I', 8)
                self.set_text_color(100, 100, 100)
                self.cell(0, 6, caption, align='C')
            self.ln(5)
        else:
            self.set_font('Helvetica', 'I', 10)
            self.set_text_color(200, 100, 100)
            self.cell(0, 10, f'[Grafico: {Path(img_path).name}]', align='C')
            self.ln()

    def add_highlight(self, text, color='warning'):
        colors = {'warning': (255, 243, 205), 'danger': (248, 215, 218),
                  'success': (212, 237, 218), 'info': (217, 237, 247)}
        border_colors = {'warning': (255, 193, 7), 'danger': (220, 53, 69),
                         'success': (40, 167, 69), 'info': (23, 162, 184)}
        bg = colors.get(color, colors['info'])
        border = border_colors.get(color, border_colors['info'])
        self.set_fill_color(*bg)
        self.set_draw_color(*border)
        start_y = self.get_y()
        self.rect(10, start_y, 190, 20, 'DF')
        for i in range(3):
            self.line(10 + i*0.5, start_y, 10 + i*0.5, start_y + 20)
        self.set_xy(15, start_y + 3)
        self.set_font('Helvetica', '', 9)
        self.set_text_color(50, 50, 50)
        text_clean = text.encode('latin-1', 'replace').decode('latin-1')
        self.multi_cell(178, 5, text_clean)
        self.ln(3)

    def add_table(self, headers, rows, col_widths=None, row_height=6):
        if col_widths is None:
            col_widths = [190 / len(headers)] * len(headers)
        self.set_font('Helvetica', 'B', 8)
        self.set_fill_color(30, 58, 95)
        self.set_text_color(255, 255, 255)
        for i, h in enumerate(headers):
            self.cell(col_widths[i], 7, str(h), border=1, fill=True, align='C')
        self.ln()
        self.set_font('Helvetica', '', 8)
        self.set_text_color(50, 50, 50)
        for row_idx, row in enumerate(rows):
            self.set_fill_color(248, 249, 250) if row_idx % 2 == 0 else self.set_fill_color(255, 255, 255)
            for i, cell in enumerate(row):
                cell_str = str(cell).encode('latin-1', 'replace').decode('latin-1')
                # Tronca solo se necessario per la larghezza
                max_chars = int(col_widths[i] / 2)  # circa 2pt per carattere
                if len(cell_str) > max_chars:
                    cell_str = cell_str[:max_chars-2] + '..'
                self.cell(col_widths[i], row_height, cell_str, border=1, fill=True, align='C')
            self.ln()
        self.ln(3)

    def add_table_multiline(self, headers, rows, col_widths=None):
        """Tabella con celle multilinea per testi lunghi"""
        if col_widths is None:
            col_widths = [190 / len(headers)] * len(headers)
        # Header
        self.set_font('Helvetica', 'B', 8)
        self.set_fill_color(30, 58, 95)
        self.set_text_color(255, 255, 255)
        for i, h in enumerate(headers):
            self.cell(col_widths[i], 7, str(h), border=1, fill=True, align='C')
        self.ln()
        # Rows
        self.set_font('Helvetica', '', 7)
        self.set_text_color(50, 50, 50)
        for row_idx, row in enumerate(rows):
            self.set_fill_color(248, 249, 250) if row_idx % 2 == 0 else self.set_fill_color(255, 255, 255)
            max_h = 10
            start_y = self.get_y()
            start_x = 10
            for i, cell in enumerate(row):
                cell_str = str(cell).encode('latin-1', 'replace').decode('latin-1')
                self.set_xy(start_x + sum(col_widths[:i]), start_y)
                self.multi_cell(col_widths[i], 5, cell_str, border=1, align='C', fill=True)
                if self.get_y() - start_y > max_h:
                    max_h = self.get_y() - start_y
            self.set_y(start_y + max_h)
        self.ln(3)

# ============================================================================
# CARICAMENTO DATI
# ============================================================================
print("\n[1/5] Caricamento dati...")

with open(RESULTS_DIR / 'metriche_complete_v2.json', 'r', encoding='utf-8') as f:
    metriche = json.load(f)

# CSV base
regioni = pd.read_csv(RESULTS_DIR / 'regioni_summary.csv')
circoli_v = pd.read_csv(RESULTS_DIR / 'circoli_virtuosi.csv')
circoli_c = pd.read_csv(RESULTS_DIR / 'circoli_critici.csv')
profili = pd.read_csv(RESULTS_DIR / 'profili_giocatori.csv')
ltv = pd.read_csv(RESULTS_DIR / 'lifetime_value.csv')
sb_analisi = pd.read_csv(RESULTS_DIR / 'scuola_bridge_analisi.csv') if (RESULTS_DIR / 'scuola_bridge_analisi.csv').exists() else None

# CSV churn
cluster_churn = pd.read_csv(RESULTS_CHURN / 'cluster_churn_profili.csv')
confronto = pd.read_csv(RESULTS_CHURN / 'confronto_churned_vs_attivi.csv')
soglie = pd.read_csv(RESULTS_CHURN / 'soglie_critiche_churn.csv')
churn_macro = pd.read_csv(RESULTS_CHURN / 'churn_per_macroregione.csv')

# Filtra macroregioni (escludi Altro e Nazionale)
churn_macro_filtered = churn_macro[~churn_macro['Macroregione'].isin(['Altro', 'Nazionale', ''])]

# CSV innovativi
if RESULTS_INNOV.exists():
    curve_sopravv = pd.read_csv(RESULTS_INNOV / 'curve_sopravvivenza.csv') if (RESULTS_INNOV / 'curve_sopravvivenza.csv').exists() else None
    # Usa la nuova analisi rischio corretta
    if (RESULTS_INNOV / 'giocatori_rischio_REALE.csv').exists():
        attivi_rischio = pd.read_csv(RESULTS_INNOV / 'giocatori_rischio_REALE.csv')
    elif (RESULTS_INNOV / 'giocatori_attivi_a_rischio.csv').exists():
        attivi_rischio = pd.read_csv(RESULTS_INNOV / 'giocatori_attivi_a_rischio.csv')
    else:
        attivi_rischio = None
    circoli_retention = pd.read_csv(RESULTS_INNOV / 'circoli_retention_analysis.csv') if (RESULTS_INNOV / 'circoli_retention_analysis.csv').exists() else None
else:
    curve_sopravv = attivi_rischio = circoli_retention = None

# Dati predittivi
if RESULTS_PRED.exists():
    proiezioni = pd.read_csv(RESULTS_PRED / 'proiezioni_2025_2035.csv') if (RESULTS_PRED / 'proiezioni_2025_2035.csv').exists() else None
    with open(RESULTS_PRED / 'rischi_strutturali.json', 'r') as f:
        rischi_pred = json.load(f)
else:
    proiezioni = None
    rischi_pred = {}

print(f"   Dati caricati")

# ============================================================================
# GENERAZIONE TESTO
# ============================================================================
print("\n[2/5] Generazione testi con Gemini...")

sezioni = {}

sezioni['sommario'] = call_gemini(f"""
Scrivi SOMMARIO ESECUTIVO (max 250 parole) report FIGB 2017-2025.
Dati: {metriche['anno_2025']['tesserati']} tesserati, {metriche['anno_2025']['eta_media']} anni media,
{metriche['anno_2025']['under_40_pct']}% under 40, 56% churn storico, 14,426 recuperabili.
Stile formale. NO markdown.
""")
print("   - Sommario")

sezioni['scuola_bridge'] = call_gemini(f"""
Scrivi ANALISI SCUOLA BRIDGE (max 250 parole).
Successo: {metriche['scuola_bridge']['tasso_successo_medio']}%
Conversione: {metriche['scuola_bridge']['tasso_conversione_medio']}%
Churn: {metriche['scuola_bridge']['tasso_churn_medio']}%
Correlazione gare-retention: {metriche['scuola_bridge']['correlazione_gare_retention']}

DEFINIZIONI CORRETTE:
- Rimanere in SB = POSITIVO (corso triennale)
- Passare altra tessera = POSITIVO (completamento)
- Non ritesserarsi = NEGATIVO (churn reale)

Spiega cosa mantiene allievi e cosa li fa andare via. NO markdown.
""")
print("   - Scuola Bridge")

sezioni['churn'] = call_gemini("""
Scrivi ANALISI CHURN PROFONDA (max 300 parole).
CLUSTER:
1. Occasionali (57.6%) - media recuperabilita
2. Attivi persi (21.1%) - ALTA recuperabilita
3. Abbandono precoce (16.5%) - mai ingaggiati

SOGLIE CRITICHE:
- <10 gare/anno: churn 78%
- <3 anni presenza: churn 78%
- No progressione categoria: churn 66%

SPIEGA PCA: Principal Component Analysis riduce le variabili
(eta, gare, anni presenza, etc) a 2 dimensioni (PC1, PC2) per visualizzare
i cluster. PC1 spiega la maggior varianza dei dati.

NO markdown.
""")
print("   - Churn")

sezioni['raccomandazioni'] = call_gemini("""
Scrivi 6 RACCOMANDAZIONI STRATEGICHE prioritizzate (max 350 parole).
1. Recuperare 4,462 giocatori attivi persi
2. Onboarding primi 3 anni critico
3. Incentivare campionati (20% meno churn)
4. Target minimo 10 gare primo anno
5. Programma mentoring
6. Eventi regionali

Per ogni: azione, KPI, impatto. NO markdown, numera.
""")
print("   - Raccomandazioni")

sezioni['survival'] = call_gemini("""
Scrivi ANALISI CURVE SOPRAVVIVENZA (max 200 parole).
Dati: 50% abbandona entro anno 3, 70% entro anno 5.
Giovani (<40) sopravvivono MENO di anziani!
Spiega cosa significa per la retention. NO markdown.
""")
print("   - Survival curves")

sezioni['engagement'] = call_gemini("""
Scrivi ANALISI RISCHIO CHURN (max 200 parole).
Sistema predittivo identifica 2,648 ATTIVI A RISCHIO REALE.
Criteri: chi gioca POCO (<10 gare) nei primi 2 anni = rischio.
Chi gioca 20+ gare/anno = rischio NULLO (non molleranno mai).
Spiega utilita per intervento proattivo. NO markdown.
""")
print("   - Rischio churn")

sezioni['predittivo'] = call_gemini(f"""
Scrivi ANALISI MODELLO PREDITTIVO (max 250 parole).
Proiezione 2025-2035:
- Tesserati 2025: {rischi_pred.get('tesserati_2025', 13661)}
- Tesserati 2035: {rischi_pred.get('tesserati_2035', 15404)}
- Eta media 2025: {rischi_pred.get('eta_media_2025', 71)} anni
- Eta media 2035: {rischi_pred.get('eta_media_2035', 69)} anni
- Reclutamento necessario: {rischi_pred.get('reclutamento_breakeven', 1200)}/anno
Considerati: invecchiamento, mortalita attuariale, churn per eta/anzianita.
Spiega implicazioni strategiche. NO markdown.
""")
print("   - Modello predittivo")

sezioni['abstract'] = call_gemini(f"""
Scrivi ABSTRACT ESECUTIVO (max 400 parole) per report FIGB.
DATI CHIAVE:
- Tesserati 2025: {metriche['anno_2025']['tesserati']}
- Eta media: {metriche['anno_2025']['eta_media']} anni
- Under 40: solo {metriche['anno_2025']['under_40_pct']}%
- Churn storico: 56%
- Giocatori recuperabili: 4,462
- Attivi a rischio REALE: 2,648 (di cui 201 urgenti)
- Proiezione 2035: +12.8% tesserati SE si reclutano 1,200+/anno

RISULTATI PRINCIPALI:
1. 50% abbandona entro 3 anni
2. Chi gioca 20+ gare/anno ha rischio NULLO
3. Primi 2 anni sono critici
4. Giovani (<40) sono priorita assoluta
5. Associazioni "hub" hanno +15% retention

RACCOMANDAZIONI TOP 3:
1. Contattare 201 giovani a rischio urgente
2. Programma onboarding primi 2 anni
3. Incentivare 10+ gare primo anno

Scrivi in modo formale ma diretto. NO markdown.
""")
print("   - Abstract")

# ============================================================================
# CREAZIONE PDF
# ============================================================================
print("\n[3/5] Creazione PDF...")

pdf = ReportPDF()
pdf.set_title('Relazione FIGB 2017-2025')

# === COPERTINA ===
pdf.add_page()
pdf.ln(25)
pdf.set_font('Helvetica', 'B', 28)
pdf.set_text_color(30, 58, 95)
pdf.cell(0, 15, 'RELAZIONE ANALISI TESSERAMENTO', align='C')
pdf.ln(12)
pdf.set_font('Helvetica', '', 18)
pdf.set_text_color(100, 100, 100)
pdf.cell(0, 10, 'FEDERAZIONE ITALIANA GIOCO BRIDGE', align='C')
pdf.ln(12)
pdf.set_font('Helvetica', 'B', 24)
pdf.set_text_color(74, 144, 217)
pdf.cell(0, 15, '2017 - 2025', align='C')
pdf.ln(8)
pdf.add_chart(CHARTS_DIR / '01_trend_tesseramenti.png', width=155)
pdf.ln(10)
pdf.set_font('Helvetica', '', 11)
pdf.set_text_color(100, 100, 100)
pdf.cell(0, 7, f"Data: {datetime.now().strftime('%d/%m/%Y')}", align='C')
pdf.ln()
pdf.cell(0, 7, "Analisi statistica + AI (Gemini)", align='C')

# === ABSTRACT ===
pdf.add_page()
pdf.chapter_title('ABSTRACT ESECUTIVO', 1)

# Box metriche chiave
y = pdf.get_y()
pdf.add_metric_box(f"{metriche['anno_2025']['tesserati']:,}", 'Tesserati 2025', 10, y)
pdf.add_metric_box(f"{metriche['anno_2025']['eta_media']}", 'Eta Media', 58, y)
pdf.add_metric_box("2,648", 'A Rischio', 106, y)
pdf.add_metric_box("+12.8%", 'Proiez. 2035', 154, y)
pdf.ln(35)

pdf.add_text(sezioni['abstract'])

pdf.ln(5)
pdf.add_highlight("AZIONE IMMEDIATA: Contattare 201 giovani (<30 anni) a rischio critico - Lista in CSV allegato", 'danger')

pdf.ln(3)
pdf.set_font('Helvetica', 'B', 11)
pdf.set_text_color(30, 58, 95)
pdf.cell(0, 8, 'NUMERI CHIAVE:')
pdf.ln()
pdf.set_font('Helvetica', '', 10)
pdf.set_text_color(50, 50, 50)
numeri = f"""
- Tesserati 2025: {metriche['anno_2025']['tesserati']:,} | Under 40: {metriche['anno_2025']['under_40_pct']}% | Over 70: {metriche['anno_2025']['over_70_pct']}%
- Churn storico: 56.1% | Giocatori recuperabili: 4,462 | A rischio reale: 2,648
- Proiezione 2035: {rischi_pred.get('tesserati_2035', 15404):,} tesserati (+12.8% se reclutamento 1,200+/anno)
- Soglia critica: <10 gare/anno nei primi 2 anni = 78% probabilita abbandono
- Best practice: Chi gioca 20+ gare/anno ha rischio NULLO
"""
pdf.multi_cell(0, 5, numeri)

# === INDICE ===
pdf.add_page()
pdf.chapter_title('INDICE', 1)
pdf.set_font('Helvetica', '', 11)
indice = [
    "ABSTRACT ESECUTIVO",
    "",
    "PARTE I - PANORAMICA",
    "   1. Sommario Esecutivo",
    "   2. Metriche Chiave 2025",
    "   3. Trend Temporale",
    "PARTE II - ANALISI DETTAGLIATE",
    "   4. Piramide Categorie e Sottocategorie (2025)",
    "   5. Analisi Scuola Bridge e BAS",
    "   6. Analisi Associazioni (Virtuose vs Critiche)",
    "   7. Analisi Regionale e Macroregionale",
    "   8. Giocatori Selettivi (Campionati vs Tornei)",
    "PARTE III - CHURN PROFONDO",
    "   9. Clustering Giocatori Churned",
    "   10. Perche Smettono vs Perche Restano",
    "   11. Soglie Critiche di Retention",
    "   12. Lifetime Value",
    "PARTE IV - ANALISI INNOVATIVE E PREDITTIVE",
    "   13. Curve di Sopravvivenza (Cohort Analysis)",
    "   14. Giocatori a Rischio Reale (2,648)",
    "   15. Momento Critico: Quando Abbandonano",
    "   16. Effetto Associazione: Network Analysis",
    "   17. Modello Predittivo 2025-2035",
    "PARTE V - AZIONI STRATEGICHE",
    "   18. Raccomandazioni Prioritizzate",
    "   19. Piano Anti-Churn Operativo",
    "   20. Dashboard e KPI",
]
for item in indice:
    pdf.set_font('Helvetica', 'B' if item.startswith("PARTE") else '', 11)
    pdf.cell(0, 7, item)
    pdf.ln()

# === PARTE I ===
pdf.add_page()
pdf.chapter_title('PARTE I - PANORAMICA', 1)

# 1. Sommario
pdf.chapter_title('1. Sommario Esecutivo', 2)
y = pdf.get_y()
pdf.add_metric_box(f"{metriche['anno_2025']['tesserati']:,}", 'Tesserati', 10, y)
pdf.add_metric_box(f"{metriche['anno_2025']['circoli_attivi']}", 'Associazioni', 58, y)
pdf.add_metric_box("56.1%", 'Churn Storico', 106, y)
pdf.add_metric_box("14,426", 'Recuperabili', 154, y)
pdf.ln(32)
pdf.add_text(sezioni['sommario'])

# 2. Metriche
pdf.add_page()
pdf.chapter_title('2. Metriche Chiave 2025', 2)
y = pdf.get_y()
pdf.add_metric_box(f"{metriche['anno_2025']['under_40_pct']}%", 'Under 40', 10, y)
pdf.add_metric_box(f"{metriche['anno_2025']['over_70_pct']}%", 'Over 70', 58, y)
pdf.add_metric_box(f"{metriche['anno_2025']['eta_media']}", 'Eta Media', 106, y)
pdf.add_metric_box(f"{metriche['anno_2025']['agonisti']}", 'Agonisti', 154, y)
pdf.ln(32)
pdf.add_text("Piramide età - SOLO DATI 2025:")
pdf.add_chart(CHARTS_DIR / '02_piramide_eta.png', width=175)
pdf.add_highlight(f"CRITICITA: Solo {metriche['anno_2025']['under_40_pct']}% under 40. "
                  f"Il {metriche['anno_2025']['over_70_pct']}% ha oltre 70 anni.", 'danger')

# 3. Trend
pdf.add_page()
pdf.chapter_title('3. Trend Temporale 2017-2025', 2)
pdf.add_chart(CHARTS_DIR / '01_trend_tesseramenti.png', width=175)
pdf.add_chart(CHARTS_DIR / '26_confronto_covid.png', width=160)
pdf.add_highlight("RECOVERY: Da 11,655 (2021) a 13,662 (2025) = +17%. "
                  "Ancora sotto pre-COVID (19,800).", 'success')

# === PARTE II ===
pdf.add_page()
pdf.chapter_title('PARTE II - ANALISI DETTAGLIATE', 1)

# 4. Categorie
pdf.chapter_title('4. Piramide Categorie e Sottocategorie (2025)', 2)
pdf.add_text("NOTA: Dati riferiti SOLO al 2025")
pdf.add_chart(CHARTS_CHURN / '03_piramide_dettagliata.png', width=180)
pdf.add_text("""La piramide mostra TUTTE le sottocategorie: NC, poi Quarta (Fiori, Quadri, Cuori, Picche),
Terza, Seconda, Prima, Honor (Fante, Dama, Re, Asso), Master (Series, Life, Grand).
ANOMALIA: Terza Fiori (3F) ha molti giocatori - piu di tutte le Quarte insieme!
Solo il 25% sale di categoria ogni anno.""")

pdf.add_page()
pdf.chapter_title('4.1 Matrice Transizioni tra Sottocategorie', 2)
pdf.add_chart(CHARTS_CHURN / '04_matrice_transizioni_dettagliata.png', width=180)
pdf.add_highlight("Le transizioni non seguono pattern logico. Molti rimangono nella stessa sottocategoria.", 'warning')

# 5. Scuola Bridge
pdf.add_page()
pdf.chapter_title('5. Analisi Scuola Bridge', 2)
y = pdf.get_y()
pdf.add_metric_box(f"{metriche['scuola_bridge']['tasso_successo_medio']}%", 'Successo', 10, y)
pdf.add_metric_box(f"{metriche['scuola_bridge']['tasso_conversione_medio']}%", 'Conversione', 58, y)
pdf.add_metric_box(f"{metriche['scuola_bridge']['tasso_churn_medio']}%", 'Churn Reale', 106, y)
pdf.add_metric_box(f"{metriche['scuola_bridge']['correlazione_gare_retention']}", 'Corr. Gare', 154, y)
pdf.ln(32)
pdf.add_chart(CHARTS_DIR / '11_scuola_bridge_esiti.png', width=175)
pdf.add_text(sezioni['scuola_bridge'])

pdf.add_page()
pdf.chapter_title('5.1 Fattori di Successo Scuola Bridge', 2)
pdf.add_chart(CHARTS_DIR / '12_fattori_successo_sb.png', width=175)
pdf.add_highlight(f"BEST PRACTICE: Correlazione gare-retention = {metriche['scuola_bridge']['correlazione_gare_retention']}. "
                  "Chi gioca piu gare rimane di piu!", 'success')

# 5.2 BAS (Bridge a Scuola)
pdf.add_page()
pdf.chapter_title('5.2 BAS - Bridge a Scuola (Istituti Scolastici)', 2)
# Calcola metriche BAS
df_temp = pd.read_csv(OUTPUT_DIR / 'dati_unificati_2017_2025.csv')
bas_df = df_temp[df_temp['MbtDesc'].isin(['Ist.Scolastici', 'Studente CAS', 'CAS Giovanile'])]
bas_2025 = bas_df[bas_df['Anno'] == 2025]['MmbCode'].nunique()
bas_totale = bas_df['MmbCode'].nunique()
bas_peak = bas_df.groupby('Anno')['MmbCode'].nunique().max()

y = pdf.get_y()
pdf.add_metric_box(f"{bas_2025}", 'BAS 2025', 10, y)
pdf.add_metric_box(f"{bas_totale}", 'BAS Totali', 58, y)
pdf.add_metric_box(f"{bas_peak}", 'Picco', 106, y)
pdf.ln(32)

pdf.add_text("""Il programma BAS (Bridge a Scuola) porta il bridge negli istituti scolastici.
Include: Ist.Scolastici, Studente CAS, CAS Giovanile.

TREND STORICO:
- Picco 2018-2019 con 800+ studenti/anno
- Crollo COVID 2020-2021 (quasi azzeramento)
- Lenta ripresa dal 2023

CRITICITA:
- Solo 163 studenti BAS nel 2025 (vs 800+ pre-COVID)
- Programma ancora non ripristinato ai livelli precedenti
- Opportunita di reclutamento giovani non sfruttata

RACCOMANDAZIONE:
Rilanciare il programma BAS e' cruciale per ringiovanire la base tesserati.
Target: tornare a 1,000+ studenti/anno entro 2027.""")

pdf.add_highlight("PRIORITA ALTA: BAS e' la migliore opportunita per reclutare under-20!", 'warning')

# 6. Associazioni
pdf.add_page()
pdf.chapter_title('6. Analisi Associazioni: Virtuose vs Critiche', 2)
# Usa il grafico migliorato se disponibile
if (CHARTS_INNOV / '01_circoli_migliorato.png').exists():
    pdf.add_chart(CHARTS_INNOV / '01_circoli_migliorato.png', width=185)
else:
    pdf.add_chart(CHARTS_DIR / '09_circoli_virtuosi_critici.png', width=185)

pdf.chapter_title('6.1 Top 10 Associazioni Virtuose (alta conversione SB)', 3)
headers = ['Associazione', 'Regione', 'Allievi', 'Successo%']
rows = [[r['NomeCircolo'][:25], r['Regione'][:8], r['AllievoSB'], f"{r['TassoSuccesso']:.0f}%"]
        for _, r in circoli_v.head(10).iterrows()]
pdf.add_table(headers, rows, [80, 35, 30, 35])

pdf.chapter_title('6.2 Top 10 Associazioni Critiche (alto churn)', 3)
headers = ['Associazione', 'Regione', 'Allievi', 'Churn%']
rows = [[r['NomeCircolo'][:25], r['Regione'][:8], r['AllievoSB'], f"{r['TassoChurn']:.0f}%"]
        for _, r in circoli_c.head(10).iterrows()]
pdf.add_table(headers, rows, [80, 35, 30, 35])

# 7. Regionale
pdf.add_page()
pdf.chapter_title('7. Analisi Regionale e Macroregionale', 2)
pdf.add_chart(CHARTS_DIR / '07_top_regioni.png', width=175)

pdf.chapter_title('7.1 Churn per Macroregione', 3)
pdf.add_chart(CHARTS_CHURN / '05_pattern_macroregionali.png', width=180)

headers = ['Macroregione', 'Giocatori', 'Churn%', 'Gare Medie']
rows = [[r['Macroregione'], f"{r['Giocatori']:,}", f"{r['ChurnRate']:.1f}%", f"{r['GareMedie']:.1f}"]
        for _, r in churn_macro_filtered.iterrows()]
pdf.add_table(headers, rows, [50, 45, 45, 45])

pdf.set_font('Helvetica', 'I', 9)
pdf.set_text_color(100, 100, 100)
pdf.multi_cell(0, 5, "Nota: Esclusi 'Altro' (dati mancanti, 292 record) e 'Nazionale' (sede FIGB, 84 record).")
pdf.ln()

pdf.add_highlight("Nord-Est ha churn piu basso (50.5%) e piu gare. Nord-Ovest il peggiore (58.7%).", 'info')

# 8. Selettivi
pdf.add_page()
pdf.chapter_title('8. Giocatori Selettivi: Campionati vs Tornei', 2)
pdf.add_chart(CHARTS_DIR / '10_profili_giocatori.png', width=175)

headers = ['Profilo', 'Giocatori', '%', 'Gare']
rows = [[r['Profilo'][:25], f"{r['Giocatori']:,}", f"{r['%']:.1f}%", f"{r['GareMedie']:.1f}"]
        for _, r in profili.iterrows()]
pdf.add_table(headers, rows, [70, 40, 35, 35])
pdf.add_highlight("Chi fa CAMPIONATI ha 20% meno churn. Incentivare partecipazione competitiva!", 'success')

# === PARTE III - CHURN ===
pdf.add_page()
pdf.chapter_title('PARTE III - ANALISI CHURN PROFONDA', 1)

# 9. Clustering
pdf.chapter_title('9. Clustering Giocatori Churned', 2)
pdf.add_chart(CHARTS_CHURN / '01_clustering_churn.png', width=185)

# Spiegazione PCA
pdf.chapter_title('9.1 Spiegazione PCA (Principal Component Analysis)', 3)
pdf.add_text("""Il grafico in alto a sinistra mostra i cluster visualizzati con PCA:

- PCA e una tecnica che RIDUCE molte variabili (eta, gare, anni presenza, punti, etc.) a sole 2 dimensioni
- PC1 (asse X) e la "componente principale 1": cattura la MAGGIOR parte della varianza nei dati
- PC2 (asse Y) e la "componente principale 2": cattura la seconda maggior varianza, ortogonale a PC1
- Ogni punto e un giocatore. I colori indicano il cluster di appartenenza.
- Giocatori vicini nel grafico hanno caratteristiche SIMILI.
- La percentuale (es. 45.2%) indica quanta informazione originale e catturata da quella componente.

In sintesi: PCA permette di "vedere" giocatori con 10+ caratteristiche in un grafico 2D.""")

y = pdf.get_y()
pdf.add_metric_box("17,433", 'Tot Churned', 10, y)
pdf.add_metric_box("14,426", 'Recuperabili', 58, y)
pdf.add_metric_box("4,462", 'Priorita Alta', 106, y)
pdf.add_metric_box("82.8%", '% Recuper.', 154, y)
pdf.ln(32)

def get_recup(nome):
    if 'attivi persi' in nome.lower():
        return 'ALTA'
    elif 'occasional' in nome.lower():
        return 'MEDIA'
    else:
        return 'BASSA'

pdf.chapter_title('9.2 Profili Cluster', 3)
headers = ['Nome Cluster', 'Giocatori', '%', 'Recuperabilita']
rows = [[r['NomeCluster'], f"{r['Numerosita']:,}", f"{r['Percentuale']:.1f}%", get_recup(r['NomeCluster'])]
        for _, r in cluster_churn.iterrows()]
pdf.add_table(headers, rows, [95, 30, 25, 40], row_height=8)

# 10. Confronto
pdf.add_page()
pdf.chapter_title('10. Perche Smettono vs Perche Restano', 2)
pdf.add_chart(CHARTS_CHURN / '02_confronto_churned_attivi.png', width=185)
pdf.add_text(sezioni['churn'])

# 11. Soglie
pdf.add_page()
pdf.chapter_title('11. Soglie Critiche di Retention', 2)
pdf.add_chart(CHARTS_CHURN / '06_fattori_retention.png', width=185)

headers = ['Fattore', 'Soglia', 'Churn Sotto', 'Churn Sopra', 'Diff']
rows = [[r['Fattore'], r['Soglia'], f"{r['ChurnSotto']:.1f}%", f"{r['ChurnSopra']:.1f}%", f"+{r['Differenza']:.0f}%"]
        for _, r in soglie.head(8).iterrows()]
pdf.add_table(headers, rows, [38, 30, 38, 38, 30])

pdf.add_highlight("CRITICO: <10 gare/anno = 78% churn. Primi 3 anni decisivi: 78% vs 36% dopo.", 'danger')

# 12. LTV
pdf.add_page()
pdf.chapter_title('12. Lifetime Value per Segmento', 2)
pdf.add_chart(CHARTS_DIR / '14_ltv_per_eta.png', width=175)

headers = ['Fascia', 'Giocatori', 'LTV', 'Totale']
rows = [[r['FasciaEta'], f"{r['Giocatori']:,}", f"EUR{r['LTV']:,.0f}", f"EUR{r['ValoreTotale']:,.0f}"]
        for _, r in ltv.iterrows()]
pdf.add_table(headers, rows, [35, 40, 55, 55])

pdf.add_highlight(f"VALORE TOTALE: EUR{metriche['ltv']['totale_milioni']}M. "
                  "Segmento 60-70 = miglior equilibrio valore/anni.", 'success')

# === PARTE IV - ANALISI INNOVATIVE ===
pdf.add_page()
pdf.chapter_title('PARTE IV - ANALISI INNOVATIVE', 1)

# 13. Curve di Sopravvivenza
pdf.chapter_title('13. Curve di Sopravvivenza (Cohort Analysis)', 2)
if (CHARTS_INNOV / '02_curve_sopravvivenza.png').exists():
    pdf.add_chart(CHARTS_INNOV / '02_curve_sopravvivenza.png', width=185)
    pdf.add_text(sezioni.get('survival', 'Analisi delle curve di sopravvivenza per coorti di ingresso.'))
    pdf.add_highlight("INSIGHT: 50% abbandona entro 3 anni. Giovani (<40) abbandonano PIU' velocemente degli anziani!", 'danger')
else:
    pdf.add_text("Grafico non disponibile.")

# 14. Giocatori a Rischio Reale
pdf.add_page()
pdf.chapter_title('14. Giocatori a Rischio REALE', 2)

pdf.add_text(sezioni.get('engagement', 'Sistema di identificazione giocatori a rischio basato su criteri reali.'))

if attivi_rischio is not None:
    n_rischio = len(attivi_rischio)
    # Controlla sia 'Rischio' che 'RischioChurn' per compatibilita
    if 'Rischio' in attivi_rischio.columns:
        n_critico = len(attivi_rischio[attivi_rischio['Rischio'] == 'CRITICO'])
        n_alto = len(attivi_rischio[attivi_rischio['Rischio'] == 'ALTO'])
    elif 'RischioChurn' in attivi_rischio.columns:
        n_critico = len(attivi_rischio[attivi_rischio['RischioChurn'] == 'CRITICO'])
        n_alto = len(attivi_rischio[attivi_rischio['RischioChurn'] == 'ALTO'])
    else:
        n_critico = n_alto = 0

    y = pdf.get_y()
    pdf.add_metric_box(f"{n_rischio:,}", 'Totale Rischio', 10, y)
    pdf.add_metric_box(f"{n_critico:,}", 'Critici', 58, y)
    pdf.add_metric_box(f"{n_alto:,}", 'Alto Rischio', 106, y)
    urgenti = len(attivi_rischio[attivi_rischio['Priorita'] == '1-URGENTE']) if 'Priorita' in attivi_rischio.columns else 0
    pdf.add_metric_box(f"{urgenti}", 'Urgenti', 154, y)
    pdf.ln(35)

    pdf.add_text("""LOGICA CORRETTA: Chi gioca 20+ gare/anno ha rischio NULLO (non molleranno mai!).
A rischio sono i giocatori con POCHE gare (<10) nei primi 2 anni di presenza.
La lista e ordinata per priorita: prima i giovani (<30 anni) che giocano poco.""")

    # Top 10 urgenti
    if 'Priorita' in attivi_rischio.columns and 'Nome' in attivi_rischio.columns:
        pdf.chapter_title('14.1 Top 10 Intervento Urgente', 3)
        urgenti_df = attivi_rischio[attivi_rischio['Priorita'] == '1-URGENTE'].head(10)
        if len(urgenti_df) > 0:
            headers = ['Nome', 'Eta', 'Gare', 'Motivo']
            rows = [[str(r['Nome'])[:25], int(r['Eta']), f"{r['GareMedie']:.1f}", str(r.get('Motivi', ''))[:25]]
                    for _, r in urgenti_df.iterrows()]
            pdf.add_table(headers, rows, [70, 25, 25, 70])

    pdf.add_highlight(f"AZIONE: Contattare {urgenti} giocatori URGENTI (giovani che giocano poco). File CSV: giocatori_rischio_REALE.csv", 'danger')

# 15. Momento Critico
pdf.add_page()
pdf.chapter_title('15. Momento Critico: Quando Abbandonano', 2)
if (CHARTS_INNOV / '04_momento_critico.png').exists():
    pdf.add_chart(CHARTS_INNOV / '04_momento_critico.png', width=185)
    pdf.add_text("Analisi di QUANDO si verifica l'abbandono: anno, stagione, e numero di gare giocate prima del churn. "
                 "Identificare questi pattern permette interventi mirati nei momenti di maggior rischio.")

# 16. Effetto Associazione
pdf.add_page()
pdf.chapter_title('16. Effetto Associazione: Network Analysis', 2)
if (CHARTS_INNOV / '05_effetto_circolo.png').exists():
    pdf.add_chart(CHARTS_INNOV / '05_effetto_circolo.png', width=185)
    pdf.add_text("Analisi dell'impatto dell'associazione sulla retention. Le associazioni 'hub' con molti tesserati "
                 "mostrano tassi di retention superiori: l'effetto network e la community fanno la differenza.")
    pdf.add_highlight("BEST PRACTICE: Associazioni hub (+100 tesserati) hanno +15% retention. Creare community e' fondamentale!", 'success')

# 17. Modello Predittivo
pdf.add_page()
pdf.chapter_title('17. Modello Predittivo 2025-2035', 2)
if (CHARTS_PRED / '01_modello_predittivo.png').exists():
    pdf.add_chart(CHARTS_PRED / '01_modello_predittivo.png', width=190)

pdf.add_text(sezioni.get('predittivo', 'Proiezione dei tesseramenti considerando invecchiamento e churn.'))

if rischi_pred:
    y = pdf.get_y()
    pdf.add_metric_box(f"{rischi_pred.get('tesserati_2025', 13661):,}", 'Tess. 2025', 10, y)
    pdf.add_metric_box(f"{rischi_pred.get('tesserati_2035', 15404):,}", 'Tess. 2035', 58, y)
    pdf.add_metric_box(f"{rischi_pred.get('eta_media_2035', 69):.0f}", 'Eta 2035', 106, y)
    pdf.add_metric_box(f"{rischi_pred.get('reclutamento_breakeven', 1200):,}", 'Recl./anno', 154, y)
    pdf.ln(35)

    pdf.add_highlight(f"OBIETTIVO: Reclutare almeno {rischi_pred.get('reclutamento_breakeven', 1200):,} nuovi tesserati/anno per mantenere i numeri stabili.", 'warning')

# === PARTE V - AZIONI STRATEGICHE ===
pdf.add_page()
pdf.chapter_title('PARTE V - AZIONI STRATEGICHE', 1)

# 18. Raccomandazioni
pdf.chapter_title('18. Raccomandazioni Prioritizzate', 2)
pdf.add_chart(CHARTS_DIR / '29_matrice_priorita.png', width=175)

# Raccomandazioni dettagliate (non troncate)
pdf.set_font('Helvetica', 'B', 11)
pdf.set_text_color(30, 58, 95)
pdf.cell(0, 8, 'PRIORITA 1 - AZIONI IMMEDIATE (0-3 mesi):')
pdf.ln()
pdf.set_font('Helvetica', '', 10)
pdf.set_text_color(50, 50, 50)
pdf.multi_cell(0, 5, """1. Contattare 201 giovani a rischio urgente (lista CSV allegata)
   - Target: under 30 che giocano <5 gare/anno
   - Azione: Chiamata personale + invito evento dedicato
   - KPI: 30% risposta, 15% recupero

2. Programma "Primi 100 Giorni" per nuovi iscritti
   - Mentoring obbligatorio primi 3 mesi
   - Obiettivo: 10 gare minimo nel primo anno
   - KPI: Retention anno 1 da 40% a 60%""")
pdf.ln(3)

pdf.set_font('Helvetica', 'B', 11)
pdf.set_text_color(30, 58, 95)
pdf.cell(0, 8, 'PRIORITA 2 - BREVE TERMINE (3-6 mesi):')
pdf.ln()
pdf.set_font('Helvetica', '', 10)
pdf.set_text_color(50, 50, 50)
pdf.multi_cell(0, 5, """3. Recuperare 4,462 giocatori "attivi persi" (ex giocatori regolari)
   - Offerta rientro con sconto 30% prima tessera
   - Evento "Bentornato" regionale
   - KPI: 10% recupero = 446 giocatori

4. Potenziare associazioni "hub" come centri di aggregazione
   - Le associazioni con 100+ tesserati hanno +15% retention
   - Creare eventi inter-associazione nelle zone con associazioni piccole
   - KPI: Aumento gare medie del 20%""")
pdf.ln(3)

pdf.set_font('Helvetica', 'B', 11)
pdf.set_text_color(30, 58, 95)
pdf.cell(0, 8, 'PRIORITA 3 - MEDIO TERMINE (6-12 mesi):')
pdf.ln()
pdf.set_font('Helvetica', '', 10)
pdf.set_text_color(50, 50, 50)
pdf.multi_cell(0, 5, """5. Campagna reclutamento giovani (<40 anni)
   - Attualmente solo 4.2% under 40
   - Partnership con universita e aziende
   - Tornei serali/weekend per lavoratori
   - KPI: 500 nuovi under 40/anno

6. Incentivare partecipazione campionati
   - Chi fa campionati ha 20% meno churn
   - Creare "mini-campionati" entry level
   - KPI: +15% partecipazione campionati""")

# 19. Piano Anti-Churn Operativo
pdf.add_page()
pdf.chapter_title('19. Piano Anti-Churn Operativo', 2)
pdf.add_chart(CHARTS_CHURN / '07_raccomandazioni_actionable.png', width=180)

pdf.set_font('Helvetica', 'B', 11)
pdf.set_text_color(30, 58, 95)
pdf.cell(0, 8, 'FASE 1 - EMERGENZA (0-30 giorni):')
pdf.ln()
pdf.set_font('Helvetica', '', 10)
pdf.set_text_color(50, 50, 50)
pdf.multi_cell(0, 5, """- Estrarre lista 201 giovani urgenti da CSV
- Assegnare ogni giocatore a un "tutor" dell'associazione locale
- Prima chiamata entro 7 giorni
- Invito a evento/torneo gratuito entro 30 giorni""")
pdf.ln(3)

pdf.set_font('Helvetica', 'B', 11)
pdf.set_text_color(30, 58, 95)
pdf.cell(0, 8, 'FASE 2 - STABILIZZAZIONE (1-3 mesi):')
pdf.ln()
pdf.set_font('Helvetica', '', 10)
pdf.set_text_color(50, 50, 50)
pdf.multi_cell(0, 5, """- Implementare programma mentoring per tutti i nuovi iscritti
- Creare "tornei scuola" a bassa competitivita
- Obiettivo: ogni nuovo iscritto giochi almeno 1 gara/mese
- Monitoraggio settimanale retention primi 90 giorni""")
pdf.ln(3)

pdf.set_font('Helvetica', 'B', 11)
pdf.set_text_color(30, 58, 95)
pdf.cell(0, 8, 'FASE 3 - CRESCITA (3-12 mesi):')
pdf.ln()
pdf.set_font('Helvetica', '', 10)
pdf.set_text_color(50, 50, 50)
pdf.multi_cell(0, 5, """- Campagna recupero 4,462 ex giocatori attivi
- Potenziamento associazioni hub come centri regionali
- Partnership aziende/universita per under 40
- Creazione "mini-campionati" entry level""")
pdf.ln(3)

pdf.set_font('Helvetica', 'B', 11)
pdf.set_text_color(30, 58, 95)
pdf.cell(0, 8, 'KPI MONITORAGGIO TRIMESTRALE:')
pdf.ln()
pdf.set_font('Helvetica', '', 10)
pdf.set_text_color(50, 50, 50)
pdf.multi_cell(0, 5, """- Retention primo anno: da 40% a 60% (target)
- Gare medie nuovi iscritti: da 8 a 12 (target)
- Under 40: da 4.2% a 6% (target anno 1)
- Giovani urgenti recuperati: 30% (target)
- Ex attivi recuperati: 10% = 446 giocatori (target)""")

# 20. Dashboard e KPI
pdf.add_page()
pdf.chapter_title('20. Dashboard e KPI', 2)
if (CHARTS_INNOV / '06_dashboard_innovativa.png').exists():
    pdf.add_chart(CHARTS_INNOV / '06_dashboard_innovativa.png', width=190)

pdf.add_text("Dashboard riepilogativa con metriche chiave per il monitoraggio periodico.")

# Tabella KPI
pdf.chapter_title('20.1 KPI Strategici', 3)
headers = ['KPI', 'Valore Attuale', 'Target Anno 1', 'Target Anno 3']
rows = [
    ['Tesserati totali', '13,661', '14,000', '15,000'],
    ['Under 40', '4.2%', '6%', '10%'],
    ['Retention anno 1', '40%', '60%', '70%'],
    ['Gare medie nuovi', '8', '12', '15'],
    ['A rischio recuperati', '-', '30%', '50%'],
    ['Ex attivi recuperati', '-', '10%', '20%']
]
pdf.add_table(headers, rows, [55, 45, 45, 45])

# Nota metodologica
pdf.add_page()
pdf.chapter_title('Nota Metodologica', 2)
pdf.set_font('Helvetica', '', 10)
pdf.multi_cell(0, 5, f"""
FONTI: Dati ufficiali FIGB 2017-2025
- Record totali: {metriche['generali']['tesseramenti_totali']:,}
- Giocatori unici: {metriche['generali']['giocatori_unici']:,}
- Periodo: 2017-2025 (9 stagioni)

METODOLOGIA:
- Clustering churn: K-Means (5 cluster) con visualizzazione PCA
- Cohort Analysis: Curve di sopravvivenza per anno di ingresso
- Risk Scoring: Modello basato su gare, anzianita, eta
- Modello Predittivo: Proiezione 2025-2035 con mortalita attuariale
- Correlazioni: Pearson
- Soglie critiche: Analisi comparativa

ANALISI INNOVATIVE:
- Curve sopravvivenza per fascia eta
- Identificazione 2,648 giocatori a rischio REALE (201 urgenti)
- Momento critico di abbandono (quando/perche)
- Effetto network/associazione sulla retention
- Proiezione decennale con scenari

CRITERI RISCHIO (logica corretta):
- Chi gioca 20+ gare/anno = rischio NULLO
- Chi gioca <10 gare nei primi 2 anni = rischio ALTO/CRITICO
- Priorita: giovani (<30) che giocano poco

STRUMENTI: Python 3.12, Pandas, scikit-learn, Matplotlib, Gemini AI, FPDF2
GRAFICI: 50+ totali
""")

pdf.ln(15)
pdf.set_font('Helvetica', 'I', 9)
pdf.set_text_color(100, 100, 100)
pdf.cell(0, 8, f"Generato: {datetime.now().strftime('%d/%m/%Y %H:%M')}", align='C')
pdf.ln()
pdf.cell(0, 8, "FIGB - Federazione Italiana Gioco Bridge", align='C')

# ============================================================================
# SALVATAGGIO
# ============================================================================
print("\n[4/5] Salvataggio...")

pdf_path = OUTPUT_DIR / f'Relazione_FIGB_2017_2025_FINALE.pdf'
pdf.output(str(pdf_path))

print(f"\n{'='*100}")
print(f"PDF COMPLETATO: {pdf_path}")
print(f"Pagine: {pdf.page_no()}")
print(f"{'='*100}")
