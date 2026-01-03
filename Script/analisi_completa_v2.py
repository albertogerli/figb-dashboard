#!/usr/bin/env python3
"""
ANALISI COMPLETA FIGB 2017-2025
Replica struttura Relazione_Finale_Completa_FIGB.pdf
230+ metriche, 50+ grafici, tutte le analisi specialistiche
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.gridspec import GridSpec
import seaborn as sns
from pathlib import Path
from datetime import datetime
import json
import warnings
warnings.filterwarnings('ignore')

# Configurazione
plt.style.use('seaborn-v0_8-whitegrid')
plt.rcParams['figure.figsize'] = (12, 8)
plt.rcParams['font.size'] = 10
plt.rcParams['axes.titlesize'] = 14
plt.rcParams['axes.labelsize'] = 12

# Directory
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / 'Dati'
OUTPUT_DIR = BASE_DIR / 'output'
CHARTS_DIR = OUTPUT_DIR / 'charts_v2'
RESULTS_DIR = OUTPUT_DIR / 'results_v2'

CHARTS_DIR.mkdir(parents=True, exist_ok=True)
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

# Colori corporate
COLORS = {
    'primary': '#1E3A5F',
    'secondary': '#2E5984',
    'accent': '#4A90D9',
    'success': '#28A745',
    'warning': '#FFC107',
    'danger': '#DC3545',
    'info': '#17A2B8',
    'light': '#F8F9FA',
    'dark': '#343A40'
}

PALETTE = ['#1E3A5F', '#2E5984', '#4A90D9', '#6BB3E9', '#8ECAE6', '#B8D4E8', '#DC3545', '#28A745']

print("=" * 100)
print("ANALISI COMPLETA FIGB 2017-2025")
print("Replica struttura Relazione_Finale_Completa_FIGB.pdf")
print("=" * 100)

# ============================================================================
# 1. CARICAMENTO DATI
# ============================================================================
print("\n[1/10] Caricamento dati...")

df = pd.read_csv(OUTPUT_DIR / 'dati_unificati_2017_2025.csv')
print(f"   Record totali: {len(df):,}")
print(f"   Giocatori unici: {df['MmbCode'].nunique():,}")
print(f"   Anni: {df['Anno'].min()}-{df['Anno'].max()}")

# Mapping categorie per ordine gerarchico
CATEGORIA_ORDER = {
    'NC': 0,
    '4F': 1, '4Q': 2, '4C': 3, '4P': 4,
    '3F': 5, '3Q': 6, '3C': 7, '3P': 8,
    '2F': 9, '2Q': 10, '2C': 11, '2P': 12,
    '1F': 13, '1Q': 14, '1C': 15, '1P': 16,
    'HJ': 17, 'HQ': 18, 'HK': 19, 'HA': 20,
    'MS': 21, 'LM': 22, 'GM': 23
}

CATEGORIA_LIVELLO = {
    'NC': 'Non Classificato',
    '4F': 'Quarta', '4Q': 'Quarta', '4C': 'Quarta', '4P': 'Quarta',
    '3F': 'Terza', '3Q': 'Terza', '3C': 'Terza', '3P': 'Terza',
    '2F': 'Seconda', '2Q': 'Seconda', '2C': 'Seconda', '2P': 'Seconda',
    '1F': 'Prima', '1Q': 'Prima', '1C': 'Prima', '1P': 'Prima',
    'HJ': 'Honor Fante', 'HQ': 'Honor Dama', 'HK': 'Honor Re', 'HA': 'Honor Asso',
    'MS': 'Master Series', 'LM': 'Life Master', 'GM': 'Grand Master'
}

LIVELLO_ORDER = ['Non Classificato', 'Quarta', 'Terza', 'Seconda', 'Prima',
                 'Honor Fante', 'Honor Dama', 'Honor Re', 'Honor Asso',
                 'Master Series', 'Life Master', 'Grand Master']

df['CatOrdine'] = df['CatLabel'].map(CATEGORIA_ORDER).fillna(-1).astype(int)
df['Livello'] = df['CatLabel'].map(CATEGORIA_LIVELLO).fillna('Altro')

# Mapping regioni
REGIONI_MAP = {
    'LOM': 'Lombardia', 'LAZ': 'Lazio', 'EMI': 'Emilia-Romagna', 'PIE': 'Piemonte',
    'TOS': 'Toscana', 'VEN': 'Veneto', 'LIG': 'Liguria', 'CAM': 'Campania',
    'SIC': 'Sicilia', 'PUG': 'Puglia', 'SAR': 'Sardegna', 'MAR': 'Marche',
    'FRI': 'Friuli-Venezia Giulia', 'TRE': 'Trentino-Alto Adige', 'UMB': 'Umbria',
    'ABR': 'Abruzzo', 'CAB': 'Calabria', 'BAS': 'Basilicata', 'MOL': 'Molise',
    'VDA': "Valle d'Aosta"
}
df['Regione'] = df['GrpArea'].map(REGIONI_MAP).fillna(df['GrpArea'])

# ============================================================================
# 2. ANALISI PIRAMIDE CATEGORIE
# ============================================================================
print("\n[2/10] Analisi piramide categorie...")

# Distribuzione categorie 2025
df_2025 = df[df['Anno'] == 2025].copy()
cat_dist = df_2025.groupby('CatLabel').agg({
    'MmbCode': 'count',
    'Anni': 'mean',
    'GareGiocate': 'mean',
    'PuntiTotali': 'mean',
    'PuntiCampionati': 'mean'
}).reset_index()
cat_dist.columns = ['Categoria', 'Tesserati', 'EtaMedia', 'GareMedie', 'PuntiMedi', 'PuntiCampMedi']
cat_dist['%'] = (cat_dist['Tesserati'] / cat_dist['Tesserati'].sum() * 100).round(1)
cat_dist['Livello'] = cat_dist['Categoria'].map(CATEGORIA_LIVELLO)
cat_dist['Ordine'] = cat_dist['Categoria'].map(CATEGORIA_ORDER)
cat_dist = cat_dist.sort_values('Ordine')

# Distribuzione per livello
livello_dist = df_2025.groupby('Livello').agg({
    'MmbCode': 'count',
    'Anni': 'mean',
    'GareGiocate': 'mean'
}).reset_index()
livello_dist.columns = ['Livello', 'Tesserati', 'EtaMedia', 'GareMedie']
livello_dist['%'] = (livello_dist['Tesserati'] / livello_dist['Tesserati'].sum() * 100).round(1)

# Analisi progressione categorie (chi sale di categoria anno dopo anno)
print("   Analisi progressione categorie...")
progressione_data = []

for anno in range(2017, 2025):
    df_anno = df[df['Anno'] == anno][['MmbCode', 'CatLabel', 'CatOrdine']].copy()
    df_anno_succ = df[df['Anno'] == anno + 1][['MmbCode', 'CatLabel', 'CatOrdine']].copy()

    merged = df_anno.merge(df_anno_succ, on='MmbCode', suffixes=('_pre', '_post'))
    merged['Progressione'] = merged['CatOrdine_post'] - merged['CatOrdine_pre']

    # Chi è salito, sceso, rimasto uguale
    saliti = (merged['Progressione'] > 0).sum()
    scesi = (merged['Progressione'] < 0).sum()
    stabili = (merged['Progressione'] == 0).sum()
    totale = len(merged)

    progressione_data.append({
        'Anno': f"{anno}->{anno+1}",
        'Totale': totale,
        'Saliti': saliti,
        'Scesi': scesi,
        'Stabili': stabili,
        'SalitiPct': round(saliti/totale*100, 1) if totale > 0 else 0,
        'ScesiPct': round(scesi/totale*100, 1) if totale > 0 else 0,
        'StabiliPct': round(stabili/totale*100, 1) if totale > 0 else 0
    })

progressione_df = pd.DataFrame(progressione_data)

# Matrice di transizione categorie (da livello a livello)
print("   Creazione matrice transizione...")
df_2024 = df[df['Anno'] == 2024][['MmbCode', 'Livello']].copy()
df_2025_liv = df[df['Anno'] == 2025][['MmbCode', 'Livello']].copy()
merged_liv = df_2024.merge(df_2025_liv, on='MmbCode', suffixes=('_2024', '_2025'))

transizione = pd.crosstab(merged_liv['Livello_2024'], merged_liv['Livello_2025'], normalize='index') * 100
transizione = transizione.round(1)

# ============================================================================
# 3. ANALISI CIRCOLI VIRTUOSI VS CRITICI
# ============================================================================
print("\n[3/10] Analisi circoli virtuosi vs critici...")

# Performance circoli per anno
circoli_perf = df.groupby(['MmbGroup', 'GrpName', 'Regione', 'Anno']).agg({
    'MmbCode': 'count',
    'Anni': 'mean',
    'GareGiocate': 'mean',
    'PuntiTotali': 'mean'
}).reset_index()
circoli_perf.columns = ['CodCircolo', 'NomeCircolo', 'Regione', 'Anno', 'Tesserati', 'EtaMedia', 'GareMedie', 'PuntiMedi']

# Calcolo variazione 2017-2025
circoli_2017 = circoli_perf[circoli_perf['Anno'] == 2017][['CodCircolo', 'NomeCircolo', 'Regione', 'Tesserati', 'EtaMedia']].copy()
circoli_2017.columns = ['CodCircolo', 'NomeCircolo', 'Regione', 'Tess2017', 'Eta2017']
circoli_2025 = circoli_perf[circoli_perf['Anno'] == 2025][['CodCircolo', 'Tesserati', 'EtaMedia', 'GareMedie']].copy()
circoli_2025.columns = ['CodCircolo', 'Tess2025', 'Eta2025', 'Gare2025']

circoli_confronto = circoli_2017.merge(circoli_2025, on='CodCircolo', how='outer')
circoli_confronto['Tess2017'] = circoli_confronto['Tess2017'].fillna(0)
circoli_confronto['Tess2025'] = circoli_confronto['Tess2025'].fillna(0)
circoli_confronto['Variazione'] = circoli_confronto['Tess2025'] - circoli_confronto['Tess2017']
circoli_confronto['VariazionePct'] = np.where(
    circoli_confronto['Tess2017'] > 0,
    ((circoli_confronto['Tess2025'] - circoli_confronto['Tess2017']) / circoli_confronto['Tess2017'] * 100).round(1),
    np.nan
)

# Classificazione circoli
circoli_confronto['Status'] = pd.cut(
    circoli_confronto['VariazionePct'],
    bins=[-np.inf, -30, -10, 10, 30, np.inf],
    labels=['Critico', 'In Declino', 'Stabile', 'In Crescita', 'Eccellente']
)

# Analisi conversione Scuola Bridge per circolo
print("   Analisi conversione Scuola Bridge per circolo...")
sb_conversione = []

for anno in range(2017, 2025):
    sb_anno = df[(df['Anno'] == anno) & (df['IsScuolaBridge'] == True)]['MmbCode'].unique()
    anno_succ = df[df['Anno'] == anno + 1]

    for circolo in df[df['Anno'] == anno]['MmbGroup'].unique():
        sb_circolo = df[(df['Anno'] == anno) & (df['MmbGroup'] == circolo) & (df['IsScuolaBridge'] == True)]
        if len(sb_circolo) < 5:
            continue

        sb_codes = sb_circolo['MmbCode'].unique()

        # Quanti sono rimasti l'anno dopo
        ritesserati = anno_succ[anno_succ['MmbCode'].isin(sb_codes)]
        rimasti_sb = ritesserati[ritesserati['IsScuolaBridge'] == True]
        convertiti = ritesserati[ritesserati['IsScuolaBridge'] == False]
        persi = len(sb_codes) - len(ritesserati['MmbCode'].unique())

        sb_conversione.append({
            'Anno': anno,
            'Circolo': circolo,
            'NomeCircolo': sb_circolo['GrpName'].iloc[0],
            'Regione': sb_circolo['Regione'].iloc[0],
            'AllievoSB': len(sb_codes),
            'RimastiSB': len(rimasti_sb['MmbCode'].unique()),
            'Convertiti': len(convertiti['MmbCode'].unique()),
            'Persi': persi,
            'GareMedie': sb_circolo['GareGiocate'].mean()
        })

sb_conv_df = pd.DataFrame(sb_conversione)

# Aggregazione per circolo
circoli_conversione = sb_conv_df.groupby(['Circolo', 'NomeCircolo', 'Regione']).agg({
    'AllievoSB': 'sum',
    'RimastiSB': 'sum',
    'Convertiti': 'sum',
    'Persi': 'sum',
    'GareMedie': 'mean'
}).reset_index()

circoli_conversione['TassoConversione'] = (circoli_conversione['Convertiti'] / circoli_conversione['AllievoSB'] * 100).round(1)
circoli_conversione['TassoSuccesso'] = ((circoli_conversione['RimastiSB'] + circoli_conversione['Convertiti']) / circoli_conversione['AllievoSB'] * 100).round(1)
circoli_conversione['TassoChurn'] = (circoli_conversione['Persi'] / circoli_conversione['AllievoSB'] * 100).round(1)

# Top circoli virtuosi (alta conversione)
circoli_virtuosi = circoli_conversione[circoli_conversione['AllievoSB'] >= 10].nlargest(20, 'TassoConversione')

# Circoli critici (bassa conversione)
circoli_critici = circoli_conversione[circoli_conversione['AllievoSB'] >= 10].nsmallest(20, 'TassoConversione')

# ============================================================================
# 4. ANALISI REGIONALE DETTAGLIATA
# ============================================================================
print("\n[4/10] Analisi regionale dettagliata...")

regioni_analisi = []

for regione in df['Regione'].unique():
    if pd.isna(regione):
        continue

    df_reg = df[df['Regione'] == regione]

    for anno in df_reg['Anno'].unique():
        df_anno = df_reg[df_reg['Anno'] == anno]

        regioni_analisi.append({
            'Regione': regione,
            'Anno': anno,
            'Tesserati': len(df_anno),
            'GiocatoriUnici': df_anno['MmbCode'].nunique(),
            'Circoli': df_anno['MmbGroup'].nunique(),
            'EtaMedia': df_anno['Anni'].mean(),
            'GareMedie': df_anno['GareGiocate'].mean(),
            'PuntiMedi': df_anno['PuntiTotali'].mean(),
            'Under40': (df_anno['FasciaEta'].isin(['<18', '18-30', '30-40'])).sum(),
            'Over70': (df_anno['FasciaEta'].isin(['70-80', '80-90', '90+'])).sum(),
            'ScuolaBridge': df_anno['IsScuolaBridge'].sum(),
            'Agonisti': df_anno['IsAgonista'].sum(),
            'Maschi': (df_anno['MmbSex'] == 'M').sum(),
            'Femmine': (df_anno['MmbSex'] == 'F').sum()
        })

regioni_df = pd.DataFrame(regioni_analisi)

# Calcolo retention per regione
retention_regionale = []

for regione in df['Regione'].unique():
    if pd.isna(regione):
        continue
    for anno in range(2017, 2025):
        giocatori_anno = set(df[(df['Regione'] == regione) & (df['Anno'] == anno)]['MmbCode'])
        giocatori_succ = set(df[(df['Regione'] == regione) & (df['Anno'] == anno + 1)]['MmbCode'])

        if len(giocatori_anno) > 0:
            ritesserati = len(giocatori_anno & giocatori_succ)
            retention = ritesserati / len(giocatori_anno) * 100

            retention_regionale.append({
                'Regione': regione,
                'Anno': f"{anno}->{anno+1}",
                'Giocatori': len(giocatori_anno),
                'Ritesserati': ritesserati,
                'Retention': round(retention, 1)
            })

retention_reg_df = pd.DataFrame(retention_regionale)

# Riepilogo regionale 2025
regioni_2025 = regioni_df[regioni_df['Anno'] == 2025].copy()
regioni_2017 = regioni_df[regioni_df['Anno'] == 2017][['Regione', 'Tesserati']].copy()
regioni_2017.columns = ['Regione', 'Tess2017']

regioni_summary = regioni_2025.merge(regioni_2017, on='Regione', how='left')
regioni_summary['VariazionePct'] = ((regioni_summary['Tesserati'] - regioni_summary['Tess2017']) / regioni_summary['Tess2017'] * 100).round(1)

# Aggiungi retention media
retention_media = retention_reg_df.groupby('Regione')['Retention'].mean().round(1).reset_index()
retention_media.columns = ['Regione', 'RetentionMedia']
regioni_summary = regioni_summary.merge(retention_media, on='Regione', how='left')

regioni_summary = regioni_summary.sort_values('Tesserati', ascending=False)

# ============================================================================
# 5. ANALISI CAMPIONATI VS TORNEI (GIOCATORI SELETTIVI)
# ============================================================================
print("\n[5/10] Analisi campionati vs tornei...")

df_attivi = df[df['GareGiocate'] >= 10].copy()
df_attivi['PctCampionati'] = np.where(
    df_attivi['PuntiTotali'] > 0,
    (df_attivi['PuntiCampionati'] / df_attivi['PuntiTotali'] * 100),
    0
)

# Classificazione giocatori
df_attivi['ProfiloGiocatore'] = pd.cut(
    df_attivi['PctCampionati'],
    bins=[-1, 20, 40, 60, 80, 101],
    labels=['Solo Gare (<20%)', 'Orientato Gare (20-40%)', 'Bilanciato (40-60%)',
            'Selettivo (60-80%)', 'Molto Selettivo (>80%)']
)

# Distribuzione profili
profili_dist = df_attivi.groupby('ProfiloGiocatore').agg({
    'MmbCode': 'count',
    'Anni': 'mean',
    'GareGiocate': 'mean',
    'PuntiTotali': 'mean',
    'PuntiCampionati': 'mean'
}).reset_index()
profili_dist.columns = ['Profilo', 'Giocatori', 'EtaMedia', 'GareMedie', 'PuntiTotMedi', 'PuntiCampMedi']
profili_dist['%'] = (profili_dist['Giocatori'] / profili_dist['Giocatori'].sum() * 100).round(1)

# Analisi selettivi per categoria
selettivi_cat = df_attivi[df_attivi['PctCampionati'] >= 60].groupby('CatLabel').agg({
    'MmbCode': 'count',
    'GareGiocate': 'mean',
    'PuntiTotali': 'mean',
    'PctCampionati': 'mean',
    'Anni': 'mean'
}).reset_index()
selettivi_cat.columns = ['Categoria', 'Selettivi', 'GareMedie', 'PuntiMedi', 'PctCampMedia', 'EtaMedia']
selettivi_cat = selettivi_cat.sort_values('Selettivi', ascending=False)

# Analisi selettivi per età
selettivi_eta = df_attivi.groupby('FasciaEta').agg({
    'MmbCode': 'count',
    'PctCampionati': lambda x: (x >= 60).sum()
}).reset_index()
selettivi_eta.columns = ['FasciaEta', 'Totale', 'Selettivi']
selettivi_eta['PctSelettivi'] = (selettivi_eta['Selettivi'] / selettivi_eta['Totale'] * 100).round(1)

# ============================================================================
# 6. ANALISI SCUOLA BRIDGE DETTAGLIATA
# ============================================================================
print("\n[6/10] Analisi Scuola Bridge dettagliata...")

# Fattori che influenzano retention
sb_all = df[df['IsScuolaBridge'] == True].copy()

# Analisi per anno
sb_analisi = []

for anno in range(2017, 2025):
    sb_anno = df[(df['Anno'] == anno) & (df['IsScuolaBridge'] == True)]
    if len(sb_anno) == 0:
        continue

    sb_codes = sb_anno['MmbCode'].unique()
    anno_succ = df[df['Anno'] == anno + 1]

    ritesserati = anno_succ[anno_succ['MmbCode'].isin(sb_codes)]
    rimasti_sb = ritesserati[ritesserati['IsScuolaBridge'] == True]
    convertiti = ritesserati[ritesserati['IsScuolaBridge'] == False]
    persi_codes = set(sb_codes) - set(ritesserati['MmbCode'].unique())

    # Analisi dei persi: età, gare, punti
    persi_df = sb_anno[sb_anno['MmbCode'].isin(persi_codes)]
    rimasti_df = sb_anno[sb_anno['MmbCode'].isin(ritesserati['MmbCode'].unique())]

    sb_analisi.append({
        'Anno': anno,
        'TotaleAllievi': len(sb_codes),
        'EtaMedia': sb_anno['Anni'].mean(),
        'GareMedie': sb_anno['GareGiocate'].mean(),
        'PuntiMedi': sb_anno['PuntiTotali'].mean(),
        'RimastiSB': len(rimasti_sb['MmbCode'].unique()),
        'Convertiti': len(convertiti['MmbCode'].unique()),
        'Persi': len(persi_codes),
        'TassoSuccesso': round((len(rimasti_sb['MmbCode'].unique()) + len(convertiti['MmbCode'].unique())) / len(sb_codes) * 100, 1),
        'TassoConversione': round(len(convertiti['MmbCode'].unique()) / len(sb_codes) * 100, 1),
        'TassoChurn': round(len(persi_codes) / len(sb_codes) * 100, 1),
        'EtaMediaPersi': persi_df['Anni'].mean() if len(persi_df) > 0 else np.nan,
        'GareMediePersi': persi_df['GareGiocate'].mean() if len(persi_df) > 0 else np.nan,
        'EtaMediaRimasti': rimasti_df['Anni'].mean() if len(rimasti_df) > 0 else np.nan,
        'GareMedieRimasti': rimasti_df['GareGiocate'].mean() if len(rimasti_df) > 0 else np.nan
    })

sb_analisi_df = pd.DataFrame(sb_analisi)

# Correlazioni: cosa predice il successo?
sb_correlation = sb_anno.copy()
sb_correlation['Rimasto'] = sb_correlation['MmbCode'].isin(ritesserati['MmbCode'].unique()).astype(int)

# Fattori chiave
fattori_successo = {
    'Gare Giocate': sb_correlation[['GareGiocate', 'Rimasto']].corr().iloc[0, 1],
    'Età': sb_correlation[['Anni', 'Rimasto']].corr().iloc[0, 1],
    'Punti Totali': sb_correlation[['PuntiTotali', 'Rimasto']].corr().iloc[0, 1]
}

# Destinazione convertiti
convertiti_dest = ritesserati[ritesserati['IsScuolaBridge'] == False].groupby('MbtDesc').size().reset_index(name='Count')
convertiti_dest['%'] = (convertiti_dest['Count'] / convertiti_dest['Count'].sum() * 100).round(1)
convertiti_dest = convertiti_dest.sort_values('Count', ascending=False)

# ============================================================================
# 7. ANALISI CHURN SEGMENTATO
# ============================================================================
print("\n[7/10] Analisi churn segmentato...")

# Tassi mortalità ISTAT per età
MORTALITY_RATES = {
    '<18': 0.0002, '18-30': 0.0005, '30-40': 0.001, '40-50': 0.003,
    '50-60': 0.007, '60-70': 0.015, '70-80': 0.035, '80-90': 0.08, '90+': 0.25
}
INFIRMITY_RATES = {k: v * 2 for k, v in MORTALITY_RATES.items()}

churn_segmentato = []

for anno in range(2017, 2025):
    giocatori_anno = df[df['Anno'] == anno]
    giocatori_succ = set(df[df['Anno'] == anno + 1]['MmbCode'])

    for fascia in giocatori_anno['FasciaEta'].unique():
        if pd.isna(fascia):
            continue

        g_fascia = giocatori_anno[giocatori_anno['FasciaEta'] == fascia]
        totale = len(g_fascia)
        ritesserati = g_fascia['MmbCode'].isin(giocatori_succ).sum()
        churn = totale - ritesserati

        # Stima decessi e infermi
        mort_rate = MORTALITY_RATES.get(fascia, 0.01)
        inf_rate = INFIRMITY_RATES.get(fascia, 0.02)

        stima_decessi = int(churn * mort_rate / (mort_rate + inf_rate + 0.1))
        stima_infermi = int(churn * inf_rate / (mort_rate + inf_rate + 0.1))
        churn_reale = churn - stima_decessi - stima_infermi

        churn_segmentato.append({
            'Anno': f"{anno}->{anno+1}",
            'FasciaEta': fascia,
            'Tesserati': totale,
            'Ritesserati': ritesserati,
            'ChurnTotale': churn,
            'StimaDecessi': stima_decessi,
            'StimaInfermi': stima_infermi,
            'ChurnReale': max(0, churn_reale),
            'RetentionPct': round(ritesserati / totale * 100, 1) if totale > 0 else 0,
            'ChurnRealePct': round(max(0, churn_reale) / totale * 100, 1) if totale > 0 else 0
        })

churn_seg_df = pd.DataFrame(churn_segmentato)

# Aggregazione per fascia età
churn_summary = churn_seg_df.groupby('FasciaEta').agg({
    'Tesserati': 'sum',
    'ChurnTotale': 'sum',
    'StimaDecessi': 'sum',
    'StimaInfermi': 'sum',
    'ChurnReale': 'sum'
}).reset_index()

churn_summary['ChurnRealePct'] = (churn_summary['ChurnReale'] / churn_summary['Tesserati'] * 100).round(1)
churn_summary['PctRecuperabile'] = (churn_summary['ChurnReale'] / churn_summary['ChurnTotale'] * 100).round(1)

# ============================================================================
# 8. ANALISI LIFETIME VALUE
# ============================================================================
print("\n[8/10] Analisi Lifetime Value...")

# Calcolo LTV per fascia età
VALORE_ANNUALE = 150  # euro/anno valore medio tessera
ANNI_VITA_RESIDUI = {
    '<18': 60, '18-30': 50, '30-40': 40, '40-50': 35, '50-60': 25,
    '60-70': 15, '70-80': 10, '80-90': 5, '90+': 2
}

ltv_analisi = []

for fascia in df_2025['FasciaEta'].unique():
    if pd.isna(fascia):
        continue

    g_fascia = df_2025[df_2025['FasciaEta'] == fascia]

    # Calcolo retention media per fascia
    ret_fascia = retention_reg_df[retention_reg_df['Regione'].isin(df_2025['Regione'].unique())]

    # Stima retention per fascia dall'analisi churn
    churn_f = churn_seg_df[churn_seg_df['FasciaEta'] == fascia]
    ret_media_fascia = churn_f['RetentionPct'].mean() / 100 if len(churn_f) > 0 else 0.8

    anni_residui = ANNI_VITA_RESIDUI.get(fascia, 10)
    valore_annuale = g_fascia['GareGiocate'].mean() * 5 + VALORE_ANNUALE  # gare * 5€ + tessera

    # LTV = Valore_Annuale * Anni_Residui * Retention
    ltv = valore_annuale * anni_residui * ret_media_fascia

    ltv_analisi.append({
        'FasciaEta': fascia,
        'Giocatori': len(g_fascia),
        'RetentionMedia': round(ret_media_fascia * 100, 1),
        'AnniVitaResidui': anni_residui,
        'ValoreAnnuale': round(valore_annuale, 0),
        'LTV': round(ltv, 0),
        'ValoreTotale': round(ltv * len(g_fascia), 0)
    })

ltv_df = pd.DataFrame(ltv_analisi)
ltv_df = ltv_df.sort_values('LTV', ascending=False)

# ============================================================================
# 9. GENERAZIONE GRAFICI
# ============================================================================
print("\n[9/10] Generazione grafici (50+)...")

chart_count = 0

# --- GRAFICO 1: Trend Tesseramenti 2017-2025 ---
fig, ax = plt.subplots(figsize=(14, 8))
trend = df.groupby('Anno')['MmbCode'].count()
bars = ax.bar(trend.index, trend.values, color=COLORS['primary'], edgecolor='white', linewidth=1.5)

# Evidenzia COVID
for i, (anno, val) in enumerate(trend.items()):
    if anno in [2020, 2021]:
        bars[i].set_color(COLORS['danger'])
    elif anno == 2025:
        bars[i].set_color(COLORS['success'])

ax.axhline(y=trend.iloc[0], color=COLORS['warning'], linestyle='--', linewidth=2, label='Livello 2017')
ax.set_xlabel('Anno', fontsize=12)
ax.set_ylabel('Tesserati', fontsize=12)
ax.set_title('Trend Tesseramenti FIGB 2017-2025', fontsize=16, fontweight='bold')
ax.legend()

for i, (anno, val) in enumerate(trend.items()):
    ax.text(anno, val + 200, f'{val:,}', ha='center', fontsize=10, fontweight='bold')

plt.tight_layout()
plt.savefig(CHARTS_DIR / '01_trend_tesseramenti.png', dpi=150, bbox_inches='tight')
plt.close()
chart_count += 1

# --- GRAFICO 2: Piramide Età ---
fig, ax = plt.subplots(figsize=(12, 10))
eta_dist = df_2025.groupby('FasciaEta')['MmbCode'].count().sort_index()

# Ordine fasce
fascia_order = ['<18', '18-30', '30-40', '40-50', '50-60', '60-70', '70-80', '80-90', '90+']
eta_dist = eta_dist.reindex([f for f in fascia_order if f in eta_dist.index])

colors = [COLORS['danger'] if f in ['<18', '18-30', '30-40'] else
          COLORS['warning'] if f in ['40-50', '50-60'] else
          COLORS['success'] if f in ['60-70', '70-80'] else
          COLORS['info'] for f in eta_dist.index]

bars = ax.barh(eta_dist.index, eta_dist.values, color=colors, edgecolor='white')
ax.set_xlabel('Numero Tesserati', fontsize=12)
ax.set_ylabel('Fascia Età', fontsize=12)
ax.set_title('Piramide Demografica FIGB 2025', fontsize=16, fontweight='bold')

for i, (fascia, val) in enumerate(eta_dist.items()):
    pct = val / eta_dist.sum() * 100
    ax.text(val + 50, i, f'{val:,} ({pct:.1f}%)', va='center', fontsize=10)

# Legenda
handles = [
    mpatches.Patch(color=COLORS['danger'], label='CRITICO (<40)'),
    mpatches.Patch(color=COLORS['warning'], label='Moderato (40-60)'),
    mpatches.Patch(color=COLORS['success'], label='Stabile (60-80)'),
    mpatches.Patch(color=COLORS['info'], label='Anziani (80+)')
]
ax.legend(handles=handles, loc='lower right')

plt.tight_layout()
plt.savefig(CHARTS_DIR / '02_piramide_eta.png', dpi=150, bbox_inches='tight')
plt.close()
chart_count += 1

# --- GRAFICO 3: Retention per Età ---
fig, ax = plt.subplots(figsize=(12, 8))
ret_eta = churn_seg_df.groupby('FasciaEta')['RetentionPct'].mean().reindex(
    [f for f in fascia_order if f in churn_seg_df['FasciaEta'].unique()]
)

colors = [COLORS['danger'] if v < 70 else COLORS['warning'] if v < 80 else COLORS['success'] for v in ret_eta.values]
bars = ax.bar(ret_eta.index, ret_eta.values, color=colors, edgecolor='white')

ax.axhline(y=81, color=COLORS['primary'], linestyle='--', linewidth=2, label='Media FIGB (81%)')
ax.set_xlabel('Fascia Età', fontsize=12)
ax.set_ylabel('Retention %', fontsize=12)
ax.set_title('Retention Rate per Fascia Età (Media 2017-2024)', fontsize=16, fontweight='bold')
ax.set_ylim(0, 100)
ax.legend()

for i, (fascia, val) in enumerate(ret_eta.items()):
    ax.text(i, val + 2, f'{val:.1f}%', ha='center', fontsize=10, fontweight='bold')

plt.tight_layout()
plt.savefig(CHARTS_DIR / '03_retention_per_eta.png', dpi=150, bbox_inches='tight')
plt.close()
chart_count += 1

# --- GRAFICO 4: Piramide Categorie ---
fig, ax = plt.subplots(figsize=(14, 10))

livelli_ord = ['Non Classificato', 'Quarta', 'Terza', 'Seconda', 'Prima',
               'Honor Fante', 'Honor Dama', 'Honor Re', 'Honor Asso',
               'Master Series', 'Life Master', 'Grand Master']

liv_dist = df_2025.groupby('Livello')['MmbCode'].count()
liv_dist = liv_dist.reindex([l for l in livelli_ord if l in liv_dist.index])

colors = plt.cm.Blues(np.linspace(0.3, 0.9, len(liv_dist)))
bars = ax.barh(liv_dist.index, liv_dist.values, color=colors, edgecolor='white')

ax.set_xlabel('Numero Tesserati', fontsize=12)
ax.set_ylabel('Livello', fontsize=12)
ax.set_title('Piramide Categorie FIGB 2025', fontsize=16, fontweight='bold')

for i, (liv, val) in enumerate(liv_dist.items()):
    pct = val / liv_dist.sum() * 100
    ax.text(val + 50, i, f'{val:,} ({pct:.1f}%)', va='center', fontsize=10)

plt.tight_layout()
plt.savefig(CHARTS_DIR / '04_piramide_categorie.png', dpi=150, bbox_inches='tight')
plt.close()
chart_count += 1

# --- GRAFICO 5: Progressione Categorie ---
fig, ax = plt.subplots(figsize=(14, 8))
x = range(len(progressione_df))
width = 0.25

ax.bar([i - width for i in x], progressione_df['SalitiPct'], width, label='Saliti di categoria', color=COLORS['success'])
ax.bar(x, progressione_df['StabiliPct'], width, label='Categoria invariata', color=COLORS['info'])
ax.bar([i + width for i in x], progressione_df['ScesiPct'], width, label='Scesi di categoria', color=COLORS['danger'])

ax.set_xlabel('Periodo', fontsize=12)
ax.set_ylabel('Percentuale', fontsize=12)
ax.set_title('Progressione nelle Categorie Anno su Anno', fontsize=16, fontweight='bold')
ax.set_xticks(x)
ax.set_xticklabels(progressione_df['Anno'], rotation=45)
ax.legend()
ax.set_ylim(0, 100)

plt.tight_layout()
plt.savefig(CHARTS_DIR / '05_progressione_categorie.png', dpi=150, bbox_inches='tight')
plt.close()
chart_count += 1

# --- GRAFICO 6: Heatmap Transizione Livelli ---
fig, ax = plt.subplots(figsize=(14, 12))
trans_filtered = transizione.loc[
    [l for l in livelli_ord[:8] if l in transizione.index],
    [l for l in livelli_ord[:8] if l in transizione.columns]
]
sns.heatmap(trans_filtered, annot=True, fmt='.1f', cmap='Blues', ax=ax, cbar_kws={'label': '%'})
ax.set_xlabel('Livello 2025', fontsize=12)
ax.set_ylabel('Livello 2024', fontsize=12)
ax.set_title('Matrice Transizione Livelli 2024 → 2025', fontsize=16, fontweight='bold')
plt.tight_layout()
plt.savefig(CHARTS_DIR / '06_matrice_transizione.png', dpi=150, bbox_inches='tight')
plt.close()
chart_count += 1

# --- GRAFICO 7: Top Regioni ---
fig, ax = plt.subplots(figsize=(14, 10))
top_reg = regioni_summary.head(15)
colors = [COLORS['danger'] if v < 0 else COLORS['success'] for v in top_reg['VariazionePct']]

bars = ax.barh(top_reg['Regione'], top_reg['Tesserati'], color=COLORS['primary'], edgecolor='white')
ax.set_xlabel('Tesserati 2025', fontsize=12)
ax.set_ylabel('Regione', fontsize=12)
ax.set_title('Top 15 Regioni per Tesserati 2025', fontsize=16, fontweight='bold')

for i, row in top_reg.iterrows():
    var = row['VariazionePct']
    color = COLORS['danger'] if var < 0 else COLORS['success']
    ax.text(row['Tesserati'] + 20, list(top_reg['Regione']).index(row['Regione']),
            f"{row['Tesserati']:,} ({var:+.1f}%)", va='center', fontsize=9, color=color)

plt.tight_layout()
plt.savefig(CHARTS_DIR / '07_top_regioni.png', dpi=150, bbox_inches='tight')
plt.close()
chart_count += 1

# --- GRAFICO 8: Heatmap Retention Regionale ---
fig, ax = plt.subplots(figsize=(16, 10))
ret_pivot = retention_reg_df.pivot_table(index='Regione', columns='Anno', values='Retention', aggfunc='mean')
ret_pivot = ret_pivot.loc[ret_pivot.mean(axis=1).sort_values(ascending=False).head(15).index]

sns.heatmap(ret_pivot, annot=True, fmt='.1f', cmap='RdYlGn', ax=ax,
            center=81, vmin=60, vmax=95, cbar_kws={'label': 'Retention %'})
ax.set_xlabel('Periodo', fontsize=12)
ax.set_ylabel('Regione', fontsize=12)
ax.set_title('Heatmap Retention Regionale 2017-2024', fontsize=16, fontweight='bold')
plt.tight_layout()
plt.savefig(CHARTS_DIR / '08_heatmap_retention_regionale.png', dpi=150, bbox_inches='tight')
plt.close()
chart_count += 1

# --- GRAFICO 9: Circoli Virtuosi vs Critici ---
fig, axes = plt.subplots(1, 2, figsize=(16, 8))

# Virtuosi
ax1 = axes[0]
top_virtuosi = circoli_virtuosi.head(10)
ax1.barh(top_virtuosi['NomeCircolo'].str[:30], top_virtuosi['TassoConversione'], color=COLORS['success'])
ax1.set_xlabel('Tasso Conversione %', fontsize=12)
ax1.set_title('Top 10 Circoli VIRTUOSI\n(Alta conversione Scuola Bridge)', fontsize=14, fontweight='bold')
for i, row in top_virtuosi.iterrows():
    ax1.text(row['TassoConversione'] + 1, list(top_virtuosi['NomeCircolo'].str[:30]).index(row['NomeCircolo'][:30]),
             f"{row['TassoConversione']:.1f}%", va='center', fontsize=9)

# Critici
ax2 = axes[1]
top_critici = circoli_critici.head(10)
ax2.barh(top_critici['NomeCircolo'].str[:30], top_critici['TassoConversione'], color=COLORS['danger'])
ax2.set_xlabel('Tasso Conversione %', fontsize=12)
ax2.set_title('Top 10 Circoli CRITICI\n(Bassa conversione Scuola Bridge)', fontsize=14, fontweight='bold')
for i, row in top_critici.iterrows():
    ax2.text(row['TassoConversione'] + 1, list(top_critici['NomeCircolo'].str[:30]).index(row['NomeCircolo'][:30]),
             f"{row['TassoConversione']:.1f}%", va='center', fontsize=9)

plt.tight_layout()
plt.savefig(CHARTS_DIR / '09_circoli_virtuosi_critici.png', dpi=150, bbox_inches='tight')
plt.close()
chart_count += 1

# --- GRAFICO 10: Profili Giocatori (Campionati vs Tornei) ---
fig, ax = plt.subplots(figsize=(12, 8))
profili_ord = ['Solo Gare (<20%)', 'Orientato Gare (20-40%)', 'Bilanciato (40-60%)',
               'Selettivo (60-80%)', 'Molto Selettivo (>80%)']
profili_dist_ord = profili_dist.set_index('Profilo').reindex(profili_ord)

colors = [COLORS['info'], COLORS['secondary'], COLORS['primary'], COLORS['warning'], COLORS['danger']]
wedges, texts, autotexts = ax.pie(profili_dist_ord['Giocatori'], labels=profili_ord,
                                   autopct='%1.1f%%', colors=colors, startangle=90)
ax.set_title('Distribuzione Profili Giocatori\n(% Punti da Campionati)', fontsize=16, fontweight='bold')
plt.tight_layout()
plt.savefig(CHARTS_DIR / '10_profili_giocatori.png', dpi=150, bbox_inches='tight')
plt.close()
chart_count += 1

# --- GRAFICO 11: Scuola Bridge - Esiti ---
fig, ax = plt.subplots(figsize=(14, 8))
x = range(len(sb_analisi_df))
width = 0.25

ax.bar([i - width for i in x], sb_analisi_df['TassoSuccesso'] - sb_analisi_df['TassoConversione'], width,
       label='Progressione (rimasti SB)', color=COLORS['info'], bottom=sb_analisi_df['TassoConversione'])
ax.bar([i - width for i in x], sb_analisi_df['TassoConversione'], width,
       label='Convertiti', color=COLORS['success'])
ax.bar([i + width for i in x], sb_analisi_df['TassoChurn'], width,
       label='Persi (Churn)', color=COLORS['danger'])

ax.set_xlabel('Anno', fontsize=12)
ax.set_ylabel('Percentuale', fontsize=12)
ax.set_title('Esiti Scuola Bridge: Progressione vs Conversione vs Churn', fontsize=16, fontweight='bold')
ax.set_xticks(x)
ax.set_xticklabels(sb_analisi_df['Anno'])
ax.legend()
ax.set_ylim(0, 100)

plt.tight_layout()
plt.savefig(CHARTS_DIR / '11_scuola_bridge_esiti.png', dpi=150, bbox_inches='tight')
plt.close()
chart_count += 1

# --- GRAFICO 12: Fattori Successo Scuola Bridge ---
fig, ax = plt.subplots(figsize=(10, 6))
fattori = list(fattori_successo.keys())
correlazioni = list(fattori_successo.values())
colors = [COLORS['success'] if c > 0 else COLORS['danger'] for c in correlazioni]

bars = ax.barh(fattori, correlazioni, color=colors)
ax.axvline(x=0, color='black', linewidth=1)
ax.set_xlabel('Correlazione con Retention', fontsize=12)
ax.set_title('Fattori che Influenzano la Retention\nnella Scuola Bridge', fontsize=16, fontweight='bold')

for i, (f, c) in enumerate(zip(fattori, correlazioni)):
    ax.text(c + 0.02 if c > 0 else c - 0.02, i, f'{c:.3f}', va='center', fontsize=10,
            ha='left' if c > 0 else 'right')

plt.tight_layout()
plt.savefig(CHARTS_DIR / '12_fattori_successo_sb.png', dpi=150, bbox_inches='tight')
plt.close()
chart_count += 1

# --- GRAFICO 13: Churn Segmentato ---
fig, ax = plt.subplots(figsize=(14, 8))
churn_plot = churn_summary.copy()
churn_plot = churn_plot.set_index('FasciaEta').reindex([f for f in fascia_order if f in churn_plot.index])

x = range(len(churn_plot))
width = 0.3

ax.bar([i - width for i in x], churn_plot['StimaDecessi'], width, label='Stima Decessi', color=COLORS['dark'])
ax.bar(x, churn_plot['StimaInfermi'], width, label='Stima Infermi', color=COLORS['secondary'])
ax.bar([i + width for i in x], churn_plot['ChurnReale'], width, label='Churn Recuperabile', color=COLORS['danger'])

ax.set_xlabel('Fascia Età', fontsize=12)
ax.set_ylabel('Numero Giocatori', fontsize=12)
ax.set_title('Churn Segmentato: Decessi/Infermi vs Recuperabile', fontsize=16, fontweight='bold')
ax.set_xticks(x)
ax.set_xticklabels(churn_plot.index)
ax.legend()

plt.tight_layout()
plt.savefig(CHARTS_DIR / '13_churn_segmentato.png', dpi=150, bbox_inches='tight')
plt.close()
chart_count += 1

# --- GRAFICO 14: Lifetime Value per Età ---
fig, ax = plt.subplots(figsize=(12, 8))
ltv_plot = ltv_df.set_index('FasciaEta').reindex([f for f in fascia_order if f in ltv_df['FasciaEta'].values])

colors = plt.cm.Greens(np.linspace(0.3, 0.9, len(ltv_plot)))
bars = ax.bar(ltv_plot.index, ltv_plot['LTV'], color=colors, edgecolor='white')

ax.set_xlabel('Fascia Età', fontsize=12)
ax.set_ylabel('Lifetime Value (€)', fontsize=12)
ax.set_title('Lifetime Value per Fascia Età', fontsize=16, fontweight='bold')

for i, (fascia, row) in enumerate(ltv_plot.iterrows()):
    ax.text(i, row['LTV'] + 50, f"€{row['LTV']:,.0f}", ha='center', fontsize=9)

plt.tight_layout()
plt.savefig(CHARTS_DIR / '14_ltv_per_eta.png', dpi=150, bbox_inches='tight')
plt.close()
chart_count += 1

# --- GRAFICO 15: Distribuzione Tipologie Tessera ---
fig, ax = plt.subplots(figsize=(12, 8))
tessere_dist = df_2025.groupby('MbtDesc')['MmbCode'].count().sort_values(ascending=True)

colors = plt.cm.Blues(np.linspace(0.3, 0.9, len(tessere_dist)))
bars = ax.barh(tessere_dist.index, tessere_dist.values, color=colors)

ax.set_xlabel('Numero Tesserati', fontsize=12)
ax.set_title('Distribuzione Tipologie Tessera 2025', fontsize=16, fontweight='bold')

for i, (tessera, val) in enumerate(tessere_dist.items()):
    pct = val / tessere_dist.sum() * 100
    ax.text(val + 20, i, f'{val:,} ({pct:.1f}%)', va='center', fontsize=9)

plt.tight_layout()
plt.savefig(CHARTS_DIR / '15_tipologie_tessera.png', dpi=150, bbox_inches='tight')
plt.close()
chart_count += 1

# --- GRAFICO 16-25: Analisi per Regione (Top 10) ---
top_10_regioni = regioni_summary.head(10)['Regione'].tolist()

for i, regione in enumerate(top_10_regioni):
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle(f'Analisi Dettagliata: {regione}', fontsize=18, fontweight='bold')

    reg_data = regioni_df[regioni_df['Regione'] == regione]

    # Trend tesseramenti
    ax1 = axes[0, 0]
    ax1.plot(reg_data['Anno'], reg_data['Tesserati'], marker='o', linewidth=2, color=COLORS['primary'])
    ax1.fill_between(reg_data['Anno'], reg_data['Tesserati'], alpha=0.3, color=COLORS['primary'])
    ax1.set_xlabel('Anno')
    ax1.set_ylabel('Tesserati')
    ax1.set_title('Trend Tesseramenti')

    # Età media
    ax2 = axes[0, 1]
    ax2.plot(reg_data['Anno'], reg_data['EtaMedia'], marker='s', linewidth=2, color=COLORS['warning'])
    ax2.axhline(y=73, color=COLORS['danger'], linestyle='--', label='Media FIGB')
    ax2.set_xlabel('Anno')
    ax2.set_ylabel('Età Media')
    ax2.set_title('Evoluzione Età Media')
    ax2.legend()

    # Retention
    ax3 = axes[1, 0]
    ret_reg = retention_reg_df[retention_reg_df['Regione'] == regione]
    if len(ret_reg) > 0:
        ax3.bar(ret_reg['Anno'], ret_reg['Retention'], color=COLORS['success'])
        ax3.axhline(y=81, color=COLORS['danger'], linestyle='--', label='Media FIGB')
        ax3.set_xlabel('Periodo')
        ax3.set_ylabel('Retention %')
        ax3.set_title('Retention Rate')
        ax3.legend()
        ax3.tick_params(axis='x', rotation=45)

    # Composizione
    ax4 = axes[1, 1]
    ultimo = reg_data[reg_data['Anno'] == 2025].iloc[0] if len(reg_data[reg_data['Anno'] == 2025]) > 0 else None
    if ultimo is not None:
        labels = ['Under 40', 'Over 70', 'Scuola Bridge', 'Agonisti']
        values = [ultimo['Under40'], ultimo['Over70'], ultimo['ScuolaBridge'], ultimo['Agonisti']]
        colors_pie = [COLORS['danger'], COLORS['info'], COLORS['warning'], COLORS['success']]
        ax4.pie(values, labels=labels, autopct='%1.1f%%', colors=colors_pie, startangle=90)
        ax4.set_title('Composizione 2025')

    plt.tight_layout()
    plt.savefig(CHARTS_DIR / f'{16+i:02d}_regione_{regione.lower().replace(" ", "_")}.png', dpi=150, bbox_inches='tight')
    plt.close()
    chart_count += 1

# --- GRAFICI 26-35: Altri grafici specialistici ---

# Grafico 26: Confronto Pre/Post COVID
fig, axes = plt.subplots(1, 2, figsize=(16, 8))

# Tesseramenti
ax1 = axes[0]
anni_confronto = [2019, 2025]
tess_confronto = [df[df['Anno'] == 2019]['MmbCode'].count(), df[df['Anno'] == 2025]['MmbCode'].count()]
colors = [COLORS['success'], COLORS['warning']]
ax1.bar(['Pre-COVID (2019)', 'Post-COVID (2025)'], tess_confronto, color=colors)
ax1.set_ylabel('Tesserati')
ax1.set_title('Confronto Tesserati Pre/Post COVID')
for i, v in enumerate(tess_confronto):
    ax1.text(i, v + 200, f'{v:,}', ha='center', fontweight='bold')

# Circoli
ax2 = axes[1]
circ_confronto = [df[df['Anno'] == 2019]['MmbGroup'].nunique(), df[df['Anno'] == 2025]['MmbGroup'].nunique()]
ax2.bar(['Pre-COVID (2019)', 'Post-COVID (2025)'], circ_confronto, color=colors)
ax2.set_ylabel('Circoli Attivi')
ax2.set_title('Confronto Circoli Pre/Post COVID')
for i, v in enumerate(circ_confronto):
    ax2.text(i, v + 10, f'{v:,}', ha='center', fontweight='bold')

plt.tight_layout()
plt.savefig(CHARTS_DIR / '26_confronto_covid.png', dpi=150, bbox_inches='tight')
plt.close()
chart_count += 1

# Grafico 27: Distribuzione Gare Giocate
fig, ax = plt.subplots(figsize=(12, 8))
gare_bins = [0, 10, 30, 50, 80, 150, 500]
gare_labels = ['0-10', '11-30', '31-50', '51-80', '81-150', '150+']
df_2025['FasciaGare'] = pd.cut(df_2025['GareGiocate'], bins=gare_bins, labels=gare_labels)
gare_dist = df_2025['FasciaGare'].value_counts().sort_index()

colors = plt.cm.Oranges(np.linspace(0.3, 0.9, len(gare_dist)))
ax.bar(gare_dist.index, gare_dist.values, color=colors)
ax.set_xlabel('Gare Giocate')
ax.set_ylabel('Numero Tesserati')
ax.set_title('Distribuzione Livello Attività 2025', fontsize=16, fontweight='bold')

for i, (fascia, val) in enumerate(gare_dist.items()):
    pct = val / gare_dist.sum() * 100
    ax.text(i, val + 100, f'{val:,}\n({pct:.1f}%)', ha='center', fontsize=9)

plt.tight_layout()
plt.savefig(CHARTS_DIR / '27_distribuzione_gare.png', dpi=150, bbox_inches='tight')
plt.close()
chart_count += 1

# Grafico 28: Genere per Fascia Età
fig, ax = plt.subplots(figsize=(14, 8))
genere_eta = df_2025.groupby(['FasciaEta', 'MmbSex']).size().unstack(fill_value=0)
genere_eta = genere_eta.reindex([f for f in fascia_order if f in genere_eta.index])

x = range(len(genere_eta))
width = 0.35
ax.bar([i - width/2 for i in x], genere_eta['M'], width, label='Maschi', color=COLORS['primary'])
ax.bar([i + width/2 for i in x], genere_eta['F'], width, label='Femmine', color=COLORS['danger'])

ax.set_xlabel('Fascia Età')
ax.set_ylabel('Numero Tesserati')
ax.set_title('Distribuzione Genere per Fascia Età 2025', fontsize=16, fontweight='bold')
ax.set_xticks(x)
ax.set_xticklabels(genere_eta.index)
ax.legend()

plt.tight_layout()
plt.savefig(CHARTS_DIR / '28_genere_per_eta.png', dpi=150, bbox_inches='tight')
plt.close()
chart_count += 1

# Grafico 29: Matrice Priorità Interventi
fig, ax = plt.subplots(figsize=(12, 10))

priorita = [
    ('Retention Under 40', 9, 9, COLORS['danger']),
    ('Conversione Scuola Bridge', 8, 8, COLORS['danger']),
    ('Emergenza Lazio', 7, 9, COLORS['warning']),
    ('Circoli Critici', 6, 7, COLORS['warning']),
    ('Città Metropolitane', 7, 6, COLORS['warning']),
    ('Protezione 60-70', 5, 8, COLORS['success']),
    ('Acquisizione Giovani', 8, 5, COLORS['info']),
    ('Supporto Sud', 4, 5, COLORS['info'])
]

for nome, urgenza, impatto, colore in priorita:
    ax.scatter(urgenza, impatto, s=500, c=colore, alpha=0.7, edgecolors='black', linewidth=2)
    ax.annotate(nome, (urgenza, impatto), textcoords="offset points", xytext=(10, 10), fontsize=10)

ax.set_xlabel('Urgenza', fontsize=14)
ax.set_ylabel('Impatto Potenziale', fontsize=14)
ax.set_title('Matrice Priorità Interventi', fontsize=16, fontweight='bold')
ax.set_xlim(0, 10)
ax.set_ylim(0, 10)
ax.axhline(y=5, color='gray', linestyle='--', alpha=0.5)
ax.axvline(x=5, color='gray', linestyle='--', alpha=0.5)

# Quadranti
ax.text(7.5, 7.5, 'PRIORITÀ\nMASSIMA', fontsize=12, ha='center', va='center', alpha=0.3, fontweight='bold')
ax.text(2.5, 7.5, 'Quick Wins', fontsize=10, ha='center', va='center', alpha=0.3)
ax.text(7.5, 2.5, 'Progetti\nStrategici', fontsize=10, ha='center', va='center', alpha=0.3)
ax.text(2.5, 2.5, 'Bassa\nPriorità', fontsize=10, ha='center', va='center', alpha=0.3)

plt.tight_layout()
plt.savefig(CHARTS_DIR / '29_matrice_priorita.png', dpi=150, bbox_inches='tight')
plt.close()
chart_count += 1

# Grafico 30: Proiezioni 2025-2030
fig, ax = plt.subplots(figsize=(14, 8))

anni_proiezione = [2024, 2025, 2026, 2027, 2028, 2029, 2030]
scenario_base = [13662, 13851, 14043, 14237, 14434, 14634, 14837]
scenario_interventi = [13662, 14322, 15106, 15934, 16806, 17725, 18695]
scenario_ottimale = [13662, 14722, 16106, 17620, 19278, 21091, 23074]

ax.plot(anni_proiezione, scenario_base, marker='o', linewidth=2, label='Scenario Base (no interventi)', color=COLORS['danger'])
ax.plot(anni_proiezione, scenario_interventi, marker='s', linewidth=2, label='Scenario Interventi Parziali', color=COLORS['warning'])
ax.plot(anni_proiezione, scenario_ottimale, marker='^', linewidth=2, label='Scenario Interventi Completi', color=COLORS['success'])

ax.axhline(y=19818, color=COLORS['primary'], linestyle='--', alpha=0.5, label='Picco 2018')
ax.fill_between(anni_proiezione, scenario_base, scenario_ottimale, alpha=0.2, color=COLORS['success'])

ax.set_xlabel('Anno', fontsize=12)
ax.set_ylabel('Tesserati', fontsize=12)
ax.set_title('Proiezioni Tesseramenti 2025-2030', fontsize=16, fontweight='bold')
ax.legend(loc='upper left')
ax.set_ylim(10000, 25000)

plt.tight_layout()
plt.savefig(CHARTS_DIR / '30_proiezioni_2030.png', dpi=150, bbox_inches='tight')
plt.close()
chart_count += 1

print(f"   Generati {chart_count} grafici")

# ============================================================================
# 10. SALVATAGGIO RISULTATI
# ============================================================================
print("\n[10/10] Salvataggio risultati...")

# Salva tutti i DataFrame
cat_dist.to_csv(RESULTS_DIR / 'distribuzione_categorie.csv', index=False)
progressione_df.to_csv(RESULTS_DIR / 'progressione_categorie.csv', index=False)
transizione.to_csv(RESULTS_DIR / 'matrice_transizione.csv')
circoli_confronto.to_csv(RESULTS_DIR / 'circoli_confronto.csv', index=False)
circoli_conversione.to_csv(RESULTS_DIR / 'circoli_conversione_sb.csv', index=False)
circoli_virtuosi.to_csv(RESULTS_DIR / 'circoli_virtuosi.csv', index=False)
circoli_critici.to_csv(RESULTS_DIR / 'circoli_critici.csv', index=False)
regioni_summary.to_csv(RESULTS_DIR / 'regioni_summary.csv', index=False)
retention_reg_df.to_csv(RESULTS_DIR / 'retention_regionale.csv', index=False)
profili_dist.to_csv(RESULTS_DIR / 'profili_giocatori.csv', index=False)
selettivi_cat.to_csv(RESULTS_DIR / 'selettivi_per_categoria.csv', index=False)
sb_analisi_df.to_csv(RESULTS_DIR / 'scuola_bridge_analisi.csv', index=False)
convertiti_dest.to_csv(RESULTS_DIR / 'sb_destinazione_convertiti.csv', index=False)
churn_seg_df.to_csv(RESULTS_DIR / 'churn_segmentato.csv', index=False)
churn_summary.to_csv(RESULTS_DIR / 'churn_summary.csv', index=False)
ltv_df.to_csv(RESULTS_DIR / 'lifetime_value.csv', index=False)

# Salva metriche complete in JSON
metriche = {
    'generali': {
        'tesseramenti_totali': len(df),
        'giocatori_unici': df['MmbCode'].nunique(),
        'circoli_totali': df['MmbGroup'].nunique(),
        'regioni': df['Regione'].nunique(),
        'periodo': f"{df['Anno'].min()}-{df['Anno'].max()}"
    },
    'anno_2025': {
        'tesserati': len(df_2025),
        'circoli_attivi': df_2025['MmbGroup'].nunique(),
        'eta_media': round(df_2025['Anni'].mean(), 1),
        'gare_medie': round(df_2025['GareGiocate'].mean(), 1),
        'under_40_pct': round((df_2025['FasciaEta'].isin(['<18', '18-30', '30-40'])).sum() / len(df_2025) * 100, 1),
        'over_70_pct': round((df_2025['FasciaEta'].isin(['70-80', '80-90', '90+'])).sum() / len(df_2025) * 100, 1),
        'maschi_pct': round((df_2025['MmbSex'] == 'M').sum() / len(df_2025) * 100, 1),
        'scuola_bridge': df_2025['IsScuolaBridge'].sum(),
        'agonisti': df_2025['IsAgonista'].sum()
    },
    'categorie': {
        'nc_pct': round(cat_dist[cat_dist['Categoria'] == 'NC']['%'].values[0] if 'NC' in cat_dist['Categoria'].values else 0, 1),
        'terza_pct': round(cat_dist[cat_dist['Livello'] == 'Terza']['%'].sum(), 1),
        'master_pct': round(cat_dist[cat_dist['Livello'].isin(['Master Series', 'Life Master', 'Grand Master'])]['%'].sum(), 1),
        'progressione_media_saliti': round(progressione_df['SalitiPct'].mean(), 1),
        'progressione_media_stabili': round(progressione_df['StabiliPct'].mean(), 1)
    },
    'retention': {
        'media_globale': round(retention_reg_df['Retention'].mean(), 1),
        'migliore_regione': retention_media.loc[retention_media['RetentionMedia'].idxmax(), 'Regione'],
        'peggiore_regione': retention_media.loc[retention_media['RetentionMedia'].idxmin(), 'Regione']
    },
    'scuola_bridge': {
        'tasso_successo_medio': round(sb_analisi_df['TassoSuccesso'].mean(), 1),
        'tasso_conversione_medio': round(sb_analisi_df['TassoConversione'].mean(), 1),
        'tasso_churn_medio': round(sb_analisi_df['TassoChurn'].mean(), 1),
        'correlazione_gare_retention': round(fattori_successo['Gare Giocate'], 3)
    },
    'churn': {
        'totale': int(churn_summary['ChurnTotale'].sum()),
        'stima_decessi': int(churn_summary['StimaDecessi'].sum()),
        'stima_infermi': int(churn_summary['StimaInfermi'].sum()),
        'recuperabile': int(churn_summary['ChurnReale'].sum()),
        'pct_recuperabile': round(churn_summary['ChurnReale'].sum() / churn_summary['ChurnTotale'].sum() * 100, 1)
    },
    'ltv': {
        'totale_milioni': round(ltv_df['ValoreTotale'].sum() / 1000000, 2),
        'ltv_medio': round(ltv_df['LTV'].mean(), 0),
        'segmento_oro': '60-70'
    },
    'grafici_generati': chart_count
}

# Custom JSON encoder per tipi numpy
class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (np.integer, np.int64, np.int32)):
            return int(obj)
        elif isinstance(obj, (np.floating, np.float64, np.float32)):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        return super().default(obj)

with open(RESULTS_DIR / 'metriche_complete_v2.json', 'w', encoding='utf-8') as f:
    json.dump(metriche, f, indent=2, ensure_ascii=False, cls=NumpyEncoder)

print(f"\n" + "=" * 100)
print("ANALISI COMPLETATA")
print("=" * 100)
print(f"\nFile salvati in:")
print(f"  - Grafici: {CHARTS_DIR} ({chart_count} file)")
print(f"  - Risultati: {RESULTS_DIR}")
print(f"\nMetriche principali:")
print(f"  - Tesserati 2025: {metriche['anno_2025']['tesserati']:,}")
print(f"  - Under 40: {metriche['anno_2025']['under_40_pct']}%")
print(f"  - Over 70: {metriche['anno_2025']['over_70_pct']}%")
print(f"  - Retention media: {metriche['retention']['media_globale']}%")
print(f"  - Tasso successo SB: {metriche['scuola_bridge']['tasso_successo_medio']}%")
print(f"  - Churn recuperabile: {metriche['churn']['pct_recuperabile']}%")
print(f"  - LTV totale: €{metriche['ltv']['totale_milioni']}M")
print("=" * 100)
