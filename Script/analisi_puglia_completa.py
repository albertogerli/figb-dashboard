#!/usr/bin/env python3
"""
Analisi Focus Puglia 2022-2025
==============================

Analisi dettagliata dei tesserati FIGB in Puglia con focus su:
1. Trend tesseramenti 2022-2025
2. Bridge a Scuola e conversione allievi
3. Tracciamento individuale: da allievo a giocatore con quale tessera
4. Performance per circolo
5. Confronto con media nazionale
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import json
from pathlib import Path

# Configurazione percorsi
BASE_DIR = Path(__file__).parent.parent
DATA_FILE = BASE_DIR / "output" / "dati_unificati_2017_2025.csv"
OUTPUT_DIR = BASE_DIR / "output" / "results_puglia"
CHARTS_DIR = BASE_DIR / "output" / "charts"

# Crea directory output se non esiste
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
CHARTS_DIR.mkdir(parents=True, exist_ok=True)

# Configurazione grafici
plt.style.use('seaborn-v0_8-whitegrid')
COLORS = {
    'primary': '#1e40af',
    'secondary': '#64748b',
    'success': '#16a34a',
    'warning': '#d97706',
    'danger': '#dc2626',
    'info': '#0891b2',
    'scuola_bridge': '#8b5cf6',
    'ordinario_sportivo': '#3b82f6',
    'agonista': '#ef4444',
    'altro': '#94a3b8'
}

# Anni di analisi
ANNI_ANALISI = [2022, 2023, 2024, 2025]


def carica_dati():
    """Carica il dataset unificato."""
    print(f"Caricamento dati da: {DATA_FILE}")
    df = pd.read_csv(DATA_FILE)
    print(f"Dataset caricato: {len(df):,} righe")
    return df


def filtra_puglia(df):
    """Filtra i dati per la Puglia negli anni 2022-2025."""
    df_puglia = df[(df['GrpArea'] == 'PUG') & (df['Anno'].isin(ANNI_ANALISI))]
    print(f"Record Puglia 2022-2025: {len(df_puglia):,}")
    return df_puglia


def analisi_trend_tesserati(df_puglia, df_nazionale):
    """Analisi trend tesseramenti Puglia 2022-2025."""
    print("\n" + "="*80)
    print("1. TREND TESSERAMENTI PUGLIA 2022-2025")
    print("="*80)

    # Trend per anno
    trend = df_puglia.groupby('Anno').agg({
        'MmbCode': 'nunique',
        'GareGiocate': 'mean',
        'PuntiTotali': 'mean'
    }).reset_index()
    trend.columns = ['Anno', 'Tesserati', 'GareMedia', 'PuntiMedi']

    # Calcola variazione anno su anno
    trend['Variazione'] = trend['Tesserati'].pct_change() * 100
    trend['Variazione'] = trend['Variazione'].fillna(0).round(1)

    # Breakdown per tipo tessera
    per_tessera = df_puglia.groupby(['Anno', 'MbtDesc']).agg({
        'MmbCode': 'nunique'
    }).reset_index()
    per_tessera.columns = ['Anno', 'TipoTessera', 'Tesserati']

    # Pivot per avere le tessere come colonne
    tessere_pivot = per_tessera.pivot(index='Anno', columns='TipoTessera', values='Tesserati').fillna(0)

    print("\nTrend Tesserati Puglia:")
    print(trend.to_string(index=False))

    print("\nDettaglio per tipo tessera:")
    print(tessere_pivot.to_string())

    # Confronto con nazionale per anno
    nazionale_trend = df_nazionale[df_nazionale['Anno'].isin(ANNI_ANALISI)].groupby('Anno').agg({
        'MmbCode': 'nunique'
    }).reset_index()
    nazionale_trend.columns = ['Anno', 'TesseratiNazionale']

    trend = trend.merge(nazionale_trend, on='Anno')
    trend['QuotaPuglia'] = (trend['Tesserati'] / trend['TesseratiNazionale'] * 100).round(2)

    # Salva risultati
    trend.to_csv(OUTPUT_DIR / "trend_puglia.csv", index=False)
    tessere_pivot.to_csv(OUTPUT_DIR / "tessere_puglia_per_anno.csv")

    return trend, tessere_pivot


def analisi_scuola_bridge_puglia(df_puglia, df_nazionale):
    """Analisi specifica Bridge a Scuola in Puglia."""
    print("\n" + "="*80)
    print("2. ANALISI SCUOLA BRIDGE PUGLIA")
    print("="*80)

    # Filtra Scuola Bridge
    sb_puglia = df_puglia[df_puglia['MbtDesc'] == 'Scuola Bridge']

    # Statistiche per anno
    sb_stats = sb_puglia.groupby('Anno').agg({
        'MmbCode': 'nunique',
        'GareGiocate': 'mean',
        'PuntiTotali': 'mean'
    }).reset_index()
    sb_stats.columns = ['Anno', 'Allievi', 'GareMedia', 'PuntiMedi']

    print("\nScuola Bridge Puglia per anno:")
    print(sb_stats.to_string(index=False))

    # Confronto con nazionale
    sb_nazionale = df_nazionale[
        (df_nazionale['MbtDesc'] == 'Scuola Bridge') &
        (df_nazionale['Anno'].isin(ANNI_ANALISI))
    ].groupby('Anno').agg({'MmbCode': 'nunique'}).reset_index()
    sb_nazionale.columns = ['Anno', 'AllieviNazionale']

    sb_stats = sb_stats.merge(sb_nazionale, on='Anno')
    sb_stats['QuotaPuglia'] = (sb_stats['Allievi'] / sb_stats['AlieviNazionale'] * 100).round(2)

    sb_stats.to_csv(OUTPUT_DIR / "scuola_bridge_puglia.csv", index=False)

    return sb_stats


def traccia_conversione_allievi(df, df_puglia):
    """
    Tracciamento individuale conversione allievi.
    Per ogni MmbCode che è stato Scuola Bridge in Puglia:
    - Anno primo tesseramento come allievo
    - Se/quando ha cambiato tessera
    - Tessera di destinazione
    - Attività post-conversione
    """
    print("\n" + "="*80)
    print("3. TRACCIAMENTO CONVERSIONE ALLIEVI PUGLIA")
    print("="*80)

    # Tutti gli allievi Scuola Bridge in Puglia nel periodo
    allievi_sb = df_puglia[df_puglia['MbtDesc'] == 'Scuola Bridge']
    allievi_codes = allievi_sb['MmbCode'].unique()
    print(f"\nAllievi unici Scuola Bridge in Puglia 2022-2025: {len(allievi_codes):,}")

    # Per ogni allievo, traccia la storia completa (anche fuori dal periodo)
    risultati = []

    for mmbcode in allievi_codes:
        # Storia completa del giocatore in Puglia
        storia = df[(df['MmbCode'] == mmbcode) & (df['GrpArea'] == 'PUG')].sort_values('Anno')

        # Prima apparizione come Scuola Bridge
        storia_sb = storia[storia['MbtDesc'] == 'Scuola Bridge']
        if len(storia_sb) == 0:
            continue

        anno_inizio = storia_sb['Anno'].min()
        anni_in_sb = storia_sb['Anno'].nunique()
        gare_in_sb = storia_sb['GareGiocate'].sum()

        # Verifica se ha cambiato tessera
        storia_non_sb = storia[storia['MbtDesc'] != 'Scuola Bridge']

        if len(storia_non_sb) > 0:
            # Ha convertito
            prima_conversione = storia_non_sb.sort_values('Anno').iloc[0]
            anno_conversione = prima_conversione['Anno']
            tessera_dest = prima_conversione['MbtDesc']

            # Attività post-conversione
            post_conv = storia_non_sb[storia_non_sb['Anno'] >= anno_conversione]
            gare_post = post_conv['GareGiocate'].sum()
            punti_post = post_conv['PuntiTotali'].sum()
            anni_post = post_conv['Anno'].nunique()
        else:
            # Non ha ancora convertito
            anno_conversione = None
            tessera_dest = 'Non Convertito'
            gare_post = 0
            punti_post = 0
            anni_post = 0

        # Ultimo anno attivo
        ultimo_anno = storia['Anno'].max()

        risultati.append({
            'MmbCode': mmbcode,
            'AnnoInizio': anno_inizio,
            'AnniInScuolaBridge': anni_in_sb,
            'GareInScuolaBridge': gare_in_sb,
            'Convertito': 'Sì' if anno_conversione else 'No',
            'AnnoConversione': anno_conversione,
            'TesseraDestinazione': tessera_dest,
            'AnniDopoConversione': anni_post,
            'GareDopoConversione': gare_post,
            'PuntiDopoConversione': punti_post,
            'UltimoAnnoAttivo': ultimo_anno,
            'AncoraAttivo2025': 'Sì' if ultimo_anno == 2025 else 'No'
        })

    df_conversione = pd.DataFrame(risultati)

    # Statistiche aggregate
    convertiti = df_conversione[df_conversione['Convertito'] == 'Sì']
    non_convertiti = df_conversione[df_conversione['Convertito'] == 'No']

    tasso_conversione = len(convertiti) / len(df_conversione) * 100 if len(df_conversione) > 0 else 0

    print(f"\nRISULTATI CONVERSIONE:")
    print(f"  Totale allievi tracciati: {len(df_conversione):,}")
    print(f"  Convertiti: {len(convertiti):,} ({tasso_conversione:.1f}%)")
    print(f"  Non ancora convertiti: {len(non_convertiti):,} ({100-tasso_conversione:.1f}%)")

    # Distribuzione tessere destinazione
    if len(convertiti) > 0:
        dest_dist = convertiti['TesseraDestinazione'].value_counts()
        print(f"\nTESSERE DI DESTINAZIONE:")
        for tessera, count in dest_dist.items():
            pct = count / len(convertiti) * 100
            print(f"  {tessera}: {count:,} ({pct:.1f}%)")

        # Tempo medio conversione
        convertiti_con_tempo = convertiti[convertiti['AnnoConversione'].notna()]
        if len(convertiti_con_tempo) > 0:
            convertiti_con_tempo['TempoConversione'] = convertiti_con_tempo['AnnoConversione'] - convertiti_con_tempo['AnnoInizio']
            tempo_medio = convertiti_con_tempo['TempoConversione'].mean()
            print(f"\nTEMPO MEDIO CONVERSIONE: {tempo_medio:.1f} anni")

        # Attività post-conversione
        gare_media_post = convertiti['GareDopoConversione'].mean()
        punti_medi_post = convertiti['PuntiDopoConversione'].mean()
        print(f"\nATTIVITÀ POST-CONVERSIONE:")
        print(f"  Gare medie dopo conversione: {gare_media_post:.1f}")
        print(f"  Punti medi dopo conversione: {punti_medi_post:.0f}")

    # Salva risultati
    df_conversione.to_csv(OUTPUT_DIR / "dettaglio_conversione_puglia.csv", index=False)

    # Aggregato per tessera destinazione
    aggregato = df_conversione.groupby('TesseraDestinazione').agg({
        'MmbCode': 'count',
        'AnniInScuolaBridge': 'mean',
        'GareDopoConversione': 'mean',
        'PuntiDopoConversione': 'mean'
    }).reset_index()
    aggregato.columns = ['TesseraDestinazione', 'NumeroAllievi', 'AnniMediInSB', 'GareMediaPost', 'PuntiMediPost']
    aggregato = aggregato.sort_values('NumeroAllievi', ascending=False)
    aggregato.to_csv(OUTPUT_DIR / "conversione_aggregata_puglia.csv", index=False)

    return df_conversione, aggregato


def analisi_transizioni_annuali_puglia(df):
    """Analisi transizioni anno per anno per Puglia."""
    print("\n" + "="*80)
    print("4. TRANSIZIONI ANNUALI SCUOLA BRIDGE PUGLIA")
    print("="*80)

    risultati = []

    for year in [2022, 2023, 2024]:
        next_year = year + 1

        # Giocatori Scuola Bridge Puglia nell'anno corrente
        sb_year = set(df[(df['Anno'] == year) & (df['MbtDesc'] == 'Scuola Bridge') & (df['GrpArea'] == 'PUG')]['MmbCode'])

        if len(sb_year) == 0:
            continue

        # Tutti i tesserati Puglia anno successivo
        df_next = df[(df['Anno'] == next_year) & (df['GrpArea'] == 'PUG')]
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
            'Transizione': f"{year}->{next_year}",
            'ScuolaBridge': len(sb_year),
            'Progressione': len(progressione),
            'ProgressionePct': round(len(progressione)/len(sb_year)*100, 1),
            'Completamento': len(completamento),
            'CompletamentoPct': round(len(completamento)/len(sb_year)*100, 1),
            'ChurnReale': len(churn_reale),
            'ChurnRealePct': round(len(churn_reale)/len(sb_year)*100, 1),
            'TassoSuccesso': round((len(progressione) + len(completamento))/len(sb_year)*100, 1)
        })

        print(f"\n{year} -> {next_year}:")
        print(f"  Scuola Bridge: {len(sb_year):,}")
        print(f"  Progressione (rimane SB): {len(progressione):,} ({len(progressione)/len(sb_year)*100:.1f}%)")
        print(f"  Completamento (passa altro): {len(completamento):,} ({len(completamento)/len(sb_year)*100:.1f}%)")
        print(f"  Churn Reale (abbandona): {len(churn_reale):,} ({len(churn_reale)/len(sb_year)*100:.1f}%)")

    df_transizioni = pd.DataFrame(risultati)
    df_transizioni.to_csv(OUTPUT_DIR / "transizioni_scuola_bridge_puglia.csv", index=False)

    return df_transizioni


def analisi_circoli_puglia(df_puglia):
    """Analisi performance per circolo in Puglia."""
    print("\n" + "="*80)
    print("5. PERFORMANCE CIRCOLI PUGLIA")
    print("="*80)

    # Statistiche per circolo
    circoli = df_puglia.groupby(['GrpName']).agg({
        'MmbCode': 'nunique',
        'GareGiocate': 'mean',
        'PuntiTotali': 'mean',
        'Anno': lambda x: list(x.unique())
    }).reset_index()
    circoli.columns = ['Circolo', 'TesseratiTotali', 'GareMedia', 'PuntiMedi', 'AnniAttivi']
    circoli['AnniAttivi'] = circoli['AnniAttivi'].apply(lambda x: len(x))
    circoli = circoli.sort_values('TesseratiTotali', ascending=False)

    print("\nTop 10 Circoli per tesserati:")
    print(circoli.head(10).to_string(index=False))

    # Analisi Scuola Bridge per circolo
    sb_circoli = df_puglia[df_puglia['MbtDesc'] == 'Scuola Bridge'].groupby('GrpName').agg({
        'MmbCode': 'nunique'
    }).reset_index()
    sb_circoli.columns = ['Circolo', 'AllievoScuolaBridge']

    # Merge con circoli totali
    circoli = circoli.merge(sb_circoli, on='Circolo', how='left')
    circoli['AllievoScuolaBridge'] = circoli['AllievoScuolaBridge'].fillna(0).astype(int)
    circoli['QuotaSB'] = (circoli['AllievoScuolaBridge'] / circoli['TesseratiTotali'] * 100).round(1)

    circoli.to_csv(OUTPUT_DIR / "circoli_puglia.csv", index=False)

    return circoli


def confronto_nazionale(df, df_puglia):
    """Confronto metriche Puglia vs Nazionale."""
    print("\n" + "="*80)
    print("6. CONFRONTO PUGLIA VS NAZIONALE")
    print("="*80)

    df_naz = df[df['Anno'].isin(ANNI_ANALISI)]

    # Metriche nazionali
    naz_stats = {
        'Regione': 'Italia',
        'Tesserati': df_naz['MmbCode'].nunique(),
        'GareMedia': df_naz['GareGiocate'].mean(),
        'EtaMedia': df_naz['Anni'].mean() if 'Anni' in df_naz.columns else None,
        'AllievoScuolaBridge': df_naz[df_naz['MbtDesc'] == 'Scuola Bridge']['MmbCode'].nunique()
    }

    # Metriche Puglia
    pug_stats = {
        'Regione': 'Puglia',
        'Tesserati': df_puglia['MmbCode'].nunique(),
        'GareMedia': df_puglia['GareGiocate'].mean(),
        'EtaMedia': df_puglia['Anni'].mean() if 'Anni' in df_puglia.columns else None,
        'AllievoScuolaBridge': df_puglia[df_puglia['MbtDesc'] == 'Scuola Bridge']['MmbCode'].nunique()
    }

    # Calcola tassi conversione
    # Nazionale
    sb_naz = df_naz[df_naz['MbtDesc'] == 'Scuola Bridge']['MmbCode'].unique()
    convertiti_naz = 0
    for code in sb_naz:
        storia = df_naz[df_naz['MmbCode'] == code]
        if (storia['MbtDesc'] != 'Scuola Bridge').any():
            convertiti_naz += 1
    naz_stats['TassoConversione'] = convertiti_naz / len(sb_naz) * 100 if len(sb_naz) > 0 else 0

    # Puglia (già calcolato)
    sb_pug = df_puglia[df_puglia['MbtDesc'] == 'Scuola Bridge']['MmbCode'].unique()
    convertiti_pug = 0
    for code in sb_pug:
        storia = df[(df['MmbCode'] == code) & (df['GrpArea'] == 'PUG')]
        if (storia['MbtDesc'] != 'Scuola Bridge').any():
            convertiti_pug += 1
    pug_stats['TassoConversione'] = convertiti_pug / len(sb_pug) * 100 if len(sb_pug) > 0 else 0

    confronto = pd.DataFrame([naz_stats, pug_stats])

    # Calcola differenze
    confronto['QuotaNazionale'] = [100, pug_stats['Tesserati'] / naz_stats['Tesserati'] * 100]

    print("\nCONFRONTO METRICHE:")
    print(confronto.to_string(index=False))

    confronto.to_csv(OUTPUT_DIR / "confronto_nazionale_puglia.csv", index=False)

    return confronto


def genera_grafici(trend, tessere_pivot, sb_stats, df_conversione, circoli, confronto):
    """Genera tutti i grafici per il tab Puglia."""
    print("\n" + "="*80)
    print("7. GENERAZIONE GRAFICI")
    print("="*80)

    # 1. Trend tesseramenti Puglia
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.bar(trend['Anno'], trend['Tesserati'], color=COLORS['primary'], edgecolor='white', linewidth=1.5)
    ax.set_xlabel('Anno', fontsize=12)
    ax.set_ylabel('Tesserati', fontsize=12)
    ax.set_title('Trend Tesseramenti Puglia 2022-2025', fontsize=14, fontweight='bold')

    # Aggiungi etichette
    for i, (anno, tess, var) in enumerate(zip(trend['Anno'], trend['Tesserati'], trend['Variazione'])):
        ax.text(anno, tess + 10, f'{tess:,}', ha='center', fontsize=10, fontweight='bold')
        if var != 0:
            color = COLORS['success'] if var > 0 else COLORS['danger']
            ax.text(anno, tess - 30, f'{var:+.1f}%', ha='center', fontsize=9, color=color)

    ax.set_ylim(0, trend['Tesserati'].max() * 1.15)
    plt.tight_layout()
    plt.savefig(CHARTS_DIR / "puglia_01_trend_tesserati.png", dpi=150, bbox_inches='tight')
    plt.close()
    print("  Salvato: puglia_01_trend_tesserati.png")

    # 2. Composizione tessere
    fig, ax = plt.subplots(figsize=(12, 6))
    tessere_principali = ['Scuola Bridge', 'Ordinario Sportivo', 'Agonista', 'Ordinario Amatoriale']
    colors_tessere = [COLORS['scuola_bridge'], COLORS['ordinario_sportivo'], COLORS['agonista'], COLORS['warning']]

    bottom = np.zeros(len(ANNI_ANALISI))
    for i, tessera in enumerate(tessere_principali):
        if tessera in tessere_pivot.columns:
            values = tessere_pivot[tessera].values
            ax.bar(ANNI_ANALISI, values, bottom=bottom, label=tessera, color=colors_tessere[i])
            bottom += values

    ax.set_xlabel('Anno', fontsize=12)
    ax.set_ylabel('Tesserati', fontsize=12)
    ax.set_title('Composizione Tessere Puglia 2022-2025', fontsize=14, fontweight='bold')
    ax.legend(loc='upper right')
    plt.tight_layout()
    plt.savefig(CHARTS_DIR / "puglia_02_composizione_tessere.png", dpi=150, bbox_inches='tight')
    plt.close()
    print("  Salvato: puglia_02_composizione_tessere.png")

    # 3. Scuola Bridge trend
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(sb_stats['Anno'], sb_stats['Allievi'], marker='o', markersize=10,
            linewidth=3, color=COLORS['scuola_bridge'])
    ax.fill_between(sb_stats['Anno'], sb_stats['Allievi'], alpha=0.3, color=COLORS['scuola_bridge'])

    for anno, allievi in zip(sb_stats['Anno'], sb_stats['Allievi']):
        ax.text(anno, allievi + 2, f'{allievi:,}', ha='center', fontsize=10, fontweight='bold')

    ax.set_xlabel('Anno', fontsize=12)
    ax.set_ylabel('Allievi Scuola Bridge', fontsize=12)
    ax.set_title('Trend Scuola Bridge Puglia 2022-2025', fontsize=14, fontweight='bold')
    ax.set_ylim(0, sb_stats['Allievi'].max() * 1.2)
    plt.tight_layout()
    plt.savefig(CHARTS_DIR / "puglia_03_scuola_bridge_trend.png", dpi=150, bbox_inches='tight')
    plt.close()
    print("  Salvato: puglia_03_scuola_bridge_trend.png")

    # 4. Funnel conversione
    fig, ax = plt.subplots(figsize=(10, 6))
    convertiti = len(df_conversione[df_conversione['Convertito'] == 'Sì'])
    non_convertiti = len(df_conversione[df_conversione['Convertito'] == 'No'])
    totale = len(df_conversione)

    categories = ['Allievi Totali', 'Convertiti', 'In Formazione']
    values = [totale, convertiti, non_convertiti]
    colors_funnel = [COLORS['info'], COLORS['success'], COLORS['scuola_bridge']]

    bars = ax.bar(categories, values, color=colors_funnel, edgecolor='white', linewidth=2)

    for bar, val in zip(bars, values):
        pct = val / totale * 100
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 2,
                f'{val:,}\n({pct:.1f}%)', ha='center', fontsize=11, fontweight='bold')

    ax.set_ylabel('Numero Allievi', fontsize=12)
    ax.set_title('Funnel Conversione Allievi Puglia', fontsize=14, fontweight='bold')
    ax.set_ylim(0, max(values) * 1.2)
    plt.tight_layout()
    plt.savefig(CHARTS_DIR / "puglia_04_funnel_conversione.png", dpi=150, bbox_inches='tight')
    plt.close()
    print("  Salvato: puglia_04_funnel_conversione.png")

    # 5. Tessere destinazione
    convertiti_df = df_conversione[df_conversione['Convertito'] == 'Sì']
    if len(convertiti_df) > 0:
        fig, ax = plt.subplots(figsize=(10, 6))
        dest_counts = convertiti_df['TesseraDestinazione'].value_counts()

        colors_dest = []
        for tessera in dest_counts.index:
            if 'Ordinario Sportivo' in tessera:
                colors_dest.append(COLORS['ordinario_sportivo'])
            elif 'Agonista' in tessera:
                colors_dest.append(COLORS['agonista'])
            elif 'Amatoriale' in tessera:
                colors_dest.append(COLORS['warning'])
            else:
                colors_dest.append(COLORS['secondary'])

        wedges, texts, autotexts = ax.pie(dest_counts.values, labels=dest_counts.index,
                                           autopct='%1.1f%%', colors=colors_dest,
                                           startangle=90, explode=[0.02]*len(dest_counts))
        ax.set_title('Tessere di Destinazione dopo Conversione', fontsize=14, fontweight='bold')
        plt.tight_layout()
        plt.savefig(CHARTS_DIR / "puglia_05_tessere_destinazione.png", dpi=150, bbox_inches='tight')
        plt.close()
        print("  Salvato: puglia_05_tessere_destinazione.png")

    # 6. Top circoli
    fig, ax = plt.subplots(figsize=(12, 6))
    top_circoli = circoli.head(10)
    y_pos = range(len(top_circoli))

    ax.barh(y_pos, top_circoli['TesseratiTotali'], color=COLORS['primary'], edgecolor='white')
    ax.set_yticks(y_pos)
    ax.set_yticklabels(top_circoli['Circolo'], fontsize=10)
    ax.invert_yaxis()
    ax.set_xlabel('Tesserati', fontsize=12)
    ax.set_title('Top 10 Circoli Puglia per Tesserati', fontsize=14, fontweight='bold')

    for i, (val, sb) in enumerate(zip(top_circoli['TesseratiTotali'], top_circoli['AllievoScuolaBridge'])):
        ax.text(val + 2, i, f'{val:,} (SB: {sb:.0f})', va='center', fontsize=9)

    plt.tight_layout()
    plt.savefig(CHARTS_DIR / "puglia_06_circoli_top10.png", dpi=150, bbox_inches='tight')
    plt.close()
    print("  Salvato: puglia_06_circoli_top10.png")


def genera_summary_json(trend, sb_stats, df_conversione, circoli, confronto):
    """Genera JSON di summary per React."""

    convertiti = df_conversione[df_conversione['Convertito'] == 'Sì']
    non_convertiti = df_conversione[df_conversione['Convertito'] == 'No']

    # Calcola tempo medio conversione
    if len(convertiti) > 0:
        convertiti_copy = convertiti.copy()
        convertiti_copy['TempoConversione'] = convertiti_copy['AnnoConversione'] - convertiti_copy['AnnoInizio']
        tempo_medio = convertiti_copy['TempoConversione'].mean()
        gare_media_post = convertiti['GareDopoConversione'].mean()
        tessera_principale = convertiti['TesseraDestinazione'].value_counts().index[0]
        tessera_principale_pct = convertiti['TesseraDestinazione'].value_counts().iloc[0] / len(convertiti) * 100
    else:
        tempo_medio = 0
        gare_media_post = 0
        tessera_principale = "N/A"
        tessera_principale_pct = 0

    # Variazione 4 anni
    tesserati_2022 = trend[trend['Anno'] == 2022]['Tesserati'].values[0] if 2022 in trend['Anno'].values else 0
    tesserati_2025 = trend[trend['Anno'] == 2025]['Tesserati'].values[0] if 2025 in trend['Anno'].values else 0
    variazione_4_anni = ((tesserati_2025 - tesserati_2022) / tesserati_2022 * 100) if tesserati_2022 > 0 else 0

    # Tasso conversione nazionale
    pug_row = confronto[confronto['Regione'] == 'Puglia']
    naz_row = confronto[confronto['Regione'] == 'Italia']

    tasso_pug = pug_row['TassoConversione'].values[0] if len(pug_row) > 0 else 0
    tasso_naz = naz_row['TassoConversione'].values[0] if len(naz_row) > 0 else 0

    summary = {
        "periodo": "2022-2025",
        "aggiornamento": "2025 (dati parziali)",
        "tesserati": {
            "totale_2025": int(tesserati_2025),
            "totale_2022": int(tesserati_2022),
            "variazione_4_anni": round(variazione_4_anni, 1),
            "trend": "positivo" if variazione_4_anni > 0 else "negativo"
        },
        "scuola_bridge": {
            "allievi_totali_periodo": len(df_conversione),
            "convertiti": len(convertiti),
            "in_formazione": len(non_convertiti),
            "tasso_conversione": round(len(convertiti) / len(df_conversione) * 100, 1) if len(df_conversione) > 0 else 0,
            "tempo_medio_conversione": round(tempo_medio, 1),
            "gare_media_post_conversione": round(gare_media_post, 1),
            "tessera_principale": tessera_principale,
            "tessera_principale_pct": round(tessera_principale_pct, 1)
        },
        "confronto_nazionale": {
            "tasso_conversione_puglia": round(tasso_pug, 1),
            "tasso_conversione_italia": round(tasso_naz, 1),
            "differenza": round(tasso_pug - tasso_naz, 1),
            "quota_tesserati_nazionale": round(pug_row['QuotaNazionale'].values[0], 2) if len(pug_row) > 0 else 0
        },
        "circoli": {
            "totale": len(circoli),
            "top_circolo": circoli.iloc[0]['Circolo'] if len(circoli) > 0 else "N/A",
            "top_circolo_tesserati": int(circoli.iloc[0]['TesseratiTotali']) if len(circoli) > 0 else 0
        },
        "anno_trend": trend[['Anno', 'Tesserati', 'Variazione']].to_dict(orient='records')
    }

    with open(OUTPUT_DIR / "summary_puglia.json", 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    print(f"\nSummary JSON salvato: {OUTPUT_DIR / 'summary_puglia.json'}")

    return summary


def main():
    """Funzione principale."""
    print("="*80)
    print("ANALISI FOCUS PUGLIA 2022-2025")
    print("="*80)

    # Carica dati
    df = carica_dati()
    df_puglia = filtra_puglia(df)

    # Esegui analisi
    trend, tessere_pivot = analisi_trend_tesserati(df_puglia, df)
    sb_stats = analisi_scuola_bridge_puglia(df_puglia, df)
    df_conversione, aggregato = traccia_conversione_allievi(df, df_puglia)
    df_transizioni = analisi_transizioni_annuali_puglia(df)
    circoli = analisi_circoli_puglia(df_puglia)
    confronto = confronto_nazionale(df, df_puglia)

    # Genera grafici
    genera_grafici(trend, tessere_pivot, sb_stats, df_conversione, circoli, confronto)

    # Genera summary JSON
    summary = genera_summary_json(trend, sb_stats, df_conversione, circoli, confronto)

    print("\n" + "="*80)
    print("ANALISI COMPLETATA!")
    print(f"Risultati salvati in: {OUTPUT_DIR}")
    print(f"Grafici salvati in: {CHARTS_DIR}")
    print("="*80)

    return summary


if __name__ == "__main__":
    main()
