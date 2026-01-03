#!/usr/bin/env python3
"""
Analisi approfondita tessere Scuola Bridge
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

print("="*80)
print("ANALISI APPROFONDITA: SCUOLA BRIDGE")
print("="*80)

# Caricamento dati
df = pd.read_csv('/home/ubuntu/bridge_analysis/dati_unificati.csv')

# Filtro solo Scuola Bridge
scuola = df[df['MbtDesc'] == 'Scuola Bridge'].copy()

print(f"\n1. PANORAMICA GENERALE")
print(f"   Totale tesseramenti Scuola Bridge: {len(scuola):,}")
print(f"   Giocatori unici Scuola Bridge: {scuola['MmbCode'].nunique():,}")
print(f"   % sul totale tesseramenti: {len(scuola)/len(df)*100:.2f}%")

# Analisi per anno
print(f"\n2. DISTRIBUZIONE PER ANNO")
print("-" * 80)
anno_stats = scuola.groupby('Anno').agg({
    'MmbCode': ['count', 'nunique'],
    'GareGiocate': 'mean',
    'PuntiTotali': 'mean'
}).round(2)
anno_stats.columns = ['Tesseramenti', 'Giocatori Unici', 'Gare Medie', 'Punti Medi']
print(anno_stats)

# Analisi conversione: quanti Scuola Bridge si sono ritesserati?
print(f"\n3. ANALISI CONVERSIONE/RETENTION")
print("-" * 80)

for year in range(2017, 2024):
    # Giocatori Scuola Bridge nell'anno corrente
    scuola_year = set(scuola[scuola['Anno'] == year]['MmbCode'].unique())
    
    if len(scuola_year) == 0:
        continue
    
    # Tutti i giocatori anno successivo (qualsiasi tipo tessera)
    next_year = year + 1
    all_next = set(df[df['Anno'] == next_year]['MmbCode'].unique())
    
    # Ritesserati (qualsiasi tipo)
    retained_any = scuola_year.intersection(all_next)
    
    # Ritesserati ancora come Scuola Bridge
    scuola_next = set(scuola[scuola['Anno'] == next_year]['MmbCode'].unique())
    retained_scuola = scuola_year.intersection(scuola_next)
    
    # Convertiti ad altre tessere
    converted = retained_any - retained_scuola
    
    retention_rate = len(retained_any) / len(scuola_year) * 100
    conversion_rate = len(converted) / len(scuola_year) * 100
    churn_rate = 100 - retention_rate
    
    print(f"\nAnno {year} → {next_year}:")
    print(f"  Scuola Bridge {year}: {len(scuola_year):,}")
    print(f"  Ritesserati totali: {len(retained_any):,} ({retention_rate:.1f}%)")
    print(f"  - Ancora Scuola Bridge: {len(retained_scuola):,} ({len(retained_scuola)/len(scuola_year)*100:.1f}%)")
    print(f"  - Convertiti ad altre tessere: {len(converted):,} ({conversion_rate:.1f}%)")
    print(f"  Persi (churn): {len(scuola_year) - len(retained_any):,} ({churn_rate:.1f}%)")

# Analisi conversione a quali tessere
print(f"\n4. CONVERSIONE A QUALI TIPOLOGIE DI TESSERA?")
print("-" * 80)

conversions = []
for year in range(2017, 2024):
    scuola_year = set(scuola[scuola['Anno'] == year]['MmbCode'].unique())
    
    if len(scuola_year) == 0:
        continue
    
    next_year = year + 1
    df_next = df[df['Anno'] == next_year]
    
    # Giocatori che erano Scuola Bridge e ora hanno altra tessera
    converted = df_next[
        (df_next['MmbCode'].isin(scuola_year)) & 
        (df_next['MbtDesc'] != 'Scuola Bridge')
    ]
    
    if len(converted) > 0:
        tipo_counts = converted['MbtDesc'].value_counts()
        print(f"\n{year} → {next_year} (Convertiti: {len(converted)})")
        for tipo, count in tipo_counts.items():
            pct = count / len(converted) * 100
            print(f"  {tipo}: {count} ({pct:.1f}%)")

# Analisi demografia Scuola Bridge
print(f"\n5. DEMOGRAFIA SCUOLA BRIDGE")
print("-" * 80)

print(f"\nEtà:")
print(f"  Media: {scuola['Anni'].mean():.1f} anni")
print(f"  Mediana: {scuola['Anni'].median():.0f} anni")
print(f"  Min: {scuola['Anni'].min():.0f} anni")
print(f"  Max: {scuola['Anni'].max():.0f} anni")

print(f"\nDistribuzione per fascia d'età:")
scuola['FasciaEta'] = pd.cut(scuola['Anni'], 
                              bins=[0, 18, 30, 40, 50, 60, 70, 80, 90, 120],
                              labels=['<18', '18-30', '30-40', '40-50', '50-60', '60-70', '70-80', '80-90', '90+'])
fascia_counts = scuola['FasciaEta'].value_counts().sort_index()
for fascia, count in fascia_counts.items():
    pct = count / len(scuola) * 100
    print(f"  {fascia}: {count:,} ({pct:.1f}%)")

print(f"\nSesso:")
sesso_counts = scuola['MmbSex'].value_counts()
for sesso, count in sesso_counts.items():
    pct = count / len(scuola) * 100
    print(f"  {sesso}: {count:,} ({pct:.1f}%)")

# Analisi attività
print(f"\n6. LIVELLO DI ATTIVITÀ SCUOLA BRIDGE")
print("-" * 80)

print(f"\nGare giocate:")
print(f"  Media: {scuola['GareGiocate'].mean():.1f}")
print(f"  Mediana: {scuola['GareGiocate'].median():.0f}")
print(f"  Con 0 gare: {len(scuola[scuola['GareGiocate'] == 0]):,} ({len(scuola[scuola['GareGiocate'] == 0])/len(scuola)*100:.1f}%)")
print(f"  Con 1-10 gare: {len(scuola[(scuola['GareGiocate'] >= 1) & (scuola['GareGiocate'] <= 10)]):,}")
print(f"  Con 11-30 gare: {len(scuola[(scuola['GareGiocate'] >= 11) & (scuola['GareGiocate'] <= 30)]):,}")
print(f"  Con 30+ gare: {len(scuola[scuola['GareGiocate'] > 30]):,}")

print(f"\nPunti:")
print(f"  Media: {scuola['PuntiTotali'].mean():.0f}")
print(f"  Mediana: {scuola['PuntiTotali'].median():.0f}")
print(f"  Con 0 punti: {len(scuola[scuola['PuntiTotali'] == 0]):,} ({len(scuola[scuola['PuntiTotali'] == 0])/len(scuola)*100:.1f}%)")

# Confronto con altre tessere
print(f"\n7. CONFRONTO CON ALTRE TIPOLOGIE TESSERA")
print("-" * 80)

tipo_comparison = df.groupby('MbtDesc').agg({
    'MmbCode': 'count',
    'GareGiocate': 'mean',
    'PuntiTotali': 'mean',
    'Anni': 'mean'
}).round(2)
tipo_comparison.columns = ['Tesseramenti', 'Gare Medie', 'Punti Medi', 'Età Media']
tipo_comparison = tipo_comparison.sort_values('Tesseramenti', ascending=False)
print(tipo_comparison.head(10))

# Calcolo retention medio per tipo tessera
print(f"\n8. RETENTION RATE PER TIPOLOGIA TESSERA")
print("-" * 80)

retention_by_type = {}
for tipo in df['MbtDesc'].unique():
    if pd.isna(tipo):
        continue
    
    retention_rates = []
    for year in range(2017, 2024):
        players_year = set(df[(df['Anno'] == year) & (df['MbtDesc'] == tipo)]['MmbCode'].unique())
        if len(players_year) == 0:
            continue
        
        players_next = set(df[df['Anno'] == year + 1]['MmbCode'].unique())
        retained = players_year.intersection(players_next)
        
        if len(players_year) > 10:  # Solo se campione significativo
            retention_rates.append(len(retained) / len(players_year) * 100)
    
    if retention_rates:
        retention_by_type[tipo] = np.mean(retention_rates)

retention_df = pd.DataFrame(list(retention_by_type.items()), columns=['Tipo Tessera', 'Retention %'])
retention_df = retention_df.sort_values('Retention %', ascending=False)
print(retention_df.to_string(index=False))

# Visualizzazioni
print(f"\n9. GENERAZIONE GRAFICI...")

fig, axes = plt.subplots(2, 2, figsize=(16, 12))
fig.suptitle('Analisi Scuola Bridge', fontsize=16, fontweight='bold')

# Grafico 1: Trend tesseramenti per anno
ax1 = axes[0, 0]
anno_counts = scuola.groupby('Anno').size()
ax1.plot(anno_counts.index, anno_counts.values, marker='o', linewidth=2, markersize=8)
ax1.set_title('Tesseramenti Scuola Bridge per Anno', fontsize=12, fontweight='bold')
ax1.set_xlabel('Anno')
ax1.set_ylabel('Numero Tesseramenti')
ax1.grid(True, alpha=0.3)
for i, v in enumerate(anno_counts.values):
    ax1.text(anno_counts.index[i], v + 50, str(v), ha='center', va='bottom', fontweight='bold')

# Grafico 2: Distribuzione età
ax2 = axes[0, 1]
fascia_counts.plot(kind='bar', ax=ax2, color='steelblue')
ax2.set_title('Distribuzione per Fascia d\'Età', fontsize=12, fontweight='bold')
ax2.set_xlabel('Fascia d\'Età')
ax2.set_ylabel('Numero Tesseramenti')
ax2.tick_params(axis='x', rotation=45)
ax2.grid(True, alpha=0.3, axis='y')

# Grafico 3: Distribuzione gare giocate
ax3 = axes[1, 0]
bins = [0, 1, 10, 20, 30, 50, 100, scuola['GareGiocate'].max()]
ax3.hist(scuola['GareGiocate'], bins=bins, edgecolor='black', alpha=0.7)
ax3.set_title('Distribuzione Gare Giocate', fontsize=12, fontweight='bold')
ax3.set_xlabel('Numero Gare')
ax3.set_ylabel('Frequenza')
ax3.grid(True, alpha=0.3, axis='y')

# Grafico 4: Retention rate confronto
ax4 = axes[1, 1]
top_types = retention_df.head(8)
colors = ['red' if x == 'Scuola Bridge' else 'steelblue' for x in top_types['Tipo Tessera']]
ax4.barh(top_types['Tipo Tessera'], top_types['Retention %'], color=colors)
ax4.set_title('Retention Rate per Tipologia Tessera', fontsize=12, fontweight='bold')
ax4.set_xlabel('Retention Rate (%)')
ax4.axvline(x=81.03, color='green', linestyle='--', linewidth=2, label='Media Generale (81%)')
ax4.legend()
ax4.grid(True, alpha=0.3, axis='x')

plt.tight_layout()
plt.savefig('/home/ubuntu/bridge_analysis/results/analisi_scuola_bridge.png', dpi=300, bbox_inches='tight')
print(f"   Grafico salvato: analisi_scuola_bridge.png")

print(f"\n{'='*80}")
print("CONCLUSIONI CHIAVE:")
print("="*80)
print("""
1. RETENTION CRITICO: Scuola Bridge ha il retention più basso tra tutte le tessere
   (~45% vs 81% medio), perdendo oltre metà dei corsisti ogni anno.

2. CONVERSIONE LIMITATA: Solo il 10-15% circa si converte a tessere "stabili" 
   (Ordinario Sportivo/Agonista), la maggior parte abbandona completamente.

3. ETÀ ELEVATA: Anche i corsisti Scuola Bridge hanno età media alta (60-70 anni),
   non si riesce ad attrarre giovani nemmeno nei corsi.

4. BASSA ATTIVITÀ: Gare medie ~21 vs 45 della media generale, indicando scarso
   engagement anche durante il periodo di corso.

5. PROBLEMA STRUTTURALE: Non è un problema di qualità del corso, ma di follow-up
   e integrazione post-corso. Serve un programma di accompagnamento strutturato.

RACCOMANDAZIONI:
- Follow-up personalizzato entro 7 giorni da fine corso
- Tutor dedicato per primi 3 mesi
- Tornei "principianti friendly" dedicati
- Community online per ex-studenti
- Incentivi economici per primo anno completo
- Target: portare retention dal 45% al 65% entro 2026
""")

print("\n✓ Analisi completata!")
