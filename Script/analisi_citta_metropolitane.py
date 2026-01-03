#!/usr/bin/env python3
"""
Analisi Andamento Città Metropolitane vs Capoluoghi vs Comuni
Confronto tesseramenti, attività, retention per dimensione centri urbani
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import json

print("="*80)
print("ANALISI CITTÀ METROPOLITANE VS CAPOLUOGHI VS COMUNI")
print("="*80)

# Caricamento dati
df = pd.read_csv('/home/ubuntu/bridge_analysis/dati_unificati.csv')

print(f"\nDati caricati: {len(df):,} tesseramenti")
print(f"Anni analizzati: {df['Anno'].min()}-{df['Anno'].max()}")

# ============================================================================
# DEFINIZIONE CITTÀ METROPOLITANE E CAPOLUOGHI
# ============================================================================

# 14 Città Metropolitane italiane
citta_metropolitane = [
    'ROMA', 'MILANO', 'NAPOLI', 'TORINO', 'PALERMO', 'GENOVA', 'BOLOGNA',
    'FIRENZE', 'BARI', 'CATANIA', 'VENEZIA', 'MESSINA', 'REGGIO CALABRIA', 'CAGLIARI'
]

# Capoluoghi di provincia (escludendo città metropolitane)
capoluoghi_provincia = [
    # Piemonte
    'ALESSANDRIA', 'ASTI', 'BIELLA', 'CUNEO', 'NOVARA', 'VERBANIA', 'VERCELLI',
    # Valle d'Aosta
    'AOSTA',
    # Lombardia
    'BERGAMO', 'BRESCIA', 'COMO', 'CREMONA', 'LECCO', 'LODI', 'MANTOVA', 
    'MONZA', 'PAVIA', 'SONDRIO', 'VARESE',
    # Trentino
    'TRENTO', 'BOLZANO',
    # Veneto
    'VERONA', 'VICENZA', 'BELLUNO', 'PADOVA', 'ROVIGO', 'TREVISO',
    # Friuli
    'UDINE', 'GORIZIA', 'PORDENONE', 'TRIESTE',
    # Liguria
    'IMPERIA', 'SAVONA', 'LA SPEZIA',
    # Emilia-Romagna
    'PIACENZA', 'PARMA', 'REGGIO EMILIA', 'MODENA', 'FERRARA', 'RAVENNA',
    'FORLI', 'CESENA', 'RIMINI',
    # Toscana
    'PISA', 'LIVORNO', 'LUCCA', 'PISTOIA', 'AREZZO', 'SIENA', 'GROSSETO',
    'PRATO', 'MASSA', 'CARRARA',
    # Umbria
    'PERUGIA', 'TERNI',
    # Marche
    'ANCONA', 'PESARO', 'URBINO', 'MACERATA', 'ASCOLI PICENO', 'FERMO',
    # Lazio
    'VITERBO', 'RIETI', 'LATINA', 'FROSINONE',
    # Abruzzo
    'L\'AQUILA', 'TERAMO', 'PESCARA', 'CHIETI',
    # Molise
    'CAMPOBASSO', 'ISERNIA',
    # Campania
    'CASERTA', 'BENEVENTO', 'AVELLINO', 'SALERNO',
    # Puglia
    'FOGGIA', 'BRINDISI', 'TARANTO', 'LECCE', 'BARLETTA', 'ANDRIA', 'TRANI',
    # Basilicata
    'POTENZA', 'MATERA',
    # Calabria
    'COSENZA', 'CATANZARO', 'CROTONE', 'VIBO VALENTIA',
    # Sicilia
    'TRAPANI', 'AGRIGENTO', 'CALTANISSETTA', 'ENNA', 'RAGUSA', 'SIRACUSA',
    # Sardegna
    'SASSARI', 'NUORO', 'ORISTANO', 'SUD SARDEGNA'
]

print("\n" + "="*80)
print("CLASSIFICAZIONE COMUNI")
print("="*80)

# Funzione per classificare comune
def classifica_comune(nome_comune):
    if pd.isna(nome_comune):
        return 'Sconosciuto'
    
    nome_upper = str(nome_comune).upper()
    
    # Città metropolitane
    for citta in citta_metropolitane:
        if citta in nome_upper:
            return 'Città Metropolitana'
    
    # Capoluoghi
    for capoluogo in capoluoghi_provincia:
        if capoluogo in nome_upper:
            return 'Capoluogo Provincia'
    
    # Altri comuni
    return 'Comune Non Capoluogo'

# Applica classificazione
df['TipoComune'] = df['GrpCity'].apply(classifica_comune)

# Verifica classificazione
print("\nDistribuzione tesseramenti per tipo comune:")
dist_tipo = df.groupby('TipoComune').size().sort_values(ascending=False)
print(dist_tipo)
print(f"\nPercentuali:")
print((dist_tipo / len(df) * 100).round(1))

# ============================================================================
# PARTE 1: TESSERAMENTI PER TIPO COMUNE (2024)
# ============================================================================

print("\n" + "="*80)
print("PARTE 1: TESSERAMENTI PER TIPO COMUNE (2024)")
print("="*80)

df_2024 = df[df['Anno'] == 2024].copy()

stats_tipo = df_2024.groupby('TipoComune').agg({
    'MmbCode': 'count',
    'Anni': 'mean',
    'GareGiocate': 'mean',
    'PuntiTotali': 'mean',
    'MmbGroup': 'nunique'
}).rename(columns={
    'MmbCode': 'Tesserati',
    'Anni': 'Eta_Media',
    'GareGiocate': 'Gare_Medie',
    'PuntiTotali': 'Punti_Medi',
    'MmbGroup': 'N_Circoli'
}).round(1)

stats_tipo['%_Tesserati'] = (stats_tipo['Tesserati'] / stats_tipo['Tesserati'].sum() * 100).round(1)
stats_tipo['Tesserati_per_Circolo'] = (stats_tipo['Tesserati'] / stats_tipo['N_Circoli']).round(1)

print("\nStatistiche per tipo comune (2024):")
print(stats_tipo.to_string())

# ============================================================================
# PARTE 2: TREND TEMPORALE PER TIPO COMUNE (2017-2024)
# ============================================================================

print("\n" + "="*80)
print("PARTE 2: TREND TEMPORALE PER TIPO COMUNE (2017-2024)")
print("="*80)

trend_tipo = df.groupby(['Anno', 'TipoComune']).size().unstack(fill_value=0)

print("\nTesseramenti per anno e tipo comune:")
print(trend_tipo.to_string())

# Variazioni 2017-2024
var_2017_2024 = pd.DataFrame({
    '2017': trend_tipo.loc[2017],
    '2024': trend_tipo.loc[2024],
    'Variazione': trend_tipo.loc[2024] - trend_tipo.loc[2017],
    'Var_%': ((trend_tipo.loc[2024] - trend_tipo.loc[2017]) / trend_tipo.loc[2017] * 100).round(1)
})

print("\nVariazioni 2017→2024:")
print(var_2017_2024.to_string())

# ============================================================================
# PARTE 3: TOP CITTÀ METROPOLITANE
# ============================================================================

print("\n" + "="*80)
print("PARTE 3: TOP CITTÀ METROPOLITANE")
print("="*80)

df_metro_2024 = df_2024[df_2024['TipoComune'] == 'Città Metropolitana'].copy()

# Identifica città specifica
def identifica_citta_metro(nome):
    if pd.isna(nome):
        return 'Sconosciuta'
    nome_upper = str(nome).upper()
    for citta in citta_metropolitane:
        if citta in nome_upper:
            return citta.title()
    return 'Altra'

df_metro_2024['Citta'] = df_metro_2024['GrpCity'].apply(identifica_citta_metro)

stats_metro = df_metro_2024.groupby('Citta').agg({
    'MmbCode': 'count',
    'Anni': 'mean',
    'GareGiocate': 'mean',
    'PuntiTotali': 'mean',
    'MmbGroup': 'nunique'
}).rename(columns={
    'MmbCode': 'Tesserati',
    'Anni': 'Eta_Media',
    'GareGiocate': 'Gare_Medie',
    'PuntiTotali': 'Punti_Medi',
    'MmbGroup': 'N_Circoli'
}).round(1)

stats_metro = stats_metro.sort_values('Tesserati', ascending=False)
stats_metro['%_Metro'] = (stats_metro['Tesserati'] / stats_metro['Tesserati'].sum() * 100).round(1)

print("\nTop Città Metropolitane (2024):")
print(stats_metro.to_string())

# ============================================================================
# PARTE 4: RETENTION PER TIPO COMUNE (2023→2024)
# ============================================================================

print("\n" + "="*80)
print("PARTE 4: RETENTION PER TIPO COMUNE (2023→2024)")
print("="*80)

df_2023 = df[df['Anno'] == 2023].copy()
df_2023['TipoComune'] = df_2023['GrpCity'].apply(classifica_comune)

retention_tipo = []

for tipo in ['Città Metropolitana', 'Capoluogo Provincia', 'Comune Non Capoluogo']:
    gioc_2023 = set(df_2023[df_2023['TipoComune'] == tipo]['MmbCode'].unique())
    gioc_2024 = set(df_2024[df_2024['TipoComune'] == tipo]['MmbCode'].unique())
    
    if len(gioc_2023) > 0:
        ritess = gioc_2023.intersection(gioc_2024)
        retention = len(ritess) / len(gioc_2023) * 100
        churn = 100 - retention
        nuovi = len(gioc_2024 - gioc_2023)
        
        retention_tipo.append({
            'TipoComune': tipo,
            'Giocatori_2023': len(gioc_2023),
            'Ritesserati': len(ritess),
            'Retention_%': round(retention, 1),
            'Churn_%': round(churn, 1),
            'Nuovi_2024': nuovi
        })

df_retention = pd.DataFrame(retention_tipo)

print("\nRetention per tipo comune (2023→2024):")
print(df_retention.to_string(index=False))

# ============================================================================
# PARTE 5: CONFRONTO FASCE ETÀ PER TIPO COMUNE
# ============================================================================

print("\n" + "="*80)
print("PARTE 5: CONFRONTO FASCE ETÀ PER TIPO COMUNE")
print("="*80)

df_2024['FasciaEta'] = pd.cut(
    df_2024['Anni'],
    bins=[0, 18, 30, 40, 50, 60, 70, 80, 90, 120],
    labels=['<18', '18-30', '30-40', '40-50', '50-60', '60-70', '70-80', '80-90', '90+']
)

dist_eta_tipo = pd.crosstab(
    df_2024['TipoComune'],
    df_2024['FasciaEta'],
    normalize='index'
) * 100

dist_eta_tipo = dist_eta_tipo.round(1)

print("\nDistribuzione % fasce età per tipo comune:")
print(dist_eta_tipo.to_string())

# Giovani per tipo
giovani_tipo = df_2024[df_2024['Anni'] < 40].groupby('TipoComune').size().reset_index(name='N_Giovani')
giovani_tipo = giovani_tipo.merge(
    stats_tipo[['Tesserati']].reset_index(),
    on='TipoComune'
)
giovani_tipo['%_Giovani'] = (giovani_tipo['N_Giovani'] / giovani_tipo['Tesserati'] * 100).round(1)

print("\nGiovani (<40) per tipo comune:")
print(giovani_tipo.to_string(index=False))

# ============================================================================
# PARTE 6: CRESCITA/DECLINO PER TIPO COMUNE
# ============================================================================

print("\n" + "="*80)
print("PARTE 6: CRESCITA/DECLINO PER TIPO COMUNE (2017-2024)")
print("="*80)

# Calcolo CAGR (Compound Annual Growth Rate)
cagr_tipo = []

for tipo in trend_tipo.columns:
    val_2017 = trend_tipo.loc[2017, tipo]
    val_2024 = trend_tipo.loc[2024, tipo]
    
    if val_2017 > 0:
        cagr = ((val_2024 / val_2017) ** (1/7) - 1) * 100
        
        cagr_tipo.append({
            'TipoComune': tipo,
            '2017': val_2017,
            '2024': val_2024,
            'Variazione': val_2024 - val_2017,
            'Var_%': round((val_2024 - val_2017) / val_2017 * 100, 1),
            'CAGR_%': round(cagr, 2)
        })

df_cagr = pd.DataFrame(cagr_tipo)
df_cagr = df_cagr.sort_values('CAGR_%', ascending=False)

print("\nCrescita/Declino per tipo comune:")
print(df_cagr.to_string(index=False))

# ============================================================================
# PARTE 7: DENSITÀ CIRCOLI PER TIPO COMUNE
# ============================================================================

print("\n" + "="*80)
print("PARTE 7: DENSITÀ CIRCOLI PER TIPO COMUNE")
print("="*80)

densita = stats_tipo[['N_Circoli', 'Tesserati', 'Tesserati_per_Circolo']].copy()
densita = densita.sort_values('Tesserati_per_Circolo', ascending=False)

print("\nDensità circoli per tipo comune:")
print(densita.to_string())

# ============================================================================
# PARTE 8: CONFRONTO CITTÀ METROPOLITANE SPECIFICHE
# ============================================================================

print("\n" + "="*80)
print("PARTE 8: CONFRONTO TREND CITTÀ METROPOLITANE SPECIFICHE")
print("="*80)

# Top 5 città metropolitane per tesserati
top5_citta = stats_metro.nlargest(5, 'Tesserati').index.tolist()

# Trend per città
df_metro_all = df[df['TipoComune'] == 'Città Metropolitana'].copy()
df_metro_all['Citta'] = df_metro_all['GrpCity'].apply(identifica_citta_metro)

trend_citta = df_metro_all[df_metro_all['Citta'].isin(top5_citta)].groupby(['Anno', 'Citta']).size().unstack(fill_value=0)

print(f"\nTrend Top 5 Città Metropolitane (2017-2024):")
print(trend_citta.to_string())

# Variazioni
var_citta = pd.DataFrame({
    '2017': trend_citta.loc[2017],
    '2024': trend_citta.loc[2024],
    'Variazione': trend_citta.loc[2024] - trend_citta.loc[2017],
    'Var_%': ((trend_citta.loc[2024] - trend_citta.loc[2017]) / trend_citta.loc[2017] * 100).round(1)
})

print("\nVariazioni Top 5 Città (2017→2024):")
print(var_citta.to_string())

# ============================================================================
# SALVATAGGIO RISULTATI
# ============================================================================

print("\n" + "="*80)
print("SALVATAGGIO RISULTATI")
print("="*80)

# Salvataggio CSV
stats_tipo.to_csv('/home/ubuntu/bridge_analysis/results/statistiche_tipo_comune.csv')
print("✓ Salvato: statistiche_tipo_comune.csv")

trend_tipo.to_csv('/home/ubuntu/bridge_analysis/results/trend_tipo_comune.csv')
print("✓ Salvato: trend_tipo_comune.csv")

stats_metro.to_csv('/home/ubuntu/bridge_analysis/results/statistiche_citta_metropolitane.csv')
print("✓ Salvato: statistiche_citta_metropolitane.csv")

df_retention.to_csv('/home/ubuntu/bridge_analysis/results/retention_tipo_comune.csv', index=False)
print("✓ Salvato: retention_tipo_comune.csv")

dist_eta_tipo.to_csv('/home/ubuntu/bridge_analysis/results/distribuzione_eta_tipo_comune.csv')
print("✓ Salvato: distribuzione_eta_tipo_comune.csv")

# ============================================================================
# VISUALIZZAZIONI
# ============================================================================

print("\n" + "="*80)
print("GENERAZIONE VISUALIZZAZIONI")
print("="*80)

fig, axes = plt.subplots(2, 3, figsize=(22, 14))
fig.suptitle('Analisi Città Metropolitane vs Capoluoghi vs Comuni', fontsize=16, fontweight='bold')

# Grafico 1: Distribuzione tesserati per tipo comune 2024
ax1 = axes[0, 0]
colors_tipo = ['#e74c3c', '#3498db', '#2ecc71']
wedges, texts, autotexts = ax1.pie(
    stats_tipo['Tesserati'],
    labels=stats_tipo.index,
    autopct='%1.1f%%',
    colors=colors_tipo,
    startangle=90
)
ax1.set_title('Distribuzione Tesserati per Tipo Comune (2024)', fontsize=11, fontweight='bold')

# Grafico 2: Trend temporale per tipo comune
ax2 = axes[0, 1]
for col in trend_tipo.columns:
    ax2.plot(trend_tipo.index, trend_tipo[col], marker='o', linewidth=2, label=col)
ax2.set_xlabel('Anno')
ax2.set_ylabel('Tesserati')
ax2.set_title('Trend Tesseramenti per Tipo Comune (2017-2024)', fontsize=11, fontweight='bold')
ax2.legend(fontsize=9)
ax2.grid(True, alpha=0.3)

# Grafico 3: Età media per tipo comune
ax3 = axes[0, 2]
ax3.bar(range(len(stats_tipo)), stats_tipo['Eta_Media'], color=colors_tipo, edgecolor='black')
ax3.set_xticks(range(len(stats_tipo)))
ax3.set_xticklabels(stats_tipo.index, rotation=15, ha='right')
ax3.set_ylabel('Età Media')
ax3.set_title('Età Media per Tipo Comune (2024)', fontsize=11, fontweight='bold')
ax3.axhline(y=df_2024['Anni'].mean(), color='red', linestyle='--', linewidth=2, label=f'Media Generale: {df_2024["Anni"].mean():.1f}')
ax3.legend()
ax3.grid(True, alpha=0.3, axis='y')

# Grafico 4: Retention per tipo comune
ax4 = axes[1, 0]
colors_ret = ['green' if x > 90 else 'orange' if x > 85 else 'red' for x in df_retention['Retention_%']]
ax4.barh(range(len(df_retention)), df_retention['Retention_%'], color=colors_ret, edgecolor='black')
ax4.set_yticks(range(len(df_retention)))
ax4.set_yticklabels(df_retention['TipoComune'])
ax4.set_xlabel('Retention %')
ax4.set_title('Retention Rate per Tipo Comune (2023→2024)', fontsize=11, fontweight='bold')
ax4.axvline(x=91.8, color='blue', linestyle='--', linewidth=2, label='Media Nazionale: 91.8%')
ax4.legend()
ax4.grid(True, alpha=0.3, axis='x')
ax4.invert_yaxis()

# Grafico 5: Top 10 Città Metropolitane
ax5 = axes[1, 1]
top10_metro = stats_metro.nlargest(10, 'Tesserati')
ax5.barh(range(len(top10_metro)), top10_metro['Tesserati'], color='steelblue', edgecolor='black')
ax5.set_yticks(range(len(top10_metro)))
ax5.set_yticklabels(top10_metro.index, fontsize=9)
ax5.set_xlabel('Tesserati')
ax5.set_title('Top 10 Città Metropolitane (2024)', fontsize=11, fontweight='bold')
ax5.grid(True, alpha=0.3, axis='x')
ax5.invert_yaxis()

# Grafico 6: Distribuzione giovani per tipo comune
ax6 = axes[1, 2]
ax6.bar(range(len(giovani_tipo)), giovani_tipo['%_Giovani'], color=colors_tipo, edgecolor='black')
ax6.set_xticks(range(len(giovani_tipo)))
ax6.set_xticklabels(giovani_tipo['TipoComune'], rotation=15, ha='right')
ax6.set_ylabel('% Giovani (<40)')
ax6.set_title('% Giovani (<40) per Tipo Comune (2024)', fontsize=11, fontweight='bold')
ax6.grid(True, alpha=0.3, axis='y')

plt.tight_layout()
plt.savefig('/home/ubuntu/bridge_analysis/results/analisi_citta_metropolitane.png', 
            dpi=300, bbox_inches='tight')
print("✓ Salvato: analisi_citta_metropolitane.png")

print("\n" + "="*80)
print("ANALISI COMPLETATA!")
print("="*80)
