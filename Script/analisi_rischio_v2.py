#!/usr/bin/env python3
"""
ANALISI RISCHIO CHURN v2
Logica corretta: chi gioca tanto NON è a rischio!
"""

import pandas as pd
import numpy as np
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
OUTPUT_DIR = BASE_DIR / 'output'

print("=" * 80)
print("ANALISI RISCHIO CHURN v2 - LOGICA CORRETTA")
print("=" * 80)

# Carica dati
print("\n[1/5] Caricamento dati...")
df = pd.read_csv(OUTPUT_DIR / 'dati_unificati_2017_2025.csv')
df['MmbCode'] = df['MmbCode'].str.strip()
df['MmbName'] = df['MmbName'].str.strip()

# Aggregazione per giocatore
print("\n[2/5] Calcolo metriche per giocatore...")
giocatori = df.groupby('MmbCode').agg({
    'MmbName': 'last',
    'Anno': ['min', 'max', 'count'],
    'GareGiocate': ['mean', 'std', 'max', 'sum'],
    'PuntiCampionati': 'sum',
    'PuntiTotali': 'sum',
    'CatLabel': 'last',
    'Anni': 'last',
    'GrpName': 'last',
    'GrpArea': 'last',
    'AdmCity': 'last',
    'IsAgonista': 'max'
}).reset_index()

giocatori.columns = ['MmbCode', 'Nome', 'AnnoInizio', 'AnnoFine', 'AnniPresenza',
                     'GareMedie', 'GareStd', 'GareMax', 'GareTotali',
                     'PuntiCamp', 'PuntiTot', 'Categoria', 'Eta',
                     'Circolo', 'Regione', 'Citta', 'Agonista']

giocatori['GareStd'] = giocatori['GareStd'].fillna(0)
giocatori['Attivo2025'] = giocatori['AnnoFine'] == 2025

# Solo attivi nel 2025
attivi = giocatori[giocatori['Attivo2025']].copy()
print(f"   Giocatori attivi 2025: {len(attivi):,}")

# ============================================================================
# NUOVA LOGICA: CRITERI ASSOLUTI
# ============================================================================
print("\n[3/5] Calcolo rischio con criteri ASSOLUTI...")

def calcola_rischio_reale(row):
    """
    Rischio REALE basato su comportamenti predittivi di churn.
    Chi gioca tanto NON è a rischio!
    """
    rischio_punti = 0
    motivi = []

    gare = row['GareMedie']
    anni = row['AnniPresenza']
    gare_max = row['GareMax']
    gare_std = row['GareStd']
    eta = row['Eta'] if pd.notna(row['Eta']) else 60
    agonista = row['Agonista']

    # === FATTORI POSITIVI (riducono rischio) ===

    # Chi gioca MOLTO è sicuro (soglia: 15+ gare/anno)
    if gare >= 30:
        rischio_punti -= 50  # Giocatore super-attivo, rischio quasi nullo
        motivi.append("Super-attivo (30+ gare)")
    elif gare >= 20:
        rischio_punti -= 30  # Molto attivo
        motivi.append("Molto attivo (20+ gare)")
    elif gare >= 15:
        rischio_punti -= 20  # Attivo
        motivi.append("Attivo (15+ gare)")
    elif gare >= 10:
        rischio_punti -= 10  # Regolare
        motivi.append("Regolare (10+ gare)")

    # Fedeltà nel tempo (5+ anni = fedele)
    if anni >= 7:
        rischio_punti -= 20
        motivi.append("Fedele (7+ anni)")
    elif anni >= 5:
        rischio_punti -= 15
        motivi.append("Consolidato (5+ anni)")
    elif anni >= 3:
        rischio_punti -= 5
        motivi.append("Stabile (3+ anni)")

    # Agonista = più investito
    if agonista:
        rischio_punti -= 10
        motivi.append("Agonista")

    # Ha raggiunto picchi alti = passione
    if gare_max >= 50:
        rischio_punti -= 10
        motivi.append("Ha giocato 50+ gare in un anno")

    # === FATTORI NEGATIVI (aumentano rischio) ===

    # Poche gare = potenziale disinteresse
    if gare < 5:
        rischio_punti += 40
        motivi.append("Pochissime gare (<5)")
    elif gare < 8:
        rischio_punti += 25
        motivi.append("Poche gare (<8)")
    elif gare < 10:
        rischio_punti += 15
        motivi.append("Gare sotto media (<10)")

    # Nuovo = più fragile (primi 2 anni critici)
    if anni <= 1:
        rischio_punti += 30
        motivi.append("Primo anno (critico)")
    elif anni == 2:
        rischio_punti += 20
        motivi.append("Secondo anno (ancora fragile)")

    # Variabilità alta = incostante
    if gare > 0 and (gare_std / gare) > 0.5:
        rischio_punti += 10
        motivi.append("Partecipazione incostante")

    # Calo rispetto al picco
    if gare_max > 0 and gare < gare_max * 0.3:
        rischio_punti += 20
        motivi.append("Forte calo vs picco")
    elif gare_max > 0 and gare < gare_max * 0.5:
        rischio_punti += 10
        motivi.append("Calo vs picco")

    # === CLASSIFICAZIONE ===
    # Score più alto = più rischio
    # Range: -80 (zero rischio) a +70 (massimo rischio)

    if rischio_punti <= -30:
        livello = 'NULLO'
    elif rischio_punti <= -10:
        livello = 'BASSO'
    elif rischio_punti <= 10:
        livello = 'MEDIO'
    elif rischio_punti <= 30:
        livello = 'ALTO'
    else:
        livello = 'CRITICO'

    return pd.Series({
        'RischioPunti': rischio_punti,
        'LivelloRischio': livello,
        'Motivi': '; '.join(motivi[:3])  # Max 3 motivi
    })

# Applica calcolo
risultati = attivi.apply(calcola_rischio_reale, axis=1)
attivi = pd.concat([attivi, risultati], axis=1)

# ============================================================================
# FILTRA SOLO CHI È VERAMENTE A RISCHIO
# ============================================================================
print("\n[4/5] Filtraggio giocatori a rischio...")

# Solo ALTO e CRITICO sono da contattare
a_rischio = attivi[attivi['LivelloRischio'].isin(['ALTO', 'CRITICO'])].copy()

print(f"\n   Distribuzione rischio (TUTTI gli attivi):")
for livello in ['NULLO', 'BASSO', 'MEDIO', 'ALTO', 'CRITICO']:
    n = len(attivi[attivi['LivelloRischio'] == livello])
    print(f"   {livello}: {n:,} ({n/len(attivi)*100:.1f}%)")

print(f"\n   VERAMENTE a rischio: {len(a_rischio):,}")

# ============================================================================
# PRIORITIZZAZIONE
# ============================================================================
print("\n[5/5] Prioritizzazione...")

def priorita_intervento(row):
    """Priorità: giovani + rischio alto = intervento urgente"""
    score = 0
    eta = row['Eta'] if pd.notna(row['Eta']) else 70

    # Età (giovani = priorità)
    if eta < 30: score += 100
    elif eta < 40: score += 80
    elif eta < 50: score += 60
    elif eta < 60: score += 40
    elif eta < 70: score += 20
    else: score += 10

    # Livello rischio
    if row['LivelloRischio'] == 'CRITICO':
        score += 40
    else:
        score += 20

    # Potenziale (se ha giocato molto in passato, recuperabile)
    if row['GareMax'] >= 30:
        score += 20
    elif row['GareMax'] >= 15:
        score += 10

    return score

a_rischio['PrioritaScore'] = a_rischio.apply(priorita_intervento, axis=1)

def livello_priorita(score):
    if score >= 120: return '1-URGENTE'
    elif score >= 80: return '2-ALTA'
    elif score >= 50: return '3-MEDIA'
    else: return '4-BASSA'

a_rischio['Priorita'] = a_rischio['PrioritaScore'].apply(livello_priorita)

# Ordina
a_rischio = a_rischio.sort_values('PrioritaScore', ascending=False)

# Output
output = a_rischio[[
    'Priorita', 'PrioritaScore', 'MmbCode', 'Nome', 'Eta',
    'LivelloRischio', 'RischioPunti', 'GareMedie', 'GareMax',
    'AnniPresenza', 'Categoria', 'Circolo', 'Regione', 'Citta', 'Motivi'
]].copy()

output.columns = [
    'Priorita', 'Score', 'Codice', 'Nome', 'Eta',
    'Rischio', 'PuntiRischio', 'GareMedie', 'GareMax',
    'AnniPresenza', 'Categoria', 'Circolo', 'Regione', 'Citta', 'Motivi'
]

output['Eta'] = output['Eta'].fillna(0).astype(int)
output['GareMedie'] = output['GareMedie'].round(1)

# Salva
output_path = OUTPUT_DIR / 'results_innovativi' / 'giocatori_rischio_REALE.csv'
output.to_csv(output_path, index=False)

# ============================================================================
# VERIFICA: Alberto Gerli NON deve essere nella lista!
# ============================================================================
print(f"\n{'='*80}")
print("VERIFICA LOGICA")
print(f"{'='*80}")

# Cerca Gerli Alberto
gerli = attivi[attivi['Nome'].str.contains('GERLI ALBERTO', case=False, na=False)]
if len(gerli) > 0:
    g = gerli.iloc[0]
    print(f"\nGERLI ALBERTO GIOVANNI:")
    print(f"   Gare medie: {g['GareMedie']:.1f}")
    print(f"   Gare max: {g['GareMax']:.0f}")
    print(f"   Anni presenza: {g['AnniPresenza']}")
    print(f"   Livello rischio: {g['LivelloRischio']}")
    print(f"   Punti rischio: {g['RischioPunti']}")
    print(f"   Motivi: {g['Motivi']}")

    if g['LivelloRischio'] in ['ALTO', 'CRITICO']:
        print("   >>> ERRORE: Non dovrebbe essere a rischio!")
    else:
        print("   >>> CORRETTO: Non è a rischio")

# ============================================================================
# RIEPILOGO
# ============================================================================
print(f"\n{'='*80}")
print("RIEPILOGO FINALE")
print(f"{'='*80}")

print(f"\nGiocatori VERAMENTE a rischio: {len(output):,}")
print(f"\nDistribuzione priorità:")
for p in ['1-URGENTE', '2-ALTA', '3-MEDIA', '4-BASSA']:
    n = len(output[output['Priorita'] == p])
    print(f"   {p}: {n:,}")

print(f"\n{'='*80}")
print("TOP 20 - INTERVENTO IMMEDIATO")
print(f"{'='*80}")
print(f"{'Nome':<28} {'Età':>3} {'Gare':>5} {'Rischio':<8} {'Motivo':<30}")
print("-" * 80)

for _, r in output.head(20).iterrows():
    nome = str(r['Nome'])[:26] if pd.notna(r['Nome']) else 'N/D'
    motivo = str(r['Motivi'])[:28] if pd.notna(r['Motivi']) else ''
    print(f"{nome:<28} {r['Eta']:>3} {r['GareMedie']:>5.1f} {r['Rischio']:<8} {motivo:<30}")

print(f"\n{'='*80}")
print(f"FILE SALVATO: {output_path}")
print(f"{'='*80}")
