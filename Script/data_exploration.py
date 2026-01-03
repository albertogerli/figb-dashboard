#!/usr/bin/env python3
"""
Script per l'analisi esplorativa dei dati di tesseramento del bridge
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# Configurazione stile
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (14, 8)
plt.rcParams['font.size'] = 10

# Caricamento dati
print("Caricamento dati da Excel...")
excel_file = '/home/ubuntu/upload/Datidal17.xlsx'
xls = pd.ExcelFile(excel_file)

# Dizionario per contenere tutti i dataframe
dfs = {}
for year in range(2017, 2025):
    sheet_name = str(year)
    df = pd.read_excel(excel_file, sheet_name=sheet_name)
    df['Anno'] = year
    dfs[year] = df
    print(f"Anno {year}: {len(df)} record")

# Unione di tutti i dataframe
df_all = pd.concat(dfs.values(), ignore_index=True)
print(f"\nTotale record: {len(df_all)}")

# Analisi struttura dati
print("\n" + "="*80)
print("STRUTTURA DEI DATI")
print("="*80)
print("\nColonne disponibili:")
print(df_all.columns.tolist())
print("\nTipi di dati:")
print(df_all.dtypes)
print("\nValori mancanti:")
print(df_all.isnull().sum())

# Statistiche descrittive
print("\n" + "="*80)
print("STATISTICHE DESCRITTIVE")
print("="*80)
print(df_all.describe())

# Analisi valori unici per colonne chiave
print("\n" + "="*80)
print("VALORI UNICI PER COLONNE CHIAVE")
print("="*80)
print(f"\nNumero di giocatori unici (MmbCode): {df_all['MmbCode'].nunique()}")
print(f"Numero di circoli unici (MmbGroup): {df_all['MmbGroup'].nunique()}")
print(f"Numero di regioni uniche (GrpArea): {df_all['GrpArea'].nunique()}")

print("\nRegioni:")
print(df_all['GrpArea'].value_counts().sort_index())

print("\nCategorie di età (CatLabel):")
print(df_all['CatLabel'].value_counts().sort_index())

print("\nTipologie di tessera (MbtDesc):")
print(df_all['MbtDesc'].value_counts())

print("\nSesso:")
print(df_all['MmbSex'].value_counts())

# Salvataggio dataset unificato
output_file = '/home/ubuntu/bridge_analysis/dati_unificati.csv'
df_all.to_csv(output_file, index=False)
print(f"\n\nDataset unificato salvato in: {output_file}")

# Analisi preliminare per anno
print("\n" + "="*80)
print("ANALISI PER ANNO")
print("="*80)
yearly_stats = df_all.groupby('Anno').agg({
    'MmbCode': 'count',
    'GareGiocate': 'sum',
    'PuntiCampionati': 'sum',
    'PuntiTotali': 'sum'
}).round(0)
yearly_stats.columns = ['Tesserati', 'Gare Totali', 'Punti Campionati', 'Punti Totali']
print(yearly_stats)

print("\n✓ Analisi esplorativa completata")
