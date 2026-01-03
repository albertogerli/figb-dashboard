#!/usr/bin/env python3
"""
Analisi giocatori attivi che non si ritesserano l'anno dopo
Stratificazione per regione ed età
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import json

print("="*80)
print("ANALISI CHURN GIOCATORI ATTIVI")
print("="*80)

# Caricamento dati
df = pd.read_csv('/home/ubuntu/bridge_analysis/dati_unificati.csv')

print(f"\nDati caricati: {len(df):,} tesseramenti")
print(f"Giocatori unici: {df['MmbCode'].nunique():,}")
print(f"Anni: {sorted(df['Anno'].unique())}")

# ============================================================================
# PARTE 1: IDENTIFICAZIONE GIOCATORI ATTIVI E CHURN
# ============================================================================

print("\n" + "="*80)
print("PARTE 1: IDENTIFICAZIONE GIOCATORI ATTIVI E CHURN")
print("="*80)

# Definizione "attivo": almeno 10 gare nell'anno
df['Attivo'] = df['GareGiocate'] >= 10

# Per ogni giocatore/anno, verificare se si ritessera l'anno dopo
df_sorted = df.sort_values(['MmbCode', 'Anno'])

# Creare colonna con anno successivo
df_sorted['Anno_Next'] = df_sorted['Anno'] + 1

# Merge per vedere se esiste tesseramento anno dopo
df_with_next = df_sorted.merge(
    df_sorted[['MmbCode', 'Anno']].rename(columns={'Anno': 'Anno_Presente'}),
    left_on=['MmbCode', 'Anno_Next'],
    right_on=['MmbCode', 'Anno_Presente'],
    how='left',
    indicator=True
)

# Ritesserato = True se esiste tesseramento anno dopo
df_with_next['Ritesserato'] = df_with_next['_merge'] == 'both'

# Focus su giocatori attivi (≥10 gare)
df_attivi = df_with_next[df_with_next['Attivo']].copy()

# Escludere 2024 (non possiamo sapere se si ritesserano nel 2025)
df_attivi = df_attivi[df_attivi['Anno'] < 2024].copy()

print(f"\nGiocatori attivi analizzati (2017-2023): {len(df_attivi):,}")

# Calcolo churn
n_ritesserati = df_attivi['Ritesserato'].sum()
n_non_ritesserati = (~df_attivi['Ritesserato']).sum()
retention_rate = n_ritesserati / len(df_attivi) * 100
churn_rate = n_non_ritesserati / len(df_attivi) * 100

print(f"\nRisultati globali:")
print(f"  Ritesserati: {n_ritesserati:,} ({retention_rate:.1f}%)")
print(f"  Non ritesserati (CHURN): {n_non_ritesserati:,} ({churn_rate:.1f}%)")

# ============================================================================
# PARTE 2: CHURN PER ANNO
# ============================================================================

print("\n" + "="*80)
print("PARTE 2: CHURN PER ANNO")
print("="*80)

churn_per_anno = df_attivi.groupby('Anno').agg({
    'MmbCode': 'count',
    'Ritesserato': lambda x: x.sum()
}).rename(columns={'MmbCode': 'Attivi', 'Ritesserato': 'Ritesserati'})

churn_per_anno['Non_Ritesserati'] = churn_per_anno['Attivi'] - churn_per_anno['Ritesserati']
churn_per_anno['Retention_%'] = (churn_per_anno['Ritesserati'] / churn_per_anno['Attivi'] * 100).round(1)
churn_per_anno['Churn_%'] = (churn_per_anno['Non_Ritesserati'] / churn_per_anno['Attivi'] * 100).round(1)

print("\nChurn per anno:")
print(churn_per_anno.to_string())

# ============================================================================
# PARTE 3: CHURN PER REGIONE
# ============================================================================

print("\n" + "="*80)
print("PARTE 3: CHURN PER REGIONE")
print("="*80)

churn_per_regione = df_attivi.groupby('GrpArea').agg({
    'MmbCode': 'count',
    'Ritesserato': lambda x: x.sum(),
    'Anni': 'mean',
    'GareGiocate': 'mean'
}).rename(columns={'MmbCode': 'Attivi', 'Ritesserato': 'Ritesserati', 'Anni': 'Eta_Media', 'GareGiocate': 'Gare_Medie'})

churn_per_regione['Non_Ritesserati'] = churn_per_regione['Attivi'] - churn_per_regione['Ritesserati']
churn_per_regione['Retention_%'] = (churn_per_regione['Ritesserati'] / churn_per_regione['Attivi'] * 100).round(1)
churn_per_regione['Churn_%'] = (churn_per_regione['Non_Ritesserati'] / churn_per_regione['Attivi'] * 100).round(1)

churn_per_regione = churn_per_regione.sort_values('Churn_%', ascending=False)

print("\nChurn per regione (ordinato per churn decrescente):")
print(churn_per_regione.round(1).to_string())

# Top 10 regioni per churn
print("\n" + "-"*80)
print("TOP 10 REGIONI PER CHURN (peggiori)")
print("-"*80)

top10_churn = churn_per_regione.head(10)
for idx, row in top10_churn.iterrows():
    print(f"\n{idx}:")
    print(f"  Attivi: {int(row['Attivi']):,}")
    print(f"  Non ritesserati: {int(row['Non_Ritesserati']):,}")
    print(f"  Churn: {row['Churn_%']:.1f}%")
    print(f"  Età media: {row['Eta_Media']:.1f} anni")
    print(f"  Gare medie: {row['Gare_Medie']:.1f}")

# Bottom 10 regioni per churn (migliori retention)
print("\n" + "-"*80)
print("BOTTOM 10 REGIONI PER CHURN (migliori retention)")
print("-"*80)

bottom10_churn = churn_per_regione.tail(10)
for idx, row in bottom10_churn.iterrows():
    print(f"\n{idx}:")
    print(f"  Attivi: {int(row['Attivi']):,}")
    print(f"  Non ritesserati: {int(row['Non_Ritesserati']):,}")
    print(f"  Churn: {row['Churn_%']:.1f}%")
    print(f"  Retention: {row['Retention_%']:.1f}%")
    print(f"  Età media: {row['Eta_Media']:.1f} anni")
    print(f"  Gare medie: {row['Gare_Medie']:.1f}")

# ============================================================================
# PARTE 4: CHURN PER FASCIA D'ETÀ
# ============================================================================

print("\n" + "="*80)
print("PARTE 4: CHURN PER FASCIA D'ETÀ")
print("="*80)

# Creazione fasce d'età
df_attivi['FasciaEta'] = pd.cut(df_attivi['Anni'], 
                                bins=[0, 18, 30, 40, 50, 60, 70, 80, 90, 120],
                                labels=['<18', '18-30', '30-40', '40-50', '50-60', '60-70', '70-80', '80-90', '90+'])

churn_per_eta = df_attivi.groupby('FasciaEta').agg({
    'MmbCode': 'count',
    'Ritesserato': lambda x: x.sum(),
    'GareGiocate': 'mean'
}).rename(columns={'MmbCode': 'Attivi', 'Ritesserato': 'Ritesserati', 'GareGiocate': 'Gare_Medie'})

churn_per_eta['Non_Ritesserati'] = churn_per_eta['Attivi'] - churn_per_eta['Ritesserati']
churn_per_eta['Retention_%'] = (churn_per_eta['Ritesserati'] / churn_per_eta['Attivi'] * 100).round(1)
churn_per_eta['Churn_%'] = (churn_per_eta['Non_Ritesserati'] / churn_per_eta['Attivi'] * 100).round(1)

print("\nChurn per fascia d'età:")
print(churn_per_eta.round(1).to_string())

# Analisi dettagliata per fascia
print("\n" + "-"*80)
print("ANALISI DETTAGLIATA PER FASCIA D'ETÀ")
print("-"*80)

for fascia in ['<18', '18-30', '30-40', '40-50', '50-60', '60-70', '70-80', '80-90', '90+']:
    if fascia in churn_per_eta.index:
        row = churn_per_eta.loc[fascia]
        print(f"\n{fascia}:")
        print(f"  Attivi: {int(row['Attivi']):,}")
        print(f"  Non ritesserati: {int(row['Non_Ritesserati']):,}")
        print(f"  Churn: {row['Churn_%']:.1f}%")
        print(f"  Retention: {row['Retention_%']:.1f}%")
        print(f"  Gare medie: {row['Gare_Medie']:.1f}")

# ============================================================================
# PARTE 5: INCROCIO REGIONE x ETÀ
# ============================================================================

print("\n" + "="*80)
print("PARTE 5: INCROCIO REGIONE x ETÀ (TOP 10 REGIONI)")
print("="*80)

# Top 10 regioni per numerosità
top_regioni = churn_per_regione.nlargest(10, 'Attivi').index

for regione in top_regioni:
    df_reg = df_attivi[df_attivi['GrpArea'] == regione]
    
    print(f"\n{regione} ({len(df_reg):,} attivi):")
    
    # Churn per fascia età
    churn_eta_reg = df_reg.groupby('FasciaEta').agg({
        'MmbCode': 'count',
        'Ritesserato': lambda x: x.sum()
    }).rename(columns={'MmbCode': 'Attivi', 'Ritesserato': 'Ritesserati'})
    
    churn_eta_reg['Churn_%'] = ((churn_eta_reg['Attivi'] - churn_eta_reg['Ritesserati']) / churn_eta_reg['Attivi'] * 100).round(1)
    
    print("  Churn per fascia età:")
    for fascia in churn_eta_reg.index:
        row = churn_eta_reg.loc[fascia]
        print(f"    {fascia}: {int(row['Attivi'])} attivi, churn {row['Churn_%']:.1f}%")

# ============================================================================
# PARTE 6: CARATTERISTICHE GIOCATORI CHE ABBANDONANO
# ============================================================================

print("\n" + "="*80)
print("PARTE 6: CARATTERISTICHE GIOCATORI CHE ABBANDONANO")
print("="*80)

churned = df_attivi[~df_attivi['Ritesserato']].copy()
retained = df_attivi[df_attivi['Ritesserato']].copy()

print(f"\nGiocatori che abbandonano: {len(churned):,}")
print(f"Giocatori che rimangono: {len(retained):,}")

# Confronto caratteristiche
confronto = pd.DataFrame({
    'Churned': [
        len(churned),
        churned['Anni'].mean(),
        churned['GareGiocate'].mean(),
        churned['PuntiTotali'].mean(),
        churned['PuntiCampionati'].mean(),
        (churned['MbtDesc'] == 'Scuola Bridge').sum() / len(churned) * 100
    ],
    'Retained': [
        len(retained),
        retained['Anni'].mean(),
        retained['GareGiocate'].mean(),
        retained['PuntiTotali'].mean(),
        retained['PuntiCampionati'].mean(),
        (retained['MbtDesc'] == 'Scuola Bridge').sum() / len(retained) * 100
    ]
}, index=['N. Giocatori', 'Età Media', 'Gare Medie', 'Punti Totali Medi', 
          'Punti Campionati Medi', '% Scuola Bridge'])

confronto['Differenza'] = confronto['Churned'] - confronto['Retained']
confronto['Diff_%'] = (confronto['Differenza'] / confronto['Retained'] * 100).round(1)

print("\nConfronto Churned vs Retained:")
print(confronto.round(1).to_string())

# Top 5 categorie tra churned
print("\n" + "-"*80)
print("TOP 5 CATEGORIE TRA GIOCATORI CHE ABBANDONANO")
print("-"*80)

top_cat_churned = churned['CatLabel'].value_counts().head(5)
for cat, count in top_cat_churned.items():
    pct = count / len(churned) * 100
    print(f"  {cat}: {count:,} ({pct:.1f}%)")

# Top 5 tessere tra churned
print("\n" + "-"*80)
print("TOP 5 TESSERE TRA GIOCATORI CHE ABBANDONANO")
print("-"*80)

top_tess_churned = churned['MbtDesc'].value_counts().head(5)
for tess, count in top_tess_churned.items():
    pct = count / len(churned) * 100
    print(f"  {tess}: {count:,} ({pct:.1f}%)")

# ============================================================================
# SALVATAGGIO RISULTATI
# ============================================================================

print("\n" + "="*80)
print("SALVATAGGIO RISULTATI")
print("="*80)

# Salvataggio CSV
churned.to_csv('/home/ubuntu/bridge_analysis/results/giocatori_churned.csv', index=False)
print("✓ Salvato: giocatori_churned.csv")

churn_per_anno.to_csv('/home/ubuntu/bridge_analysis/results/churn_per_anno.csv')
print("✓ Salvato: churn_per_anno.csv")

churn_per_regione.to_csv('/home/ubuntu/bridge_analysis/results/churn_per_regione.csv')
print("✓ Salvato: churn_per_regione.csv")

churn_per_eta.to_csv('/home/ubuntu/bridge_analysis/results/churn_per_eta.csv')
print("✓ Salvato: churn_per_eta.csv")

# Salvataggio JSON summary
summary = {
    'overview': {
        'totale_attivi_analizzati': len(df_attivi),
        'ritesserati': int(n_ritesserati),
        'non_ritesserati': int(n_non_ritesserati),
        'retention_rate': float(retention_rate),
        'churn_rate': float(churn_rate)
    },
    'churn_per_anno': churn_per_anno['Churn_%'].to_dict(),
    'top_5_regioni_churn': churn_per_regione.head(5)['Churn_%'].to_dict(),
    'churn_per_fascia_eta': churn_per_eta['Churn_%'].to_dict()
}

with open('/home/ubuntu/bridge_analysis/results/analisi_churn_summary.json', 'w') as f:
    json.dump(summary, f, indent=2)
print("✓ Salvato: analisi_churn_summary.json")

# ============================================================================
# VISUALIZZAZIONI
# ============================================================================

print("\n" + "="*80)
print("GENERAZIONE VISUALIZZAZIONI")
print("="*80)

fig, axes = plt.subplots(2, 3, figsize=(20, 12))
fig.suptitle('Analisi Churn Giocatori Attivi', fontsize=16, fontweight='bold')

# Grafico 1: Churn per anno
ax1 = axes[0, 0]
churn_per_anno['Churn_%'].plot(kind='bar', ax=ax1, color='crimson', edgecolor='black')
ax1.set_title('Churn Rate per Anno', fontsize=12, fontweight='bold')
ax1.set_xlabel('Anno')
ax1.set_ylabel('Churn %')
ax1.tick_params(axis='x', rotation=45)
ax1.grid(True, alpha=0.3, axis='y')
ax1.axhline(y=churn_rate, color='blue', linestyle='--', linewidth=2, label=f'Media: {churn_rate:.1f}%')
ax1.legend()

# Grafico 2: Top 10 regioni per churn
ax2 = axes[0, 1]
top10_churn['Churn_%'].plot(kind='barh', ax=ax2, color='orangered', edgecolor='black')
ax2.set_title('Top 10 Regioni per Churn', fontsize=12, fontweight='bold')
ax2.set_xlabel('Churn %')
ax2.grid(True, alpha=0.3, axis='x')

# Grafico 3: Churn per fascia età
ax3 = axes[0, 2]
churn_per_eta['Churn_%'].plot(kind='bar', ax=ax3, color='darkred', edgecolor='black')
ax3.set_title('Churn per Fascia d\'Età', fontsize=12, fontweight='bold')
ax3.set_xlabel('Fascia d\'Età')
ax3.set_ylabel('Churn %')
ax3.tick_params(axis='x', rotation=45)
ax3.grid(True, alpha=0.3, axis='y')

# Grafico 4: Retention per fascia età
ax4 = axes[1, 0]
churn_per_eta['Retention_%'].plot(kind='bar', ax=ax4, color='forestgreen', edgecolor='black')
ax4.set_title('Retention Rate per Fascia d\'Età', fontsize=12, fontweight='bold')
ax4.set_xlabel('Fascia d\'Età')
ax4.set_ylabel('Retention %')
ax4.tick_params(axis='x', rotation=45)
ax4.grid(True, alpha=0.3, axis='y')

# Grafico 5: Scatter età vs gare (churned vs retained)
ax5 = axes[1, 1]
sample_churned = churned.sample(min(1000, len(churned)))
sample_retained = retained.sample(min(1000, len(retained)))
ax5.scatter(sample_churned['Anni'], sample_churned['GareGiocate'], 
           c='red', alpha=0.3, s=20, label='Churned')
ax5.scatter(sample_retained['Anni'], sample_retained['GareGiocate'], 
           c='green', alpha=0.3, s=20, label='Retained')
ax5.set_title('Età vs Gare: Churned vs Retained (sample)', fontsize=12, fontweight='bold')
ax5.set_xlabel('Età')
ax5.set_ylabel('Gare Giocate')
ax5.legend()
ax5.grid(True, alpha=0.3)

# Grafico 6: Confronto caratteristiche churned vs retained
ax6 = axes[1, 2]
metriche = ['Età Media', 'Gare Medie', 'Punti Tot\n(x100)', '% Scuola\nBridge']
churned_vals = [
    churned['Anni'].mean(),
    churned['GareGiocate'].mean(),
    churned['PuntiTotali'].mean() / 100,
    (churned['MbtDesc'] == 'Scuola Bridge').sum() / len(churned) * 100
]
retained_vals = [
    retained['Anni'].mean(),
    retained['GareGiocate'].mean(),
    retained['PuntiTotali'].mean() / 100,
    (retained['MbtDesc'] == 'Scuola Bridge').sum() / len(retained) * 100
]

x = np.arange(len(metriche))
width = 0.35

ax6.bar(x - width/2, churned_vals, width, label='Churned', color='crimson', edgecolor='black')
ax6.bar(x + width/2, retained_vals, width, label='Retained', color='forestgreen', edgecolor='black')
ax6.set_title('Confronto Churned vs Retained', fontsize=12, fontweight='bold')
ax6.set_ylabel('Valore')
ax6.set_xticks(x)
ax6.set_xticklabels(metriche, fontsize=9)
ax6.legend()
ax6.grid(True, alpha=0.3, axis='y')

plt.tight_layout()
plt.savefig('/home/ubuntu/bridge_analysis/results/analisi_churn_attivi.png', 
            dpi=300, bbox_inches='tight')
print("✓ Salvato: analisi_churn_attivi.png")

print("\n" + "="*80)
print("ANALISI COMPLETATA!")
print("="*80)
