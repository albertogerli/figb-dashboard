#!/usr/bin/env python3
"""
ANALISI BRIDGE A SCUOLA
=======================

Script per analizzare in dettaglio i programmi scolastici e i corsi Bridge:
- Corsi adulti ("Scuola Bridge") - adulti che fanno corsi nei circoli
- Studenti veri ("Ist.Scolastici", "Studente CAS") - ragazzi nelle scuole
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
RESULTS_DIR = OUTPUT_DIR / 'results_scuola'
RESULTS_DIR.mkdir(exist_ok=True)


def main():
    print("=" * 70)
    print("ANALISI BRIDGE A SCUOLA")
    print("=" * 70)

    # Carica dati
    print("\n1. Caricamento dati...")
    df = pd.read_csv(OUTPUT_DIR / 'dati_unificati_2017_2025.csv')
    print(f"   Record totali: {len(df):,}")

    # Separa tipologie
    corsi_adulti = df[df['MbtDesc'] == 'Scuola Bridge'].copy()
    studenti = df[df['MbtDesc'].isin(['Ist.Scolastici', 'Studente CAS', 'CAS Giovanile'])].copy()

    print(f"\n   Corsi Adulti (Scuola Bridge): {len(corsi_adulti):,} record, {corsi_adulti['MmbCode'].nunique():,} persone")
    print(f"   Studenti (Ist.Scolastici/CAS): {len(studenti):,} record, {studenti['MmbCode'].nunique():,} persone")

    # ==========================================================================
    # ANALISI CORSI ADULTI
    # ==========================================================================
    print("\n" + "=" * 70)
    print("2. ANALISI CORSI ADULTI")
    print("=" * 70)

    # Trend annuale
    trend_adulti = corsi_adulti.groupby('Anno').agg({
        'MmbCode': 'nunique',
        'Anni': 'mean'
    }).rename(columns={'MmbCode': 'Iscritti', 'Anni': 'EtaMedia'})
    trend_adulti['EtaMedia'] = trend_adulti['EtaMedia'].round(1)
    print("\n   Trend annuale corsi adulti:")
    print(trend_adulti.to_string())

    # Per regione
    regione_adulti = corsi_adulti.groupby('GrpArea').agg({
        'MmbCode': 'nunique',
        'Anni': 'mean',
        'Anno': lambda x: (x == x.max()).sum()  # Attivi nell'ultimo anno
    }).rename(columns={'MmbCode': 'TotaleIscritti', 'Anni': 'EtaMedia', 'Anno': 'AttiviUltimoAnno'})
    regione_adulti['EtaMedia'] = regione_adulti['EtaMedia'].round(1)
    regione_adulti = regione_adulti.sort_values('TotaleIscritti', ascending=False)

    # Per associazione
    ass_adulti = corsi_adulti.groupby('Associazione').agg({
        'MmbCode': 'nunique',
        'Anni': 'mean',
        'GrpArea': 'first'
    }).rename(columns={'MmbCode': 'Iscritti', 'Anni': 'EtaMedia', 'GrpArea': 'Regione'})
    ass_adulti['EtaMedia'] = ass_adulti['EtaMedia'].round(1)
    ass_adulti = ass_adulti.sort_values('Iscritti', ascending=False)

    # Conversione a tesserati regolari
    tessere_regolari = ['Ordinario Sportivo', 'Agonista', 'Ordinario Amatoriale', 'Non Agonista']
    regolari = df[df['MbtDesc'].isin(tessere_regolari)]

    corsisti_set = set(corsi_adulti['MmbCode'].unique())
    regolari_set = set(regolari['MmbCode'].unique())
    convertiti_adulti = corsisti_set & regolari_set

    tasso_conv_adulti = len(convertiti_adulti) / len(corsisti_set) * 100
    print(f"\n   Conversione adulti: {len(convertiti_adulti):,} su {len(corsisti_set):,} ({tasso_conv_adulti:.1f}%)")

    # Analisi conversione per anno di prima iscrizione
    prima_iscrizione = corsi_adulti.groupby('MmbCode')['Anno'].min().reset_index()
    prima_iscrizione.columns = ['MmbCode', 'AnnoPrimaIscrizione']
    prima_iscrizione['Convertito'] = prima_iscrizione['MmbCode'].isin(convertiti_adulti)

    conv_per_anno = prima_iscrizione.groupby('AnnoPrimaIscrizione').agg({
        'MmbCode': 'count',
        'Convertito': 'sum'
    }).rename(columns={'MmbCode': 'NuoviCorsisti', 'Convertito': 'PoiConvertiti'})
    conv_per_anno['TassoConversione'] = (conv_per_anno['PoiConvertiti'] / conv_per_anno['NuoviCorsisti'] * 100).round(1)

    # ==========================================================================
    # ANALISI STUDENTI
    # ==========================================================================
    print("\n" + "=" * 70)
    print("3. ANALISI STUDENTI (SCUOLE)")
    print("=" * 70)

    # Trend annuale
    trend_studenti = studenti.groupby('Anno').agg({
        'MmbCode': 'nunique',
        'Anni': 'mean'
    }).rename(columns={'MmbCode': 'Iscritti', 'Anni': 'EtaMedia'})
    trend_studenti['EtaMedia'] = trend_studenti['EtaMedia'].round(1)
    print("\n   Trend annuale studenti:")
    print(trend_studenti.to_string())

    # Per regione
    regione_studenti = studenti.groupby('GrpArea').agg({
        'MmbCode': 'nunique',
        'Anni': 'mean'
    }).rename(columns={'MmbCode': 'TotaleIscritti', 'Anni': 'EtaMedia'})
    regione_studenti['EtaMedia'] = regione_studenti['EtaMedia'].round(1)
    regione_studenti = regione_studenti.sort_values('TotaleIscritti', ascending=False)

    # Per scuola/associazione
    scuole = studenti.groupby('Associazione').agg({
        'MmbCode': 'nunique',
        'Anni': 'mean',
        'GrpArea': 'first',
        'Anno': ['min', 'max', 'nunique']
    })
    scuole.columns = ['Studenti', 'EtaMedia', 'Regione', 'AnnoInizio', 'AnnoFine', 'AnniAttivi']
    scuole['EtaMedia'] = scuole['EtaMedia'].round(1)
    scuole = scuole.sort_values('Studenti', ascending=False)

    # Conversione studenti
    studenti_set = set(studenti['MmbCode'].unique())
    convertiti_studenti = studenti_set & regolari_set

    tasso_conv_studenti = len(convertiti_studenti) / len(studenti_set) * 100
    print(f"\n   Conversione studenti: {len(convertiti_studenti):,} su {len(studenti_set):,} ({tasso_conv_studenti:.1f}%)")

    # Analisi conversione studenti per anno
    prima_iscr_stud = studenti.groupby('MmbCode')['Anno'].min().reset_index()
    prima_iscr_stud.columns = ['MmbCode', 'AnnoPrimaIscrizione']
    prima_iscr_stud['Convertito'] = prima_iscr_stud['MmbCode'].isin(convertiti_studenti)

    conv_stud_per_anno = prima_iscr_stud.groupby('AnnoPrimaIscrizione').agg({
        'MmbCode': 'count',
        'Convertito': 'sum'
    }).rename(columns={'MmbCode': 'NuoviStudenti', 'Convertito': 'PoiConvertiti'})
    conv_stud_per_anno['TassoConversione'] = (conv_stud_per_anno['PoiConvertiti'] / conv_stud_per_anno['NuoviStudenti'] * 100).round(1)

    # ==========================================================================
    # ANALISI IMPATTO COVID
    # ==========================================================================
    print("\n" + "=" * 70)
    print("4. ANALISI IMPATTO COVID")
    print("=" * 70)

    # Pre-COVID (2018-2019 media)
    pre_covid_adulti = trend_adulti.loc[2018:2019, 'Iscritti'].mean()
    pre_covid_studenti = trend_studenti.loc[2018:2019, 'Iscritti'].mean()

    # 2020 (anno COVID)
    covid_adulti = trend_adulti.loc[2020, 'Iscritti'] if 2020 in trend_adulti.index else 0
    covid_studenti = trend_studenti.loc[2020, 'Iscritti'] if 2020 in trend_studenti.index else 0

    # Post-COVID (2024)
    post_covid_adulti = trend_adulti.loc[2024, 'Iscritti'] if 2024 in trend_adulti.index else 0
    post_covid_studenti = trend_studenti.loc[2024, 'Iscritti'] if 2024 in trend_studenti.index else 0

    print(f"\n   CORSI ADULTI:")
    print(f"   - Pre-COVID (media 2018-19): {pre_covid_adulti:.0f}")
    print(f"   - Anno COVID (2020): {covid_adulti} ({100*covid_adulti/pre_covid_adulti:.0f}% del pre-COVID)")
    print(f"   - Recupero 2024: {post_covid_adulti} ({100*post_covid_adulti/pre_covid_adulti:.0f}% del pre-COVID)")

    print(f"\n   STUDENTI:")
    print(f"   - Pre-COVID (media 2018-19): {pre_covid_studenti:.0f}")
    print(f"   - Anno COVID (2020): {covid_studenti} ({100*covid_studenti/pre_covid_studenti:.0f}% del pre-COVID)")
    print(f"   - Recupero 2024: {post_covid_studenti} ({100*post_covid_studenti/pre_covid_studenti:.0f}% del pre-COVID)")

    # ==========================================================================
    # SALVATAGGIO RISULTATI
    # ==========================================================================
    print("\n" + "=" * 70)
    print("5. SALVATAGGIO RISULTATI")
    print("=" * 70)

    # Summary JSON
    summary = {
        'corsi_adulti': {
            'totale_record': int(len(corsi_adulti)),
            'persone_uniche': int(corsi_adulti['MmbCode'].nunique()),
            'eta_media': float(corsi_adulti['Anni'].mean().round(1)),
            'tasso_conversione': round(tasso_conv_adulti, 1),
            'convertiti': int(len(convertiti_adulti)),
            'pre_covid_media': float(pre_covid_adulti),
            'anno_covid_2020': int(covid_adulti),
            'recupero_2024': int(post_covid_adulti),
            'recupero_percentuale': round(100 * post_covid_adulti / pre_covid_adulti, 1)
        },
        'studenti': {
            'totale_record': int(len(studenti)),
            'persone_uniche': int(studenti['MmbCode'].nunique()),
            'eta_media': float(studenti['Anni'].mean().round(1)),
            'tasso_conversione': round(tasso_conv_studenti, 1),
            'convertiti': int(len(convertiti_studenti)),
            'pre_covid_media': float(pre_covid_studenti),
            'anno_covid_2020': int(covid_studenti),
            'recupero_2024': int(post_covid_studenti),
            'recupero_percentuale': round(100 * post_covid_studenti / pre_covid_studenti, 1)
        }
    }

    with open(RESULTS_DIR / 'summary_scuola.json', 'w') as f:
        json.dump(summary, f, indent=2)
    print(f"   Salvato summary_scuola.json")

    # Trend CSV
    trend_adulti.reset_index().to_csv(RESULTS_DIR / 'trend_corsi_adulti.csv', index=False)
    trend_studenti.reset_index().to_csv(RESULTS_DIR / 'trend_studenti.csv', index=False)
    print(f"   Salvato trend_corsi_adulti.csv e trend_studenti.csv")

    # Regioni CSV
    regione_adulti.reset_index().to_csv(RESULTS_DIR / 'corsi_per_regione.csv', index=False)
    regione_studenti.reset_index().to_csv(RESULTS_DIR / 'studenti_per_regione.csv', index=False)
    print(f"   Salvato corsi_per_regione.csv e studenti_per_regione.csv")

    # Associazioni/Scuole CSV
    ass_adulti.reset_index().to_csv(RESULTS_DIR / 'top_circoli_corsi.csv', index=False)
    scuole.reset_index().to_csv(RESULTS_DIR / 'scuole_attive.csv', index=False)
    print(f"   Salvato top_circoli_corsi.csv e scuole_attive.csv")

    # Conversione per anno CSV
    conv_per_anno.reset_index().to_csv(RESULTS_DIR / 'conversione_adulti_per_anno.csv', index=False)
    conv_stud_per_anno.reset_index().to_csv(RESULTS_DIR / 'conversione_studenti_per_anno.csv', index=False)
    print(f"   Salvato conversione_adulti_per_anno.csv e conversione_studenti_per_anno.csv")

    # Lista convertiti (per eventuale analisi dettagliata)
    convertiti_df = pd.DataFrame({
        'MmbCode': list(convertiti_adulti | convertiti_studenti),
        'TipoOrigine': ['CorsoAdulti' if m in convertiti_adulti else 'Studente'
                       for m in (convertiti_adulti | convertiti_studenti)]
    })
    convertiti_df.to_csv(RESULTS_DIR / 'lista_convertiti.csv', index=False)
    print(f"   Salvato lista_convertiti.csv ({len(convertiti_df)} record)")

    # ==========================================================================
    # RIEPILOGO
    # ==========================================================================
    print("\n" + "=" * 70)
    print("RIEPILOGO FINALE")
    print("=" * 70)
    print(f"""
    CORSI ADULTI ("Scuola Bridge"):
    - {corsi_adulti['MmbCode'].nunique():,} persone uniche
    - Eta media: {corsi_adulti['Anni'].mean():.1f} anni
    - Conversione a tesserati: {tasso_conv_adulti:.1f}%
    - Recupero post-COVID: {100*post_covid_adulti/pre_covid_adulti:.0f}%

    STUDENTI (Scuole):
    - {studenti['MmbCode'].nunique():,} studenti unici
    - Eta media: {studenti['Anni'].mean():.1f} anni
    - Conversione a tesserati: {tasso_conv_studenti:.1f}%
    - Recupero post-COVID: {100*post_covid_studenti/pre_covid_studenti:.0f}% (CRITICO!)

    INSIGHT CHIAVE:
    - I corsi adulti convertono 8x meglio degli studenti ({tasso_conv_adulti:.0f}% vs {tasso_conv_studenti:.0f}%)
    - Il programma scolastico e' in GRAVE difficolta' post-COVID
    - Solo {post_covid_studenti} studenti nel 2024 vs {pre_covid_studenti:.0f} nel pre-COVID
    """)


if __name__ == '__main__':
    main()
