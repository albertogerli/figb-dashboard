#!/usr/bin/env python3
"""
Analisi statistica avanzata con 100+ metriche professionali
"""

import pandas as pd
import numpy as np
import json
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

print("Caricamento dati...")
df = pd.read_csv('/home/ubuntu/bridge_analysis/dati_unificati.csv')

# Creazione fasce d'età
df['FasciaEta'] = pd.cut(df['Anni'], 
                         bins=[0, 18, 30, 40, 50, 60, 70, 80, 90, 120],
                         labels=['<18', '18-30', '30-40', '40-50', '50-60', '60-70', '70-80', '80-90', '90+'])

# Creazione fasce di punti
df['FasciaPunti'] = pd.cut(df['PuntiTotali'], 
                           bins=[-1, 0, 500, 2000, 5000, 10000, 20000, 50000, 500000],
                           labels=['0', '1-500', '501-2000', '2001-5000', '5001-10000', 
                                  '10001-20000', '20001-50000', '50000+'])

# Dizionario per tutte le statistiche
stats = {}

print("\n" + "="*80)
print("ANALISI STATISTICA AVANZATA - 100+ METRICHE")
print("="*80)

# ============================================================================
# SEZIONE 1: STATISTICHE GENERALI (15 metriche)
# ============================================================================
print("\n1. STATISTICHE GENERALI")

stats['generale'] = {
    '01_periodo_analisi': '2017-2024',
    '02_totale_record': len(df),
    '03_giocatori_unici': df['MmbCode'].nunique(),
    '04_circoli_unici': df['MmbGroup'].nunique(),
    '05_regioni_coperte': df['GrpArea'].nunique(),
    '06_anni_analizzati': df['Anno'].nunique(),
    '07_totale_gare_giocate': int(df['GareGiocate'].sum()),
    '08_totale_punti_campionati': int(df['PuntiCampionati'].sum()),
    '09_totale_punti_totali': int(df['PuntiTotali'].sum()),
    '10_media_gare_per_tesserato': round(df['GareGiocate'].mean(), 2),
    '11_mediana_gare_per_tesserato': int(df['GareGiocate'].median()),
    '12_media_punti_per_tesserato': int(df['PuntiTotali'].mean()),
    '13_mediana_punti_per_tesserato': int(df['PuntiTotali'].median()),
    '14_percentuale_con_zero_punti': round(len(df[df['PuntiTotali'] == 0]) / len(df) * 100, 2),
    '15_percentuale_con_zero_gare': round(len(df[df['GareGiocate'] == 0]) / len(df) * 100, 2),
}

# ============================================================================
# SEZIONE 2: STATISTICHE PER ANNO (16 metriche per anno = 128 totali)
# ============================================================================
print("\n2. STATISTICHE PER ANNO")

stats['per_anno'] = {}
for year in range(2017, 2025):
    df_year = df[df['Anno'] == year]
    
    stats['per_anno'][year] = {
        'tesserati': len(df_year),
        'nuovi_codici': df_year['MmbCode'].nunique(),
        'circoli_attivi': df_year['MmbGroup'].nunique(),
        'gare_totali': int(df_year['GareGiocate'].sum()),
        'gare_media': round(df_year['GareGiocate'].mean(), 2),
        'gare_mediana': int(df_year['GareGiocate'].median()),
        'punti_totali': int(df_year['PuntiTotali'].sum()),
        'punti_medi': int(df_year['PuntiTotali'].mean()),
        'punti_mediana': int(df_year['PuntiTotali'].median()),
        'eta_media': round(df_year['Anni'].mean(), 1),
        'eta_mediana': round(df_year['Anni'].median(), 1),
        'eta_min': int(df_year['Anni'].min()),
        'eta_max': int(df_year['Anni'].max()),
        'percentuale_maschi': round(len(df_year[df_year['MmbSex'] == 'M']) / len(df_year) * 100, 2),
        'percentuale_femmine': round(len(df_year[df_year['MmbSex'] == 'F']) / len(df_year) * 100, 2),
        'giocatori_attivi_50plus_gare': len(df_year[df_year['GareGiocate'] >= 50]),
    }

# Calcolo variazioni anno su anno
for year in range(2018, 2025):
    prev_year = year - 1
    if prev_year in stats['per_anno']:
        stats['per_anno'][year]['variazione_tesserati_pct'] = round(
            (stats['per_anno'][year]['tesserati'] - stats['per_anno'][prev_year]['tesserati']) / 
            stats['per_anno'][prev_year]['tesserati'] * 100, 2
        )
        stats['per_anno'][year]['variazione_gare_pct'] = round(
            (stats['per_anno'][year]['gare_totali'] - stats['per_anno'][prev_year]['gare_totali']) / 
            stats['per_anno'][prev_year]['gare_totali'] * 100, 2
        )

# ============================================================================
# SEZIONE 3: STATISTICHE DEMOGRAFICHE (30 metriche)
# ============================================================================
print("\n3. STATISTICHE DEMOGRAFICHE")

stats['demografiche'] = {
    'eta_media_totale': round(df['Anni'].mean(), 2),
    'eta_mediana_totale': round(df['Anni'].median(), 1),
    'eta_moda': int(df['Anni'].mode()[0]),
    'eta_std': round(df['Anni'].std(), 2),
    'eta_min': int(df['Anni'].min()),
    'eta_max': int(df['Anni'].max()),
    'range_eta': int(df['Anni'].max() - df['Anni'].min()),
}

# Distribuzione per fascia d'età
for fascia in ['<18', '18-30', '30-40', '40-50', '50-60', '60-70', '70-80', '80-90', '90+']:
    count = len(df[df['FasciaEta'] == fascia])
    pct = round(count / len(df) * 100, 2)
    stats['demografiche'][f'fascia_{fascia}_count'] = count
    stats['demografiche'][f'fascia_{fascia}_pct'] = pct

# Statistiche per sesso
stats['demografiche']['totale_maschi'] = len(df[df['MmbSex'] == 'M'])
stats['demografiche']['totale_femmine'] = len(df[df['MmbSex'] == 'F'])
stats['demografiche']['pct_maschi'] = round(len(df[df['MmbSex'] == 'M']) / len(df) * 100, 2)
stats['demografiche']['pct_femmine'] = round(len(df[df['MmbSex'] == 'F']) / len(df) * 100, 2)
stats['demografiche']['rapporto_m_f'] = round(len(df[df['MmbSex'] == 'M']) / len(df[df['MmbSex'] == 'F']), 3)

# Età media per sesso
stats['demografiche']['eta_media_maschi'] = round(df[df['MmbSex'] == 'M']['Anni'].mean(), 2)
stats['demografiche']['eta_media_femmine'] = round(df[df['MmbSex'] == 'F']['Anni'].mean(), 2)
stats['demografiche']['diff_eta_m_f'] = round(
    df[df['MmbSex'] == 'M']['Anni'].mean() - df[df['MmbSex'] == 'F']['Anni'].mean(), 2
)

# ============================================================================
# SEZIONE 4: STATISTICHE REGIONALI (25 metriche)
# ============================================================================
print("\n4. STATISTICHE REGIONALI")

regional_stats = df.groupby('GrpArea').agg({
    'MmbCode': 'count',
    'GareGiocate': 'sum',
    'PuntiTotali': 'sum'
}).sort_values('MmbCode', ascending=False)

stats['regionali'] = {
    'regioni_totali': len(regional_stats),
    'top_regione': regional_stats.index[0],
    'top_regione_tesserati': int(regional_stats.iloc[0]['MmbCode']),
    'top_regione_pct': round(regional_stats.iloc[0]['MmbCode'] / len(df) * 100, 2),
}

# Top 10 regioni
for i, (region, row) in enumerate(regional_stats.head(10).iterrows(), 1):
    stats['regionali'][f'top{i}_regione'] = region
    stats['regionali'][f'top{i}_tesserati'] = int(row['MmbCode'])
    stats['regionali'][f'top{i}_pct'] = round(row['MmbCode'] / len(df) * 100, 2)

# Concentrazione geografica
stats['regionali']['top3_concentrazione_pct'] = round(
    regional_stats.head(3)['MmbCode'].sum() / len(df) * 100, 2
)
stats['regionali']['top5_concentrazione_pct'] = round(
    regional_stats.head(5)['MmbCode'].sum() / len(df) * 100, 2
)
stats['regionali']['top10_concentrazione_pct'] = round(
    regional_stats.head(10)['MmbCode'].sum() / len(df) * 100, 2
)

# ============================================================================
# SEZIONE 5: STATISTICHE ATTIVITÀ (20 metriche)
# ============================================================================
print("\n5. STATISTICHE ATTIVITÀ")

stats['attivita'] = {
    'gare_totali': int(df['GareGiocate'].sum()),
    'gare_media': round(df['GareGiocate'].mean(), 2),
    'gare_mediana': int(df['GareGiocate'].median()),
    'gare_std': round(df['GareGiocate'].std(), 2),
    'gare_min': int(df['GareGiocate'].min()),
    'gare_max': int(df['GareGiocate'].max()),
}

# Distribuzione per livello di attività
stats['attivita']['giocatori_zero_gare'] = len(df[df['GareGiocate'] == 0])
stats['attivita']['giocatori_1_10_gare'] = len(df[(df['GareGiocate'] >= 1) & (df['GareGiocate'] <= 10)])
stats['attivita']['giocatori_11_30_gare'] = len(df[(df['GareGiocate'] >= 11) & (df['GareGiocate'] <= 30)])
stats['attivita']['giocatori_31_50_gare'] = len(df[(df['GareGiocate'] >= 31) & (df['GareGiocate'] <= 50)])
stats['attivita']['giocatori_51_100_gare'] = len(df[(df['GareGiocate'] >= 51) & (df['GareGiocate'] <= 100)])
stats['attivita']['giocatori_100plus_gare'] = len(df[df['GareGiocate'] > 100])

# Percentuali
total = len(df)
stats['attivita']['pct_zero_gare'] = round(stats['attivita']['giocatori_zero_gare'] / total * 100, 2)
stats['attivita']['pct_1_10_gare'] = round(stats['attivita']['giocatori_1_10_gare'] / total * 100, 2)
stats['attivita']['pct_11_30_gare'] = round(stats['attivita']['giocatori_11_30_gare'] / total * 100, 2)
stats['attivita']['pct_31_50_gare'] = round(stats['attivita']['giocatori_31_50_gare'] / total * 100, 2)
stats['attivita']['pct_51_100_gare'] = round(stats['attivita']['giocatori_51_100_gare'] / total * 100, 2)
stats['attivita']['pct_100plus_gare'] = round(stats['attivita']['giocatori_100plus_gare'] / total * 100, 2)

# Gare medie per fascia d'età
for fascia in ['<18', '18-30', '30-40', '40-50', '50-60', '60-70', '70-80', '80-90', '90+']:
    df_fascia = df[df['FasciaEta'] == fascia]
    if len(df_fascia) > 0:
        stats['attivita'][f'gare_media_{fascia}'] = round(df_fascia['GareGiocate'].mean(), 2)

# ============================================================================
# SEZIONE 6: STATISTICHE PUNTI (20 metriche)
# ============================================================================
print("\n6. STATISTICHE PUNTI")

stats['punti'] = {
    'punti_totali_cumulati': int(df['PuntiTotali'].sum()),
    'punti_campionati_totali': int(df['PuntiCampionati'].sum()),
    'punti_medi': int(df['PuntiTotali'].mean()),
    'punti_mediana': int(df['PuntiTotali'].median()),
    'punti_std': int(df['PuntiTotali'].std()),
    'punti_min': int(df['PuntiTotali'].min()),
    'punti_max': int(df['PuntiTotali'].max()),
}

# Distribuzione per fasce di punti
for fascia in ['0', '1-500', '501-2000', '2001-5000', '5001-10000', '10001-20000', '20001-50000', '50000+']:
    count = len(df[df['FasciaPunti'] == fascia])
    pct = round(count / len(df) * 100, 2)
    stats['punti'][f'fascia_{fascia}_count'] = count
    stats['punti'][f'fascia_{fascia}_pct'] = pct

# Punti medi per fascia d'età
for fascia in ['<18', '18-30', '30-40', '40-50', '50-60', '60-70', '70-80', '80-90', '90+']:
    df_fascia = df[df['FasciaEta'] == fascia]
    if len(df_fascia) > 0:
        stats['punti'][f'punti_medi_{fascia}'] = int(df_fascia['PuntiTotali'].mean())

# ============================================================================
# SEZIONE 7: STATISTICHE CATEGORIE (15 metriche)
# ============================================================================
print("\n7. STATISTICHE CATEGORIE")

cat_stats = df['CatLabel'].value_counts()
stats['categorie'] = {
    'categorie_totali': len(cat_stats),
    'categoria_piu_numerosa': cat_stats.index[0],
    'categoria_piu_numerosa_count': int(cat_stats.iloc[0]),
    'categoria_piu_numerosa_pct': round(cat_stats.iloc[0] / len(df) * 100, 2),
}

# Top 10 categorie
for i, (cat, count) in enumerate(cat_stats.head(10).items(), 1):
    stats['categorie'][f'top{i}_categoria'] = cat
    stats['categorie'][f'top{i}_count'] = int(count)
    stats['categorie'][f'top{i}_pct'] = round(count / len(df) * 100, 2)

# ============================================================================
# SEZIONE 8: STATISTICHE TIPOLOGIE TESSERA (15 metriche)
# ============================================================================
print("\n8. STATISTICHE TIPOLOGIE TESSERA")

tipo_stats = df['MbtDesc'].value_counts()
stats['tipologie_tessera'] = {
    'tipologie_totali': len(tipo_stats),
    'tipologia_piu_comune': tipo_stats.index[0],
    'tipologia_piu_comune_count': int(tipo_stats.iloc[0]),
    'tipologia_piu_comune_pct': round(tipo_stats.iloc[0] / len(df) * 100, 2),
}

# Statistiche per ogni tipologia principale
for tipo in ['Ordinario Sportivo', 'Agonista', 'Scuola Bridge', 'Ordinario Amatoriale', 'Non Agonista']:
    df_tipo = df[df['MbtDesc'] == tipo]
    if len(df_tipo) > 0:
        stats['tipologie_tessera'][f'{tipo}_count'] = len(df_tipo)
        stats['tipologie_tessera'][f'{tipo}_pct'] = round(len(df_tipo) / len(df) * 100, 2)
        stats['tipologie_tessera'][f'{tipo}_gare_medie'] = round(df_tipo['GareGiocate'].mean(), 2)
        stats['tipologie_tessera'][f'{tipo}_punti_medi'] = int(df_tipo['PuntiTotali'].mean())

# ============================================================================
# SEZIONE 9: STATISTICHE RETENTION (10 metriche)
# ============================================================================
print("\n9. STATISTICHE RETENTION")

retention_data = []
for year in range(2017, 2024):
    next_year = year + 1
    players_current = set(df[df['Anno'] == year]['MmbCode'].unique())
    players_next = set(df[df['Anno'] == next_year]['MmbCode'].unique())
    retained = players_current.intersection(players_next)
    retention_rate = (len(retained) / len(players_current) * 100) if len(players_current) > 0 else 0
    retention_data.append({
        'anno': year,
        'tesserati': len(players_current),
        'ritesserati': len(retained),
        'retention_rate': retention_rate,
        'persi': len(players_current) - len(retained),
        'nuovi': len(players_next) - len(retained)
    })

retention_df = pd.DataFrame(retention_data)

stats['retention'] = {
    'retention_medio_2017_2023': round(retention_df['retention_rate'].mean(), 2),
    'retention_min': round(retention_df['retention_rate'].min(), 2),
    'retention_max': round(retention_df['retention_rate'].max(), 2),
    'anno_retention_min': int(retention_df.loc[retention_df['retention_rate'].idxmin(), 'anno']),
    'anno_retention_max': int(retention_df.loc[retention_df['retention_rate'].idxmax(), 'anno']),
    'totale_persi_2017_2023': int(retention_df['persi'].sum()),
    'media_persi_anno': int(retention_df['persi'].mean()),
    'totale_nuovi_2017_2023': int(retention_df['nuovi'].sum()),
    'media_nuovi_anno': int(retention_df['nuovi'].mean()),
    'saldo_netto_2017_2023': int(retention_df['nuovi'].sum() - retention_df['persi'].sum()),
}

# ============================================================================
# SEZIONE 10: STATISTICHE CIRCOLI (10 metriche)
# ============================================================================
print("\n10. STATISTICHE CIRCOLI")

circoli_stats = df.groupby('MmbGroup').agg({
    'MmbCode': 'count',
    'GareGiocate': 'sum'
}).sort_values('MmbCode', ascending=False)

stats['circoli'] = {
    'circoli_totali': len(circoli_stats),
    'circolo_piu_grande': circoli_stats.index[0],
    'circolo_piu_grande_tesserati': int(circoli_stats.iloc[0]['MmbCode']),
    'media_tesserati_per_circolo': round(circoli_stats['MmbCode'].mean(), 2),
    'mediana_tesserati_per_circolo': int(circoli_stats['MmbCode'].median()),
    'circoli_con_meno_10_tesserati': len(circoli_stats[circoli_stats['MmbCode'] < 10]),
    'circoli_con_10_50_tesserati': len(circoli_stats[(circoli_stats['MmbCode'] >= 10) & (circoli_stats['MmbCode'] < 50)]),
    'circoli_con_50_100_tesserati': len(circoli_stats[(circoli_stats['MmbCode'] >= 50) & (circoli_stats['MmbCode'] < 100)]),
    'circoli_con_100plus_tesserati': len(circoli_stats[circoli_stats['MmbCode'] >= 100]),
    'top10_circoli_concentrazione_pct': round(circoli_stats.head(10)['MmbCode'].sum() / len(df) * 100, 2),
}

# ============================================================================
# CONTEGGIO TOTALE METRICHE
# ============================================================================
total_metrics = 0
for section, data in stats.items():
    if isinstance(data, dict):
        total_metrics += len(data)
    else:
        total_metrics += 1

print(f"\n{'='*80}")
print(f"TOTALE METRICHE CALCOLATE: {total_metrics}")
print(f"{'='*80}")

# Salvataggio JSON
output_file = '/home/ubuntu/bridge_analysis/results/statistiche_avanzate.json'
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(stats, f, indent=2, ensure_ascii=False)

print(f"\n✓ Statistiche salvate in: {output_file}")

# Creazione CSV per ogni sezione
for section, data in stats.items():
    if isinstance(data, dict) and section != 'per_anno':
        df_section = pd.DataFrame([data])
        csv_file = f'/home/ubuntu/bridge_analysis/results/stats_{section}.csv'
        df_section.to_csv(csv_file, index=False)
        print(f"✓ CSV salvato: {csv_file}")

# CSV speciale per statistiche per anno
if 'per_anno' in stats:
    df_years = pd.DataFrame(stats['per_anno']).T
    df_years.index.name = 'Anno'
    csv_file = '/home/ubuntu/bridge_analysis/results/stats_per_anno.csv'
    df_years.to_csv(csv_file)
    print(f"✓ CSV salvato: {csv_file}")

print("\n✓ Analisi statistica avanzata completata!")
