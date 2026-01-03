#!/usr/bin/env python3
"""
Script per l'unificazione dei dati di tesseramento FIGB 2017-2025
Combina i dati storici con i nuovi dati 2025
"""

import pandas as pd
import numpy as np
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# Percorsi
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR
OUTPUT_DIR = BASE_DIR / 'output'
OUTPUT_DIR.mkdir(exist_ok=True)

print("=" * 80)
print("UNIFICAZIONE DATI TESSERAMENTO FIGB 2017-2025")
print("=" * 80)

# Caricamento dati storici 2017-2024
print("\n1. Caricamento dati storici (2017-2024)...")
excel_storico = DATA_DIR / 'Dati dal 17.xlsx'
xls = pd.ExcelFile(excel_storico)

dfs = {}
for year in range(2017, 2025):
    sheet_name = str(year)
    df = pd.read_excel(excel_storico, sheet_name=sheet_name)
    df['Anno'] = year
    dfs[year] = df
    print(f"   Anno {year}: {len(df):,} tesserati")

# Caricamento dati 2025
print("\n2. Caricamento dati 2025...")
excel_2025 = DATA_DIR / '2025 Dopo Natale.xlsx'
df_2025 = pd.read_excel(excel_2025, sheet_name='Foglio1')
df_2025['Anno'] = 2025
dfs[2025] = df_2025
print(f"   Anno 2025: {len(df_2025):,} tesserati")

# Unione di tutti i dataframe
print("\n3. Unificazione dataset...")
df_all = pd.concat(dfs.values(), ignore_index=True)
print(f"   Totale record: {len(df_all):,}")
print(f"   Giocatori unici: {df_all['MmbCode'].nunique():,}")

# Creazione fasce d'età
print("\n4. Creazione variabili derivate...")
df_all['FasciaEta'] = pd.cut(df_all['Anni'],
                             bins=[0, 18, 30, 40, 50, 60, 70, 80, 90, 120],
                             labels=['<18', '18-30', '30-40', '40-50', '50-60', '60-70', '70-80', '80-90', '90+'])

# Creazione fasce di punti
df_all['FasciaPunti'] = pd.cut(df_all['PuntiTotali'],
                               bins=[-1, 0, 500, 2000, 5000, 10000, 20000, 50000, 500000],
                               labels=['0', '1-500', '501-2000', '2001-5000', '5001-10000',
                                      '10001-20000', '20001-50000', '50000+'])

# Identificazione tipologia tesserato
df_all['IsScuolaBridge'] = df_all['MbtDesc'].str.contains('Scuola Bridge', case=False, na=False)
df_all['IsAgonista'] = df_all['MbtDesc'].str.contains('Agonista', case=False, na=False)

# Statistiche riepilogative
print("\n5. Statistiche riepilogative per anno:")
print("-" * 60)
yearly_stats = df_all.groupby('Anno').agg({
    'MmbCode': 'count',
    'GareGiocate': 'sum',
    'Anni': 'mean'
}).round(1)
yearly_stats.columns = ['Tesserati', 'Gare Totali', 'Età Media']
print(yearly_stats)

# Variazione anno su anno
print("\n6. Variazioni anno su anno:")
print("-" * 60)
for i, year in enumerate(range(2018, 2026)):
    prev = yearly_stats.loc[year-1, 'Tesserati']
    curr = yearly_stats.loc[year, 'Tesserati']
    var = ((curr - prev) / prev) * 100
    emoji = "📈" if var > 0 else "📉"
    print(f"   {year-1} → {year}: {var:+.1f}% {emoji} ({int(curr - prev):+,})")

# Salvataggio
output_file = OUTPUT_DIR / 'dati_unificati_2017_2025.csv'
df_all.to_csv(output_file, index=False)
print(f"\n✓ Dataset unificato salvato in: {output_file}")

# Nota: Parquet rimosso per problemi di tipi misti nelle colonne

# Statistiche finali
print("\n" + "=" * 80)
print("RIEPILOGO FINALE")
print("=" * 80)
print(f"Periodo: 2017-2025 ({len(dfs)} anni)")
print(f"Totale tesseramenti: {len(df_all):,}")
print(f"Giocatori unici: {df_all['MmbCode'].nunique():,}")
print(f"Circoli unici: {df_all['MmbGroup'].nunique():,}")
print(f"Regioni: {df_all['GrpArea'].nunique()}")
print(f"Età media: {df_all['Anni'].mean():.1f} anni")
print(f"Tesserati Scuola Bridge: {df_all['IsScuolaBridge'].sum():,}")
print("=" * 80)
