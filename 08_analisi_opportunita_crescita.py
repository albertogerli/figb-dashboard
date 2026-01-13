#!/usr/bin/env python3
"""
ANALISI OPPORTUNITA' DI CRESCITA
================================

Script per identificare segmenti di crescita facili da aggredire:
1. Quasi Agganciati - 1 anno, poche gare, poi spariti
2. Dormienti - Tesserati che non giocano gare
3. Gap Demografico - Fasce età sotto-rappresentate
4. Opportunità Geografiche - Province con potenziale inespresso
5. Effetto COVID Persistente - Chi non è tornato dopo 2020
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
RESULTS_DIR = OUTPUT_DIR / 'results_opportunita'
RESULTS_DIR.mkdir(exist_ok=True)

# Import dati popolazione
try:
    from province_mapping import PROVINCE_POPOLAZIONE, REGIONE_POPOLAZIONE
    HAS_POPULATION = True
except ImportError:
    HAS_POPULATION = False
    PROVINCE_POPOLAZIONE = {}
    REGIONE_POPOLAZIONE = {}

# Popolazione Italia per fascia età (ISTAT 2024 - approssimata)
POPOLAZIONE_PER_ETA = {
    '<18': 9_200_000,
    '18-30': 7_100_000,
    '30-40': 6_800_000,
    '40-50': 8_900_000,
    '50-60': 9_600_000,
    '60-70': 8_200_000,
    '70-80': 6_100_000,
    '80-90': 3_400_000,
    '90+': 800_000,
}


def main():
    print("=" * 70)
    print("ANALISI OPPORTUNITA' DI CRESCITA")
    print("=" * 70)

    # Carica dati
    print("\n1. Caricamento dati...")
    df = pd.read_csv(OUTPUT_DIR / 'dati_unificati_2017_2025.csv')
    print(f"   Record totali: {len(df):,}")

    anno_corrente = df['Anno'].max()
    print(f"   Anno più recente: {anno_corrente}")

    # =========================================================================
    # 1. QUASI AGGANCIATI
    # =========================================================================
    print("\n" + "=" * 70)
    print("2. ANALISI 'QUASI AGGANCIATI'")
    print("   (1 anno di tessera, poche gare, poi spariti)")
    print("=" * 70)

    # Trova chi ha fatto solo 1-2 anni e poi sparito
    # Escludi tessere scuola
    tessere_regolari = ['Ordinario Sportivo', 'Agonista', 'Ordinario Amatoriale', 'Non Agonista']
    df_regolari = df[df['MbtDesc'].isin(tessere_regolari)].copy()

    # Storia per persona
    storia_giocatori = df_regolari.groupby('MmbCode').agg({
        'Anno': ['min', 'max', 'count', list],
        'GareGiocate': 'sum',
        'Associazione': 'first',
        'GrpArea': 'first',
        'Anni': 'last',
        'MmbSex': 'first',
        'MmbName': 'first'
    }).reset_index()
    storia_giocatori.columns = ['MmbCode', 'AnnoInizio', 'AnnoFine', 'AnniTotali', 'AnniLista',
                                 'GareTotali', 'Associazione', 'Regione', 'Eta', 'Sesso', 'Nome']

    # Quasi Agganciati: 1-2 anni, spariti da almeno 2 anni, poche gare
    quasi_agganciati = storia_giocatori[
        (storia_giocatori['AnniTotali'] <= 2) &
        (storia_giocatori['AnnoFine'] <= anno_corrente - 2) &
        (storia_giocatori['GareTotali'] < 20) &
        (storia_giocatori['Eta'] < 80)  # Età ragionevole
    ].copy()

    quasi_agganciati['GarePerAnno'] = (quasi_agganciati['GareTotali'] / quasi_agganciati['AnniTotali']).round(1)
    quasi_agganciati['AnniAssenza'] = anno_corrente - quasi_agganciati['AnnoFine']

    print(f"\n   Quasi Agganciati trovati: {len(quasi_agganciati):,}")
    print(f"   Profilo medio:")
    print(f"   - Anni tessera: {quasi_agganciati['AnniTotali'].mean():.1f}")
    print(f"   - Gare totali: {quasi_agganciati['GareTotali'].mean():.1f}")
    print(f"   - Età media: {quasi_agganciati['Eta'].mean():.1f}")
    print(f"   - Assenza media: {quasi_agganciati['AnniAssenza'].mean():.1f} anni")

    # Distribuzione per regione
    quasi_per_regione = quasi_agganciati.groupby('Regione').agg({
        'MmbCode': 'count',
        'GareTotali': 'mean',
        'Eta': 'mean'
    }).reset_index()
    quasi_per_regione.columns = ['Regione', 'NumQuasiAgganciati', 'GareMedie', 'EtaMedia']
    quasi_per_regione = quasi_per_regione.sort_values('NumQuasiAgganciati', ascending=False)

    print(f"\n   Top 5 regioni:")
    print(quasi_per_regione.head().to_string(index=False))

    # =========================================================================
    # 2. DORMIENTI
    # =========================================================================
    print("\n" + "=" * 70)
    print("3. ANALISI 'DORMIENTI'")
    print("   (Tesserati attivi che non giocano gare)")
    print("=" * 70)

    # Tesserati nell'ultimo anno
    tesserati_ultimo_anno = df_regolari[df_regolari['Anno'] == anno_corrente].copy()

    # Dormienti: 0 gare nell'ultimo anno
    dormienti = tesserati_ultimo_anno[tesserati_ultimo_anno['GareGiocate'] == 0].copy()

    # Aggiungi storia
    storia_dict = storia_giocatori.set_index('MmbCode')[['AnniTotali', 'GareTotali']].to_dict('index')
    dormienti['AnniTotali'] = dormienti['MmbCode'].map(lambda x: storia_dict.get(x, {}).get('AnniTotali', 1))
    dormienti['GareStoriche'] = dormienti['MmbCode'].map(lambda x: storia_dict.get(x, {}).get('GareTotali', 0))

    print(f"\n   Tesserati {anno_corrente}: {len(tesserati_ultimo_anno):,}")
    print(f"   Dormienti (0 gare): {len(dormienti):,} ({100*len(dormienti)/len(tesserati_ultimo_anno):.1f}%)")

    # Categorizza dormienti
    dormienti['Categoria'] = 'Nuovo Dormiente'
    dormienti.loc[dormienti['AnniTotali'] >= 3, 'Categoria'] = 'Ex-Attivo'
    dormienti.loc[(dormienti['AnniTotali'] >= 2) & (dormienti['GareStoriche'] > 0), 'Categoria'] = 'Rallentato'

    print(f"\n   Categorie Dormienti:")
    print(dormienti['Categoria'].value_counts().to_string())

    # Per regione
    dormienti_regione = dormienti.groupby('GrpArea').agg({
        'MmbCode': 'count',
        'Anni': 'mean'
    }).reset_index()
    dormienti_regione.columns = ['Regione', 'NumDormienti', 'EtaMedia']
    dormienti_regione = dormienti_regione.sort_values('NumDormienti', ascending=False)

    # Per associazione (top 20)
    dormienti_assoc = dormienti.groupby('Associazione').agg({
        'MmbCode': 'count',
        'Anni': 'mean',
        'GrpArea': 'first'
    }).reset_index()
    dormienti_assoc.columns = ['Associazione', 'NumDormienti', 'EtaMedia', 'Regione']
    dormienti_assoc = dormienti_assoc.sort_values('NumDormienti', ascending=False)

    print(f"\n   Top 10 associazioni con più dormienti:")
    print(dormienti_assoc.head(10).to_string(index=False))

    # =========================================================================
    # 3. GAP DEMOGRAFICO
    # =========================================================================
    print("\n" + "=" * 70)
    print("4. ANALISI GAP DEMOGRAFICO")
    print("   (Fasce età sotto-rappresentate vs popolazione)")
    print("=" * 70)

    # Bridgisti per fascia età (ultimo anno)
    tesserati_eta = tesserati_ultimo_anno.groupby('FasciaEta')['MmbCode'].nunique().to_dict()

    # Calcola penetrazione
    gap_demografico = []
    for fascia, pop in POPOLAZIONE_PER_ETA.items():
        bridgisti = tesserati_eta.get(fascia, 0)
        penetrazione = bridgisti / pop * 100000  # per 100k abitanti
        gap_demografico.append({
            'FasciaEta': fascia,
            'Popolazione': pop,
            'Bridgisti': bridgisti,
            'Per100k': round(penetrazione, 1)
        })

    gap_df = pd.DataFrame(gap_demografico)

    # Calcola "potenziale" (se avessero stessa penetrazione dei 70-80)
    max_penetrazione = gap_df[gap_df['FasciaEta'] == '70-80']['Per100k'].values[0]
    gap_df['Potenziale'] = (gap_df['Popolazione'] * max_penetrazione / 100000).astype(int)
    gap_df['Gap'] = gap_df['Potenziale'] - gap_df['Bridgisti']
    gap_df['GapPct'] = ((gap_df['Potenziale'] - gap_df['Bridgisti']) / gap_df['Potenziale'] * 100).round(1)

    print(f"\n   Penetrazione per 100k abitanti:")
    print(gap_df.to_string(index=False))

    # Focus 60-70
    focus_60_70 = gap_df[gap_df['FasciaEta'] == '60-70'].iloc[0]
    print(f"\n   FOCUS 60-70 anni:")
    print(f"   - Popolazione: {focus_60_70['Popolazione']:,}")
    print(f"   - Bridgisti: {focus_60_70['Bridgisti']:,}")
    print(f"   - Penetrazione: {focus_60_70['Per100k']} per 100k")
    print(f"   - Se avesse penetrazione 70-80: {focus_60_70['Potenziale']:,} bridgisti")
    print(f"   - GAP: {focus_60_70['Gap']:,} bridgisti potenziali!")

    # =========================================================================
    # 4. OPPORTUNITA' GEOGRAFICHE
    # =========================================================================
    print("\n" + "=" * 70)
    print("5. ANALISI OPPORTUNITA' GEOGRAFICHE")
    print("   (Province con alto potenziale inespresso)")
    print("=" * 70)

    if HAS_POPULATION:
        # Tesserati per provincia
        if 'Provincia' in df.columns:
            tess_provincia = tesserati_ultimo_anno.groupby('Provincia')['MmbCode'].nunique().to_dict()
        else:
            # Approssima da città
            tess_provincia = {}

        # Calcola opportunità per provincia
        opp_geo = []
        for prov, pop in PROVINCE_POPOLAZIONE.items():
            bridgisti = tess_provincia.get(prov, 0)
            penetrazione = bridgisti / pop * 100000 if pop > 0 else 0

            # Stima popolazione 60+
            pop_60_plus = pop * 0.28  # ~28% della popolazione è 60+

            opp_geo.append({
                'Provincia': prov,
                'Popolazione': pop,
                'Pop60Plus': int(pop_60_plus),
                'Bridgisti': bridgisti,
                'Per100k': round(penetrazione, 1)
            })

        opp_df = pd.DataFrame(opp_geo)

        # Penetrazione media nazionale
        pen_media = opp_df[opp_df['Bridgisti'] > 0]['Per100k'].mean()
        opp_df['Potenziale'] = (opp_df['Popolazione'] * pen_media / 100000).astype(int)
        opp_df['Gap'] = opp_df['Potenziale'] - opp_df['Bridgisti']

        # Province con maggior gap (popolazione alta, penetrazione bassa)
        opp_df['Score'] = opp_df['Pop60Plus'] * (1 - opp_df['Per100k'] / pen_media)
        opp_df = opp_df.sort_values('Score', ascending=False)

        print(f"\n   Top 15 province con maggior potenziale:")
        print(opp_df[['Provincia', 'Popolazione', 'Bridgisti', 'Per100k', 'Gap']].head(15).to_string(index=False))
    else:
        print("   Dati popolazione non disponibili.")
        opp_df = pd.DataFrame()

    # =========================================================================
    # 5. EFFETTO COVID PERSISTENTE
    # =========================================================================
    print("\n" + "=" * 70)
    print("6. ANALISI EFFETTO COVID PERSISTENTE")
    print("   (Chi non è tornato dopo il 2020)")
    print("=" * 70)

    # Tesserati pre-COVID (2019)
    tess_2019 = set(df_regolari[df_regolari['Anno'] == 2019]['MmbCode'].unique())
    tess_2020 = set(df_regolari[df_regolari['Anno'] == 2020]['MmbCode'].unique())
    tess_post = set(df_regolari[df_regolari['Anno'] >= 2022]['MmbCode'].unique())

    # Chi c'era nel 2019 ma non è più tornato dal 2022 in poi
    persi_covid = tess_2019 - tess_post

    # Profilo dei persi COVID
    persi_covid_df = storia_giocatori[storia_giocatori['MmbCode'].isin(persi_covid)].copy()

    print(f"\n   Tesserati 2019: {len(tess_2019):,}")
    print(f"   Non tornati dopo 2022: {len(persi_covid):,} ({100*len(persi_covid)/len(tess_2019):.1f}%)")

    if len(persi_covid_df) > 0:
        print(f"\n   Profilo 'Persi COVID':")
        print(f"   - Età media attuale: {persi_covid_df['Eta'].mean():.1f}")
        print(f"   - Gare medie (quando attivi): {persi_covid_df['GareTotali'].mean():.1f}")
        print(f"   - Anni di tessera: {persi_covid_df['AnniTotali'].mean():.1f}")

        # Segmenta per recuperabilità
        persi_covid_df['Recuperabile'] = 'Difficile'
        persi_covid_df.loc[
            (persi_covid_df['Eta'] < 75) &
            (persi_covid_df['GareTotali'] > 30) &
            (persi_covid_df['AnniTotali'] >= 3),
            'Recuperabile'
        ] = 'Alta Priorità'
        persi_covid_df.loc[
            (persi_covid_df['Eta'] < 80) &
            (persi_covid_df['GareTotali'] > 10),
            'Recuperabile'
        ] = 'Media Priorità'

        print(f"\n   Segmentazione Recuperabilità:")
        print(persi_covid_df['Recuperabile'].value_counts().to_string())

        # Per regione
        persi_regione = persi_covid_df.groupby('Regione').agg({
            'MmbCode': 'count',
            'Eta': 'mean',
            'GareTotali': 'mean'
        }).reset_index()
        persi_regione.columns = ['Regione', 'PersiCovid', 'EtaMedia', 'GareMedie']
        persi_regione = persi_regione.sort_values('PersiCovid', ascending=False)

    # =========================================================================
    # 6. RIEPILOGO E PRIORITÀ
    # =========================================================================
    print("\n" + "=" * 70)
    print("7. RIEPILOGO OPPORTUNITA'")
    print("=" * 70)

    riepilogo = {
        'quasi_agganciati': {
            'totale': len(quasi_agganciati),
            'descrizione': 'Tesserati 1-2 anni con poche gare, poi spariti',
            'effort': 'BASSO',
            'potenziale': 'ALTO - Conoscono già il bridge'
        },
        'dormienti': {
            'totale': len(dormienti),
            'descrizione': f'Tesserati {anno_corrente} con 0 gare',
            'effort': 'BASSO',
            'potenziale': 'ALTO - Già pagano la tessera'
        },
        'gap_60_70': {
            'gap': int(focus_60_70['Gap']) if 'Gap' in focus_60_70 else 0,
            'descrizione': 'Potenziali bridgisti 60-70 non raggiunti',
            'effort': 'MEDIO',
            'potenziale': 'MOLTO ALTO - Fascia età ideale'
        },
        'persi_covid': {
            'totale': len(persi_covid),
            'alta_priorita': len(persi_covid_df[persi_covid_df['Recuperabile'] == 'Alta Priorità']) if len(persi_covid_df) > 0 else 0,
            'descrizione': 'Ex-bridgisti pre-COVID non tornati',
            'effort': 'MEDIO',
            'potenziale': 'ALTO - Esperienza e affetto per il gioco'
        }
    }

    print(f"""
    ┌─────────────────────────────────────────────────────────────────────┐
    │  OPPORTUNITA' DI CRESCITA - PRIORITA'                              │
    ├─────────────────────────────────────────────────────────────────────┤
    │  1. DORMIENTI: {riepilogo['dormienti']['totale']:,} persone                                      │
    │     → Già tesserati, basta attivarli!                              │
    │                                                                     │
    │  2. QUASI AGGANCIATI: {riepilogo['quasi_agganciati']['totale']:,} persone                              │
    │     → Hanno provato, ricontattarli                                 │
    │                                                                     │
    │  3. PERSI COVID: {riepilogo['persi_covid']['totale']:,} persone ({riepilogo['persi_covid']['alta_priorita']:,} alta priorità)           │
    │     → Ex-attivi, potrebbero tornare                                │
    │                                                                     │
    │  4. GAP 60-70: ~{riepilogo['gap_60_70']['gap']:,} potenziali                                   │
    │     → Fascia ideale sotto-penetrata                                │
    └─────────────────────────────────────────────────────────────────────┘
    """)

    # =========================================================================
    # SALVATAGGIO
    # =========================================================================
    print("\n" + "=" * 70)
    print("8. SALVATAGGIO RISULTATI")
    print("=" * 70)

    # Summary JSON
    with open(RESULTS_DIR / 'summary_opportunita.json', 'w') as f:
        json.dump(riepilogo, f, indent=2, default=str)
    print("   Salvato summary_opportunita.json")

    # Quasi Agganciati
    quasi_agganciati[['MmbCode', 'Nome', 'Associazione', 'Regione', 'Eta', 'AnniTotali',
                       'GareTotali', 'AnnoFine', 'AnniAssenza']].to_csv(
        RESULTS_DIR / 'quasi_agganciati.csv', index=False
    )
    quasi_per_regione.to_csv(RESULTS_DIR / 'quasi_agganciati_regione.csv', index=False)
    print(f"   Salvato quasi_agganciati.csv ({len(quasi_agganciati)} record)")

    # Dormienti
    dormienti[['MmbCode', 'MmbName', 'Associazione', 'GrpArea', 'Anni', 'Categoria',
               'AnniTotali', 'GareStoriche']].to_csv(
        RESULTS_DIR / 'dormienti.csv', index=False
    )
    dormienti_regione.to_csv(RESULTS_DIR / 'dormienti_regione.csv', index=False)
    dormienti_assoc.to_csv(RESULTS_DIR / 'dormienti_associazione.csv', index=False)
    print(f"   Salvato dormienti.csv ({len(dormienti)} record)")

    # Gap demografico
    gap_df.to_csv(RESULTS_DIR / 'gap_demografico.csv', index=False)
    print("   Salvato gap_demografico.csv")

    # Opportunità geografiche
    if len(opp_df) > 0:
        opp_df.to_csv(RESULTS_DIR / 'opportunita_geografiche.csv', index=False)
        print("   Salvato opportunita_geografiche.csv")

    # Persi COVID
    if len(persi_covid_df) > 0:
        persi_covid_df[['MmbCode', 'Nome', 'Associazione', 'Regione', 'Eta',
                        'AnniTotali', 'GareTotali', 'Recuperabile']].to_csv(
            RESULTS_DIR / 'persi_covid.csv', index=False
        )
        persi_regione.to_csv(RESULTS_DIR / 'persi_covid_regione.csv', index=False)
        print(f"   Salvato persi_covid.csv ({len(persi_covid_df)} record)")

    print("\n   COMPLETATO!")


if __name__ == '__main__':
    main()
