#!/usr/bin/env python3
"""
Analisi giocatori che fanno tanti campionati ma poche gare totali
Clusterizzazione per CatLabel e età
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import json

print("="*80)
print("ANALISI GIOCATORI: CAMPIONATI vs GARE TOTALI")
print("="*80)

# Caricamento dati
df = pd.read_csv('/home/ubuntu/bridge_analysis/dati_unificati.csv')

print(f"\nDati caricati: {len(df):,} tesseramenti")
print(f"Giocatori unici: {df['MmbCode'].nunique():,}")

# Verifica colonne disponibili
print(f"\nColonne disponibili: {df.columns.tolist()}")

# Calcolo ratio campionati/gare totali
df['Ratio_Campionati'] = df['PuntiCampionati'] / (df['PuntiTotali'] + 1)  # +1 per evitare divisione per zero
df['Pct_Campionati'] = (df['PuntiCampionati'] / (df['PuntiTotali'] + 1) * 100).round(1)

# Filtro giocatori attivi (almeno 10 gare)
df_attivi = df[df['GareGiocate'] >= 10].copy()

print(f"\nGiocatori attivi (≥10 gare): {len(df_attivi):,}")

# Creazione fasce d'età
df_attivi['FasciaEta'] = pd.cut(df_attivi['Anni'], 
                                bins=[0, 30, 40, 50, 60, 70, 80, 90, 120],
                                labels=['<30', '30-40', '40-50', '50-60', '60-70', '70-80', '80-90', '90+'])

# ============================================================================
# PARTE 1: IDENTIFICAZIONE GIOCATORI "SELETTIVI"
# ============================================================================

print("\n" + "="*80)
print("PARTE 1: IDENTIFICAZIONE GIOCATORI SELETTIVI")
print("="*80)

# Definizione: giocatori con alta % punti da campionati
# Soglie:
# - Molto selettivi: >80% punti da campionati
# - Selettivi: 60-80% punti da campionati
# - Bilanciati: 40-60%
# - Orientati gare: 20-40%
# - Solo gare: <20%

df_attivi['Profilo'] = pd.cut(
    df_attivi['Pct_Campionati'],
    bins=[0, 20, 40, 60, 80, 100],
    labels=['Solo Gare (<20%)', 'Orient. Gare (20-40%)', 'Bilanciati (40-60%)', 
            'Selettivi (60-80%)', 'Molto Selettivi (>80%)']
)

profilo_counts = df_attivi['Profilo'].value_counts().sort_index()
print("\nDistribuzione profili giocatori:")
for profilo, count in profilo_counts.items():
    pct = count / len(df_attivi) * 100
    print(f"  {profilo}: {count:,} ({pct:.1f}%)")

# Focus su giocatori selettivi (>60% punti da campionati)
selettivi = df_attivi[df_attivi['Pct_Campionati'] >= 60].copy()

print(f"\n{'='*80}")
print(f"GIOCATORI SELETTIVI (≥60% punti da campionati)")
print(f"{'='*80}")
print(f"Totale: {len(selettivi):,} ({len(selettivi)/len(df_attivi)*100:.1f}% dei giocatori attivi)")

# Statistiche giocatori selettivi
print(f"\nStatistiche giocatori selettivi:")
print(f"  Gare medie: {selettivi['GareGiocate'].mean():.1f}")
print(f"  Gare mediane: {selettivi['GareGiocate'].median():.0f}")
print(f"  Punti totali medi: {selettivi['PuntiTotali'].mean():.0f}")
print(f"  Punti campionati medi: {selettivi['PuntiCampionati'].mean():.0f}")
print(f"  % campionati media: {selettivi['Pct_Campionati'].mean():.1f}%")
print(f"  Età media: {selettivi['Anni'].mean():.1f} anni")

# ============================================================================
# PARTE 2: CLUSTERIZZAZIONE PER CATEGORIA (CatLabel)
# ============================================================================

print("\n" + "="*80)
print("PARTE 2: CLUSTERIZZAZIONE PER CATEGORIA")
print("="*80)

# Analisi per categoria
cluster_cat = selettivi.groupby('CatLabel').agg({
    'MmbCode': 'count',
    'GareGiocate': ['mean', 'median'],
    'PuntiTotali': ['mean', 'median'],
    'PuntiCampionati': ['mean', 'median'],
    'Pct_Campionati': 'mean',
    'Anni': 'mean'
}).round(1)

cluster_cat.columns = ['N_Giocatori', 'Gare_Medie', 'Gare_Mediane', 
                       'Punti_Tot_Medi', 'Punti_Tot_Mediani',
                       'Punti_Camp_Medi', 'Punti_Camp_Mediani',
                       'Pct_Camp_Media', 'Eta_Media']

cluster_cat = cluster_cat.sort_values('N_Giocatori', ascending=False)

print("\nGiocatori selettivi per categoria:")
print(cluster_cat.to_string())

# Top 10 categorie per numerosità
print("\n" + "-"*80)
print("TOP 10 CATEGORIE PER NUMEROSITÀ (giocatori selettivi)")
print("-"*80)

top10_cat = cluster_cat.head(10)
for idx, row in top10_cat.iterrows():
    print(f"\n{idx}:")
    print(f"  N. giocatori: {int(row['N_Giocatori']):,}")
    print(f"  Gare medie: {row['Gare_Medie']:.1f}")
    print(f"  Punti totali medi: {row['Punti_Tot_Medi']:.0f}")
    print(f"  Punti campionati medi: {row['Punti_Camp_Medi']:.0f}")
    print(f"  % campionati: {row['Pct_Camp_Media']:.1f}%")
    print(f"  Età media: {row['Eta_Media']:.1f} anni")

# ============================================================================
# PARTE 3: CLUSTERIZZAZIONE PER ETÀ
# ============================================================================

print("\n" + "="*80)
print("PARTE 3: CLUSTERIZZAZIONE PER ETÀ")
print("="*80)

# Analisi per fascia d'età
cluster_eta = selettivi.groupby('FasciaEta').agg({
    'MmbCode': 'count',
    'GareGiocate': ['mean', 'median'],
    'PuntiTotali': ['mean', 'median'],
    'PuntiCampionati': ['mean', 'median'],
    'Pct_Campionati': 'mean',
    'Anni': 'mean'
}).round(1)

cluster_eta.columns = ['N_Giocatori', 'Gare_Medie', 'Gare_Mediane', 
                       'Punti_Tot_Medi', 'Punti_Tot_Mediani',
                       'Punti_Camp_Medi', 'Punti_Camp_Mediani',
                       'Pct_Camp_Media', 'Eta_Media']

print("\nGiocatori selettivi per fascia d'età:")
print(cluster_eta.to_string())

# Distribuzione % per fascia
print("\n" + "-"*80)
print("DISTRIBUZIONE % GIOCATORI SELETTIVI PER FASCIA D'ETÀ")
print("-"*80)

for fascia in ['<30', '30-40', '40-50', '50-60', '60-70', '70-80', '80-90', '90+']:
    tot_fascia = len(df_attivi[df_attivi['FasciaEta'] == fascia])
    sel_fascia = len(selettivi[selettivi['FasciaEta'] == fascia])
    
    if tot_fascia > 0:
        pct = sel_fascia / tot_fascia * 100
        print(f"  {fascia}: {sel_fascia:,}/{tot_fascia:,} ({pct:.1f}%)")

# ============================================================================
# PARTE 4: INCROCIO CATEGORIA x ETÀ
# ============================================================================

print("\n" + "="*80)
print("PARTE 4: INCROCIO CATEGORIA x ETÀ (TOP 5 CATEGORIE)")
print("="*80)

top5_categories = cluster_cat.head(5).index

for cat in top5_categories:
    sel_cat = selettivi[selettivi['CatLabel'] == cat]
    
    print(f"\n{cat} ({len(sel_cat):,} giocatori selettivi):")
    
    # Distribuzione età
    eta_dist = sel_cat.groupby('FasciaEta').size()
    print(f"  Distribuzione età:")
    for fascia, count in eta_dist.items():
        pct = count / len(sel_cat) * 100
        print(f"    {fascia}: {count:,} ({pct:.1f}%)")
    
    # Statistiche
    print(f"  Gare medie: {sel_cat['GareGiocate'].mean():.1f}")
    print(f"  Punti totali medi: {sel_cat['PuntiTotali'].mean():.0f}")
    print(f"  % campionati: {sel_cat['Pct_Campionati'].mean():.1f}%")

# ============================================================================
# PARTE 5: CONFRONTO SELETTIVI vs NON SELETTIVI
# ============================================================================

print("\n" + "="*80)
print("PARTE 5: CONFRONTO SELETTIVI vs NON SELETTIVI")
print("="*80)

non_selettivi = df_attivi[df_attivi['Pct_Campionati'] < 60]

confronto = pd.DataFrame({
    'Selettivi (≥60%)': [
        len(selettivi),
        selettivi['GareGiocate'].mean(),
        selettivi['PuntiTotali'].mean(),
        selettivi['PuntiCampionati'].mean(),
        selettivi['Pct_Campionati'].mean(),
        selettivi['Anni'].mean()
    ],
    'Non Selettivi (<60%)': [
        len(non_selettivi),
        non_selettivi['GareGiocate'].mean(),
        non_selettivi['PuntiTotali'].mean(),
        non_selettivi['PuntiCampionati'].mean(),
        non_selettivi['Pct_Campionati'].mean(),
        non_selettivi['Anni'].mean()
    ]
}, index=['N. Giocatori', 'Gare Medie', 'Punti Totali Medi', 
          'Punti Campionati Medi', '% Campionati', 'Età Media'])

confronto['Differenza'] = confronto['Selettivi (≥60%)'] - confronto['Non Selettivi (<60%)']
confronto['Diff %'] = (confronto['Differenza'] / confronto['Non Selettivi (<60%)'] * 100).round(1)

print("\n" + confronto.round(1).to_string())

# ============================================================================
# PARTE 6: GIOCATORI "ULTRA-SELETTIVI" (>80% campionati)
# ============================================================================

print("\n" + "="*80)
print("PARTE 6: GIOCATORI ULTRA-SELETTIVI (>80% punti da campionati)")
print("="*80)

ultra_selettivi = df_attivi[df_attivi['Pct_Campionati'] >= 80].copy()

print(f"Totale: {len(ultra_selettivi):,} ({len(ultra_selettivi)/len(df_attivi)*100:.1f}%)")

print(f"\nStatistiche ultra-selettivi:")
print(f"  Gare medie: {ultra_selettivi['GareGiocate'].mean():.1f}")
print(f"  Punti totali medi: {ultra_selettivi['PuntiTotali'].mean():.0f}")
print(f"  % campionati media: {ultra_selettivi['Pct_Campionati'].mean():.1f}%")
print(f"  Età media: {ultra_selettivi['Anni'].mean():.1f} anni")

# Top 5 categorie ultra-selettivi
print("\nTop 5 categorie ultra-selettivi:")
top_ultra = ultra_selettivi['CatLabel'].value_counts().head(5)
for cat, count in top_ultra.items():
    pct = count / len(ultra_selettivi) * 100
    print(f"  {cat}: {count:,} ({pct:.1f}%)")

# Distribuzione età ultra-selettivi
print("\nDistribuzione età ultra-selettivi:")
eta_ultra = ultra_selettivi['FasciaEta'].value_counts().sort_index()
for fascia, count in eta_ultra.items():
    pct = count / len(ultra_selettivi) * 100
    print(f"  {fascia}: {count:,} ({pct:.1f}%)")

# ============================================================================
# SALVATAGGIO RISULTATI
# ============================================================================

print("\n" + "="*80)
print("SALVATAGGIO RISULTATI")
print("="*80)

# Salvataggio CSV
selettivi.to_csv('/home/ubuntu/bridge_analysis/results/giocatori_selettivi.csv', index=False)
print("✓ Salvato: giocatori_selettivi.csv")

cluster_cat.to_csv('/home/ubuntu/bridge_analysis/results/cluster_categoria.csv')
print("✓ Salvato: cluster_categoria.csv")

cluster_eta.to_csv('/home/ubuntu/bridge_analysis/results/cluster_eta.csv')
print("✓ Salvato: cluster_eta.csv")

# Salvataggio JSON summary
summary = {
    'overview': {
        'totale_giocatori_attivi': len(df_attivi),
        'giocatori_selettivi': len(selettivi),
        'pct_selettivi': round(len(selettivi) / len(df_attivi) * 100, 1),
        'giocatori_ultra_selettivi': len(ultra_selettivi),
        'pct_ultra_selettivi': round(len(ultra_selettivi) / len(df_attivi) * 100, 1)
    },
    'statistiche_selettivi': {
        'gare_medie': float(selettivi['GareGiocate'].mean()),
        'punti_totali_medi': float(selettivi['PuntiTotali'].mean()),
        'pct_campionati_media': float(selettivi['Pct_Campionati'].mean()),
        'eta_media': float(selettivi['Anni'].mean())
    },
    'top_5_categorie': cluster_cat.head(5)['N_Giocatori'].to_dict(),
    'distribuzione_eta': cluster_eta['N_Giocatori'].to_dict()
}

with open('/home/ubuntu/bridge_analysis/results/analisi_selettivi_summary.json', 'w') as f:
    json.dump(summary, f, indent=2)
print("✓ Salvato: analisi_selettivi_summary.json")

# ============================================================================
# VISUALIZZAZIONI
# ============================================================================

print("\n" + "="*80)
print("GENERAZIONE VISUALIZZAZIONI")
print("="*80)

fig, axes = plt.subplots(2, 3, figsize=(20, 12))
fig.suptitle('Analisi Giocatori Selettivi: Campionati vs Gare Totali', 
             fontsize=16, fontweight='bold')

# Grafico 1: Distribuzione profili
ax1 = axes[0, 0]
profilo_counts.plot(kind='bar', ax=ax1, color='steelblue', edgecolor='black')
ax1.set_title('Distribuzione Profili Giocatori', fontsize=12, fontweight='bold')
ax1.set_xlabel('Profilo')
ax1.set_ylabel('Numero Giocatori')
ax1.tick_params(axis='x', rotation=45)
ax1.grid(True, alpha=0.3, axis='y')
for i, v in enumerate(profilo_counts.values):
    ax1.text(i, v + 500, f'{v:,}', ha='center', va='bottom', fontweight='bold')

# Grafico 2: Top 10 categorie selettivi
ax2 = axes[0, 1]
top10_cat['N_Giocatori'].plot(kind='barh', ax=ax2, color='coral', edgecolor='black')
ax2.set_title('Top 10 Categorie - Giocatori Selettivi', fontsize=12, fontweight='bold')
ax2.set_xlabel('Numero Giocatori')
ax2.grid(True, alpha=0.3, axis='x')

# Grafico 3: Distribuzione età selettivi
ax3 = axes[0, 2]
cluster_eta['N_Giocatori'].plot(kind='bar', ax=ax3, color='lightgreen', edgecolor='black')
ax3.set_title('Distribuzione Età - Giocatori Selettivi', fontsize=12, fontweight='bold')
ax3.set_xlabel('Fascia d\'Età')
ax3.set_ylabel('Numero Giocatori')
ax3.tick_params(axis='x', rotation=45)
ax3.grid(True, alpha=0.3, axis='y')

# Grafico 4: % selettivi per fascia età
ax4 = axes[1, 0]
pct_sel_per_fascia = []
fasce = ['<30', '30-40', '40-50', '50-60', '60-70', '70-80', '80-90', '90+']
for fascia in fasce:
    tot = len(df_attivi[df_attivi['FasciaEta'] == fascia])
    sel = len(selettivi[selettivi['FasciaEta'] == fascia])
    pct = (sel / tot * 100) if tot > 0 else 0
    pct_sel_per_fascia.append(pct)

ax4.bar(fasce, pct_sel_per_fascia, color='purple', edgecolor='black', alpha=0.7)
ax4.set_title('% Giocatori Selettivi per Fascia d\'Età', fontsize=12, fontweight='bold')
ax4.set_xlabel('Fascia d\'Età')
ax4.set_ylabel('% Selettivi')
ax4.tick_params(axis='x', rotation=45)
ax4.grid(True, alpha=0.3, axis='y')
ax4.axhline(y=len(selettivi)/len(df_attivi)*100, color='red', linestyle='--', 
            linewidth=2, label=f'Media: {len(selettivi)/len(df_attivi)*100:.1f}%')
ax4.legend()

# Grafico 5: Scatter gare vs punti campionati (sample)
ax5 = axes[1, 1]
sample = selettivi.sample(min(1000, len(selettivi)))
scatter = ax5.scatter(sample['GareGiocate'], sample['PuntiCampionati'], 
                     c=sample['Anni'], cmap='viridis', alpha=0.6, s=30)
ax5.set_title('Gare vs Punti Campionati (sample 1000)', fontsize=12, fontweight='bold')
ax5.set_xlabel('Gare Giocate')
ax5.set_ylabel('Punti Campionati')
ax5.grid(True, alpha=0.3)
plt.colorbar(scatter, ax=ax5, label='Età')

# Grafico 6: Confronto selettivi vs non selettivi
ax6 = axes[1, 2]
metriche = ['Gare Medie', 'Punti Totali\nMedi', '% Campionati', 'Età Media']
sel_vals = [
    selettivi['GareGiocate'].mean(),
    selettivi['PuntiTotali'].mean() / 100,  # Scala per visualizzazione
    selettivi['Pct_Campionati'].mean(),
    selettivi['Anni'].mean()
]
non_sel_vals = [
    non_selettivi['GareGiocate'].mean(),
    non_selettivi['PuntiTotali'].mean() / 100,
    non_selettivi['Pct_Campionati'].mean(),
    non_selettivi['Anni'].mean()
]

x = np.arange(len(metriche))
width = 0.35

ax6.bar(x - width/2, sel_vals, width, label='Selettivi', color='coral', edgecolor='black')
ax6.bar(x + width/2, non_sel_vals, width, label='Non Selettivi', color='steelblue', edgecolor='black')
ax6.set_title('Confronto Selettivi vs Non Selettivi', fontsize=12, fontweight='bold')
ax6.set_ylabel('Valore (Punti/100)')
ax6.set_xticks(x)
ax6.set_xticklabels(metriche, fontsize=9)
ax6.legend()
ax6.grid(True, alpha=0.3, axis='y')

plt.tight_layout()
plt.savefig('/home/ubuntu/bridge_analysis/results/analisi_giocatori_selettivi.png', 
            dpi=300, bbox_inches='tight')
print("✓ Salvato: analisi_giocatori_selettivi.png")

print("\n" + "="*80)
print("ANALISI COMPLETATA!")
print("="*80)
