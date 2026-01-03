#!/usr/bin/env python3
"""
Script per analisi statistica completa dei dati di tesseramento FIGB 2017-2025
Versione corretta con percorsi relativi e logica Scuola Bridge aggiornata
"""

import pandas as pd
import numpy as np
import json
from config import (
    OUTPUT_DIR, RESULTS_DIR, FILE_UNIFICATO_CSV,
    FASCE_ETA_BINS, FASCE_ETA_LABELS,
    FASCE_PUNTI_BINS, FASCE_PUNTI_LABELS,
    ANNI_ANALISI
)
import warnings
warnings.filterwarnings('ignore')

print("=" * 80)
print("ANALISI COMPLETA TESSERAMENTO FIGB 2017-2025")
print("=" * 80)

# Caricamento dati
print("\nCaricamento dati unificati...")
df = pd.read_csv(FILE_UNIFICATO_CSV)
print(f"Record totali: {len(df):,}")

# Creazione fasce
df['FasciaEta'] = pd.cut(df['Anni'], bins=FASCE_ETA_BINS, labels=FASCE_ETA_LABELS)
df['FasciaPunti'] = pd.cut(df['PuntiTotali'], bins=FASCE_PUNTI_BINS, labels=FASCE_PUNTI_LABELS)

results = {}

# ============================================================================
# 1. ANALISI TEMPORALE
# ============================================================================
print("\n" + "=" * 80)
print("1. ANALISI TEMPORALE")
print("=" * 80)

yearly_analysis = df.groupby('Anno').agg({
    'MmbCode': 'count',
    'GareGiocate': ['sum', 'mean', 'median'],
    'PuntiCampionati': ['sum', 'mean'],
    'PuntiTotali': ['sum', 'mean'],
    'Anni': 'mean'
}).round(2)

yearly_analysis.columns = ['_'.join(col).strip() for col in yearly_analysis.columns.values]
yearly_analysis = yearly_analysis.rename(columns={'MmbCode_count': 'Tesserati'})
yearly_analysis['Var_Tesserati_%'] = yearly_analysis['Tesserati'].pct_change() * 100
yearly_analysis['Var_Gare_%'] = yearly_analysis['GareGiocate_sum'].pct_change() * 100

print(yearly_analysis[['Tesserati', 'Var_Tesserati_%', 'Anni_mean']].round(1))
yearly_analysis.to_csv(RESULTS_DIR / 'analisi_temporale.csv')
results['temporale'] = yearly_analysis.to_dict()

# ============================================================================
# 2. ANALISI PER REGIONE
# ============================================================================
print("\n" + "=" * 80)
print("2. ANALISI PER REGIONE")
print("=" * 80)

regional_yearly = df.groupby(['Anno', 'GrpArea']).agg({
    'MmbCode': 'count',
    'GareGiocate': 'sum',
    'PuntiTotali': 'sum'
}).reset_index()
regional_yearly.columns = ['Anno', 'Regione', 'Tesserati', 'Gare', 'Punti']

# Top regioni 2025
top_regions = regional_yearly[regional_yearly['Anno'] == 2025].nlargest(10, 'Tesserati')
print("\nTop 10 Regioni 2025:")
print(top_regions[['Regione', 'Tesserati', 'Gare']])

regional_yearly.to_csv(RESULTS_DIR / 'analisi_regionale.csv', index=False)
results['regioni_top'] = top_regions.to_dict('records')

# ============================================================================
# 3. ANALISI DEMOGRAFICA (ETÀ E SESSO)
# ============================================================================
print("\n" + "=" * 80)
print("3. ANALISI DEMOGRAFICA")
print("=" * 80)

age_sex_analysis = df.groupby(['Anno', 'FasciaEta', 'MmbSex']).agg({
    'MmbCode': 'count',
    'GareGiocate': 'mean',
    'PuntiTotali': 'mean'
}).reset_index()
age_sex_analysis.columns = ['Anno', 'FasciaEta', 'Sesso', 'Tesserati', 'GareMediane', 'PuntiMedi']

# Distribuzione sesso 2025
sex_dist = df[df['Anno'] == 2025].groupby('MmbSex')['MmbCode'].count()
print(f"\nDistribuzione per sesso 2025:")
print(f"  Maschi: {sex_dist.get('M', 0):,} ({sex_dist.get('M', 0)/len(df[df['Anno']==2025])*100:.1f}%)")
print(f"  Femmine: {sex_dist.get('F', 0):,} ({sex_dist.get('F', 0)/len(df[df['Anno']==2025])*100:.1f}%)")

age_sex_analysis.to_csv(RESULTS_DIR / 'analisi_eta_sesso.csv', index=False)

# ============================================================================
# 4. ANALISI RETENTION RATE
# ============================================================================
print("\n" + "=" * 80)
print("4. ANALISI RETENTION RATE")
print("=" * 80)

retention_data = []
for year in range(2017, 2025):
    next_year = year + 1
    players_current = set(df[df['Anno'] == year]['MmbCode'].unique())
    players_next = set(df[df['Anno'] == next_year]['MmbCode'].unique())

    retained = players_current.intersection(players_next)
    retention_rate = (len(retained) / len(players_current) * 100) if len(players_current) > 0 else 0

    retention_data.append({
        'Anno': year,
        'Tesserati': len(players_current),
        'Ritesserati': len(retained),
        'RetentionRate_%': round(retention_rate, 2),
        'Persi': len(players_current) - len(retained),
        'Nuovi_AnnoSuccessivo': len(players_next) - len(retained)
    })

retention_df = pd.DataFrame(retention_data)
print(retention_df)
retention_df.to_csv(RESULTS_DIR / 'retention_rate.csv', index=False)
results['retention'] = retention_df.to_dict('records')

# ============================================================================
# 5. ANALISI SCUOLA BRIDGE (LOGICA CORRETTA)
# ============================================================================
print("\n" + "=" * 80)
print("5. ANALISI SCUOLA BRIDGE (LOGICA CORRETTA)")
print("=" * 80)

sb_analysis = []
for year in range(2017, 2025):
    next_year = year + 1

    # Tesserati Scuola Bridge anno corrente
    df_sb_current = df[(df['Anno'] == year) &
                       (df['MbtDesc'].str.contains('Scuola Bridge', case=False, na=False))]
    sb_players = set(df_sb_current['MmbCode'].unique())

    if len(sb_players) == 0:
        continue

    # Tesserati anno successivo
    df_next = df[df['Anno'] == next_year]
    tesserati_next = set(df_next['MmbCode'].unique())

    # Scuola Bridge anno successivo
    df_sb_next = df_next[df_next['MbtDesc'].str.contains('Scuola Bridge', case=False, na=False)]
    sb_next = set(df_sb_next['MmbCode'].unique())

    # Calcoli con logica corretta
    ritesserati = sb_players.intersection(tesserati_next)
    progressione = sb_players.intersection(sb_next)  # Rimane in SB = POSITIVO
    completamento = ritesserati - progressione  # Passa ad altra tessera = POSITIVO
    churn_reale = sb_players - ritesserati  # Non si ritessera = NEGATIVO

    tasso_successo = (len(progressione) + len(completamento)) / len(sb_players) * 100
    tasso_churn = len(churn_reale) / len(sb_players) * 100

    sb_analysis.append({
        'Anno': year,
        'TesseratiSB': len(sb_players),
        'Progressione': len(progressione),
        'Completamento': len(completamento),
        'ChurnReale': len(churn_reale),
        'TassoSuccesso_%': round(tasso_successo, 1),
        'TassoChurn_%': round(tasso_churn, 1)
    })

sb_df = pd.DataFrame(sb_analysis)
print(sb_df)
sb_df.to_csv(RESULTS_DIR / 'scuola_bridge_corretta.csv', index=False)
results['scuola_bridge'] = sb_df.to_dict('records')

# ============================================================================
# 6. ANALISI TIPOLOGIE TESSERA
# ============================================================================
print("\n" + "=" * 80)
print("6. ANALISI TIPOLOGIE TESSERA")
print("=" * 80)

membership_analysis = df.groupby(['Anno', 'MbtDesc']).agg({
    'MmbCode': 'count',
    'GareGiocate': 'mean',
    'PuntiTotali': 'mean'
}).reset_index()
membership_analysis.columns = ['Anno', 'TipoTessera', 'Tesserati', 'GareMediane', 'PuntiMedi']

# Top tipologie 2025
top_tessere = membership_analysis[membership_analysis['Anno'] == 2025].nlargest(10, 'Tesserati')
print("\nTop tipologie tessera 2025:")
print(top_tessere[['TipoTessera', 'Tesserati']])

membership_analysis.to_csv(RESULTS_DIR / 'analisi_tipologie_tessera.csv', index=False)
results['tipologie_tessera'] = top_tessere.to_dict('records')

# ============================================================================
# 7. ANALISI CIRCOLI
# ============================================================================
print("\n" + "=" * 80)
print("7. ANALISI CIRCOLI")
print("=" * 80)

circoli_analysis = df.groupby(['Anno', 'MmbGroup']).agg({
    'MmbCode': 'count',
    'GareGiocate': 'sum',
    'PuntiTotali': 'sum'
}).reset_index()
circoli_analysis.columns = ['Anno', 'Circolo', 'Tesserati', 'GareTotali', 'PuntiTotali']

# Top circoli 2025
top_circoli = circoli_analysis[circoli_analysis['Anno'] == 2025].nlargest(15, 'Tesserati')
print("\nTop 15 Circoli 2025:")
print(top_circoli[['Circolo', 'Tesserati', 'GareTotali']])

circoli_analysis.to_csv(RESULTS_DIR / 'analisi_circoli.csv', index=False)
results['top_circoli'] = top_circoli.to_dict('records')

# ============================================================================
# 8. ANALISI NUOVI TESSERATI VS VETERANI
# ============================================================================
print("\n" + "=" * 80)
print("8. NUOVI TESSERATI VS VETERANI")
print("=" * 80)

# Per ogni anno, identifica nuovi tesserati
nuovi_analysis = []
all_players_seen = set()

for year in sorted(df['Anno'].unique()):
    year_players = set(df[df['Anno'] == year]['MmbCode'].unique())
    nuovi = year_players - all_players_seen
    veterani = year_players.intersection(all_players_seen)

    nuovi_analysis.append({
        'Anno': year,
        'Totali': len(year_players),
        'Nuovi': len(nuovi),
        'Veterani': len(veterani),
        'PercNuovi': round(len(nuovi) / len(year_players) * 100, 1) if len(year_players) > 0 else 0
    })

    all_players_seen.update(year_players)

nuovi_df = pd.DataFrame(nuovi_analysis)
print(nuovi_df)
nuovi_df.to_csv(RESULTS_DIR / 'nuovi_vs_veterani.csv', index=False)
results['nuovi_veterani'] = nuovi_df.to_dict('records')

# ============================================================================
# 9. STATISTICHE RIASSUNTIVE
# ============================================================================
print("\n" + "=" * 80)
print("9. STATISTICHE RIASSUNTIVE FINALI")
print("=" * 80)

summary_stats = {
    'periodo': '2017-2025',
    'anni_analizzati': 9,
    'totale_tesseramenti': int(len(df)),
    'giocatori_unici': int(df['MmbCode'].nunique()),
    'circoli_unici': int(df['MmbGroup'].nunique()),
    'regioni': int(df['GrpArea'].nunique()),
    'eta_media': round(float(df['Anni'].mean()), 1),
    'eta_mediana': round(float(df['Anni'].median()), 1),
    'eta_min': int(df['Anni'].min()),
    'eta_max': int(df['Anni'].max()),
    'gare_media': round(float(df['GareGiocate'].mean()), 1),
    'gare_totali': int(df['GareGiocate'].sum()),
    'punti_medi': round(float(df['PuntiTotali'].mean()), 0),
    'percentuale_maschi': round(float(len(df[df['MmbSex'] == 'M']) / len(df) * 100), 1),
    'percentuale_femmine': round(float(len(df[df['MmbSex'] == 'F']) / len(df) * 100), 1),
    'retention_rate_medio': round(float(retention_df['RetentionRate_%'].mean()), 2),
    'tesserati_2025': int(len(df[df['Anno'] == 2025])),
    'variazione_2024_2025': round(float(yearly_analysis.loc[2025, 'Var_Tesserati_%']), 1),
    'scuola_bridge_successo_medio': round(float(sb_df['TassoSuccesso_%'].mean()), 1)
}

print(json.dumps(summary_stats, indent=2, ensure_ascii=False))

with open(RESULTS_DIR / 'summary_stats.json', 'w', encoding='utf-8') as f:
    json.dump(summary_stats, f, indent=2, ensure_ascii=False)

# Salva tutti i risultati per il report
with open(RESULTS_DIR / 'all_results.json', 'w', encoding='utf-8') as f:
    # Converti i dati per la serializzazione JSON
    json_results = {
        'summary': summary_stats,
        'retention': results['retention'],
        'scuola_bridge': results['scuola_bridge'],
        'nuovi_veterani': results['nuovi_veterani'],
        'regioni_top': results['regioni_top'],
        'tipologie_tessera': results['tipologie_tessera'],
        'top_circoli': results['top_circoli']
    }
    json.dump(json_results, f, indent=2, ensure_ascii=False)

print("\n" + "=" * 80)
print("ANALISI COMPLETATA")
print("=" * 80)
print(f"Risultati salvati in: {RESULTS_DIR}")
print(f"File generati:")
for f in RESULTS_DIR.glob('*.csv'):
    print(f"  - {f.name}")
for f in RESULTS_DIR.glob('*.json'):
    print(f"  - {f.name}")
