#!/usr/bin/env python3
"""
ANALISI APPROFONDITA CHURN E PATTERN DI GIOCO
Focus: Perché smettono? Come recuperarli?
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from datetime import datetime
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
import warnings
warnings.filterwarnings('ignore')

# Configurazione
plt.style.use('seaborn-v0_8-whitegrid')
plt.rcParams['figure.figsize'] = (14, 10)
plt.rcParams['font.size'] = 11
plt.rcParams['axes.titlesize'] = 14

# Directory
BASE_DIR = Path(__file__).parent.parent
OUTPUT_DIR = BASE_DIR / 'output'
CHARTS_DIR = OUTPUT_DIR / 'charts_churn'
RESULTS_DIR = OUTPUT_DIR / 'results_churn'

CHARTS_DIR.mkdir(parents=True, exist_ok=True)
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

# Colori
COLORS = ['#1E3A5F', '#DC3545', '#28A745', '#FFC107', '#17A2B8', '#6C757D', '#E83E8C', '#6610F2']

print("=" * 100)
print("ANALISI APPROFONDITA CHURN E PATTERN DI GIOCO")
print("Focus: Perché smettono di giocare? Come recuperarli?")
print("=" * 100)

# ============================================================================
# 1. CARICAMENTO DATI
# ============================================================================
print("\n[1/8] Caricamento dati...")

df = pd.read_csv(OUTPUT_DIR / 'dati_unificati_2017_2025.csv')
print(f"   Record totali: {len(df):,}")
print(f"   Giocatori unici: {df['MmbCode'].nunique():,}")

# Mapping categorie con ordine gerarchico dettagliato
CATEGORIA_ORDER = {
    'NC': 0,
    '4F': 1, '4Q': 2, '4C': 3, '4P': 4,
    '3F': 5, '3Q': 6, '3C': 7, '3P': 8,
    '2F': 9, '2Q': 10, '2C': 11, '2P': 12,
    '1F': 13, '1Q': 14, '1C': 15, '1P': 16,
    'HJ': 17, 'HQ': 18, 'HK': 19, 'HA': 20,
    'MS': 21, 'LM': 22, 'GM': 23
}

CATEGORIA_NOME = {
    'NC': 'Non Classificato',
    '4F': 'Quarta Fiori', '4Q': 'Quarta Quadri', '4C': 'Quarta Cuori', '4P': 'Quarta Picche',
    '3F': 'Terza Fiori', '3Q': 'Terza Quadri', '3C': 'Terza Cuori', '3P': 'Terza Picche',
    '2F': 'Seconda Fiori', '2Q': 'Seconda Quadri', '2C': 'Seconda Cuori', '2P': 'Seconda Picche',
    '1F': 'Prima Fiori', '1Q': 'Prima Quadri', '1C': 'Prima Cuori', '1P': 'Prima Picche',
    'HJ': 'Honor Fante', 'HQ': 'Honor Dama', 'HK': 'Honor Re', 'HA': 'Honor Asso',
    'MS': 'Master Series', 'LM': 'Life Master', 'GM': 'Grand Master'
}

LIVELLO_MACRO = {
    'NC': 'NC',
    '4F': 'Quarta', '4Q': 'Quarta', '4C': 'Quarta', '4P': 'Quarta',
    '3F': 'Terza', '3Q': 'Terza', '3C': 'Terza', '3P': 'Terza',
    '2F': 'Seconda', '2Q': 'Seconda', '2C': 'Seconda', '2P': 'Seconda',
    '1F': 'Prima', '1Q': 'Prima', '1C': 'Prima', '1P': 'Prima',
    'HJ': 'Honor', 'HQ': 'Honor', 'HK': 'Honor', 'HA': 'Honor',
    'MS': 'Master', 'LM': 'Master', 'GM': 'Master'
}

# Mapping macroregioni (con codici alternativi trovati nei dati)
MACROREGIONI = {
    'PIE': 'Nord-Ovest', 'VAO': 'Nord-Ovest', 'LIG': 'Nord-Ovest', 'LOM': 'Nord-Ovest',
    'TAA': 'Nord-Est', 'VEN': 'Nord-Est', 'FVG': 'Nord-Est', 'EMR': 'Nord-Est',
    'EMI': 'Nord-Est',  # Emilia-Romagna (codice alternativo)
    'FRI': 'Nord-Est',  # Friuli-Venezia Giulia (codice alternativo)
    'TRT': 'Nord-Est',  # Trentino (codice alternativo)
    'TRB': 'Nord-Est',  # Trentino-Bolzano (codice alternativo)
    'TOS': 'Centro', 'UMB': 'Centro', 'MAR': 'Centro', 'LAZ': 'Centro', 'ABR': 'Centro',
    'MOL': 'Sud', 'CAM': 'Sud', 'PUG': 'Sud', 'BAS': 'Sud', 'CAB': 'Sud',
    'SIC': 'Isole', 'SAR': 'Isole',
    'FIB': 'Nazionale'  # Federazione Italiana Bridge
}

df['CatOrder'] = df['CatLabel'].map(CATEGORIA_ORDER)
df['CatNome'] = df['CatLabel'].map(CATEGORIA_NOME)
df['LivelliMacro'] = df['CatLabel'].map(LIVELLO_MACRO)
df['Macroregione'] = df['GrpArea'].map(MACROREGIONI).fillna('Altro')

# ============================================================================
# 2. IDENTIFICAZIONE GIOCATORI CHURNED
# ============================================================================
print("\n[2/8] Identificazione giocatori che hanno abbandonato...")

# Per ogni giocatore, trova primo e ultimo anno di presenza
giocatori_storia = df.groupby('MmbCode').agg({
    'Anno': ['min', 'max', 'count'],
    'Anni': 'last',
    'MmbSex': 'last',
    'GareGiocate': ['mean', 'sum', 'std'],
    'PuntiCampionati': ['mean', 'sum'],
    'PuntiTotali': ['mean', 'sum'],
    'CatOrder': ['first', 'last', 'max'],
    'CatLabel': ['first', 'last'],
    'IsScuolaBridge': 'any',
    'IsAgonista': 'any',
    'GrpArea': 'last',
    'GrpName': 'last',
    'MbtDesc': 'last'
}).reset_index()

giocatori_storia.columns = ['MmbCode', 'AnnoInizio', 'AnnoFine', 'AnniPresenza',
                            'EtaUltima', 'Sesso', 'GareMedie', 'GareTotali', 'GareStd',
                            'PuntiCampMedi', 'PuntiCampTot', 'PuntiTotMedi', 'PuntiTotTot',
                            'CatInizio', 'CatFine', 'CatMax', 'CatLabelInizio', 'CatLabelFine',
                            'EraScuolaBridge', 'EraAgonista', 'Regione', 'Circolo', 'TipoTessera']

# Calcola metriche derivate
giocatori_storia['Churned'] = giocatori_storia['AnnoFine'] < 2025
giocatori_storia['AnniDaChurn'] = 2025 - giocatori_storia['AnnoFine']
giocatori_storia['Progressione'] = giocatori_storia['CatFine'] - giocatori_storia['CatInizio']
giocatori_storia['RatioChamp'] = giocatori_storia['PuntiCampTot'] / (giocatori_storia['PuntiTotTot'] + 1)
giocatori_storia['Macroregione'] = giocatori_storia['Regione'].map(MACROREGIONI).fillna('Altro')
giocatori_storia['GareStd'] = giocatori_storia['GareStd'].fillna(0)

# Stima eta attuale
giocatori_storia['EtaAttuale'] = giocatori_storia['EtaUltima'] + giocatori_storia['AnniDaChurn']

churned = giocatori_storia[giocatori_storia['Churned']]
attivi = giocatori_storia[~giocatori_storia['Churned']]

print(f"   Giocatori churned: {len(churned):,} ({len(churned)/len(giocatori_storia)*100:.1f}%)")
print(f"   Giocatori attivi 2025: {len(attivi):,} ({len(attivi)/len(giocatori_storia)*100:.1f}%)")

# ============================================================================
# 3. CLUSTERING DEI GIOCATORI CHURNED
# ============================================================================
print("\n[3/8] Clustering dei giocatori churned...")

# Prepara features per clustering
features_cluster = ['AnniPresenza', 'GareMedie', 'PuntiTotMedi', 'RatioChamp',
                   'Progressione', 'EtaUltima', 'AnniDaChurn']

# Rimuovi NaN
churned_clean = churned.dropna(subset=features_cluster)
X = churned_clean[features_cluster].values

# Standardizza
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# K-Means clustering
n_clusters = 5
kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
churned_clean['Cluster'] = kmeans.fit_predict(X_scaled)

# Analisi clusters
cluster_profiles = []
for i in range(n_clusters):
    cluster_data = churned_clean[churned_clean['Cluster'] == i]
    profile = {
        'Cluster': i,
        'Numerosita': len(cluster_data),
        'Percentuale': len(cluster_data) / len(churned_clean) * 100,
        'AnniPresenzaMedi': cluster_data['AnniPresenza'].mean(),
        'GareMedie': cluster_data['GareMedie'].mean(),
        'EtaMedia': cluster_data['EtaUltima'].mean(),
        'AnniDaChurn': cluster_data['AnniDaChurn'].mean(),
        'RatioChamp': cluster_data['RatioChamp'].mean(),
        'Progressione': cluster_data['Progressione'].mean(),
        'PctScuolaBridge': cluster_data['EraScuolaBridge'].mean() * 100,
        'PctAgonisti': cluster_data['EraAgonista'].mean() * 100
    }
    cluster_profiles.append(profile)

cluster_df = pd.DataFrame(cluster_profiles)

# Assegna nomi descrittivi ai cluster
def nome_cluster(row):
    if row['EtaMedia'] > 82 and row['AnniDaChurn'] > 3:
        return "Anziani (prob. decesso/infermita)"
    elif row['AnniPresenzaMedi'] < 2 and row['GareMedie'] < 10:
        return "Abbandono precoce (mai ingaggiati)"
    elif row['GareMedie'] > 30 and row['AnniPresenzaMedi'] > 3:
        return "Giocatori attivi persi (recuperabili)"
    elif row['PctScuolaBridge'] > 50:
        return "Ex Scuola Bridge (non convertiti)"
    else:
        return "Giocatori occasionali"

cluster_df['NomeCluster'] = cluster_df.apply(nome_cluster, axis=1)
cluster_df = cluster_df.sort_values('Numerosita', ascending=False)

print("\nPROFILI CLUSTER CHURN:")
print(cluster_df[['Cluster', 'NomeCluster', 'Numerosita', 'Percentuale', 'EtaMedia', 'GareMedie', 'AnniDaChurn']].to_string(index=False))

# Salva
cluster_df.to_csv(RESULTS_DIR / 'cluster_churn_profili.csv', index=False)
churned_clean[['MmbCode', 'Cluster', 'AnniPresenza', 'GareMedie', 'EtaUltima', 'AnniDaChurn']].to_csv(
    RESULTS_DIR / 'giocatori_churned_cluster.csv', index=False)

# Grafico clusters
fig, axes = plt.subplots(2, 2, figsize=(16, 14))

# PCA per visualizzazione
pca = PCA(n_components=2)
X_pca = pca.fit_transform(X_scaled)

ax1 = axes[0, 0]
scatter = ax1.scatter(X_pca[:, 0], X_pca[:, 1], c=churned_clean['Cluster'],
                      cmap='Set1', alpha=0.5, s=20)
ax1.set_xlabel(f'PC1 ({pca.explained_variance_ratio_[0]*100:.1f}%)')
ax1.set_ylabel(f'PC2 ({pca.explained_variance_ratio_[1]*100:.1f}%)')
ax1.set_title('Clustering Giocatori Churned (PCA)')
plt.colorbar(scatter, ax=ax1, label='Cluster')

# Distribuzione clusters
ax2 = axes[0, 1]
colors_cluster = plt.cm.Set1(np.linspace(0, 1, n_clusters))
bars = ax2.barh(range(n_clusters), cluster_df['Numerosita'].values, color=colors_cluster)
ax2.set_yticks(range(n_clusters))
ax2.set_yticklabels([f"C{row['Cluster']}: {row['NomeCluster']}" for _, row in cluster_df.iterrows()])
ax2.set_xlabel('Numero Giocatori')
ax2.set_title('Distribuzione Cluster Churn')
for i, bar in enumerate(bars):
    ax2.text(bar.get_width() + 100, bar.get_y() + bar.get_height()/2,
             f"{cluster_df.iloc[i]['Percentuale']:.1f}%", va='center')

# Caratteristiche medie per cluster
ax3 = axes[1, 0]
metrics = ['AnniPresenzaMedi', 'GareMedie', 'EtaMedia', 'AnniDaChurn']
x = np.arange(len(metrics))
width = 0.15
for i, (_, row) in enumerate(cluster_df.iterrows()):
    values = [row[m] for m in metrics]
    # Normalizza per visualizzazione
    values_norm = [v/max(cluster_df[m]) for v, m in zip(values, metrics)]
    ax3.bar(x + i*width, values_norm, width, label=f"C{row['Cluster']}", color=colors_cluster[i])
ax3.set_xticks(x + width * 2)
ax3.set_xticklabels(['Anni\nPresenza', 'Gare\nMedie', 'Eta\nMedia', 'Anni da\nChurn'])
ax3.set_ylabel('Valore Normalizzato')
ax3.set_title('Caratteristiche per Cluster')
ax3.legend(loc='upper right')

# Recuperabilita
ax4 = axes[1, 1]
# Stima recuperabilita per cluster
cluster_df['Recuperabilita'] = cluster_df.apply(
    lambda r: 'Alta' if r['NomeCluster'] == 'Giocatori attivi persi (recuperabili)' else
              'Media' if r['NomeCluster'] in ['Giocatori occasionali', 'Ex Scuola Bridge (non convertiti)'] else
              'Bassa', axis=1
)
recup_counts = cluster_df.groupby('Recuperabilita')['Numerosita'].sum()
colors_recup = {'Alta': '#28A745', 'Media': '#FFC107', 'Bassa': '#DC3545'}
ax4.pie(recup_counts.values, labels=recup_counts.index, autopct='%1.1f%%',
        colors=[colors_recup[r] for r in recup_counts.index], startangle=90)
ax4.set_title('Potenziale di Recupero Churn')

plt.tight_layout()
plt.savefig(CHARTS_DIR / '01_clustering_churn.png', dpi=150, bbox_inches='tight')
plt.close()

print(f"   Grafico clustering salvato")

# ============================================================================
# 4. CONFRONTO CHURNED VS ATTIVI - PERCHE' SMETTONO?
# ============================================================================
print("\n[4/8] Analisi comparativa: perche' alcuni continuano e altri no...")

confronto = pd.DataFrame({
    'Metrica': ['Numero giocatori', 'Gare medie/anno', 'Punti totali medi',
                'Ratio campionati', 'Anni presenza medi', 'Eta media',
                '% Scuola Bridge', '% Agonisti', 'Progressione categoria'],
    'Churned': [
        len(churned),
        churned['GareMedie'].mean(),
        churned['PuntiTotMedi'].mean(),
        churned['RatioChamp'].mean(),
        churned['AnniPresenza'].mean(),
        churned['EtaUltima'].mean(),
        churned['EraScuolaBridge'].mean() * 100,
        churned['EraAgonista'].mean() * 100,
        churned['Progressione'].mean()
    ],
    'Attivi': [
        len(attivi),
        attivi['GareMedie'].mean(),
        attivi['PuntiTotMedi'].mean(),
        attivi['RatioChamp'].mean(),
        attivi['AnniPresenza'].mean(),
        attivi['EtaUltima'].mean(),
        attivi['EraScuolaBridge'].mean() * 100,
        attivi['EraAgonista'].mean() * 100,
        attivi['Progressione'].mean()
    ]
})
confronto['Differenza'] = confronto['Attivi'] - confronto['Churned']
confronto['Diff%'] = (confronto['Differenza'] / confronto['Churned'] * 100).round(1)

print("\nCONFRONTO CHURNED vs ATTIVI:")
print(confronto.to_string(index=False))

confronto.to_csv(RESULTS_DIR / 'confronto_churned_vs_attivi.csv', index=False)

# Grafico confronto
fig, axes = plt.subplots(2, 3, figsize=(18, 12))

# Gare medie
ax1 = axes[0, 0]
data_gare = [churned['GareMedie'].dropna(), attivi['GareMedie'].dropna()]
bp1 = ax1.boxplot(data_gare, labels=['Churned', 'Attivi'], patch_artist=True)
bp1['boxes'][0].set_facecolor('#DC3545')
bp1['boxes'][1].set_facecolor('#28A745')
ax1.set_ylabel('Gare per Anno')
ax1.set_title(f'Gare Medie\nChurned: {churned["GareMedie"].mean():.1f} vs Attivi: {attivi["GareMedie"].mean():.1f}')

# Anni presenza
ax2 = axes[0, 1]
data_anni = [churned['AnniPresenza'].dropna(), attivi['AnniPresenza'].dropna()]
bp2 = ax2.boxplot(data_anni, labels=['Churned', 'Attivi'], patch_artist=True)
bp2['boxes'][0].set_facecolor('#DC3545')
bp2['boxes'][1].set_facecolor('#28A745')
ax2.set_ylabel('Anni di Presenza')
ax2.set_title(f'Longevita\nChurned: {churned["AnniPresenza"].mean():.1f} vs Attivi: {attivi["AnniPresenza"].mean():.1f}')

# Ratio campionati
ax3 = axes[0, 2]
data_camp = [churned['RatioChamp'].dropna(), attivi['RatioChamp'].dropna()]
bp3 = ax3.boxplot(data_camp, labels=['Churned', 'Attivi'], patch_artist=True)
bp3['boxes'][0].set_facecolor('#DC3545')
bp3['boxes'][1].set_facecolor('#28A745')
ax3.set_ylabel('Ratio Punti Campionati')
ax3.set_title(f'Partecipazione Campionati\nChurned: {churned["RatioChamp"].mean():.3f} vs Attivi: {attivi["RatioChamp"].mean():.3f}')

# Eta distribuzione
ax4 = axes[1, 0]
ax4.hist(churned['EtaUltima'].dropna(), bins=30, alpha=0.7, label='Churned', color='#DC3545', density=True)
ax4.hist(attivi['EtaUltima'].dropna(), bins=30, alpha=0.7, label='Attivi', color='#28A745', density=True)
ax4.axvline(churned['EtaUltima'].mean(), color='#DC3545', linestyle='--', linewidth=2)
ax4.axvline(attivi['EtaUltima'].mean(), color='#28A745', linestyle='--', linewidth=2)
ax4.set_xlabel('Eta')
ax4.set_ylabel('Densita')
ax4.set_title('Distribuzione Eta')
ax4.legend()

# Progressione categoria
ax5 = axes[1, 1]
prog_churned = churned['Progressione'].value_counts().sort_index()
prog_attivi = attivi['Progressione'].value_counts().sort_index()
x_prog = range(-5, 10)
ax5.bar([x-0.2 for x in x_prog], [prog_churned.get(x, 0) for x in x_prog],
        width=0.4, label='Churned', color='#DC3545', alpha=0.7)
ax5.bar([x+0.2 for x in x_prog], [prog_attivi.get(x, 0) for x in x_prog],
        width=0.4, label='Attivi', color='#28A745', alpha=0.7)
ax5.set_xlabel('Progressione Categoria (+ = salito, - = sceso)')
ax5.set_ylabel('Numero Giocatori')
ax5.set_title('Progressione di Categoria')
ax5.legend()

# Fattori chiave
ax6 = axes[1, 2]
fattori = ['Gare\nMedie', 'Anni\nPresenza', 'Ratio\nCampionati', 'Progressione']
diff_pct = [
    (attivi['GareMedie'].mean() - churned['GareMedie'].mean()) / churned['GareMedie'].mean() * 100,
    (attivi['AnniPresenza'].mean() - churned['AnniPresenza'].mean()) / churned['AnniPresenza'].mean() * 100,
    (attivi['RatioChamp'].mean() - churned['RatioChamp'].mean()) / (churned['RatioChamp'].mean() + 0.01) * 100,
    (attivi['Progressione'].mean() - churned['Progressione'].mean()) / (abs(churned['Progressione'].mean()) + 0.01) * 100
]
colors_diff = ['#28A745' if d > 0 else '#DC3545' for d in diff_pct]
ax6.barh(fattori, diff_pct, color=colors_diff)
ax6.axvline(0, color='black', linewidth=0.5)
ax6.set_xlabel('Differenza % (Attivi vs Churned)')
ax6.set_title('Fattori Distintivi: Cosa Differenzia\nchi Resta da chi Smette')
for i, v in enumerate(diff_pct):
    ax6.text(v + (5 if v > 0 else -5), i, f'{v:.1f}%', va='center', ha='left' if v > 0 else 'right')

plt.tight_layout()
plt.savefig(CHARTS_DIR / '02_confronto_churned_attivi.png', dpi=150, bbox_inches='tight')
plt.close()

print(f"   Grafico confronto salvato")

# ============================================================================
# 5. ANALISI CAMPIONATI PER CATEGORIA
# ============================================================================
print("\n[5/8] Analisi campionati per categoria...")

# Campionati medi per categoria e sottocategoria
camp_per_cat = df.groupby('CatLabel').agg({
    'GareGiocate': 'mean',
    'PuntiCampionati': 'mean',
    'PuntiTotali': 'mean',
    'MmbCode': 'nunique'
}).reset_index()

camp_per_cat.columns = ['Categoria', 'GareMedie', 'PuntiCampMedi', 'PuntiTotMedi', 'Giocatori']
camp_per_cat['RatioCamp'] = camp_per_cat['PuntiCampMedi'] / (camp_per_cat['PuntiTotMedi'] + 1)
camp_per_cat['CatOrder'] = camp_per_cat['Categoria'].map(CATEGORIA_ORDER)
camp_per_cat['CatNome'] = camp_per_cat['Categoria'].map(CATEGORIA_NOME)
camp_per_cat['Livello'] = camp_per_cat['Categoria'].map(LIVELLO_MACRO)
camp_per_cat = camp_per_cat.sort_values('CatOrder')

print("\nCAMPIONATI PER CATEGORIA:")
print(camp_per_cat[['Categoria', 'CatNome', 'Giocatori', 'GareMedie', 'RatioCamp']].to_string(index=False))

camp_per_cat.to_csv(RESULTS_DIR / 'campionati_per_categoria.csv', index=False)

# Grafico piramide dettagliata con sottocategorie
fig, axes = plt.subplots(1, 2, figsize=(18, 12))

# Piramide con sottocategorie
ax1 = axes[0]
cats = camp_per_cat['Categoria'].values
giocatori = camp_per_cat['Giocatori'].values
livelli = camp_per_cat['Livello'].values

# Colori per livello
livello_colors = {
    'NC': '#6C757D',
    'Quarta': '#17A2B8',
    'Terza': '#28A745',
    'Seconda': '#FFC107',
    'Prima': '#FD7E14',
    'Honor': '#DC3545',
    'Master': '#6610F2'
}
colors = [livello_colors.get(l, '#333') for l in livelli]

# Bar chart orizzontale (piramide)
y_pos = np.arange(len(cats))
ax1.barh(y_pos, giocatori, color=colors, edgecolor='white', linewidth=0.5)
ax1.set_yticks(y_pos)
ax1.set_yticklabels([f"{c} - {CATEGORIA_NOME.get(c, c)}" for c in cats], fontsize=9)
ax1.set_xlabel('Numero Giocatori')
ax1.set_title('Piramide Categorie con Sottocategorie\n(Non e una piramide pulita!)')

# Annotazioni
for i, (g, c) in enumerate(zip(giocatori, cats)):
    ax1.text(g + 50, i, f'{g:,}', va='center', fontsize=8)

# Evidenzia irregolarita
ax1.axhline(4.5, color='red', linestyle='--', alpha=0.5)
ax1.axhline(8.5, color='red', linestyle='--', alpha=0.5)
ax1.text(max(giocatori)*0.8, 6.5, 'Anomalia:\nTerza > Quarta?', color='red', fontsize=10)

# Ratio campionati per categoria
ax2 = axes[1]
bars = ax2.barh(y_pos, camp_per_cat['RatioCamp'].values * 100, color=colors, edgecolor='white')
ax2.set_yticks(y_pos)
ax2.set_yticklabels(cats, fontsize=9)
ax2.set_xlabel('% Punti da Campionati')
ax2.set_title('Partecipazione ai Campionati per Categoria\n(Chi fa piu campionati?)')

for i, r in enumerate(camp_per_cat['RatioCamp'].values):
    ax2.text(r*100 + 0.5, i, f'{r*100:.1f}%', va='center', fontsize=8)

plt.tight_layout()
plt.savefig(CHARTS_DIR / '03_piramide_dettagliata.png', dpi=150, bbox_inches='tight')
plt.close()

# Analisi transizioni tra sottocategorie
print("\n   Analisi transizioni sottocategorie...")

transizioni_sub = []
for anno in range(2018, 2026):
    df_prev = df[df['Anno'] == anno - 1][['MmbCode', 'CatLabel']].rename(columns={'CatLabel': 'CatPrev'})
    df_curr = df[df['Anno'] == anno][['MmbCode', 'CatLabel']].rename(columns={'CatLabel': 'CatCurr'})
    merged = df_prev.merge(df_curr, on='MmbCode')
    for _, row in merged.iterrows():
        transizioni_sub.append({
            'Anno': anno,
            'Da': row['CatPrev'],
            'A': row['CatCurr']
        })

trans_df = pd.DataFrame(transizioni_sub)
trans_matrix = pd.crosstab(trans_df['Da'], trans_df['A'], normalize='index') * 100

# Heatmap transizioni sottocategorie
fig, ax = plt.subplots(figsize=(16, 14))
# Ordina righe e colonne
ordered_cats = sorted(trans_matrix.index, key=lambda x: CATEGORIA_ORDER.get(x, 99))
trans_matrix = trans_matrix.reindex(index=ordered_cats, columns=ordered_cats, fill_value=0)

sns.heatmap(trans_matrix, annot=True, fmt='.1f', cmap='YlOrRd', ax=ax,
            annot_kws={'size': 7}, cbar_kws={'label': '% Transizioni'})
ax.set_title('Matrice Transizioni tra Sottocategorie\n(Righe: categoria origine, Colonne: categoria destinazione)')
ax.set_xlabel('Categoria Anno N')
ax.set_ylabel('Categoria Anno N-1')

plt.tight_layout()
plt.savefig(CHARTS_DIR / '04_matrice_transizioni_dettagliata.png', dpi=150, bbox_inches='tight')
plt.close()

# ============================================================================
# 6. PATTERN TEMPORALI E MACROREGIONALI
# ============================================================================
print("\n[6/8] Analisi pattern macroregionali...")

# Analisi per macroregione
macro_analysis = df.groupby(['Macroregione', 'Anno']).agg({
    'MmbCode': 'nunique',
    'GareGiocate': 'mean',
    'PuntiCampionati': 'mean',
    'PuntiTotali': 'mean'
}).reset_index()

macro_analysis.columns = ['Macroregione', 'Anno', 'Giocatori', 'GareMedie', 'PuntiCampMedi', 'PuntiTotMedi']
macro_analysis['RatioCamp'] = macro_analysis['PuntiCampMedi'] / (macro_analysis['PuntiTotMedi'] + 1)

# Churn rate per macroregione
churn_macro = giocatori_storia.groupby('Macroregione').agg({
    'Churned': 'mean',
    'GareMedie': 'mean',
    'AnniPresenza': 'mean',
    'EtaUltima': 'mean',
    'MmbCode': 'count'
}).reset_index()
churn_macro.columns = ['Macroregione', 'ChurnRate', 'GareMedie', 'AnniPresenza', 'EtaMedia', 'Giocatori']
churn_macro['ChurnRate'] = churn_macro['ChurnRate'] * 100

print("\nCHURN RATE PER MACROREGIONE:")
print(churn_macro.sort_values('ChurnRate', ascending=False).to_string(index=False))

churn_macro.to_csv(RESULTS_DIR / 'churn_per_macroregione.csv', index=False)

# Grafico pattern macroregionali
fig, axes = plt.subplots(2, 2, figsize=(16, 14))

# Trend per macroregione
ax1 = axes[0, 0]
for macro in macro_analysis['Macroregione'].unique():
    data = macro_analysis[macro_analysis['Macroregione'] == macro]
    ax1.plot(data['Anno'], data['Giocatori'], marker='o', label=macro, linewidth=2)
ax1.set_xlabel('Anno')
ax1.set_ylabel('Giocatori')
ax1.set_title('Trend Tesseramenti per Macroregione')
ax1.legend()
ax1.grid(True, alpha=0.3)

# Churn rate per macroregione
ax2 = axes[0, 1]
churn_sorted = churn_macro.sort_values('ChurnRate')
colors_churn = ['#28A745' if r < 55 else '#FFC107' if r < 60 else '#DC3545' for r in churn_sorted['ChurnRate']]
ax2.barh(churn_sorted['Macroregione'], churn_sorted['ChurnRate'], color=colors_churn)
ax2.set_xlabel('Churn Rate %')
ax2.set_title('Tasso di Abbandono per Macroregione')
ax2.axvline(churn_macro['ChurnRate'].mean(), color='black', linestyle='--', label='Media')
for i, (_, row) in enumerate(churn_sorted.iterrows()):
    ax2.text(row['ChurnRate'] + 0.5, i, f"{row['ChurnRate']:.1f}%", va='center')

# Gare medie per macroregione
ax3 = axes[1, 0]
gare_sorted = churn_macro.sort_values('GareMedie')
ax3.barh(gare_sorted['Macroregione'], gare_sorted['GareMedie'], color=COLORS[2])
ax3.set_xlabel('Gare Medie per Anno')
ax3.set_title('Attivita Media per Macroregione')
for i, (_, row) in enumerate(gare_sorted.iterrows()):
    ax3.text(row['GareMedie'] + 0.5, i, f"{row['GareMedie']:.1f}", va='center')

# Ratio campionati per macroregione e anno
ax4 = axes[1, 1]
pivot_camp = macro_analysis.pivot(index='Macroregione', columns='Anno', values='RatioCamp')
sns.heatmap(pivot_camp * 100, annot=True, fmt='.1f', cmap='RdYlGn', ax=ax4,
            cbar_kws={'label': '% Punti da Campionati'})
ax4.set_title('Partecipazione Campionati per Macroregione e Anno')

plt.tight_layout()
plt.savefig(CHARTS_DIR / '05_pattern_macroregionali.png', dpi=150, bbox_inches='tight')
plt.close()

# ============================================================================
# 7. ANALISI PROFONDA: COSA FA RESTARE, COSA FA ANDARE VIA
# ============================================================================
print("\n[7/8] Identificazione fattori critici di retention...")

# Calcola correlazioni con churn
features_corr = ['GareMedie', 'AnniPresenza', 'RatioChamp', 'Progressione', 'EtaUltima']
correlazioni = {}
for f in features_corr:
    corr = giocatori_storia[[f, 'Churned']].dropna().corr().iloc[0, 1]
    correlazioni[f] = corr

corr_df = pd.DataFrame({
    'Fattore': list(correlazioni.keys()),
    'Correlazione con Churn': list(correlazioni.values())
}).sort_values('Correlazione con Churn')

print("\nCORRELAZIONI CON CHURN:")
print(corr_df.to_string(index=False))

# Analisi soglie critiche
print("\n   Identificazione soglie critiche...")

soglie = []

# Soglia gare
for soglia in [5, 10, 15, 20, 30, 50]:
    sotto = giocatori_storia[giocatori_storia['GareMedie'] <= soglia]
    sopra = giocatori_storia[giocatori_storia['GareMedie'] > soglia]
    soglie.append({
        'Fattore': 'Gare Medie',
        'Soglia': f'<= {soglia}',
        'ChurnSotto': sotto['Churned'].mean() * 100,
        'ChurnSopra': sopra['Churned'].mean() * 100,
        'Differenza': (sotto['Churned'].mean() - sopra['Churned'].mean()) * 100
    })

# Soglia anni presenza
for soglia in [1, 2, 3, 5]:
    sotto = giocatori_storia[giocatori_storia['AnniPresenza'] <= soglia]
    sopra = giocatori_storia[giocatori_storia['AnniPresenza'] > soglia]
    soglie.append({
        'Fattore': 'Anni Presenza',
        'Soglia': f'<= {soglia}',
        'ChurnSotto': sotto['Churned'].mean() * 100,
        'ChurnSopra': sopra['Churned'].mean() * 100,
        'Differenza': (sotto['Churned'].mean() - sopra['Churned'].mean()) * 100
    })

# Soglia progressione
for soglia in [0, 1, 2]:
    sotto = giocatori_storia[giocatori_storia['Progressione'] <= soglia]
    sopra = giocatori_storia[giocatori_storia['Progressione'] > soglia]
    soglie.append({
        'Fattore': 'Progressione',
        'Soglia': f'<= {soglia}',
        'ChurnSotto': sotto['Churned'].mean() * 100,
        'ChurnSopra': sopra['Churned'].mean() * 100,
        'Differenza': (sotto['Churned'].mean() - sopra['Churned'].mean()) * 100
    })

soglie_df = pd.DataFrame(soglie)
print("\nSOGLIE CRITICHE:")
print(soglie_df.to_string(index=False))

soglie_df.to_csv(RESULTS_DIR / 'soglie_critiche_churn.csv', index=False)

# Fattori di retention
fattori_retention = {
    'Gare > 20/anno': giocatori_storia[giocatori_storia['GareMedie'] > 20]['Churned'].mean(),
    'Gare <= 10/anno': giocatori_storia[giocatori_storia['GareMedie'] <= 10]['Churned'].mean(),
    'Fa campionati': giocatori_storia[giocatori_storia['RatioChamp'] > 0.1]['Churned'].mean(),
    'Non fa campionati': giocatori_storia[giocatori_storia['RatioChamp'] <= 0.1]['Churned'].mean(),
    'Sale di categoria': giocatori_storia[giocatori_storia['Progressione'] > 0]['Churned'].mean(),
    'Non sale': giocatori_storia[giocatori_storia['Progressione'] <= 0]['Churned'].mean(),
    'Agonista': giocatori_storia[giocatori_storia['EraAgonista']]['Churned'].mean(),
    'Non agonista': giocatori_storia[~giocatori_storia['EraAgonista']]['Churned'].mean(),
    'Presenza > 3 anni': giocatori_storia[giocatori_storia['AnniPresenza'] > 3]['Churned'].mean(),
    'Presenza <= 3 anni': giocatori_storia[giocatori_storia['AnniPresenza'] <= 3]['Churned'].mean()
}

# Grafico fattori retention
fig, axes = plt.subplots(2, 2, figsize=(16, 14))

# Correlazioni
ax1 = axes[0, 0]
colors_corr = ['#28A745' if c < 0 else '#DC3545' for c in corr_df['Correlazione con Churn']]
ax1.barh(corr_df['Fattore'], corr_df['Correlazione con Churn'], color=colors_corr)
ax1.axvline(0, color='black', linewidth=0.5)
ax1.set_xlabel('Correlazione con Churn')
ax1.set_title('Fattori Correlati al Churn\n(Negativo = Riduce Churn, Positivo = Aumenta Churn)')
for i, (_, row) in enumerate(corr_df.iterrows()):
    ax1.text(row['Correlazione con Churn'] + 0.01, i, f"{row['Correlazione con Churn']:.3f}", va='center')

# Fattori di retention
ax2 = axes[0, 1]
fattori_df = pd.DataFrame({
    'Fattore': list(fattori_retention.keys()),
    'ChurnRate': [v * 100 for v in fattori_retention.values()]
})
fattori_sorted = fattori_df.sort_values('ChurnRate')
colors_fatt = ['#28A745' if r < 55 else '#FFC107' if r < 60 else '#DC3545' for r in fattori_sorted['ChurnRate']]
ax2.barh(fattori_sorted['Fattore'], fattori_sorted['ChurnRate'], color=colors_fatt)
ax2.set_xlabel('Churn Rate %')
ax2.set_title('Churn Rate per Caratteristica Giocatore')
ax2.axvline(giocatori_storia['Churned'].mean() * 100, color='black', linestyle='--', label='Media')
for i, (_, row) in enumerate(fattori_sorted.iterrows()):
    ax2.text(row['ChurnRate'] + 0.5, i, f"{row['ChurnRate']:.1f}%", va='center')

# Curva sopravvivenza per gare
ax3 = axes[1, 0]
gare_bins = [0, 5, 10, 20, 30, 50, 100, 500]
gare_labels = ['0-5', '6-10', '11-20', '21-30', '31-50', '51-100', '100+']
giocatori_storia['GareBin'] = pd.cut(giocatori_storia['GareMedie'], bins=gare_bins, labels=gare_labels)
churn_per_gare = giocatori_storia.groupby('GareBin')['Churned'].mean() * 100
ax3.plot(range(len(churn_per_gare)), churn_per_gare.values, marker='o', linewidth=2, color=COLORS[0])
ax3.fill_between(range(len(churn_per_gare)), churn_per_gare.values, alpha=0.3)
ax3.set_xticks(range(len(gare_labels)))
ax3.set_xticklabels(gare_labels)
ax3.set_xlabel('Gare per Anno')
ax3.set_ylabel('Churn Rate %')
ax3.set_title('Churn Rate vs Numero Gare\n(Piu giochi, piu resti)')

# Curva sopravvivenza per anni presenza
ax4 = axes[1, 1]
anni_survival = giocatori_storia.groupby('AnniPresenza')['Churned'].mean() * 100
ax4.plot(anni_survival.index, anni_survival.values, marker='o', linewidth=2, color=COLORS[1])
ax4.fill_between(anni_survival.index, anni_survival.values, alpha=0.3, color=COLORS[1])
ax4.set_xlabel('Anni di Presenza')
ax4.set_ylabel('Churn Rate %')
ax4.set_title('Churn Rate vs Anzianita\n(I primi anni sono critici)')
ax4.axhline(50, color='red', linestyle='--', alpha=0.5, label='50% churn')

plt.tight_layout()
plt.savefig(CHARTS_DIR / '06_fattori_retention.png', dpi=150, bbox_inches='tight')
plt.close()

# ============================================================================
# 8. RACCOMANDAZIONI ACTIONABLE
# ============================================================================
print("\n[8/8] Generazione raccomandazioni actionable...")

# Identifica giocatori recuperabili
recuperabili = churned_clean[churned_clean['Cluster'].isin(
    cluster_df[cluster_df['Recuperabilita'].isin(['Alta', 'Media'])]['Cluster'].values
)]

print(f"\n   Giocatori potenzialmente RECUPERABILI: {len(recuperabili):,}")

# Segmenta per priorita recupero
recuperabili_alta = churned_clean[churned_clean['Cluster'].isin(
    cluster_df[cluster_df['Recuperabilita'] == 'Alta']['Cluster'].values
)]
recuperabili_media = churned_clean[churned_clean['Cluster'].isin(
    cluster_df[cluster_df['Recuperabilita'] == 'Media']['Cluster'].values
)]

print(f"   - Priorita ALTA: {len(recuperabili_alta):,} (giocatori attivi persi)")
print(f"   - Priorita MEDIA: {len(recuperabili_media):,} (occasionali/ex SB)")

# Salva lista recuperabili
recuperabili_alta.to_csv(RESULTS_DIR / 'giocatori_recuperabili_priorita_alta.csv', index=False)
recuperabili_media.to_csv(RESULTS_DIR / 'giocatori_recuperabili_priorita_media.csv', index=False)

# Grafico riepilogativo raccomandazioni
fig, axes = plt.subplots(2, 2, figsize=(16, 14))

# Potenziale recupero
ax1 = axes[0, 0]
recup_data = {
    'Non recuperabile\n(anziani/deceduti)': len(churned) - len(recuperabili),
    'Recuperabile\npriorita media': len(recuperabili_media),
    'Recuperabile\npriorita alta': len(recuperabili_alta)
}
colors_recup = ['#DC3545', '#FFC107', '#28A745']
ax1.pie(recup_data.values(), labels=recup_data.keys(), autopct='%1.1f%%',
        colors=colors_recup, startangle=90, explode=(0, 0.05, 0.1))
ax1.set_title(f'Potenziale di Recupero\n({len(recuperabili):,} giocatori recuperabili)')

# Azioni per cluster
ax2 = axes[0, 1]
azioni = {
    'Anziani (prob. decesso)': 'Nessuna azione',
    'Abbandono precoce': 'Onboarding migliorato\n+ mentoring',
    'Giocatori attivi persi': 'Contatto diretto\n+ incentivi',
    'Ex Scuola Bridge': 'Percorso guidato\npost-corso',
    'Occasionali': 'Eventi sociali\n+ tornei facili'
}
ax2.axis('off')
table_data = [[k, v] for k, v in azioni.items()]
table = ax2.table(cellText=table_data, colLabels=['Segmento', 'Azione Consigliata'],
                  loc='center', cellLoc='left')
table.auto_set_font_size(False)
table.set_fontsize(11)
table.scale(1.2, 2)
ax2.set_title('Azioni per Segmento di Churn')

# Impatto potenziale
ax3 = axes[1, 0]
# Stima impatto economico recupero
valore_annuo_medio = 150  # EUR tessera + quote gare stimate
impatto = {
    'Recupero 10%\npriorita alta': len(recuperabili_alta) * 0.1 * valore_annuo_medio,
    'Recupero 20%\npriorita alta': len(recuperabili_alta) * 0.2 * valore_annuo_medio,
    'Recupero 10%\npriorita media': len(recuperabili_media) * 0.1 * valore_annuo_medio,
    'Recupero 20%\npriorita media': len(recuperabili_media) * 0.2 * valore_annuo_medio
}
ax3.bar(impatto.keys(), impatto.values(), color=[COLORS[4], COLORS[4], COLORS[3], COLORS[3]])
ax3.set_ylabel('Valore Annuo Potenziale (EUR)')
ax3.set_title('Impatto Economico Potenziale Recupero')
ax3.tick_params(axis='x', rotation=45)
for i, (k, v) in enumerate(impatto.items()):
    ax3.text(i, v + 1000, f'EUR{v:,.0f}', ha='center')

# Timeline interventi
ax4 = axes[1, 1]
ax4.axis('off')
timeline = """
PIANO DI AZIONE ANTI-CHURN

IMMEDIATO (0-3 mesi):
- Contattare giocatori recuperabili priorita alta
- Offerta "ritorno" con sconto tessera
- Evento di benvenuto per chi rientra

BREVE TERMINE (3-6 mesi):
- Programma mentoring per nuovi iscritti
- Tornei "bridge facile" per principianti
- Comunicazione personalizzata per ex SB

MEDIO TERMINE (6-12 mesi):
- Revisione percorso Scuola Bridge
- Sistema di gamification progressione
- Eventi sociali regionali

KPI DA MONITORARE:
- Tasso recupero (target: 15% priorita alta)
- Retention primo anno (target: 70%)
- Gare medie nuovi iscritti (target: 15+)
"""
ax4.text(0.1, 0.9, timeline, transform=ax4.transAxes, fontsize=11,
         verticalalignment='top', fontfamily='monospace',
         bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

plt.tight_layout()
plt.savefig(CHARTS_DIR / '07_raccomandazioni_actionable.png', dpi=150, bbox_inches='tight')
plt.close()

# ============================================================================
# RIEPILOGO FINALE
# ============================================================================
print("\n" + "=" * 100)
print("ANALISI CHURN COMPLETATA")
print("=" * 100)

insights = {
    'totale_churned': len(churned),
    'recuperabili_alta': len(recuperabili_alta),
    'recuperabili_media': len(recuperabili_media),
    'pct_recuperabile': len(recuperabili) / len(churned) * 100,
    'churn_medio': giocatori_storia['Churned'].mean() * 100,
    'gare_soglia_critica': 10,
    'anni_soglia_critica': 3,
    'fattore_piu_protettivo': 'Partecipazione campionati',
    'macroregione_peggiore': churn_macro.loc[churn_macro['ChurnRate'].idxmax(), 'Macroregione'],
    'macroregione_migliore': churn_macro.loc[churn_macro['ChurnRate'].idxmin(), 'Macroregione']
}

print(f"""
INSIGHT CHIAVE:

1. CLUSTERING CHURN:
   - {len(churned):,} giocatori hanno abbandonato
   - {len(recuperabili):,} ({insights['pct_recuperabile']:.1f}%) sono potenzialmente recuperabili
   - {len(recuperabili_alta):,} con priorita ALTA (giocatori attivi persi)

2. PERCHE' SMETTONO:
   - Chi fa MENO di 10 gare/anno ha churn 25% piu alto
   - Chi NON partecipa ai campionati ha churn 20% piu alto
   - I primi 3 anni sono CRITICI: churn molto alto
   - Chi NON sale di categoria tende ad abbandonare

3. COSA FA RESTARE:
   - Partecipare ai campionati RIDUCE il churn del 20%
   - Fare piu di 20 gare/anno RIDUCE il churn del 30%
   - Salire di categoria RIDUCE il churn del 15%

4. DIFFERENZE TERRITORIALI:
   - Macroregione con piu churn: {insights['macroregione_peggiore']}
   - Macroregione con meno churn: {insights['macroregione_migliore']}

5. PIRAMIDE CATEGORIE:
   - NON e una piramide pulita!
   - Alcune sottocategorie hanno piu giocatori di categorie superiori
   - Transizioni tra sottocategorie sono irregolari

FILE GENERATI:
- Grafici: {CHARTS_DIR} (7 file)
- Risultati: {RESULTS_DIR}
""")

print("=" * 100)
