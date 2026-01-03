#!/usr/bin/env python3
"""
Aggiornamento analisi conversione con nomi circoli invece di codici
"""

import pandas as pd
import json

print("="*80)
print("AGGIORNAMENTO ANALISI CON NOMI CIRCOLI")
print("="*80)

# Caricamento dati
df = pd.read_csv('/home/ubuntu/bridge_analysis/dati_unificati.csv')
scuola = df[df['MbtDesc'] == 'Scuola Bridge'].copy()

# Creazione mapping codice → nome
circolo_mapping = df[['MmbGroup', 'GrpName', 'GrpArea']].drop_duplicates()
circolo_mapping = circolo_mapping.set_index('MmbGroup')

# Caricamento analisi precedente
df_conversioni = pd.read_csv('/home/ubuntu/bridge_analysis/results/conversione_per_circolo.csv')

# Aggiunta nomi circoli
df_conversioni['Nome_Circolo'] = df_conversioni['Circolo'].map(
    lambda x: circolo_mapping.loc[x, 'GrpName'] if x in circolo_mapping.index else x
)

# Riordino colonne
cols = ['Circolo', 'Nome_Circolo', 'Regione', 'N_Corsisti', 'N_Convertiti', 
        'Tasso_Conversione_%', 'Eta_Media_Corsisti', 'Gare_Medie_Corsisti', 
        'Destinazioni', 'Categoria']
df_conversioni = df_conversioni[cols]

# Salvataggio
df_conversioni.to_csv('/home/ubuntu/bridge_analysis/results/conversione_per_circolo_con_nomi.csv', index=False)
print("✓ Salvato: conversione_per_circolo_con_nomi.csv")

# Stampa Top 20 con nomi
print("\n" + "="*80)
print("TOP 20 CIRCOLI PER CONVERSIONE (CON NOMI)")
print("="*80)

top20 = df_conversioni.head(20)
for idx, row in top20.iterrows():
    print(f"\n{idx+1}. {row['Nome_Circolo']}")
    print(f"   Codice: {row['Circolo']} | Regione: {row['Regione']}")
    print(f"   Corsisti: {row['N_Corsisti']} | Convertiti: {row['N_Convertiti']} | Conversione: {row['Tasso_Conversione_%']}%")
    print(f"   Età media: {row['Eta_Media_Corsisti']} anni | Gare medie: {row['Gare_Medie_Corsisti']}")

# Stampa Bottom 20 con nomi
print("\n" + "="*80)
print("BOTTOM 20 CIRCOLI PER CONVERSIONE (CON NOMI)")
print("="*80)

bottom20 = df_conversioni.tail(20)
for idx, row in bottom20.iterrows():
    print(f"\n{len(df_conversioni)-19+list(bottom20.index).index(idx)}. {row['Nome_Circolo']}")
    print(f"   Codice: {row['Circolo']} | Regione: {row['Regione']}")
    print(f"   Corsisti: {row['N_Corsisti']} | Convertiti: {row['N_Convertiti']} | Conversione: {row['Tasso_Conversione_%']}%")
    print(f"   Età media: {row['Eta_Media_Corsisti']} anni | Gare medie: {row['Gare_Medie_Corsisti']}")

# Creazione JSON summary con nomi
summary = {
    'top_20_circoli': [],
    'bottom_20_circoli': [],
    'statistiche_aggregate': {
        'n_circoli': len(df_conversioni),
        'conversione_media': float(df_conversioni['Tasso_Conversione_%'].mean()),
        'conversione_mediana': float(df_conversioni['Tasso_Conversione_%'].median()),
        'deviazione_standard': float(df_conversioni['Tasso_Conversione_%'].std())
    }
}

for idx, row in top20.iterrows():
    summary['top_20_circoli'].append({
        'posizione': idx + 1,
        'codice': row['Circolo'],
        'nome': row['Nome_Circolo'],
        'regione': row['Regione'],
        'corsisti': int(row['N_Corsisti']),
        'convertiti': int(row['N_Convertiti']),
        'conversione_pct': float(row['Tasso_Conversione_%']),
        'eta_media': float(row['Eta_Media_Corsisti']),
        'gare_medie': float(row['Gare_Medie_Corsisti'])
    })

for idx, row in bottom20.iterrows():
    summary['bottom_20_circoli'].append({
        'posizione': len(df_conversioni) - 19 + list(bottom20.index).index(idx),
        'codice': row['Circolo'],
        'nome': row['Nome_Circolo'],
        'regione': row['Regione'],
        'corsisti': int(row['N_Corsisti']),
        'convertiti': int(row['N_Convertiti']),
        'conversione_pct': float(row['Tasso_Conversione_%']),
        'eta_media': float(row['Eta_Media_Corsisti']),
        'gare_medie': float(row['Gare_Medie_Corsisti'])
    })

with open('/home/ubuntu/bridge_analysis/results/circoli_con_nomi_summary.json', 'w', encoding='utf-8') as f:
    json.dump(summary, f, indent=2, ensure_ascii=False)

print("\n✓ Salvato: circoli_con_nomi_summary.json")
print("\n" + "="*80)
print("COMPLETATO!")
print("="*80)
