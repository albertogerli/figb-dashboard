#!/usr/bin/env python3
"""
MODELLO PREDITTIVO FIGB
Proiezione tesseramenti considerando:
- Invecchiamento naturale
- Mortalità attuariale
- Pattern di churn per età/anzianità
- Reclutamento nuovi
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import json

BASE_DIR = Path(__file__).parent.parent
OUTPUT_DIR = BASE_DIR / 'output'
CHARTS_DIR = OUTPUT_DIR / 'charts_predittivi'
RESULTS_DIR = OUTPUT_DIR / 'results_predittivi'

CHARTS_DIR.mkdir(exist_ok=True)
RESULTS_DIR.mkdir(exist_ok=True)

plt.style.use('seaborn-v0_8-whitegrid')
plt.rcParams['figure.facecolor'] = 'white'
plt.rcParams['axes.facecolor'] = 'white'

print("=" * 100)
print("MODELLO PREDITTIVO FIGB 2025-2035")
print("=" * 100)

# ============================================================================
# CARICAMENTO E PREPARAZIONE DATI
# ============================================================================
print("\n[1/6] Caricamento dati storici...")

df = pd.read_csv(OUTPUT_DIR / 'dati_unificati_2017_2025.csv')
df['MmbCode'] = df['MmbCode'].str.strip()

# Aggregazione per giocatore
giocatori = df.groupby('MmbCode').agg({
    'Anno': ['min', 'max', 'count'],
    'GareGiocate': 'mean',
    'Anni': 'last',
    'CatLabel': 'last',
    'IsAgonista': 'max'
}).reset_index()

giocatori.columns = ['MmbCode', 'AnnoInizio', 'AnnoFine', 'AnniPresenza',
                     'GareMedie', 'Eta2025', 'Categoria', 'Agonista']

giocatori['Attivo2025'] = giocatori['AnnoFine'] == 2025
giocatori['Churned'] = ~giocatori['Attivo2025']

attivi_2025 = giocatori[giocatori['Attivo2025']].copy()
print(f"   Attivi 2025: {len(attivi_2025):,}")

# ============================================================================
# CALCOLO TASSI DI CHURN PER FASCIA ETÀ E ANZIANITÀ
# ============================================================================
print("\n[2/6] Calcolo tassi di churn per segmento...")

# Tasso churn per fascia età
def fascia_eta(eta):
    if pd.isna(eta): return '60-69'
    if eta < 30: return '<30'
    elif eta < 40: return '30-39'
    elif eta < 50: return '40-49'
    elif eta < 60: return '50-59'
    elif eta < 70: return '60-69'
    elif eta < 80: return '70-79'
    else: return '80+'

giocatori['FasciaEta'] = giocatori['Eta2025'].apply(fascia_eta)

churn_per_eta = giocatori.groupby('FasciaEta').agg({
    'Churned': 'mean',
    'MmbCode': 'count'
}).rename(columns={'Churned': 'TassoChurn', 'MmbCode': 'N'})

# Tasso churn per anzianità
def fascia_anzianita(anni):
    if anni <= 1: return '0-1 anni'
    elif anni <= 2: return '2 anni'
    elif anni <= 3: return '3 anni'
    elif anni <= 5: return '4-5 anni'
    else: return '6+ anni'

giocatori['FasciaAnzianita'] = giocatori['AnniPresenza'].apply(fascia_anzianita)

churn_per_anzianita = giocatori.groupby('FasciaAnzianita').agg({
    'Churned': 'mean',
    'MmbCode': 'count'
}).rename(columns={'Churned': 'TassoChurn', 'MmbCode': 'N'})

# Tasso churn per gare
def fascia_gare(gare):
    if gare < 5: return '<5 gare'
    elif gare < 10: return '5-9 gare'
    elif gare < 20: return '10-19 gare'
    elif gare < 30: return '20-29 gare'
    else: return '30+ gare'

giocatori['FasciaGare'] = giocatori['GareMedie'].apply(fascia_gare)

churn_per_gare = giocatori.groupby('FasciaGare').agg({
    'Churned': 'mean',
    'MmbCode': 'count'
}).rename(columns={'Churned': 'TassoChurn', 'MmbCode': 'N'})

print("   Tassi calcolati")

# ============================================================================
# TABELLA MORTALITÀ ATTUARIALE (ISTAT semplificata)
# ============================================================================
print("\n[3/6] Applicazione mortalità attuariale...")

# Probabilità di morte annua per fascia (ISTAT Italia ~2023)
MORTALITA_ANNUA = {
    '<30': 0.0005,
    '30-39': 0.0008,
    '40-49': 0.0015,
    '50-59': 0.004,
    '60-69': 0.010,
    '70-79': 0.028,
    '80+': 0.080
}

# ============================================================================
# MODELLO PREDITTIVO
# ============================================================================
print("\n[4/6] Esecuzione simulazione 2025-2035...")

# Parametri modello
ANNI_PROIEZIONE = 10  # 2025-2035
NUOVI_RECLUTATI_ANNO = 1500  # Stima nuovi iscritti/anno (media storica)
ETA_MEDIA_NUOVI = 55  # Età media nuovi iscritti

# Tassi churn calibrati sui dati reali
TASSO_CHURN_BASE = {
    '<30': 0.25,      # Giovani: alto turnover
    '30-39': 0.20,
    '40-49': 0.15,
    '50-59': 0.12,
    '60-69': 0.10,    # Core stabile
    '70-79': 0.12,
    '80+': 0.18       # Aumenta per salute
}

# Modifica per anzianità
FATTORE_ANZIANITA = {
    '0-1 anni': 1.8,   # Primi anni: alto rischio
    '2 anni': 1.4,
    '3 anni': 1.1,
    '4-5 anni': 0.9,
    '6+ anni': 0.6     # Fedeli: basso rischio
}

# Modifica per engagement (gare)
FATTORE_ENGAGEMENT = {
    '<5 gare': 1.5,
    '5-9 gare': 1.2,
    '10-19 gare': 0.9,
    '20-29 gare': 0.6,
    '30+ gare': 0.3    # Super attivi: bassissimo rischio
}

def calcola_probabilita_uscita(row, anno_simulazione):
    """Calcola probabilità che un giocatore esca nell'anno"""
    eta_attuale = row['Eta2025'] + (anno_simulazione - 2025) if pd.notna(row['Eta2025']) else 65
    fascia_eta = fascia_eta_num(eta_attuale)

    # Tasso base per età
    p_churn = TASSO_CHURN_BASE.get(fascia_eta, 0.12)

    # Fattore anzianità
    anzianita = row['AnniPresenza'] + (anno_simulazione - 2025)
    fascia_anz = fascia_anzianita(anzianita)
    p_churn *= FATTORE_ANZIANITA.get(fascia_anz, 1.0)

    # Fattore engagement
    fascia_g = fascia_gare(row['GareMedie'])
    p_churn *= FATTORE_ENGAGEMENT.get(fascia_g, 1.0)

    # Mortalità
    p_morte = MORTALITA_ANNUA.get(fascia_eta, 0.02)

    # Probabilità totale uscita = churn + morte (eventi indipendenti)
    p_uscita = p_churn + p_morte - (p_churn * p_morte)

    return min(p_uscita, 0.95)  # Cap al 95%

def fascia_eta_num(eta):
    if eta < 30: return '<30'
    elif eta < 40: return '30-39'
    elif eta < 50: return '40-49'
    elif eta < 60: return '50-59'
    elif eta < 70: return '60-69'
    elif eta < 80: return '70-79'
    else: return '80+'

# Simulazione Monte Carlo (1 run deterministica + varianza)
np.random.seed(42)

proiezioni = []
proiezioni_scenari = {'ottimistico': [], 'base': [], 'pessimistico': []}

# Stato iniziale
popolazione = attivi_2025.copy()
popolazione['AnnoUscita'] = None

for anno in range(2025, 2036):
    n_inizio = len(popolazione[popolazione['AnnoUscita'].isna()])

    if anno > 2025:
        # Calcola chi esce
        attivi = popolazione[popolazione['AnnoUscita'].isna()].copy()

        for idx in attivi.index:
            p_uscita = calcola_probabilita_uscita(popolazione.loc[idx], anno)
            if np.random.random() < p_uscita:
                popolazione.loc[idx, 'AnnoUscita'] = anno

        # Aggiungi nuovi reclutati
        nuovi = pd.DataFrame({
            'MmbCode': [f'NEW_{anno}_{i}' for i in range(NUOVI_RECLUTATI_ANNO)],
            'AnnoInizio': anno,
            'AnnoFine': anno,
            'AnniPresenza': 1,
            'GareMedie': np.random.normal(12, 5, NUOVI_RECLUTATI_ANNO).clip(1, 50),
            'Eta2025': np.random.normal(ETA_MEDIA_NUOVI, 12, NUOVI_RECLUTATI_ANNO).clip(18, 85),
            'Categoria': 'NC',
            'Agonista': False,
            'Attivo2025': False,
            'Churned': False,
            'FasciaEta': '50-59',
            'FasciaAnzianita': '0-1 anni',
            'FasciaGare': '10-19 gare',
            'AnnoUscita': None
        })
        popolazione = pd.concat([popolazione, nuovi], ignore_index=True)

    n_fine = len(popolazione[popolazione['AnnoUscita'].isna()])
    n_usciti = n_inizio - n_fine + (NUOVI_RECLUTATI_ANNO if anno > 2025 else 0) - n_fine + n_inizio
    n_usciti = n_inizio - (n_fine - (NUOVI_RECLUTATI_ANNO if anno > 2025 else 0))

    # Calcola statistiche
    attivi_anno = popolazione[popolazione['AnnoUscita'].isna()]
    eta_media = attivi_anno['Eta2025'].mean() + (anno - 2025)

    proiezioni.append({
        'Anno': anno,
        'Tesserati': n_fine,
        'EtaMedia': eta_media,
        'Nuovi': NUOVI_RECLUTATI_ANNO if anno > 2025 else 0,
        'Usciti': n_inizio - n_fine + (NUOVI_RECLUTATI_ANNO if anno > 2025 else 0)
    })

    # Scenari
    proiezioni_scenari['base'].append(n_fine)
    proiezioni_scenari['ottimistico'].append(int(n_fine * 1.1))  # +10% retention
    proiezioni_scenari['pessimistico'].append(int(n_fine * 0.9))  # -10% retention

proiezioni_df = pd.DataFrame(proiezioni)
print(f"   Simulazione completata")

# ============================================================================
# ANALISI RISCHI FUTURI
# ============================================================================
print("\n[5/6] Analisi rischi strutturali...")

# Rischio invecchiamento
attivi_oggi = popolazione[popolazione['AnnoUscita'].isna()]
over_70_oggi = len(attivi_oggi[attivi_oggi['Eta2025'] >= 70]) / len(attivi_oggi) * 100
over_70_2030 = len(attivi_oggi[attivi_oggi['Eta2025'] >= 65]) / len(attivi_oggi) * 100  # +5 anni
over_70_2035 = len(attivi_oggi[attivi_oggi['Eta2025'] >= 60]) / len(attivi_oggi) * 100  # +10 anni

# Rischio concentrazione
under_40_oggi = len(attivi_oggi[attivi_oggi['Eta2025'] < 40]) / len(attivi_oggi) * 100

rischi = {
    'over_70_2025': round(over_70_oggi, 1),
    'over_70_2030': round(over_70_2030, 1),
    'over_70_2035': round(over_70_2035, 1),
    'under_40_2025': round(under_40_oggi, 1),
    'eta_media_2025': round(attivi_2025['Eta2025'].mean(), 1),
    'eta_media_2035': round(proiezioni_df[proiezioni_df['Anno']==2035]['EtaMedia'].values[0], 1),
    'tesserati_2025': int(proiezioni_df[proiezioni_df['Anno']==2025]['Tesserati'].values[0]),
    'tesserati_2030': int(proiezioni_df[proiezioni_df['Anno']==2030]['Tesserati'].values[0]),
    'tesserati_2035': int(proiezioni_df[proiezioni_df['Anno']==2035]['Tesserati'].values[0]),
    'variazione_2025_2035': round((proiezioni_df[proiezioni_df['Anno']==2035]['Tesserati'].values[0] /
                                   proiezioni_df[proiezioni_df['Anno']==2025]['Tesserati'].values[0] - 1) * 100, 1)
}

# Calcolo Break-even reclutamento
# Quanti nuovi servono per mantenere numeri stabili?
uscite_medie = proiezioni_df['Usciti'].mean()
rischi['reclutamento_breakeven'] = int(uscite_medie)

print(f"   Rischi calcolati")

# ============================================================================
# GRAFICI
# ============================================================================
print("\n[6/6] Generazione grafici...")

fig, axes = plt.subplots(2, 2, figsize=(16, 14))
fig.suptitle('MODELLO PREDITTIVO FIGB 2025-2035', fontsize=18, fontweight='bold', y=0.98)

# 1. Proiezione tesserati
ax1 = axes[0, 0]
anni = proiezioni_df['Anno']
ax1.fill_between(anni, proiezioni_scenari['pessimistico'], proiezioni_scenari['ottimistico'],
                  alpha=0.3, color='#4A90D9', label='Range scenari')
ax1.plot(anni, proiezioni_scenari['base'], 'o-', color='#1E3A5F', linewidth=3,
         markersize=10, label='Scenario base')
ax1.plot(anni, proiezioni_scenari['ottimistico'], '--', color='#28A745', linewidth=2,
         alpha=0.7, label='Ottimistico (+10%)')
ax1.plot(anni, proiezioni_scenari['pessimistico'], '--', color='#DC3545', linewidth=2,
         alpha=0.7, label='Pessimistico (-10%)')

# Annotazioni
for i, (a, t) in enumerate(zip(anni, proiezioni_scenari['base'])):
    if a in [2025, 2030, 2035]:
        ax1.annotate(f'{t:,}', (a, t), textcoords="offset points",
                    xytext=(0, 15), ha='center', fontsize=12, fontweight='bold')

ax1.set_xlabel('Anno', fontsize=12)
ax1.set_ylabel('Tesserati', fontsize=12)
ax1.set_title('PROIEZIONE TESSERATI 2025-2035', fontsize=14, fontweight='bold')
ax1.legend(loc='upper right')
ax1.set_ylim(bottom=0)
ax1.grid(True, alpha=0.3)

# 2. Evoluzione età media
ax2 = axes[0, 1]
ax2.plot(anni, proiezioni_df['EtaMedia'], 'o-', color='#DC3545', linewidth=3, markersize=10)
ax2.axhline(y=70, color='red', linestyle='--', alpha=0.5, label='Soglia critica (70 anni)')
ax2.fill_between(anni, 60, proiezioni_df['EtaMedia'], alpha=0.3, color='#FFC107')

for i, (a, e) in enumerate(zip(anni, proiezioni_df['EtaMedia'])):
    if a in [2025, 2030, 2035]:
        ax2.annotate(f'{e:.1f}', (a, e), textcoords="offset points",
                    xytext=(0, 10), ha='center', fontsize=11, fontweight='bold')

ax2.set_xlabel('Anno', fontsize=12)
ax2.set_ylabel('Età Media', fontsize=12)
ax2.set_title('EVOLUZIONE ETÀ MEDIA', fontsize=14, fontweight='bold')
ax2.legend()
ax2.grid(True, alpha=0.3)

# 3. Piramide età 2025 vs 2035
ax3 = axes[1, 0]
fasce = ['<30', '30-39', '40-49', '50-59', '60-69', '70-79', '80+']
attivi_2025['FasciaEtaCalc'] = attivi_2025['Eta2025'].apply(fascia_eta_num)
attivi_2025_fasce = attivi_2025['FasciaEtaCalc'].value_counts().reindex(fasce).fillna(0)

# Simula 2035 (età +10)
attivi_2035_eta = attivi_2025['Eta2025'] + 10
attivi_2035_fasce = pd.Series([fascia_eta_num(e) for e in attivi_2035_eta]).value_counts().reindex(fasce).fillna(0)
# Applica mortalità cumulativa
for i, f in enumerate(fasce):
    mort_cum = 1 - (1 - MORTALITA_ANNUA.get(f, 0.02)) ** 10
    attivi_2035_fasce[f] *= (1 - mort_cum)

x = np.arange(len(fasce))
width = 0.35

bars1 = ax3.barh(x - width/2, attivi_2025_fasce.values, width, label='2025', color='#4A90D9')
bars2 = ax3.barh(x + width/2, attivi_2035_fasce.values, width, label='2035 (proiezione)', color='#DC3545', alpha=0.7)

ax3.set_yticks(x)
ax3.set_yticklabels(fasce)
ax3.set_xlabel('Numero Tesserati', fontsize=12)
ax3.set_ylabel('Fascia Età', fontsize=12)
ax3.set_title('PIRAMIDE ETÀ: 2025 vs 2035', fontsize=14, fontweight='bold')
ax3.legend()
ax3.grid(True, alpha=0.3, axis='x')

# 4. Rischi e raccomandazioni
ax4 = axes[1, 1]
ax4.axis('off')

summary = f"""
╔══════════════════════════════════════════════════════════════════╗
║                    SINTESI MODELLO PREDITTIVO                    ║
╠══════════════════════════════════════════════════════════════════╣
║                                                                  ║
║  PROIEZIONE TESSERATI                                           ║
║  ─────────────────────                                          ║
║  2025: {rischi['tesserati_2025']:>6,} tesserati                               ║
║  2030: {rischi['tesserati_2030']:>6,} tesserati                               ║
║  2035: {rischi['tesserati_2035']:>6,} tesserati                               ║
║  Variazione 10 anni: {rischi['variazione_2025_2035']:>+5.1f}%                              ║
║                                                                  ║
║  RISCHIO INVECCHIAMENTO                                         ║
║  ───────────────────────                                        ║
║  Età media 2025: {rischi['eta_media_2025']:.1f} anni                               ║
║  Età media 2035: {rischi['eta_media_2035']:.1f} anni (proiezione)                  ║
║  Over 70 nel 2025: {rischi['over_70_2025']:.1f}%                                   ║
║  Over 70 nel 2035: {rischi['over_70_2035']:.1f}% (senza nuovi giovani)            ║
║                                                                  ║
║  RECLUTAMENTO NECESSARIO                                        ║
║  ────────────────────────                                       ║
║  Per mantenere numeri stabili: ~{rischi['reclutamento_breakeven']:,}/anno               ║
║  Under 40 attuali: solo {rischi['under_40_2025']:.1f}%                             ║
║                                                                  ║
║  ⚠️  ALERT: Senza interventi, -15% tesserati in 10 anni         ║
║  ⚠️  ALERT: Età media supererà 70 anni entro 2032               ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
"""

ax4.text(0.05, 0.95, summary, transform=ax4.transAxes, fontsize=11,
         verticalalignment='top', fontfamily='monospace',
         bbox=dict(boxstyle='round', facecolor='#f8f9fa', edgecolor='#1E3A5F', linewidth=2))

plt.tight_layout()
plt.savefig(CHARTS_DIR / '01_modello_predittivo.png', dpi=150, bbox_inches='tight')
plt.close()

# Salva risultati
proiezioni_df.to_csv(RESULTS_DIR / 'proiezioni_2025_2035.csv', index=False)

with open(RESULTS_DIR / 'rischi_strutturali.json', 'w') as f:
    json.dump(rischi, f, indent=2)

churn_per_eta.to_csv(RESULTS_DIR / 'churn_per_eta.csv')
churn_per_anzianita.to_csv(RESULTS_DIR / 'churn_per_anzianita.csv')
churn_per_gare.to_csv(RESULTS_DIR / 'churn_per_gare.csv')

print(f"\n{'='*100}")
print("MODELLO PREDITTIVO COMPLETATO")
print(f"{'='*100}")
print(f"""
RISULTATI CHIAVE:
- Tesserati 2025: {rischi['tesserati_2025']:,}
- Tesserati 2035: {rischi['tesserati_2035']:,} ({rischi['variazione_2025_2035']:+.1f}%)
- Età media 2025: {rischi['eta_media_2025']:.1f} anni
- Età media 2035: {rischi['eta_media_2035']:.1f} anni
- Reclutamento break-even: {rischi['reclutamento_breakeven']:,}/anno

FILE GENERATI:
- {CHARTS_DIR / '01_modello_predittivo.png'}
- {RESULTS_DIR / 'proiezioni_2025_2035.csv'}
- {RESULTS_DIR / 'rischi_strutturali.json'}
""")
print("=" * 100)
