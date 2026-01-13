#!/usr/bin/env python3
"""
Script per arricchire i dati con informazioni sulle province
e calcolare statistiche territoriali con popolazione
"""

import pandas as pd
import numpy as np
from pathlib import Path
from province_mapping import (
    get_provincia_from_city,
    is_citta_metropolitana,
    PROVINCE_POPOLAZIONE,
    REGIONE_POPOLAZIONE,
    CITTA_METROPOLITANE,
    PROVINCIA_TO_REGIONE
)

# Paths
BASE_DIR = Path(__file__).parent
OUTPUT_DIR = BASE_DIR / 'output'
RESULTS_DIR = OUTPUT_DIR / 'results_v2'

def main():
    print("=" * 60)
    print("ARRICCHIMENTO DATI CON PROVINCE E POPOLAZIONE")
    print("=" * 60)

    # Carica dati
    print("\n📂 Caricamento dati...")
    df = pd.read_csv(OUTPUT_DIR / 'dati_unificati_2017_2025.csv')
    print(f"   Record totali: {len(df):,}")

    # Analizza colonna AdmCity
    print(f"\n📍 Analisi città...")
    citta_uniche = df['AdmCity'].dropna().unique()
    print(f"   Città uniche nei dati: {len(citta_uniche):,}")

    # Aggiungi colonna Provincia
    print("\n🔄 Mapping città -> provincia...")
    df['Provincia'] = df['AdmCity'].apply(get_provincia_from_city)

    # Statistiche mapping
    n_mapped = df['Provincia'].notna().sum()
    pct_mapped = n_mapped / len(df) * 100
    print(f"   Record con provincia identificata: {n_mapped:,} ({pct_mapped:.1f}%)")

    # Città non mappate
    citta_non_mappate = df[df['Provincia'].isna()]['AdmCity'].dropna().unique()
    print(f"   Città non mappate: {len(citta_non_mappate)}")

    # Mostra top città non mappate per frequenza
    if len(citta_non_mappate) > 0:
        freq_non_mappate = df[df['Provincia'].isna()].groupby('AdmCity').size().sort_values(ascending=False)
        print("\n   Top 20 città da mappare (per frequenza):")
        for city, count in freq_non_mappate.head(20).items():
            if pd.notna(city):
                print(f"      - {city}: {count} record")

    # Aggiungi flag città metropolitana
    df['IsCittaMetropolitana'] = df['Provincia'].apply(lambda x: is_citta_metropolitana(x) if pd.notna(x) else False)

    # Salva dati arricchiti
    print("\n💾 Salvataggio dati arricchiti...")
    df.to_csv(OUTPUT_DIR / 'dati_unificati_2017_2025.csv', index=False)
    print(f"   Salvato: dati_unificati_2017_2025.csv")

    # ============================================
    # GENERA STATISTICHE PER PROVINCIA
    # ============================================
    print("\n" + "=" * 60)
    print("GENERAZIONE STATISTICHE TERRITORIALI")
    print("=" * 60)

    # Filtra solo record con provincia
    df_prov = df[df['Provincia'].notna()].copy()

    # 1. STATISTICHE PER PROVINCIA (ultimo anno disponibile)
    print("\n📊 Statistiche per provincia (2025)...")
    ultimo_anno = df_prov['Anno'].max()
    df_ultimo = df_prov[df_prov['Anno'] == ultimo_anno]

    prov_stats = df_ultimo.groupby('Provincia').agg({
        'MmbCode': 'nunique',
        'GareGiocate': 'mean',
        'Anni': 'mean',
        'PuntiCampionati': 'sum',
        'IsAgonista': 'sum'
    }).reset_index()
    prov_stats.columns = ['Provincia', 'Tesserati', 'GareMedie', 'EtaMedia', 'PuntiTotali', 'Agonisti']

    # Aggiungi popolazione e tasso penetrazione
    prov_stats['Popolazione'] = prov_stats['Provincia'].map(PROVINCE_POPOLAZIONE)
    prov_stats['TesseratiPer100k'] = prov_stats.apply(
        lambda row: (row['Tesserati'] / row['Popolazione'] * 100000) if row['Popolazione'] > 0 else 0,
        axis=1
    )
    prov_stats['IsCittaMetropolitana'] = prov_stats['Provincia'].apply(is_citta_metropolitana)
    prov_stats['Regione'] = prov_stats['Provincia'].map(PROVINCIA_TO_REGIONE)

    # Ordina per tesserati
    prov_stats = prov_stats.sort_values('Tesserati', ascending=False)
    prov_stats.to_csv(RESULTS_DIR / 'province_summary.csv', index=False)
    print(f"   Salvato: province_summary.csv ({len(prov_stats)} province)")

    # 2. TREND TEMPORALE PER PROVINCIA
    print("\n📈 Trend temporale per provincia...")
    trend_prov = df_prov.groupby(['Provincia', 'Anno']).agg({
        'MmbCode': 'nunique'
    }).reset_index()
    trend_prov.columns = ['Provincia', 'Anno', 'Tesserati']
    trend_prov.to_csv(RESULTS_DIR / 'province_trend.csv', index=False)
    print(f"   Salvato: province_trend.csv")

    # 3. STATISTICHE PER REGIONE CON POPOLAZIONE
    print("\n🗺️ Statistiche per regione con popolazione...")
    reg_stats = df_ultimo.groupby('GrpArea').agg({
        'MmbCode': 'nunique',
        'GareGiocate': 'mean',
        'Anni': 'mean',
        'PuntiCampionati': 'sum',
        'IsAgonista': 'sum'
    }).reset_index()
    reg_stats.columns = ['Regione', 'Tesserati', 'GareMedie', 'EtaMedia', 'PuntiTotali', 'Agonisti']

    reg_stats['Popolazione'] = reg_stats['Regione'].map(REGIONE_POPOLAZIONE)
    reg_stats['TesseratiPer100k'] = reg_stats.apply(
        lambda row: (row['Tesserati'] / row['Popolazione'] * 100000) if row['Popolazione'] > 0 else 0,
        axis=1
    )
    reg_stats = reg_stats.sort_values('Tesserati', ascending=False)
    reg_stats.to_csv(RESULTS_DIR / 'regioni_popolazione.csv', index=False)
    print(f"   Salvato: regioni_popolazione.csv")

    # 4. CONFRONTO CITTÀ METROPOLITANE VS ALTRE PROVINCE
    print("\n🏙️ Confronto città metropolitane vs altre...")
    df_ultimo['TipoProvincia'] = df_ultimo['IsCittaMetropolitana'].map({True: 'Città Metropolitana', False: 'Altra Provincia'})

    tipo_stats = df_ultimo.groupby('TipoProvincia').agg({
        'MmbCode': 'nunique',
        'GareGiocate': 'mean',
        'Anni': 'mean',
        'IsAgonista': 'mean'
    }).reset_index()
    tipo_stats.columns = ['Tipo', 'Tesserati', 'GareMedie', 'EtaMedia', 'PctAgonisti']
    tipo_stats['PctAgonisti'] = tipo_stats['PctAgonisti'] * 100
    tipo_stats.to_csv(RESULTS_DIR / 'confronto_citta_metropolitane.csv', index=False)
    print(f"   Salvato: confronto_citta_metropolitane.csv")

    # 5. STATISTICHE CITTA METROPOLITANE DETTAGLIATE
    print("\n🏙️ Dettaglio città metropolitane...")
    cm_stats = prov_stats[prov_stats['IsCittaMetropolitana']].copy()
    cm_stats = cm_stats.sort_values('Tesserati', ascending=False)
    cm_stats.to_csv(RESULTS_DIR / 'citta_metropolitane_dettaglio.csv', index=False)
    print(f"   Salvato: citta_metropolitane_dettaglio.csv")

    # ============================================
    # RIEPILOGO
    # ============================================
    print("\n" + "=" * 60)
    print("RIEPILOGO")
    print("=" * 60)

    print(f"\n📊 Tesserati {ultimo_anno}:")
    print(f"   Totali: {df_ultimo['MmbCode'].nunique():,}")
    print(f"   In città metropolitane: {df_ultimo[df_ultimo['IsCittaMetropolitana']]['MmbCode'].nunique():,}")
    print(f"   In altre province: {df_ultimo[~df_ultimo['IsCittaMetropolitana']]['MmbCode'].nunique():,}")

    print(f"\n🏆 Top 5 province per tesserati:")
    for _, row in prov_stats.head(5).iterrows():
        cm_flag = "🏙️" if row['IsCittaMetropolitana'] else ""
        print(f"   {row['Provincia']}: {row['Tesserati']:,} ({row['TesseratiPer100k']:.1f}/100k) {cm_flag}")

    print(f"\n📈 Top 5 province per penetrazione (tesserati/100k):")
    top_penetrazione = prov_stats[prov_stats['Tesserati'] >= 20].nlargest(5, 'TesseratiPer100k')
    for _, row in top_penetrazione.iterrows():
        cm_flag = "🏙️" if row['IsCittaMetropolitana'] else ""
        print(f"   {row['Provincia']}: {row['TesseratiPer100k']:.1f}/100k ({row['Tesserati']} tess.) {cm_flag}")

    print("\n✅ Arricchimento completato!")


if __name__ == '__main__':
    main()
