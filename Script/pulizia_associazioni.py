#!/usr/bin/env python3
"""
PULIZIA NOMI ASSOCIAZIONI
Fuzzy matching CONSERVATIVO per unificare solo nomi veramente simili
"""

import pandas as pd
import re
from collections import defaultdict
from difflib import SequenceMatcher
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
OUTPUT_DIR = BASE_DIR / 'output'

print("=" * 80)
print("PULIZIA NOMI ASSOCIAZIONI (FUZZY MATCHING CONSERVATIVO)")
print("=" * 80)

# Carica dati ORIGINALI (backup)
print("\n[1/6] Caricamento dati...")
# Ricarica da backup se esiste, altrimenti usa il file corrente
df = pd.read_csv(OUTPUT_DIR / 'dati_unificati_2017_2025.csv')

# Se già processato, usa GrpName originale
if 'Associazione' in df.columns:
    df = df.drop(columns=['Associazione'])

df['GrpName'] = df['GrpName'].str.strip()

nomi_originali = df['GrpName'].dropna().unique()
print(f"   Associazioni uniche originali: {len(nomi_originali)}")

# ============================================================================
# LISTA CITTÀ ITALIANE (per evitare merge errati)
# ============================================================================
CITTA_ITALIANE = {
    'ROMA', 'MILANO', 'NAPOLI', 'TORINO', 'PALERMO', 'GENOVA', 'BOLOGNA',
    'FIRENZE', 'BARI', 'CATANIA', 'CATANZARO', 'VENEZIA', 'VERONA', 'MESSINA',
    'PADOVA', 'TRIESTE', 'TARANTO', 'BRESCIA', 'PARMA', 'MODENA', 'REGGIO',
    'PERUGIA', 'LIVORNO', 'RAVENNA', 'CAGLIARI', 'FOGGIA', 'RIMINI', 'SALERNO',
    'FERRARA', 'SASSARI', 'LATINA', 'GIUGLIANO', 'MONZA', 'SIRACUSA', 'PESCARA',
    'BERGAMO', 'FORLÌ', 'TRENTO', 'VICENZA', 'TERNI', 'BOLZANO', 'NOVARA',
    'PIACENZA', 'ANCONA', 'ANDRIA', 'AREZZO', 'UDINE', 'CESENA', 'LECCE',
    'PESARO', 'BARLETTA', 'ALESSANDRIA', 'PISA', 'PISTOIA', 'LUCCA', 'COMO',
    'CASERTA', 'BRINDISI', 'COSENZA', 'RAGUSA', 'TRAPANI', 'JESI', 'PORDENONE',
    'DESIO', 'SORRENTO', 'BRENO', 'ORISTANO', 'IVREA', 'SORA', 'FROSINONE',
    'AVELLINO', 'BAVENO', 'MANTOVA', 'BIELLA', 'CREMONA', 'CREMA', 'PAVIA', 'VARESE',
    'SANNIO', 'GARDA', 'SELARGIUS', 'CONEGLIANO', 'SASSUOLO', 'CAGLI'
}

# Abbreviazioni province
ABBREV_PROVINCE = {
    'RI': 'RIETI', 'RN': 'RIMINI', 'RM': 'ROMA', 'MI': 'MILANO', 'TO': 'TORINO',
    'NA': 'NAPOLI', 'FI': 'FIRENZE', 'BO': 'BOLOGNA', 'GE': 'GENOVA', 'PA': 'PALERMO',
    'VE': 'VENEZIA', 'VR': 'VERONA', 'PD': 'PADOVA', 'TS': 'TRIESTE', 'BA': 'BARI',
    'CT': 'CATANIA', 'CZ': 'CATANZARO', 'CA': 'CAGLIARI', 'PE': 'PESCARA'
}

def estrai_citta(nome):
    """Estrae città dal nome se presente"""
    nome_upper = nome.upper()
    # Cerca abbreviazioni province alla fine (es. "RI", "- CT")
    for abbrev, citta in ABBREV_PROVINCE.items():
        if nome_upper.endswith(f' {abbrev}') or nome_upper.endswith(f'-{abbrev}') or nome_upper.endswith(f'- {abbrev}'):
            return citta
    # Cerca città per nome
    for citta in CITTA_ITALIANE:
        if citta in nome_upper:
            return citta
    return None

def estrai_numeri(nome):
    """Estrae numeri dal nome (per evitare merge di 'nr. 3' con 'nr. 6')"""
    import re
    numeri = re.findall(r'\d+', nome)
    return tuple(numeri) if numeri else None

# ============================================================================
# NORMALIZZAZIONE NOMI
# ============================================================================
print("\n[2/6] Normalizzazione nomi...")

def normalizza_nome(nome):
    """Normalizza nome per confronto"""
    if pd.isna(nome):
        return ""

    nome = str(nome).upper().strip()

    # Rimuovi suffissi comuni (forma giuridica)
    suffissi = [
        ' - ASD', ' -ASD', ' ASD', ' A.S.D.', ' A.S.D',
        ' - APS', ' -APS', ' APS', ' A.P.S.', ' A.P.S',
        ' - APD', ' -APD', ' APD', ' A.P.D.', ' A.P.D',
        ' ONLUS', ' ODV', ' ETS', ' - SOMS', ' SOMS',
        ' - ', '- '
    ]
    for suff in suffissi:
        if nome.endswith(suff):
            nome = nome[:-len(suff)]

    # Rimuovi spazi extra
    nome = ' '.join(nome.split())

    return nome.strip()

# ============================================================================
# IDENTIFICA DUPLICATI SICURI
# ============================================================================
print("\n[3/6] Identificazione duplicati sicuri...")

# Crea mapping normalizzato -> originali
nome_to_originali = defaultdict(list)
for nome in nomi_originali:
    norm = normalizza_nome(nome)
    nome_to_originali[norm].append(nome)

# Duplicati esatti dopo normalizzazione (questi sono sicuri)
duplicati_sicuri = {}
for norm, originali in nome_to_originali.items():
    if len(originali) > 1:
        # Verifica che abbiano la stessa città (o nessuna città)
        citta = [estrai_citta(o) for o in originali]
        citta_uniche = set([c for c in citta if c])

        if len(citta_uniche) <= 1:  # Stessa città o nessuna
            canonico = max(originali, key=len)
            for orig in originali:
                duplicati_sicuri[orig] = canonico

print(f"   Duplicati sicuri (stessa normalizzazione): {len(duplicati_sicuri)}")

# ============================================================================
# FUZZY MATCHING CONSERVATIVO
# ============================================================================
print("\n[4/6] Fuzzy matching conservativo...")

def similarita(a, b):
    """Calcola similarità tra due stringhe (0-1)"""
    return SequenceMatcher(None, a.upper(), b.upper()).ratio()

def sono_stesso_posto(n1, n2):
    """Verifica se due nomi si riferiscono allo stesso posto"""
    citta1 = estrai_citta(n1)
    citta2 = estrai_citta(n2)

    # Se entrambi hanno città diverse, NON unire
    if citta1 and citta2 and citta1 != citta2:
        return False

    # Se entrambi hanno numeri diversi (es. "nr. 3" vs "nr. 6"), NON unire
    num1 = estrai_numeri(n1)
    num2 = estrai_numeri(n2)
    if num1 and num2 and num1 != num2:
        return False

    return True

# Lista nomi normalizzati unici (escludi già processati)
nomi_processati = set(duplicati_sicuri.keys())
nomi_rimanenti = [n for n in nomi_originali if n not in nomi_processati]

# Soglia alta per sicurezza
SOGLIA_ALTA = 0.92

coppie_unite = []
for i, n1 in enumerate(nomi_rimanenti):
    for n2 in nomi_rimanenti[i+1:]:
        # Skip se città diverse
        if not sono_stesso_posto(n1, n2):
            continue

        # Confronta normalizzati
        norm1 = normalizza_nome(n1)
        norm2 = normalizza_nome(n2)

        # Skip se troppo corti (rischio falsi positivi)
        if len(norm1) < 10 or len(norm2) < 10:
            continue

        sim = similarita(norm1, norm2)
        if sim >= SOGLIA_ALTA:
            coppie_unite.append((n1, n2, sim))

print(f"   Coppie simili trovate (>{SOGLIA_ALTA*100:.0f}%): {len(coppie_unite)}")

# ============================================================================
# CREAZIONE MAPPING FINALE
# ============================================================================
print("\n[5/6] Creazione mapping finale...")

gruppi_uniti = dict(duplicati_sicuri)  # Inizia con duplicati sicuri

# Aggiungi coppie fuzzy
for n1, n2, sim in coppie_unite:
    canonico = max([n1, n2], key=len)
    gruppi_uniti[n1] = canonico
    gruppi_uniti[n2] = canonico

# Per i nomi non in gruppi, mantieni originale
for nome in nomi_originali:
    if nome not in gruppi_uniti:
        gruppi_uniti[nome] = nome

# Conta associazioni uniche dopo pulizia
nomi_canonici = set(gruppi_uniti.values())
print(f"   Associazioni dopo pulizia: {len(nomi_canonici)}")
print(f"   Riduzione: {len(nomi_originali) - len(nomi_canonici)} nomi unificati")

# ============================================================================
# APPLICA MAPPING AI DATI
# ============================================================================
print("\n[6/6] Applicazione mapping...")

# Crea colonna Associazione
df['Associazione'] = df['GrpName'].map(gruppi_uniti).fillna(df['GrpName'])

# Verifica
print(f"   Associazioni uniche nel dataset: {df['Associazione'].nunique()}")

# Salva mapping per riferimento
mapping_df = pd.DataFrame([
    {'NomeOriginale': k, 'NomeUnificato': v, 'Modificato': k != v}
    for k, v in gruppi_uniti.items()
])
mapping_df = mapping_df.sort_values('NomeUnificato')
mapping_df.to_csv(OUTPUT_DIR / 'mapping_associazioni.csv', index=False)

# Salva dati puliti
df.to_csv(OUTPUT_DIR / 'dati_unificati_2017_2025.csv', index=False)

# ============================================================================
# REPORT
# ============================================================================
print(f"\n{'='*80}")
print("PULIZIA COMPLETATA")
print(f"{'='*80}")

# Mostra esempi di unificazioni
modificati = mapping_df[mapping_df['Modificato']]
print(f"\nUnificazioni effettuate ({len(modificati)} totali):")
for _, row in modificati.iterrows():
    if row['NomeOriginale'] != row['NomeUnificato']:
        print(f"   '{row['NomeOriginale']}' -> '{row['NomeUnificato']}'")

print(f"\n{'='*80}")
print(f"FILE AGGIORNATI:")
print(f"   - dati_unificati_2017_2025.csv (colonna 'Associazione' aggiunta)")
print(f"   - mapping_associazioni.csv (riferimento trasformazioni)")
print(f"{'='*80}")
