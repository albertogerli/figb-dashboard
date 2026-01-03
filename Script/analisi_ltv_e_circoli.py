#!/usr/bin/env python3
"""
Analisi 1: Lifetime Value (LTV) per Segmento
Analisi 2: Crescita/Declino Circoli
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import json

print("="*80)
print("ANALISI LIFETIME VALUE E CRESCITA CIRCOLI")
print("="*80)

# Caricamento dati
df = pd.read_csv('/home/ubuntu/bridge_analysis/dati_unificati.csv')

print(f"\nDati caricati: {len(df):,} tesseramenti")
print(f"Giocatori unici: {df['MmbCode'].nunique():,}")
print(f"Anni: {sorted(df['Anno'].unique())}")

# ============================================================================
# PARTE 1: ANALISI LIFETIME VALUE (LTV) PER SEGMENTO
# ============================================================================

print("\n" + "="*80)
print("PARTE 1: ANALISI LIFETIME VALUE (LTV) PER SEGMENTO")
print("="*80)

# Parametri economici
COSTO_TESSERA = 70  # €/anno
COSTO_GARA = 5      # €/gara
ANNI_VITA_MEDIA = {
    '<18': 60,
    '18-30': 50,
    '30-40': 40,
    '40-50': 30,
    '50-60': 20,
    '60-70': 15,
    '70-80': 10,
    '80-90': 5,
    '90+': 2
}

# Calcolo retention rate per fascia età (da analisi precedente)
RETENTION_RATE = {
    '<18': 0.883,
    '18-30': 0.909,
    '30-40': 0.882,
    '40-50': 0.908,
    '50-60': 0.930,
    '60-70': 0.935,
    '70-80': 0.924,
    '80-90': 0.893,
    '90+': 0.838
}

# Creazione fasce d'età
df['FasciaEta'] = pd.cut(df['Anni'], 
                         bins=[0, 18, 30, 40, 50, 60, 70, 80, 90, 120],
                         labels=['<18', '18-30', '30-40', '40-50', '50-60', '60-70', '70-80', '80-90', '90+'])

# Calcolo valore annuale per giocatore
df['Valore_Annuale'] = COSTO_TESSERA + (df['GareGiocate'] * COSTO_GARA)

print("\n" + "-"*80)
print("1.1 LTV PER FASCIA D'ETÀ")
print("-"*80)

ltv_eta = []
for fascia in ['<18', '18-30', '30-40', '40-50', '50-60', '60-70', '70-80', '80-90', '90+']:
    df_fascia = df[df['FasciaEta'] == fascia]
    
    if len(df_fascia) > 0:
        valore_annuale_medio = df_fascia['Valore_Annuale'].mean()
        anni_vita = ANNI_VITA_MEDIA[fascia]
        retention = RETENTION_RATE[fascia]
        
        # Calcolo LTV con formula geometrica (retention decrescente)
        # LTV = Valore_Anno_1 + Valore_Anno_2 * retention + Valore_Anno_3 * retention^2 + ...
        # Semplificato: LTV = Valore_Annuale * (1 - retention^anni) / (1 - retention)
        if retention < 1:
            ltv = valore_annuale_medio * (1 - retention**anni_vita) / (1 - retention)
        else:
            ltv = valore_annuale_medio * anni_vita
        
        ltv_eta.append({
            'Fascia': fascia,
            'N_Giocatori': len(df_fascia),
            'Valore_Annuale_Medio': valore_annuale_medio,
            'Anni_Vita_Potenziali': anni_vita,
            'Retention_Rate': retention,
            'LTV': ltv,
            'Eta_Media': df_fascia['Anni'].mean()
        })

df_ltv_eta = pd.DataFrame(ltv_eta)
df_ltv_eta = df_ltv_eta.sort_values('LTV', ascending=False)

print("\nLifetime Value per Fascia d'Età:")
print(df_ltv_eta[['Fascia', 'N_Giocatori', 'Valore_Annuale_Medio', 'Anni_Vita_Potenziali', 'Retention_Rate', 'LTV']].to_string(index=False))

print("\n" + "-"*80)
print("TOP 3 FASCE PER LTV:")
for idx, row in df_ltv_eta.head(3).iterrows():
    print(f"\n{row['Fascia']}:")
    print(f"  LTV: €{row['LTV']:,.0f}")
    print(f"  Valore annuale: €{row['Valore_Annuale_Medio']:.0f}")
    print(f"  Anni vita potenziali: {row['Anni_Vita_Potenziali']}")
    print(f"  Retention: {row['Retention_Rate']*100:.1f}%")
    print(f"  N. giocatori: {row['N_Giocatori']:,}")

print("\n" + "-"*80)
print("1.2 LTV PER CATEGORIA")
print("-"*80)

# Calcolo LTV per categoria
ltv_cat = df.groupby('CatLabel').agg({
    'MmbCode': 'count',
    'Valore_Annuale': 'mean',
    'Anni': 'mean'
}).rename(columns={'MmbCode': 'N_Giocatori', 'Valore_Annuale': 'Valore_Annuale_Medio', 'Anni': 'Eta_Media'})

# Stima anni vita residui basata su età media
ltv_cat['Anni_Vita_Residui'] = ltv_cat['Eta_Media'].apply(lambda x: max(1, 85 - x))

# Stima retention basata su categoria (categorie alte = retention più alta)
def stima_retention_categoria(cat):
    if cat.startswith('1') or cat in ['HJ', 'HQ', 'MS', 'GM']:
        return 0.95
    elif cat.startswith('2'):
        return 0.90
    elif cat.startswith('3'):
        return 0.85
    else:  # NC
        return 0.75

ltv_cat['Retention_Stimata'] = ltv_cat.index.map(stima_retention_categoria)

# Calcolo LTV
ltv_cat['LTV'] = ltv_cat.apply(
    lambda row: row['Valore_Annuale_Medio'] * (1 - row['Retention_Stimata']**row['Anni_Vita_Residui']) / (1 - row['Retention_Stimata'])
    if row['Retention_Stimata'] < 1 else row['Valore_Annuale_Medio'] * row['Anni_Vita_Residui'],
    axis=1
)

ltv_cat = ltv_cat.sort_values('LTV', ascending=False)

print("\nTop 15 Categorie per LTV:")
print(ltv_cat.head(15)[['N_Giocatori', 'Valore_Annuale_Medio', 'Eta_Media', 'Anni_Vita_Residui', 'LTV']].round(0).to_string())

print("\n" + "-"*80)
print("1.3 LTV PER REGIONE")
print("-"*80)

# Calcolo LTV per regione
ltv_reg = df.groupby('GrpArea').agg({
    'MmbCode': 'count',
    'Valore_Annuale': 'mean',
    'Anni': 'mean'
}).rename(columns={'MmbCode': 'N_Giocatori', 'Valore_Annuale': 'Valore_Annuale_Medio', 'Anni': 'Eta_Media'})

ltv_reg['Anni_Vita_Residui'] = ltv_reg['Eta_Media'].apply(lambda x: max(1, 85 - x))
ltv_reg['Retention_Stimata'] = 0.918  # Media nazionale

ltv_reg['LTV'] = ltv_reg.apply(
    lambda row: row['Valore_Annuale_Medio'] * (1 - row['Retention_Stimata']**row['Anni_Vita_Residui']) / (1 - row['Retention_Stimata']),
    axis=1
)

ltv_reg = ltv_reg.sort_values('LTV', ascending=False)

print("\nTop 15 Regioni per LTV:")
print(ltv_reg.head(15)[['N_Giocatori', 'Valore_Annuale_Medio', 'Eta_Media', 'Anni_Vita_Residui', 'LTV']].round(0).to_string())

# ============================================================================
# PARTE 2: ANALISI CRESCITA/DECLINO CIRCOLI
# ============================================================================

print("\n" + "="*80)
print("PARTE 2: ANALISI CRESCITA/DECLINO CIRCOLI")
print("="*80)

# Tesseramenti per circolo per anno
circoli_anno = df.groupby(['MmbGroup', 'GrpName', 'GrpArea', 'Anno']).size().reset_index(name='Tesseramenti')

# Pivot per avere anni come colonne
circoli_pivot = circoli_anno.pivot_table(
    index=['MmbGroup', 'GrpName', 'GrpArea'],
    columns='Anno',
    values='Tesseramenti',
    fill_value=0
)

# Calcolo crescita 2017-2024
circoli_pivot['Tess_2017'] = circoli_pivot[2017] if 2017 in circoli_pivot.columns else 0
circoli_pivot['Tess_2024'] = circoli_pivot[2024] if 2024 in circoli_pivot.columns else 0
circoli_pivot['Crescita_Assoluta'] = circoli_pivot['Tess_2024'] - circoli_pivot['Tess_2017']
circoli_pivot['Crescita_%'] = ((circoli_pivot['Tess_2024'] - circoli_pivot['Tess_2017']) / (circoli_pivot['Tess_2017'] + 1) * 100).round(1)

# Filtro circoli con almeno 10 tesserati nel 2017 o 2024
circoli_analisi = circoli_pivot[(circoli_pivot['Tess_2017'] >= 10) | (circoli_pivot['Tess_2024'] >= 10)].copy()

print(f"\nCircoli analizzati: {len(circoli_analisi)}")

# Reset index per lavorare meglio
circoli_analisi = circoli_analisi.reset_index()

print("\n" + "-"*80)
print("2.1 TOP 20 CIRCOLI IN CRESCITA")
print("-"*80)

top_crescita = circoli_analisi.nlargest(20, 'Crescita_Assoluta')

for idx, row in top_crescita.iterrows():
    print(f"\n{row['GrpName']} ({row['GrpArea']})")
    print(f"  2017: {int(row['Tess_2017'])} → 2024: {int(row['Tess_2024'])}")
    print(f"  Crescita: +{int(row['Crescita_Assoluta'])} ({row['Crescita_%']:+.1f}%)")

print("\n" + "-"*80)
print("2.2 TOP 20 CIRCOLI IN DECLINO")
print("-"*80)

top_declino = circoli_analisi.nsmallest(20, 'Crescita_Assoluta')

for idx, row in top_declino.iterrows():
    print(f"\n{row['GrpName']} ({row['GrpArea']})")
    print(f"  2017: {int(row['Tess_2017'])} → 2024: {int(row['Tess_2024'])}")
    print(f"  Declino: {int(row['Crescita_Assoluta'])} ({row['Crescita_%']:+.1f}%)")

print("\n" + "-"*80)
print("2.3 STATISTICHE CRESCITA PER REGIONE")
print("-"*80)

# Aggregazione per regione
crescita_regione = circoli_analisi.groupby('GrpArea').agg({
    'MmbGroup': 'count',
    'Tess_2017': 'sum',
    'Tess_2024': 'sum',
    'Crescita_Assoluta': 'sum'
}).rename(columns={'MmbGroup': 'N_Circoli'})

crescita_regione['Crescita_%'] = ((crescita_regione['Tess_2024'] - crescita_regione['Tess_2017']) / (crescita_regione['Tess_2017'] + 1) * 100).round(1)
crescita_regione = crescita_regione.sort_values('Crescita_%', ascending=False)

print("\nCrescita per Regione:")
print(crescita_regione.to_string())

print("\n" + "-"*80)
print("2.4 CARATTERISTICHE CIRCOLI IN CRESCITA VS DECLINO")
print("-"*80)

# Definizione crescita/declino
circoli_analisi['Categoria'] = pd.cut(
    circoli_analisi['Crescita_%'],
    bins=[-1000, -20, -10, 10, 20, 1000],
    labels=['Forte Declino (<-20%)', 'Declino (-20/-10%)', 'Stabile (-10/+10%)', 'Crescita (+10/+20%)', 'Forte Crescita (>+20%)']
)

print("\nDistribuzione circoli per categoria:")
print(circoli_analisi['Categoria'].value_counts().sort_index())

# Analisi caratteristiche
# Merge con dati completi per avere info su età, gare, ecc.
df_2024 = df[df['Anno'] == 2024].copy()
circoli_2024 = df_2024.groupby('MmbGroup').agg({
    'Anni': 'mean',
    'GareGiocate': 'mean',
    'PuntiTotali': 'mean',
    'MmbCode': 'count'
}).rename(columns={'MmbCode': 'N_Giocatori_2024', 'Anni': 'Eta_Media_2024', 'GareGiocate': 'Gare_Medie_2024', 'PuntiTotali': 'Punti_Medi_2024'})

circoli_completo = circoli_analisi.merge(circoli_2024, left_on='MmbGroup', right_index=True, how='left')

# Confronto crescita vs declino
forte_crescita = circoli_completo[circoli_completo['Categoria'] == 'Forte Crescita (>+20%)']
forte_declino = circoli_completo[circoli_completo['Categoria'] == 'Forte Declino (<-20%)']

print(f"\nCircoli in Forte Crescita: {len(forte_crescita)}")
print(f"  Età media 2024: {forte_crescita['Eta_Media_2024'].mean():.1f} anni")
print(f"  Gare medie 2024: {forte_crescita['Gare_Medie_2024'].mean():.1f}")
print(f"  Punti medi 2024: {forte_crescita['Punti_Medi_2024'].mean():.0f}")
print(f"  Tesserati medi 2024: {forte_crescita['Tess_2024'].mean():.0f}")

print(f"\nCircoli in Forte Declino: {len(forte_declino)}")
print(f"  Età media 2024: {forte_declino['Eta_Media_2024'].mean():.1f} anni")
print(f"  Gare medie 2024: {forte_declino['Gare_Medie_2024'].mean():.1f}")
print(f"  Punti medi 2024: {forte_declino['Punti_Medi_2024'].mean():.0f}")
print(f"  Tesserati medi 2024: {forte_declino['Tess_2024'].mean():.0f}")

# ============================================================================
# SALVATAGGIO RISULTATI
# ============================================================================

print("\n" + "="*80)
print("SALVATAGGIO RISULTATI")
print("="*80)

# Salvataggio CSV
df_ltv_eta.to_csv('/home/ubuntu/bridge_analysis/results/ltv_per_eta.csv', index=False)
print("✓ Salvato: ltv_per_eta.csv")

ltv_cat.to_csv('/home/ubuntu/bridge_analysis/results/ltv_per_categoria.csv')
print("✓ Salvato: ltv_per_categoria.csv")

ltv_reg.to_csv('/home/ubuntu/bridge_analysis/results/ltv_per_regione.csv')
print("✓ Salvato: ltv_per_regione.csv")

circoli_completo.to_csv('/home/ubuntu/bridge_analysis/results/crescita_circoli.csv', index=False)
print("✓ Salvato: crescita_circoli.csv")

crescita_regione.to_csv('/home/ubuntu/bridge_analysis/results/crescita_per_regione.csv')
print("✓ Salvato: crescita_per_regione.csv")

# ============================================================================
# VISUALIZZAZIONI
# ============================================================================

print("\n" + "="*80)
print("GENERAZIONE VISUALIZZAZIONI")
print("="*80)

fig, axes = plt.subplots(2, 3, figsize=(20, 12))
fig.suptitle('Analisi LTV e Crescita Circoli', fontsize=16, fontweight='bold')

# Grafico 1: LTV per fascia età
ax1 = axes[0, 0]
df_ltv_eta_sorted = df_ltv_eta.sort_values('Fascia')
ax1.bar(df_ltv_eta_sorted['Fascia'], df_ltv_eta_sorted['LTV']/1000, color='green', edgecolor='black', alpha=0.7)
ax1.set_title('Lifetime Value per Fascia d\'Età', fontsize=12, fontweight='bold')
ax1.set_xlabel('Fascia d\'Età')
ax1.set_ylabel('LTV (€ migliaia)')
ax1.tick_params(axis='x', rotation=45)
ax1.grid(True, alpha=0.3, axis='y')
for i, v in enumerate(df_ltv_eta_sorted['LTV'].values):
    ax1.text(i, v/1000 + 0.5, f'€{v/1000:.1f}k', ha='center', va='bottom', fontweight='bold', fontsize=9)

# Grafico 2: Top 15 categorie per LTV
ax2 = axes[0, 1]
top15_cat = ltv_cat.head(15)
ax2.barh(range(len(top15_cat)), top15_cat['LTV']/1000, color='teal', edgecolor='black', alpha=0.7)
ax2.set_yticks(range(len(top15_cat)))
ax2.set_yticklabels(top15_cat.index)
ax2.set_title('Top 15 Categorie per LTV', fontsize=12, fontweight='bold')
ax2.set_xlabel('LTV (€ migliaia)')
ax2.grid(True, alpha=0.3, axis='x')
ax2.invert_yaxis()

# Grafico 3: Top 15 regioni per LTV
ax3 = axes[0, 2]
top15_reg = ltv_reg.head(15)
ax3.barh(range(len(top15_reg)), top15_reg['LTV']/1000, color='orange', edgecolor='black', alpha=0.7)
ax3.set_yticks(range(len(top15_reg)))
ax3.set_yticklabels(top15_reg.index)
ax3.set_title('Top 15 Regioni per LTV', fontsize=12, fontweight='bold')
ax3.set_xlabel('LTV (€ migliaia)')
ax3.grid(True, alpha=0.3, axis='x')
ax3.invert_yaxis()

# Grafico 4: Distribuzione crescita circoli
ax4 = axes[1, 0]
circoli_analisi['Categoria'].value_counts().sort_index().plot(kind='bar', ax=ax4, color='steelblue', edgecolor='black')
ax4.set_title('Distribuzione Circoli per Crescita', fontsize=12, fontweight='bold')
ax4.set_xlabel('Categoria')
ax4.set_ylabel('Numero Circoli')
ax4.tick_params(axis='x', rotation=45)
ax4.grid(True, alpha=0.3, axis='y')

# Grafico 5: Crescita per regione
ax5 = axes[1, 1]
top_crescita_reg = crescita_regione.head(10)
colors = ['green' if x > 0 else 'red' for x in top_crescita_reg['Crescita_%']]
ax5.barh(range(len(top_crescita_reg)), top_crescita_reg['Crescita_%'], color=colors, edgecolor='black', alpha=0.7)
ax5.set_yticks(range(len(top_crescita_reg)))
ax5.set_yticklabels(top_crescita_reg.index)
ax5.set_title('Top 10 Regioni per Crescita %', fontsize=12, fontweight='bold')
ax5.set_xlabel('Crescita %')
ax5.axvline(x=0, color='black', linestyle='-', linewidth=1)
ax5.grid(True, alpha=0.3, axis='x')
ax5.invert_yaxis()

# Grafico 6: Scatter crescita vs età media
ax6 = axes[1, 2]
scatter = ax6.scatter(circoli_completo['Eta_Media_2024'], circoli_completo['Crescita_%'], 
                     c=circoli_completo['Tess_2024'], cmap='viridis', alpha=0.6, s=50)
ax6.set_title('Crescita vs Età Media Circolo', fontsize=12, fontweight='bold')
ax6.set_xlabel('Età Media 2024')
ax6.set_ylabel('Crescita % 2017-2024')
ax6.axhline(y=0, color='red', linestyle='--', linewidth=2, alpha=0.7)
ax6.grid(True, alpha=0.3)
plt.colorbar(scatter, ax=ax6, label='Tesserati 2024')

plt.tight_layout()
plt.savefig('/home/ubuntu/bridge_analysis/results/analisi_ltv_crescita.png', 
            dpi=300, bbox_inches='tight')
print("✓ Salvato: analisi_ltv_crescita.png")

print("\n" + "="*80)
print("ANALISI COMPLETATA!")
print("="*80)
