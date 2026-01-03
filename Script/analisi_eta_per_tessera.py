#!/usr/bin/env python3
"""
Analisi Età per Tipologia di Tessera
Statistiche dettagliate età per ogni tipo di tessera
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import json

print("="*80)
print("ANALISI ETÀ PER TIPOLOGIA DI TESSERA")
print("="*80)

# Caricamento dati
df = pd.read_csv('/home/ubuntu/bridge_analysis/dati_unificati.csv')

print(f"\nDati caricati: {len(df):,} tesseramenti")
print(f"Anni analizzati: {df['Anno'].min()}-{df['Anno'].max()}")

# Focus su dati 2024 per analisi corrente
df_2024 = df[df['Anno'] == 2024].copy()

print(f"\nTesseramenti 2024: {len(df_2024):,}")
print(f"Tipologie tessera: {df_2024['MbtDesc'].nunique()}")

# ============================================================================
# PARTE 1: STATISTICHE ETÀ PER TESSERA (2024)
# ============================================================================

print("\n" + "="*80)
print("PARTE 1: STATISTICHE ETÀ PER TESSERA (2024)")
print("="*80)

# Statistiche per tessera
stats_tessera = df_2024.groupby('MbtDesc').agg({
    'MmbCode': 'count',
    'Anni': ['mean', 'median', 'std', 'min', 'max'],
    'GareGiocate': 'mean',
    'PuntiTotali': 'mean'
}).round(1)

stats_tessera.columns = ['N_Tesserati', 'Eta_Media', 'Eta_Mediana', 'Eta_StdDev', 'Eta_Min', 'Eta_Max', 'Gare_Medie', 'Punti_Medi']
stats_tessera = stats_tessera.sort_values('Eta_Media')

print("\nStatistiche età per tipologia tessera (ordinate per età media):")
print(stats_tessera.to_string())

# Calcolo percentuali
stats_tessera['%_Totale'] = (stats_tessera['N_Tesserati'] / len(df_2024) * 100).round(1)

# ============================================================================
# PARTE 2: DISTRIBUZIONE FASCE D'ETÀ PER TESSERA
# ============================================================================

print("\n" + "="*80)
print("PARTE 2: DISTRIBUZIONE FASCE D'ETÀ PER TESSERA")
print("="*80)

# Definizione fasce età
df_2024['FasciaEta'] = pd.cut(
    df_2024['Anni'],
    bins=[0, 18, 30, 40, 50, 60, 70, 80, 90, 120],
    labels=['<18', '18-30', '30-40', '40-50', '50-60', '60-70', '70-80', '80-90', '90+']
)

# Distribuzione per tessera
dist_tessera_eta = pd.crosstab(
    df_2024['MbtDesc'],
    df_2024['FasciaEta'],
    normalize='index'
) * 100

dist_tessera_eta = dist_tessera_eta.round(1)

print("\nDistribuzione % fasce d'età per tessera:")
print(dist_tessera_eta.to_string())

# ============================================================================
# PARTE 3: TOP/BOTTOM TESSERE PER ETÀ
# ============================================================================

print("\n" + "="*80)
print("PARTE 3: TOP/BOTTOM TESSERE PER ETÀ")
print("="*80)

# Ordina per età media
stats_sorted = stats_tessera.sort_values('Eta_Media')

print("\n" + "-"*80)
print("TOP 5 TESSERE PIÙ GIOVANI")
print("-"*80)

top5_giovani = stats_sorted.head(5)
for idx, row in top5_giovani.iterrows():
    print(f"\n{idx}")
    print(f"  Età media: {row['Eta_Media']:.1f} anni")
    print(f"  Età mediana: {row['Eta_Mediana']:.1f} anni")
    print(f"  Range: {int(row['Eta_Min'])}-{int(row['Eta_Max'])} anni")
    print(f"  Tesserati: {int(row['N_Tesserati'])} ({row['%_Totale']:.1f}%)")
    print(f"  Gare medie: {row['Gare_Medie']:.1f}")

print("\n" + "-"*80)
print("TOP 5 TESSERE PIÙ ANZIANE")
print("-"*80)

top5_anziani = stats_sorted.tail(5)
for idx, row in top5_anziani.iterrows():
    print(f"\n{idx}")
    print(f"  Età media: {row['Eta_Media']:.1f} anni")
    print(f"  Età mediana: {row['Eta_Mediana']:.1f} anni")
    print(f"  Range: {int(row['Eta_Min'])}-{int(row['Eta_Max'])} anni")
    print(f"  Tesserati: {int(row['N_Tesserati'])} ({row['%_Totale']:.1f}%)")
    print(f"  Gare medie: {row['Gare_Medie']:.1f}")

# ============================================================================
# PARTE 4: CONFRONTO TESSERE PRINCIPALI
# ============================================================================

print("\n" + "="*80)
print("PARTE 4: CONFRONTO TESSERE PRINCIPALI")
print("="*80)

# Tessere principali (>500 tesserati)
tessere_principali = stats_tessera[stats_tessera['N_Tesserati'] > 500].sort_values('N_Tesserati', ascending=False)

print("\nTessere principali (>500 tesserati):")
print(tessere_principali[['N_Tesserati', '%_Totale', 'Eta_Media', 'Eta_Mediana', 'Gare_Medie']].to_string())

# ============================================================================
# PARTE 5: ANALISI GIOVANI (<40 ANNI) PER TESSERA
# ============================================================================

print("\n" + "="*80)
print("PARTE 5: ANALISI GIOVANI (<40 ANNI) PER TESSERA")
print("="*80)

# Giocatori giovani per tessera
df_giovani = df_2024[df_2024['Anni'] < 40].copy()

giovani_per_tessera = df_giovani.groupby('MbtDesc').size().reset_index(name='N_Giovani')
giovani_per_tessera = giovani_per_tessera.merge(
    stats_tessera[['N_Tesserati']].reset_index(),
    on='MbtDesc'
)
giovani_per_tessera['%_Giovani'] = (giovani_per_tessera['N_Giovani'] / giovani_per_tessera['N_Tesserati'] * 100).round(1)
giovani_per_tessera = giovani_per_tessera.sort_values('%_Giovani', ascending=False)

print("\nTessere con più giovani (<40 anni) in %:")
print(giovani_per_tessera.head(10).to_string(index=False))

print("\nTessere con più giovani (<40 anni) in valore assoluto:")
print(giovani_per_tessera.sort_values('N_Giovani', ascending=False).head(10).to_string(index=False))

# ============================================================================
# PARTE 6: EVOLUZIONE ETÀ MEDIA PER TESSERA (2017-2024)
# ============================================================================

print("\n" + "="*80)
print("PARTE 6: EVOLUZIONE ETÀ MEDIA PER TESSERA (2017-2024)")
print("="*80)

# Età media per tessera per anno (solo tessere principali)
tessere_top = stats_tessera.nlargest(5, 'N_Tesserati').index.tolist()

evoluzione_eta = df[df['MbtDesc'].isin(tessere_top)].groupby(['Anno', 'MbtDesc'])['Anni'].mean().unstack()
evoluzione_eta = evoluzione_eta.round(1)

print("\nEvoluzione età media tessere principali:")
print(evoluzione_eta.to_string())

# Variazione 2017-2024
variazione_eta = pd.DataFrame({
    '2017': evoluzione_eta.loc[2017],
    '2024': evoluzione_eta.loc[2024],
    'Variazione': (evoluzione_eta.loc[2024] - evoluzione_eta.loc[2017]).round(1)
})

print("\nVariazione età media 2017→2024:")
print(variazione_eta.to_string())

# ============================================================================
# PARTE 7: CORRELAZIONE ETÀ - ATTIVITÀ PER TESSERA
# ============================================================================

print("\n" + "="*80)
print("PARTE 7: CORRELAZIONE ETÀ - ATTIVITÀ PER TESSERA")
print("="*80)

# Correlazione età media vs gare medie
corr_eta_gare = stats_tessera[['Eta_Media', 'Gare_Medie']].corr().iloc[0, 1]

print(f"\nCorrelazione età media - gare medie: {corr_eta_gare:.3f}")

if abs(corr_eta_gare) < 0.3:
    print("  Interpretazione: Correlazione debole/nulla")
elif abs(corr_eta_gare) < 0.7:
    print("  Interpretazione: Correlazione moderata")
else:
    print("  Interpretazione: Correlazione forte")

# Tessere ordinate per gare medie
stats_gare = stats_tessera.sort_values('Gare_Medie', ascending=False)

print("\nTessere con più gare medie:")
print(stats_gare[['N_Tesserati', 'Eta_Media', 'Gare_Medie']].head(10).to_string())

print("\nTessere con meno gare medie:")
print(stats_gare[['N_Tesserati', 'Eta_Media', 'Gare_Medie']].tail(10).to_string())

# ============================================================================
# PARTE 8: ANALISI SPECIFICA TESSERE CHIAVE
# ============================================================================

print("\n" + "="*80)
print("PARTE 8: ANALISI SPECIFICA TESSERE CHIAVE")
print("="*80)

tessere_chiave = [
    'Scuola Bridge',
    'Ordinario Sportivo',
    'Ordinario Non Sportivo',
    'Agonista',
    'Amatoriale'
]

for tessera in tessere_chiave:
    if tessera in stats_tessera.index:
        print(f"\n{'-'*80}")
        print(f"{tessera}")
        print(f"{'-'*80}")
        
        row = stats_tessera.loc[tessera]
        print(f"Tesserati: {int(row['N_Tesserati'])} ({row['%_Totale']:.1f}% del totale)")
        print(f"Età media: {row['Eta_Media']:.1f} anni")
        print(f"Età mediana: {row['Eta_Mediana']:.1f} anni")
        print(f"Range età: {int(row['Eta_Min'])}-{int(row['Eta_Max'])} anni")
        print(f"Deviazione std: {row['Eta_StdDev']:.1f} anni")
        print(f"Gare medie: {row['Gare_Medie']:.1f}")
        print(f"Punti medi: {row['Punti_Medi']:.0f}")
        
        # Distribuzione fasce età
        if tessera in dist_tessera_eta.index:
            print("\nDistribuzione fasce d'età:")
            dist = dist_tessera_eta.loc[tessera]
            for fascia in dist.index:
                if dist[fascia] > 0:
                    print(f"  {fascia}: {dist[fascia]:.1f}%")
        
        # Giovani
        if tessera in giovani_per_tessera['MbtDesc'].values:
            gio = giovani_per_tessera[giovani_per_tessera['MbtDesc'] == tessera].iloc[0]
            print(f"\nGiovani (<40): {int(gio['N_Giovani'])} ({gio['%_Giovani']:.1f}%)")

# ============================================================================
# SALVATAGGIO RISULTATI
# ============================================================================

print("\n" + "="*80)
print("SALVATAGGIO RISULTATI")
print("="*80)

# Salvataggio CSV
stats_tessera.to_csv('/home/ubuntu/bridge_analysis/results/statistiche_eta_per_tessera.csv')
print("✓ Salvato: statistiche_eta_per_tessera.csv")

dist_tessera_eta.to_csv('/home/ubuntu/bridge_analysis/results/distribuzione_eta_per_tessera.csv')
print("✓ Salvato: distribuzione_eta_per_tessera.csv")

giovani_per_tessera.to_csv('/home/ubuntu/bridge_analysis/results/giovani_per_tessera.csv', index=False)
print("✓ Salvato: giovani_per_tessera.csv")

evoluzione_eta.to_csv('/home/ubuntu/bridge_analysis/results/evoluzione_eta_tessere.csv')
print("✓ Salvato: evoluzione_eta_tessere.csv")

# ============================================================================
# VISUALIZZAZIONI
# ============================================================================

print("\n" + "="*80)
print("GENERAZIONE VISUALIZZAZIONI")
print("="*80)

fig, axes = plt.subplots(2, 3, figsize=(22, 14))
fig.suptitle('Analisi Età per Tipologia di Tessera', fontsize=16, fontweight='bold')

# Grafico 1: Età media per tessera (top 15)
ax1 = axes[0, 0]
top15_tessere = stats_tessera.nlargest(15, 'N_Tesserati')
colors = plt.cm.RdYlGn_r((top15_tessere['Eta_Media'] - top15_tessere['Eta_Media'].min()) / 
                          (top15_tessere['Eta_Media'].max() - top15_tessere['Eta_Media'].min()))
ax1.barh(range(len(top15_tessere)), top15_tessere['Eta_Media'], color=colors, edgecolor='black')
ax1.set_yticks(range(len(top15_tessere)))
ax1.set_yticklabels([t[:30] for t in top15_tessere.index], fontsize=9)
ax1.set_xlabel('Età Media')
ax1.set_title('Età Media per Tessera (Top 15 per numerosità)', fontsize=11, fontweight='bold')
ax1.axvline(x=df_2024['Anni'].mean(), color='red', linestyle='--', linewidth=2, label=f'Media Generale: {df_2024["Anni"].mean():.1f}')
ax1.legend()
ax1.grid(True, alpha=0.3, axis='x')
ax1.invert_yaxis()

# Grafico 2: Distribuzione età tessere principali (boxplot)
ax2 = axes[0, 1]
tessere_box = stats_tessera.nlargest(8, 'N_Tesserati').index.tolist()
data_box = [df_2024[df_2024['MbtDesc'] == t]['Anni'].values for t in tessere_box]
bp = ax2.boxplot(data_box, labels=[t[:20] for t in tessere_box], patch_artist=True)
for patch in bp['boxes']:
    patch.set_facecolor('lightblue')
ax2.set_ylabel('Età')
ax2.set_title('Distribuzione Età Tessere Principali', fontsize=11, fontweight='bold')
ax2.tick_params(axis='x', rotation=45, labelsize=8)
ax2.grid(True, alpha=0.3, axis='y')

# Grafico 3: % Giovani (<40) per tessera
ax3 = axes[0, 2]
top10_giovani = giovani_per_tessera.head(10)
ax3.barh(range(len(top10_giovani)), top10_giovani['%_Giovani'], color='green', edgecolor='black')
ax3.set_yticks(range(len(top10_giovani)))
ax3.set_yticklabels([t[:30] for t in top10_giovani['MbtDesc']], fontsize=9)
ax3.set_xlabel('% Giovani (<40 anni)')
ax3.set_title('Tessere con Più Giovani (%)', fontsize=11, fontweight='bold')
ax3.grid(True, alpha=0.3, axis='x')
ax3.invert_yaxis()

# Grafico 4: Evoluzione età media tessere principali
ax4 = axes[1, 0]
for tessera in evoluzione_eta.columns:
    ax4.plot(evoluzione_eta.index, evoluzione_eta[tessera], marker='o', linewidth=2, label=tessera[:20])
ax4.set_xlabel('Anno')
ax4.set_ylabel('Età Media')
ax4.set_title('Evoluzione Età Media Tessere Principali (2017-2024)', fontsize=11, fontweight='bold')
ax4.legend(fontsize=8, loc='best')
ax4.grid(True, alpha=0.3)

# Grafico 5: Correlazione età - gare medie
ax5 = axes[1, 1]
ax5.scatter(stats_tessera['Eta_Media'], stats_tessera['Gare_Medie'], 
            s=stats_tessera['N_Tesserati']/10, alpha=0.6, edgecolors='black')
ax5.set_xlabel('Età Media')
ax5.set_ylabel('Gare Medie')
ax5.set_title(f'Correlazione Età-Attività (r={corr_eta_gare:.3f})', fontsize=11, fontweight='bold')
ax5.grid(True, alpha=0.3)

# Aggiungi etichette per tessere principali
for idx, row in tessere_principali.iterrows():
    ax5.annotate(idx[:15], (row['Eta_Media'], row['Gare_Medie']), 
                fontsize=7, alpha=0.7)

# Grafico 6: Distribuzione fasce età per tessere chiave
ax6 = axes[1, 2]
tessere_viz = ['Scuola Bridge', 'Ordinario Sportivo', 'Agonista', 'Amatoriale']
tessere_viz = [t for t in tessere_viz if t in dist_tessera_eta.index]
dist_viz = dist_tessera_eta.loc[tessere_viz]

x = np.arange(len(dist_viz.columns))
width = 0.2
for i, tessera in enumerate(tessere_viz):
    ax6.bar(x + i*width, dist_viz.loc[tessera], width, label=tessera[:20], edgecolor='black')

ax6.set_xlabel('Fascia d\'Età')
ax6.set_ylabel('% Tesserati')
ax6.set_title('Distribuzione Fasce Età per Tessera', fontsize=11, fontweight='bold')
ax6.set_xticks(x + width * 1.5)
ax6.set_xticklabels(dist_viz.columns, rotation=45)
ax6.legend(fontsize=8)
ax6.grid(True, alpha=0.3, axis='y')

plt.tight_layout()
plt.savefig('/home/ubuntu/bridge_analysis/results/analisi_eta_per_tessera.png', 
            dpi=300, bbox_inches='tight')
print("✓ Salvato: analisi_eta_per_tessera.png")

print("\n" + "="*80)
print("ANALISI COMPLETATA!")
print("="*80)
