#!/usr/bin/env python3
"""
ANALISI CONVERSIONE CORSI BRIDGE
================================

Script per analizzare la conversione dei corsisti "Scuola Bridge" (percorso 3 anni)
in tesserati regolari. Identifica:
- Fattori che favoriscono la conversione
- Regioni e associazioni più efficaci
- Pattern di churn

Il tasso di conversione ottimale dovrebbe essere vicino al 100% dopo 3 anni.
"""

import pandas as pd
import numpy as np
from pathlib import Path
import json
import warnings
warnings.filterwarnings('ignore')

# Paths
BASE_DIR = Path(__file__).parent
OUTPUT_DIR = BASE_DIR / 'output'
RESULTS_DIR = OUTPUT_DIR / 'results_conversione'
RESULTS_DIR.mkdir(exist_ok=True)


def main():
    print("=" * 70)
    print("ANALISI CONVERSIONE CORSI BRIDGE")
    print("=" * 70)

    # Carica dati
    print("\n1. Caricamento dati...")
    df = pd.read_csv(OUTPUT_DIR / 'dati_unificati_2017_2025.csv')

    # Corsisti Scuola Bridge
    corsi = df[df['MbtDesc'] == 'Scuola Bridge'].copy()
    print(f"   Record corsi: {len(corsi):,}")

    # Storia di ogni corsista
    corsisti = corsi.groupby('MmbCode').agg({
        'Anno': ['min', 'max', 'count'],
        'Associazione': 'first',
        'GrpArea': 'first',
        'Anni': 'first',
        'MmbSex': 'first',
        'GareGiocate': 'sum',
        'PuntiTotali': 'sum'
    }).reset_index()
    corsisti.columns = ['MmbCode', 'AnnoInizio', 'AnnoFine', 'AnniCorso',
                        'Associazione', 'Regione', 'Eta', 'Sesso',
                        'GareTotali', 'PuntiTotali']

    print(f"   Corsisti unici totali: {len(corsisti):,}")

    # =========================================================================
    # FILTRA CORSISTI "MATURI" (che hanno avuto tempo di convertirsi)
    # =========================================================================
    # Consideriamo chi ha iniziato entro il 2022 (almeno 2 anni per decidere)
    corsisti_maturi = corsisti[corsisti['AnnoInizio'] <= 2022].copy()
    print(f"   Corsisti maturi (iniziati ≤2022): {len(corsisti_maturi):,}")

    # Identifica chi è diventato tesserato regolare
    tessere_regolari = ['Ordinario Sportivo', 'Agonista', 'Ordinario Amatoriale', 'Non Agonista']
    regolari = df[df['MbtDesc'].isin(tessere_regolari)]
    regolari_set = set(regolari['MmbCode'].unique())

    corsisti_maturi['Convertito'] = corsisti_maturi['MmbCode'].isin(regolari_set)

    n_convertiti = corsisti_maturi['Convertito'].sum()
    tasso_conv = 100 * n_convertiti / len(corsisti_maturi)

    print(f"\n   CONVERSIONE GLOBALE:")
    print(f"   Convertiti: {n_convertiti:,} su {len(corsisti_maturi):,} ({tasso_conv:.1f}%)")
    print(f"   Persi: {len(corsisti_maturi) - n_convertiti:,} ({100-tasso_conv:.1f}%)")

    # =========================================================================
    # ANALISI FATTORI DI CONVERSIONE
    # =========================================================================
    print("\n" + "=" * 70)
    print("2. ANALISI FATTORI DI CONVERSIONE")
    print("=" * 70)

    # 2.1 DURATA CORSO
    print("\n   2.1 Per DURATA CORSO:")
    conv_durata = corsisti_maturi.groupby('AnniCorso').agg({
        'MmbCode': 'count',
        'Convertito': ['sum', 'mean']
    })
    conv_durata.columns = ['Totale', 'Convertiti', 'TassoConv']
    conv_durata['TassoConv'] = (conv_durata['TassoConv'] * 100).round(1)
    conv_durata['Persi'] = conv_durata['Totale'] - conv_durata['Convertiti']
    print(conv_durata.to_string())

    # 2.2 GARE GIOCATE (il fattore più importante!)
    print("\n   2.2 Per GARE GIOCATE (FATTORE CHIAVE):")
    corsisti_maturi['FasciaGare'] = pd.cut(
        corsisti_maturi['GareTotali'],
        bins=[-1, 5, 15, 30, 60, 100, 10000],
        labels=['0-5', '6-15', '16-30', '31-60', '61-100', '100+']
    )
    conv_gare = corsisti_maturi.groupby('FasciaGare', observed=True).agg({
        'MmbCode': 'count',
        'Convertito': ['sum', 'mean']
    })
    conv_gare.columns = ['Totale', 'Convertiti', 'TassoConv']
    conv_gare['TassoConv'] = (conv_gare['TassoConv'] * 100).round(1)
    print(conv_gare.to_string())

    # 2.3 ETA'
    print("\n   2.3 Per ETA':")
    corsisti_maturi['FasciaEta'] = pd.cut(
        corsisti_maturi['Eta'],
        bins=[0, 50, 60, 70, 80, 100],
        labels=['<50', '50-60', '60-70', '70-80', '80+']
    )
    conv_eta = corsisti_maturi.groupby('FasciaEta', observed=True).agg({
        'MmbCode': 'count',
        'Convertito': ['sum', 'mean']
    })
    conv_eta.columns = ['Totale', 'Convertiti', 'TassoConv']
    conv_eta['TassoConv'] = (conv_eta['TassoConv'] * 100).round(1)
    print(conv_eta.to_string())

    # 2.4 SESSO
    print("\n   2.4 Per SESSO:")
    conv_sesso = corsisti_maturi.groupby('Sesso').agg({
        'MmbCode': 'count',
        'Convertito': ['sum', 'mean']
    })
    conv_sesso.columns = ['Totale', 'Convertiti', 'TassoConv']
    conv_sesso['TassoConv'] = (conv_sesso['TassoConv'] * 100).round(1)
    print(conv_sesso.to_string())

    # =========================================================================
    # ANALISI PER REGIONE
    # =========================================================================
    print("\n" + "=" * 70)
    print("3. CONVERSIONE PER REGIONE")
    print("=" * 70)

    conv_regione = corsisti_maturi.groupby('Regione').agg({
        'MmbCode': 'count',
        'Convertito': ['sum', 'mean'],
        'GareTotali': 'mean',
        'AnniCorso': 'mean'
    })
    conv_regione.columns = ['Corsisti', 'Convertiti', 'TassoConv', 'GareMedie', 'DurataMedia']
    conv_regione['TassoConv'] = (conv_regione['TassoConv'] * 100).round(1)
    conv_regione['GareMedie'] = conv_regione['GareMedie'].round(1)
    conv_regione['DurataMedia'] = conv_regione['DurataMedia'].round(2)
    conv_regione['Persi'] = conv_regione['Corsisti'] - conv_regione['Convertiti']
    conv_regione = conv_regione[conv_regione['Corsisti'] >= 20].sort_values('TassoConv', ascending=False)
    print(conv_regione.to_string())

    # =========================================================================
    # ANALISI PER ASSOCIAZIONE
    # =========================================================================
    print("\n" + "=" * 70)
    print("4. CONVERSIONE PER ASSOCIAZIONE")
    print("=" * 70)

    conv_ass = corsisti_maturi.groupby('Associazione').agg({
        'MmbCode': 'count',
        'Convertito': ['sum', 'mean'],
        'GareTotali': 'mean',
        'AnniCorso': 'mean',
        'Regione': 'first'
    })
    conv_ass.columns = ['Corsisti', 'Convertiti', 'TassoConv', 'GareMedie', 'DurataMedia', 'Regione']
    conv_ass['TassoConv'] = (conv_ass['TassoConv'] * 100).round(1)
    conv_ass['GareMedie'] = conv_ass['GareMedie'].round(1)
    conv_ass['DurataMedia'] = conv_ass['DurataMedia'].round(2)
    conv_ass['Persi'] = conv_ass['Corsisti'] - conv_ass['Convertiti']

    # Solo associazioni con almeno 20 corsisti
    conv_ass_filtrato = conv_ass[conv_ass['Corsisti'] >= 20].copy()

    print(f"\n   Associazioni con ≥20 corsisti: {len(conv_ass_filtrato)}")

    # Top e Bottom
    top_ass = conv_ass_filtrato.sort_values('TassoConv', ascending=False).head(15)
    bottom_ass = conv_ass_filtrato.sort_values('TassoConv', ascending=True).head(15)

    print("\n   TOP 15 (Migliore conversione):")
    print(top_ass[['Corsisti', 'Convertiti', 'TassoConv', 'GareMedie', 'Regione']].to_string())

    print("\n   BOTTOM 15 (Peggiore conversione):")
    print(bottom_ass[['Corsisti', 'Convertiti', 'TassoConv', 'GareMedie', 'Regione']].to_string())

    # =========================================================================
    # ANALISI PATTERN CHURN
    # =========================================================================
    print("\n" + "=" * 70)
    print("5. PATTERN DI CHURN (Chi abbandona)")
    print("=" * 70)

    churned = corsisti_maturi[~corsisti_maturi['Convertito']].copy()

    print(f"\n   Corsisti persi: {len(churned):,}")

    # Quando abbandonano?
    print("\n   Quando abbandonano (dopo quanti anni):")
    print(churned['AnniCorso'].value_counts().sort_index())

    # Quante gare avevano fatto?
    print("\n   Gare giocate prima di abbandonare:")
    print(churned['FasciaGare'].value_counts())

    # Profilo medio chi abbandona vs chi converte
    print("\n   PROFILO COMPARATIVO:")
    convertiti = corsisti_maturi[corsisti_maturi['Convertito']]

    profilo = pd.DataFrame({
        'Metrica': ['Gare medie', 'Durata media (anni)', 'Età media', '% Donne'],
        'Convertiti': [
            convertiti['GareTotali'].mean(),
            convertiti['AnniCorso'].mean(),
            convertiti['Eta'].mean(),
            100 * (convertiti['Sesso'] == 'F').mean()
        ],
        'Persi': [
            churned['GareTotali'].mean(),
            churned['AnniCorso'].mean(),
            churned['Eta'].mean(),
            100 * (churned['Sesso'] == 'F').mean()
        ]
    })
    profilo['Convertiti'] = profilo['Convertiti'].round(1)
    profilo['Persi'] = profilo['Persi'].round(1)
    print(profilo.to_string(index=False))

    # =========================================================================
    # SALVATAGGIO RISULTATI
    # =========================================================================
    print("\n" + "=" * 70)
    print("6. SALVATAGGIO RISULTATI")
    print("=" * 70)

    # Summary JSON
    summary = {
        'totale_corsisti_maturi': int(len(corsisti_maturi)),
        'convertiti': int(n_convertiti),
        'persi': int(len(corsisti_maturi) - n_convertiti),
        'tasso_conversione': round(tasso_conv, 1),
        'gare_medie_convertiti': round(convertiti['GareTotali'].mean(), 1),
        'gare_medie_persi': round(churned['GareTotali'].mean(), 1),
        'durata_media_convertiti': round(convertiti['AnniCorso'].mean(), 2),
        'durata_media_persi': round(churned['AnniCorso'].mean(), 2),
        'insight_chiave': {
            'conv_1_anno': float(conv_durata.loc[1, 'TassoConv']) if 1 in conv_durata.index else 0,
            'conv_3_anni': float(conv_durata.loc[3, 'TassoConv']) if 3 in conv_durata.index else 0,
            'conv_0_5_gare': float(conv_gare.loc['0-5', 'TassoConv']) if '0-5' in conv_gare.index else 0,
            'conv_100_gare': float(conv_gare.loc['100+', 'TassoConv']) if '100+' in conv_gare.index else 0,
        }
    }

    with open(RESULTS_DIR / 'summary_conversione.json', 'w') as f:
        json.dump(summary, f, indent=2)
    print("   Salvato summary_conversione.json")

    # Conversione per fattori
    conv_durata.reset_index().to_csv(RESULTS_DIR / 'conversione_per_durata.csv', index=False)
    conv_gare.reset_index().to_csv(RESULTS_DIR / 'conversione_per_gare.csv', index=False)
    conv_eta.reset_index().to_csv(RESULTS_DIR / 'conversione_per_eta.csv', index=False)
    print("   Salvato conversione_per_*.csv")

    # Per regione e associazione
    conv_regione.reset_index().to_csv(RESULTS_DIR / 'conversione_per_regione.csv', index=False)
    conv_ass.reset_index().to_csv(RESULTS_DIR / 'conversione_per_associazione.csv', index=False)
    print("   Salvato conversione_per_regione.csv e conversione_per_associazione.csv")

    # Lista corsisti con status
    corsisti_export = corsisti_maturi[['MmbCode', 'Associazione', 'Regione', 'Eta',
                                        'AnniCorso', 'GareTotali', 'Convertito']].copy()
    corsisti_export.to_csv(RESULTS_DIR / 'lista_corsisti_status.csv', index=False)
    print(f"   Salvato lista_corsisti_status.csv ({len(corsisti_export)} record)")

    # =========================================================================
    # RIEPILOGO
    # =========================================================================
    print("\n" + "=" * 70)
    print("RIEPILOGO - INSIGHT CHIAVE")
    print("=" * 70)
    print(f"""
    CONVERSIONE GLOBALE: {tasso_conv:.1f}%
    (Obiettivo ideale: >80% dopo percorso 3 anni)

    FATTORI CRITICI:
    ┌─────────────────────────────────────────────────────────────────┐
    │  GARE GIOCATE = FATTORE #1                                     │
    │  • 0-5 gare:   {summary['insight_chiave']['conv_0_5_gare']:.0f}% conversione                                 │
    │  • 100+ gare:  {summary['insight_chiave']['conv_100_gare']:.0f}% conversione                                 │
    │  → FAR GIOCARE I CORSISTI E' LA CHIAVE!                        │
    └─────────────────────────────────────────────────────────────────┘

    DURATA CORSO:
    • 1 anno:  {summary['insight_chiave']['conv_1_anno']:.0f}% conversione (troppo poco!)
    • 3 anni:  {summary['insight_chiave']['conv_3_anni']:.0f}% conversione

    PROFILO CHI ABBANDONA:
    • Gare medie: {summary['gare_medie_persi']:.0f} (vs {summary['gare_medie_convertiti']:.0f} dei convertiti)
    • Durata: {summary['durata_media_persi']:.1f} anni (vs {summary['durata_media_convertiti']:.1f})

    RACCOMANDAZIONI:
    1. Inserire i corsisti in gare "protette" fin dal primo anno
    2. Obiettivo minimo: 30 gare/anno per corsista
    3. Monitorare i circoli con bassa conversione
    4. Creare tornei dedicati ai principianti
    """)


if __name__ == '__main__':
    main()
