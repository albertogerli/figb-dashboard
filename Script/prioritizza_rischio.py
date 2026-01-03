#!/usr/bin/env python3
"""
PRIORITIZZAZIONE GIOCATORI A RISCHIO
Crea lista actionable con nomi e priorità
"""

import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
OUTPUT_DIR = BASE_DIR / 'output'

print("=" * 80)
print("PRIORITIZZAZIONE GIOCATORI A RISCHIO")
print("=" * 80)

# Carica dati
print("\n[1/4] Caricamento dati...")
rischio = pd.read_csv(OUTPUT_DIR / 'results_innovativi' / 'giocatori_attivi_a_rischio.csv')
dati = pd.read_csv(OUTPUT_DIR / 'dati_unificati_2017_2025.csv')

# Pulisci MmbCode (rimuovi spazi)
rischio['MmbCode'] = rischio['MmbCode'].str.strip()
dati['MmbCode'] = dati['MmbCode'].str.strip()

print(f"   Giocatori a rischio: {len(rischio):,}")

# Prendi ultima info per ogni giocatore (anno più recente)
print("\n[2/4] Estrazione informazioni giocatori...")
dati_recenti = dati.sort_values('Anno', ascending=False).drop_duplicates('MmbCode', keep='first')

# Merge per ottenere nomi e altre info
rischio_completo = rischio.merge(
    dati_recenti[['MmbCode', 'MmbName', 'GrpName', 'CatLabel', 'MmbSex', 'AdmCity']],
    on='MmbCode',
    how='left'
)

print(f"   Match trovati: {rischio_completo['MmbName'].notna().sum():,}")

# Calcola priorità
print("\n[3/4] Calcolo priorità...")

def calcola_priorita(row):
    """
    Priorità basata su:
    1. Età giovane (MASSIMA priorità - futuro della federazione)
    2. Rischio critico vs attenzione
    3. Più gare giocate (più investimento, più da perdere)
    4. Categoria (agonisti valgono di più)
    """
    score = 0

    # ETÀ - giovani hanno massima priorità (inversamente proporzionale)
    eta = row['Eta'] if pd.notna(row['Eta']) else 70
    if eta < 30:
        score += 100  # Under 30 = priorità massima
    elif eta < 40:
        score += 80   # Under 40 = alta
    elif eta < 50:
        score += 60   # Under 50 = media-alta
    elif eta < 60:
        score += 40   # Under 60 = media
    elif eta < 70:
        score += 20   # Under 70 = bassa
    else:
        score += 10   # Over 70 = minima

    # RISCHIO CRITICO vale di più
    if row['RischioChurn'] == 'CRITICO':
        score += 30
    else:
        score += 15

    # GARE - chi gioca di più è più investito
    gare = row['GareMedie'] if pd.notna(row['GareMedie']) else 0
    score += min(gare * 2, 20)  # max 20 punti

    # CATEGORIA - agonisti priorità
    cat = str(row.get('CatLabel', 'NC'))
    if cat.startswith(('1', 'H', 'M', 'G', 'L')):  # Prima, Honor, Master
        score += 15
    elif cat.startswith(('2', '3')):  # Seconda, Terza
        score += 10
    elif cat.startswith('4'):  # Quarta
        score += 5

    return score

rischio_completo['PunteggioPriorita'] = rischio_completo.apply(calcola_priorita, axis=1)

# Assegna livello priorità
def livello_priorita(score):
    if score >= 100:
        return '1-URGENTE'
    elif score >= 70:
        return '2-ALTA'
    elif score >= 50:
        return '3-MEDIA'
    else:
        return '4-BASSA'

rischio_completo['LivelloPriorita'] = rischio_completo['PunteggioPriorita'].apply(livello_priorita)

# Ordina per priorità
rischio_completo = rischio_completo.sort_values('PunteggioPriorita', ascending=False)

# Pulisci nomi (rimuovi spazi extra)
rischio_completo['MmbName'] = rischio_completo['MmbName'].str.strip()
rischio_completo['GrpName'] = rischio_completo['GrpName'].fillna('N/D').str.strip()
rischio_completo['AdmCity'] = rischio_completo['AdmCity'].fillna('N/D').str.strip()
rischio_completo['CatLabel'] = rischio_completo['CatLabel'].fillna('NC')

# Seleziona e rinomina colonne
output = rischio_completo[[
    'LivelloPriorita', 'PunteggioPriorita', 'MmbCode', 'MmbName',
    'Eta', 'RischioChurn', 'EngagementScore', 'GareMedie',
    'CatLabel', 'GrpName', 'Regione', 'AdmCity'
]].copy()

output.columns = [
    'Priorita', 'Score', 'Codice', 'Nome',
    'Eta', 'Rischio', 'EngagementScore', 'GareMedie',
    'Categoria', 'Circolo', 'Regione', 'Citta'
]

# Arrotonda
output['Eta'] = output['Eta'].fillna(0).astype(int)
output['GareMedie'] = output['GareMedie'].round(1)
output['EngagementScore'] = output['EngagementScore'].round(2)

# Salva
print("\n[4/4] Salvataggio...")
output_path = OUTPUT_DIR / 'results_innovativi' / 'giocatori_priorita_intervento.csv'
output.to_csv(output_path, index=False)

# Statistiche
print(f"\n{'='*80}")
print("RIEPILOGO PRIORITÀ")
print(f"{'='*80}")

priorita_counts = output['Priorita'].value_counts().sort_index()
for p, n in priorita_counts.items():
    print(f"   {p}: {n:,} giocatori")

print(f"\n   TOTALE: {len(output):,} giocatori a rischio")

# Top 20 per intervento immediato
print(f"\n{'='*80}")
print("TOP 20 - INTERVENTO IMMEDIATO")
print(f"{'='*80}")
print(f"{'Nome':<30} {'Età':>4} {'Rischio':<10} {'Circolo':<25} {'Città':<15}")
print("-" * 90)

for _, r in output.head(20).iterrows():
    nome = r['Nome'][:28] if pd.notna(r['Nome']) else 'N/D'
    circolo = r['Circolo'][:23] if pd.notna(r['Circolo']) else 'N/D'
    citta = r['Citta'][:13] if pd.notna(r['Citta']) else 'N/D'
    print(f"{nome:<30} {r['Eta']:>4} {r['Rischio']:<10} {circolo:<25} {citta:<15}")

# Statistiche per fascia età
print(f"\n{'='*80}")
print("DISTRIBUZIONE PER ETÀ")
print(f"{'='*80}")

def fascia_eta(eta):
    if eta < 30: return 'Under 30'
    elif eta < 40: return '30-39'
    elif eta < 50: return '40-49'
    elif eta < 60: return '50-59'
    elif eta < 70: return '60-69'
    else: return 'Over 70'

output['FasciaEta'] = output['Eta'].apply(fascia_eta)
for fascia in ['Under 30', '30-39', '40-49', '50-59', '60-69', 'Over 70']:
    n = len(output[output['FasciaEta'] == fascia])
    print(f"   {fascia}: {n:,} ({n/len(output)*100:.1f}%)")

print(f"\n{'='*80}")
print(f"FILE SALVATO: {output_path}")
print(f"{'='*80}")
