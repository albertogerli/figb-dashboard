#!/usr/bin/env python3
"""
Script per la creazione di visualizzazioni per la dashboard
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# Configurazione
sns.set_style("whitegrid")
sns.set_palette("husl")
plt.rcParams['figure.figsize'] = (14, 8)
plt.rcParams['font.size'] = 10

# Creazione directory per grafici
Path('/home/ubuntu/bridge_analysis/charts').mkdir(exist_ok=True)

# Caricamento dati
print("Caricamento dati...")
df = pd.read_csv('/home/ubuntu/bridge_analysis/dati_unificati.csv')

# Creazione fasce d'età
df['FasciaEta'] = pd.cut(df['Anni'], 
                         bins=[0, 18, 30, 40, 50, 60, 70, 80, 90, 120],
                         labels=['<18', '18-30', '30-40', '40-50', '50-60', '60-70', '70-80', '80-90', '90+'])

# ============================================================================
# 1. TREND TESSERAMENTI NEL TEMPO
# ============================================================================
print("Creazione grafico 1: Trend tesseramenti...")
yearly_counts = df.groupby('Anno')['MmbCode'].count()

fig, ax = plt.subplots(figsize=(14, 8))
ax.plot(yearly_counts.index, yearly_counts.values, marker='o', linewidth=3, markersize=10, color='#2E86AB')
ax.fill_between(yearly_counts.index, yearly_counts.values, alpha=0.3, color='#2E86AB')

for i, v in enumerate(yearly_counts.values):
    ax.text(yearly_counts.index[i], v + 300, f'{int(v):,}', ha='center', fontsize=11, fontweight='bold')

ax.set_xlabel('Anno', fontsize=12, fontweight='bold')
ax.set_ylabel('Numero Tesserati', fontsize=12, fontweight='bold')
ax.set_title('Evoluzione Tesseramenti FIGB 2017-2024', fontsize=16, fontweight='bold', pad=20)
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('/home/ubuntu/bridge_analysis/charts/01_trend_tesseramenti.png', dpi=150, bbox_inches='tight')
plt.close()

# ============================================================================
# 2. DISTRIBUZIONE PER REGIONE (2024)
# ============================================================================
print("Creazione grafico 2: Distribuzione regionale...")
regional_2024 = df[df['Anno'] == 2024].groupby('GrpArea')['MmbCode'].count().sort_values(ascending=True).tail(15)

fig, ax = plt.subplots(figsize=(14, 10))
bars = ax.barh(range(len(regional_2024)), regional_2024.values, color='#A23B72')

for i, v in enumerate(regional_2024.values):
    ax.text(v + 50, i, f'{int(v):,}', va='center', fontsize=10, fontweight='bold')

ax.set_yticks(range(len(regional_2024)))
ax.set_yticklabels(regional_2024.index, fontsize=11)
ax.set_xlabel('Numero Tesserati', fontsize=12, fontweight='bold')
ax.set_title('Top 15 Regioni per Tesserati - 2024', fontsize=16, fontweight='bold', pad=20)
ax.grid(True, alpha=0.3, axis='x')
plt.tight_layout()
plt.savefig('/home/ubuntu/bridge_analysis/charts/02_distribuzione_regionale.png', dpi=150, bbox_inches='tight')
plt.close()

# ============================================================================
# 3. PIRAMIDE DELL'ETÀ PER SESSO (2024)
# ============================================================================
print("Creazione grafico 3: Piramide età...")
age_sex_2024 = df[df['Anno'] == 2024].groupby(['FasciaEta', 'MmbSex'])['MmbCode'].count().unstack(fill_value=0)

# Riordina le fasce d'età
age_order = ['<18', '18-30', '30-40', '40-50', '50-60', '60-70', '70-80', '80-90', '90+']
age_sex_2024 = age_sex_2024.reindex(age_order)

fig, ax = plt.subplots(figsize=(14, 8))
y_pos = np.arange(len(age_sex_2024))

# Maschi a sinistra (negativi)
ax.barh(y_pos, -age_sex_2024['M'], color='#2E86AB', label='Maschi', alpha=0.8)
# Femmine a destra (positivi)
ax.barh(y_pos, age_sex_2024['F'], color='#F18F01', label='Femmine', alpha=0.8)

# Etichette
for i, (m, f) in enumerate(zip(age_sex_2024['M'], age_sex_2024['F'])):
    ax.text(-m/2, i, f'{int(m):,}', ha='center', va='center', fontsize=9, fontweight='bold', color='white')
    ax.text(f/2, i, f'{int(f):,}', ha='center', va='center', fontsize=9, fontweight='bold', color='white')

ax.set_yticks(y_pos)
ax.set_yticklabels(age_sex_2024.index, fontsize=11)
ax.set_xlabel('Numero Tesserati', fontsize=12, fontweight='bold')
ax.set_title('Distribuzione per Fascia d\'Età e Sesso - 2024', fontsize=16, fontweight='bold', pad=20)
ax.legend(loc='upper right', fontsize=11)

# Formattazione asse x
max_val = max(age_sex_2024['M'].max(), age_sex_2024['F'].max())
ax.set_xlim(-max_val*1.2, max_val*1.2)
ax.axvline(0, color='black', linewidth=0.8)
ax.grid(True, alpha=0.3, axis='x')

plt.tight_layout()
plt.savefig('/home/ubuntu/bridge_analysis/charts/03_piramide_eta.png', dpi=150, bbox_inches='tight')
plt.close()

# ============================================================================
# 4. RETENTION RATE NEL TEMPO
# ============================================================================
print("Creazione grafico 4: Retention rate...")
retention_df = pd.read_csv('/home/ubuntu/bridge_analysis/results/retention_rate.csv')

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7))

# Grafico 1: Retention Rate
ax1.plot(retention_df['Anno'], retention_df['RetentionRate_%'], marker='o', linewidth=3, 
         markersize=10, color='#06A77D')
ax1.fill_between(retention_df['Anno'], retention_df['RetentionRate_%'], alpha=0.3, color='#06A77D')

for i, v in enumerate(retention_df['RetentionRate_%']):
    ax1.text(retention_df['Anno'].iloc[i], v + 1.5, f'{v:.1f}%', ha='center', fontsize=10, fontweight='bold')

ax1.set_xlabel('Anno', fontsize=12, fontweight='bold')
ax1.set_ylabel('Retention Rate (%)', fontsize=12, fontweight='bold')
ax1.set_title('Tasso di Ritesseramento Anno su Anno', fontsize=14, fontweight='bold', pad=15)
ax1.grid(True, alpha=0.3)
ax1.set_ylim(60, 95)

# Grafico 2: Persi vs Nuovi
x = np.arange(len(retention_df))
width = 0.35

bars1 = ax2.bar(x - width/2, retention_df['Persi'], width, label='Persi', color='#D62828', alpha=0.8)
bars2 = ax2.bar(x + width/2, retention_df['Nuovi_AnnoSuccessivo'], width, label='Nuovi', color='#06A77D', alpha=0.8)

ax2.set_xlabel('Anno', fontsize=12, fontweight='bold')
ax2.set_ylabel('Numero Giocatori', fontsize=12, fontweight='bold')
ax2.set_title('Giocatori Persi vs Nuovi Acquisiti', fontsize=14, fontweight='bold', pad=15)
ax2.set_xticks(x)
ax2.set_xticklabels(retention_df['Anno'])
ax2.legend(fontsize=11)
ax2.grid(True, alpha=0.3, axis='y')

plt.tight_layout()
plt.savefig('/home/ubuntu/bridge_analysis/charts/04_retention_rate.png', dpi=150, bbox_inches='tight')
plt.close()

# ============================================================================
# 5. RETENTION PER FASCIA D'ETÀ
# ============================================================================
print("Creazione grafico 5: Retention per età...")
retention_age_df = pd.read_csv('/home/ubuntu/bridge_analysis/results/retention_per_eta.csv')

# Media retention per fascia d'età
avg_retention_age = retention_age_df.groupby('FasciaEta')['RetentionRate_%'].mean().sort_values(ascending=True)

fig, ax = plt.subplots(figsize=(14, 8))
bars = ax.barh(range(len(avg_retention_age)), avg_retention_age.values, color='#F77F00')

for i, v in enumerate(avg_retention_age.values):
    ax.text(v + 1, i, f'{v:.1f}%', va='center', fontsize=10, fontweight='bold')

ax.set_yticks(range(len(avg_retention_age)))
ax.set_yticklabels(avg_retention_age.index, fontsize=11)
ax.set_xlabel('Retention Rate Medio (%)', fontsize=12, fontweight='bold')
ax.set_title('Tasso di Ritesseramento Medio per Fascia d\'Età (2017-2023)', fontsize=16, fontweight='bold', pad=20)
ax.grid(True, alpha=0.3, axis='x')
ax.set_xlim(0, 100)

plt.tight_layout()
plt.savefig('/home/ubuntu/bridge_analysis/charts/05_retention_per_eta.png', dpi=150, bbox_inches='tight')
plt.close()

# ============================================================================
# 6. DISTRIBUZIONE TIPOLOGIE TESSERA
# ============================================================================
print("Creazione grafico 6: Tipologie tessera...")
membership_2024 = df[df['Anno'] == 2024].groupby('MbtDesc')['MmbCode'].count().sort_values(ascending=False).head(8)

fig, ax = plt.subplots(figsize=(14, 8))
colors = sns.color_palette("husl", len(membership_2024))
wedges, texts, autotexts = ax.pie(membership_2024.values, labels=membership_2024.index, autopct='%1.1f%%',
                                    colors=colors, startangle=90, textprops={'fontsize': 11, 'fontweight': 'bold'})

for autotext in autotexts:
    autotext.set_color('white')
    autotext.set_fontsize(10)

ax.set_title('Distribuzione Tipologie Tessera - 2024', fontsize=16, fontweight='bold', pad=20)

plt.tight_layout()
plt.savefig('/home/ubuntu/bridge_analysis/charts/06_tipologie_tessera.png', dpi=150, bbox_inches='tight')
plt.close()

# ============================================================================
# 7. HEATMAP CATEGORIE PER ANNO
# ============================================================================
print("Creazione grafico 7: Heatmap categorie...")
cat_yearly = df.groupby(['Anno', 'CatLabel'])['MmbCode'].count().unstack(fill_value=0)

# Seleziona solo le top 15 categorie
top_cats = df.groupby('CatLabel')['MmbCode'].count().nlargest(15).index
cat_yearly_top = cat_yearly[top_cats]

fig, ax = plt.subplots(figsize=(16, 10))
sns.heatmap(cat_yearly_top.T, annot=True, fmt='d', cmap='YlOrRd', cbar_kws={'label': 'Numero Tesserati'},
            linewidths=0.5, ax=ax)

ax.set_xlabel('Anno', fontsize=12, fontweight='bold')
ax.set_ylabel('Categoria', fontsize=12, fontweight='bold')
ax.set_title('Evoluzione Tesseramenti per Categoria (Top 15)', fontsize=16, fontweight='bold', pad=20)

plt.tight_layout()
plt.savefig('/home/ubuntu/bridge_analysis/charts/07_heatmap_categorie.png', dpi=150, bbox_inches='tight')
plt.close()

# ============================================================================
# 8. MANCATI RITESSERAMENTI PER FASCIA D'ETÀ
# ============================================================================
print("Creazione grafico 8: Mancati ritesseramenti...")
churn_df = pd.read_csv('/home/ubuntu/bridge_analysis/results/mancati_ritesseramenti.csv')

# Aggregazione per anno e fascia d'età
churn_age = churn_df.groupby(['Anno', 'FasciaEta'])['NumeroPersi'].sum().unstack(fill_value=0)

# Riordina le fasce d'età
age_order = ['<18', '18-30', '30-40', '40-50', '50-60', '60-70', '70-80', '80-90', '90+']
churn_age = churn_age[[col for col in age_order if col in churn_age.columns]]

fig, ax = plt.subplots(figsize=(14, 8))
churn_age.plot(kind='bar', stacked=True, ax=ax, colormap='Spectral', width=0.8)

ax.set_xlabel('Anno', fontsize=12, fontweight='bold')
ax.set_ylabel('Numero Giocatori Persi', fontsize=12, fontweight='bold')
ax.set_title('Distribuzione Mancati Ritesseramenti per Fascia d\'Età', fontsize=16, fontweight='bold', pad=20)
ax.legend(title='Fascia Età', bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=10)
ax.grid(True, alpha=0.3, axis='y')
plt.xticks(rotation=0)

plt.tight_layout()
plt.savefig('/home/ubuntu/bridge_analysis/charts/08_churn_per_eta.png', dpi=150, bbox_inches='tight')
plt.close()

# ============================================================================
# 9. GARE GIOCATE PER FASCIA D'ETÀ
# ============================================================================
print("Creazione grafico 9: Gare per età...")
games_age_2024 = df[df['Anno'] == 2024].groupby('FasciaEta')['GareGiocate'].mean().reindex(age_order)

fig, ax = plt.subplots(figsize=(14, 8))
bars = ax.bar(range(len(games_age_2024)), games_age_2024.values, color='#6A4C93', alpha=0.8)

for i, v in enumerate(games_age_2024.values):
    ax.text(i, v + 1, f'{v:.1f}', ha='center', fontsize=10, fontweight='bold')

ax.set_xticks(range(len(games_age_2024)))
ax.set_xticklabels(games_age_2024.index, fontsize=11)
ax.set_xlabel('Fascia d\'Età', fontsize=12, fontweight='bold')
ax.set_ylabel('Numero Medio Gare Giocate', fontsize=12, fontweight='bold')
ax.set_title('Attività Media per Fascia d\'Età - 2024', fontsize=16, fontweight='bold', pad=20)
ax.grid(True, alpha=0.3, axis='y')

plt.tight_layout()
plt.savefig('/home/ubuntu/bridge_analysis/charts/09_gare_per_eta.png', dpi=150, bbox_inches='tight')
plt.close()

# ============================================================================
# 10. TREND REGIONALE NEL TEMPO (TOP 5)
# ============================================================================
print("Creazione grafico 10: Trend regionale...")
regional_yearly = df.groupby(['Anno', 'GrpArea'])['MmbCode'].count().unstack(fill_value=0)

# Top 5 regioni nel 2024
top5_regions = regional_yearly.loc[2024].nlargest(5).index

fig, ax = plt.subplots(figsize=(14, 8))
for region in top5_regions:
    ax.plot(regional_yearly.index, regional_yearly[region], marker='o', linewidth=2.5, 
            markersize=8, label=region)

ax.set_xlabel('Anno', fontsize=12, fontweight='bold')
ax.set_ylabel('Numero Tesserati', fontsize=12, fontweight='bold')
ax.set_title('Evoluzione Tesseramenti - Top 5 Regioni', fontsize=16, fontweight='bold', pad=20)
ax.legend(fontsize=11, loc='best')
ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('/home/ubuntu/bridge_analysis/charts/10_trend_regionale.png', dpi=150, bbox_inches='tight')
plt.close()

print("\n✓ Tutte le visualizzazioni create con successo")
print(f"✓ Grafici salvati in: /home/ubuntu/bridge_analysis/charts/")
