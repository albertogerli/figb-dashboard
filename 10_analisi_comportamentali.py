#!/usr/bin/env python3
"""
ANALISI COMPORTAMENTALI E TERRITORIALI
=======================================

1. Cluster Comportamentali - Segmentazione giocatori
2. Cannibalizzazione Circoli - Circoli vicini si rubano iscritti?
3. Effetto Città Grande vs Piccola - Dinamiche metropolitane vs provincia
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
RESULTS_DIR = OUTPUT_DIR / 'results_comportamentali'
RESULTS_DIR.mkdir(exist_ok=True)


def main():
    print("=" * 70)
    print("ANALISI COMPORTAMENTALI E TERRITORIALI")
    print("=" * 70)

    # Carica dati
    print("\n1. Caricamento dati...")
    df = pd.read_csv(OUTPUT_DIR / 'dati_unificati_2017_2025.csv')
    print(f"   Record totali: {len(df):,}")

    anno_corrente = df['Anno'].max()
    col_assoc = 'Associazione' if 'Associazione' in df.columns else 'GrpName'

    # =========================================================================
    # 1. CLUSTER COMPORTAMENTALI
    # =========================================================================
    print("\n" + "=" * 70)
    print("2. CLUSTER COMPORTAMENTALI")
    print("   (Segmentazione giocatori per comportamento)")
    print("=" * 70)

    # Calcola metriche per giocatore
    giocatori = df.groupby('MmbCode').agg({
        'Anno': ['min', 'max', 'count'],
        'GareGiocate': ['mean', 'sum', 'std'],
        'PuntiCampionati': ['mean', 'sum'],
        'PuntiTotali': ['mean', 'sum'],
        'Anni': 'last',
        'MmbSex': 'first',
        'CatLabel': 'last',
        col_assoc: 'nunique',
        'IsAgonista': 'max'
    }).reset_index()

    giocatori.columns = ['MmbCode', 'AnnoInizio', 'AnnoFine', 'AnniPresenza',
                         'GareMedie', 'GareTotali', 'GareStd',
                         'CampMedi', 'CampTotali', 'PuntiMedi', 'PuntiTotali',
                         'Eta', 'Sesso', 'Categoria', 'NumCircoli', 'IsAgonista']

    # Calcola metriche derivate
    giocatori['GareStd'] = giocatori['GareStd'].fillna(0)
    giocatori['Costanza'] = 1 - (giocatori['GareStd'] / (giocatori['GareMedie'] + 1))
    giocatori['Costanza'] = giocatori['Costanza'].clip(0, 1)

    # Definisci cluster basati su regole
    def assegna_cluster(row):
        gare = row['GareMedie']
        anni = row['AnniPresenza']
        camp = row['CampMedi']
        agonista = row['IsAgonista']

        # Super Agonista: molte gare, molti campionati, agonista
        if gare >= 80 and camp >= 5000 and agonista:
            return 'Super Agonista'

        # Agonista Attivo: buone gare, partecipa a campionati
        if gare >= 50 and camp >= 2000:
            return 'Agonista Attivo'

        # Regolare Fedele: gare medie, presente da anni
        if gare >= 30 and anni >= 4:
            return 'Regolare Fedele'

        # Sociale: poche gare ma presente
        if gare >= 10 and gare < 30:
            return 'Sociale'

        # Occasionale: pochissime gare
        if gare >= 1 and gare < 10:
            return 'Occasionale'

        # Dormiente: quasi zero gare
        if gare < 1:
            return 'Dormiente'

        # Nuovo Entusiasta: pochi anni ma molte gare
        if anni <= 2 and gare >= 40:
            return 'Nuovo Entusiasta'

        return 'Altro'

    giocatori['Cluster'] = giocatori.apply(assegna_cluster, axis=1)

    # Ricalcola cluster con priorità corretta
    def assegna_cluster_v2(row):
        gare = row['GareMedie']
        anni = row['AnniPresenza']
        camp = row['CampMedi']
        agonista = row['IsAgonista']

        # Dormiente: quasi zero gare
        if gare < 1:
            return 'Dormiente'

        # Super Agonista
        if gare >= 80 and camp >= 5000:
            return 'Super Agonista'

        # Nuovo Entusiasta: pochi anni ma molte gare
        if anni <= 2 and gare >= 40:
            return 'Nuovo Entusiasta'

        # Agonista Attivo
        if gare >= 50 and camp >= 2000:
            return 'Agonista Attivo'

        # Regolare Fedele
        if gare >= 30 and anni >= 4:
            return 'Regolare Fedele'

        # Sociale
        if gare >= 10 and gare < 30:
            return 'Sociale'

        # Occasionale
        if gare < 10:
            return 'Occasionale'

        return 'Regolare'

    giocatori['Cluster'] = giocatori.apply(assegna_cluster_v2, axis=1)

    # Statistiche cluster
    cluster_stats = giocatori.groupby('Cluster').agg({
        'MmbCode': 'count',
        'GareMedie': 'mean',
        'AnniPresenza': 'mean',
        'CampMedi': 'mean',
        'Eta': 'mean',
        'NumCircoli': 'mean'
    }).reset_index()
    cluster_stats.columns = ['Cluster', 'NumGiocatori', 'GareMedie', 'AnniMedi', 'CampMedi', 'EtaMedia', 'CircoliMedi']

    # Percentuali
    cluster_stats['Percentuale'] = (cluster_stats['NumGiocatori'] / cluster_stats['NumGiocatori'].sum() * 100).round(1)
    cluster_stats = cluster_stats.sort_values('NumGiocatori', ascending=False)

    print("\n   DISTRIBUZIONE CLUSTER:")
    print(cluster_stats.round(1).to_string(index=False))

    # Profilo per cluster
    print("\n   PROFILO DETTAGLIATO PER CLUSTER:")
    for cluster in cluster_stats['Cluster']:
        subset = giocatori[giocatori['Cluster'] == cluster]
        print(f"\n   {cluster} ({len(subset):,} giocatori, {100*len(subset)/len(giocatori):.1f}%):")
        print(f"      Gare medie: {subset['GareMedie'].mean():.1f}")
        print(f"      Anni presenza: {subset['AnniPresenza'].mean():.1f}")
        print(f"      Età media: {subset['Eta'].mean():.1f}")
        print(f"      % Donne: {100*(subset['Sesso']=='F').mean():.1f}%")

    # Retention per cluster (chi è ancora attivo)
    giocatori['AncoraAttivo'] = giocatori['AnnoFine'] == anno_corrente
    retention_cluster = giocatori.groupby('Cluster')['AncoraAttivo'].mean() * 100
    print("\n   RETENTION PER CLUSTER:")
    print(retention_cluster.round(1).sort_values(ascending=False).to_string())

    # =========================================================================
    # 2. CANNIBALIZZAZIONE CIRCOLI
    # =========================================================================
    print("\n" + "=" * 70)
    print("3. CANNIBALIZZAZIONE CIRCOLI")
    print("   (Circoli vicini si rubano iscritti o crescono insieme?)")
    print("=" * 70)

    # Analisi per provincia - circoli nella stessa provincia
    circoli_provincia = df.groupby(['Provincia', col_assoc, 'Anno']).agg({
        'MmbCode': 'nunique'
    }).reset_index()
    circoli_provincia.columns = ['Provincia', 'Circolo', 'Anno', 'Tesserati']

    # Conta circoli per provincia
    circoli_per_provincia = circoli_provincia.groupby(['Provincia', 'Anno'])['Circolo'].nunique().reset_index()
    circoli_per_provincia.columns = ['Provincia', 'Anno', 'NumCircoli']

    # Tesserati totali per provincia
    tess_per_provincia = circoli_provincia.groupby(['Provincia', 'Anno'])['Tesserati'].sum().reset_index()

    # Merge
    provincia_stats = circoli_per_provincia.merge(tess_per_provincia, on=['Provincia', 'Anno'])

    # Calcola correlazione: più circoli = più tesserati?
    # Confronto anno corrente
    prov_corrente = provincia_stats[provincia_stats['Anno'] == anno_corrente]
    prov_corrente = prov_corrente[prov_corrente['NumCircoli'] > 0]

    if len(prov_corrente) > 10:
        corr = prov_corrente['NumCircoli'].corr(prov_corrente['Tesserati'])
        print(f"\n   Correlazione NumCircoli vs Tesserati: {corr:.3f}")

    # Analisi trend: province che hanno aggiunto circoli
    prov_inizio = provincia_stats[provincia_stats['Anno'] == provincia_stats['Anno'].min()].set_index('Provincia')
    prov_fine = provincia_stats[provincia_stats['Anno'] == anno_corrente].set_index('Provincia')

    province_comuni = set(prov_inizio.index) & set(prov_fine.index)

    evoluzione = []
    for prov in province_comuni:
        if prov in prov_inizio.index and prov in prov_fine.index:
            evoluzione.append({
                'Provincia': prov,
                'CircoliInizio': prov_inizio.loc[prov, 'NumCircoli'],
                'CircoliFine': prov_fine.loc[prov, 'NumCircoli'],
                'TessInizio': prov_inizio.loc[prov, 'Tesserati'],
                'TessFine': prov_fine.loc[prov, 'Tesserati'],
            })

    df_evol = pd.DataFrame(evoluzione)
    df_evol['DeltaCircoli'] = df_evol['CircoliFine'] - df_evol['CircoliInizio']
    df_evol['DeltaTess'] = df_evol['TessFine'] - df_evol['TessInizio']
    df_evol['DeltaTessPct'] = ((df_evol['TessFine'] - df_evol['TessInizio']) / df_evol['TessInizio'] * 100).round(1)

    # Province che hanno aggiunto circoli
    prov_piu_circoli = df_evol[df_evol['DeltaCircoli'] > 0].sort_values('DeltaCircoli', ascending=False)
    prov_meno_circoli = df_evol[df_evol['DeltaCircoli'] < 0].sort_values('DeltaCircoli')

    print(f"\n   Province che hanno AGGIUNTO circoli:")
    if len(prov_piu_circoli) > 0:
        print(prov_piu_circoli[['Provincia', 'DeltaCircoli', 'DeltaTess', 'DeltaTessPct']].head(10).to_string(index=False))

        # Effetto medio
        media_delta_tess = prov_piu_circoli['DeltaTessPct'].mean()
        print(f"\n   → Effetto medio su tesserati: {media_delta_tess:+.1f}%")
    else:
        print("   Nessuna provincia ha aggiunto circoli")

    print(f"\n   Province che hanno PERSO circoli:")
    if len(prov_meno_circoli) > 0:
        print(prov_meno_circoli[['Provincia', 'DeltaCircoli', 'DeltaTess', 'DeltaTessPct']].head(10).to_string(index=False))

        media_delta_tess_meno = prov_meno_circoli['DeltaTessPct'].mean()
        print(f"\n   → Effetto medio su tesserati: {media_delta_tess_meno:+.1f}%")
    else:
        print("   Nessuna provincia ha perso circoli")

    # Analisi cannibalizzazione: stessa provincia, giocatori che cambiano circolo
    print("\n   ANALISI CAMBIO CIRCOLO NELLA STESSA PROVINCIA:")

    # Trova giocatori che hanno cambiato circolo
    giocatori_circoli = df.groupby('MmbCode').agg({
        col_assoc: list,
        'Provincia': list
    }).reset_index()

    giocatori_circoli['NumCircoli'] = giocatori_circoli[col_assoc].apply(lambda x: len(set(x)))
    giocatori_circoli['NumProvince'] = giocatori_circoli['Provincia'].apply(lambda x: len(set([p for p in x if pd.notna(p)])))

    # Chi ha cambiato circolo ma restando nella stessa provincia
    cambio_stesso_posto = giocatori_circoli[(giocatori_circoli['NumCircoli'] > 1) & (giocatori_circoli['NumProvince'] == 1)]
    cambio_altra_provincia = giocatori_circoli[(giocatori_circoli['NumCircoli'] > 1) & (giocatori_circoli['NumProvince'] > 1)]

    print(f"   Giocatori che hanno cambiato circolo: {(giocatori_circoli['NumCircoli'] > 1).sum():,}")
    print(f"   - Restando nella stessa provincia: {len(cambio_stesso_posto):,} ({100*len(cambio_stesso_posto)/(giocatori_circoli['NumCircoli'] > 1).sum():.1f}%)")
    print(f"   - Cambiando provincia: {len(cambio_altra_provincia):,} ({100*len(cambio_altra_provincia)/(giocatori_circoli['NumCircoli'] > 1).sum():.1f}%)")

    # =========================================================================
    # 3. EFFETTO CITTÀ GRANDE VS PICCOLA
    # =========================================================================
    print("\n" + "=" * 70)
    print("4. EFFETTO CITTÀ GRANDE VS PICCOLA")
    print("   (Dinamiche metropolitane vs provincia)")
    print("=" * 70)

    # Usa colonna IsCittaMetropolitana se esiste
    if 'IsCittaMetropolitana' in df.columns:
        df['TipoArea'] = df['IsCittaMetropolitana'].map({True: 'Città Metropolitana', False: 'Provincia'})
    else:
        # Definisci città metropolitane manualmente
        citta_metro = ['Milano', 'Roma', 'Napoli', 'Torino', 'Firenze', 'Bologna', 'Genova',
                      'Venezia', 'Bari', 'Palermo', 'Catania', 'Cagliari', 'Messina', 'Reggio Calabria']
        df['TipoArea'] = df['Provincia'].apply(lambda x: 'Città Metropolitana' if x in citta_metro else 'Provincia')

    # Statistiche per tipo area
    stats_area = df.groupby(['TipoArea', 'Anno']).agg({
        'MmbCode': 'nunique',
        'GareGiocate': 'mean',
        'PuntiCampionati': 'mean',
        col_assoc: 'nunique'
    }).reset_index()
    stats_area.columns = ['TipoArea', 'Anno', 'Tesserati', 'GareMedie', 'CampMedi', 'NumCircoli']

    print("\n   CONFRONTO CITTÀ METROPOLITANA VS PROVINCIA (ultimo anno):")
    stats_ultimo = stats_area[stats_area['Anno'] == anno_corrente]
    print(stats_ultimo.to_string(index=False))

    # Metriche dettagliate
    metro = df[df['TipoArea'] == 'Città Metropolitana']
    prov = df[df['TipoArea'] == 'Provincia']

    confronto = pd.DataFrame({
        'Metrica': ['Tesserati', 'Gare Medie', 'Punti Camp Medi', '% Agonisti', 'Età Media', 'Circoli'],
        'Città Metro': [
            metro[metro['Anno'] == anno_corrente]['MmbCode'].nunique(),
            metro['GareGiocate'].mean(),
            metro['PuntiCampionati'].mean(),
            metro['IsAgonista'].mean() * 100,
            metro['Anni'].mean(),
            metro[metro['Anno'] == anno_corrente][col_assoc].nunique()
        ],
        'Provincia': [
            prov[prov['Anno'] == anno_corrente]['MmbCode'].nunique(),
            prov['GareGiocate'].mean(),
            prov['PuntiCampionati'].mean(),
            prov['IsAgonista'].mean() * 100,
            prov['Anni'].mean(),
            prov[prov['Anno'] == anno_corrente][col_assoc].nunique()
        ]
    })
    confronto['Differenza'] = confronto['Città Metro'] - confronto['Provincia']
    confronto['Diff%'] = ((confronto['Città Metro'] - confronto['Provincia']) / confronto['Provincia'] * 100).round(1)

    print("\n   CONFRONTO DETTAGLIATO:")
    print(confronto.round(1).to_string(index=False))

    # Retention per tipo area
    print("\n   RETENTION PER TIPO AREA:")

    def calc_retention_area(gruppo):
        anni = sorted(gruppo['Anno'].unique())
        if len(anni) < 2:
            return None
        ret_list = []
        for i in range(len(anni) - 1):
            t1 = set(gruppo[gruppo['Anno'] == anni[i]]['MmbCode'])
            t2 = set(gruppo[gruppo['Anno'] == anni[i+1]]['MmbCode'])
            if len(t1) > 0:
                ret_list.append(len(t1 & t2) / len(t1) * 100)
        return np.mean(ret_list) if ret_list else None

    ret_metro = calc_retention_area(metro)
    ret_prov = calc_retention_area(prov)

    print(f"   - Città Metropolitana: {ret_metro:.1f}%")
    print(f"   - Provincia: {ret_prov:.1f}%")
    print(f"   - Differenza: {ret_metro - ret_prov:+.1f} punti")

    # Trend nel tempo
    print("\n   TREND TESSERATI PER TIPO AREA:")
    trend_area = stats_area.pivot(index='Anno', columns='TipoArea', values='Tesserati')
    if 'Città Metropolitana' in trend_area.columns and 'Provincia' in trend_area.columns:
        trend_area['Rapporto'] = (trend_area['Città Metropolitana'] / trend_area['Provincia']).round(2)
        print(trend_area.to_string())

    # =========================================================================
    # SALVATAGGIO RISULTATI
    # =========================================================================
    print("\n" + "=" * 70)
    print("5. SALVATAGGIO RISULTATI")
    print("=" * 70)

    # Summary JSON
    summary = {
        'cluster': {
            'distribuzione': cluster_stats.to_dict('records'),
            'num_giocatori_totali': int(len(giocatori))
        },
        'cannibalizzazione': {
            'correlazione_circoli_tesserati': float(corr) if 'corr' in dir() else None,
            'cambio_stessa_provincia_pct': float(100*len(cambio_stesso_posto)/(giocatori_circoli['NumCircoli'] > 1).sum()) if (giocatori_circoli['NumCircoli'] > 1).sum() > 0 else 0
        },
        'citta_vs_provincia': {
            'retention_metro': float(ret_metro) if ret_metro else None,
            'retention_provincia': float(ret_prov) if ret_prov else None,
            'gare_medie_metro': float(metro['GareGiocate'].mean()),
            'gare_medie_provincia': float(prov['GareGiocate'].mean())
        }
    }

    with open(RESULTS_DIR / 'summary_comportamentali.json', 'w') as f:
        json.dump(summary, f, indent=2)
    print("   Salvato summary_comportamentali.json")

    # CSV
    cluster_stats.to_csv(RESULTS_DIR / 'cluster_stats.csv', index=False)
    giocatori[['MmbCode', 'Cluster', 'GareMedie', 'AnniPresenza', 'Eta', 'Sesso', 'AncoraAttivo']].to_csv(
        RESULTS_DIR / 'giocatori_cluster.csv', index=False)
    print("   Salvato cluster_stats.csv, giocatori_cluster.csv")

    df_evol.to_csv(RESULTS_DIR / 'evoluzione_province.csv', index=False)
    print("   Salvato evoluzione_province.csv")

    confronto.to_csv(RESULTS_DIR / 'confronto_metro_provincia.csv', index=False)
    stats_area.to_csv(RESULTS_DIR / 'stats_per_area.csv', index=False)
    print("   Salvato confronto_metro_provincia.csv, stats_per_area.csv")

    # Retention per cluster
    ret_cluster_df = retention_cluster.reset_index()
    ret_cluster_df.columns = ['Cluster', 'Retention']
    ret_cluster_df.to_csv(RESULTS_DIR / 'retention_cluster.csv', index=False)
    print("   Salvato retention_cluster.csv")

    # =========================================================================
    # RIEPILOGO
    # =========================================================================
    print("\n" + "=" * 70)
    print("RIEPILOGO INSIGHT")
    print("=" * 70)

    print(f"""
    1. CLUSTER COMPORTAMENTALI:
       - {cluster_stats.iloc[0]['Cluster']}: {cluster_stats.iloc[0]['Percentuale']:.1f}% dei giocatori
       - {cluster_stats.iloc[1]['Cluster']}: {cluster_stats.iloc[1]['Percentuale']:.1f}%
       - Retention migliore: {retention_cluster.idxmax()} ({retention_cluster.max():.1f}%)

    2. CANNIBALIZZAZIONE CIRCOLI:
       - {100*len(cambio_stesso_posto)/(giocatori_circoli['NumCircoli'] > 1).sum():.1f}% cambia circolo restando in provincia
       - Più circoli = più tesserati? Correlazione: {corr:.2f}

    3. CITTÀ VS PROVINCIA:
       - Retention Metro: {ret_metro:.1f}% vs Provincia: {ret_prov:.1f}%
       - Gare medie Metro: {metro['GareGiocate'].mean():.1f} vs Provincia: {prov['GareGiocate'].mean():.1f}
    """)


if __name__ == '__main__':
    main()
