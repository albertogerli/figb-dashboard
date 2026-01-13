#!/usr/bin/env python3
"""
MODELLO PREDITTIVO DI RECUPERABILITÀ BRIDGISTI
===============================================

Modello sofisticato multi-fattoriale per identificare quali bridgisti
che hanno abbandonato sono più facilmente recuperabili.

Componenti del modello:
1. ENGAGEMENT SCORE - Attività passata (gare, punti, agonismo)
2. LOYALTY SCORE - Fedeltà storica (anni iscrizione, progressione)
3. RECENCY SCORE - Quanto tempo fa hanno smesso
4. HEALTH RISK SCORE - Rischio mortalità/malattia per età (ISTAT)
5. GEOGRAPHIC SCORE - Facilità recupero per zona
6. SOCIAL SCORE - Connessioni nel circolo

Output: Score finale 0-100 con classificazione priorità
"""

import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Paths
BASE_DIR = Path(__file__).parent
OUTPUT_DIR = BASE_DIR / 'output'
RESULTS_DIR = OUTPUT_DIR / 'results_recuperabilita'
RESULTS_DIR.mkdir(exist_ok=True)

# =============================================================================
# TAVOLE ATTUARIALI ISTAT - RISCHIO MORTALITÀ E MALATTIA
# =============================================================================
# Dati basati su tavole di mortalità ISTAT 2023 e statistiche sanitarie

# Probabilità di morte entro 1 anno per fascia d'età (per 1000)
MORTALITA_PER_1000 = {
    (0, 30): 0.3,      # Giovani: rischio bassissimo
    (30, 40): 0.8,
    (40, 50): 1.8,
    (50, 55): 3.5,
    (55, 60): 5.2,
    (60, 65): 8.5,
    (65, 70): 14.0,
    (70, 75): 23.0,
    (75, 80): 42.0,
    (80, 85): 78.0,
    (85, 90): 145.0,
    (90, 95): 250.0,
    (95, 120): 380.0
}

# Probabilità di malattia invalidante/limitante entro 1 anno (per 1000)
# Include: problemi mobilità, vista, demenza iniziale, etc.
MALATTIA_INVALIDANTE_PER_1000 = {
    (0, 30): 2.0,
    (30, 40): 5.0,
    (40, 50): 12.0,
    (50, 55): 20.0,
    (55, 60): 32.0,
    (60, 65): 48.0,
    (65, 70): 72.0,
    (70, 75): 105.0,
    (75, 80): 155.0,
    (80, 85): 220.0,
    (85, 90): 310.0,
    (90, 95): 420.0,
    (95, 120): 550.0
}

# Fattore di rischio cumulativo per anni dall'abbandono
# Dopo X anni, il rischio di non essere più recuperabili aumenta
RISCHIO_CUMULATIVO_ANNI = {
    1: 1.0,    # Primo anno: rischio base
    2: 1.15,   # Secondo anno: +15%
    3: 1.35,   # Terzo anno: +35%
    4: 1.60,   # Quarto anno: +60%
    5: 1.90,   # Quinto anno: +90%
    6: 2.30,   # Sesto anno: +130%
    7: 2.80,   # Settimo anno: +180%
    8: 3.50,   # Ottavo anno: +250%
}

# =============================================================================
# PESI DEL MODELLO
# =============================================================================
PESI = {
    'engagement': 0.25,      # 25% - Quanto erano attivi
    'loyalty': 0.20,         # 20% - Quanto erano fedeli
    'recency': 0.20,         # 20% - Quanto recente l'abbandono
    'health': 0.15,          # 15% - Rischio salute (penalità)
    'geographic': 0.10,      # 10% - Zona geografica
    'social': 0.10,          # 10% - Connessioni sociali nel circolo
}

# Retention rate per macroregione (inverso del churn)
RETENTION_MACROREGIONE = {
    'Nord-Est': 0.495,       # Migliore
    'Isole': 0.480,
    'Sud': 0.448,
    'Centro': 0.428,
    'Nord-Ovest': 0.413,     # Peggiore tra le principali
    'Altro': 0.096,
    'Nazionale': 0.786,
}

# Mapping regione -> macroregione
REGIONE_TO_MACRO = {
    'PIE': 'Nord-Ovest', 'VDA': 'Nord-Ovest', 'LOM': 'Nord-Ovest', 'LIG': 'Nord-Ovest',
    'TRT': 'Nord-Est', 'TRB': 'Nord-Est', 'FRI': 'Nord-Est', 'VEN': 'Nord-Est', 'EMI': 'Nord-Est',
    'TOS': 'Centro', 'UMB': 'Centro', 'MAR': 'Centro', 'LAZ': 'Centro',
    'ABR': 'Sud', 'MOL': 'Sud', 'CAM': 'Sud', 'PUG': 'Sud', 'BAS': 'Sud', 'CAB': 'Sud',
    'SIC': 'Isole', 'SAR': 'Isole'
}


def get_mortality_risk(eta, anni_da_churn=1):
    """
    Calcola il rischio di mortalità cumulativo.
    Considera l'età attuale e gli anni trascorsi dall'abbandono.
    """
    if pd.isna(eta):
        return 0.5  # Default medio se età sconosciuta

    # Trova la fascia d'età
    prob_morte_annua = 0
    for (min_eta, max_eta), prob in MORTALITA_PER_1000.items():
        if min_eta <= eta < max_eta:
            prob_morte_annua = prob / 1000
            break

    # Calcola rischio cumulativo per anni trascorsi
    # P(morte in N anni) = 1 - (1 - p)^N approssimato
    anni = min(anni_da_churn, 8)
    moltiplicatore = RISCHIO_CUMULATIVO_ANNI.get(anni, 3.5)

    # Rischio aumenta con l'età durante gli anni di assenza
    eta_proiettata = eta + anni_da_churn
    for (min_eta, max_eta), prob in MORTALITA_PER_1000.items():
        if min_eta <= eta_proiettata < max_eta:
            prob_morte_proiettata = prob / 1000
            break
    else:
        prob_morte_proiettata = 0.38  # 95+ anni

    # Media tra rischio iniziale e proiettato
    rischio_medio = (prob_morte_annua + prob_morte_proiettata) / 2

    # Rischio cumulativo
    rischio_cumulativo = 1 - (1 - rischio_medio) ** anni_da_churn

    return min(rischio_cumulativo * moltiplicatore, 0.95)


def get_illness_risk(eta, anni_da_churn=1):
    """
    Calcola il rischio di malattia invalidante cumulativo.
    """
    if pd.isna(eta):
        return 0.3

    # Trova la fascia d'età
    prob_malattia_annua = 0
    for (min_eta, max_eta), prob in MALATTIA_INVALIDANTE_PER_1000.items():
        if min_eta <= eta < max_eta:
            prob_malattia_annua = prob / 1000
            break

    # Rischio cumulativo
    anni = min(anni_da_churn, 8)
    rischio_cumulativo = 1 - (1 - prob_malattia_annua) ** anni

    return min(rischio_cumulativo, 0.90)


def get_health_risk_score(eta, anni_da_churn):
    """
    Score combinato di rischio salute (0-1, dove 1 = alto rischio = bassa recuperabilità)
    """
    mortality = get_mortality_risk(eta, anni_da_churn)
    illness = get_illness_risk(eta, anni_da_churn)

    # Combina i rischi (probabilità di essere ancora vivi E in salute)
    prob_disponibile = (1 - mortality) * (1 - illness * 0.7)  # Malattia pesa meno della morte

    # Inverti: vogliamo che alto score = alto rischio
    return 1 - prob_disponibile


def calculate_engagement_score(row):
    """
    Score di engagement basato sull'attività passata.
    Range: 0-100
    """
    score = 0

    # 1. Gare medie (0-40 punti)
    gare = row.get('GareMedie', 0) or 0
    if gare >= 50:
        score += 40
    elif gare >= 30:
        score += 35
    elif gare >= 20:
        score += 28
    elif gare >= 10:
        score += 18
    elif gare >= 5:
        score += 10
    else:
        score += 3

    # 2. Punti totali medi (0-25 punti)
    punti = row.get('PuntiMedi', 0) or 0
    if punti >= 5000:
        score += 25
    elif punti >= 2000:
        score += 20
    elif punti >= 1000:
        score += 15
    elif punti >= 500:
        score += 10
    elif punti >= 100:
        score += 5

    # 3. Agonista (0-20 punti)
    if row.get('EraAgonista', False):
        score += 20
    elif row.get('RatioChamp', 0) > 0.1:
        score += 12

    # 4. Partecipazione campionati (0-15 punti)
    ratio_champ = row.get('RatioChamp', 0) or 0
    if ratio_champ >= 0.3:
        score += 15
    elif ratio_champ >= 0.15:
        score += 10
    elif ratio_champ >= 0.05:
        score += 5

    return min(score, 100)


def calculate_loyalty_score(row):
    """
    Score di fedeltà/lealtà storica.
    Range: 0-100
    """
    score = 0

    # 1. Anni di presenza (0-50 punti)
    anni = row.get('AnniPresenza', 0) or 0
    if anni >= 7:
        score += 50
    elif anni >= 5:
        score += 42
    elif anni >= 4:
        score += 35
    elif anni >= 3:
        score += 28
    elif anni >= 2:
        score += 18
    else:
        score += 8

    # 2. Progressione categoria (0-30 punti)
    progressione = row.get('Progressione', 0) or 0
    if progressione >= 3:
        score += 30
    elif progressione >= 2:
        score += 25
    elif progressione >= 1:
        score += 18
    elif progressione > 0:
        score += 10

    # 3. Costanza (presente in anni consecutivi) (0-20 punti)
    # Approssimato dalla densità di presenza
    densita = anni / max(row.get('AnniDaChurn', 1) + anni, 1)
    score += int(densita * 20)

    return min(score, 100)


def calculate_recency_score(row):
    """
    Score basato su quanto recente è l'abbandono.
    Range: 0-100 (più recente = più alto)
    """
    anni_da_churn = row.get('AnniDaChurn', 5) or 5

    if anni_da_churn <= 1:
        return 100
    elif anni_da_churn <= 2:
        return 85
    elif anni_da_churn <= 3:
        return 68
    elif anni_da_churn <= 4:
        return 50
    elif anni_da_churn <= 5:
        return 35
    elif anni_da_churn <= 6:
        return 22
    elif anni_da_churn <= 7:
        return 12
    else:
        return 5


def calculate_geographic_score(row):
    """
    Score basato sulla zona geografica.
    Alcune zone hanno retention migliore = più facile recuperare.
    Range: 0-100
    """
    regione = row.get('Regione', '')
    macro = REGIONE_TO_MACRO.get(regione, 'Altro')
    retention = RETENTION_MACROREGIONE.get(macro, 0.4)

    # Normalizza retention (0.1-0.8) a score (0-100)
    score = (retention - 0.1) / 0.7 * 100

    # Bonus se ha provincia mappata (più facile contattare)
    if pd.notna(row.get('Provincia')):
        score += 10

    return min(max(score, 0), 100)


def calculate_social_score(row):
    """
    Score basato sulle connessioni sociali nel circolo.
    Range: 0-100
    """
    score = 50  # Base

    # Bonus se il circolo è ancora attivo
    if row.get('CircoloAttivo', False):
        score += 25

    # Bonus se ha giocato tante gare (più connessioni)
    gare = row.get('GareMedie', 0) or 0
    if gare >= 30:
        score += 15
    elif gare >= 15:
        score += 10

    # Bonus se era in categoria alta (più visibile nella community)
    cat = row.get('CategoriaFinale', 'NC')
    if cat in ['GM', 'LM', 'MS', 'HK', 'HA', 'HQ', 'HJ']:
        score += 15
    elif cat in ['1P', '1F', '1C', '1Q']:
        score += 10
    elif cat in ['2P', '2F', '2C', '2Q']:
        score += 5

    return min(score, 100)


def calculate_health_penalty(row):
    """
    Penalità basata sul rischio salute.
    Range: 0-100 (0 = nessuna penalità, 100 = non recuperabile)
    """
    eta = row.get('EtaAttuale', 70)
    anni_da_churn = row.get('AnniDaChurn', 1)

    risk = get_health_risk_score(eta, anni_da_churn)

    return risk * 100


def calculate_final_score(row):
    """
    Calcola lo score finale di recuperabilità.
    Range: 0-100
    """
    # Calcola tutti i sub-score
    engagement = calculate_engagement_score(row)
    loyalty = calculate_loyalty_score(row)
    recency = calculate_recency_score(row)
    geographic = calculate_geographic_score(row)
    social = calculate_social_score(row)
    health_penalty = calculate_health_penalty(row)

    # Score positivi pesati
    positive_score = (
        engagement * PESI['engagement'] +
        loyalty * PESI['loyalty'] +
        recency * PESI['recency'] +
        geographic * PESI['geographic'] +
        social * PESI['social']
    )

    # Applica penalità salute
    # Formula: score_finale = score_positivo * (1 - health_penalty * peso_health)
    health_factor = 1 - (health_penalty / 100) * PESI['health'] * 2

    final_score = positive_score * health_factor

    return max(min(final_score, 100), 0)


def classify_priority(score, health_penalty, eta):
    """
    Classifica la priorità di recupero.
    """
    if health_penalty >= 70 or eta >= 90:
        return '5-NON_RECUPERABILE'
    elif health_penalty >= 50 or eta >= 85:
        return '4-DIFFICILE'
    elif score >= 70:
        return '1-URGENTE'
    elif score >= 50:
        return '2-ALTA'
    elif score >= 30:
        return '3-MEDIA'
    else:
        return '4-BASSA'


def main():
    print("=" * 70)
    print("MODELLO PREDITTIVO DI RECUPERABILITÀ BRIDGISTI")
    print("=" * 70)

    # Carica dati
    print("\n📂 Caricamento dati...")
    df = pd.read_csv(OUTPUT_DIR / 'dati_unificati_2017_2025.csv')
    print(f"   Record totali: {len(df):,}")

    # Identifica giocatori churned
    print("\n🔍 Identificazione giocatori churned...")
    ultimo_anno = df['Anno'].max()

    # Giocatori attivi nel 2025
    attivi_2025 = set(df[df['Anno'] == ultimo_anno]['MmbCode'].unique())
    print(f"   Attivi {ultimo_anno}: {len(attivi_2025):,}")

    # Tutti i giocatori storici
    tutti_giocatori = set(df['MmbCode'].unique())
    print(f"   Giocatori totali storici: {len(tutti_giocatori):,}")

    # Churned = storici - attivi
    churned_codes = tutti_giocatori - attivi_2025
    print(f"   Giocatori churned: {len(churned_codes):,}")

    # Costruisci dataset churned con statistiche aggregate
    print("\n📊 Calcolo statistiche per giocatore...")

    # Aggrega per giocatore
    giocatore_stats = df.groupby('MmbCode').agg({
        'MmbName': 'last',
        'Anno': ['min', 'max', 'count'],
        'GareGiocate': 'mean',
        'PuntiTotali': 'mean',
        'PuntiCampionati': 'mean',
        'Anni': 'last',  # Ultima età registrata
        'GrpArea': 'last',
        'GrpName': 'last',
        'CatLabel': 'last',
        'MbtDesc': 'last',
        'IsAgonista': 'max',  # Se è mai stato agonista
        'AdmCity': 'last',
        'MmbSex': 'first'
    })

    # Flatten columns
    giocatore_stats.columns = [
        'Nome', 'AnnoInizio', 'AnnoFine', 'AnniPresenza',
        'GareMedie', 'PuntiMedi', 'PuntiChampMedi',
        'UltimaEta', 'Regione', 'Circolo', 'CategoriaFinale',
        'TipoTessera', 'EraAgonista', 'Citta', 'Sesso'
    ]
    giocatore_stats = giocatore_stats.reset_index()

    # Filtra solo churned
    churned_df = giocatore_stats[giocatore_stats['MmbCode'].isin(churned_codes)].copy()
    print(f"   Record churned: {len(churned_df):,}")

    # Calcola variabili aggiuntive
    print("\n🧮 Calcolo variabili derivate...")

    # Anni da churn
    churned_df['AnniDaChurn'] = ultimo_anno - churned_df['AnnoFine']

    # Età attuale stimata
    churned_df['EtaAttuale'] = churned_df['UltimaEta'] + churned_df['AnniDaChurn']

    # Progressione categoria (semplificata)
    cat_order = {'NC': 0, '4F': 1, '4Q': 2, '4C': 3, '4P': 4,
                 '3F': 5, '3Q': 6, '3C': 7, '3P': 8,
                 '2F': 9, '2Q': 10, '2C': 11, '2P': 12,
                 '1F': 13, '1Q': 14, '1C': 15, '1P': 16,
                 'HJ': 17, 'HQ': 18, 'HA': 19, 'HK': 20,
                 'MS': 21, 'LM': 22, 'GM': 23}
    churned_df['CatNum'] = churned_df['CategoriaFinale'].map(cat_order).fillna(0)
    churned_df['Progressione'] = churned_df['CatNum'] / churned_df['AnniPresenza'].clip(lower=1)

    # Ratio campionati
    churned_df['RatioChamp'] = churned_df['PuntiChampMedi'] / churned_df['PuntiMedi'].replace(0, 1)
    churned_df['RatioChamp'] = churned_df['RatioChamp'].clip(0, 1)

    # Circoli ancora attivi
    circoli_attivi = set(df[df['Anno'] == ultimo_anno]['GrpName'].unique())
    churned_df['CircoloAttivo'] = churned_df['Circolo'].isin(circoli_attivi)

    # Aggiungi provincia se disponibile
    if 'Provincia' in df.columns:
        prov_map = df.groupby('MmbCode')['Provincia'].last().to_dict()
        churned_df['Provincia'] = churned_df['MmbCode'].map(prov_map)

    # =================================================================
    # CALCOLO SCORE DI RECUPERABILITÀ
    # =================================================================
    print("\n🎯 Calcolo score di recuperabilità...")

    # Calcola tutti i sub-score
    churned_df['EngagementScore'] = churned_df.apply(calculate_engagement_score, axis=1)
    churned_df['LoyaltyScore'] = churned_df.apply(calculate_loyalty_score, axis=1)
    churned_df['RecencyScore'] = churned_df.apply(calculate_recency_score, axis=1)
    churned_df['GeographicScore'] = churned_df.apply(calculate_geographic_score, axis=1)
    churned_df['SocialScore'] = churned_df.apply(calculate_social_score, axis=1)
    churned_df['HealthPenalty'] = churned_df.apply(calculate_health_penalty, axis=1)

    # Score finale
    churned_df['RecoverabilityScore'] = churned_df.apply(calculate_final_score, axis=1)

    # Priorità
    churned_df['Priorita'] = churned_df.apply(
        lambda r: classify_priority(r['RecoverabilityScore'], r['HealthPenalty'], r['EtaAttuale']),
        axis=1
    )

    # Rischio specifico
    churned_df['RischioMorte'] = churned_df.apply(
        lambda r: get_mortality_risk(r['EtaAttuale'], r['AnniDaChurn']) * 100, axis=1
    )
    churned_df['RischioMalattia'] = churned_df.apply(
        lambda r: get_illness_risk(r['EtaAttuale'], r['AnniDaChurn']) * 100, axis=1
    )

    # Ordina per score
    churned_df = churned_df.sort_values('RecoverabilityScore', ascending=False)

    # =================================================================
    # STATISTICHE E OUTPUT
    # =================================================================
    print("\n" + "=" * 70)
    print("RISULTATI MODELLO")
    print("=" * 70)

    # Distribuzione priorità
    print("\n📊 Distribuzione per priorità:")
    prio_dist = churned_df['Priorita'].value_counts().sort_index()
    for prio, count in prio_dist.items():
        pct = count / len(churned_df) * 100
        print(f"   {prio}: {count:,} ({pct:.1f}%)")

    # Score medio per priorità
    print("\n📈 Score medio per priorità:")
    for prio in sorted(churned_df['Priorita'].unique()):
        subset = churned_df[churned_df['Priorita'] == prio]
        print(f"   {prio}: Score {subset['RecoverabilityScore'].mean():.1f}, "
              f"Età media {subset['EtaAttuale'].mean():.1f}, "
              f"Rischio salute {subset['HealthPenalty'].mean():.1f}%")

    # Top 10 recuperabili
    print("\n🏆 Top 10 più recuperabili:")
    top10 = churned_df.head(10)
    for _, row in top10.iterrows():
        print(f"   {row['Nome'][:30]:30} | Score: {row['RecoverabilityScore']:.1f} | "
              f"Età: {row['EtaAttuale']:.0f} | Gare: {row['GareMedie']:.1f} | "
              f"Anni assente: {row['AnniDaChurn']}")

    # =================================================================
    # SALVATAGGIO OUTPUT
    # =================================================================
    print("\n💾 Salvataggio risultati...")

    # 1. Lista completa
    cols_output = [
        'MmbCode', 'Nome', 'Sesso', 'EtaAttuale', 'Citta', 'Provincia', 'Regione',
        'Circolo', 'CircoloAttivo', 'CategoriaFinale', 'TipoTessera',
        'AnnoInizio', 'AnnoFine', 'AnniPresenza', 'AnniDaChurn',
        'GareMedie', 'PuntiMedi', 'EraAgonista', 'RatioChamp',
        'RecoverabilityScore', 'Priorita',
        'EngagementScore', 'LoyaltyScore', 'RecencyScore',
        'GeographicScore', 'SocialScore', 'HealthPenalty',
        'RischioMorte', 'RischioMalattia'
    ]
    cols_available = [c for c in cols_output if c in churned_df.columns]

    churned_df[cols_available].to_csv(
        RESULTS_DIR / 'bridgisti_recuperabili_completo.csv', index=False
    )
    print(f"   ✓ bridgisti_recuperabili_completo.csv ({len(churned_df):,} record)")

    # 2. Solo priorità alta (1-URGENTE e 2-ALTA)
    alta_priorita = churned_df[churned_df['Priorita'].isin(['1-URGENTE', '2-ALTA'])]
    alta_priorita[cols_available].to_csv(
        RESULTS_DIR / 'bridgisti_priorita_alta.csv', index=False
    )
    print(f"   ✓ bridgisti_priorita_alta.csv ({len(alta_priorita):,} record)")

    # 3. Aggregazione per provincia (per mappa)
    if 'Provincia' in churned_df.columns:
        prov_agg = churned_df.groupby('Provincia').agg({
            'MmbCode': 'count',
            'RecoverabilityScore': 'mean',
            'EtaAttuale': 'mean',
            'HealthPenalty': 'mean',
            'GareMedie': 'mean'
        }).reset_index()
        prov_agg.columns = ['Provincia', 'NumRecuperabili', 'ScoreMedio',
                           'EtaMedia', 'RischioSaluteMedio', 'GareMedie']
        prov_agg = prov_agg.sort_values('NumRecuperabili', ascending=False)
        prov_agg.to_csv(RESULTS_DIR / 'recuperabili_per_provincia.csv', index=False)
        print(f"   ✓ recuperabili_per_provincia.csv ({len(prov_agg)} province)")

    # 4. Aggregazione per regione (per mappa)
    reg_agg = churned_df.groupby('Regione').agg({
        'MmbCode': 'count',
        'RecoverabilityScore': 'mean',
        'EtaAttuale': 'mean',
        'HealthPenalty': 'mean',
        'Priorita': lambda x: (x.isin(['1-URGENTE', '2-ALTA'])).sum()
    }).reset_index()
    reg_agg.columns = ['Regione', 'NumRecuperabili', 'ScoreMedio',
                       'EtaMedia', 'RischioSaluteMedio', 'AltaPriorita']
    reg_agg = reg_agg.sort_values('NumRecuperabili', ascending=False)
    reg_agg.to_csv(RESULTS_DIR / 'recuperabili_per_regione.csv', index=False)
    print(f"   ✓ recuperabili_per_regione.csv ({len(reg_agg)} regioni)")

    # 5. Statistiche summary
    summary = {
        'totale_churned': len(churned_df),
        'urgenti': len(churned_df[churned_df['Priorita'] == '1-URGENTE']),
        'alta_priorita': len(churned_df[churned_df['Priorita'] == '2-ALTA']),
        'media_priorita': len(churned_df[churned_df['Priorita'] == '3-MEDIA']),
        'bassa_priorita': len(churned_df[churned_df['Priorita'] == '4-BASSA']),
        'non_recuperabili': len(churned_df[churned_df['Priorita'].str.contains('NON_RECUPERABILE|DIFFICILE')]),
        'score_medio': churned_df['RecoverabilityScore'].mean(),
        'eta_media': churned_df['EtaAttuale'].mean(),
        'rischio_salute_medio': churned_df['HealthPenalty'].mean(),
        'anni_assenza_media': churned_df['AnniDaChurn'].mean(),
    }

    import json
    with open(RESULTS_DIR / 'summary_recuperabilita.json', 'w') as f:
        json.dump(summary, f, indent=2)
    print(f"   ✓ summary_recuperabilita.json")

    # =================================================================
    # RIEPILOGO FINALE
    # =================================================================
    print("\n" + "=" * 70)
    print("RIEPILOGO FINALE")
    print("=" * 70)

    recuperabili_tot = summary['urgenti'] + summary['alta_priorita']
    print(f"""
    📌 BRIDGISTI ANALIZZATI: {summary['totale_churned']:,}

    🎯 PRIORITÀ DI RECUPERO:
       • 1-URGENTE:        {summary['urgenti']:,} ({summary['urgenti']/summary['totale_churned']*100:.1f}%)
       • 2-ALTA:           {summary['alta_priorita']:,} ({summary['alta_priorita']/summary['totale_churned']*100:.1f}%)
       • 3-MEDIA:          {summary['media_priorita']:,} ({summary['media_priorita']/summary['totale_churned']*100:.1f}%)
       • 4-BASSA/DIFFICILE:{summary['bassa_priorita'] + summary['non_recuperabili']:,}

    📊 METRICHE MEDIE:
       • Score recuperabilità: {summary['score_medio']:.1f}/100
       • Età attuale stimata:  {summary['eta_media']:.1f} anni
       • Rischio salute:       {summary['rischio_salute_medio']:.1f}%
       • Anni di assenza:      {summary['anni_assenza_media']:.1f}

    🚀 RACCOMANDAZIONE:
       Concentrare gli sforzi sui {recuperabili_tot:,} bridgisti
       con priorità URGENTE o ALTA per massimizzare ROI.
    """)

    print("✅ Analisi completata!")
    print(f"   Output salvati in: {RESULTS_DIR}")


if __name__ == '__main__':
    main()
