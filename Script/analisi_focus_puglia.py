#!/usr/bin/env python3
"""
Analisi Focus Puglia - Ultimi 2 Anni (2023-2024)
Trend, allievi, attività, retention, circoli
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import json

print("="*80)
print("ANALISI FOCUS PUGLIA 2023-2024")
print("="*80)

# Caricamento dati
df = pd.read_csv('/home/ubuntu/bridge_analysis/dati_unificati.csv')

print(f"\nDati caricati: {len(df):,} tesseramenti")

# Filtro Puglia
df_puglia = df[df['GrpArea'] == 'PUG'].copy()

print(f"Tesseramenti Puglia: {len(df_puglia):,}")
print(f"Giocatori unici Puglia: {df_puglia['MmbCode'].nunique():,}")
print(f"Circoli Puglia: {df_puglia['MmbGroup'].nunique()}")

# ============================================================================
# PARTE 1: TREND TESSERAMENTI 2017-2024
# ============================================================================

print("\n" + "="*80)
print("PARTE 1: TREND TESSERAMENTI 2017-2024")
print("="*80)

tess_anno = df_puglia.groupby('Anno').agg({
    'MmbCode': 'count',
    'Anni': 'mean',
    'GareGiocate': 'mean',
    'PuntiTotali': 'mean'
}).rename(columns={'MmbCode': 'Tesseramenti', 'Anni': 'Eta_Media', 'GareGiocate': 'Gare_Medie', 'PuntiTotali': 'Punti_Medi'})

print("\nTesseramenti per anno:")
print(tess_anno.round(1).to_string())

# Variazione anno su anno
tess_anno['Var_Assoluta'] = tess_anno['Tesseramenti'].diff()
tess_anno['Var_%'] = tess_anno['Tesseramenti'].pct_change() * 100

print("\nVariazioni anno su anno:")
print(tess_anno[['Tesseramenti', 'Var_Assoluta', 'Var_%']].round(1).to_string())

# Focus ultimi 2 anni
print("\n" + "-"*80)
print("FOCUS ULTIMI 2 ANNI (2023-2024)")
print("-"*80)

tess_2023 = tess_anno.loc[2023, 'Tesseramenti']
tess_2024 = tess_anno.loc[2024, 'Tesseramenti']
var_2023_2024 = tess_2024 - tess_2023
var_pct_2023_2024 = (var_2023_2024 / tess_2023) * 100

print(f"\n2023: {int(tess_2023)} tesseramenti")
print(f"2024: {int(tess_2024)} tesseramenti")
print(f"Variazione: {int(var_2023_2024):+d} ({var_pct_2023_2024:+.1f}%)")

if var_2023_2024 > 0:
    print("✅ MIGLIORAMENTO: Tesseramenti in crescita")
else:
    print("🔴 PEGGIORAMENTO: Tesseramenti in calo")

# ============================================================================
# PARTE 2: ALLIEVI (SCUOLA BRIDGE) 2023 vs 2024
# ============================================================================

print("\n" + "="*80)
print("PARTE 2: ALLIEVI (SCUOLA BRIDGE) 2023 vs 2024")
print("="*80)

# Filtro Scuola Bridge
df_puglia_sb = df_puglia[df_puglia['MbtDesc'] == 'Scuola Bridge'].copy()

sb_anno = df_puglia_sb.groupby('Anno').agg({
    'MmbCode': 'count',
    'Anni': 'mean',
    'GareGiocate': 'mean'
}).rename(columns={'MmbCode': 'Allievi', 'Anni': 'Eta_Media', 'GareGiocate': 'Gare_Medie'})

print("\nAllievi Scuola Bridge per anno:")
print(sb_anno.round(1).to_string())

# Focus 2023 vs 2024
if 2023 in sb_anno.index and 2024 in sb_anno.index:
    allievi_2023 = sb_anno.loc[2023, 'Allievi']
    allievi_2024 = sb_anno.loc[2024, 'Allievi']
    var_allievi = allievi_2024 - allievi_2023
    var_allievi_pct = (var_allievi / allievi_2023) * 100
    
    print(f"\n2023: {int(allievi_2023)} allievi")
    print(f"2024: {int(allievi_2024)} allievi")
    print(f"Variazione: {int(var_allievi):+d} ({var_allievi_pct:+.1f}%)")
    
    if var_allievi > 0:
        print("✅ MIGLIORAMENTO: Allievi in crescita")
    else:
        print("🔴 PEGGIORAMENTO: Allievi in calo")
    
    # Età media allievi
    eta_2023 = sb_anno.loc[2023, 'Eta_Media']
    eta_2024 = sb_anno.loc[2024, 'Eta_Media']
    var_eta = eta_2024 - eta_2023
    
    print(f"\nEtà media allievi:")
    print(f"  2023: {eta_2023:.1f} anni")
    print(f"  2024: {eta_2024:.1f} anni")
    print(f"  Variazione: {var_eta:+.1f} anni")
    
    if var_eta < 0:
        print("  ✅ MIGLIORAMENTO: Allievi più giovani")
    else:
        print("  🔴 PEGGIORAMENTO: Allievi più anziani")

# ============================================================================
# PARTE 3: ATTIVITÀ (GARE GIOCATE) 2023 vs 2024
# ============================================================================

print("\n" + "="*80)
print("PARTE 3: ATTIVITÀ (GARE GIOCATE) 2023 vs 2024")
print("="*80)

gare_2023 = tess_anno.loc[2023, 'Gare_Medie']
gare_2024 = tess_anno.loc[2024, 'Gare_Medie']
var_gare = gare_2024 - gare_2023
var_gare_pct = (var_gare / gare_2023) * 100

print(f"\nGare medie per giocatore:")
print(f"  2023: {gare_2023:.1f} gare")
print(f"  2024: {gare_2024:.1f} gare")
print(f"  Variazione: {var_gare:+.1f} ({var_gare_pct:+.1f}%)")

if var_gare > 0:
    print("  ✅ MIGLIORAMENTO: Attività in crescita")
else:
    print("  🔴 PEGGIORAMENTO: Attività in calo")

# Distribuzione attività
print("\n" + "-"*80)
print("DISTRIBUZIONE ATTIVITÀ 2024")
print("-"*80)

df_puglia_2024 = df_puglia[df_puglia['Anno'] == 2024].copy()

df_puglia_2024['Categoria_Attivita'] = pd.cut(
    df_puglia_2024['GareGiocate'],
    bins=[0, 10, 30, 50, 100, 1000],
    labels=['Inattivo (<10)', 'Poco Attivo (10-30)', 'Attivo (30-50)', 'Molto Attivo (50-100)', 'Iper Attivo (>100)']
)

dist_attivita = df_puglia_2024['Categoria_Attivita'].value_counts().sort_index()
dist_attivita_pct = (dist_attivita / len(df_puglia_2024) * 100).round(1)

print("\nDistribuzione attività 2024:")
for cat in dist_attivita.index:
    print(f"  {cat}: {dist_attivita[cat]} ({dist_attivita_pct[cat]:.1f}%)")

# ============================================================================
# PARTE 4: RETENTION RATE 2023→2024
# ============================================================================

print("\n" + "="*80)
print("PARTE 4: RETENTION RATE 2023→2024")
print("="*80)

# Giocatori 2023
giocatori_2023 = set(df_puglia[df_puglia['Anno'] == 2023]['MmbCode'].unique())
giocatori_2024 = set(df_puglia[df_puglia['Anno'] == 2024]['MmbCode'].unique())

# Ritesserati
ritesserati = giocatori_2023.intersection(giocatori_2024)
non_ritesserati = giocatori_2023 - giocatori_2024
nuovi = giocatori_2024 - giocatori_2023

retention_rate = len(ritesserati) / len(giocatori_2023) * 100
churn_rate = len(non_ritesserati) / len(giocatori_2023) * 100

print(f"\nGiocatori 2023: {len(giocatori_2023)}")
print(f"Ritesserati 2024: {len(ritesserati)} ({retention_rate:.1f}%)")
print(f"Non ritesserati: {len(non_ritesserati)} ({churn_rate:.1f}%)")
print(f"Nuovi 2024: {len(nuovi)}")

print(f"\nRetention Rate 2023→2024: {retention_rate:.1f}%")
print(f"Churn Rate 2023→2024: {churn_rate:.1f}%")

# Confronto con media nazionale
# (dalla analisi precedente: retention nazionale 91,8%, churn 8,2%)
retention_nazionale = 91.8
churn_nazionale = 8.2

print(f"\nConfronto con media nazionale:")
print(f"  Retention Puglia: {retention_rate:.1f}% vs Nazionale: {retention_nazionale:.1f}%")
print(f"  Differenza: {retention_rate - retention_nazionale:+.1f}pp")

if retention_rate > retention_nazionale:
    print("  ✅ MIGLIORAMENTO: Retention superiore alla media")
elif retention_rate > retention_nazionale - 2:
    print("  ⚠️ NELLA NORMA: Retention vicina alla media")
else:
    print("  🔴 PEGGIORAMENTO: Retention inferiore alla media")

# Retention per fascia età
print("\n" + "-"*80)
print("RETENTION PER FASCIA D'ETÀ 2023→2024")
print("-"*80)

df_puglia_2023 = df_puglia[df_puglia['Anno'] == 2023].copy()
df_puglia_2023['FasciaEta'] = pd.cut(
    df_puglia_2023['Anni'],
    bins=[0, 30, 40, 50, 60, 70, 80, 90, 120],
    labels=['<30', '30-40', '40-50', '50-60', '60-70', '70-80', '80-90', '90+']
)

for fascia in ['<30', '30-40', '40-50', '50-60', '60-70', '70-80', '80-90', '90+']:
    gioc_fascia_2023 = set(df_puglia_2023[df_puglia_2023['FasciaEta'] == fascia]['MmbCode'].unique())
    if len(gioc_fascia_2023) > 0:
        ritess_fascia = gioc_fascia_2023.intersection(giocatori_2024)
        retention_fascia = len(ritess_fascia) / len(gioc_fascia_2023) * 100
        print(f"  {fascia}: {len(gioc_fascia_2023)} giocatori, retention {retention_fascia:.1f}%")

# ============================================================================
# PARTE 5: PERFORMANCE CIRCOLI PUGLIESI
# ============================================================================

print("\n" + "="*80)
print("PARTE 5: PERFORMANCE CIRCOLI PUGLIESI")
print("="*80)

# Tesseramenti per circolo 2023 vs 2024
circoli_2023 = df_puglia[df_puglia['Anno'] == 2023].groupby(['MmbGroup', 'GrpName']).size().reset_index(name='Tess_2023')
circoli_2024 = df_puglia[df_puglia['Anno'] == 2024].groupby(['MmbGroup', 'GrpName']).size().reset_index(name='Tess_2024')

circoli_confronto = circoli_2023.merge(circoli_2024, on=['MmbGroup', 'GrpName'], how='outer', indicator=True).fillna(0)
circoli_confronto['Tess_2023'] = circoli_confronto['Tess_2023'].astype(int)
circoli_confronto['Tess_2024'] = circoli_confronto['Tess_2024'].astype(int)
circoli_confronto['Variazione'] = circoli_confronto['Tess_2024'] - circoli_confronto['Tess_2023']
circoli_confronto['Var_%'] = ((circoli_confronto['Tess_2024'] - circoli_confronto['Tess_2023']) / (circoli_confronto['Tess_2023'] + 1) * 100).round(1)

# Ordina per variazione
circoli_confronto = circoli_confronto.sort_values('Variazione', ascending=False)

print(f"\nCircoli Puglia: {len(circoli_confronto)}")

print("\n" + "-"*80)
print("TOP 10 CIRCOLI IN CRESCITA 2023→2024")
print("-"*80)

top10_crescita = circoli_confronto.head(10)
for idx, row in top10_crescita.iterrows():
    print(f"\n{row['GrpName']}")
    print(f"  2023: {row['Tess_2023']} → 2024: {row['Tess_2024']}")
    print(f"  Variazione: {row['Variazione']:+d} ({row['Var_%']:+.1f}%)")

print("\n" + "-"*80)
print("TOP 10 CIRCOLI IN DECLINO 2023→2024")
print("-"*80)

top10_declino = circoli_confronto.tail(10)
for idx, row in top10_declino.iterrows():
    print(f"\n{row['GrpName']}")
    print(f"  2023: {row['Tess_2023']} → 2024: {row['Tess_2024']}")
    print(f"  Variazione: {row['Variazione']:+d} ({row['Var_%']:+.1f}%)")

# Statistiche aggregate
n_crescita = len(circoli_confronto[circoli_confronto['Variazione'] > 0])
n_stabile = len(circoli_confronto[circoli_confronto['Variazione'] == 0])
n_declino = len(circoli_confronto[circoli_confronto['Variazione'] < 0])

print("\n" + "-"*80)
print("DISTRIBUZIONE CIRCOLI PER PERFORMANCE")
print("-"*80)

print(f"\nCircoli in crescita: {n_crescita} ({n_crescita/len(circoli_confronto)*100:.1f}%)")
print(f"Circoli stabili: {n_stabile} ({n_stabile/len(circoli_confronto)*100:.1f}%)")
print(f"Circoli in declino: {n_declino} ({n_declino/len(circoli_confronto)*100:.1f}%)")

# ============================================================================
# PARTE 6: CONFRONTO CON ALTRE REGIONI SUD
# ============================================================================

print("\n" + "="*80)
print("PARTE 6: CONFRONTO CON ALTRE REGIONI SUD")
print("="*80)

regioni_sud = ['PUG', 'CAM', 'CAB', 'SIC', 'SAR', 'BAS', 'MOL', 'ABR']

confronto_sud = []
for regione in regioni_sud:
    df_reg = df[df['GrpArea'] == regione]
    
    if len(df_reg) > 0:
        # Tesseramenti 2023 vs 2024
        tess_2023_reg = len(df_reg[df_reg['Anno'] == 2023])
        tess_2024_reg = len(df_reg[df_reg['Anno'] == 2024])
        var_reg = tess_2024_reg - tess_2023_reg
        var_pct_reg = (var_reg / tess_2023_reg * 100) if tess_2023_reg > 0 else 0
        
        # Retention 2023→2024
        gioc_2023_reg = set(df_reg[df_reg['Anno'] == 2023]['MmbCode'].unique())
        gioc_2024_reg = set(df_reg[df_reg['Anno'] == 2024]['MmbCode'].unique())
        ritess_reg = gioc_2023_reg.intersection(gioc_2024_reg)
        retention_reg = (len(ritess_reg) / len(gioc_2023_reg) * 100) if len(gioc_2023_reg) > 0 else 0
        
        # Gare medie 2024
        gare_2024_reg = df_reg[df_reg['Anno'] == 2024]['GareGiocate'].mean()
        
        confronto_sud.append({
            'Regione': regione,
            'Tess_2023': tess_2023_reg,
            'Tess_2024': tess_2024_reg,
            'Var_Assoluta': var_reg,
            'Var_%': var_pct_reg,
            'Retention_%': retention_reg,
            'Gare_Medie_2024': gare_2024_reg
        })

df_confronto_sud = pd.DataFrame(confronto_sud)
df_confronto_sud = df_confronto_sud.sort_values('Var_%', ascending=False)

print("\nConfronto Regioni Sud 2023→2024:")
print(df_confronto_sud.round(1).to_string(index=False))

# Posizione Puglia
pos_puglia = df_confronto_sud[df_confronto_sud['Regione'] == 'PUG'].index[0] + 1
print(f"\nPosizione Puglia: {pos_puglia}° su {len(df_confronto_sud)} regioni Sud")

# ============================================================================
# PARTE 7: SINTESI E VALUTAZIONE
# ============================================================================

print("\n" + "="*80)
print("PARTE 7: SINTESI E VALUTAZIONE MIGLIORAMENTO")
print("="*80)

# Calcolo score miglioramento
score = 0
max_score = 6

print("\nIndicatori miglioramento 2023→2024:")

# 1. Tesseramenti
if var_2023_2024 > 0:
    print(f"  ✅ Tesseramenti: +{int(var_2023_2024)} ({var_pct_2023_2024:+.1f}%)")
    score += 1
else:
    print(f"  🔴 Tesseramenti: {int(var_2023_2024)} ({var_pct_2023_2024:+.1f}%)")

# 2. Allievi
if 2023 in sb_anno.index and 2024 in sb_anno.index:
    if var_allievi > 0:
        print(f"  ✅ Allievi: +{int(var_allievi)} ({var_allievi_pct:+.1f}%)")
        score += 1
    else:
        print(f"  🔴 Allievi: {int(var_allievi)} ({var_allievi_pct:+.1f}%)")

# 3. Attività
if var_gare > 0:
    print(f"  ✅ Attività (gare): +{var_gare:.1f} ({var_gare_pct:+.1f}%)")
    score += 1
else:
    print(f"  🔴 Attività (gare): {var_gare:.1f} ({var_gare_pct:+.1f}%)")

# 4. Retention
if retention_rate > retention_nazionale:
    print(f"  ✅ Retention: {retention_rate:.1f}% (>{retention_nazionale:.1f}% nazionale)")
    score += 1
elif retention_rate > retention_nazionale - 2:
    print(f"  ⚠️ Retention: {retention_rate:.1f}% (~{retention_nazionale:.1f}% nazionale)")
    score += 0.5
else:
    print(f"  🔴 Retention: {retention_rate:.1f}% (<{retention_nazionale:.1f}% nazionale)")

# 5. Età allievi
if 2023 in sb_anno.index and 2024 in sb_anno.index:
    if var_eta < 0:
        print(f"  ✅ Età allievi: {var_eta:.1f} anni (più giovani)")
        score += 1
    else:
        print(f"  🔴 Età allievi: {var_eta:+.1f} anni (più anziani)")

# 6. Circoli in crescita
pct_crescita = n_crescita / len(circoli_confronto) * 100
if pct_crescita > 50:
    print(f"  ✅ Circoli in crescita: {pct_crescita:.1f}%")
    score += 1
elif pct_crescita > 30:
    print(f"  ⚠️ Circoli in crescita: {pct_crescita:.1f}%")
    score += 0.5
else:
    print(f"  🔴 Circoli in crescita: {pct_crescita:.1f}%")

print(f"\n{'='*80}")
print(f"SCORE MIGLIORAMENTO: {score:.1f}/{max_score}")
print(f"{'='*80}")

if score >= 5:
    valutazione = "✅ MIGLIORAMENTO SIGNIFICATIVO"
    colore = "verde"
elif score >= 3:
    valutazione = "⚠️ MIGLIORAMENTO MODERATO"
    colore = "giallo"
else:
    valutazione = "🔴 SITUAZIONE STABILE O IN PEGGIORAMENTO"
    colore = "rosso"

print(f"\nVALUTAZIONE FINALE: {valutazione}")

# ============================================================================
# SALVATAGGIO RISULTATI
# ============================================================================

print("\n" + "="*80)
print("SALVATAGGIO RISULTATI")
print("="*80)

# Salvataggio CSV
tess_anno.to_csv('/home/ubuntu/bridge_analysis/results/puglia_trend_anno.csv')
print("✓ Salvato: puglia_trend_anno.csv")

circoli_confronto.to_csv('/home/ubuntu/bridge_analysis/results/puglia_circoli_2023_2024.csv', index=False)
print("✓ Salvato: puglia_circoli_2023_2024.csv")

df_confronto_sud.to_csv('/home/ubuntu/bridge_analysis/results/confronto_sud_2023_2024.csv', index=False)
print("✓ Salvato: confronto_sud_2023_2024.csv")

# Salvataggio JSON summary
summary = {
    'tesseramenti': {
        '2023': int(tess_2023),
        '2024': int(tess_2024),
        'variazione': int(var_2023_2024),
        'variazione_pct': float(var_pct_2023_2024)
    },
    'allievi': {
        '2023': int(allievi_2023) if 2023 in sb_anno.index else 0,
        '2024': int(allievi_2024) if 2024 in sb_anno.index else 0,
        'variazione': int(var_allievi) if 2023 in sb_anno.index and 2024 in sb_anno.index else 0
    },
    'attivita': {
        'gare_2023': float(gare_2023),
        'gare_2024': float(gare_2024),
        'variazione': float(var_gare)
    },
    'retention': {
        'rate': float(retention_rate),
        'nazionale': float(retention_nazionale),
        'differenza': float(retention_rate - retention_nazionale)
    },
    'circoli': {
        'totale': len(circoli_confronto),
        'crescita': n_crescita,
        'declino': n_declino
    },
    'score': float(score),
    'valutazione': valutazione
}

with open('/home/ubuntu/bridge_analysis/results/puglia_summary.json', 'w') as f:
    json.dump(summary, f, indent=2)
print("✓ Salvato: puglia_summary.json")

# ============================================================================
# VISUALIZZAZIONI
# ============================================================================

print("\n" + "="*80)
print("GENERAZIONE VISUALIZZAZIONI")
print("="*80)

fig, axes = plt.subplots(2, 3, figsize=(20, 12))
fig.suptitle('Analisi Focus Puglia 2023-2024', fontsize=16, fontweight='bold')

# Grafico 1: Trend tesseramenti 2017-2024
ax1 = axes[0, 0]
tess_anno['Tesseramenti'].plot(kind='line', ax=ax1, marker='o', linewidth=2, markersize=8, color='steelblue')
ax1.set_title('Trend Tesseramenti Puglia 2017-2024', fontsize=12, fontweight='bold')
ax1.set_xlabel('Anno')
ax1.set_ylabel('Tesseramenti')
ax1.grid(True, alpha=0.3)
ax1.axvspan(2023, 2024, alpha=0.2, color='yellow', label='Focus 2023-2024')
ax1.legend()

# Grafico 2: Tesseramenti 2023 vs 2024
ax2 = axes[0, 1]
colors = ['green' if var_2023_2024 > 0 else 'red']
ax2.bar(['2023', '2024'], [tess_2023, tess_2024], color=['steelblue', colors[0]], edgecolor='black')
ax2.set_title('Tesseramenti 2023 vs 2024', fontsize=12, fontweight='bold')
ax2.set_ylabel('Tesseramenti')
ax2.grid(True, alpha=0.3, axis='y')
for i, v in enumerate([tess_2023, tess_2024]):
    ax2.text(i, v + 5, str(int(v)), ha='center', va='bottom', fontweight='bold')

# Grafico 3: Distribuzione attività 2024
ax3 = axes[0, 2]
dist_attivita.plot(kind='bar', ax=ax3, color='orange', edgecolor='black')
ax3.set_title('Distribuzione Attività 2024', fontsize=12, fontweight='bold')
ax3.set_xlabel('Categoria Attività')
ax3.set_ylabel('Numero Giocatori')
ax3.tick_params(axis='x', rotation=45)
ax3.grid(True, alpha=0.3, axis='y')

# Grafico 4: Retention per fascia età
ax4 = axes[1, 0]
retention_eta = []
fasce_eta = []
for fascia in ['<30', '30-40', '40-50', '50-60', '60-70', '70-80', '80-90', '90+']:
    gioc_fascia_2023 = set(df_puglia_2023[df_puglia_2023['FasciaEta'] == fascia]['MmbCode'].unique())
    if len(gioc_fascia_2023) > 0:
        ritess_fascia = gioc_fascia_2023.intersection(giocatori_2024)
        retention_fascia = len(ritess_fascia) / len(gioc_fascia_2023) * 100
        retention_eta.append(retention_fascia)
        fasce_eta.append(fascia)

ax4.bar(fasce_eta, retention_eta, color='forestgreen', edgecolor='black')
ax4.axhline(y=retention_nazionale, color='red', linestyle='--', linewidth=2, label=f'Nazionale: {retention_nazionale:.1f}%')
ax4.set_title('Retention per Fascia d\'Età 2023→2024', fontsize=12, fontweight='bold')
ax4.set_xlabel('Fascia d\'Età')
ax4.set_ylabel('Retention %')
ax4.tick_params(axis='x', rotation=45)
ax4.grid(True, alpha=0.3, axis='y')
ax4.legend()

# Grafico 5: Top circoli crescita/declino
ax5 = axes[1, 1]
top5_crescita = circoli_confronto.head(5)
top5_declino = circoli_confronto.tail(5)
circoli_top = pd.concat([top5_crescita, top5_declino])
colors_circoli = ['green' if x > 0 else 'red' for x in circoli_top['Variazione']]
ax5.barh(range(len(circoli_top)), circoli_top['Variazione'], color=colors_circoli, edgecolor='black')
ax5.set_yticks(range(len(circoli_top)))
ax5.set_yticklabels([name[:30] for name in circoli_top['GrpName']], fontsize=8)
ax5.set_title('Top 5 Crescita/Declino Circoli', fontsize=12, fontweight='bold')
ax5.set_xlabel('Variazione Tesseramenti')
ax5.axvline(x=0, color='black', linestyle='-', linewidth=1)
ax5.grid(True, alpha=0.3, axis='x')
ax5.invert_yaxis()

# Grafico 6: Confronto Regioni Sud
ax6 = axes[1, 2]
colors_sud = ['green' if x > 0 else 'red' for x in df_confronto_sud['Var_%']]
ax6.barh(range(len(df_confronto_sud)), df_confronto_sud['Var_%'], color=colors_sud, edgecolor='black')
ax6.set_yticks(range(len(df_confronto_sud)))
ax6.set_yticklabels(df_confronto_sud['Regione'])
ax6.set_title('Variazione % Tesseramenti Sud 2023→2024', fontsize=12, fontweight='bold')
ax6.set_xlabel('Variazione %')
ax6.axvline(x=0, color='black', linestyle='-', linewidth=1)
ax6.grid(True, alpha=0.3, axis='x')
ax6.invert_yaxis()

# Evidenzia Puglia
pos_pug = df_confronto_sud[df_confronto_sud['Regione'] == 'PUG'].index[0]
ax6.get_children()[pos_pug].set_linewidth(3)
ax6.get_children()[pos_pug].set_edgecolor('blue')

plt.tight_layout()
plt.savefig('/home/ubuntu/bridge_analysis/results/analisi_focus_puglia.png', 
            dpi=300, bbox_inches='tight')
print("✓ Salvato: analisi_focus_puglia.png")

print("\n" + "="*80)
print("ANALISI COMPLETATA!")
print("="*80)
