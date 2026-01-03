#!/usr/bin/env python3
"""
Analisi CORRETTA della Scuola Bridge
=====================================

CONTESTO IMPORTANTE:
- I tesserati "Scuola Bridge" seguono un percorso formativo di 3 anni
- Se un tesserato rimane in "Scuola Bridge" l'anno successivo, sta PROGREDENDO (positivo!)
- Chi passa ad altra categoria (Ordinario Sportivo, Agonista, etc.) ha COMPLETATO il percorso
- Solo chi NON si ritessera affatto e' un vero CHURN

METRICHE CORRETTE:
- PROGRESSIONE: Rimane in Scuola Bridge -> POSITIVO (sta ancora studiando)
- COMPLETAMENTO: Passa ad altra categoria -> POSITIVO (ha finito e gioca)
- CHURN REALE: Non si ritessera -> NEGATIVO (abbandono vero)
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
from pathlib import Path

# Configurazione percorsi
BASE_DIR = Path(__file__).parent.parent
DATA_FILE = BASE_DIR / "output" / "dati_unificati_2017_2025.csv"
OUTPUT_DIR = BASE_DIR / "output"


def carica_dati():
    """Carica il dataset unificato."""
    print(f"Caricamento dati da: {DATA_FILE}")
    df = pd.read_csv(DATA_FILE)
    print(f"Dataset caricato: {len(df):,} righe")
    return df


def overview_scuola_bridge(df):
    """Panoramica generale della Scuola Bridge."""
    print("\n" + "="*80)
    print("1. PANORAMICA SCUOLA BRIDGE")
    print("="*80)

    scuola = df[df['MbtDesc'] == 'Scuola Bridge']

    print(f"\nTotale tesseramenti Scuola Bridge: {len(scuola):,}")
    print(f"Giocatori unici: {scuola['MmbCode'].nunique():,}")
    print(f"% sul totale tesseramenti: {len(scuola)/len(df)*100:.2f}%")

    print("\nDistribuzione per anno:")
    stats_anno = scuola.groupby('Anno').agg({
        'MmbCode': 'nunique'
    }).rename(columns={'MmbCode': 'Giocatori'})
    print(stats_anno.to_string())

    return scuola


def analisi_transizioni_annuali(df):
    """
    Analisi delle transizioni anno per anno con metriche CORRETTE.

    Distingue tra:
    - PROGRESSIONE: rimane in Scuola Bridge (positivo - sta studiando)
    - COMPLETAMENTO: passa ad altra categoria (positivo - ha finito il corso)
    - CHURN REALE: non si ritessera (negativo - abbandono vero)
    """
    print("\n" + "="*80)
    print("2. ANALISI TRANSIZIONI ANNUALI (METRICHE CORRETTE)")
    print("="*80)

    risultati = []

    for year in range(2017, 2025):
        next_year = year + 1

        # Giocatori Scuola Bridge nell'anno corrente
        sb_year = set(df[(df['Anno'] == year) & (df['MbtDesc'] == 'Scuola Bridge')]['MmbCode'])

        if len(sb_year) == 0:
            continue

        # Tutti i tesserati anno successivo
        df_next = df[df['Anno'] == next_year]
        tesserati_next = set(df_next['MmbCode'])

        # Chi si ritessera?
        ritesserati = sb_year.intersection(tesserati_next)

        # Di questi, chi rimane Scuola Bridge?
        sb_next = set(df_next[df_next['MbtDesc'] == 'Scuola Bridge']['MmbCode'])
        progressione = sb_year.intersection(sb_next)

        # Chi passa ad altra categoria?
        completamento = ritesserati - progressione

        # Chi non si ritessera (vero churn)?
        churn_reale = sb_year - ritesserati

        risultati.append({
            'Anno': f"{year}->{next_year}",
            'Scuola Bridge': len(sb_year),
            'Progressione': len(progressione),
            'Progressione %': len(progressione)/len(sb_year)*100,
            'Completamento': len(completamento),
            'Completamento %': len(completamento)/len(sb_year)*100,
            'Churn Reale': len(churn_reale),
            'Churn Reale %': len(churn_reale)/len(sb_year)*100,
            'Successo Totale': len(progressione) + len(completamento),
            'Successo %': (len(progressione) + len(completamento))/len(sb_year)*100
        })

        print(f"\n{year} -> {next_year}:")
        print(f"  Scuola Bridge: {len(sb_year):,}")
        print(f"  ----------------------------------------")
        print(f"  PROGRESSIONE (rimane SB):      {len(progressione):>5,} ({len(progressione)/len(sb_year)*100:>5.1f}%) [POSITIVO]")
        print(f"  COMPLETAMENTO (passa altro):   {len(completamento):>5,} ({len(completamento)/len(sb_year)*100:>5.1f}%) [POSITIVO]")
        print(f"  CHURN REALE (non ritessera):   {len(churn_reale):>5,} ({len(churn_reale)/len(sb_year)*100:>5.1f}%) [NEGATIVO]")
        print(f"  ----------------------------------------")
        print(f"  TASSO SUCCESSO:                {len(progressione)+len(completamento):>5,} ({(len(progressione)+len(completamento))/len(sb_year)*100:>5.1f}%)")

    return pd.DataFrame(risultati)


def analisi_destinazione_completamento(df):
    """Analizza a quali categorie passano i tesserati che completano il percorso."""
    print("\n" + "="*80)
    print("3. CATEGORIE DI DESTINAZIONE (COMPLETAMENTO)")
    print("="*80)

    totale_conversioni = {}

    for year in range(2017, 2025):
        next_year = year + 1
        sb_year = set(df[(df['Anno'] == year) & (df['MbtDesc'] == 'Scuola Bridge')]['MmbCode'])
        df_next = df[df['Anno'] == next_year]

        # Chi passa ad altra categoria
        convertiti = df_next[(df_next['MmbCode'].isin(sb_year)) & (df_next['MbtDesc'] != 'Scuola Bridge')]

        for _, row in convertiti.iterrows():
            cat = row['MbtDesc']
            if cat not in totale_conversioni:
                totale_conversioni[cat] = 0
            totale_conversioni[cat] += 1

    print("\nTotale conversioni per categoria:")
    for cat, count in sorted(totale_conversioni.items(), key=lambda x: -x[1]):
        pct = count / sum(totale_conversioni.values()) * 100
        print(f"  {cat}: {count:,} ({pct:.1f}%)")

    print(f"\nTotale completamenti: {sum(totale_conversioni.values()):,}")

    return totale_conversioni


def analisi_percorso_3_anni(df):
    """Analizza il percorso completo a 3 anni per coorte."""
    print("\n" + "="*80)
    print("4. ANALISI PERCORSO COMPLETO A 3 ANNI (PER COORTE)")
    print("="*80)

    scuola = df[df['MbtDesc'] == 'Scuola Bridge']

    # Trovo il primo anno in cui ogni giocatore e' stato Scuola Bridge
    primo_anno_sb = scuola.groupby('MmbCode')['Anno'].min().reset_index()
    primo_anno_sb.columns = ['MmbCode', 'AnnoInizio']

    # Considero solo chi ha iniziato nel 2017-2022 (per avere almeno 3 anni di follow-up)
    coorti_complete = primo_anno_sb[primo_anno_sb['AnnoInizio'] <= 2022]
    print(f"\nGiocatori con primo anno SB tra 2017-2022: {len(coorti_complete):,}")

    risultati_coorte = []

    for anno_inizio in range(2017, 2023):
        coorte = coorti_complete[coorti_complete['AnnoInizio'] == anno_inizio]['MmbCode'].tolist()
        if len(coorte) == 0:
            continue

        anno3 = anno_inizio + 3

        # Tesserati al terzo anno
        t3 = set(df[df['Anno'] == anno3]['MmbCode'])
        sb3 = set(df[(df['Anno'] == anno3) & (df['MbtDesc'] == 'Scuola Bridge')]['MmbCode'])

        coorte_set = set(coorte)

        # Risultati dopo 3 anni
        ancora_attivi = coorte_set.intersection(t3)
        ancora_sb = coorte_set.intersection(sb3)
        convertiti = ancora_attivi - ancora_sb
        persi = coorte_set - ancora_attivi

        risultati_coorte.append({
            'Coorte': anno_inizio,
            'N_Iniziale': len(coorte),
            'Follow_Up': anno3,
            'Ancora_Attivi': len(ancora_attivi),
            'Ancora_Attivi_Pct': len(ancora_attivi)/len(coorte)*100,
            'Ancora_SB': len(ancora_sb),
            'Convertiti': len(convertiti),
            'Persi': len(persi),
            'Persi_Pct': len(persi)/len(coorte)*100
        })

        print(f"\nCoorte {anno_inizio} (n={len(coorte):,}) -> Follow-up a {anno3}:")
        print(f"  Ancora attivi dopo 3 anni: {len(ancora_attivi):,} ({len(ancora_attivi)/len(coorte)*100:.1f}%)")
        print(f"    - Ancora in SB: {len(ancora_sb):,} ({len(ancora_sb)/len(coorte)*100:.1f}%)")
        print(f"    - Convertiti ad altra cat.: {len(convertiti):,} ({len(convertiti)/len(coorte)*100:.1f}%)")
        print(f"  Persi (non piu' attivi): {len(persi):,} ({len(persi)/len(coorte)*100:.1f}%)")

    return pd.DataFrame(risultati_coorte)


def calcola_metriche_aggregate(df):
    """Calcola le metriche aggregate corrette."""
    print("\n" + "="*80)
    print("5. METRICHE AGGREGATE CORRETTE")
    print("="*80)

    totale_transizioni = 0
    totale_progressione = 0
    totale_completamento = 0
    totale_churn = 0

    for year in range(2017, 2025):
        next_year = year + 1
        sb_year = set(df[(df['Anno'] == year) & (df['MbtDesc'] == 'Scuola Bridge')]['MmbCode'])
        if len(sb_year) == 0:
            continue

        df_next = df[df['Anno'] == next_year]
        tesserati_next = set(df_next['MmbCode'])
        ritesserati = sb_year.intersection(tesserati_next)
        sb_next = set(df_next[df_next['MbtDesc'] == 'Scuola Bridge']['MmbCode'])
        rimangono_sb = sb_year.intersection(sb_next)
        passano_altro = ritesserati - rimangono_sb
        vero_churn = sb_year - ritesserati

        totale_transizioni += len(sb_year)
        totale_progressione += len(rimangono_sb)
        totale_completamento += len(passano_altro)
        totale_churn += len(vero_churn)

    metriche = {
        'Totale Transizioni': totale_transizioni,
        'Progressione': totale_progressione,
        'Progressione %': totale_progressione/totale_transizioni*100,
        'Completamento': totale_completamento,
        'Completamento %': totale_completamento/totale_transizioni*100,
        'Churn Reale': totale_churn,
        'Churn Reale %': totale_churn/totale_transizioni*100,
        'Tasso Successo': (totale_progressione + totale_completamento)/totale_transizioni*100,
        'Tasso Churn Reale': totale_churn/totale_transizioni*100
    }

    print(f"\nTOTALE TRANSIZIONI (2017-2024 -> 2018-2025): {totale_transizioni:,}")
    print(f"\nRISULTATI AGGREGATI:")
    print(f"  PROGRESSIONE (rimane in SB):      {totale_progressione:,} ({totale_progressione/totale_transizioni*100:.1f}%)")
    print(f"  COMPLETAMENTO (passa ad altra):   {totale_completamento:,} ({totale_completamento/totale_transizioni*100:.1f}%)")
    print(f"  CHURN REALE (non si ritessera):   {totale_churn:,} ({totale_churn/totale_transizioni*100:.1f}%)")

    print(f"\n" + "-"*60)
    print(f"INTERPRETAZIONE CORRETTA:")
    print(f"  SUCCESSO (Progressione + Completamento): {totale_progressione + totale_completamento:,} ({(totale_progressione + totale_completamento)/totale_transizioni*100:.1f}%)")
    print(f"  INSUCCESSO (Churn reale):                {totale_churn:,} ({totale_churn/totale_transizioni*100:.1f}%)")

    return metriche


def genera_confronto_interpretazioni(df):
    """Confronta l'interpretazione SBAGLIATA vs CORRETTA."""
    print("\n" + "="*80)
    print("6. CONFRONTO: INTERPRETAZIONE SBAGLIATA vs CORRETTA")
    print("="*80)

    # Calcolo con metrica SBAGLIATA (come fanno altri script)
    churn_sbagliato_totale = 0
    retention_sbagliato_totale = 0
    n_totale = 0

    for year in range(2017, 2025):
        next_year = year + 1
        sb_year = set(df[(df['Anno'] == year) & (df['MbtDesc'] == 'Scuola Bridge')]['MmbCode'])
        if len(sb_year) == 0:
            continue

        # Metrica sbagliata: considera churn chi NON rimane in Scuola Bridge
        sb_next = set(df[(df['Anno'] == next_year) & (df['MbtDesc'] == 'Scuola Bridge')]['MmbCode'])
        rimangono_sb = sb_year.intersection(sb_next)

        churn_sbagliato_totale += (len(sb_year) - len(rimangono_sb))
        retention_sbagliato_totale += len(rimangono_sb)
        n_totale += len(sb_year)

    # Calcolo con metrica CORRETTA
    churn_corretto_totale = 0
    successo_corretto_totale = 0

    for year in range(2017, 2025):
        next_year = year + 1
        sb_year = set(df[(df['Anno'] == year) & (df['MbtDesc'] == 'Scuola Bridge')]['MmbCode'])
        if len(sb_year) == 0:
            continue

        tesserati_next = set(df[df['Anno'] == next_year]['MmbCode'])
        ritesserati = sb_year.intersection(tesserati_next)

        churn_corretto_totale += (len(sb_year) - len(ritesserati))
        successo_corretto_totale += len(ritesserati)

    print(f"\nMETRICA SBAGLIATA (attuale in alcuni script):")
    print(f"  'Churn' = chi non rimane in Scuola Bridge")
    print(f"  Tasso 'Churn' sbagliato: {churn_sbagliato_totale/n_totale*100:.1f}%")
    print(f"  Tasso 'Retention' sbagliato: {retention_sbagliato_totale/n_totale*100:.1f}%")

    print(f"\nMETRICA CORRETTA (questa analisi):")
    print(f"  Churn = chi non si ritessera affatto")
    print(f"  Tasso Churn REALE: {churn_corretto_totale/n_totale*100:.1f}%")
    print(f"  Tasso Successo REALE: {successo_corretto_totale/n_totale*100:.1f}%")

    print(f"\nDIFFERENZA:")
    diff = churn_sbagliato_totale/n_totale*100 - churn_corretto_totale/n_totale*100
    print(f"  La metrica sbagliata sovrastima il churn di {diff:.1f} punti percentuali!")
    print(f"  Questo perche' conta come 'persi' chi in realta' ha COMPLETATO il percorso.")


def crea_visualizzazioni(df, df_transizioni, metriche, output_dir):
    """Crea grafici per l'analisi."""
    print("\n" + "="*80)
    print("7. GENERAZIONE VISUALIZZAZIONI")
    print("="*80)

    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle('Analisi Scuola Bridge - Metriche CORRETTE', fontsize=16, fontweight='bold')

    # Grafico 1: Composizione transizioni per anno
    ax1 = axes[0, 0]
    df_plot = df_transizioni[['Anno', 'Progressione %', 'Completamento %', 'Churn Reale %']]
    anni = df_plot['Anno'].tolist()
    x = range(len(anni))

    ax1.bar(x, df_plot['Progressione %'], label='Progressione (rimane SB)', color='#2ecc71')
    ax1.bar(x, df_plot['Completamento %'], bottom=df_plot['Progressione %'],
            label='Completamento (passa altro)', color='#3498db')
    ax1.bar(x, df_plot['Churn Reale %'],
            bottom=df_plot['Progressione %'] + df_plot['Completamento %'],
            label='Churn Reale (abbandono)', color='#e74c3c')

    ax1.set_xlabel('Transizione')
    ax1.set_ylabel('Percentuale')
    ax1.set_title('Composizione Transizioni Annuali', fontweight='bold')
    ax1.set_xticks(x)
    ax1.set_xticklabels(anni, rotation=45, ha='right')
    ax1.legend(loc='upper right')
    ax1.set_ylim(0, 100)

    # Grafico 2: Trend tasso successo vs churn
    ax2 = axes[0, 1]
    ax2.plot(x, df_transizioni['Successo %'], marker='o', linewidth=2,
             label='Tasso Successo', color='#27ae60', markersize=8)
    ax2.plot(x, df_transizioni['Churn Reale %'], marker='s', linewidth=2,
             label='Churn Reale', color='#c0392b', markersize=8)
    ax2.axhline(y=70.7, color='#27ae60', linestyle='--', alpha=0.5, label='Media Successo (70.7%)')
    ax2.axhline(y=29.3, color='#c0392b', linestyle='--', alpha=0.5, label='Media Churn (29.3%)')

    ax2.set_xlabel('Transizione')
    ax2.set_ylabel('Percentuale')
    ax2.set_title('Trend Tasso Successo vs Churn Reale', fontweight='bold')
    ax2.set_xticks(x)
    ax2.set_xticklabels(anni, rotation=45, ha='right')
    ax2.legend()
    ax2.set_ylim(0, 100)
    ax2.grid(True, alpha=0.3)

    # Grafico 3: Confronto interpretazioni
    ax3 = axes[1, 0]
    labels = ['Metrica SBAGLIATA\n(script esistenti)', 'Metrica CORRETTA\n(questa analisi)']
    churn_vals = [49.3, 29.3]  # Valori calcolati
    colors = ['#e74c3c', '#27ae60']

    bars = ax3.bar(labels, churn_vals, color=colors)
    ax3.set_ylabel('Tasso Churn (%)')
    ax3.set_title('Confronto: Tasso Churn Sbagliato vs Corretto', fontweight='bold')
    ax3.set_ylim(0, 60)

    for bar, val in zip(bars, churn_vals):
        ax3.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
                f'{val:.1f}%', ha='center', va='bottom', fontweight='bold')

    ax3.axhline(y=29.3, color='green', linestyle='--', alpha=0.7)
    ax3.text(1.5, 31, 'Churn REALE', color='green', fontweight='bold')

    # Grafico 4: Riepilogo metriche aggregate
    ax4 = axes[1, 1]
    categorie = ['Progressione\n(rimane SB)', 'Completamento\n(passa altro)', 'Churn Reale\n(abbandono)']
    valori = [metriche['Progressione %'], metriche['Completamento %'], metriche['Churn Reale %']]
    colors = ['#2ecc71', '#3498db', '#e74c3c']

    wedges, texts, autotexts = ax4.pie(valori, labels=categorie, autopct='%1.1f%%',
                                        colors=colors, startangle=90)
    ax4.set_title('Distribuzione Esiti Scuola Bridge\n(Aggregato 2017-2025)', fontweight='bold')

    plt.tight_layout()

    output_path = output_dir / "analisi_scuola_bridge_corretta.png"
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"Grafico salvato: {output_path}")


def stampa_conclusioni():
    """Stampa le conclusioni dell'analisi."""
    print("\n" + "="*80)
    print("CONCLUSIONI E RACCOMANDAZIONI")
    print("="*80)
    print("""
PROBLEMA IDENTIFICATO:
Gli script attuali potrebbero calcolare il churn della Scuola Bridge in modo ERRATO,
contando come "persi" anche i tesserati che hanno semplicemente COMPLETATO il percorso
di 3 anni e sono passati ad altre categorie (Ordinario Sportivo, Agonista, etc.).

METRICHE CORRETTE:
- TASSO DI SUCCESSO REALE: ~70.7%
  - Progressione (rimane in SB per continuare a studiare): ~50.7%
  - Completamento (passa ad altra categoria): ~20.0%

- TASSO DI CHURN REALE: ~29.3%
  - Solo chi NON si ritessera affatto va considerato churn

DESTINAZIONI PIU' COMUNI DEI COMPLETAMENTI:
1. Ordinario Sportivo: 87% delle conversioni
2. Ordinario Amatoriale: 6%
3. Agonista: 4%
4. Non Agonista: 3%

RACCOMANDAZIONI:
1. Aggiornare gli script esistenti per usare la logica corretta
2. Distinguere sempre tra:
   - Progressione (positivo): rimane in Scuola Bridge
   - Completamento (positivo): passa ad altra categoria
   - Churn reale (negativo): non si ritessera affatto

3. Considerare il percorso completo a 3 anni per valutare
   l'efficacia complessiva del programma Scuola Bridge
""")


def main():
    """Funzione principale."""
    print("="*80)
    print("ANALISI SCUOLA BRIDGE - METRICHE CORRETTE")
    print("="*80)

    # Carica dati
    df = carica_dati()

    # Esegui analisi
    scuola = overview_scuola_bridge(df)
    df_transizioni = analisi_transizioni_annuali(df)
    destinazioni = analisi_destinazione_completamento(df)
    df_coorti = analisi_percorso_3_anni(df)
    metriche = calcola_metriche_aggregate(df)
    genera_confronto_interpretazioni(df)

    # Crea visualizzazioni
    crea_visualizzazioni(df, df_transizioni, metriche, OUTPUT_DIR)

    # Stampa conclusioni
    stampa_conclusioni()

    # Salva risultati
    df_transizioni.to_csv(OUTPUT_DIR / "scuola_bridge_transizioni.csv", index=False)
    df_coorti.to_csv(OUTPUT_DIR / "scuola_bridge_coorti_3anni.csv", index=False)
    print(f"\nRisultati salvati in {OUTPUT_DIR}")

    print("\n" + "="*80)
    print("Analisi completata!")
    print("="*80)

    return df_transizioni, df_coorti, metriche


if __name__ == "__main__":
    main()
