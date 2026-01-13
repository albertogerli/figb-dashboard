#!/usr/bin/env python3
"""
FUZZY MATCHING ASSOCIAZIONI
===========================

Script per identificare e unificare nomi di associazioni duplicati
usando tecniche di fuzzy matching e normalizzazione.
"""

import pandas as pd
import numpy as np
import re
from pathlib import Path
from collections import defaultdict
from difflib import SequenceMatcher
import warnings
warnings.filterwarnings('ignore')

# Paths
BASE_DIR = Path(__file__).parent
OUTPUT_DIR = BASE_DIR / 'output'

# =============================================================================
# REGOLE DI NORMALIZZAZIONE
# =============================================================================

# Parole da rimuovere o standardizzare
STOPWORDS = [
    'A.S.D.', 'ASD', 'A.S.D', 'S.S.D.', 'SSD', 'A R.L.', 'A.R.L.', 'ARL',
    'S.R.L.', 'SRL', 'A.P.D.', 'APD', 'A.P.S.D.', 'APSD', 'A.C.S.D.', 'ACSD',
    'CIRCOLO', 'C.LO', 'CLO', 'CLUB', 'ASSOCIAZIONE', 'ASS.', 'ASSOC.',
    'SPORTIVA', 'SPORT.', 'DILETTANTISTICA', 'DILETT.',
    'BRIDGE', 'BR.', 'BR', 'BRIDGE CLUB',
]

# Abbreviazioni comuni da espandere
ABBREVIAZIONI = {
    'C.LO': 'CIRCOLO',
    'CLO': 'CIRCOLO',
    'BR.': 'BRIDGE',
    'BR': 'BRIDGE',
    'ASS.': 'ASSOCIAZIONE',
    'ASSOC.': 'ASSOCIAZIONE',
    'S.': 'SAN',
    'SS.': 'SANTI',
    'SPORT.': 'SPORTIVA',
    'DILETT.': 'DILETTANTISTICA',
    'RM': 'ROMA',
    'MI': 'MILANO',
    'TO': 'TORINO',
    'NA': 'NAPOLI',
    'BO': 'BOLOGNA',
    'FI': 'FIRENZE',
    'GE': 'GENOVA',
    'VE': 'VENEZIA',
    'PD': 'PADOVA',
    'BA': 'BARI',
    'PA': 'PALERMO',
    'CT': 'CATANIA',
    'CA': 'CAGLIARI',
    'TS': 'TRIESTE',
    'PG': 'PERUGIA',
    'AN': 'ANCONA',
    'RI': 'RIETI',
    'SR': 'SIRACUSA',
}

# Mapping manuale per casi noti
MAPPING_MANUALE = {
    'A.B.SAN GIORGIO DEL SANNIO': 'BRIDGE SAN GIORGIO DEL SANNIO',
    'A.B.S.GIORGIO SANNIO': 'BRIDGE SAN GIORGIO DEL SANNIO',
    'ANKON BRIDGE': 'ANKON BRIDGE ANCONA',
    'ANKON BRIDGE – RIVIERA DEL CONERO': 'ANKON BRIDGE ANCONA',
    'A.S.D.ALESSANDRIA BRIDGE': 'ALESSANDRIA BRIDGE',
    'ALESSANDRIA BRIDGE A.S.D.': 'ALESSANDRIA BRIDGE',
    'ASD C.LO CITTADINO FROSINONE': 'CIRCOLO CITTADINO FROSINONE',
    'ASD CIRCOLO CITTADINO FROSINONE': 'CIRCOLO CITTADINO FROSINONE',
    'A.BRIDGE CIRCOLO 1871': 'CIRCOLO 1871 CATANZARO',
    'A.BR.CIRCOLO 1871 CATANZARO': 'CIRCOLO 1871 CATANZARO',
    'ALPI APUANE': 'ALPI APUANE BRIDGE',
    'ALPI APUANE CASTELLO DI SAN GIORGIO': 'ALPI APUANE BRIDGE',
}


def normalize_name(name):
    """
    Normalizza il nome di un'associazione per il confronto.
    """
    if pd.isna(name):
        return ''

    # Uppercase
    s = str(name).upper().strip()

    # Rimuovi caratteri speciali mantenendo spazi
    s = re.sub(r'[–—]', ' ', s)  # Trattini lunghi -> spazio
    s = re.sub(r'[^\w\s]', ' ', s)  # Rimuovi punteggiatura
    s = re.sub(r'\s+', ' ', s).strip()  # Spazi multipli

    # Espandi abbreviazioni
    words = s.split()
    expanded = []
    for w in words:
        if w in ABBREVIAZIONI:
            expanded.append(ABBREVIAZIONI[w])
        else:
            expanded.append(w)
    s = ' '.join(expanded)

    # Rimuovi stopwords per confronto
    for sw in ['ASD', 'SSD', 'ARL', 'SRL', 'APD', 'APSD', 'ACSD',
               'ASSOCIAZIONE', 'CIRCOLO', 'CLUB', 'SPORTIVA', 'DILETTANTISTICA']:
        s = re.sub(rf'\b{sw}\b', '', s)

    s = re.sub(r'\s+', ' ', s).strip()

    return s


def similarity_ratio(s1, s2):
    """Calcola similarità tra due stringhe (0-1)"""
    return SequenceMatcher(None, s1, s2).ratio()


def find_similar_names(names, threshold=0.85):
    """
    Trova gruppi di nomi simili.
    Restituisce un dizionario {nome_canonico: [lista_varianti]}
    """
    # Normalizza tutti i nomi
    normalized = {name: normalize_name(name) for name in names}

    # Trova gruppi di nomi simili
    groups = defaultdict(set)
    processed = set()

    for name1, norm1 in normalized.items():
        if name1 in processed or not norm1:
            continue

        # Questo nome diventa il candidato canonico del gruppo
        current_group = {name1}

        for name2, norm2 in normalized.items():
            if name2 == name1 or name2 in processed or not norm2:
                continue

            # Controlla similarità
            sim = similarity_ratio(norm1, norm2)
            if sim >= threshold:
                current_group.add(name2)

        # Se il gruppo ha più di un nome, salvalo
        if len(current_group) > 1:
            # Scegli il nome canonico (il più lungo o quello senza abbreviazioni)
            canonical = max(current_group, key=lambda x: (len(x), x.count('CIRCOLO'), x.count('BRIDGE')))
            groups[canonical] = current_group
            processed.update(current_group)

    return groups


def create_mapping(df, col='Associazione'):
    """
    Crea un mapping completo nome_originale -> nome_canonico
    """
    # Ottieni nomi unici
    names = df[col].dropna().unique().tolist()
    print(f"   Nomi unici da analizzare: {len(names)}")

    # Applica mapping manuale prima
    mapping = {}
    for name in names:
        name_upper = str(name).upper().strip()
        if name_upper in MAPPING_MANUALE:
            mapping[name] = MAPPING_MANUALE[name_upper]

    # Trova gruppi simili
    remaining_names = [n for n in names if n not in mapping]
    similar_groups = find_similar_names(remaining_names, threshold=0.80)

    print(f"   Gruppi di duplicati trovati: {len(similar_groups)}")

    # Crea mapping per i gruppi trovati
    for canonical, variants in similar_groups.items():
        for variant in variants:
            if variant != canonical:
                mapping[variant] = canonical

    return mapping, similar_groups


def main():
    print("=" * 70)
    print("FUZZY MATCHING ASSOCIAZIONI")
    print("=" * 70)

    # Carica dati
    print("\n📂 Caricamento dati...")
    df = pd.read_csv(OUTPUT_DIR / 'dati_unificati_2017_2025.csv')
    print(f"   Record totali: {len(df):,}")

    # Determina colonna associazioni
    col = 'Associazione' if 'Associazione' in df.columns else 'GrpName'
    print(f"   Colonna associazioni: {col}")
    print(f"   Associazioni uniche PRIMA: {df[col].nunique()}")

    # Crea mapping
    print("\n🔍 Analisi duplicati...")
    mapping, groups = create_mapping(df, col)

    # Mostra duplicati trovati
    print("\n📋 DUPLICATI TROVATI:")
    for canonical, variants in sorted(groups.items(), key=lambda x: len(x[1]), reverse=True)[:30]:
        if len(variants) > 1:
            print(f"\n   ✓ {canonical}")
            for v in sorted(variants):
                if v != canonical:
                    print(f"      ← {v}")

    # Applica mapping
    print("\n🔄 Applicazione correzioni...")
    df['AssociazioneNorm'] = df[col].map(lambda x: mapping.get(x, x))

    print(f"   Associazioni uniche DOPO: {df['AssociazioneNorm'].nunique()}")
    print(f"   Duplicati corretti: {df[col].nunique() - df['AssociazioneNorm'].nunique()}")

    # Salva dati corretti
    print("\n💾 Salvataggio...")

    # Sostituisci la colonna originale
    df[col] = df['AssociazioneNorm']
    df = df.drop(columns=['AssociazioneNorm'])

    df.to_csv(OUTPUT_DIR / 'dati_unificati_2017_2025.csv', index=False)
    print(f"   ✓ Salvato dati_unificati_2017_2025.csv")

    # Salva mapping per riferimento
    mapping_df = pd.DataFrame([
        {'Originale': k, 'Normalizzato': v}
        for k, v in mapping.items()
    ])
    mapping_df.to_csv(OUTPUT_DIR / 'mapping_associazioni.csv', index=False)
    print(f"   ✓ Salvato mapping_associazioni.csv ({len(mapping_df)} correzioni)")

    # Riepilogo
    print("\n" + "=" * 70)
    print("RIEPILOGO")
    print("=" * 70)
    print(f"""
    📊 ASSOCIAZIONI:
       • Prima: {len(mapping) + df[col].nunique()} nomi unici
       • Dopo:  {df[col].nunique()} nomi unici
       • Duplicati corretti: {len(mapping)}

    ✅ Dati puliti salvati!
    """)


if __name__ == '__main__':
    main()
