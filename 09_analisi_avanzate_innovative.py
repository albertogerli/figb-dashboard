#!/usr/bin/env python3
"""
ANALISI AVANZATE INNOVATIVE
============================

Script per analisi comportamentali e predittive avanzate:
1. Curva di Apprendimento - progressione punti nei primi anni
2. Early Warning Circoli - previsione circoli a rischio chiusura
3. Effetto Maestro - impatto corsi/istruttori sulla retention
4. Migrazione Giocatori - analisi cambi circolo
5. Gender Gap per Livello - abbandono donne per categoria
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
RESULTS_DIR = OUTPUT_DIR / 'results_avanzate'
RESULTS_DIR.mkdir(exist_ok=True)


def main():
    print("=" * 70)
    print("ANALISI AVANZATE INNOVATIVE")
    print("=" * 70)

    # Carica dati
    print("\n1. Caricamento dati...")
    df = pd.read_csv(OUTPUT_DIR / 'dati_unificati_2017_2025.csv')
    print(f"   Record totali: {len(df):,}")

    anno_corrente = df['Anno'].max()
    col_assoc = 'Associazione' if 'Associazione' in df.columns else 'GrpName'

    # =========================================================================
    # 1. CURVA DI APPRENDIMENTO
    # =========================================================================
    print("\n" + "=" * 70)
    print("2. CURVA DI APPRENDIMENTO")
    print("   (Come progrediscono i punti nei primi anni)")
    print("=" * 70)

    # Trova primo anno per ogni giocatore
    primo_anno = df.groupby('MmbCode')['Anno'].min().reset_index()
    primo_anno.columns = ['MmbCode', 'AnnoPrimoTessera']

    df_curva = df.merge(primo_anno, on='MmbCode')
    df_curva['AnnoCarriera'] = df_curva['Anno'] - df_curva['AnnoPrimoTessera'] + 1

    # Filtra solo chi ha iniziato entro 2020 (per avere almeno 4-5 anni di storia)
    giocatori_con_storia = primo_anno[primo_anno['AnnoPrimoTessera'] <= 2020]['MmbCode']
    df_curva_filtrato = df_curva[df_curva['MmbCode'].isin(giocatori_con_storia)]

    # Curva media per anno di carriera
    curva_media = df_curva_filtrato.groupby('AnnoCarriera').agg({
        'PuntiTotali': 'mean',
        'GareGiocate': 'mean',
        'MmbCode': 'nunique'
    }).reset_index()
    curva_media.columns = ['AnnoCarriera', 'PuntiMedi', 'GareMedie', 'NumGiocatori']
    curva_media = curva_media[curva_media['AnnoCarriera'] <= 10]  # Primi 10 anni

    print("\n   Progressione media nei primi 10 anni:")
    print(curva_media.round(1).to_string(index=False))

    # Curva per chi resta vs chi abbandona
    # Chi e' ancora attivo nell'ultimo anno?
    attivi_ultimo = set(df[df['Anno'] == anno_corrente]['MmbCode'])

    df_curva_filtrato['AncoraAttivo'] = df_curva_filtrato['MmbCode'].isin(attivi_ultimo)

    curva_confronto = df_curva_filtrato.groupby(['AnnoCarriera', 'AncoraAttivo']).agg({
        'PuntiTotali': 'mean',
        'GareGiocate': 'mean',
        'MmbCode': 'nunique'
    }).reset_index()
    curva_confronto.columns = ['AnnoCarriera', 'AncoraAttivo', 'PuntiMedi', 'GareMedie', 'NumGiocatori']
    curva_confronto = curva_confronto[curva_confronto['AnnoCarriera'] <= 8]

    print("\n   Confronto chi resta vs chi abbandona:")
    for attivo in [True, False]:
        print(f"\n   {'ANCORA ATTIVI' if attivo else 'HANNO ABBANDONATO'}:")
        subset = curva_confronto[curva_confronto['AncoraAttivo'] == attivo]
        print(subset[['AnnoCarriera', 'PuntiMedi', 'GareMedie', 'NumGiocatori']].round(1).to_string(index=False))

    # Soglia critica: quando si decide se restare?
    print("\n   SOGLIA CRITICA:")
    anno1_attivi = curva_confronto[(curva_confronto['AnnoCarriera'] == 1) & (curva_confronto['AncoraAttivo'] == True)]['GareMedie'].values[0]
    anno1_persi = curva_confronto[(curva_confronto['AnnoCarriera'] == 1) & (curva_confronto['AncoraAttivo'] == False)]['GareMedie'].values[0]
    print(f"   - Anno 1: chi resta fa {anno1_attivi:.0f} gare, chi abbandona {anno1_persi:.0f}")
    print(f"   - Differenza: {anno1_attivi - anno1_persi:.0f} gare (fattore predittivo!)")

    # =========================================================================
    # 2. EARLY WARNING CIRCOLI
    # =========================================================================
    print("\n" + "=" * 70)
    print("3. EARLY WARNING CIRCOLI")
    print("   (Identificazione circoli a rischio chiusura)")
    print("=" * 70)

    # Calcola metriche per circolo per anno
    circoli_anno = df.groupby([col_assoc, 'Anno']).agg({
        'MmbCode': 'nunique',
        'GareGiocate': 'mean',
        'Anni': 'mean',
        'GrpArea': 'first'
    }).reset_index()
    circoli_anno.columns = ['Circolo', 'Anno', 'Tesserati', 'GareMedie', 'EtaMedia', 'Regione']

    # Pivot per vedere trend
    circoli_pivot = circoli_anno.pivot(index='Circolo', columns='Anno', values='Tesserati').fillna(0)

    # Calcola trend ultimi 3 anni
    anni_recenti = sorted(df['Anno'].unique())[-4:]  # ultimi 4 anni

    circoli_trend = []
    for circolo in circoli_pivot.index:
        valori = [circoli_pivot.loc[circolo, a] if a in circoli_pivot.columns else 0 for a in anni_recenti]
        if valori[0] > 0:  # Era attivo all'inizio del periodo
            trend_pct = (valori[-1] - valori[0]) / valori[0] * 100 if valori[0] > 0 else 0
            circoli_trend.append({
                'Circolo': circolo,
                f'Tess_{anni_recenti[0]}': valori[0],
                f'Tess_{anni_recenti[-1]}': valori[-1],
                'TrendPct': trend_pct,
                'Attivo': valori[-1] > 0
            })

    df_trend = pd.DataFrame(circoli_trend)

    # Aggiungi info regione e eta
    info_circoli = circoli_anno[circoli_anno['Anno'] == anno_corrente][['Circolo', 'Regione', 'EtaMedia', 'GareMedie']]
    df_trend = df_trend.merge(info_circoli, on='Circolo', how='left')

    # Classifica rischio
    def calcola_rischio(row):
        score = 0
        # Trend negativo forte
        if row['TrendPct'] < -50:
            score += 3
        elif row['TrendPct'] < -30:
            score += 2
        elif row['TrendPct'] < -10:
            score += 1

        # Pochi tesserati
        tess_ultimo = row[f'Tess_{anni_recenti[-1]}']
        if tess_ultimo < 10:
            score += 3
        elif tess_ultimo < 20:
            score += 2
        elif tess_ultimo < 30:
            score += 1

        # Eta alta
        if pd.notna(row.get('EtaMedia')):
            if row['EtaMedia'] > 75:
                score += 2
            elif row['EtaMedia'] > 70:
                score += 1

        # Poca attivita
        if pd.notna(row.get('GareMedie')):
            if row['GareMedie'] < 10:
                score += 2
            elif row['GareMedie'] < 20:
                score += 1

        return score

    df_trend['RiskScore'] = df_trend.apply(calcola_rischio, axis=1)

    # Classifica
    def classifica_rischio(score):
        if score >= 7:
            return 'CRITICO'
        elif score >= 5:
            return 'ALTO'
        elif score >= 3:
            return 'MEDIO'
        else:
            return 'BASSO'

    df_trend['LivelioRischio'] = df_trend['RiskScore'].apply(classifica_rischio)

    # Solo circoli ancora attivi
    circoli_attivi = df_trend[df_trend['Attivo']].copy()

    print(f"\n   Circoli attivi analizzati: {len(circoli_attivi)}")
    print("\n   Distribuzione rischio:")
    print(circoli_attivi['LivelioRischio'].value_counts())

    # Top circoli a rischio
    circoli_critici = circoli_attivi[circoli_attivi['LivelioRischio'].isin(['CRITICO', 'ALTO'])].sort_values('RiskScore', ascending=False)

    print(f"\n   CIRCOLI A RISCHIO CRITICO/ALTO: {len(circoli_critici)}")
    if len(circoli_critici) > 0:
        print(circoli_critici[['Circolo', f'Tess_{anni_recenti[0]}', f'Tess_{anni_recenti[-1]}',
                              'TrendPct', 'EtaMedia', 'LivelioRischio', 'Regione']].head(20).to_string(index=False))

    # Riepilogo per regione
    rischio_regione = circoli_attivi.groupby('Regione').agg({
        'Circolo': 'count',
        'RiskScore': 'mean'
    }).reset_index()
    rischio_regione.columns = ['Regione', 'NumCircoli', 'RischioMedio']
    rischio_regione = rischio_regione.sort_values('RischioMedio', ascending=False)

    print("\n   Rischio medio per regione:")
    print(rischio_regione.round(2).to_string(index=False))

    # =========================================================================
    # 3. EFFETTO MAESTRO (Corsi vs Retention)
    # =========================================================================
    print("\n" + "=" * 70)
    print("4. EFFETTO MAESTRO")
    print("   (Impatto dei corsi sulla retention)")
    print("=" * 70)

    # Circoli che hanno avuto corsisti "Scuola Bridge"
    corsisti = df[df['MbtDesc'] == 'Scuola Bridge']
    circoli_con_corsi = set(corsisti[col_assoc].unique())

    print(f"\n   Circoli con corsi attivi: {len(circoli_con_corsi)}")
    print(f"   Circoli senza corsi: {len(set(df[col_assoc].unique()) - circoli_con_corsi)}")

    # Calcola retention per circoli con/senza corsi
    def calcola_retention_circolo(gruppo):
        """Calcola retention media del circolo"""
        anni = sorted(gruppo['Anno'].unique())
        if len(anni) < 2:
            return None

        retention_tot = []
        for i in range(len(anni) - 1):
            tess_anno1 = set(gruppo[gruppo['Anno'] == anni[i]]['MmbCode'])
            tess_anno2 = set(gruppo[gruppo['Anno'] == anni[i+1]]['MmbCode'])
            if len(tess_anno1) > 0:
                retention = len(tess_anno1 & tess_anno2) / len(tess_anno1) * 100
                retention_tot.append(retention)

        return np.mean(retention_tot) if retention_tot else None

    # Calcola per ogni circolo
    retention_per_circolo = df.groupby(col_assoc).apply(calcola_retention_circolo).reset_index()
    retention_per_circolo.columns = ['Circolo', 'RetentionMedia']
    retention_per_circolo = retention_per_circolo.dropna()

    retention_per_circolo['HaCorsi'] = retention_per_circolo['Circolo'].isin(circoli_con_corsi)

    # Confronto
    ret_con_corsi = retention_per_circolo[retention_per_circolo['HaCorsi']]['RetentionMedia'].mean()
    ret_senza_corsi = retention_per_circolo[~retention_per_circolo['HaCorsi']]['RetentionMedia'].mean()

    print(f"\n   RETENTION MEDIA:")
    print(f"   - Circoli CON corsi: {ret_con_corsi:.1f}%")
    print(f"   - Circoli SENZA corsi: {ret_senza_corsi:.1f}%")
    print(f"   - Differenza: {ret_con_corsi - ret_senza_corsi:+.1f} punti percentuali")

    # Analisi piu granulare: quanti corsisti ha avuto?
    corsisti_per_circolo = corsisti.groupby(col_assoc)['MmbCode'].nunique().reset_index()
    corsisti_per_circolo.columns = ['Circolo', 'NumCorsisti']

    retention_con_num = retention_per_circolo.merge(corsisti_per_circolo, on='Circolo', how='left')
    retention_con_num['NumCorsisti'] = retention_con_num['NumCorsisti'].fillna(0)

    # Fasce di corsisti
    retention_con_num['FasciaCorsisti'] = pd.cut(
        retention_con_num['NumCorsisti'],
        bins=[-1, 0, 10, 30, 100, 10000],
        labels=['0', '1-10', '11-30', '31-100', '100+']
    )

    effetto_maestro = retention_con_num.groupby('FasciaCorsisti', observed=True).agg({
        'RetentionMedia': 'mean',
        'Circolo': 'count'
    }).reset_index()
    effetto_maestro.columns = ['FasciaCorsisti', 'RetentionMedia', 'NumCircoli']

    print("\n   Retention per numero di corsisti formati:")
    print(effetto_maestro.round(1).to_string(index=False))

    # =========================================================================
    # 4. MIGRAZIONE GIOCATORI
    # =========================================================================
    print("\n" + "=" * 70)
    print("5. MIGRAZIONE GIOCATORI")
    print("   (Chi cambia circolo e perche)")
    print("=" * 70)

    # Trova giocatori che hanno cambiato circolo
    circoli_per_giocatore = df.groupby('MmbCode').agg({
        col_assoc: lambda x: list(x.unique()),
        'Anno': ['min', 'max', 'count']
    }).reset_index()
    circoli_per_giocatore.columns = ['MmbCode', 'Circoli', 'AnnoInizio', 'AnnoFine', 'AnniPresenza']

    circoli_per_giocatore['NumCircoli'] = circoli_per_giocatore['Circoli'].apply(len)

    # Distribuzione
    print("\n   Distribuzione numero circoli frequentati:")
    print(circoli_per_giocatore['NumCircoli'].value_counts().sort_index().head(10))

    # Chi ha cambiato almeno una volta
    migranti = circoli_per_giocatore[circoli_per_giocatore['NumCircoli'] > 1]
    fedeli = circoli_per_giocatore[circoli_per_giocatore['NumCircoli'] == 1]

    print(f"\n   Giocatori 'fedeli' (1 solo circolo): {len(fedeli):,} ({100*len(fedeli)/len(circoli_per_giocatore):.1f}%)")
    print(f"   Giocatori 'migranti' (2+ circoli): {len(migranti):,} ({100*len(migranti)/len(circoli_per_giocatore):.1f}%)")

    # Profilo migranti vs fedeli
    # Aggiungi info dal df principale
    info_giocatori = df.groupby('MmbCode').agg({
        'Anni': 'last',
        'GareGiocate': 'mean',
        'PuntiTotali': 'mean',
        'CatLabel': 'last',
        'MmbSex': 'first'
    }).reset_index()

    migranti_info = migranti.merge(info_giocatori, on='MmbCode')
    fedeli_info = fedeli.merge(info_giocatori, on='MmbCode')

    print("\n   PROFILO COMPARATIVO:")
    profilo_migrazione = pd.DataFrame({
        'Metrica': ['Eta media', 'Gare medie/anno', 'Punti medi/anno', 'Anni presenza', '% Donne'],
        'Fedeli': [
            fedeli_info['Anni'].mean(),
            fedeli_info['GareGiocate'].mean(),
            fedeli_info['PuntiTotali'].mean(),
            fedeli_info['AnniPresenza'].mean(),
            100 * (fedeli_info['MmbSex'] == 'F').mean()
        ],
        'Migranti': [
            migranti_info['Anni'].mean(),
            migranti_info['GareGiocate'].mean(),
            migranti_info['PuntiTotali'].mean(),
            migranti_info['AnniPresenza'].mean(),
            100 * (migranti_info['MmbSex'] == 'F').mean()
        ]
    })
    profilo_migrazione['Fedeli'] = profilo_migrazione['Fedeli'].round(1)
    profilo_migrazione['Migranti'] = profilo_migrazione['Migranti'].round(1)
    print(profilo_migrazione.to_string(index=False))

    # Circoli che "perdono" vs "guadagnano" giocatori
    # Per ogni giocatore migrante, trova primo e ultimo circolo
    def get_migration_flow(row):
        if len(row['Circoli']) >= 2:
            return {'from': row['Circoli'][0], 'to': row['Circoli'][-1]}
        return None

    # Nota: questo e' semplificato, in realta' dovremmo tracciare per anno
    # Ma da' un'idea dei flussi

    # =========================================================================
    # 5. GENDER GAP PER LIVELLO
    # =========================================================================
    print("\n" + "=" * 70)
    print("6. GENDER GAP PER LIVELLO")
    print("   (Le donne abbandonano piu' a certi livelli?)")
    print("=" * 70)

    # Retention per sesso e categoria
    def calcola_retention_gruppo(gruppo):
        anni = sorted(df['Anno'].unique())
        results = []
        for i in range(len(anni) - 1):
            tess_anno1 = set(gruppo[gruppo['Anno'] == anni[i]]['MmbCode'])
            tess_anno2 = set(gruppo[gruppo['Anno'] == anni[i+1]]['MmbCode'])
            if len(tess_anno1) >= 10:  # Minimo per statistica
                retention = len(tess_anno1 & tess_anno2) / len(tess_anno1) * 100
                results.append(retention)
        return np.mean(results) if results else None

    # Per sesso
    retention_sesso = df.groupby('MmbSex').apply(calcola_retention_gruppo)
    print("\n   Retention per sesso:")
    print(f"   - Uomini (M): {retention_sesso.get('M', 0):.1f}%")
    print(f"   - Donne (F): {retention_sesso.get('F', 0):.1f}%")

    # Per categoria e sesso
    print("\n   Retention per categoria e sesso:")
    categorie_principali = ['Allievo 1\xb0 Anno', 'Allievo 2\xb0 Anno', 'Allievo 3\xb0 Anno',
                           '4\xaa Categoria', '3\xaa Categoria', '2\xaa Categoria', '1\xaa Categoria',
                           'Maestro', 'Maestro Nazionale']

    gender_gap_cat = []
    for cat in df['CatLabel'].unique():
        for sesso in ['M', 'F']:
            subset = df[(df['CatLabel'] == cat) & (df['MmbSex'] == sesso)]
            if len(subset) >= 50:
                ret = calcola_retention_gruppo(subset)
                if ret:
                    gender_gap_cat.append({
                        'Categoria': cat,
                        'Sesso': sesso,
                        'Retention': ret,
                        'NumGiocatori': subset['MmbCode'].nunique()
                    })

    df_gender_gap = pd.DataFrame(gender_gap_cat)

    if len(df_gender_gap) > 0:
        # Pivot
        gender_pivot = df_gender_gap.pivot(index='Categoria', columns='Sesso', values='Retention')
        if 'M' in gender_pivot.columns and 'F' in gender_pivot.columns:
            gender_pivot['Gap'] = gender_pivot['M'] - gender_pivot['F']
            gender_pivot = gender_pivot.sort_values('Gap', ascending=False)
            print(gender_pivot.round(1).to_string())

    # Analisi abbandono per fascia di carriera
    print("\n   Gender gap per anno di carriera:")
    df_carriera = df.merge(primo_anno, on='MmbCode')
    df_carriera['AnnoCarriera'] = df_carriera['Anno'] - df_carriera['AnnoPrimoTessera'] + 1

    for anno_c in [1, 2, 3, 5]:
        subset_m = df_carriera[(df_carriera['AnnoCarriera'] == anno_c) & (df_carriera['MmbSex'] == 'M')]
        subset_f = df_carriera[(df_carriera['AnnoCarriera'] == anno_c) & (df_carriera['MmbSex'] == 'F')]
        if len(subset_m) > 0 and len(subset_f) > 0:
            # Quanti arrivano all'anno successivo?
            next_year_m = df_carriera[(df_carriera['AnnoCarriera'] == anno_c + 1) & (df_carriera['MmbSex'] == 'M')]['MmbCode'].unique()
            next_year_f = df_carriera[(df_carriera['AnnoCarriera'] == anno_c + 1) & (df_carriera['MmbSex'] == 'F')]['MmbCode'].unique()

            curr_m = set(subset_m['MmbCode'].unique())
            curr_f = set(subset_f['MmbCode'].unique())

            pass_m = len(curr_m & set(next_year_m)) / len(curr_m) * 100 if len(curr_m) > 0 else 0
            pass_f = len(curr_f & set(next_year_f)) / len(curr_f) * 100 if len(curr_f) > 0 else 0

            print(f"   Anno {anno_c} -> {anno_c+1}: M={pass_m:.1f}%, F={pass_f:.1f}%, Gap={pass_m-pass_f:+.1f}pp")

    # =========================================================================
    # SALVATAGGIO RISULTATI
    # =========================================================================
    print("\n" + "=" * 70)
    print("7. SALVATAGGIO RISULTATI")
    print("=" * 70)

    # Summary JSON
    summary = {
        'curva_apprendimento': {
            'gare_anno1_attivi': float(anno1_attivi),
            'gare_anno1_persi': float(anno1_persi),
            'differenza_predittiva': float(anno1_attivi - anno1_persi)
        },
        'early_warning': {
            'circoli_critici': int(len(circoli_critici[circoli_critici['LivelioRischio'] == 'CRITICO'])),
            'circoli_alto_rischio': int(len(circoli_critici[circoli_critici['LivelioRischio'] == 'ALTO'])),
            'circoli_medio_rischio': int(len(circoli_attivi[circoli_attivi['LivelioRischio'] == 'MEDIO'])),
            'circoli_analizzati': int(len(circoli_attivi))
        },
        'effetto_maestro': {
            'retention_con_corsi': float(ret_con_corsi),
            'retention_senza_corsi': float(ret_senza_corsi),
            'differenza_pp': float(ret_con_corsi - ret_senza_corsi),
            'circoli_con_corsi': int(len(circoli_con_corsi))
        },
        'migrazione': {
            'giocatori_fedeli': int(len(fedeli)),
            'giocatori_migranti': int(len(migranti)),
            'pct_fedeli': float(100 * len(fedeli) / len(circoli_per_giocatore))
        },
        'gender_gap': {
            'retention_uomini': float(retention_sesso.get('M', 0)),
            'retention_donne': float(retention_sesso.get('F', 0)),
            'gap_pp': float(retention_sesso.get('M', 0) - retention_sesso.get('F', 0))
        }
    }

    with open(RESULTS_DIR / 'summary_avanzate.json', 'w') as f:
        json.dump(summary, f, indent=2)
    print("   Salvato summary_avanzate.json")

    # CSV dettagliati
    curva_media.to_csv(RESULTS_DIR / 'curva_apprendimento.csv', index=False)
    curva_confronto.to_csv(RESULTS_DIR / 'curva_confronto_attivi_persi.csv', index=False)
    print("   Salvato curva_apprendimento.csv")

    circoli_attivi.to_csv(RESULTS_DIR / 'early_warning_circoli.csv', index=False)
    circoli_critici.to_csv(RESULTS_DIR / 'circoli_critici.csv', index=False)
    rischio_regione.to_csv(RESULTS_DIR / 'rischio_per_regione.csv', index=False)
    print("   Salvato early_warning_circoli.csv")

    effetto_maestro.to_csv(RESULTS_DIR / 'effetto_maestro.csv', index=False)
    retention_con_num.to_csv(RESULTS_DIR / 'retention_per_circolo.csv', index=False)
    print("   Salvato effetto_maestro.csv")

    profilo_migrazione.to_csv(RESULTS_DIR / 'profilo_migrazione.csv', index=False)
    print("   Salvato profilo_migrazione.csv")

    if len(df_gender_gap) > 0:
        df_gender_gap.to_csv(RESULTS_DIR / 'gender_gap_categoria.csv', index=False)
        print("   Salvato gender_gap_categoria.csv")

    # =========================================================================
    # RIEPILOGO FINALE
    # =========================================================================
    print("\n" + "=" * 70)
    print("RIEPILOGO - INSIGHT CHIAVE")
    print("=" * 70)
    print(f"""
    1. CURVA DI APPRENDIMENTO:
       Chi resta gioca {anno1_attivi:.0f} gare il primo anno
       Chi abbandona ne gioca solo {anno1_persi:.0f}
       → SOGLIA CRITICA: ~{(anno1_attivi + anno1_persi)/2:.0f} gare/anno

    2. EARLY WARNING CIRCOLI:
       {len(circoli_critici[circoli_critici['LivelioRischio'] == 'CRITICO'])} circoli CRITICI (rischio chiusura imminente)
       {len(circoli_critici[circoli_critici['LivelioRischio'] == 'ALTO'])} circoli ALTO rischio
       → Intervenire subito!

    3. EFFETTO MAESTRO:
       Retention con corsi: {ret_con_corsi:.1f}%
       Retention senza corsi: {ret_senza_corsi:.1f}%
       → I corsi aumentano retention di {ret_con_corsi - ret_senza_corsi:+.1f} punti!

    4. MIGRAZIONE:
       {100*len(fedeli)/len(circoli_per_giocatore):.1f}% giocatori sono "fedeli" (1 solo circolo)
       {100*len(migranti)/len(circoli_per_giocatore):.1f}% hanno cambiato circolo
       → I migranti giocano di piu' ({migranti_info['GareGiocate'].mean():.0f} vs {fedeli_info['GareGiocate'].mean():.0f} gare/anno)

    5. GENDER GAP:
       Retention uomini: {retention_sesso.get('M', 0):.1f}%
       Retention donne: {retention_sesso.get('F', 0):.1f}%
       → Gap di {retention_sesso.get('M', 0) - retention_sesso.get('F', 0):+.1f} punti
    """)


if __name__ == '__main__':
    main()
