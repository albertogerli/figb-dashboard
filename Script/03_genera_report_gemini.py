#!/usr/bin/env python3
"""
Script per la generazione automatica del report FIGB usando Gemini API
"""

import json
import requests
from datetime import datetime
from config import RESULTS_DIR, OUTPUT_DIR, GEMINI_API_KEY, GEMINI_MODEL

print("=" * 80)
print("GENERAZIONE REPORT AUTOMATICO CON GEMINI")
print("=" * 80)

# Caricamento risultati analisi
print("\n1. Caricamento risultati analisi...")
with open(RESULTS_DIR / 'all_results.json', 'r', encoding='utf-8') as f:
    results = json.load(f)

with open(RESULTS_DIR / 'summary_stats.json', 'r', encoding='utf-8') as f:
    summary = json.load(f)

# Preparazione prompt per Gemini
print("\n2. Preparazione dati per Gemini...")

data_context = f"""
DATI ANALISI TESSERAMENTO FIGB (Federazione Italiana Gioco Bridge) 2017-2025

STATISTICHE GENERALI:
- Periodo analizzato: {summary['periodo']}
- Totale tesseramenti: {summary['totale_tesseramenti']:,}
- Giocatori unici: {summary['giocatori_unici']:,}
- Circoli attivi: {summary['circoli_unici']}
- Regioni: {summary['regioni']}
- Età media tesserati: {summary['eta_media']} anni
- Età mediana: {summary['eta_mediana']} anni
- Distribuzione sesso: {summary['percentuale_maschi']}% maschi, {summary['percentuale_femmine']}% femmine
- Gare giocate (media per tesserato): {summary['gare_media']}
- Tesserati 2025: {summary['tesserati_2025']:,}
- Variazione 2024-2025: +{summary['variazione_2024_2025']}%

DATI RETENTION:
{json.dumps(results['retention'], indent=2, ensure_ascii=False)}

ANALISI SCUOLA BRIDGE (con logica corretta - progressione = positivo):
{json.dumps(results['scuola_bridge'], indent=2, ensure_ascii=False)}

NUOVI TESSERATI VS VETERANI:
{json.dumps(results['nuovi_veterani'], indent=2, ensure_ascii=False)}

TOP 10 REGIONI 2025:
{json.dumps(results['regioni_top'], indent=2, ensure_ascii=False)}

TIPOLOGIE TESSERA 2025:
{json.dumps(results['tipologie_tessera'], indent=2, ensure_ascii=False)}

TOP CIRCOLI 2025:
{json.dumps(results['top_circoli'][:10], indent=2, ensure_ascii=False)}
"""

prompt = f"""Sei un esperto analista di dati sportivi. Devi scrivere una RELAZIONE COMPLETA E PROFESSIONALE sull'andamento del tesseramento della Federazione Italiana Gioco Bridge (FIGB) basandoti sui dati forniti.

{data_context}

STRUTTURA RICHIESTA PER LA RELAZIONE:

1. SOMMARIO ESECUTIVO (massimo 200 parole)
   - Punti chiave dell'analisi
   - Trend principali identificati
   - Raccomandazioni strategiche

2. ANALISI TEMPORALE (2017-2025)
   - Andamento del numero di tesserati anno per anno
   - Impatto della pandemia COVID-19 (2020-2021)
   - Trend di recupero post-pandemia
   - Proiezioni per il futuro

3. ANALISI DEL RETENTION RATE
   - Tasso medio di ritesseramento: {summary['retention_rate_medio']}%
   - Variazioni anno su anno
   - Fattori che influenzano la retention
   - Confronto pre e post pandemia

4. ANALISI SCUOLA BRIDGE
   - IMPORTANTE: Il tasso di successo medio è del {summary['scuola_bridge_successo_medio']}%
   - Spiegazione: rimanere in Scuola Bridge significa PROGRESSIONE (corso triennale)
   - Passare ad altra tessera significa COMPLETAMENTO (successo)
   - Solo chi non si ritessera è CHURN REALE
   - Valutazione dell'efficacia del programma formativo

5. ANALISI DEMOGRAFICA
   - Distribuzione per età (età media: {summary['eta_media']} anni)
   - Distribuzione per genere
   - Sfide legate all'invecchiamento della base tesserati
   - Strategie per attrarre giovani

6. ANALISI GEOGRAFICA
   - Regioni trainanti (Lombardia, Lazio, Emilia-Romagna)
   - Disparità territoriali
   - Opportunità di crescita

7. RACCOMANDAZIONI STRATEGICHE
   - Almeno 5 raccomandazioni concrete e attuabili
   - Priorità d'intervento
   - KPI suggeriti per il monitoraggio

8. CONCLUSIONI

Scrivi in italiano formale e professionale. Usa numeri e percentuali per supportare ogni affermazione.
La relazione deve essere completa (almeno 2000 parole) e pronta per essere presentata al Consiglio Federale FIGB.
"""

# Chiamata API Gemini
print("\n3. Invio richiesta a Gemini...")
url = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}"

payload = {
    "contents": [{
        "parts": [{
            "text": prompt
        }]
    }],
    "generationConfig": {
        "temperature": 0.7,
        "maxOutputTokens": 8192
    }
}

response = requests.post(url, json=payload)

if response.status_code == 200:
    result = response.json()
    report_text = result['candidates'][0]['content']['parts'][0]['text']

    # Aggiunta intestazione
    full_report = f"""================================================================================
RELAZIONE ANALISI TESSERAMENTO FIGB 2017-2025
================================================================================
Generata automaticamente il {datetime.now().strftime('%d/%m/%Y alle %H:%M')}
Powered by Google Gemini ({GEMINI_MODEL})
================================================================================

{report_text}

================================================================================
NOTA METODOLOGICA
================================================================================
Questa relazione è stata generata automaticamente utilizzando:
- Dati ufficiali tesseramento FIGB 2017-2025
- Analisi statistica con Python (pandas, numpy)
- Generazione testo con Google Gemini API

I dati sono stati elaborati correggendo la logica di analisi della Scuola Bridge:
- Progressione (rimane in SB) = Esito positivo (corso triennale)
- Completamento (passa altra tessera) = Esito positivo (ha finito il corso)
- Churn reale = Solo chi non si ritessera affatto

Fonte dati: FIGB - Federazione Italiana Gioco Bridge
================================================================================
"""

    # Salvataggio report
    output_file = OUTPUT_DIR / f'Report_FIGB_2017_2025_{datetime.now().strftime("%Y%m%d")}.txt'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(full_report)

    print(f"\n✅ Report generato con successo!")
    print(f"📄 File salvato: {output_file}")
    print(f"📊 Lunghezza: {len(report_text):,} caratteri")

    # Salva anche in formato markdown
    md_file = OUTPUT_DIR / f'Report_FIGB_2017_2025_{datetime.now().strftime("%Y%m%d")}.md'
    with open(md_file, 'w', encoding='utf-8') as f:
        f.write(f"# Relazione Analisi Tesseramento FIGB 2017-2025\n\n")
        f.write(f"*Generata il {datetime.now().strftime('%d/%m/%Y alle %H:%M')} con Google Gemini*\n\n")
        f.write("---\n\n")
        f.write(report_text)

    print(f"📝 Versione Markdown: {md_file}")

else:
    print(f"\n❌ Errore nella chiamata API: {response.status_code}")
    print(response.text)

print("\n" + "=" * 80)
print("GENERAZIONE COMPLETATA")
print("=" * 80)
