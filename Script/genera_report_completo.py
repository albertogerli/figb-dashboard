#!/usr/bin/env python3
"""
Generazione Report Completo FIGB 2017-2025
Stile Top Consulting Firm - Replica della Relazione_Finale_Completa_FIGB.pdf
"""

import json
import requests
from datetime import datetime
from pathlib import Path
import pandas as pd

# Directory
BASE_DIR = Path(__file__).parent.parent
OUTPUT_DIR = BASE_DIR / 'output'
RESULTS_DIR = OUTPUT_DIR / 'results'
CHARTS_DIR = OUTPUT_DIR / 'charts'

# Gemini API
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', '')
GEMINI_MODEL = 'gemini-2.0-flash'

print("=" * 100)
print("GENERAZIONE REPORT COMPLETO FIGB 2017-2025")
print("Stile Top Consulting Firm")
print("=" * 100)

# Caricamento dati
print("\n[1/4] Caricamento dati analisi...")

with open(RESULTS_DIR / 'metriche_complete.json', 'r', encoding='utf-8') as f:
    metrics = json.load(f)

churn_df = pd.read_csv(RESULTS_DIR / 'churn_segmentato_eta.csv')
ltv_df = pd.read_csv(RESULTS_DIR / 'lifetime_value.csv')
sb_df = pd.read_csv(RESULTS_DIR / 'scuola_bridge_dettagliata.csv')
regional_df = pd.read_csv(RESULTS_DIR / 'analisi_regionale_completa.csv')
circoli_df = pd.read_csv(RESULTS_DIR / 'analisi_circoli_completa.csv')
priorities_df = pd.read_csv(RESULTS_DIR / 'priorita_intervento.csv')

# Preparazione dati per prompt
churn_by_age = churn_df.groupby('FasciaEta').agg({
    'Tesserati': 'sum', 'ChurnTotale': 'sum', 'StimaDecessi': 'sum',
    'StimaInfermi': 'sum', 'ChurnReale': 'sum'
}).reset_index()

print("\n[2/4] Preparazione prompt per Gemini...")

data_context = f"""
================================================================================
DATI COMPLETI ANALISI STRATEGICA FIGB 2017-2025
================================================================================

SEZIONE 1: PANORAMICA GENERALE
------------------------------
Periodo analizzato: 2017-2025 (9 anni)
Tesseramenti totali: {metrics['generali']['tesseramenti_totali']:,}
Giocatori unici: {metrics['generali']['giocatori_unici']:,}
Circoli totali storici: {metrics['generali']['circoli_totali']}
Regioni: {metrics['generali']['regioni']}
Tipologie tessera: {metrics['generali']['tipologie_tessera']}

SEZIONE 2: SITUAZIONE 2025
--------------------------
Tesserati 2025: {metrics['anno_2025']['tesserati']:,}
Circoli attivi 2025: {metrics['anno_2025']['circoli_attivi']}
Eta media: {metrics['anno_2025']['eta_media']} anni
Eta mediana: {metrics['anno_2025']['eta_mediana']} anni
Gare medie per tesserato: {metrics['anno_2025']['gare_medie']}
Gare totali giocate: {metrics['anno_2025']['gare_totali']:,}
Distribuzione genere: {metrics['anno_2025']['maschi_pct']}% M / {metrics['anno_2025']['femmine_pct']}% F
Under 40: {metrics['anno_2025']['under_40_pct']}% (CRITICO)
Over 70: {metrics['anno_2025']['over_70_pct']}% (CRITICO - invecchiamento estremo)
Tesserati Scuola Bridge: {metrics['anno_2025']['scuola_bridge']:,}
Agonisti: {metrics['anno_2025']['agonisti']:,}

SEZIONE 3: TREND E VARIAZIONI
-----------------------------
Variazione 2017-2025: {metrics['variazioni']['var_2017_2025_pct']:+.1f}%
Variazione 2019-2025 (pre-COVID vs oggi): {metrics['variazioni']['var_2019_2025_pct']:+.1f}%
Variazione 2024-2025: {metrics['variazioni']['var_2024_2025_pct']:+.1f}%
Picco storico 2018: {metrics['variazioni']['picco_2018']:,} tesserati
Minimo COVID 2021: {metrics['variazioni']['minimo_2021']:,} tesserati
Ripresa post-COVID dal 2021: {metrics['variazioni']['ripresa_post_covid_pct']:+.1f}%

SEZIONE 4: ANALISI CHURN SEGMENTATA (MORTI/INFERMI vs ABBANDONI REALI)
----------------------------------------------------------------------
Churn totale 2017-2024: {metrics['churn']['totale_2017_2024']:,}
Stima decessi (causa naturale): {metrics['churn']['stima_decessi']:,} ({metrics['churn']['stima_decessi']/metrics['churn']['totale_2017_2024']*100:.1f}%)
Stima infermi (impossibilitati a giocare): {metrics['churn']['stima_infermi']:,} ({metrics['churn']['stima_infermi']/metrics['churn']['totale_2017_2024']*100:.1f}%)
CHURN REALE RECUPERABILE: {metrics['churn']['churn_reale_recuperabile']:,} ({metrics['churn']['pct_recuperabile']:.1f}%)

Dettaglio churn per fascia eta:
{churn_by_age.to_string(index=False)}

INSIGHT CHIAVE CHURN:
- Under 30: 61.2% churn reale (CRITICO - perdiamo i giovani)
- 60-70: 12.7% churn reale (ottimo - segmento oro)
- 85+: alta componente decessi/infermi (non recuperabile)
- Il 85% del churn totale e' RECUPERABILE con interventi mirati

SEZIONE 5: LIFETIME VALUE (LTV)
-------------------------------
Valore totale base tesserati: {metrics['ltv_totale']['valore_totale_milioni']:.2f} milioni di euro
LTV medio per giocatore: {metrics['ltv_totale']['ltv_medio']:,.0f} euro

LTV per fascia eta:
{ltv_df.to_string(index=False)}

INSIGHT CHIAVE LTV:
- Fascia 60-70: LTV massimo (2,705 euro) - SEGMENTO D'ORO da proteggere
- Under 40: LTV attuale basso (617 euro) MA potenziale enorme (40 anni vita residua)
- Paradosso giovani: bassa retention (56.6%) = basso LTV, MA investire qui massimizza ROI lungo termine

SEZIONE 6: SCUOLA BRIDGE
------------------------
Tasso successo medio: {metrics['scuola_bridge']['tasso_successo_medio']}% (progressione + conversione)
Tasso conversione medio: {metrics['scuola_bridge']['tasso_conversione_medio']}% (passa ad altra tessera)
Tasso churn medio: {metrics['scuola_bridge']['tasso_churn_medio']}% (abbandona)

NOTA METODOLOGICA IMPORTANTE:
- "Progressione" = rimane in Scuola Bridge = POSITIVO (corso triennale in corso)
- "Conversione" = passa ad altra tessera (Ordinario, Agonista) = SUCCESSO
- "Churn" = non si ritessera = PERDITA REALE

Il tasso di successo del 70.9% e' BUONO considerando la logica corretta.
Problema: tasso conversione solo 19.6% vs target 35%.

Dettaglio annuale:
{sb_df[['Anno', 'TesseratiSB', 'EtaMedia', 'Progressione', 'Convertiti', 'Churn', 'TassoSuccesso%']].to_string(index=False)}

SEZIONE 7: ANALISI REGIONALE
----------------------------
Top 10 regioni per tesserati 2025:
{regional_df.head(10)[['Regione', 'Tesserati2017', 'Tesserati2025', 'Variazione%', 'Retention%', 'Circoli2025', 'EtaMedia']].to_string(index=False)}

CRITICITA REGIONALI:
- Lombardia: -33.7% dal 2017, ma ancora prima regione
- Lazio: -32.9% e retention piu' bassa (80.3%) - EMERGENZA
- Tutte le regioni in declino (nessuna crescita assoluta)
- Emilia-Romagna: miglior retention (87.6%) - modello da replicare
- Sardegna: retention eccellente (90.8%) su base piccola

SEZIONE 8: ANALISI CIRCOLI
--------------------------
Circoli totali analizzati: {len(circoli_df)}
Circoli in crescita (>+10%): {len(circoli_df[circoli_df['Variazione%'] > 10])} ({len(circoli_df[circoli_df['Variazione%'] > 10])/len(circoli_df)*100:.1f}%)
Circoli stabili: {len(circoli_df[(circoli_df['Variazione%'] >= -10) & (circoli_df['Variazione%'] <= 10)])} ({len(circoli_df[(circoli_df['Variazione%'] >= -10) & (circoli_df['Variazione%'] <= 10)])/len(circoli_df)*100:.1f}%)
Circoli in declino (<-10%): {len(circoli_df[circoli_df['Variazione%'] < -10])} ({len(circoli_df[circoli_df['Variazione%'] < -10])/len(circoli_df)*100:.1f}%)

SEZIONE 9: RETENTION
--------------------
Retention medio 2017-2024: {metrics['retention']['media_2017_2024']}%

Retention annuale:
{pd.DataFrame(metrics['retention']['annuale']).to_string(index=False)}

CRITICITA RETENTION PER ETA:
- Under 40: ~56% retention (CRITICO - perdiamo 1 giovane su 2)
- 40-60: ~82% retention (sotto media)
- 60-70: ~86% retention (buono)
- 70-80: ~85% retention (buono)
- 80+: ~79% retention (calo fisiologico)

SEZIONE 10: PRIORITA DI INTERVENTO
----------------------------------
{priorities_df.to_string(index=False)}

================================================================================
"""

prompt = f"""Sei un Senior Partner di McKinsey specializzato in analisi strategica per federazioni sportive.
Devi scrivere una RELAZIONE FINALE COMPLETA per il Consiglio Federale della FIGB (Federazione Italiana Gioco Bridge).

La relazione deve essere PROFESSIONALE, DETTAGLIATA e ACTIONABLE, con lo stesso livello di qualita' di un report McKinsey/BCG/Bain.

{data_context}

================================================================================
STRUTTURA RICHIESTA DELLA RELAZIONE (40+ pagine equivalenti)
================================================================================

Scrivi una relazione completa con TUTTE le seguenti sezioni:

# RELAZIONE FINALE COMPLETA
## Analisi Strategica Tesseramenti FIGB 2017-2025
### Federazione Italiana Gioco Bridge

**Cliente:** Federazione Italiana Gioco Bridge (FIGB)
**Periodo Analizzato:** 2017-2025 (9 anni)
**Dataset:** [inserire numeri]
**Data Relazione:** {datetime.now().strftime('%d %B %Y')}
**Versione:** 2.0 Final Comprehensive Report
**Analista:** Sistema di Business Intelligence FIGB

---

## EXECUTIVE SUMMARY
(Massimo 400 parole - punti chiave, criticita', opportunita', raccomandazioni top-level)

## SINTESI QUANTITATIVA GLOBALE
(Tutti i numeri chiave in formato bullet point)

---

## PARTE I: ANALISI PANORAMICA

### 1. Panoramica Generale Dataset
- Dimensioni dataset
- Copertura temporale (tabella anno per anno)
- Qualita' dati

### 2. Trend Tesseramenti 2017-2025
- Evoluzione complessiva
- Fasi identificate (Pre-COVID, COVID, Ripresa)
- Confronto Pre/Post COVID (tabella)
- Proiezioni scenario base

### 3. Analisi Demografica Globale
- Distribuzione eta' (tabella dettagliata con valutazioni)
- Distribuzione genere
- Attivita' media
- Evoluzione eta' media

---

## PARTE II: ANALISI SPECIALISTICHE

### 4. Analisi Churn Segmentata
**QUESTA E' LA SEZIONE PIU' IMPORTANTE - PRIORITA' INTERVENTO**
- Distinzione tra DECESSI/INFERMI e CHURN REALE RECUPERABILE
- Analisi per fascia eta' (tabella)
- Identificazione segmenti prioritari
- Insight: l'85% del churn e' recuperabile

### 5. Analisi Lifetime Value (LTV)
- LTV per fascia eta' (tabella)
- Segmento d'oro (60-70)
- Paradosso giovani (basso LTV attuale, alto potenziale)
- Valore totale base tesserati

### 6. Analisi Scuola Bridge
- Panoramica e statistiche
- LOGICA CORRETTA: Progressione = POSITIVO (corso triennale)
- Tasso conversione e churn
- Destinazione convertiti
- Problema e cause

### 7. Analisi Regionale
- Top regioni (tabella)
- Variazioni 2017-2025
- Retention regionale
- Emergenza Lazio

### 8. Analisi Circoli
- Segmentazione crescita/declino
- Top performers
- Circoli critici
- Fattori successo

### 9. Analisi Retention per Eta'
- Retention per fascia
- Criticita' giovani
- Modello over 60

---

## PARTE III: SINTESI STRATEGICA

### 10. Quadro Complessivo Criticita'
- 7 criticita' strutturali identificate
- Urgenza intervento

### 11. Opportunita' Strategiche
- Punti di forza da capitalizzare
- Opportunita' non capitalizzate

### 12. Piano Strategico Integrato
- Visione 2025-2030
- 5-8 priorita' strategiche con:
  - Budget stimato
  - Target
  - Azioni
  - ROI atteso

### 13. Proiezioni 2025-2030
- Scenario base (senza interventi)
- Scenario interventi parziali
- Scenario interventi completi
- Confronto scenari (tabella)

### 14. Conclusioni e Raccomandazioni
- Sintesi esecutiva finale
- Raccomandazioni prioritarie
- Urgenza e finestra intervento
- Giudizio finale

---

REQUISITI:
1. Usa TABELLE per tutti i dati numerici
2. Usa BULLET POINT per le liste
3. Includi VALUTAZIONI (ottimo/buono/critico) con emoji se appropriato
4. Sii SPECIFICO con i numeri (non arrotondare troppo)
5. Includi INSIGHT STRATEGICI originali
6. Proponi AZIONI CONCRETE con budget/ROI
7. Scrivi almeno 4000 parole
8. Usa linguaggio professionale italiano
9. Evidenzia le PRIORITA' DI INTERVENTO basate sull'analisi churn segmentata
10. Il focus principale deve essere: DOVE INTERVENIRE per recuperare tesserati?

NOTA CRITICA: La segmentazione del churn per eta' (distinguendo morti/infermi da abbandoni reali) e' la chiave per identificare dove investire. Il 85% del churn e' recuperabile - questo deve guidare le priorita'.
"""

print("\n[3/4] Invio richiesta a Gemini...")
url = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}"

payload = {
    "contents": [{
        "parts": [{
            "text": prompt
        }]
    }],
    "generationConfig": {
        "temperature": 0.7,
        "maxOutputTokens": 32000
    }
}

response = requests.post(url, json=payload)

if response.status_code == 200:
    result = response.json()
    report_text = result['candidates'][0]['content']['parts'][0]['text']

    print("\n[4/4] Salvataggio report...")

    # Header del report
    header = f"""================================================================================
RELAZIONE FINALE COMPLETA
ANALISI STRATEGICA TESSERAMENTI FIGB 2017-2025
================================================================================

Generata automaticamente il {datetime.now().strftime('%d/%m/%Y alle %H:%M')}
Powered by Google Gemini ({GEMINI_MODEL}) + Analisi Python
Sistema di Business Intelligence FIGB

================================================================================
NOTA METODOLOGICA
================================================================================
Questa relazione e' stata generata combinando:
- Analisi statistica avanzata con Python (pandas, numpy, matplotlib)
- Segmentazione churn per eta' (distinguendo decessi/infermi da churn recuperabile)
- Calcolo Lifetime Value per segmento
- Analisi conversione Scuola Bridge con logica corretta
- Generazione testo con Google Gemini API

Dataset: 137,432 tesseramenti | 31,094 giocatori unici | 836 circoli | 9 anni
================================================================================

"""

    footer = f"""

================================================================================
ALLEGATI
================================================================================

GRAFICI GENERATI (output/charts/):
- 01_trend_tesseramenti.png
- 02_piramide_eta.png
- 03_retention_per_eta.png
- 04_churn_segmentato.png
- 05_heatmap_regionale.png
- 06_scuola_bridge_funnel.png
- 07_ltv_per_eta.png
- 08_tipologie_tessera.png
- 09_confronto_covid.png
- 10_matrice_priorita.png

FILE DATI (output/results/):
- metriche_complete.json (230+ metriche)
- churn_segmentato_eta.csv
- lifetime_value.csv
- scuola_bridge_dettagliata.csv
- analisi_regionale_completa.csv
- analisi_circoli_completa.csv
- priorita_intervento.csv

================================================================================
Fine Relazione

Report compilato da: Sistema di Business Intelligence FIGB
Data: {datetime.now().strftime('%d %B %Y')}
Versione: 2.0 Final Comprehensive Report (Dati 2017-2025)
Classificazione: Riservato - Dirigenza FIGB
================================================================================
"""

    full_report = header + report_text + footer

    # Salvataggio TXT
    output_txt = OUTPUT_DIR / f'Relazione_Completa_FIGB_2017_2025_{datetime.now().strftime("%Y%m%d")}.txt'
    with open(output_txt, 'w', encoding='utf-8') as f:
        f.write(full_report)

    # Salvataggio MD
    output_md = OUTPUT_DIR / f'Relazione_Completa_FIGB_2017_2025_{datetime.now().strftime("%Y%m%d")}.md'
    with open(output_md, 'w', encoding='utf-8') as f:
        f.write(report_text)

    print(f"\n" + "=" * 100)
    print("REPORT GENERATO CON SUCCESSO")
    print("=" * 100)
    print(f"\nFile salvati:")
    print(f"  - {output_txt}")
    print(f"  - {output_md}")
    print(f"\nLunghezza report: {len(report_text):,} caratteri ({len(report_text.split()):,} parole circa)")

else:
    print(f"\nERRORE: {response.status_code}")
    print(response.text)

print("\n" + "=" * 100)
