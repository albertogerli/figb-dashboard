#!/usr/bin/env python3
"""
Analisi conversione Scuola Bridge per circolo/associazione
+ Statistiche stratificate per età e regione
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import json

print("="*80)
print("ANALISI CONVERSIONE PER CIRCOLO E STATISTICHE STRATIFICATE")
print("="*80)

# Caricamento dati
df = pd.read_csv('/home/ubuntu/bridge_analysis/dati_unificati.csv')

# ============================================================================
# PARTE 1: ANALISI CONVERSIONE PER CIRCOLO
# ============================================================================

print("\n" + "="*80)
print("PARTE 1: ANALISI CONVERSIONE SCUOLA BRIDGE PER CIRCOLO")
print("="*80)

# Filtro Scuola Bridge
scuola = df[df['MbtDesc'] == 'Scuola Bridge'].copy()

# Analisi conversione per circolo
conversioni_circolo = []

for circolo in scuola['MmbGroup'].unique():
    if pd.isna(circolo):
        continue
    
    # Giocatori Scuola Bridge di questo circolo
    players_scuola = set(scuola[scuola['MmbGroup'] == circolo]['MmbCode'].unique())
    
    if len(players_scuola) < 10:  # Solo circoli con almeno 10 corsisti
        continue
    
    # Verifica conversione: quanti di questi hanno anche tessere non-Scuola
    df_players = df[df['MmbCode'].isin(players_scuola)]
    
    # Tessere non-Scuola di questi giocatori
    converted = df_players[df_players['MbtDesc'] != 'Scuola Bridge']
    players_converted = set(converted['MmbCode'].unique())
    
    # Calcolo metriche
    n_corsisti = len(players_scuola)
    n_convertiti = len(players_converted)
    tasso_conversione = (n_convertiti / n_corsisti * 100) if n_corsisti > 0 else 0
    
    # Destinazioni conversione
    destinazioni = converted.groupby('MbtDesc').size().to_dict()
    
    # Regione circolo
    regione = scuola[scuola['MmbGroup'] == circolo]['GrpArea'].mode()
    regione = regione.iloc[0] if len(regione) > 0 else 'N/A'
    
    # Età media corsisti
    eta_media = scuola[scuola['MmbGroup'] == circolo]['Anni'].mean()
    
    # Gare medie corsisti
    gare_medie = scuola[scuola['MmbGroup'] == circolo]['GareGiocate'].mean()
    
    conversioni_circolo.append({
        'Circolo': circolo,
        'Regione': regione,
        'N_Corsisti': n_corsisti,
        'N_Convertiti': n_convertiti,
        'Tasso_Conversione_%': round(tasso_conversione, 1),
        'Eta_Media_Corsisti': round(eta_media, 1),
        'Gare_Medie_Corsisti': round(gare_medie, 1),
        'Destinazioni': destinazioni
    })

# Creazione DataFrame
df_conversioni = pd.DataFrame(conversioni_circolo)
df_conversioni = df_conversioni.sort_values('Tasso_Conversione_%', ascending=False)

print(f"\nCircoli analizzati: {len(df_conversioni)}")
print(f"Circoli con almeno 10 corsisti: {len(df_conversioni)}")

# Top 20 circoli per tasso di conversione
print("\n" + "-"*80)
print("TOP 20 CIRCOLI PER TASSO DI CONVERSIONE")
print("-"*80)

top20 = df_conversioni.head(20)
print(top20[['Circolo', 'Regione', 'N_Corsisti', 'N_Convertiti', 'Tasso_Conversione_%', 
             'Eta_Media_Corsisti', 'Gare_Medie_Corsisti']].to_string(index=False))

# Bottom 20 circoli per tasso di conversione
print("\n" + "-"*80)
print("BOTTOM 20 CIRCOLI PER TASSO DI CONVERSIONE")
print("-"*80)

bottom20 = df_conversioni.tail(20)
print(bottom20[['Circolo', 'Regione', 'N_Corsisti', 'N_Convertiti', 'Tasso_Conversione_%',
               'Eta_Media_Corsisti', 'Gare_Medie_Corsisti']].to_string(index=False))

# Statistiche aggregate
print("\n" + "-"*80)
print("STATISTICHE AGGREGATE CONVERSIONE CIRCOLI")
print("-"*80)

print(f"\nTasso di conversione:")
print(f"  Media: {df_conversioni['Tasso_Conversione_%'].mean():.1f}%")
print(f"  Mediana: {df_conversioni['Tasso_Conversione_%'].median():.1f}%")
print(f"  Deviazione Standard: {df_conversioni['Tasso_Conversione_%'].std():.1f}%")
print(f"  Minimo: {df_conversioni['Tasso_Conversione_%'].min():.1f}%")
print(f"  Massimo: {df_conversioni['Tasso_Conversione_%'].max():.1f}%")
print(f"  Q1 (25%): {df_conversioni['Tasso_Conversione_%'].quantile(0.25):.1f}%")
print(f"  Q3 (75%): {df_conversioni['Tasso_Conversione_%'].quantile(0.75):.1f}%")

# Segmentazione circoli per performance
print("\n" + "-"*80)
print("SEGMENTAZIONE CIRCOLI PER PERFORMANCE")
print("-"*80)

df_conversioni['Categoria'] = pd.cut(
    df_conversioni['Tasso_Conversione_%'],
    bins=[0, 10, 20, 30, 40, 100],
    labels=['Critico (<10%)', 'Basso (10-20%)', 'Medio (20-30%)', 'Buono (30-40%)', 'Eccellente (>40%)']
)

categoria_counts = df_conversioni['Categoria'].value_counts().sort_index()
for cat, count in categoria_counts.items():
    pct = count / len(df_conversioni) * 100
    avg_conversion = df_conversioni[df_conversioni['Categoria'] == cat]['Tasso_Conversione_%'].mean()
    print(f"  {cat}: {count} circoli ({pct:.1f}%) - Conversione media: {avg_conversion:.1f}%")

# Correlazione con altre variabili
print("\n" + "-"*80)
print("CORRELAZIONI")
print("-"*80)

corr_eta = df_conversioni['Tasso_Conversione_%'].corr(df_conversioni['Eta_Media_Corsisti'])
corr_gare = df_conversioni['Tasso_Conversione_%'].corr(df_conversioni['Gare_Medie_Corsisti'])
corr_numerosita = df_conversioni['Tasso_Conversione_%'].corr(df_conversioni['N_Corsisti'])

print(f"\nCorrelazione Tasso Conversione con:")
print(f"  Età Media Corsisti: {corr_eta:.3f} {'(negativa)' if corr_eta < 0 else '(positiva)'}")
print(f"  Gare Medie Corsisti: {corr_gare:.3f} {'(negativa)' if corr_gare < 0 else '(positiva)'}")
print(f"  Numerosità Corsisti: {corr_numerosita:.3f} {'(negativa)' if corr_numerosita < 0 else '(positiva)'}")

# Analisi per regione
print("\n" + "-"*80)
print("TASSO DI CONVERSIONE MEDIO PER REGIONE")
print("-"*80)

conversione_regione = df_conversioni.groupby('Regione').agg({
    'Tasso_Conversione_%': 'mean',
    'N_Corsisti': 'sum',
    'N_Convertiti': 'sum',
    'Circolo': 'count'
}).round(1)
conversione_regione.columns = ['Tasso_Conv_%_Medio', 'Tot_Corsisti', 'Tot_Convertiti', 'N_Circoli']
conversione_regione = conversione_regione.sort_values('Tasso_Conv_%_Medio', ascending=False)

print(conversione_regione.to_string())

# ============================================================================
# PARTE 2: STATISTICHE STRATIFICATE PER FASCIA D'ETÀ
# ============================================================================

print("\n" + "="*80)
print("PARTE 2: STATISTICHE STRATIFICATE PER FASCIA D'ETÀ")
print("="*80)

# Creazione fasce d'età
df['FasciaEta'] = pd.cut(df['Anni'], 
                         bins=[0, 18, 30, 40, 50, 60, 70, 80, 90, 120],
                         labels=['<18', '18-30', '30-40', '40-50', '50-60', '60-70', '70-80', '80-90', '90+'])

# Statistiche per fascia d'età
print("\n" + "-"*80)
print("STATISTICHE COMPLETE PER FASCIA D'ETÀ")
print("-"*80)

stats_eta = df.groupby('FasciaEta').agg({
    'MmbCode': ['count', 'nunique'],
    'GareGiocate': ['mean', 'median', 'sum'],
    'PuntiTotali': ['mean', 'median', 'sum'],
    'Anni': ['mean', 'min', 'max']
}).round(2)

stats_eta.columns = ['Tesseramenti', 'Giocatori_Unici', 'Gare_Medie', 'Gare_Mediane', 
                     'Gare_Totali', 'Punti_Medi', 'Punti_Mediani', 'Punti_Totali',
                     'Eta_Media', 'Eta_Min', 'Eta_Max']

print(stats_eta.to_string())

# Distribuzione sesso per fascia d'età
print("\n" + "-"*80)
print("DISTRIBUZIONE SESSO PER FASCIA D'ETÀ")
print("-"*80)

sesso_eta = df.groupby(['FasciaEta', 'MmbSex']).size().unstack(fill_value=0)
sesso_eta['Totale'] = sesso_eta.sum(axis=1)
sesso_eta['%_Maschi'] = (sesso_eta['M'] / sesso_eta['Totale'] * 100).round(1)
sesso_eta['%_Femmine'] = (sesso_eta['F'] / sesso_eta['Totale'] * 100).round(1)

print(sesso_eta.to_string())

# Distribuzione tipologie tessera per fascia d'età
print("\n" + "-"*80)
print("TOP 5 TIPOLOGIE TESSERA PER FASCIA D'ETÀ")
print("-"*80)

for fascia in ['<18', '18-30', '30-40', '40-50', '50-60', '60-70', '70-80', '80-90', '90+']:
    df_fascia = df[df['FasciaEta'] == fascia]
    if len(df_fascia) == 0:
        continue
    
    print(f"\n{fascia} anni ({len(df_fascia):,} tesseramenti):")
    top_tessere = df_fascia['MbtDesc'].value_counts().head(5)
    for tessera, count in top_tessere.items():
        pct = count / len(df_fascia) * 100
        print(f"  {tessera}: {count:,} ({pct:.1f}%)")

# Retention per fascia d'età
print("\n" + "-"*80)
print("RETENTION RATE PER FASCIA D'ETÀ (ANNO SU ANNO)")
print("-"*80)

retention_eta = []
for fascia in ['<18', '18-30', '30-40', '40-50', '50-60', '60-70', '70-80', '80-90', '90+']:
    retention_rates = []
    
    for year in range(2017, 2024):
        players_year = set(df[(df['Anno'] == year) & (df['FasciaEta'] == fascia)]['MmbCode'].unique())
        if len(players_year) < 10:
            continue
        
        players_next = set(df[df['Anno'] == year + 1]['MmbCode'].unique())
        retained = players_year.intersection(players_next)
        
        retention_rate = len(retained) / len(players_year) * 100
        retention_rates.append(retention_rate)
    
    if retention_rates:
        retention_eta.append({
            'Fascia': fascia,
            'Retention_%_Medio': round(np.mean(retention_rates), 1),
            'Retention_%_Min': round(np.min(retention_rates), 1),
            'Retention_%_Max': round(np.max(retention_rates), 1),
            'N_Anni_Analizzati': len(retention_rates)
        })

df_retention_eta = pd.DataFrame(retention_eta)
print(df_retention_eta.to_string(index=False))

# ============================================================================
# PARTE 3: STATISTICHE STRATIFICATE PER REGIONE
# ============================================================================

print("\n" + "="*80)
print("PARTE 3: STATISTICHE STRATIFICATE PER REGIONE")
print("="*80)

# Statistiche complete per regione
print("\n" + "-"*80)
print("STATISTICHE COMPLETE PER REGIONE")
print("-"*80)

stats_regione = df.groupby('GrpArea').agg({
    'MmbCode': ['count', 'nunique'],
    'MmbGroup': 'nunique',
    'GareGiocate': ['mean', 'sum'],
    'PuntiTotali': ['mean', 'sum'],
    'Anni': 'mean'
}).round(2)

stats_regione.columns = ['Tesseramenti', 'Giocatori_Unici', 'Circoli', 
                         'Gare_Medie', 'Gare_Totali', 'Punti_Medi', 'Punti_Totali', 'Eta_Media']
stats_regione = stats_regione.sort_values('Tesseramenti', ascending=False)

print(stats_regione.to_string())

# Distribuzione età per regione (Top 10)
print("\n" + "-"*80)
print("DISTRIBUZIONE ETÀ PER REGIONE (TOP 10)")
print("-"*80)

top_regioni = stats_regione.head(10).index

for regione in top_regioni:
    df_regione = df[df['GrpArea'] == regione]
    
    print(f"\n{regione} ({len(df_regione):,} tesseramenti):")
    print(f"  Età media: {df_regione['Anni'].mean():.1f} anni")
    print(f"  Età mediana: {df_regione['Anni'].median():.0f} anni")
    
    # Distribuzione fasce
    fasce = df_regione['FasciaEta'].value_counts().sort_index()
    print(f"  Distribuzione fasce:")
    for fascia, count in fasce.items():
        pct = count / len(df_regione) * 100
        print(f"    {fascia}: {count:,} ({pct:.1f}%)")

# Retention per regione
print("\n" + "-"*80)
print("RETENTION RATE PER REGIONE (TOP 15)")
print("-"*80)

retention_regione = []
for regione in top_regioni:
    retention_rates = []
    
    for year in range(2017, 2024):
        players_year = set(df[(df['Anno'] == year) & (df['GrpArea'] == regione)]['MmbCode'].unique())
        if len(players_year) < 50:
            continue
        
        players_next = set(df[df['Anno'] == year + 1]['MmbCode'].unique())
        retained = players_year.intersection(players_next)
        
        retention_rate = len(retained) / len(players_year) * 100
        retention_rates.append(retention_rate)
    
    if retention_rates:
        retention_regione.append({
            'Regione': regione,
            'Retention_%': round(np.mean(retention_rates), 1),
            'Tesseramenti_Totali': len(df[df['GrpArea'] == regione])
        })

df_retention_regione = pd.DataFrame(retention_regione)
df_retention_regione = df_retention_regione.sort_values('Retention_%', ascending=False)
print(df_retention_regione.to_string(index=False))

# Tipologie tessera per regione (Top 10)
print("\n" + "-"*80)
print("DISTRIBUZIONE TIPOLOGIE TESSERA PER REGIONE (TOP 10)")
print("-"*80)

for regione in list(top_regioni)[:10]:
    df_regione = df[df['GrpArea'] == regione]
    
    print(f"\n{regione}:")
    top_tessere = df_regione['MbtDesc'].value_counts().head(5)
    for tessera, count in top_tessere.items():
        pct = count / len(df_regione) * 100
        print(f"  {tessera}: {count:,} ({pct:.1f}%)")

# ============================================================================
# PARTE 4: INCROCIO ETÀ x REGIONE
# ============================================================================

print("\n" + "="*80)
print("PARTE 4: INCROCIO ETÀ x REGIONE (TOP 10 REGIONI)")
print("="*80)

for regione in list(top_regioni)[:10]:
    df_regione = df[df['GrpArea'] == regione]
    
    print(f"\n{regione}:")
    print(f"  Tesseramenti totali: {len(df_regione):,}")
    print(f"  Età media: {df_regione['Anni'].mean():.1f} anni")
    
    # Statistiche per fascia
    stats_fascia = df_regione.groupby('FasciaEta').agg({
        'MmbCode': 'count',
        'GareGiocate': 'mean',
        'PuntiTotali': 'mean'
    }).round(1)
    stats_fascia.columns = ['Count', 'Gare_Medie', 'Punti_Medi']
    stats_fascia['%'] = (stats_fascia['Count'] / len(df_regione) * 100).round(1)
    
    print("\n  Distribuzione per fascia:")
    print(stats_fascia.to_string())

# ============================================================================
# SALVATAGGIO RISULTATI
# ============================================================================

print("\n" + "="*80)
print("SALVATAGGIO RISULTATI")
print("="*80)

# Salvataggio CSV
df_conversioni.to_csv('/home/ubuntu/bridge_analysis/results/conversione_per_circolo.csv', index=False)
print("✓ Salvato: conversione_per_circolo.csv")

stats_eta.to_csv('/home/ubuntu/bridge_analysis/results/statistiche_per_eta.csv')
print("✓ Salvato: statistiche_per_eta.csv")

stats_regione.to_csv('/home/ubuntu/bridge_analysis/results/statistiche_per_regione.csv')
print("✓ Salvato: statistiche_per_regione.csv")

df_retention_eta.to_csv('/home/ubuntu/bridge_analysis/results/retention_per_eta.csv', index=False)
print("✓ Salvato: retention_per_eta.csv")

df_retention_regione.to_csv('/home/ubuntu/bridge_analysis/results/retention_per_regione.csv', index=False)
print("✓ Salvato: retention_per_regione.csv")

# Salvataggio JSON riepilogativo
summary = {
    'conversione_circoli': {
        'n_circoli_analizzati': len(df_conversioni),
        'tasso_medio': float(df_conversioni['Tasso_Conversione_%'].mean()),
        'tasso_mediano': float(df_conversioni['Tasso_Conversione_%'].median()),
        'top_10_circoli': df_conversioni.head(10)[['Circolo', 'Regione', 'Tasso_Conversione_%']].to_dict('records'),
        'correlazioni': {
            'con_eta': float(corr_eta),
            'con_gare': float(corr_gare),
            'con_numerosita': float(corr_numerosita)
        }
    },
    'statistiche_eta': {
        'retention_per_fascia': df_retention_eta.to_dict('records')
    },
    'statistiche_regione': {
        'retention_per_regione': df_retention_regione.to_dict('records')
    }
}

with open('/home/ubuntu/bridge_analysis/results/analisi_stratificata_summary.json', 'w') as f:
    json.dump(summary, f, indent=2)
print("✓ Salvato: analisi_stratificata_summary.json")

# ============================================================================
# VISUALIZZAZIONI
# ============================================================================

print("\n" + "="*80)
print("GENERAZIONE VISUALIZZAZIONI")
print("="*80)

fig, axes = plt.subplots(2, 2, figsize=(18, 14))
fig.suptitle('Analisi Conversione e Statistiche Stratificate', fontsize=16, fontweight='bold')

# Grafico 1: Distribuzione tasso conversione circoli
ax1 = axes[0, 0]
ax1.hist(df_conversioni['Tasso_Conversione_%'], bins=20, edgecolor='black', alpha=0.7)
ax1.axvline(df_conversioni['Tasso_Conversione_%'].mean(), color='red', linestyle='--', 
            linewidth=2, label=f'Media: {df_conversioni["Tasso_Conversione_%"].mean():.1f}%')
ax1.axvline(df_conversioni['Tasso_Conversione_%'].median(), color='green', linestyle='--', 
            linewidth=2, label=f'Mediana: {df_conversioni["Tasso_Conversione_%"].median():.1f}%')
ax1.set_title('Distribuzione Tasso di Conversione per Circolo', fontsize=12, fontweight='bold')
ax1.set_xlabel('Tasso di Conversione (%)')
ax1.set_ylabel('Numero Circoli')
ax1.legend()
ax1.grid(True, alpha=0.3, axis='y')

# Grafico 2: Retention per fascia d'età
ax2 = axes[0, 1]
ax2.barh(df_retention_eta['Fascia'], df_retention_eta['Retention_%_Medio'], color='steelblue')
ax2.axvline(81.03, color='red', linestyle='--', linewidth=2, label='Media Generale (81%)')
ax2.set_title('Retention Rate per Fascia d\'Età', fontsize=12, fontweight='bold')
ax2.set_xlabel('Retention Rate (%)')
ax2.legend()
ax2.grid(True, alpha=0.3, axis='x')

# Grafico 3: Top 15 regioni per retention
ax3 = axes[1, 0]
top15_ret = df_retention_regione.head(15)
ax3.barh(top15_ret['Regione'], top15_ret['Retention_%'], color='coral')
ax3.axvline(81.03, color='red', linestyle='--', linewidth=2, label='Media Generale (81%)')
ax3.set_title('Top 15 Regioni per Retention Rate', fontsize=12, fontweight='bold')
ax3.set_xlabel('Retention Rate (%)')
ax3.legend()
ax3.grid(True, alpha=0.3, axis='x')

# Grafico 4: Scatter conversione vs età media
ax4 = axes[1, 1]
scatter = ax4.scatter(df_conversioni['Eta_Media_Corsisti'], 
                     df_conversioni['Tasso_Conversione_%'],
                     s=df_conversioni['N_Corsisti']*2,
                     alpha=0.5,
                     c=df_conversioni['Gare_Medie_Corsisti'],
                     cmap='viridis')
ax4.set_title('Conversione vs Età Media Corsisti\n(dimensione = n. corsisti, colore = gare medie)', 
              fontsize=12, fontweight='bold')
ax4.set_xlabel('Età Media Corsisti')
ax4.set_ylabel('Tasso di Conversione (%)')
ax4.grid(True, alpha=0.3)
plt.colorbar(scatter, ax=ax4, label='Gare Medie')

# Linea di tendenza
z = np.polyfit(df_conversioni['Eta_Media_Corsisti'], df_conversioni['Tasso_Conversione_%'], 1)
p = np.poly1d(z)
ax4.plot(df_conversioni['Eta_Media_Corsisti'], p(df_conversioni['Eta_Media_Corsisti']), 
         "r--", alpha=0.8, linewidth=2, label=f'Trend (corr={corr_eta:.3f})')
ax4.legend()

plt.tight_layout()
plt.savefig('/home/ubuntu/bridge_analysis/results/analisi_stratificata.png', dpi=300, bbox_inches='tight')
print("✓ Salvato: analisi_stratificata.png")

print("\n" + "="*80)
print("ANALISI COMPLETATA!")
print("="*80)
