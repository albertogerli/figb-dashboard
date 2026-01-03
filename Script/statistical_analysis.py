#!/usr/bin/env python3
"""
Script per analisi statistica completa dei dati di tesseramento del bridge
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import json
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# Configurazione
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (14, 8)

# Caricamento dati
print("Caricamento dati unificati...")
df = pd.read_csv('/home/ubuntu/bridge_analysis/dati_unificati.csv')

# Creazione directory per output
Path('/home/ubuntu/bridge_analysis/results').mkdir(exist_ok=True)

# ============================================================================
# 1. ANALISI TEMPORALE
# ============================================================================
print("\n" + "="*80)
print("1. ANALISI TEMPORALE")
print("="*80)

yearly_analysis = df.groupby('Anno').agg({
    'MmbCode': 'count',
    'GareGiocate': ['sum', 'mean', 'median'],
    'PuntiCampionati': ['sum', 'mean'],
    'PuntiTotali': ['sum', 'mean']
}).round(2)

yearly_analysis.columns = ['_'.join(col).strip() for col in yearly_analysis.columns.values]
yearly_analysis = yearly_analysis.rename(columns={'MmbCode_count': 'Tesserati'})

# Calcolo variazioni anno su anno
yearly_analysis['Var_Tesserati_%'] = yearly_analysis['Tesserati'].pct_change() * 100
yearly_analysis['Var_Gare_%'] = yearly_analysis['GareGiocate_sum'].pct_change() * 100

print(yearly_analysis)
yearly_analysis.to_csv('/home/ubuntu/bridge_analysis/results/analisi_temporale.csv')

# ============================================================================
# 2. ANALISI PER REGIONE
# ============================================================================
print("\n" + "="*80)
print("2. ANALISI PER REGIONE")
print("="*80)

regional_yearly = df.groupby(['Anno', 'GrpArea']).agg({
    'MmbCode': 'count',
    'GareGiocate': 'sum',
    'PuntiTotali': 'sum'
}).reset_index()

regional_yearly.columns = ['Anno', 'Regione', 'Tesserati', 'Gare', 'Punti']

# Top 10 regioni per tesserati nel 2024
top_regions_2024 = regional_yearly[regional_yearly['Anno'] == 2024].nlargest(10, 'Tesserati')
print("\nTop 10 Regioni 2024:")
print(top_regions_2024)

regional_yearly.to_csv('/home/ubuntu/bridge_analysis/results/analisi_regionale.csv', index=False)

# ============================================================================
# 3. ANALISI PER FASCIA D'ETÀ E SESSO
# ============================================================================
print("\n" + "="*80)
print("3. ANALISI PER FASCIA D'ETÀ E SESSO")
print("="*80)

# Creazione fasce d'età
df['FasciaEta'] = pd.cut(df['Anni'], 
                         bins=[0, 18, 30, 40, 50, 60, 70, 80, 90, 120],
                         labels=['<18', '18-30', '30-40', '40-50', '50-60', '60-70', '70-80', '80-90', '90+'])

age_sex_analysis = df.groupby(['Anno', 'FasciaEta', 'MmbSex']).agg({
    'MmbCode': 'count',
    'GareGiocate': 'mean',
    'PuntiTotali': 'mean'
}).reset_index()

age_sex_analysis.columns = ['Anno', 'FasciaEta', 'Sesso', 'Tesserati', 'GareMediane', 'PuntiMedi']

print("\nDistribuzione per fascia d'età e sesso (2024):")
age_sex_2024 = age_sex_analysis[age_sex_analysis['Anno'] == 2024]
print(age_sex_2024)

age_sex_analysis.to_csv('/home/ubuntu/bridge_analysis/results/analisi_eta_sesso.csv', index=False)

# ============================================================================
# 4. ANALISI CATEGORIE ETÀ (CatLabel)
# ============================================================================
print("\n" + "="*80)
print("4. ANALISI CATEGORIE ETÀ")
print("="*80)

cat_analysis = df.groupby(['Anno', 'CatLabel']).agg({
    'MmbCode': 'count',
    'GareGiocate': 'mean',
    'PuntiTotali': 'mean'
}).reset_index()

cat_analysis.columns = ['Anno', 'Categoria', 'Tesserati', 'GareMediane', 'PuntiMedi']

print("\nTop 10 categorie per tesserati (2024):")
cat_2024 = cat_analysis[cat_analysis['Anno'] == 2024].nlargest(10, 'Tesserati')
print(cat_2024)

cat_analysis.to_csv('/home/ubuntu/bridge_analysis/results/analisi_categorie.csv', index=False)

# ============================================================================
# 5. ANALISI CATEGORIE ETÀ E PUNTI
# ============================================================================
print("\n" + "="*80)
print("5. ANALISI CATEGORIE ETÀ E PUNTI")
print("="*80)

# Creazione fasce di punti
df['FasciaPunti'] = pd.cut(df['PuntiTotali'], 
                           bins=[-1, 0, 500, 2000, 5000, 10000, 20000, 50000, 500000],
                           labels=['0', '1-500', '501-2000', '2001-5000', '5001-10000', 
                                  '10001-20000', '20001-50000', '50000+'])

cat_points_analysis = df.groupby(['Anno', 'CatLabel', 'FasciaPunti']).agg({
    'MmbCode': 'count'
}).reset_index()

cat_points_analysis.columns = ['Anno', 'Categoria', 'FasciaPunti', 'Tesserati']

print("\nDistribuzione categorie per fasce di punti (2024):")
cat_points_2024 = cat_points_analysis[cat_points_analysis['Anno'] == 2024]
print(cat_points_2024.head(20))

cat_points_analysis.to_csv('/home/ubuntu/bridge_analysis/results/analisi_categorie_punti.csv', index=False)

# ============================================================================
# 6. ANALISI RETENTION RATE
# ============================================================================
print("\n" + "="*80)
print("6. ANALISI RETENTION RATE")
print("="*80)

# Calcolo retention per ogni coppia di anni consecutivi
retention_data = []

for year in range(2017, 2024):
    next_year = year + 1
    
    # Giocatori nell'anno corrente
    players_current = set(df[df['Anno'] == year]['MmbCode'].unique())
    
    # Giocatori nell'anno successivo
    players_next = set(df[df['Anno'] == next_year]['MmbCode'].unique())
    
    # Retention: giocatori che si sono ritesserati
    retained = players_current.intersection(players_next)
    
    # Calcolo percentuale
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
retention_df.to_csv('/home/ubuntu/bridge_analysis/results/retention_rate.csv', index=False)

# ============================================================================
# 7. RETENTION PER FASCIA D'ETÀ
# ============================================================================
print("\n" + "="*80)
print("7. RETENTION PER FASCIA D'ETÀ")
print("="*80)

retention_age_data = []

for year in range(2017, 2024):
    next_year = year + 1
    
    # Dati anno corrente
    df_current = df[df['Anno'] == year].copy()
    df_next = df[df['Anno'] == next_year].copy()
    
    # Per ogni fascia d'età
    for fascia in df_current['FasciaEta'].dropna().unique():
        players_current = set(df_current[df_current['FasciaEta'] == fascia]['MmbCode'].unique())
        players_next_all = set(df_next['MmbCode'].unique())
        
        retained = players_current.intersection(players_next_all)
        retention_rate = (len(retained) / len(players_current) * 100) if len(players_current) > 0 else 0
        
        retention_age_data.append({
            'Anno': year,
            'FasciaEta': fascia,
            'Tesserati': len(players_current),
            'Ritesserati': len(retained),
            'RetentionRate_%': round(retention_rate, 2)
        })

retention_age_df = pd.DataFrame(retention_age_data)
print(retention_age_df.head(20))
retention_age_df.to_csv('/home/ubuntu/bridge_analysis/results/retention_per_eta.csv', index=False)

# ============================================================================
# 8. MANCATI RITESSERAMENTI
# ============================================================================
print("\n" + "="*80)
print("8. MANCATI RITESSERAMENTI")
print("="*80)

churn_data = []

for year in range(2017, 2024):
    next_year = year + 1
    
    # Giocatori anno corrente
    df_current = df[df['Anno'] == year].copy()
    players_current = set(df_current['MmbCode'].unique())
    
    # Giocatori anno successivo
    players_next = set(df[df['Anno'] == next_year]['MmbCode'].unique())
    
    # Giocatori che NON si sono ritesserati
    churned = players_current - players_next
    
    # Dettagli dei giocatori persi
    df_churned = df_current[df_current['MmbCode'].isin(churned)]
    
    # Analisi per età e tipo tessera
    churn_analysis = df_churned.groupby(['FasciaEta', 'MbtDesc']).agg({
        'MmbCode': 'count'
    }).reset_index()
    
    churn_analysis['Anno'] = year
    churn_analysis.columns = ['FasciaEta', 'TipoTessera', 'NumeroPersi', 'Anno']
    
    churn_data.append(churn_analysis)

churn_df = pd.concat(churn_data, ignore_index=True)
print(churn_df.head(30))
churn_df.to_csv('/home/ubuntu/bridge_analysis/results/mancati_ritesseramenti.csv', index=False)

# ============================================================================
# 9. ANALISI TIPOLOGIE TESSERA
# ============================================================================
print("\n" + "="*80)
print("9. ANALISI TIPOLOGIE TESSERA")
print("="*80)

membership_analysis = df.groupby(['Anno', 'MbtDesc']).agg({
    'MmbCode': 'count',
    'GareGiocate': 'mean',
    'PuntiTotali': 'mean'
}).reset_index()

membership_analysis.columns = ['Anno', 'TipoTessera', 'Tesserati', 'GareMediane', 'PuntiMedi']

print("\nDistribuzione tipologie tessera (2024):")
print(membership_analysis[membership_analysis['Anno'] == 2024])

membership_analysis.to_csv('/home/ubuntu/bridge_analysis/results/analisi_tipologie_tessera.csv', index=False)

# ============================================================================
# 10. STATISTICHE RIASSUNTIVE
# ============================================================================
print("\n" + "="*80)
print("10. STATISTICHE RIASSUNTIVE")
print("="*80)

summary_stats = {
    'periodo': '2017-2024',
    'totale_tesseramenti': len(df),
    'giocatori_unici': df['MmbCode'].nunique(),
    'circoli_unici': df['MmbGroup'].nunique(),
    'regioni': df['GrpArea'].nunique(),
    'eta_media': round(df['Anni'].mean(), 1),
    'eta_mediana': round(df['Anni'].median(), 1),
    'gare_media': round(df['GareGiocate'].mean(), 1),
    'punti_medi': round(df['PuntiTotali'].mean(), 0),
    'percentuale_maschi': round(len(df[df['MmbSex'] == 'M']) / len(df) * 100, 1),
    'percentuale_femmine': round(len(df[df['MmbSex'] == 'F']) / len(df) * 100, 1),
    'retention_rate_medio': round(retention_df['RetentionRate_%'].mean(), 2)
}

print(json.dumps(summary_stats, indent=2))

with open('/home/ubuntu/bridge_analysis/results/summary_stats.json', 'w') as f:
    json.dump(summary_stats, f, indent=2)

print("\n✓ Analisi statistica completata")
print(f"✓ Risultati salvati in: /home/ubuntu/bridge_analysis/results/")
