#!/usr/bin/env python3
"""
DASHBOARD FIGB - Analisi Tesseramento 2017-2025
App Streamlit interattiva
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
from pathlib import Path

# Import mapping province (per analisi territoriale)
try:
    from province_mapping import (
        PROVINCE_POPOLAZIONE, REGIONE_POPOLAZIONE, CITTA_METROPOLITANE,
        PROVINCIA_TO_REGIONE
    )
    PROVINCE_MAPPING_AVAILABLE = True
except ImportError:
    PROVINCE_MAPPING_AVAILABLE = False
    PROVINCE_POPOLAZIONE = {}
    REGIONE_POPOLAZIONE = {}
    CITTA_METROPOLITANE = []
    PROVINCIA_TO_REGIONE = {}

# Configurazione pagina
st.set_page_config(
    page_title="FIGB Dashboard",
    page_icon="🃏",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Paths
BASE_DIR = Path(__file__).parent
OUTPUT_DIR = BASE_DIR / 'output'
RESULTS_DIR = OUTPUT_DIR / 'results_v2'
RESULTS_CHURN = OUTPUT_DIR / 'results_churn'
RESULTS_INNOV = OUTPUT_DIR / 'results_innovativi'
RESULTS_PRED = OUTPUT_DIR / 'results_predittivi'

# ============================================================================
# CARICAMENTO DATI
# ============================================================================
@st.cache_data
def load_data():
    """Carica tutti i dati necessari"""
    data = {}

    # Dati principali
    data['df'] = pd.read_csv(OUTPUT_DIR / 'dati_unificati_2017_2025.csv')
    data['df']['MmbCode'] = data['df']['MmbCode'].str.strip()
    data['df']['MmbName'] = data['df']['MmbName'].str.strip()

    # Metriche
    with open(RESULTS_DIR / 'metriche_complete_v2.json', 'r') as f:
        data['metriche'] = json.load(f)

    # Regioni
    data['regioni'] = pd.read_csv(RESULTS_DIR / 'regioni_summary.csv')

    # Associazioni
    data['associazioni_v'] = pd.read_csv(RESULTS_DIR / 'circoli_virtuosi.csv')
    data['associazioni_c'] = pd.read_csv(RESULTS_DIR / 'circoli_critici.csv')

    # Churn
    data['cluster_churn'] = pd.read_csv(RESULTS_CHURN / 'cluster_churn_profili.csv')
    data['soglie'] = pd.read_csv(RESULTS_CHURN / 'soglie_critiche_churn.csv')
    data['churn_macro'] = pd.read_csv(RESULTS_CHURN / 'churn_per_macroregione.csv')

    # Rischio reale
    if (RESULTS_INNOV / 'giocatori_rischio_REALE.csv').exists():
        data['rischio'] = pd.read_csv(RESULTS_INNOV / 'giocatori_rischio_REALE.csv')

    # Predittivo
    if RESULTS_PRED.exists():
        data['proiezioni'] = pd.read_csv(RESULTS_PRED / 'proiezioni_2025_2035.csv')
        with open(RESULTS_PRED / 'rischi_strutturali.json', 'r') as f:
            data['rischi_pred'] = json.load(f)

    return data

# Carica dati
data = load_data()
df = data['df']
metriche = data['metriche']

# Carica deceduti (se disponibile)
deceduti_file = BASE_DIR / 'Deceduti.xlsx'
deceduti_df = None
if deceduti_file.exists():
    deceduti_df = pd.read_excel(deceduti_file)
    deceduti_df['MmbCode'] = deceduti_df['MmbCode'].str.strip()

# ============================================================================
# SIDEBAR - FILTRI
# ============================================================================
st.sidebar.title("🃏 FIGB Dashboard")
st.sidebar.markdown("---")

# Navigazione
pagina = st.sidebar.selectbox(
    "📊 Sezione",
    ["📊 Executive Summary", "🏠 Overview", "📈 Trend Temporale", "🗺️ Analisi Regionale",
     "📍 Analisi Territoriale", "🏆 Mappa Agonismo", "🏢 Analisi Associazioni",
     "🎓 Bridge a Scuola", "🎯 Focus Puglia", "⚠️ Giocatori a Rischio", "🔄 Bridgisti Recuperabili",
     "🔮 Modello Predittivo", "🌱 Opportunità Crescita", "🔬 Analisi Avanzate",
     "🎯 Attività per Età/Sesso", "🧩 Cluster e Territori", "🎖️ Priorità Intervento", "🔍 Esplora Dati"]
)

st.sidebar.markdown("---")
st.sidebar.markdown("### Filtri Globali")

# Filtro anni (slider range)
anni_min = int(df['Anno'].min())
anni_max = int(df['Anno'].max())
anni_range = st.sidebar.slider(
    "Periodo",
    anni_min, anni_max,
    (anni_min, anni_max)
)
anni_selezionati = list(range(anni_range[0], anni_range[1] + 1))

# Mapping regioni -> macroregioni
MACRO_REGIONI = {
    'Nord-Ovest': ['PIE', 'VDA', 'LOM', 'LIG'],
    'Nord-Est': ['TRT', 'TRB', 'FRI', 'VEN', 'EMI'],
    'Centro': ['TOS', 'UMB', 'MAR', 'LAZ'],
    'Sud': ['ABR', 'MOL', 'CAM', 'PUG', 'BAS', 'CAB'],
    'Isole': ['SIC', 'SAR']
}

# Inverti mapping
REGIONE_TO_MACRO = {}
for macro, regs in MACRO_REGIONI.items():
    for r in regs:
        REGIONE_TO_MACRO[r] = macro

# Nomi completi regioni
NOMI_REGIONI_COMPLETI = {
    'PIE': 'Piemonte', 'VDA': "Valle d'Aosta", 'LOM': 'Lombardia', 'LIG': 'Liguria',
    'TRT': 'Trentino', 'TRB': 'Alto Adige', 'FRI': 'Friuli V.G.', 'VEN': 'Veneto', 'EMI': 'Emilia-Romagna',
    'TOS': 'Toscana', 'UMB': 'Umbria', 'MAR': 'Marche', 'LAZ': 'Lazio',
    'ABR': 'Abruzzo', 'MOL': 'Molise', 'CAM': 'Campania', 'PUG': 'Puglia', 'BAS': 'Basilicata', 'CAB': 'Calabria',
    'SIC': 'Sicilia', 'SAR': 'Sardegna'
}

# Filtro Area + Regione semplificato
st.sidebar.markdown("**📍 Area Geografica**")

# Step 1: Seleziona macroaree
macro_options = ['🇮🇹 Tutta Italia'] + list(MACRO_REGIONI.keys())
macro_sel = st.sidebar.selectbox("Macroarea", macro_options, index=0)

# Step 2: Se non è tutta Italia, mostra regioni di quella macro
if macro_sel == '🇮🇹 Tutta Italia':
    regioni_selezionate = list(REGIONE_TO_MACRO.keys())
else:
    # Mostra multiselect per le regioni della macroarea
    regioni_macro = MACRO_REGIONI[macro_sel]
    opzioni_regioni = [f"{NOMI_REGIONI_COMPLETI[r]}" for r in regioni_macro]

    regioni_scelte = st.sidebar.multiselect(
        "Regioni",
        opzioni_regioni,
        default=opzioni_regioni,
        help="Seleziona una o più regioni"
    )

    # Converti nomi in codici
    nome_to_codice = {v: k for k, v in NOMI_REGIONI_COMPLETI.items()}
    regioni_selezionate = [nome_to_codice[n] for n in regioni_scelte if n in nome_to_codice]

    if not regioni_selezionate:
        regioni_selezionate = regioni_macro

# Filtro età
eta_min, eta_max = st.sidebar.slider(
    "Fascia Età",
    int(df['Anni'].min()),
    int(df['Anni'].max()),
    (18, 100)
)

# Filtro Macrocategoria
MACRO_CATEGORIE = {
    'Master/GM': ['GM', 'LM', 'MS'],
    'Honor': ['HK', 'HA', 'HQ', 'HJ'],
    '1a Categoria': ['1P', '1F', '1C', '1Q'],
    '2a Categoria': ['2P', '2F', '2C', '2Q'],
    '3a Categoria': ['3P', '3F', '3C', '3Q'],
    '4a Categoria': ['4P', '4F', '4C', '4Q'],
    'NC': ['NC', 'Ordinario Sportivo']
}
macro_cat_options = ["Tutte"] + list(MACRO_CATEGORIE.keys())
macro_cat_sel = st.sidebar.selectbox("Macrocategoria", macro_cat_options, index=0)

# Filtro Tipo Tessera (include BAS)
TIPI_TESSERA = {
    'Agonista': ['Agonista'],
    'Scuola Bridge': ['Scuola Bridge'],
    'BAS (Bridge a Scuola)': ['Ist.Scolastici', 'Studente CAS', 'CAS Giovanile'],
    'Ordinario Sportivo': ['Ordinario Sportivo'],
    'Ordinario Amatoriale': ['Ordinario Amatoriale'],
    'Non Agonista': ['Non Agonista'],
    'Altro': ['Aderente', 'Normale', 'Promozionale', 'Estero']
}
tipo_tessera_options = ["Tutti"] + list(TIPI_TESSERA.keys())
tipo_tessera_sel = st.sidebar.selectbox("Tipo Tessera", tipo_tessera_options, index=0)

# Applica filtri
df_filtered = df[
    (df['Anno'].isin(anni_selezionati)) &
    (df['GrpArea'].isin(regioni_selezionate)) &
    (df['Anni'] >= eta_min) &
    (df['Anni'] <= eta_max)
]

# Applica filtro macrocategoria
if macro_cat_sel != "Tutte":
    cat_valide = MACRO_CATEGORIE[macro_cat_sel]
    df_filtered = df_filtered[df_filtered['CatLabel'].isin(cat_valide)]

# Applica filtro tipo tessera
if tipo_tessera_sel != "Tutti":
    tipi_validi = TIPI_TESSERA[tipo_tessera_sel]
    df_filtered = df_filtered[df_filtered['MbtDesc'].isin(tipi_validi)]

st.sidebar.markdown("---")
st.sidebar.markdown("### 📊 Dati Filtrati")
st.sidebar.metric("Record", f"{len(df_filtered):,}")
st.sidebar.metric("Giocatori", f"{df_filtered['MmbCode'].nunique():,}")
# Usa colonna Associazione se esiste, altrimenti GrpName
col_assoc = 'Associazione' if 'Associazione' in df_filtered.columns else 'GrpName'
st.sidebar.metric("Associazioni", f"{df_filtered[col_assoc].nunique():,}")

# Riepilogo filtri attivi
with st.sidebar.expander("🔍 Filtri attivi"):
    st.write(f"**Periodo:** {anni_range[0]} - {anni_range[1]}")
    st.write(f"**Area:** {macro_sel}")
    if macro_sel != '🇮🇹 Tutta Italia':
        st.write(f"**Regioni:** {len(regioni_selezionate)}")
    st.write(f"**Età:** {eta_min} - {eta_max}")
    st.write(f"**Categoria:** {macro_cat_sel}")
    st.write(f"**Tipo Tessera:** {tipo_tessera_sel}")

# ============================================================================
# PAGINA: EXECUTIVE SUMMARY (Per Consiglio Federale)
# ============================================================================
if pagina == "📊 Executive Summary":
    st.title("📊 Executive Summary - Analisi Strategica FIGB")
    st.markdown("##### Report per il Consiglio Federale | Dati 2017-2025")

    # -------------------------------------------------------------------------
    # SEZIONE 1: STATO ATTUALE - KPI CRITICI
    # -------------------------------------------------------------------------
    st.markdown("---")
    st.header("1️⃣ Stato Attuale della Federazione")

    # Calcoli KPI
    df_2025 = df[df['Anno'] == 2025]
    df_2019 = df[df['Anno'] == 2019]
    df_2017 = df[df['Anno'] == 2017]

    tess_2025 = df_2025['MmbCode'].nunique()
    tess_2019 = df_2019['MmbCode'].nunique()
    tess_2017 = df_2017['MmbCode'].nunique()

    var_vs_2019 = (tess_2025 - tess_2019) / tess_2019 * 100
    var_vs_2017 = (tess_2025 - tess_2017) / tess_2017 * 100

    eta_media_2025 = df_2025['Anni'].mean()
    eta_media_2017 = df_2017['Anni'].mean()

    # Under 40
    under40_2025 = len(df_2025[df_2025['Anni'] < 40])
    pct_under40 = under40_2025 / tess_2025 * 100

    # Gare medie
    gare_medie_2025 = df_2025['GareGiocate'].mean()

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Tesserati 2025",
            f"{tess_2025:,}",
            f"{var_vs_2019:+.1f}% vs 2019",
            delta_color="inverse"
        )
    with col2:
        st.metric(
            "Età Media",
            f"{eta_media_2025:.1f} anni",
            f"+{eta_media_2025 - eta_media_2017:.1f} vs 2017",
            delta_color="inverse"
        )
    with col3:
        st.metric(
            "Under 40",
            f"{under40_2025:,}",
            f"{pct_under40:.1f}% del totale",
            delta_color="off"
        )
    with col4:
        st.metric(
            "Gare Medie/Anno",
            f"{gare_medie_2025:.1f}",
            help="Media gare giocate per tesserato"
        )

    # Alert box principale
    st.error(f"""
    ### ⚠️ ALERT STRATEGICO

    **Il bridge italiano sta affrontando una crisi demografica strutturale:**

    - 📉 **-{abs(var_vs_2019):.1f}%** tesserati rispetto al pre-COVID (2019)
    - 👴 Età media **{eta_media_2025:.0f} anni** (+{eta_media_2025 - eta_media_2017:.0f} anni in 8 anni)
    - 👶 Solo **{pct_under40:.1f}%** under 40 - rischio estinzione generazionale
    - ⏰ Senza interventi: **proiezione sotto 10.000 tesserati entro 2030**
    """)

    # -------------------------------------------------------------------------
    # SEZIONE 2: DIAGNOSI - I 5 PROBLEMI CHIAVE
    # -------------------------------------------------------------------------
    st.markdown("---")
    st.header("2️⃣ Diagnosi: I 5 Problemi Chiave")

    prob_col1, prob_col2 = st.columns(2)

    with prob_col1:
        st.markdown("""
        ### 🔴 Problema 1: Invecchiamento Accelerato
        - Età media: **71→75 anni** in 8 anni
        - Fascia 70-79 = **39%** dei tesserati
        - Fascia 80+ = **20%** dei tesserati
        - **Perdita naturale stimata: 400-500/anno**

        ### 🔴 Problema 2: Crollo Reclutamento Giovani
        - Under 30: solo **275 persone** (2%)
        - Fascia 30-39: **170 persone** (1.3%)
        - Tasso conversione scuole: **<5%**
        - **Gap vs benchmark europei: -70%**

        ### 🔴 Problema 3: Abbandono Primi Anni
        - **50%** abbandona entro 3 anni
        - Soglia critica: **37 gare/anno**
        - Chi fa <10 gare: retention **22%**
        - Chi fa >50 gare: retention **81%**
        """)

    with prob_col2:
        st.markdown("""
        ### 🟡 Problema 4: Circoli in Difficoltà
        - **30 circoli** a rischio chiusura
        - **232 circoli** senza corsi attivi
        - Concentrazione: 50% tesserati in 15% circoli
        - Province scoperte: **12** senza circoli

        ### 🟡 Problema 5: Effetto COVID Persistente
        - **5.322** persi post-2020 mai tornati
        - Calo maggiore nelle **grandi città** (-32%)
        - Bridge online non ha compensato
        - Abitudini sociali cambiate
        """)

    # -------------------------------------------------------------------------
    # SEZIONE 3: OPPORTUNITÀ IDENTIFICATE
    # -------------------------------------------------------------------------
    st.markdown("---")
    st.header("3️⃣ Opportunità di Recupero Identificate")

    # Carica dati opportunità se disponibili
    RESULTS_OPP = OUTPUT_DIR / 'results_opportunita'
    RESULTS_PRIORITA = OUTPUT_DIR / 'results_priorita'

    opp_data = []

    # Quasi Agganciati
    if (RESULTS_OPP / 'quasi_agganciati.csv').exists():
        qa = pd.read_csv(RESULTS_OPP / 'quasi_agganciati.csv')
        # Filtra deceduti se disponibile
        if deceduti_df is not None:
            qa = qa[~qa['MmbCode'].str.strip().isin(set(deceduti_df['MmbCode'].str.strip()))]
        opp_data.append({
            'Opportunità': '🎯 Quasi Agganciati',
            'Target': f"{len(qa):,} persone",
            'Descrizione': 'Ex-tesserati 1-2 anni, poche gare, poi spariti',
            'Potenziale': f"+{int(len(qa)*0.1):,} (10% recupero)",
            'Difficoltà': '🟢 Bassa',
            'Priorità': 1
        })

    # Persi COVID
    if (RESULTS_OPP / 'persi_covid.csv').exists():
        pc = pd.read_csv(RESULTS_OPP / 'persi_covid.csv')
        if deceduti_df is not None:
            pc = pc[~pc['MmbCode'].str.strip().isin(set(deceduti_df['MmbCode'].str.strip()))]
        alta_prio = len(pc[pc['Recuperabile'] == 'Alta Priorità']) if 'Recuperabile' in pc.columns else int(len(pc)*0.2)
        opp_data.append({
            'Opportunità': '😷 Persi COVID Recuperabili',
            'Target': f"{alta_prio:,} alta priorità",
            'Descrizione': 'Under 75, molte gare storiche, potrebbero tornare',
            'Potenziale': f"+{int(alta_prio*0.15):,} (15% recupero)",
            'Difficoltà': '🟡 Media',
            'Priorità': 2
        })

    # Circoli senza corsi
    opp_data.append({
        'Opportunità': '📚 Circoli senza Corsi',
        'Target': '232 circoli',
        'Descrizione': 'Retention con corsi: 75% vs senza: 49%',
        'Potenziale': '+545 (se attivano corsi)',
        'Difficoltà': '🟡 Media',
        'Priorità': 3
    })

    # Occasionali da attivare
    opp_data.append({
        'Opportunità': '🎮 Occasionali da Attivare',
        'Target': '11.788 persone',
        'Descrizione': 'Fanno solo 3.6 gare/anno, soglia retention: 37',
        'Potenziale': '+799 (se superano soglia)',
        'Difficoltà': '🟡 Media',
        'Priorità': 4
    })

    # Gap demografico
    opp_data.append({
        'Opportunità': '👔 Gap Demografico 60-70',
        'Target': '3.610 potenziali',
        'Descrizione': 'Penetrazione 60-70: 34/100k vs 70-80: 78/100k',
        'Potenziale': '+180 (campagne mirate)',
        'Difficoltà': '🔴 Alta',
        'Priorità': 5
    })

    if opp_data:
        opp_df = pd.DataFrame(opp_data).sort_values('Priorità')
        st.dataframe(opp_df[['Opportunità', 'Target', 'Descrizione', 'Potenziale', 'Difficoltà']],
                     use_container_width=True, hide_index=True)

        # Totale potenziale
        st.success(f"""
        ### 💰 Impatto Potenziale Totale: **+2.500-3.000 tesserati**

        Questa stima considera tassi di conversione realistici (10-20%) sulle opportunità identificate.
        Con interventi mirati e coordinati, è possibile **invertire il trend negativo entro 2-3 anni**.
        """)

    # -------------------------------------------------------------------------
    # SEZIONE 4: PIANO D'AZIONE RACCOMANDATO
    # -------------------------------------------------------------------------
    st.markdown("---")
    st.header("4️⃣ Piano d'Azione Raccomandato")

    tab1, tab2, tab3 = st.tabs(["🚀 Fase 1: Immediata", "📈 Fase 2: Medio Termine", "🎯 Fase 3: Strutturale"])

    with tab1:
        st.markdown("""
        ### 🚀 FASE 1: Azioni Immediate (0-6 mesi)

        | # | Azione | Target | KPI Atteso | Owner Suggerito |
        |---|--------|--------|------------|-----------------|
        | 1 | **Campagna "Torna al Bridge"** | 1.735 Quasi Agganciati | +170 recuperi | Comunicazione |
        | 2 | **Contatto diretto Persi COVID** | Alta priorità under 75 | +150 recuperi | Circoli locali |
        | 3 | **Programma "Prima Gara"** | 11.788 Occasionali | +500 attivazioni | Settore Tecnico |
        | 4 | **Audit circoli critici** | 30 a rischio | 0 chiusure | Consiglio |

        **Budget stimato Fase 1:** €15.000-25.000
        **ROI atteso:** +820 tesserati = €32.800 in quote (a €40/tessera)
        """)

    with tab2:
        st.markdown("""
        ### 📈 FASE 2: Medio Termine (6-18 mesi)

        | # | Azione | Target | KPI Atteso | Owner Suggerito |
        |---|--------|--------|------------|-----------------|
        | 1 | **Espansione corsi a 232 circoli** | Circoli senza corsi | +545 nuovi | Scuola Bridge |
        | 2 | **Programma "Bridge After Work"** | Fascia 40-55 anni | +200 nuovi | Marketing |
        | 3 | **Partnership aziendali** | Welfare aziendale | +100 nuovi | Presidenza |
        | 4 | **Tornei regionali giovani** | Under 30 | +50 nuovi | Settore Giovanile |
        | 5 | **Piano rilancio Milano/Roma/Torino** | 3 città in calo | -50% calo | Comitati Regionali |

        **Budget stimato Fase 2:** €40.000-60.000
        **ROI atteso:** +895 tesserati = €35.800 in quote
        """)

    with tab3:
        st.markdown("""
        ### 🎯 FASE 3: Strutturale (18-36 mesi)

        | # | Azione | Target | KPI Atteso | Owner Suggerito |
        |---|--------|--------|------------|-----------------|
        | 1 | **Riforma percorso principianti** | Tutti i nuovi | Retention +20pp | Settore Tecnico |
        | 2 | **Piattaforma nazionale online** | Tutti i tesserati | Engagement +30% | IT/Digital |
        | 3 | **Apertura nuovi circoli** | Province scoperte | +5 circoli | Espansione |
        | 4 | **Academy insegnanti** | Formazione | +50 maestri | Scuola Bridge |
        | 5 | **Brand refresh Bridge** | Immagine | Awareness +50% | Comunicazione |

        **Budget stimato Fase 3:** €80.000-120.000
        **ROI atteso:** Inversione trend, stabilizzazione a 15.000+ tesserati
        """)

    # -------------------------------------------------------------------------
    # SEZIONE 5: PROIEZIONI E SCENARI
    # -------------------------------------------------------------------------
    st.markdown("---")
    st.header("5️⃣ Proiezioni e Scenari")

    col1, col2 = st.columns(2)

    with col1:
        # Scenario senza interventi
        anni_proj = list(range(2025, 2036))
        scenario_base = [tess_2025]
        for i in range(1, 11):
            scenario_base.append(int(scenario_base[-1] * 0.95))  # -5% annuo

        scenario_ottimista = [tess_2025]
        for i in range(1, 11):
            if i <= 2:
                scenario_ottimista.append(int(scenario_ottimista[-1] * 0.98))  # -2% primi 2 anni
            else:
                scenario_ottimista.append(int(scenario_ottimista[-1] * 1.02))  # +2% poi

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=anni_proj, y=scenario_base, mode='lines+markers',
                                name='Scenario Base (no interventi)', line=dict(color='red', dash='dash')))
        fig.add_trace(go.Scatter(x=anni_proj, y=scenario_ottimista, mode='lines+markers',
                                name='Scenario con Piano', line=dict(color='green')))
        fig.add_hline(y=10000, line_dash="dot", line_color="orange",
                     annotation_text="Soglia critica")
        fig.update_layout(title="Proiezione Tesserati 2025-2035", height=400,
                         xaxis_title="Anno", yaxis_title="Tesserati")
        fig.update_xaxes(dtick=1)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("""
        ### 📊 Confronto Scenari

        | Indicatore | Base (no azioni) | Con Piano |
        |------------|------------------|-----------|
        | **Tesserati 2030** | ~8.700 | ~14.500 |
        | **Tesserati 2035** | ~5.500 | ~16.000 |
        | **Età media 2030** | 78 anni | 73 anni |
        | **Circoli attivi** | -30% | +10% |

        ### ⚖️ Costo dell'Inazione

        - Perdita quote: **€200.000/anno**
        - Perdita sponsor: **€50.000/anno**
        - Chiusura circoli: **€30.000/anno** (supporto)
        - **Totale 5 anni: €1.4M di mancati ricavi**

        💡 *Il Piano costa €150k in 3 anni ma genera €500k+ in nuove quote*
        """)

    # -------------------------------------------------------------------------
    # SEZIONE 6: SINTESI DECISIONALE
    # -------------------------------------------------------------------------
    st.markdown("---")
    st.header("6️⃣ Sintesi per il Consiglio Federale")

    st.info("""
    ### 📋 DECISIONI RICHIESTE

    1. **Approvazione Budget Fase 1**: €25.000 per azioni immediate
    2. **Mandato Comitato Esecutivo**: Coordinamento piano triennale
    3. **Nomina Responsabile Progetto**: Figura dedicata al rilancio
    4. **Obiettivo 2026**: Invertire il trend, tornare a +0% crescita
    """)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.success("""
        ### ✅ PUNTI DI FORZA
        - Base dati eccellente
        - Opportunità identificate
        - Circoli fedeli
        - Tradizione consolidata
        """)

    with col2:
        st.warning("""
        ### ⚠️ RISCHI
        - Tempo limitato
        - Risorse scarse
        - Resistenza cambio
        - Competizione leisure
        """)

    with col3:
        st.error("""
        ### 🎯 PRIORITÀ ASSOLUTA
        1. Fermare emorragia
        2. Attivare occasionali
        3. Recuperare persi
        4. Ringiovanire base
        """)

    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; padding: 20px; background-color: #f0f2f6; border-radius: 10px;'>
        <h4>📊 Report preparato per il Consiglio Federale FIGB</h4>
        <p>Dati aggiornati al 2025 | Analisi basata su 137.000+ record storici</p>
        <p><em>Per approfondimenti, consultare le sezioni specifiche del dashboard</em></p>
    </div>
    """, unsafe_allow_html=True)

# ============================================================================
# PAGINA: OVERVIEW
# ============================================================================
elif pagina == "🏠 Overview":
    st.title("🃏 FIGB - Dashboard Tesseramento 2017-2025")

    # Mostra filtri attivi se non sono tutti i dati
    if macro_sel != '🇮🇹 Tutta Italia' or anni_range != (anni_min, anni_max) or eta_min > 18 or eta_max < 100 or macro_cat_sel != "Tutte" or tipo_tessera_sel != "Tutti":
        filtri_attivi = []
        if anni_range != (anni_min, anni_max):
            filtri_attivi.append(f"Periodo: {anni_range[0]}-{anni_range[1]}")
        if macro_sel != '🇮🇹 Tutta Italia':
            filtri_attivi.append(f"Area: {macro_sel}")
        if eta_min > 18 or eta_max < 100:
            filtri_attivi.append(f"Età: {eta_min}-{eta_max}")
        if macro_cat_sel != "Tutte":
            filtri_attivi.append(f"Categoria: {macro_cat_sel}")
        if tipo_tessera_sel != "Tutti":
            filtri_attivi.append(f"Tessera: {tipo_tessera_sel}")
        st.info(f"🔍 **Filtri attivi:** {' | '.join(filtri_attivi)}")

    # Metriche principali (dinamiche in base ai filtri)
    col1, col2, col3, col4 = st.columns(4)

    # Calcola metriche sui dati filtrati
    # Tesserati dell'ultimo anno nel range selezionato
    ultimo_anno = df_filtered['Anno'].max()
    tesserati_ultimo_anno = df_filtered[df_filtered['Anno'] == ultimo_anno]['MmbCode'].nunique()
    tesserati_totali_periodo = df_filtered['MmbCode'].nunique()
    eta_media_filtrata = df_filtered['Anni'].mean()
    under_40_pct = (df_filtered['Anni'] < 40).sum() / len(df_filtered) * 100 if len(df_filtered) > 0 else 0
    gare_medie = df_filtered['GareGiocate'].mean()

    with col1:
        st.metric(
            f"Tesserati {ultimo_anno}",
            f"{tesserati_ultimo_anno:,}",
            delta=f"{tesserati_totali_periodo:,} nel periodo"
        )

    with col2:
        st.metric(
            "Età Media",
            f"{eta_media_filtrata:.1f}",
            delta=None
        )

    with col3:
        st.metric(
            "Under 40",
            f"{under_40_pct:.1f}%",
            delta="target: 20%",
            delta_color="inverse"
        )

    with col4:
        st.metric(
            "Gare Medie",
            f"{gare_medie:.1f}",
            delta=None
        )

    st.markdown("---")

    # Grafici principali
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📈 Trend Tesserati")
        trend = df.groupby('Anno')['MmbCode'].nunique().reset_index()
        trend.columns = ['Anno', 'Tesserati']
        fig = px.line(trend, x='Anno', y='Tesserati', markers=True)
        fig.update_layout(height=350)
        fig.update_xaxes(dtick=1)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("👥 Piramide Età 2025")
        # Usa solo dati 2025 (rispettando altri filtri globali)
        df_2025 = df_filtered[df_filtered['Anno'] == 2025].copy()
        if len(df_2025) > 0:
            df_2025['FasciaEta'] = pd.cut(df_2025['Anni'],
                                           bins=[0, 30, 40, 50, 60, 70, 80, 100],
                                           labels=['<30', '30-39', '40-49', '50-59', '60-69', '70-79', '80+'])

            # Categorizza per tipo: Scuola Bridge, Bridge a Scuola, Altri
            def categorizza_tipo(mbt):
                if mbt == 'Scuola Bridge':
                    return 'Scuola Bridge'
                elif mbt in ['Ist.Scolastici', 'Studente CAS', 'CAS Giovanile']:
                    return 'Bridge a Scuola'
                else:
                    return 'Altri'

            df_2025['TipoTessera'] = df_2025['MbtDesc'].apply(categorizza_tipo)

            # Aggrega per fascia età e tipo
            eta_tipo = df_2025.groupby(['FasciaEta', 'TipoTessera']).size().reset_index(name='Count')

            fig = px.bar(eta_tipo, x='FasciaEta', y='Count', color='TipoTessera',
                         barmode='stack',
                         color_discrete_map={
                             'Scuola Bridge': '#3498db',
                             'Bridge a Scuola': '#e74c3c',
                             'Altri': '#95a5a6'
                         },
                         category_orders={'TipoTessera': ['Bridge a Scuola', 'Scuola Bridge', 'Altri']})
            fig.update_layout(height=350, legend=dict(orientation='h', yanchor='bottom', y=1.02))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("Nessun dato per 2025 con i filtri selezionati")

    # Alert box
    st.error("""
    **⚠️ ALERT CRITICO:**
    - 201 giovani (<30 anni) a rischio urgente - intervento immediato necessario
    - Solo 4.2% under 40 - rischio estinzione demografica
    - 50% abbandona entro 3 anni dall'iscrizione
    """)

    # Tabella riassuntiva
    st.subheader("📊 Riepilogo per Anno")
    summary = df.groupby('Anno').agg({
        'MmbCode': 'nunique',
        'GareGiocate': 'mean',
        'Anni': 'mean'
    }).round(1)
    summary.columns = ['Tesserati', 'Gare Medie', 'Età Media']
    st.dataframe(summary, use_container_width=True)

    # Churn naturale per anno (discreto)
    if deceduti_df is not None and len(deceduti_df) > 0:
        st.markdown("---")
        with st.expander("📋 Nota: Churn naturale per anno", expanded=False):
            churn_naturale = deceduti_df.groupby('UltimoAnnoTess').size().reset_index(name='N')
            churn_naturale = churn_naturale[churn_naturale['UltimoAnnoTess'] >= 2017].sort_values('UltimoAnnoTess')
            churn_naturale.columns = ['Anno', 'Persone']

            col1, col2 = st.columns([2, 3])
            with col1:
                st.dataframe(churn_naturale, use_container_width=True, hide_index=True)
            with col2:
                st.caption("Numero di tesserati il cui ultimo anno di tessera coincide con l'anno indicato, per cause naturali.")

# ============================================================================
# PAGINA: TREND TEMPORALE
# ============================================================================
elif pagina == "📈 Trend Temporale":
    st.title("📈 Trend Temporale 2017-2025")

    # Trend tesserati
    st.subheader("Evoluzione Tesserati")
    trend = df_filtered.groupby('Anno')['MmbCode'].nunique().reset_index()
    trend.columns = ['Anno', 'Tesserati']

    fig = px.area(trend, x='Anno', y='Tesserati',
                  title="Numero Tesserati per Anno")
    fig.add_vline(x=2020, line_dash="dash", line_color="red",
                  annotation_text="COVID-19")
    fig.update_xaxes(dtick=1)
    st.plotly_chart(fig, use_container_width=True)

    # Trend per categoria
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Distribuzione Categorie")
        # Raggruppa categorie in macro-classi
        df_cat = df_filtered.copy()

        def macro_categoria(cat):
            if pd.isna(cat):
                return 'NC'
            cat = str(cat)
            if cat.startswith('1'):
                return '1a Categoria'
            elif cat.startswith('2'):
                return '2a Categoria'
            elif cat.startswith('3'):
                return '3a Categoria'
            elif cat.startswith('4'):
                return '4a Categoria'
            elif cat in ['NC', 'Ordinario Sportivo']:
                return 'Non Classificati'
            elif cat.startswith('H') or cat in ['GM', 'LM', 'MS']:
                return 'Onorarie/Speciali'
            else:
                return 'Altro'

        df_cat['MacroCategoria'] = df_cat['CatLabel'].apply(macro_categoria)
        cat_trend = df_cat.groupby(['Anno', 'MacroCategoria']).size().reset_index(name='Count')

        # Ordine logico
        cat_order = ['Non Classificati', '1a Categoria', '2a Categoria', '3a Categoria', '4a Categoria', 'Onorarie/Speciali', 'Altro']
        cat_trend['MacroCategoria'] = pd.Categorical(cat_trend['MacroCategoria'], categories=cat_order, ordered=True)

        fig = px.bar(cat_trend, x='Anno', y='Count', color='MacroCategoria',
                     title="Tesserati per Categoria",
                     color_discrete_map={
                         'Non Classificati': '#95a5a6',
                         '1a Categoria': '#27ae60',
                         '2a Categoria': '#3498db',
                         '3a Categoria': '#9b59b6',
                         '4a Categoria': '#e74c3c',
                         'Onorarie/Speciali': '#f39c12',
                         'Altro': '#7f8c8d'
                     })
        fig.update_xaxes(dtick=1)
        fig.update_layout(legend=dict(orientation='h', yanchor='bottom', y=1.02))
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Età Media nel Tempo")
        eta_trend = df_filtered.groupby('Anno')['Anni'].mean().reset_index()
        fig = px.line(eta_trend, x='Anno', y='Anni', markers=True,
                      title="Evoluzione Età Media")
        fig.add_hline(y=70, line_dash="dash", line_color="red",
                      annotation_text="Soglia critica")
        fig.update_xaxes(dtick=1)
        st.plotly_chart(fig, use_container_width=True)

    # Gare medie
    st.subheader("Partecipazione Gare")
    gare_trend = df_filtered.groupby('Anno')['GareGiocate'].mean().reset_index()
    fig = px.bar(gare_trend, x='Anno', y='GareGiocate',
                 title="Gare Medie per Anno", color='GareGiocate',
                 color_continuous_scale='Viridis')
    fig.update_xaxes(dtick=1)
    st.plotly_chart(fig, use_container_width=True)

    # Piramide categorie per anno
    st.markdown("---")
    st.subheader("🏆 Piramide Categorie per Anno")
    st.markdown("""
    Distribuzione dei giocatori per categoria tecnica, dalla più bassa (NC) alla più alta (GM).
    Una vera "piramide" dovrebbe avere molti giocatori alla base e pochi in cima.
    """)

    # Ordine categorie dal basso verso l'alto
    ordine_categorie = [
        'NC',  # Non Classificato
        '4Q', '4C', '4F', '4P',  # 4a categoria (solo 2017-2018)
        '3Q', '3C', '3F', '3P',  # 3a categoria
        '2Q', '2C', '2F', '2P',  # 2a categoria
        '1Q', '1C', '1F', '1P',  # 1a categoria
        'HJ',  # Honorary Jack (più bassa)
        'HQ',  # Honorary Queen
        'HK',  # Honorary King
        'HA',  # Honorary Ace (più alta)
        'MS',  # Master
        'LM',  # Life Master
        'GM'   # Grand Master
    ]

    # Filtri: anno e classe d'età
    col_filtro1, col_filtro2 = st.columns(2)

    with col_filtro1:
        anni_disponibili = sorted(df_filtered['Anno'].unique())
        anno_sel = st.select_slider("Seleziona anno:", options=anni_disponibili, value=anni_disponibili[-1])

    with col_filtro2:
        fasce_eta = ['Tutte', '<30', '30-39', '40-49', '50-59', '60-69', '70-79', '80+']
        fascia_sel = st.selectbox("Filtra per classe d'età:", fasce_eta)

    # Filtra per anno selezionato
    df_anno = df_filtered[df_filtered['Anno'] == anno_sel].copy()

    # Applica filtro età se selezionato
    if fascia_sel != 'Tutte':
        df_anno['FasciaEta'] = pd.cut(df_anno['Anni'],
                                       bins=[0, 30, 40, 50, 60, 70, 80, 150],
                                       labels=['<30', '30-39', '40-49', '50-59', '60-69', '70-79', '80+'])
        df_anno = df_anno[df_anno['FasciaEta'] == fascia_sel]

    # Conta per categoria
    cat_counts = df_anno['CatLabel'].value_counts()

    # Prepara dati per il grafico (solo categorie con giocatori)
    piramide_data = []
    for cat in ordine_categorie:
        count = cat_counts.get(cat, 0)
        if count > 0:
            piramide_data.append({'Categoria': cat, 'Giocatori': count})

    if piramide_data:
        piramide_df = pd.DataFrame(piramide_data)

        # Colori per livello
        def get_color(cat):
            if cat == 'NC':
                return '#bdc3c7'
            elif cat.startswith('4'):
                return '#e74c3c'
            elif cat.startswith('3'):
                return '#9b59b6'
            elif cat.startswith('2'):
                return '#3498db'
            elif cat.startswith('1'):
                return '#27ae60'
            elif cat.startswith('H'):
                return '#f39c12'
            else:  # MS, LM, GM
                return '#f1c40f'

        piramide_df['Colore'] = piramide_df['Categoria'].apply(get_color)

        # Mantieni ordine corretto
        cat_presenti = [c for c in ordine_categorie if c in piramide_df['Categoria'].values]

        # Grafico piramide centrata (barre sovrapposte simmetriche)
        fig = go.Figure()

        # Barre a sinistra (valori negativi per centrare)
        fig.add_trace(go.Bar(
            y=piramide_df['Categoria'],
            x=-piramide_df['Giocatori'] / 2,
            orientation='h',
            marker_color=piramide_df['Colore'],
            hovertemplate='%{y}: %{customdata:,}<extra></extra>',
            customdata=piramide_df['Giocatori'],
            showlegend=False
        ))

        # Barre a destra (valori positivi)
        fig.add_trace(go.Bar(
            y=piramide_df['Categoria'],
            x=piramide_df['Giocatori'] / 2,
            orientation='h',
            marker_color=piramide_df['Colore'],
            text=piramide_df['Giocatori'].apply(lambda x: f'{x:,}'),
            textposition='outside',
            hovertemplate='%{y}: %{customdata:,}<extra></extra>',
            customdata=piramide_df['Giocatori'],
            showlegend=False
        ))

        fig.update_layout(
            title=f"Piramide Categorie - {anno_sel}",
            height=650,
            barmode='overlay',
            bargap=0.1,
            xaxis=dict(
                showticklabels=False,
                zeroline=True,
                zerolinewidth=2,
                zerolinecolor='#333'
            ),
            yaxis=dict(
                categoryorder='array',
                categoryarray=cat_presenti
            ),
            showlegend=False,
            margin=dict(l=60, r=100)
        )

        st.plotly_chart(fig, use_container_width=True)

        # Statistiche
        col1, col2, col3, col4 = st.columns(4)
        totale = piramide_df['Giocatori'].sum()
        nc_count = cat_counts.get('NC', 0)
        top_count = sum(cat_counts.get(c, 0) for c in ['GM', 'LM', 'MS'])
        cat1_count = sum(cat_counts.get(c, 0) for c in ['1Q', '1C', '1F', '1P'])

        with col1:
            st.metric("Totale", f"{totale:,}")
        with col2:
            st.metric("NC (base)", f"{nc_count:,}", f"{nc_count/totale*100:.1f}%")
        with col3:
            st.metric("1a Categoria", f"{cat1_count:,}", f"{cat1_count/totale*100:.1f}%")
        with col4:
            st.metric("Master+ (top)", f"{top_count:,}", f"{top_count/totale*100:.1f}%")

        # Nota sulla forma
        nc_pct = nc_count / totale * 100
        top_pct = (cat1_count + top_count + sum(cat_counts.get(c, 0) for c in ['HJ', 'HQ', 'HK', 'HA'])) / totale * 100

        if nc_pct > 40:
            st.success(f"✅ **Piramide SANA** - Base ampia ({nc_pct:.0f}% NC), struttura equilibrata")
        elif nc_pct > 25:
            st.warning(f"⚠️ **Piramide COMPRESSA** - Base moderata ({nc_pct:.0f}% NC), possibile stagnazione")
        else:
            st.error(f"🔴 **Piramide INVERTITA** - Base ristretta ({nc_pct:.0f}% NC), popolazione esperta senza ricambio")

    # =========================================================================
    # ANALISI DIAGNOSTICA COMPLETA PER FASCIA D'ETÀ (solo 2025)
    # =========================================================================
    if anno_sel == anni_disponibili[-1]:  # Solo per ultimo anno disponibile
        st.markdown("---")
        st.subheader("🔬 Diagnosi Strutturale per Fascia d'Età")

        # Calcola statistiche per tutte le fasce
        df_diag = df_filtered[df_filtered['Anno'] == anno_sel].copy()
        df_diag['FasciaEta'] = pd.cut(df_diag['Anni'],
                                       bins=[0, 30, 40, 50, 60, 70, 80, 150],
                                       labels=['<30', '30-39', '40-49', '50-59', '60-69', '70-79', '80+'])

        def calc_macro(cat):
            if pd.isna(cat) or cat in ['NC', 'Ordinario Sportivo']:
                return 'NC'
            cat = str(cat)
            if cat.startswith('1'):
                return '1a'
            elif cat.startswith('H') or cat in ['MS', 'LM', 'GM']:
                return 'Top'
            else:
                return 'Medio'

        df_diag['Livello'] = df_diag['CatLabel'].apply(calc_macro)

        # Analisi per fascia
        analisi_fasce = []
        for fascia in ['<30', '30-39', '40-49', '50-59', '60-69', '70-79', '80+']:
            df_f = df_diag[df_diag['FasciaEta'] == fascia]
            tot = len(df_f)
            if tot == 0:
                continue

            nc = (df_f['Livello'] == 'NC').sum()
            top = (df_f['Livello'].isin(['1a', 'Top'])).sum()

            nc_pct = nc / tot * 100
            top_pct = top / tot * 100

            # Diagnosi
            if nc_pct > 40:
                stato = "🟢 Sana"
                problema = "Nessuno"
            elif nc_pct > 30:
                stato = "🟡 Compressa"
                problema = "Ricambio lento"
            else:
                stato = "🔴 Invertita"
                problema = "No ricambio"

            analisi_fasce.append({
                'Fascia': fascia,
                'Giocatori': tot,
                'NC%': nc_pct,
                'Top%': top_pct,
                'Stato': stato,
                'Problema': problema
            })

        analisi_df = pd.DataFrame(analisi_fasce)

        # Visualizzazione tabella
        st.dataframe(
            analisi_df.style.format({
                'Giocatori': '{:,.0f}',
                'NC%': '{:.1f}%',
                'Top%': '{:.1f}%'
            }).background_gradient(subset=['NC%'], cmap='RdYlGn').background_gradient(subset=['Top%'], cmap='RdYlGn_r'),
            use_container_width=True,
            hide_index=True
        )

        # Grafico confronto fasce
        col1, col2 = st.columns(2)

        with col1:
            fig = px.bar(analisi_df, x='Fascia', y='Giocatori',
                        title="Distribuzione Giocatori per Età",
                        color='Stato',
                        color_discrete_map={'🟢 Sana': '#27ae60', '🟡 Compressa': '#f39c12', '🔴 Invertita': '#e74c3c'})
            fig.update_layout(showlegend=False, height=350)
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            fig = px.bar(analisi_df, x='Fascia', y=['NC%', 'Top%'],
                        title="Base vs Top per Fascia",
                        barmode='group',
                        color_discrete_map={'NC%': '#3498db', 'Top%': '#e74c3c'})
            fig.update_layout(height=350, legend_title="")
            st.plotly_chart(fig, use_container_width=True)

        # Box diagnostico
        st.markdown("### 📋 Diagnosi e Raccomandazioni")

        # Identifica problemi
        under40 = analisi_df[analisi_df['Fascia'].isin(['<30', '30-39', '40-49'])]['Giocatori'].sum()
        totale_2025 = analisi_df['Giocatori'].sum()
        pct_under40 = under40 / totale_2025 * 100

        fascia_30_39 = analisi_df[analisi_df['Fascia'] == '30-39'].iloc[0] if len(analisi_df[analisi_df['Fascia'] == '30-39']) > 0 else None
        fascia_70_79 = analisi_df[analisi_df['Fascia'] == '70-79'].iloc[0] if len(analisi_df[analisi_df['Fascia'] == '70-79']) > 0 else None

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("#### 🚨 Problemi Identificati")
            st.markdown(f"""
            1. **Crisi 30-39 anni**: Solo {fascia_30_39['Giocatori']:,.0f} giocatori ({fascia_30_39['Giocatori']/totale_2025*100:.1f}%)
               - Top% più alto ({fascia_30_39['Top%']:.1f}%): chi resta è esperto
               - Bridge non attrae adulti in età lavorativa

            2. **Gap generazionale**: Under 40 = {under40:,.0f} ({pct_under40:.1f}% del totale)
               - Popolazione concentrata in 60-80 anni
               - Rischio estinzione demografica in 15-20 anni

            3. **Piramidi compresse 60-79**: NC% tra 34-40%
               - Meno principianti che entrano in età pensionabile
               - Saturazione delle categorie intermedie
            """)

        with col2:
            st.markdown("#### 💡 Redistribuzione Ideale")

            # Calcola distribuzione ideale
            ideale = {
                '<30': {'target': 5, 'NC_ideale': 70},
                '30-39': {'target': 5, 'NC_ideale': 50},
                '40-49': {'target': 8, 'NC_ideale': 45},
                '50-59': {'target': 15, 'NC_ideale': 45},
                '60-69': {'target': 27, 'NC_ideale': 40},
                '70-79': {'target': 30, 'NC_ideale': 35},
                '80+': {'target': 10, 'NC_ideale': 30}
            }

            st.markdown(f"""
            | Fascia | Attuale | Ideale | Gap |
            |--------|---------|--------|-----|
            | <40 anni | {pct_under40:.1f}% | 18% | **{18-pct_under40:+.1f}%** |
            | 60-69 | {fascia_70_79['Giocatori']/totale_2025*100 if fascia_70_79 is not None else 0:.1f}% | 27% | - |
            | 70-79 | {analisi_df[analisi_df['Fascia']=='70-79']['Giocatori'].sum()/totale_2025*100:.1f}% | 30% | - |

            **Azioni prioritarie:**
            1. 🎯 Programmi per 30-49 anni (flessibilità oraria, online)
            2. 📚 Corsi "seconda carriera" per 50-59 anni
            3. 🔄 Aumentare conversione NC → categorie (gare dedicate)
            """)

# ============================================================================
# PAGINA: ANALISI REGIONALE
# ============================================================================
elif pagina == "🗺️ Analisi Regionale":
    st.title("🗺️ Analisi Regionale")

    # Info filtro attivo
    if macro_sel != '🇮🇹 Tutta Italia':
        st.info(f"📍 Visualizzazione filtrata: **{macro_sel}** ({len(regioni_selezionate)} regioni)")

    # Calcola dati per regione
    regioni_df = df_filtered.groupby('GrpArea').agg({
        'MmbCode': 'nunique',
        'GareGiocate': 'mean',
        'Anni': 'mean'
    }).reset_index()
    regioni_df.columns = ['Codice', 'Tesserati', 'Gare Medie', 'Età Media']
    regioni_df['Regione'] = regioni_df['Codice'].map(NOMI_REGIONI_COMPLETI).fillna(regioni_df['Codice'])
    regioni_df['Macroregione'] = regioni_df['Codice'].map(REGIONE_TO_MACRO).fillna('Altro')

    # Statistiche per macroregione
    st.subheader("📊 Riepilogo per Macroregione")

    macro_stats = regioni_df.groupby('Macroregione').agg({
        'Tesserati': 'sum',
        'Gare Medie': 'mean',
        'Età Media': 'mean'
    }).round(1)

    col1, col2, col3, col4, col5 = st.columns(5)
    cols = [col1, col2, col3, col4, col5]
    macro_order = ['Nord-Ovest', 'Nord-Est', 'Centro', 'Sud', 'Isole']

    for i, macro in enumerate(macro_order):
        if macro in macro_stats.index:
            with cols[i]:
                st.metric(macro, f"{int(macro_stats.loc[macro, 'Tesserati']):,}")
                st.caption(f"Gare: {macro_stats.loc[macro, 'Gare Medie']:.1f}")

    st.markdown("---")

    # Grafici
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🏆 Tesserati per Regione")
        fig = px.bar(regioni_df.sort_values('Tesserati', ascending=True),
                     x='Tesserati', y='Regione', orientation='h',
                     color='Macroregione',
                     color_discrete_map={
                         'Nord-Ovest': '#1E3A5F', 'Nord-Est': '#4A90D9',
                         'Centro': '#28A745', 'Sud': '#FFC107', 'Isole': '#DC3545'
                     })
        fig.update_layout(height=600, showlegend=True)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("🎯 Gare Medie per Regione")
        fig = px.bar(regioni_df.sort_values('Gare Medie', ascending=True),
                     x='Gare Medie', y='Regione', orientation='h',
                     color='Macroregione',
                     color_discrete_map={
                         'Nord-Ovest': '#1E3A5F', 'Nord-Est': '#4A90D9',
                         'Centro': '#28A745', 'Sud': '#FFC107', 'Isole': '#DC3545'
                     })
        fig.update_layout(height=600, showlegend=True)
        st.plotly_chart(fig, use_container_width=True)

    # Churn per macroregione
    st.markdown("---")
    st.subheader("⚠️ Churn per Macroregione")

    churn_macro = data['churn_macro']
    churn_macro = churn_macro[~churn_macro['Macroregione'].isin(['Altro', 'Nazionale', ''])]

    col1, col2 = st.columns([2, 1])

    with col1:
        fig = px.bar(churn_macro.sort_values('ChurnRate'),
                     x='Macroregione', y='ChurnRate',
                     color='ChurnRate', color_continuous_scale='RdYlGn_r',
                     text='ChurnRate')
        fig.update_traces(texttemplate='%{text:.1f}%', textposition='auto', cliponaxis=False)
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("**Legenda Churn:**")
        st.markdown("🟢 < 52% = Buono")
        st.markdown("🟡 52-55% = Attenzione")
        st.markdown("🔴 > 55% = Critico")
        st.markdown("---")
        best = churn_macro.loc[churn_macro['ChurnRate'].idxmin()]
        worst = churn_macro.loc[churn_macro['ChurnRate'].idxmax()]
        st.success(f"**Migliore:** {best['Macroregione']} ({best['ChurnRate']:.1f}%)")
        st.error(f"**Peggiore:** {worst['Macroregione']} ({worst['ChurnRate']:.1f}%)")

    # Tabella dettagliata
    st.markdown("---")
    st.subheader("📋 Dettaglio Completo")
    st.dataframe(
        regioni_df[['Regione', 'Macroregione', 'Tesserati', 'Gare Medie', 'Età Media']]
        .sort_values('Tesserati', ascending=False)
        .style.background_gradient(subset=['Tesserati'], cmap='Blues')
        .background_gradient(subset=['Gare Medie'], cmap='Greens')
        .format({'Gare Medie': '{:.1f}', 'Età Media': '{:.1f}'}),
        use_container_width=True
    )

# ============================================================================
# PAGINA: ANALISI TERRITORIALE (Province e Città Metropolitane)
# ============================================================================
elif pagina == "📍 Analisi Territoriale":
    st.title("📍 Analisi Territoriale Dettagliata")
    st.markdown("Analisi per **province** e **città metropolitane** con tassi di penetrazione sulla popolazione")

    # Verifica disponibilità mapping province
    if not PROVINCE_MAPPING_AVAILABLE:
        st.error("⚠️ Modulo province_mapping non trovato. Verifica che il file province_mapping.py sia presente.")
    # Verifica se colonna Provincia esiste
    elif 'Provincia' not in df_filtered.columns:
        st.error("⚠️ Colonna 'Provincia' non trovata. Esegui prima `python 03_arricchisci_province.py`")
    else:
        # Filtra dati con provincia
        df_prov = df_filtered[df_filtered['Provincia'].notna()].copy()
        ultimo_anno = df_prov['Anno'].max()
        df_ultimo = df_prov[df_prov['Anno'] == ultimo_anno]

        # === METRICHE PRINCIPALI ===
        col1, col2, col3, col4 = st.columns(4)

        n_province = df_ultimo['Provincia'].nunique()
        tesserati_cm = df_ultimo[df_ultimo['IsCittaMetropolitana'] == True]['MmbCode'].nunique()
        tesserati_altre = df_ultimo[df_ultimo['IsCittaMetropolitana'] == False]['MmbCode'].nunique()

        # Calcola penetrazione media
        prov_stats = df_ultimo.groupby('Provincia')['MmbCode'].nunique().reset_index()
        prov_stats.columns = ['Provincia', 'Tesserati']
        prov_stats['Popolazione'] = prov_stats['Provincia'].map(PROVINCE_POPOLAZIONE)
        prov_stats['TesseratiPer100k'] = prov_stats.apply(
            lambda r: (r['Tesserati'] / r['Popolazione'] * 100000) if r['Popolazione'] > 0 else 0, axis=1
        )
        penetrazione_media = prov_stats['TesseratiPer100k'].mean()

        with col1:
            st.metric("Province Attive", f"{n_province}")
        with col2:
            st.metric("In Città Metropolitane", f"{tesserati_cm:,}", delta=f"{tesserati_cm/(tesserati_cm+tesserati_altre)*100:.0f}%")
        with col3:
            st.metric("Altre Province", f"{tesserati_altre:,}")
        with col4:
            st.metric("Penetrazione Media", f"{penetrazione_media:.1f}/100k")

        st.markdown("---")

        # === TAB LAYOUT ===
        tab1, tab2, tab3, tab4, tab5 = st.tabs(["💚 Vitalità Bridge", "🏙️ Province", "🌆 Città Metropolitane", "📈 Trend", "🗺️ Mappa Penetrazione"])

        # ========== TAB 0: VITALITÀ BRIDGE ==========
        with tab1:
            st.subheader("💚 Indice di Vitalità del Bridge")
            st.markdown("""
            **A colpo d'occhio**: dove il bridge è più vivo? L'indice combina:
            - 🎯 **Penetrazione** (tesserati per 100k abitanti)
            - 🎮 **Attività** (gare medie giocate)
            - 👶 **Giovinezza** (% under 60 anni)
            - 🏆 **Agonismo** (% giocatori agonisti)
            """)

            # Calcola indice vitalità per provincia
            vit_prov = df_ultimo.groupby('Provincia').agg({
                'MmbCode': 'nunique',
                'GareGiocate': 'mean',
                'Anni': 'mean',
                'IsAgonista': 'mean'
            }).reset_index()
            vit_prov.columns = ['Provincia', 'Tesserati', 'GareMedie', 'EtaMedia', 'PctAgonisti']

            # Aggiungi popolazione e calcola metriche
            vit_prov['Popolazione'] = vit_prov['Provincia'].map(PROVINCE_POPOLAZIONE)
            vit_prov['Penetrazione'] = vit_prov.apply(
                lambda r: (r['Tesserati'] / r['Popolazione'] * 100000) if r['Popolazione'] and r['Popolazione'] > 0 else 0, axis=1
            )
            vit_prov['IsCittaMetro'] = vit_prov['Provincia'].apply(lambda x: x in CITTA_METROPOLITANE)
            vit_prov['Regione'] = vit_prov['Provincia'].map(PROVINCIA_TO_REGIONE)

            # Calcola % under 60
            under60_prov = df_ultimo[df_ultimo['Anni'] < 60].groupby('Provincia')['MmbCode'].nunique().reset_index()
            under60_prov.columns = ['Provincia', 'Under60']
            vit_prov = vit_prov.merge(under60_prov, on='Provincia', how='left')
            vit_prov['Under60'] = vit_prov['Under60'].fillna(0)
            vit_prov['PctUnder60'] = (vit_prov['Under60'] / vit_prov['Tesserati'] * 100).fillna(0)

            # Filtra province con almeno 15 tesserati
            vit_prov = vit_prov[vit_prov['Tesserati'] >= 15].copy()

            # CALCOLO INDICE VITALITÀ (0-100)
            # Normalizza ogni componente 0-100 e poi media pesata
            vit_prov['Score_Penetrazione'] = (vit_prov['Penetrazione'] / vit_prov['Penetrazione'].max() * 100).clip(0, 100)
            vit_prov['Score_Attivita'] = (vit_prov['GareMedie'] / 50 * 100).clip(0, 100)  # 50 gare = 100
            vit_prov['Score_Giovinezza'] = (vit_prov['PctUnder60'] / 30 * 100).clip(0, 100)  # 30% under60 = 100
            vit_prov['Score_Agonismo'] = (vit_prov['PctAgonisti'] * 100 / 0.5 * 100).clip(0, 100)  # 50% agonisti = 100

            # Indice finale pesato
            vit_prov['IndiceVitalita'] = (
                vit_prov['Score_Penetrazione'] * 0.35 +
                vit_prov['Score_Attivita'] * 0.30 +
                vit_prov['Score_Giovinezza'] * 0.20 +
                vit_prov['Score_Agonismo'] * 0.15
            ).round(1)

            # Classifica vitalità
            def classifica_vitalita(score):
                if score >= 70: return '🟢 Eccellente'
                elif score >= 50: return '🟡 Buono'
                elif score >= 30: return '🟠 Medio'
                else: return '🔴 Critico'

            vit_prov['Stato'] = vit_prov['IndiceVitalita'].apply(classifica_vitalita)

            # Ordina per indice
            vit_prov = vit_prov.sort_values('IndiceVitalita', ascending=False)

            # === VISUALIZZAZIONE PRINCIPALE ===
            col1, col2 = st.columns([2, 1])

            with col1:
                st.markdown("##### 🗺️ Mappa Vitalità Bridge")

                # Coordinate province principali (approssimate al centroide regionale)
                COORD_PROV = {
                    'Roma': (41.89, 12.48), 'Milano': (45.46, 9.19), 'Torino': (45.07, 7.69),
                    'Napoli': (40.85, 14.27), 'Bologna': (44.49, 11.34), 'Firenze': (43.77, 11.25),
                    'Genova': (44.41, 8.93), 'Venezia': (45.44, 12.32), 'Palermo': (38.12, 13.36),
                    'Bari': (41.13, 16.87), 'Catania': (37.50, 15.09), 'Cagliari': (39.22, 9.12),
                    'Trieste': (45.65, 13.78), 'Padova': (45.41, 11.88), 'Verona': (45.44, 10.99),
                    'Brescia': (45.54, 10.21), 'Bergamo': (45.70, 9.67), 'Modena': (44.65, 10.92),
                    'Parma': (44.80, 10.33), 'Reggio Emilia': (44.70, 10.63), 'Livorno': (43.55, 10.31),
                    'Pisa': (43.72, 10.40), 'Lucca': (43.84, 10.50), 'Ancona': (43.62, 13.52),
                    'Perugia': (43.11, 12.39), 'Pescara': (42.46, 14.21), 'Salerno': (40.68, 14.77),
                    'Lecce': (40.35, 18.17), 'Messina': (38.19, 15.55), 'Sassari': (40.73, 8.56),
                    'Trento': (46.07, 11.12), 'Bolzano': (46.50, 11.35), 'Udine': (46.06, 13.24),
                    'Ravenna': (44.42, 12.20), 'Rimini': (44.06, 12.57), 'Ferrara': (44.84, 11.62),
                    'Piacenza': (45.05, 9.69), 'La Spezia': (44.10, 9.82), 'Savona': (44.31, 8.48),
                    'Imperia': (43.89, 8.03), 'Arezzo': (43.46, 11.88), 'Siena': (43.32, 11.33),
                    'Grosseto': (42.76, 11.11), 'Terni': (42.56, 12.64), 'Macerata': (43.30, 13.45),
                    'Ascoli Piceno': (42.85, 13.57), 'Foggia': (41.46, 15.54), 'Taranto': (40.48, 17.23),
                    'Cosenza': (39.30, 16.25), 'Reggio Calabria': (38.11, 15.65), 'Catanzaro': (38.91, 16.59),
                    'Potenza': (40.64, 15.80), 'Matera': (40.67, 16.60), 'Siracusa': (37.07, 15.29),
                    'Ragusa': (36.93, 14.73), 'Trapani': (38.02, 12.51), 'Agrigento': (37.31, 13.58),
                    'Nuoro': (40.32, 9.33), 'Oristano': (39.90, 8.59)
                }

                # Aggiungi coordinate
                vit_prov['lat'] = vit_prov['Provincia'].map(lambda x: COORD_PROV.get(x, (None, None))[0])
                vit_prov['lon'] = vit_prov['Provincia'].map(lambda x: COORD_PROV.get(x, (None, None))[1])

                # Filtra solo province con coordinate
                vit_map = vit_prov.dropna(subset=['lat', 'lon'])

                fig = px.scatter_geo(
                    vit_map,
                    lat='lat', lon='lon',
                    size='Tesserati',
                    color='IndiceVitalita',
                    hover_name='Provincia',
                    hover_data={
                        'IndiceVitalita': ':.1f',
                        'Tesserati': True,
                        'Penetrazione': ':.1f',
                        'GareMedie': ':.1f',
                        'PctUnder60': ':.1f',
                        'Stato': True,
                        'lat': False, 'lon': False
                    },
                    color_continuous_scale='RdYlGn',
                    size_max=40,
                    title="Indice Vitalità Bridge per Provincia"
                )
                fig.update_coloraxes(colorbar_title="Vitalità")
                fig.update_geos(
                    scope='europe',
                    center=dict(lat=42.5, lon=12.5),
                    projection_scale=6,
                    showland=True, landcolor='rgb(243, 243, 243)',
                    showcoastlines=True
                )
                fig.update_layout(height=500, margin=dict(l=0, r=0, t=40, b=0))
                st.plotly_chart(fig, use_container_width=True)

            with col2:
                st.markdown("##### 📊 Classifica Vitalità")

                # Conteggio per stato
                stato_counts = vit_prov['Stato'].value_counts()
                for stato in ['🟢 Eccellente', '🟡 Buono', '🟠 Medio', '🔴 Critico']:
                    count = stato_counts.get(stato, 0)
                    st.markdown(f"{stato}: **{count}** province")

                st.markdown("---")
                st.markdown("**🏆 Top 5 Vitalità**")
                for _, row in vit_prov.head(5).iterrows():
                    cm = "🏙️" if row['IsCittaMetro'] else ""
                    st.markdown(f"**{row['Provincia']}** {cm}: {row['IndiceVitalita']:.0f}")

                st.markdown("---")
                st.markdown("**⚠️ Bottom 5 Vitalità**")
                for _, row in vit_prov.tail(5).iterrows():
                    cm = "🏙️" if row['IsCittaMetro'] else ""
                    st.markdown(f"**{row['Provincia']}** {cm}: {row['IndiceVitalita']:.0f}")

            # === CLASSIFICA COMPLETA ===
            st.markdown("---")
            st.markdown("##### 📋 Classifica Completa Province")

            # Grafico a barre orizzontali con colori per vitalità
            col1, col2 = st.columns([3, 2])

            with col1:
                top30 = vit_prov.head(30)
                fig = px.bar(
                    top30.sort_values('IndiceVitalita', ascending=True),
                    x='IndiceVitalita', y='Provincia', orientation='h',
                    color='IndiceVitalita',
                    color_continuous_scale='RdYlGn',
                    text='IndiceVitalita',
                    hover_data=['Tesserati', 'Penetrazione', 'GareMedie', 'PctUnder60']
                )
                fig.update_traces(texttemplate='%{text:.0f}', textposition='auto', cliponaxis=False)
                fig.update_layout(height=700, showlegend=False)
                fig.add_vline(x=70, line_dash="dash", line_color="green", annotation_text="Eccellente")
                fig.add_vline(x=50, line_dash="dash", line_color="orange", annotation_text="Buono")
                fig.add_vline(x=30, line_dash="dash", line_color="red", annotation_text="Medio")
                st.plotly_chart(fig, use_container_width=True)

            with col2:
                st.markdown("**Tabella Dettaglio**")
                st.dataframe(
                    vit_prov[['Provincia', 'Stato', 'IndiceVitalita', 'Tesserati', 'Penetrazione', 'GareMedie', 'PctUnder60', 'PctAgonisti']]
                    .rename(columns={
                        'IndiceVitalita': 'Vitalità',
                        'Penetrazione': 'Tess/100k',
                        'GareMedie': 'Gare',
                        'PctUnder60': '%<60',
                        'PctAgonisti': '%Agon'
                    })
                    .style.background_gradient(subset=['Vitalità'], cmap='RdYlGn')
                    .format({
                        'Vitalità': '{:.0f}',
                        'Tess/100k': '{:.1f}',
                        'Gare': '{:.1f}',
                        '%<60': '{:.1f}%',
                        '%Agon': '{:.1%}'
                    }),
                    use_container_width=True,
                    height=650
                )

            # === VITALITÀ PER REGIONE ===
            st.markdown("---")
            st.markdown("##### 🗺️ Vitalità per Regione")

            vit_reg = df_ultimo.groupby('GrpArea').agg({
                'MmbCode': 'nunique',
                'GareGiocate': 'mean',
                'Anni': 'mean',
                'IsAgonista': 'mean'
            }).reset_index()
            vit_reg.columns = ['Regione', 'Tesserati', 'GareMedie', 'EtaMedia', 'PctAgonisti']
            vit_reg['Popolazione'] = vit_reg['Regione'].map(REGIONE_POPOLAZIONE)
            vit_reg['Penetrazione'] = vit_reg.apply(
                lambda r: (r['Tesserati'] / r['Popolazione'] * 100000) if r['Popolazione'] and r['Popolazione'] > 0 else 0, axis=1
            )

            # % under 60 per regione
            under60_reg = df_ultimo[df_ultimo['Anni'] < 60].groupby('GrpArea')['MmbCode'].nunique().reset_index()
            under60_reg.columns = ['Regione', 'Under60']
            vit_reg = vit_reg.merge(under60_reg, on='Regione', how='left')
            vit_reg['PctUnder60'] = (vit_reg['Under60'].fillna(0) / vit_reg['Tesserati'] * 100)

            # Indice vitalità regionale
            vit_reg['Score_Pen'] = (vit_reg['Penetrazione'] / vit_reg['Penetrazione'].max() * 100).clip(0, 100)
            vit_reg['Score_Att'] = (vit_reg['GareMedie'] / 50 * 100).clip(0, 100)
            vit_reg['Score_Gio'] = (vit_reg['PctUnder60'] / 30 * 100).clip(0, 100)
            vit_reg['Score_Ago'] = (vit_reg['PctAgonisti'] * 100 / 0.5 * 100).clip(0, 100)

            vit_reg['IndiceVitalita'] = (
                vit_reg['Score_Pen'] * 0.35 +
                vit_reg['Score_Att'] * 0.30 +
                vit_reg['Score_Gio'] * 0.20 +
                vit_reg['Score_Ago'] * 0.15
            ).round(1)

            vit_reg['NomeRegione'] = vit_reg['Regione'].map(NOMI_REGIONI_COMPLETI)
            vit_reg = vit_reg.sort_values('IndiceVitalita', ascending=False)

            col1, col2 = st.columns(2)

            with col1:
                fig = px.bar(
                    vit_reg.sort_values('IndiceVitalita', ascending=True),
                    x='IndiceVitalita', y='NomeRegione', orientation='h',
                    color='IndiceVitalita',
                    color_continuous_scale='RdYlGn',
                    text='IndiceVitalita',
                    title="Indice Vitalità per Regione"
                )
                fig.update_traces(texttemplate='%{text:.0f}', textposition='auto', cliponaxis=False)
                fig.update_layout(height=550, showlegend=False)
                st.plotly_chart(fig, use_container_width=True)

            with col2:
                st.dataframe(
                    vit_reg[['NomeRegione', 'IndiceVitalita', 'Tesserati', 'Penetrazione', 'GareMedie', 'PctUnder60']]
                    .rename(columns={
                        'NomeRegione': 'Regione',
                        'IndiceVitalita': 'Vitalità',
                        'Penetrazione': 'Tess/100k',
                        'GareMedie': 'Gare',
                        'PctUnder60': '%<60'
                    })
                    .style.background_gradient(subset=['Vitalità'], cmap='RdYlGn')
                    .format({
                        'Vitalità': '{:.0f}',
                        'Tess/100k': '{:.1f}',
                        'Gare': '{:.1f}',
                        '%<60': '{:.1f}%'
                    }),
                    use_container_width=True,
                    height=500
                )

        # ========== TAB 2: PROVINCE ==========
        with tab2:
            st.subheader("📊 Classifica Province per Tesserati e Penetrazione")

            col1, col2 = st.columns(2)

            # Prepara dati completi province
            prov_full = df_ultimo.groupby('Provincia').agg({
                'MmbCode': 'nunique',
                'GareGiocate': 'mean',
                'Anni': 'mean',
                'IsAgonista': 'sum'
            }).reset_index()
            prov_full.columns = ['Provincia', 'Tesserati', 'GareMedie', 'EtaMedia', 'Agonisti']
            prov_full['Popolazione'] = prov_full['Provincia'].map(PROVINCE_POPOLAZIONE)
            prov_full['TesseratiPer100k'] = prov_full.apply(
                lambda r: (r['Tesserati'] / r['Popolazione'] * 100000) if r['Popolazione'] > 0 else 0, axis=1
            )
            prov_full['IsCittaMetro'] = prov_full['Provincia'].apply(lambda x: x in CITTA_METROPOLITANE)
            prov_full['Regione'] = prov_full['Provincia'].map(PROVINCIA_TO_REGIONE)

            with col1:
                st.markdown("##### 🏆 Top 20 Province per Tesserati")
                top_tess = prov_full.nlargest(20, 'Tesserati')
                fig = px.bar(
                    top_tess.sort_values('Tesserati', ascending=True),
                    x='Tesserati', y='Provincia', orientation='h',
                    color='IsCittaMetro',
                    color_discrete_map={True: '#1E88E5', False: '#43A047'},
                    hover_data=['TesseratiPer100k', 'EtaMedia', 'GareMedie']
                )
                fig.update_layout(height=600, showlegend=True,
                                  legend_title="Città Metropolitana")
                st.plotly_chart(fig, use_container_width=True)

            with col2:
                st.markdown("##### 📈 Top 20 Province per Penetrazione (tesserati/100k ab.)")
                # Filtra province con almeno 20 tesserati per significatività
                prov_sig = prov_full[prov_full['Tesserati'] >= 20]
                top_pen = prov_sig.nlargest(20, 'TesseratiPer100k')
                fig = px.bar(
                    top_pen.sort_values('TesseratiPer100k', ascending=True),
                    x='TesseratiPer100k', y='Provincia', orientation='h',
                    color='IsCittaMetro',
                    color_discrete_map={True: '#1E88E5', False: '#43A047'},
                    hover_data=['Tesserati', 'Popolazione']
                )
                fig.update_layout(height=600, showlegend=True,
                                  legend_title="Città Metropolitana")
                fig.update_xaxes(title="Tesserati per 100.000 abitanti")
                st.plotly_chart(fig, use_container_width=True)

            # Tabella completa
            st.markdown("---")
            st.subheader("📋 Tabella Completa Province")

            # Selettore ordinamento
            col_ord1, col_ord2 = st.columns([1, 3])
            with col_ord1:
                ordina_per = st.selectbox("Ordina per:", ["Tesserati", "TesseratiPer100k", "EtaMedia", "GareMedie"])

            prov_display = prov_full.sort_values(ordina_per, ascending=False).copy()
            prov_display['Tipo'] = prov_display['IsCittaMetro'].map({True: '🏙️ Città Metro', False: '📍 Provincia'})

            st.dataframe(
                prov_display[['Provincia', 'Tipo', 'Tesserati', 'TesseratiPer100k', 'Popolazione', 'EtaMedia', 'GareMedie', 'Agonisti']]
                .style.background_gradient(subset=['Tesserati'], cmap='Blues')
                .background_gradient(subset=['TesseratiPer100k'], cmap='Greens')
                .format({
                    'TesseratiPer100k': '{:.1f}',
                    'EtaMedia': '{:.1f}',
                    'GareMedie': '{:.1f}',
                    'Popolazione': '{:,.0f}'
                }),
                use_container_width=True,
                height=500
            )

        # ========== TAB 3: CITTÀ METROPOLITANE ==========
        with tab3:
            st.subheader("🌆 Focus Città Metropolitane")
            st.markdown("Le 14 città metropolitane italiane a confronto")

            # Filtra solo città metropolitane
            cm_df = prov_full[prov_full['IsCittaMetro']].copy()
            cm_df = cm_df.sort_values('Tesserati', ascending=False)

            col1, col2 = st.columns(2)

            with col1:
                st.markdown("##### Tesserati per Città Metropolitana")
                fig = px.bar(
                    cm_df.sort_values('Tesserati', ascending=True),
                    x='Tesserati', y='Provincia', orientation='h',
                    color='TesseratiPer100k',
                    color_continuous_scale='Viridis'
                )
                fig.update_layout(height=500)
                st.plotly_chart(fig, use_container_width=True)

            with col2:
                st.markdown("##### Penetrazione nelle Città Metropolitane")
                fig = px.bar(
                    cm_df.sort_values('TesseratiPer100k', ascending=True),
                    x='TesseratiPer100k', y='Provincia', orientation='h',
                    color='Tesserati',
                    color_continuous_scale='Blues'
                )
                fig.update_layout(height=500)
                fig.update_xaxes(title="Tesserati per 100.000 abitanti")
                st.plotly_chart(fig, use_container_width=True)

            # Confronto CM vs Altre
            st.markdown("---")
            st.subheader("📊 Confronto: Città Metropolitane vs Altre Province")

            col1, col2, col3 = st.columns(3)

            with col1:
                # Distribuzione tesserati
                pie_data = pd.DataFrame({
                    'Tipo': ['Città Metropolitane', 'Altre Province'],
                    'Tesserati': [tesserati_cm, tesserati_altre]
                })
                fig = px.pie(pie_data, values='Tesserati', names='Tipo',
                            color_discrete_sequence=['#1E88E5', '#43A047'],
                            title="Distribuzione Tesserati")
                st.plotly_chart(fig, use_container_width=True)

            with col2:
                # Confronto età media
                eta_cm = df_ultimo[df_ultimo['IsCittaMetropolitana'] == True]['Anni'].mean()
                eta_altre = df_ultimo[df_ultimo['IsCittaMetropolitana'] == False]['Anni'].mean()
                bar_data = pd.DataFrame({
                    'Tipo': ['Città Metropolitane', 'Altre Province'],
                    'Età Media': [eta_cm, eta_altre]
                })
                fig = px.bar(bar_data, x='Tipo', y='Età Media',
                            color='Tipo', color_discrete_sequence=['#1E88E5', '#43A047'],
                            title="Età Media")
                fig.update_layout(showlegend=False)
                st.plotly_chart(fig, use_container_width=True)

            with col3:
                # Confronto gare medie
                gare_cm = df_ultimo[df_ultimo['IsCittaMetropolitana'] == True]['GareGiocate'].mean()
                gare_altre = df_ultimo[df_ultimo['IsCittaMetropolitana'] == False]['GareGiocate'].mean()
                bar_data = pd.DataFrame({
                    'Tipo': ['Città Metropolitane', 'Altre Province'],
                    'Gare Medie': [gare_cm, gare_altre]
                })
                fig = px.bar(bar_data, x='Tipo', y='Gare Medie',
                            color='Tipo', color_discrete_sequence=['#1E88E5', '#43A047'],
                            title="Gare Medie")
                fig.update_layout(showlegend=False)
                st.plotly_chart(fig, use_container_width=True)

            # Dettaglio città metropolitane
            st.markdown("---")
            st.subheader("📋 Dettaglio Città Metropolitane")
            st.dataframe(
                cm_df[['Provincia', 'Tesserati', 'TesseratiPer100k', 'Popolazione', 'EtaMedia', 'GareMedie', 'Agonisti']]
                .style.background_gradient(subset=['TesseratiPer100k'], cmap='Greens')
                .format({
                    'TesseratiPer100k': '{:.1f}',
                    'EtaMedia': '{:.1f}',
                    'GareMedie': '{:.1f}',
                    'Popolazione': '{:,.0f}'
                }),
                use_container_width=True
            )

        # ========== TAB 4: TREND TEMPORALE ==========
        with tab4:
            st.subheader("📈 Evoluzione Territoriale nel Tempo")

            # Trend per provincia (top 10)
            st.markdown("##### Trend Top 10 Province")

            # Calcola top 10 province per tesserati ultimo anno
            top10_prov = prov_full.nlargest(10, 'Tesserati')['Provincia'].tolist()

            # Trend storico
            trend_prov = df_prov[df_prov['Provincia'].isin(top10_prov)].groupby(
                ['Anno', 'Provincia']
            )['MmbCode'].nunique().reset_index()
            trend_prov.columns = ['Anno', 'Provincia', 'Tesserati']

            fig = px.line(trend_prov, x='Anno', y='Tesserati', color='Provincia',
                         markers=True, title="Evoluzione Tesserati - Top 10 Province")
            fig.add_vline(x=2020, line_dash="dash", line_color="red",
                         annotation_text="COVID-19")
            fig.update_layout(height=500)
            fig.update_xaxes(dtick=1)
            st.plotly_chart(fig, use_container_width=True)

            # Variazione % per provincia
            st.markdown("---")
            st.markdown("##### Variazione % Tesserati (primo anno disponibile vs ultimo)")

            # Calcola variazione per tutte le province con dati sufficienti
            var_prov = df_prov.groupby(['Provincia', 'Anno'])['MmbCode'].nunique().reset_index()
            var_prov.columns = ['Provincia', 'Anno', 'Tesserati']

            # Pivot per calcolare variazione
            var_pivot = var_prov.pivot(index='Provincia', columns='Anno', values='Tesserati')

            # Prendi primo e ultimo anno disponibile per ogni provincia
            primo_anno = var_pivot.columns.min()
            ultimo_anno_var = var_pivot.columns.max()

            var_calc = pd.DataFrame({
                'Provincia': var_pivot.index,
                'Tess_Inizio': var_pivot[primo_anno].values,
                'Tess_Fine': var_pivot[ultimo_anno_var].values
            })
            var_calc['Variazione_Pct'] = ((var_calc['Tess_Fine'] - var_calc['Tess_Inizio']) / var_calc['Tess_Inizio'] * 100).round(1)
            var_calc = var_calc.dropna()
            var_calc = var_calc[var_calc['Tess_Inizio'] >= 10]  # Minimo 10 tesserati iniziali

            col1, col2 = st.columns(2)

            with col1:
                st.markdown("**🟢 Top 10 Province in Crescita**")
                top_crescita = var_calc.nlargest(10, 'Variazione_Pct')
                fig = px.bar(
                    top_crescita.sort_values('Variazione_Pct', ascending=True),
                    x='Variazione_Pct', y='Provincia', orientation='h',
                    color='Variazione_Pct', color_continuous_scale='Greens',
                    text='Variazione_Pct'
                )
                fig.update_traces(texttemplate='%{text:.1f}%', textposition='auto', cliponaxis=False)
                fig.update_layout(height=400, showlegend=False)
                fig.update_xaxes(title=f"Variazione % ({primo_anno} → {ultimo_anno_var})")
                st.plotly_chart(fig, use_container_width=True)

            with col2:
                st.markdown("**🔴 Top 10 Province in Calo**")
                top_calo = var_calc.nsmallest(10, 'Variazione_Pct')
                fig = px.bar(
                    top_calo.sort_values('Variazione_Pct', ascending=False),
                    x='Variazione_Pct', y='Provincia', orientation='h',
                    color='Variazione_Pct', color_continuous_scale='Reds_r',
                    text='Variazione_Pct'
                )
                fig.update_traces(texttemplate='%{text:.1f}%', textposition='auto', cliponaxis=False)
                fig.update_layout(height=400, showlegend=False)
                fig.update_xaxes(title=f"Variazione % ({primo_anno} → {ultimo_anno_var})")
                st.plotly_chart(fig, use_container_width=True)

        # ========== TAB 5: MAPPA PENETRAZIONE ==========
        with tab5:
            st.subheader("🗺️ Mappa Penetrazione per Regione")
            st.markdown("Tesserati per 100.000 abitanti a livello regionale")

            # Calcola penetrazione per regione
            reg_stats = df_ultimo.groupby('GrpArea')['MmbCode'].nunique().reset_index()
            reg_stats.columns = ['Regione', 'Tesserati']
            reg_stats['Popolazione'] = reg_stats['Regione'].map(REGIONE_POPOLAZIONE)
            reg_stats['TesseratiPer100k'] = reg_stats.apply(
                lambda r: (r['Tesserati'] / r['Popolazione'] * 100000) if r['Popolazione'] > 0 else 0, axis=1
            )
            reg_stats['NomeRegione'] = reg_stats['Regione'].map(NOMI_REGIONI_COMPLETI)

            # Coordinate centroidi regioni
            COORD_REGIONI_MAP = {
                'Piemonte': (45.0522, 7.5155), "Valle d'Aosta": (45.7370, 7.3205),
                'Lombardia': (45.4791, 9.8452), 'Trentino': (46.0679, 11.1211),
                'Alto Adige': (46.7, 11.35), 'Veneto': (45.4414, 12.3155),
                'Friuli V.G.': (46.0711, 13.2346), 'Liguria': (44.4112, 8.9327),
                'Emilia-Romagna': (44.4949, 11.3426), 'Toscana': (43.7711, 11.2486),
                'Umbria': (42.9384, 12.6218), 'Marche': (43.6168, 13.5188),
                'Lazio': (41.8931, 12.4831), 'Abruzzo': (42.1920, 13.7289),
                'Molise': (41.6738, 14.7520), 'Campania': (40.8394, 14.2528),
                'Puglia': (41.1259, 16.8670), 'Basilicata': (40.6396, 15.8056),
                'Calabria': (38.9060, 16.5943), 'Sicilia': (37.5994, 14.0154),
                'Sardegna': (40.1209, 9.0129)
            }

            reg_stats['lat'] = reg_stats['NomeRegione'].map(lambda x: COORD_REGIONI_MAP.get(x, (0,0))[0])
            reg_stats['lon'] = reg_stats['NomeRegione'].map(lambda x: COORD_REGIONI_MAP.get(x, (0,0))[1])
            reg_stats = reg_stats.dropna(subset=['NomeRegione'])

            # Mappa
            col1, col2 = st.columns([3, 1])

            with col1:
                metrica_mappa = st.radio("Visualizza:", ["Tesserati per 100k abitanti", "Tesserati Totali"], horizontal=True)

                if metrica_mappa == "Tesserati per 100k abitanti":
                    size_col = 'TesseratiPer100k'
                    color_col = 'TesseratiPer100k'
                    title = f"Penetrazione Bridge per Regione - {ultimo_anno}"
                else:
                    size_col = 'Tesserati'
                    color_col = 'Tesserati'
                    title = f"Tesserati per Regione - {ultimo_anno}"

                fig = px.scatter_geo(
                    reg_stats,
                    lat='lat', lon='lon',
                    size=size_col, color=color_col,
                    hover_name='NomeRegione',
                    hover_data={
                        'Tesserati': True,
                        'TesseratiPer100k': ':.1f',
                        'Popolazione': ':,.0f',
                        'lat': False, 'lon': False
                    },
                    color_continuous_scale='YlOrRd',
                    size_max=50,
                    title=title
                )

                fig.update_geos(
                    scope='europe',
                    center=dict(lat=42.5, lon=12.5),
                    projection_scale=6,
                    showland=True,
                    landcolor='rgb(243, 243, 243)',
                    countrycolor='rgb(204, 204, 204)',
                    showcoastlines=True
                )
                fig.update_layout(height=600, margin=dict(l=0, r=0, t=40, b=0))
                st.plotly_chart(fig, use_container_width=True)

            with col2:
                st.markdown("**🏆 Top 5 Penetrazione**")
                for _, row in reg_stats.nlargest(5, 'TesseratiPer100k').iterrows():
                    st.markdown(f"**{row['NomeRegione']}**: {row['TesseratiPer100k']:.1f}/100k")

                st.markdown("---")
                st.markdown("**⚠️ Bottom 5 Penetrazione**")
                for _, row in reg_stats.nsmallest(5, 'TesseratiPer100k').iterrows():
                    st.markdown(f"**{row['NomeRegione']}**: {row['TesseratiPer100k']:.1f}/100k")

            # Tabella regioni con popolazione
            st.markdown("---")
            st.subheader("📋 Dettaglio Regioni")
            st.dataframe(
                reg_stats[['NomeRegione', 'Tesserati', 'Popolazione', 'TesseratiPer100k']]
                .sort_values('TesseratiPer100k', ascending=False)
                .style.background_gradient(subset=['TesseratiPer100k'], cmap='YlOrRd')
                .format({
                    'TesseratiPer100k': '{:.1f}',
                    'Popolazione': '{:,.0f}'
                }),
                use_container_width=True
            )

# ============================================================================
# PAGINA: MAPPA AGONISMO
# ============================================================================
elif pagina == "🏆 Mappa Agonismo":
    st.title("🏆 Mappa Agonismo Bridge in Italia")
    st.markdown("Distribuzione geografica dei giocatori agonisti e dei punti campionato")

    # Mapping codici regione -> nomi per GeoJSON
    REGIONI_GEOJSON = {
        'PIE': 'Piemonte', 'VAO': "Valle d'Aosta", 'LOM': 'Lombardia',
        'TRT': 'Trentino-Alto Adige', 'TRB': 'Trentino-Alto Adige',
        'VEN': 'Veneto', 'FRI': 'Friuli-Venezia Giulia',
        'LIG': 'Liguria', 'EMI': 'Emilia-Romagna', 'TOS': 'Toscana',
        'UMB': 'Umbria', 'MAR': 'Marche', 'LAZ': 'Lazio',
        'ABR': 'Abruzzo', 'MOL': 'Molise', 'CAM': 'Campania',
        'PUG': 'Puglia', 'BAS': 'Basilicata', 'CAB': 'Calabria',
        'SIC': 'Sicilia', 'SAR': 'Sardegna'
    }

    # Coordinate centroidi regioni per scatter map
    COORD_REGIONI = {
        'Piemonte': (45.0522, 7.5155), "Valle d'Aosta": (45.7370, 7.3205),
        'Lombardia': (45.4791, 9.8452), 'Trentino-Alto Adige': (46.4337, 11.1693),
        'Veneto': (45.4414, 12.3155), 'Friuli-Venezia Giulia': (46.0711, 13.2346),
        'Liguria': (44.4112, 8.9327), 'Emilia-Romagna': (44.4949, 11.3426),
        'Toscana': (43.7711, 11.2486), 'Umbria': (42.9384, 12.6218),
        'Marche': (43.6168, 13.5188), 'Lazio': (41.8931, 12.4831),
        'Abruzzo': (42.1920, 13.7289), 'Molise': (41.6738, 14.7520),
        'Campania': (40.8394, 14.2528), 'Puglia': (41.1259, 16.8670),
        'Basilicata': (40.6396, 15.8056), 'Calabria': (38.9060, 16.5943),
        'Sicilia': (37.5994, 14.0154), 'Sardegna': (40.1209, 9.0129)
    }

    # Filtri specifici per questa pagina
    col_filtri1, col_filtri2 = st.columns(2)
    with col_filtri1:
        anno_mappa = st.selectbox("Anno", sorted(df_filtered['Anno'].unique(), reverse=True), index=0)
    with col_filtri2:
        top_x = st.selectbox("Top X giocatori per media", [10, 20, 50, 100, 200, 500, "Tutti"], index=6)

    # Usa dati già filtrati dalla sidebar + filtro anno e tessera Agonista
    df_anno = df_filtered[(df_filtered['Anno'] == anno_mappa) & (df_filtered['MbtDesc'] == 'Agonista')]

    # Funzione per calcolare media top X per regione
    def calcola_media_top_x(group, x):
        if x == "Tutti":
            return group['PuntiCampionati'].mean()
        top = group.nlargest(min(x, len(group)), 'PuntiCampionati')
        return top['PuntiCampionati'].mean() if len(top) > 0 else 0

    # Aggrega per regione
    mappa_data = df_anno.groupby('GrpArea').agg({
        'MmbCode': 'nunique',
        'PuntiCampionati': ['sum', 'mean']
    }).reset_index()
    mappa_data.columns = ['Codice', 'Agonisti', 'PuntiTotali', 'PuntiMedi']

    # Calcola media Top X
    media_top_x = df_anno.groupby('GrpArea').apply(
        lambda g: calcola_media_top_x(g, top_x)
    ).reset_index()
    media_top_x.columns = ['Codice', 'MediaTopX']
    mappa_data = mappa_data.merge(media_top_x, on='Codice')

    mappa_data['Regione'] = mappa_data['Codice'].map(REGIONI_GEOJSON)
    mappa_data = mappa_data.dropna(subset=['Regione'])

    # Aggiungi coordinate
    mappa_data['lat'] = mappa_data['Regione'].map(lambda x: COORD_REGIONI.get(x, (0,0))[0])
    mappa_data['lon'] = mappa_data['Regione'].map(lambda x: COORD_REGIONI.get(x, (0,0))[1])

    # Metriche
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Agonisti Totali", f"{mappa_data['Agonisti'].sum():,}")
    with col2:
        st.metric("Punti Totali", f"{mappa_data['PuntiTotali'].sum():,.0f}")
    with col3:
        top_regione = mappa_data.loc[mappa_data['PuntiTotali'].idxmax(), 'Regione']
        st.metric("Regione Top", top_regione)
    with col4:
        label_top = f"Top {top_x}" if top_x != "Tutti" else "Tutti"
        st.metric(f"Media Punti ({label_top})", f"{mappa_data['MediaTopX'].mean():,.0f}")

    st.markdown("---")

    # Selezione metrica per mappa
    col1, col2 = st.columns([1, 3])
    with col1:
        top_label = f"Media Top {top_x}" if top_x != "Tutti" else "Media Punti"
        metrica_mappa = st.radio(
            "Visualizza:",
            ["Punti Campionati", "Numero Agonisti", top_label]
        )

    # Mappa a bolle
    if metrica_mappa == "Punti Campionati":
        size_col = 'PuntiTotali'
        color_col = 'PuntiTotali'
        title = f"Punti Campionati per Regione - {anno_mappa}"
    elif metrica_mappa == "Numero Agonisti":
        size_col = 'Agonisti'
        color_col = 'Agonisti'
        title = f"Numero Agonisti per Regione - {anno_mappa}"
    else:
        size_col = 'MediaTopX'
        color_col = 'MediaTopX'
        top_desc = f"Top {top_x}" if top_x != "Tutti" else "tutti i"
        title = f"Media Punti {top_desc} giocatori - {anno_mappa}"

    with col2:
        fig = px.scatter_geo(
            mappa_data,
            lat='lat',
            lon='lon',
            size=size_col,
            color=color_col,
            hover_name='Regione',
            hover_data={
                'Agonisti': True,
                'PuntiTotali': ':,.0f',
                'MediaTopX': ':,.0f',
                'lat': False,
                'lon': False
            },
            color_continuous_scale='YlOrRd',
            size_max=60,
            title=title
        )

        fig.update_geos(
            scope='europe',
            center=dict(lat=42.5, lon=12.5),
            projection_scale=6,
            showland=True,
            landcolor='rgb(243, 243, 243)',
            countrycolor='rgb(204, 204, 204)',
            showcoastlines=True,
            coastlinecolor='rgb(100, 100, 100)',
            showlakes=True,
            lakecolor='rgb(200, 220, 255)'
        )

        fig.update_layout(
            height=600,
            margin=dict(l=0, r=0, t=40, b=0)
        )

        st.plotly_chart(fig, use_container_width=True)

    # Tabella dettaglio
    st.subheader("📊 Dettaglio per Regione")
    top_col_name = f"Media Top {top_x}" if top_x != "Tutti" else "Media Punti"
    tabella = mappa_data[['Regione', 'Agonisti', 'PuntiTotali', 'MediaTopX']].copy()
    tabella.columns = ['Regione', 'Agonisti', 'Punti Totali', top_col_name]
    tabella = tabella.sort_values('Punti Totali', ascending=False)

    st.dataframe(
        tabella.style.background_gradient(subset=['Punti Totali'], cmap='YlOrRd')
        .background_gradient(subset=[top_col_name], cmap='Greens')
        .format({'Punti Totali': '{:,.0f}', top_col_name: '{:,.0f}'}),
        use_container_width=True
    )

    # Top agonisti
    st.markdown("---")
    st.subheader("🥇 Top 20 Agonisti per Punti Campionati")

    top_agonisti = df_anno.groupby(['MmbCode', 'MmbName', 'GrpArea']).agg({
        'PuntiCampionati': 'sum',
        'GareGiocate': 'sum',
        'Anni': 'first'
    }).reset_index()
    top_agonisti['Regione'] = top_agonisti['GrpArea'].map(REGIONI_GEOJSON)
    top_agonisti = top_agonisti.nlargest(20, 'PuntiCampionati')
    top_agonisti = top_agonisti[['MmbName', 'Regione', 'PuntiCampionati', 'GareGiocate', 'Anni']]
    top_agonisti.columns = ['Nome', 'Regione', 'Punti Campionati', 'Gare', 'Età']

    st.dataframe(
        top_agonisti.style.background_gradient(subset=['Punti Campionati'], cmap='Greens'),
        use_container_width=True
    )

# ============================================================================
# PAGINA: ANALISI CIRCOLI
# ============================================================================
elif pagina == "🏢 Analisi Associazioni":
    st.title("🏢 Analisi Associazioni")

    # Mostra filtri attivi
    if len(regioni_selezionate) < len(df['GrpArea'].unique()) or anni_range != (anni_min, anni_max):
        st.info(f"🔍 Filtri attivi: {len(regioni_selezionate)} regioni, anni {anni_range[0]}-{anni_range[1]}")

    # =========================================================================
    # CALCOLO METRICHE ASSOCIAZIONI DAI DATI FILTRATI
    # =========================================================================
    col_assoc = 'Associazione' if 'Associazione' in df_filtered.columns else 'GrpName'

    # Calcola retention/churn per associazione
    if len(df_filtered) > 0 and len(anni_selezionati) >= 2:
        # Calcola retention anno su anno
        retention_data = []
        for anno in anni_selezionati[:-1]:
            anno_succ = anno + 1
            if anno_succ in anni_selezionati:
                # Tesserati anno corrente per associazione
                tess_anno = df_filtered[df_filtered['Anno'] == anno].groupby(col_assoc)['MmbCode'].apply(set).to_dict()
                # Tesserati anno successivo
                tess_succ = df_filtered[df_filtered['Anno'] == anno_succ].groupby(col_assoc)['MmbCode'].apply(set).to_dict()

                for assoc in tess_anno:
                    if assoc in tess_succ:
                        ritesserati = len(tess_anno[assoc] & tess_succ[assoc])
                        totale = len(tess_anno[assoc])
                        if totale >= 5:
                            retention_data.append({
                                'Associazione': assoc,
                                'Anno': anno,
                                'Tesserati': totale,
                                'Ritesserati': ritesserati,
                                'TassoRetention': ritesserati / totale * 100
                            })

        if retention_data:
            retention_df = pd.DataFrame(retention_data)

            # Aggrega per associazione (media retention)
            assoc_retention = retention_df.groupby('Associazione').agg({
                'Tesserati': 'mean',
                'TassoRetention': 'mean'
            }).reset_index()
            assoc_retention.columns = ['Associazione', 'TesseratiMedi', 'TassoRetention']
            assoc_retention['TassoChurn'] = 100 - assoc_retention['TassoRetention']
            assoc_retention['TassoRetention'] = assoc_retention['TassoRetention'].round(1)
            assoc_retention['TassoChurn'] = assoc_retention['TassoChurn'].round(1)
            assoc_retention['TesseratiMedi'] = assoc_retention['TesseratiMedi'].round(0).astype(int)

            # Aggiungi regione
            regione_map = df_filtered.groupby(col_assoc)['GrpArea'].first().to_dict()
            assoc_retention['Regione'] = assoc_retention['Associazione'].map(regione_map)

            # Filtra associazioni con almeno 10 tesserati medi
            assoc_retention_filt = assoc_retention[assoc_retention['TesseratiMedi'] >= 10]

            col1, col2 = st.columns(2)

            with col1:
                st.subheader("🏆 Top 15 - Migliore Retention")
                top_retention = assoc_retention_filt.nlargest(15, 'TassoRetention')
                if len(top_retention) > 0:
                    fig = px.bar(top_retention.sort_values('TassoRetention'),
                                x='TassoRetention', y='Associazione',
                                orientation='h', color='TassoRetention',
                                color_continuous_scale='Greens',
                                hover_data=['Regione', 'TesseratiMedi'],
                                text='TassoRetention')
                    fig.update_traces(texttemplate='%{text:.0f}%', textposition='auto', cliponaxis=False)
                    fig.update_layout(height=500, yaxis={'categoryorder':'total ascending'},
                                     xaxis_title="% Retention", margin=dict(r=60))
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("Non ci sono abbastanza dati.")

            with col2:
                st.subheader("⚠️ Top 15 - Maggiore Churn")
                top_churn = assoc_retention_filt.nlargest(15, 'TassoChurn')
                if len(top_churn) > 0:
                    fig = px.bar(top_churn.sort_values('TassoChurn'),
                                x='TassoChurn', y='Associazione',
                                orientation='h', color='TassoChurn',
                                color_continuous_scale='Reds',
                                hover_data=['Regione', 'TesseratiMedi'],
                                text='TassoChurn')
                    fig.update_traces(texttemplate='%{text:.0f}%', textposition='auto', cliponaxis=False)
                    fig.update_layout(height=500, yaxis={'categoryorder':'total ascending'},
                                     xaxis_title="% Churn", margin=dict(r=60))
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("Non ci sono abbastanza dati.")

            # Tabella completa retention
            st.markdown("---")
            st.subheader("📊 Retention/Churn Tutte le Associazioni")
            st.dataframe(
                assoc_retention_filt[['Associazione', 'Regione', 'TesseratiMedi', 'TassoRetention', 'TassoChurn']]
                .sort_values('TassoRetention', ascending=False)
                .head(50),
                use_container_width=True, hide_index=True
            )
        else:
            st.warning("Non ci sono abbastanza dati per calcolare retention/churn.")
    else:
        st.warning("Seleziona almeno 2 anni consecutivi per vedere retention/churn.")

    # =========================================================================
    # ESPLORA ASSOCIAZIONI
    # =========================================================================
    st.markdown("---")
    st.subheader("🔍 Esplora Associazioni")

    associazioni_df = df_filtered.groupby([col_assoc, 'GrpArea']).agg({
        'MmbCode': 'nunique',
        'GareGiocate': 'mean',
        'Anni': 'mean'
    }).reset_index()
    associazioni_df.columns = ['Associazione', 'Regione', 'Tesserati', 'Gare Medie', 'Età Media']
    associazioni_df['Gare Medie'] = associazioni_df['Gare Medie'].round(1)
    associazioni_df['Età Media'] = associazioni_df['Età Media'].round(1)
    associazioni_df = associazioni_df.sort_values('Tesserati', ascending=False)

    # Filtro per nome associazione
    search = st.text_input("🔍 Cerca associazione:", "", key="search_assoc_main")
    if search:
        associazioni_df = associazioni_df[associazioni_df['Associazione'].str.contains(search, case=False, na=False)]

    st.dataframe(associazioni_df.head(100), use_container_width=True, hide_index=True)

# ============================================================================
# PAGINA: BRIDGE A SCUOLA
# ============================================================================
elif pagina == "🎓 Bridge a Scuola":
    st.title("🎓 Corsi Bridge & Conversione")
    st.markdown("""
    Analisi del percorso **"Scuola Bridge"** (3 anni) e della conversione in tesserati regolari.
    Il tasso di conversione ideale dovrebbe essere >80%.
    """)

    # =========================================================================
    # CALCOLO ON-THE-FLY DAI DATI FILTRATI
    # =========================================================================

    # Corsisti Scuola Bridge (filtrati per regione selezionata)
    corsi_filtered = df[
        (df['MbtDesc'] == 'Scuola Bridge') &
        (df['GrpArea'].isin(regioni_selezionate))
    ].copy()

    if len(corsi_filtered) == 0:
        st.warning("Nessun dato per i filtri selezionati.")
    else:
        # Storia di ogni corsista
        corsisti = corsi_filtered.groupby('MmbCode').agg({
            'Anno': ['min', 'max', 'count'],
            'Associazione': 'first',
            'GrpArea': 'first',
            'Anni': 'first',
            'GareGiocate': 'sum'
        }).reset_index()
        corsisti.columns = ['MmbCode', 'AnnoInizio', 'AnnoFine', 'AnniCorso',
                            'Associazione', 'Regione', 'Eta', 'GareTotali']

        # Filtra per anno inizio (se l'utente ha filtrato per anni)
        corsisti = corsisti[
            (corsisti['AnnoInizio'] >= anni_range[0]) &
            (corsisti['AnnoInizio'] <= anni_range[1])
        ]

        # Solo corsisti "maturi" (iniziati almeno 2 anni fa)
        anno_max_maturo = min(anni_range[1], 2023)  # Devono aver avuto tempo di convertire
        corsisti_maturi = corsisti[corsisti['AnnoInizio'] <= anno_max_maturo].copy()

        # Identifica chi è diventato tesserato regolare (in tutto il dataset, non filtrato)
        tessere_regolari = ['Ordinario Sportivo', 'Agonista', 'Ordinario Amatoriale', 'Non Agonista']
        regolari_members = set(df[df['MbtDesc'].isin(tessere_regolari)]['MmbCode'].unique())
        corsisti_maturi['Convertito'] = corsisti_maturi['MmbCode'].isin(regolari_members)

        # Calcola metriche
        n_corsisti = len(corsisti_maturi)
        n_convertiti = corsisti_maturi['Convertito'].sum()
        n_persi = n_corsisti - n_convertiti
        tasso_conv = 100 * n_convertiti / n_corsisti if n_corsisti > 0 else 0

        convertiti_df = corsisti_maturi[corsisti_maturi['Convertito']]
        persi_df = corsisti_maturi[~corsisti_maturi['Convertito']]

        gare_medie_conv = convertiti_df['GareTotali'].mean() if len(convertiti_df) > 0 else 0
        gare_medie_persi = persi_df['GareTotali'].mean() if len(persi_df) > 0 else 0
        durata_media_conv = convertiti_df['AnniCorso'].mean() if len(convertiti_df) > 0 else 0
        durata_media_persi = persi_df['AnniCorso'].mean() if len(persi_df) > 0 else 0

        # Conversione per durata
        conv_durata = corsisti_maturi.groupby('AnniCorso').agg({
            'MmbCode': 'count',
            'Convertito': ['sum', 'mean']
        })
        conv_durata.columns = ['Totale', 'Convertiti', 'TassoConv']
        conv_durata['TassoConv'] = (conv_durata['TassoConv'] * 100).round(1)
        conv_durata['Persi'] = conv_durata['Totale'] - conv_durata['Convertiti']
        conv_durata = conv_durata.reset_index()

        # Conversione per gare
        corsisti_maturi['FasciaGare'] = pd.cut(
            corsisti_maturi['GareTotali'],
            bins=[-1, 5, 15, 30, 60, 100, 10000],
            labels=['0-5', '6-15', '16-30', '31-60', '61-100', '100+']
        )
        conv_gare = corsisti_maturi.groupby('FasciaGare', observed=True).agg({
            'MmbCode': 'count',
            'Convertito': ['sum', 'mean']
        })
        conv_gare.columns = ['Totale', 'Convertiti', 'TassoConv']
        conv_gare['TassoConv'] = (conv_gare['TassoConv'] * 100).round(1)
        conv_gare = conv_gare.reset_index()

        # Conversione per regione
        conv_regione = corsisti_maturi.groupby('Regione').agg({
            'MmbCode': 'count',
            'Convertito': ['sum', 'mean'],
            'GareTotali': 'mean'
        })
        conv_regione.columns = ['Corsisti', 'Convertiti', 'TassoConv', 'GareMedie']
        conv_regione['TassoConv'] = (conv_regione['TassoConv'] * 100).round(1)
        conv_regione['GareMedie'] = conv_regione['GareMedie'].round(1)
        conv_regione['Persi'] = conv_regione['Corsisti'] - conv_regione['Convertiti']
        conv_regione = conv_regione[conv_regione['Corsisti'] >= 10].reset_index()

        # Conversione per associazione
        conv_ass = corsisti_maturi.groupby('Associazione').agg({
            'MmbCode': 'count',
            'Convertito': ['sum', 'mean'],
            'GareTotali': 'mean',
            'Regione': 'first'
        })
        conv_ass.columns = ['Corsisti', 'Convertiti', 'TassoConv', 'GareMedie', 'Regione']
        conv_ass['TassoConv'] = (conv_ass['TassoConv'] * 100).round(1)
        conv_ass['GareMedie'] = conv_ass['GareMedie'].round(1)
        conv_ass['Persi'] = conv_ass['Corsisti'] - conv_ass['Convertiti']
        conv_ass = conv_ass.reset_index()

        # =====================================================================
        # TAB
        # =====================================================================
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "📊 Overview", "🎯 Fattori Conversione", "🗺️ Per Regione",
            "🏢 Per Associazione", "🎒 Studenti Scuole"
        ])

        # TAB 1: OVERVIEW
        with tab1:
            st.subheader("Panoramica Conversione Corsi")

            # Mostra filtri attivi
            if len(regioni_selezionate) < len(df['GrpArea'].unique()):
                st.info(f"🔍 Filtro attivo: {len(regioni_selezionate)} regioni selezionate")

            # Alert principale
            if n_corsisti > 0:
                st.error(f"""
                **🚨 PROBLEMA: Perdiamo il {100 - tasso_conv:.0f}% dei corsisti!**

                Su {n_corsisti:,} persone che hanno fatto il corso,
                solo {n_convertiti:,} sono diventati tesserati regolari.
                **{n_persi:,} persone perse.**
                """)

                # KPI principali
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Corsisti Analizzati", f"{n_corsisti:,}",
                             help="Corsisti nelle regioni selezionate")
                with col2:
                    st.metric("Convertiti", f"{n_convertiti:,}",
                             delta=f"{tasso_conv:.1f}%")
                with col3:
                    st.metric("Persi", f"{n_persi:,}",
                             delta=f"-{100-tasso_conv:.0f}%", delta_color="inverse")
                with col4:
                    st.metric("Gare Medie Convertiti", f"{gare_medie_conv:.0f}",
                             help=f"vs {gare_medie_persi:.0f} gare dei persi")

                # Insight chiave
                st.markdown("### 🔑 La Chiave: FAR GIOCARE GARE")

                # Calcola insight
                conv_0_5 = conv_gare[conv_gare['FasciaGare'] == '0-5']['TassoConv'].values
                conv_100 = conv_gare[conv_gare['FasciaGare'] == '100+']['TassoConv'].values
                conv_1_anno = conv_durata[conv_durata['AnniCorso'] == 1]['TassoConv'].values
                conv_3_anni = conv_durata[conv_durata['AnniCorso'] == 3]['TassoConv'].values

                col1, col2 = st.columns(2)
                with col1:
                    fig_gare = go.Figure()
                    fig_gare.add_trace(go.Bar(
                        x=['0-5 gare', '100+ gare'],
                        y=[conv_0_5[0] if len(conv_0_5) > 0 else 0,
                           conv_100[0] if len(conv_100) > 0 else 0],
                        marker_color=['#dc2626', '#059669'],
                        text=[f"{conv_0_5[0]:.0f}%" if len(conv_0_5) > 0 else "N/A",
                              f"{conv_100[0]:.0f}%" if len(conv_100) > 0 else "N/A"],
                        textposition='auto', cliponaxis=False
                    ))
                    fig_gare.update_layout(
                        title="Conversione per Gare Giocate",
                        yaxis_title="% Conversione",
                        height=300,
                        showlegend=False
                    )
                    st.plotly_chart(fig_gare, use_container_width=True)

                with col2:
                    fig_durata = go.Figure()
                    fig_durata.add_trace(go.Bar(
                        x=['1 anno', '3 anni'],
                        y=[conv_1_anno[0] if len(conv_1_anno) > 0 else 0,
                           conv_3_anni[0] if len(conv_3_anni) > 0 else 0],
                        marker_color=['#f97316', '#2563eb'],
                        text=[f"{conv_1_anno[0]:.0f}%" if len(conv_1_anno) > 0 else "N/A",
                              f"{conv_3_anni[0]:.0f}%" if len(conv_3_anni) > 0 else "N/A"],
                        textposition='auto', cliponaxis=False
                    ))
                    fig_durata.update_layout(
                        title="Conversione per Durata Corso",
                        yaxis_title="% Conversione",
                        height=300,
                        showlegend=False
                    )
                    st.plotly_chart(fig_durata, use_container_width=True)

                st.success(f"""
                **PROFILO COMPARATIVO:**

                |  | Convertiti | Persi |
                |--|------------|-------|
                | Gare medie | **{gare_medie_conv:.0f}** | {gare_medie_persi:.0f} |
                | Durata corso | {durata_media_conv:.1f} anni | {durata_media_persi:.1f} anni |

                **→ Chi gioca tante gare converte, chi gioca poche abbandona!**
                """)

        # TAB 2: FATTORI CONVERSIONE
        with tab2:
            st.subheader("🎯 Fattori che Influenzano la Conversione")

            if len(conv_gare) > 0:
                st.markdown("### 1. Gare Giocate (FATTORE #1)")
                fig_gare_det = px.bar(
                    conv_gare, x='FasciaGare', y='TassoConv',
                    color='TassoConv', color_continuous_scale='RdYlGn',
                    text='TassoConv',
                    labels={'FasciaGare': 'Gare Giocate', 'TassoConv': '% Conversione'}
                )
                fig_gare_det.update_traces(texttemplate='%{text:.0f}%', textposition='auto', cliponaxis=False)
                fig_gare_det.update_layout(height=350)
                st.plotly_chart(fig_gare_det, use_container_width=True)

            if len(conv_durata) > 0:
                st.markdown("### 2. Durata del Corso")
                fig_durata_det = px.bar(
                    conv_durata, x='AnniCorso', y='TassoConv',
                    color='TassoConv', color_continuous_scale='Blues',
                    text='TassoConv',
                    labels={'AnniCorso': 'Anni di Corso', 'TassoConv': '% Conversione'}
                )
                fig_durata_det.update_traces(texttemplate='%{text:.0f}%', textposition='auto', cliponaxis=False)
                fig_durata_det.update_layout(height=350)
                st.plotly_chart(fig_durata_det, use_container_width=True)

                # Chi abbandona quando
                st.markdown("### 📉 Quando Abbandonano")
                churn_timing = conv_durata[['AnniCorso', 'Persi']].copy()
                churn_timing['Persi'] = churn_timing['Persi'].astype(int)
                tot_persi_chart = churn_timing['Persi'].sum()

                if tot_persi_chart > 0:
                    fig_churn = px.pie(
                        churn_timing, values='Persi', names='AnniCorso',
                        title=f"Quando abbandonano i {tot_persi_chart:,} corsisti persi",
                        color_discrete_sequence=px.colors.sequential.Reds_r
                    )
                    fig_churn.update_layout(height=350)
                    st.plotly_chart(fig_churn, use_container_width=True)

        # TAB 3: PER REGIONE
        with tab3:
            st.subheader("🗺️ Conversione per Regione")

            if len(conv_regione) > 0:
                conv_regione_sorted = conv_regione.sort_values('TassoConv', ascending=True)

                fig_reg = px.bar(
                    conv_regione_sorted,
                    x='TassoConv', y='Regione',
                    orientation='h',
                    color='TassoConv',
                    color_continuous_scale='RdYlGn',
                    text='TassoConv',
                    hover_data=['Corsisti', 'Convertiti', 'Persi', 'GareMedie']
                )
                fig_reg.update_traces(texttemplate='%{text:.0f}%', textposition='auto', cliponaxis=False)
                fig_reg.update_layout(height=max(400, len(conv_regione) * 25), yaxis_title="", xaxis_title="% Conversione",
                                     margin=dict(r=60))
                st.plotly_chart(fig_reg, use_container_width=True)

                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("### ✅ Migliori Regioni")
                    st.dataframe(conv_regione.nlargest(5, 'TassoConv')[['Regione', 'TassoConv', 'GareMedie', 'Corsisti']],
                                hide_index=True, use_container_width=True)
                with col2:
                    st.markdown("### ❌ Peggiori Regioni")
                    st.dataframe(conv_regione.nsmallest(5, 'TassoConv')[['Regione', 'TassoConv', 'GareMedie', 'Corsisti']],
                                hide_index=True, use_container_width=True)
            else:
                st.info("Non ci sono abbastanza dati per questa vista.")

        # TAB 4: PER ASSOCIAZIONE
        with tab4:
            st.subheader("🏢 Conversione per Associazione")

            min_corsisti = st.slider("Minimo corsisti", 5, 50, 15)
            conv_ass_filt = conv_ass[conv_ass['Corsisti'] >= min_corsisti].copy()

            if len(conv_ass_filt) > 0:
                st.markdown(f"### 🏆 Top Associazioni (≥{min_corsisti} corsisti)")
                top_ass = conv_ass_filt.nlargest(15, 'TassoConv')

                fig_top = px.bar(
                    top_ass.sort_values('TassoConv', ascending=True),
                    x='TassoConv', y='Associazione',
                    orientation='h',
                    color='TassoConv',
                    color_continuous_scale='Greens',
                    text='TassoConv',
                    hover_data=['Corsisti', 'GareMedie', 'Regione']
                )
                fig_top.update_traces(texttemplate='%{text:.0f}%', textposition='auto', cliponaxis=False)
                fig_top.update_layout(height=450, yaxis_title="", margin=dict(r=60))
                st.plotly_chart(fig_top, use_container_width=True)

                st.markdown("### ⚠️ Associazioni da Monitorare")
                bottom_ass = conv_ass_filt.nsmallest(15, 'TassoConv')

                fig_bottom = px.bar(
                    bottom_ass.sort_values('TassoConv', ascending=False),
                    x='TassoConv', y='Associazione',
                    orientation='h',
                    color='TassoConv',
                    color_continuous_scale='Reds_r',
                    text='TassoConv',
                    hover_data=['Corsisti', 'GareMedie', 'Regione']
                )
                fig_bottom.update_traces(texttemplate='%{text:.0f}%', textposition='auto', cliponaxis=False)
                fig_bottom.update_layout(height=450, yaxis_title="", margin=dict(r=60))
                st.plotly_chart(fig_bottom, use_container_width=True)

                # Tabella completa
                st.markdown("### 📋 Tabella Completa")
                search_ass = st.text_input("🔍 Cerca associazione:", "", key="search_ass_conv")
                if search_ass:
                    conv_ass_filt = conv_ass_filt[conv_ass_filt['Associazione'].str.contains(search_ass, case=False, na=False)]

                st.dataframe(
                    conv_ass_filt[['Associazione', 'Regione', 'Corsisti', 'Convertiti', 'Persi', 'TassoConv', 'GareMedie']]
                    .sort_values('TassoConv', ascending=False),
                    use_container_width=True,
                    hide_index=True
                )
            else:
                st.info(f"Nessuna associazione con almeno {min_corsisti} corsisti.")

        # TAB 5: STUDENTI SCUOLE
        with tab5:
            st.subheader("🎒 Bridge nelle Scuole")

            # Studenti (filtrati per regione)
            studenti_filtered = df[
                (df['MbtDesc'].isin(['Ist.Scolastici', 'Studente CAS', 'CAS Giovanile'])) &
                (df['GrpArea'].isin(regioni_selezionate)) &
                (df['Anno'].isin(anni_selezionati))
            ]

            if len(studenti_filtered) > 0:
                n_studenti = studenti_filtered['MmbCode'].nunique()
                studenti_set = set(studenti_filtered['MmbCode'].unique())
                conv_studenti = studenti_set & regolari_members
                tasso_conv_stud = 100 * len(conv_studenti) / len(studenti_set) if len(studenti_set) > 0 else 0

                # Trend per anno
                trend_stud = studenti_filtered.groupby('Anno')['MmbCode'].nunique().reset_index()
                trend_stud.columns = ['Anno', 'Iscritti']

                st.error(f"""
                **🚨 PROGRAMMA SCOLASTICO**

                - Studenti nel periodo selezionato: **{n_studenti:,}**
                - Tasso conversione a tesserati: solo **{tasso_conv_stud:.1f}%**
                """)

                col1, col2 = st.columns(2)
                with col1:
                    fig_stud = go.Figure()
                    fig_stud.add_trace(go.Bar(
                        x=trend_stud['Anno'],
                        y=trend_stud['Iscritti'],
                        marker_color=['#dc2626' if y < 200 else '#059669' for y in trend_stud['Iscritti']]
                    ))
                    fig_stud.add_vline(x=2020, line_dash="dash", line_color="red", opacity=0.5)
                    fig_stud.update_layout(title="Studenti per Anno", height=350)
                    fig_stud.update_xaxes(dtick=1)
                    st.plotly_chart(fig_stud, use_container_width=True)

                with col2:
                    fig_conv_stud = go.Figure(go.Pie(
                        values=[len(conv_studenti), n_studenti - len(conv_studenti)],
                        labels=['Convertiti', 'Non Convertiti'],
                        hole=0.6,
                        marker_colors=['#059669', '#e5e7eb']
                    ))
                    fig_conv_stud.add_annotation(
                        text=f"<b>{tasso_conv_stud:.1f}%</b>",
                        x=0.5, y=0.5, font_size=24, showarrow=False
                    )
                    fig_conv_stud.update_layout(title="Conversione Studenti", height=350, showlegend=False)
                    st.plotly_chart(fig_conv_stud, use_container_width=True)

                # Scuole attive
                st.markdown("### 🏫 Scuole Attive")
                scuole = studenti_filtered.groupby('Associazione').agg({
                    'MmbCode': 'nunique',
                    'GrpArea': 'first',
                    'Anni': 'mean'
                }).reset_index()
                scuole.columns = ['Scuola', 'Studenti', 'Regione', 'EtàMedia']
                scuole['EtàMedia'] = scuole['EtàMedia'].round(1)
                scuole = scuole.sort_values('Studenti', ascending=False)

                st.dataframe(scuole.head(15), use_container_width=True, hide_index=True)

                # ============================================================
                # ANALISI STUDENTI CON PUNTI CAMPIONATO
                # ============================================================
                st.markdown("---")
                st.markdown("### 🏆 Studenti che Partecipano a Gare con Punti")
                st.markdown("Analisi degli studenti che, oltre al percorso scolastico, partecipano a tornei con punti campionato.")

                # Studenti con punti campionato
                stud_con_punti = studenti_filtered[studenti_filtered['PuntiCampionati'] > 0].copy()
                n_stud_punti = stud_con_punti['MmbCode'].nunique()
                pct_stud_punti = n_stud_punti / n_studenti * 100 if n_studenti > 0 else 0

                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Studenti Totali", f"{n_studenti:,}")
                with col2:
                    st.metric("Con Punti Campionato", f"{n_stud_punti:,}", f"{pct_stud_punti:.1f}%")
                with col3:
                    punti_medi = stud_con_punti['PuntiCampionati'].mean() if len(stud_con_punti) > 0 else 0
                    st.metric("Punti Medi", f"{punti_medi:.0f}")

                if n_stud_punti > 0:
                    # Crea fasce età per studenti
                    stud_con_punti['FasciaEta'] = pd.cut(
                        stud_con_punti['Anni'],
                        bins=[0, 12, 15, 18, 25, 100],
                        labels=['<12', '12-14', '15-17', '18-24', '25+']
                    )

                    col1, col2 = st.columns(2)

                    with col1:
                        # Per fascia età
                        st.markdown("#### Per Classe d'Età")
                        stud_eta = stud_con_punti.groupby('FasciaEta', observed=True).agg({
                            'MmbCode': 'nunique',
                            'PuntiCampionati': 'mean',
                            'GareGiocate': 'mean'
                        }).reset_index()
                        stud_eta.columns = ['Fascia Età', 'Studenti', 'Punti Medi', 'Gare Medie']
                        stud_eta['Punti Medi'] = stud_eta['Punti Medi'].round(0)
                        stud_eta['Gare Medie'] = stud_eta['Gare Medie'].round(1)

                        # Calcola % sul totale studenti per fascia
                        tot_per_fascia = studenti_filtered.copy()
                        tot_per_fascia['FasciaEta'] = pd.cut(
                            tot_per_fascia['Anni'],
                            bins=[0, 12, 15, 18, 25, 100],
                            labels=['<12', '12-14', '15-17', '18-24', '25+']
                        )
                        tot_fascia = tot_per_fascia.groupby('FasciaEta', observed=True)['MmbCode'].nunique()
                        stud_eta['% Fascia'] = stud_eta.apply(
                            lambda r: f"{r['Studenti']/tot_fascia.get(r['Fascia Età'], 1)*100:.1f}%" if tot_fascia.get(r['Fascia Età'], 0) > 0 else "0%",
                            axis=1
                        )

                        st.dataframe(stud_eta, use_container_width=True, hide_index=True)

                        # Grafico
                        fig = px.bar(stud_eta, x='Fascia Età', y='Studenti',
                                    color='Punti Medi', color_continuous_scale='Viridis',
                                    title="Studenti Agonisti per Età")
                        fig.update_layout(height=300)
                        st.plotly_chart(fig, use_container_width=True)

                    with col2:
                        # Per regione
                        st.markdown("#### Per Regione")
                        stud_reg = stud_con_punti.groupby('GrpArea').agg({
                            'MmbCode': 'nunique',
                            'PuntiCampionati': 'mean',
                            'GareGiocate': 'mean'
                        }).reset_index()
                        stud_reg.columns = ['Regione', 'Studenti', 'Punti Medi', 'Gare Medie']
                        stud_reg['Punti Medi'] = stud_reg['Punti Medi'].round(0)
                        stud_reg['Gare Medie'] = stud_reg['Gare Medie'].round(1)
                        stud_reg = stud_reg.sort_values('Studenti', ascending=False)

                        # Calcola % sul totale studenti per regione
                        tot_per_reg = studenti_filtered.groupby('GrpArea')['MmbCode'].nunique()
                        stud_reg['% Regione'] = stud_reg.apply(
                            lambda r: f"{r['Studenti']/tot_per_reg.get(r['Regione'], 1)*100:.1f}%" if tot_per_reg.get(r['Regione'], 0) > 0 else "0%",
                            axis=1
                        )

                        st.dataframe(stud_reg.head(15), use_container_width=True, hide_index=True)

                        # Grafico
                        fig = px.bar(stud_reg.head(10), x='Regione', y='Studenti',
                                    color='Punti Medi', color_continuous_scale='Viridis',
                                    title="Top 10 Regioni - Studenti Agonisti")
                        fig.update_layout(height=300)
                        st.plotly_chart(fig, use_container_width=True)

                    # Insight
                    if pct_stud_punti < 10:
                        st.warning(f"""
                        ⚠️ **Solo il {pct_stud_punti:.1f}% degli studenti partecipa a tornei con punti.**

                        Suggerimenti:
                        - Organizzare tornei scolastici con punti campionato
                        - Creare percorsi "dal banco alla gara"
                        - Incentivare partecipazione con premi/riconoscimenti
                        """)
                    else:
                        st.success(f"✅ Il {pct_stud_punti:.1f}% degli studenti partecipa a tornei agonistici - buon coinvolgimento!")
                else:
                    st.info("Nessuno studente con punti campionato nel periodo selezionato.")
            else:
                st.info("Nessun dato studenti per i filtri selezionati.")

# ============================================================================
# PAGINA: FOCUS PUGLIA
# ============================================================================
elif pagina == "🎯 Focus Puglia":
    st.title("🎯 Focus Puglia 2022-2025")
    st.markdown("""
    Analisi approfondita della **Puglia** negli ultimi 4 anni, con focus su:
    - Trend tesseramenti e composizione per tipo tessera
    - **Bridge a Scuola**: conversione allievi in giocatori
    - Tracciamento individuale: da allievo a quale tessera
    - Performance per circolo
    """)

    # =========================================================================
    # FILTRO DATI PUGLIA 2022-2025
    # =========================================================================
    ANNI_PUGLIA = [2022, 2023, 2024, 2025]

    df_puglia = df[
        (df['GrpArea'] == 'PUG') &
        (df['Anno'].isin(ANNI_PUGLIA))
    ].copy()

    if len(df_puglia) == 0:
        st.warning("Nessun dato disponibile per la Puglia nel periodo 2022-2025.")
    else:
        # =====================================================================
        # TAB
        # =====================================================================
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "📊 Overview", "🎓 Conversione Allievi", "📋 Dettaglio Conversione",
            "🏢 Circoli", "📈 Confronto Nazionale"
        ])

        # =====================================================================
        # TAB 1: OVERVIEW
        # =====================================================================
        with tab1:
            st.subheader("Panoramica Puglia 2022-2025")

            # Trend per anno
            trend_puglia = df_puglia.groupby('Anno').agg({
                'MmbCode': 'nunique',
                'GareGiocate': 'mean',
                'PuntiTotali': 'mean'
            }).reset_index()
            trend_puglia.columns = ['Anno', 'Tesserati', 'GareMedia', 'PuntiMedi']

            # Calcola variazioni
            tess_2022 = trend_puglia[trend_puglia['Anno'] == 2022]['Tesserati'].values
            tess_2025 = trend_puglia[trend_puglia['Anno'] == 2025]['Tesserati'].values
            tess_2022 = tess_2022[0] if len(tess_2022) > 0 else 0
            tess_2025 = tess_2025[0] if len(tess_2025) > 0 else 0
            var_4_anni = ((tess_2025 - tess_2022) / tess_2022 * 100) if tess_2022 > 0 else 0

            # KPI principali
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric("Tesserati 2025", f"{tess_2025:,}",
                         delta=f"{var_4_anni:+.1f}% vs 2022")
            with col2:
                st.metric("Tesserati 2022", f"{tess_2022:,}")
            with col3:
                gare_media = df_puglia['GareGiocate'].mean()
                st.metric("Gare Medie", f"{gare_media:.1f}")
            with col4:
                eta_media = df_puglia['Anni'].mean() if 'Anni' in df_puglia.columns else 0
                st.metric("Età Media", f"{eta_media:.1f} anni")

            st.markdown("---")

            # Grafico trend
            fig_trend = px.bar(
                trend_puglia, x='Anno', y='Tesserati',
                title="Trend Tesserati Puglia 2022-2025",
                text='Tesserati',
                color='Tesserati',
                color_continuous_scale='Blues'
            )
            fig_trend.update_traces(texttemplate='%{text:,}', textposition='outside', cliponaxis=False)
            fig_trend.update_layout(showlegend=False, height=400)
            st.plotly_chart(fig_trend, use_container_width=True)

            # Composizione per tipo tessera
            st.markdown("### Composizione per Tipo Tessera")

            tessere_puglia = df_puglia.groupby(['Anno', 'MbtDesc']).agg({
                'MmbCode': 'nunique'
            }).reset_index()
            tessere_puglia.columns = ['Anno', 'TipoTessera', 'Tesserati']

            # Filtra tessere principali
            tessere_principali = ['Scuola Bridge', 'Ordinario Sportivo', 'Agonista', 'Ordinario Amatoriale']
            tessere_plot = tessere_puglia[tessere_puglia['TipoTessera'].isin(tessere_principali)]

            fig_tessere = px.bar(
                tessere_plot, x='Anno', y='Tesserati', color='TipoTessera',
                title="Composizione Tessere Puglia",
                barmode='group'
            )
            fig_tessere.update_layout(height=400)
            st.plotly_chart(fig_tessere, use_container_width=True)

            # Tabella riepilogo
            with st.expander("📋 Dati Dettagliati"):
                pivot_tessere = tessere_puglia.pivot(index='Anno', columns='TipoTessera', values='Tesserati').fillna(0)
                st.dataframe(pivot_tessere, use_container_width=True)

        # =====================================================================
        # TAB 2: CONVERSIONE ALLIEVI
        # =====================================================================
        with tab2:
            st.subheader("🎓 Conversione Allievi Scuola Bridge")

            st.markdown("""
            **Focus principale**: quanti allievi della Scuola Bridge si sono trasformati in giocatori
            e con quale tipo di tessera.
            """)

            # Identifica tutti gli allievi Scuola Bridge in Puglia
            allievi_sb = df_puglia[df_puglia['MbtDesc'] == 'Scuola Bridge']
            allievi_codes = allievi_sb['MmbCode'].unique()

            st.info(f"**{len(allievi_codes):,}** allievi unici in Scuola Bridge in Puglia 2022-2025")

            # Traccia conversione per ogni allievo
            tessere_regolari = ['Ordinario Sportivo', 'Agonista', 'Ordinario Amatoriale', 'Non Agonista']
            risultati_conv = []

            for mmbcode in allievi_codes:
                # Storia completa del giocatore in Puglia (tutti gli anni)
                storia = df[(df['MmbCode'] == mmbcode) & (df['GrpArea'] == 'PUG')].sort_values('Anno')

                storia_sb = storia[storia['MbtDesc'] == 'Scuola Bridge']
                if len(storia_sb) == 0:
                    continue

                anno_inizio = storia_sb['Anno'].min()
                anni_in_sb = storia_sb['Anno'].nunique()
                gare_in_sb = storia_sb['GareGiocate'].sum()

                # Verifica se ha cambiato tessera
                storia_non_sb = storia[storia['MbtDesc'].isin(tessere_regolari)]

                if len(storia_non_sb) > 0:
                    prima_conv = storia_non_sb.sort_values('Anno').iloc[0]
                    anno_conv = prima_conv['Anno']
                    tessera_dest = prima_conv['MbtDesc']
                    post_conv = storia_non_sb[storia_non_sb['Anno'] >= anno_conv]
                    gare_post = post_conv['GareGiocate'].sum()
                    punti_post = post_conv['PuntiTotali'].sum()
                    convertito = True
                else:
                    anno_conv = None
                    tessera_dest = 'Non Convertito'
                    gare_post = 0
                    punti_post = 0
                    convertito = False

                ultimo_anno = storia['Anno'].max()

                risultati_conv.append({
                    'MmbCode': mmbcode,
                    'AnnoInizio': anno_inizio,
                    'AnniInSB': anni_in_sb,
                    'GareInSB': gare_in_sb,
                    'Convertito': convertito,
                    'AnnoConversione': anno_conv,
                    'TesseraDestinazione': tessera_dest,
                    'GareDopoConv': gare_post,
                    'PuntiDopoConv': punti_post,
                    'UltimoAnno': ultimo_anno
                })

            df_conv = pd.DataFrame(risultati_conv)

            if len(df_conv) > 0:
                # Statistiche aggregate
                n_totale = len(df_conv)
                n_convertiti = df_conv['Convertito'].sum()
                n_non_conv = n_totale - n_convertiti
                tasso_conv = (n_convertiti / n_totale * 100) if n_totale > 0 else 0

                # KPI conversione
                col1, col2, col3, col4 = st.columns(4)

                with col1:
                    st.metric("Allievi Totali", f"{n_totale:,}")
                with col2:
                    st.metric("Convertiti", f"{n_convertiti:,}",
                             delta=f"{tasso_conv:.1f}%")
                with col3:
                    st.metric("In Formazione / Persi", f"{n_non_conv:,}",
                             delta=f"{100-tasso_conv:.1f}%", delta_color="inverse")
                with col4:
                    convertiti_df = df_conv[df_conv['Convertito']]
                    if len(convertiti_df) > 0:
                        convertiti_df = convertiti_df.copy()
                        convertiti_df['TempoConv'] = convertiti_df['AnnoConversione'] - convertiti_df['AnnoInizio']
                        tempo_medio = convertiti_df['TempoConv'].mean()
                    else:
                        tempo_medio = 0
                    st.metric("Tempo Medio Conversione", f"{tempo_medio:.1f} anni")

                st.markdown("---")

                # Funnel conversione
                st.markdown("### Funnel Conversione")

                col1, col2 = st.columns(2)

                with col1:
                    fig_funnel = go.Figure(go.Funnel(
                        y=['Allievi Totali', 'Convertiti'],
                        x=[n_totale, n_convertiti],
                        textinfo="value+percent initial",
                        marker_color=['#3b82f6', '#22c55e']
                    ))
                    fig_funnel.update_layout(title="Funnel Conversione", height=350)
                    st.plotly_chart(fig_funnel, use_container_width=True)

                with col2:
                    # Tessere di destinazione
                    if n_convertiti > 0:
                        dest_counts = convertiti_df['TesseraDestinazione'].value_counts().reset_index()
                        dest_counts.columns = ['Tessera', 'Numero']

                        fig_dest = px.pie(
                            dest_counts, values='Numero', names='Tessera',
                            title="Tessere di Destinazione",
                            color_discrete_sequence=px.colors.qualitative.Set2
                        )
                        fig_dest.update_layout(height=350)
                        st.plotly_chart(fig_dest, use_container_width=True)

                # Insight principale
                if n_convertiti > 0:
                    tessera_principale = convertiti_df['TesseraDestinazione'].value_counts().index[0]
                    tessera_principale_pct = convertiti_df['TesseraDestinazione'].value_counts().iloc[0] / n_convertiti * 100
                    gare_media_conv = convertiti_df['GareDopoConv'].mean()

                    st.success(f"""
                    **📊 Insight Chiave:**
                    - **{tasso_conv:.1f}%** degli allievi si è convertito in giocatore
                    - La tessera di destinazione principale è **{tessera_principale}** ({tessera_principale_pct:.0f}%)
                    - Tempo medio di conversione: **{tempo_medio:.1f} anni**
                    - Gare medie dopo conversione: **{gare_media_conv:.0f}**
                    """)

                # Conversione per anno di inizio
                st.markdown("### Conversione per Anno di Inizio")

                conv_per_anno = df_conv.groupby('AnnoInizio').agg({
                    'MmbCode': 'count',
                    'Convertito': ['sum', 'mean']
                }).reset_index()
                conv_per_anno.columns = ['AnnoInizio', 'Totale', 'Convertiti', 'TassoConv']
                conv_per_anno['TassoConv'] = (conv_per_anno['TassoConv'] * 100).round(1)

                fig_anno = px.bar(
                    conv_per_anno, x='AnnoInizio', y='TassoConv',
                    text='TassoConv',
                    title="Tasso di Conversione per Anno di Inizio Corso",
                    color='TassoConv',
                    color_continuous_scale='RdYlGn'
                )
                fig_anno.update_traces(texttemplate='%{text:.1f}%', textposition='outside', cliponaxis=False)
                fig_anno.update_layout(height=400, showlegend=False)
                st.plotly_chart(fig_anno, use_container_width=True)

                st.caption("Nota: gli allievi più recenti (2024-2025) hanno avuto meno tempo per convertirsi.")

        # =====================================================================
        # TAB 3: DETTAGLIO CONVERSIONE
        # =====================================================================
        with tab3:
            st.subheader("📋 Dettaglio Conversione Individuale")

            if len(df_conv) > 0:
                # Filtri
                col1, col2 = st.columns(2)

                with col1:
                    filtro_stato = st.selectbox(
                        "Stato",
                        ["Tutti", "Solo Convertiti", "Solo Non Convertiti"]
                    )

                with col2:
                    if filtro_stato == "Solo Convertiti":
                        tessere_uniche = df_conv[df_conv['Convertito']]['TesseraDestinazione'].unique().tolist()
                        filtro_tessera = st.selectbox("Tessera Destinazione", ["Tutte"] + tessere_uniche)
                    else:
                        filtro_tessera = "Tutte"

                # Applica filtri
                df_show = df_conv.copy()

                if filtro_stato == "Solo Convertiti":
                    df_show = df_show[df_show['Convertito']]
                elif filtro_stato == "Solo Non Convertiti":
                    df_show = df_show[~df_show['Convertito']]

                if filtro_tessera != "Tutte":
                    df_show = df_show[df_show['TesseraDestinazione'] == filtro_tessera]

                # Mostra tabella
                st.markdown(f"**{len(df_show):,}** record trovati")

                # Prepara per visualizzazione
                df_display = df_show[[
                    'MmbCode', 'AnnoInizio', 'AnniInSB', 'GareInSB',
                    'Convertito', 'AnnoConversione', 'TesseraDestinazione',
                    'GareDopoConv', 'PuntiDopoConv', 'UltimoAnno'
                ]].copy()

                df_display['Convertito'] = df_display['Convertito'].map({True: '✅ Sì', False: '❌ No'})
                df_display['AnnoConversione'] = df_display['AnnoConversione'].fillna('-')

                st.dataframe(df_display, use_container_width=True, height=500)

                # Download
                csv = df_show.to_csv(index=False).encode('utf-8')
                st.download_button(
                    "📥 Scarica CSV",
                    csv,
                    "conversione_puglia_dettaglio.csv",
                    "text/csv"
                )

                # Statistiche aggiuntive
                st.markdown("---")
                st.markdown("### Statistiche per Tessera di Destinazione")

                stats_tessera = df_conv.groupby('TesseraDestinazione').agg({
                    'MmbCode': 'count',
                    'AnniInSB': 'mean',
                    'GareInSB': 'mean',
                    'GareDopoConv': 'mean',
                    'PuntiDopoConv': 'mean'
                }).reset_index()
                stats_tessera.columns = ['Tessera', 'Numero', 'AnniMediInSB', 'GareMedieInSB', 'GareMediePost', 'PuntiMediPost']
                stats_tessera = stats_tessera.sort_values('Numero', ascending=False)

                st.dataframe(stats_tessera.round(1), use_container_width=True)

        # =====================================================================
        # TAB 4: CIRCOLI
        # =====================================================================
        with tab4:
            st.subheader("🏢 Performance Circoli Pugliesi")

            # Statistiche per circolo
            col_assoc = 'Associazione' if 'Associazione' in df_puglia.columns else 'GrpName'

            circoli = df_puglia.groupby(col_assoc).agg({
                'MmbCode': 'nunique',
                'GareGiocate': 'mean',
                'PuntiTotali': 'mean',
                'Anno': lambda x: len(x.unique())
            }).reset_index()
            circoli.columns = ['Circolo', 'Tesserati', 'GareMedia', 'PuntiMedi', 'AnniAttivi']
            circoli = circoli.sort_values('Tesserati', ascending=False)

            # Allievi per circolo
            sb_circoli = df_puglia[df_puglia['MbtDesc'] == 'Scuola Bridge'].groupby(col_assoc).agg({
                'MmbCode': 'nunique'
            }).reset_index()
            sb_circoli.columns = ['Circolo', 'AllieviSB']

            circoli = circoli.merge(sb_circoli, on='Circolo', how='left')
            circoli['AllieviSB'] = circoli['AllieviSB'].fillna(0).astype(int)
            circoli['QuotaSB'] = (circoli['AllieviSB'] / circoli['Tesserati'] * 100).round(1)

            # KPI
            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric("Circoli Attivi", f"{len(circoli):,}")
            with col2:
                st.metric("Tesserati Totali", f"{circoli['Tesserati'].sum():,}")
            with col3:
                st.metric("Allievi SB Totali", f"{circoli['AllieviSB'].sum():,}")

            st.markdown("---")

            # Grafico top circoli
            top_n = min(15, len(circoli))
            top_circoli = circoli.head(top_n)

            fig_circoli = px.bar(
                top_circoli, x='Tesserati', y='Circolo',
                orientation='h',
                title=f"Top {top_n} Circoli Puglia per Tesserati",
                color='GareMedia',
                color_continuous_scale='Blues'
            )
            fig_circoli.update_layout(height=500, yaxis={'categoryorder': 'total ascending'})
            st.plotly_chart(fig_circoli, use_container_width=True)

            # Tabella completa
            st.markdown("### Tabella Completa")
            st.dataframe(
                circoli.round(1),
                use_container_width=True,
                column_config={
                    'Circolo': 'Associazione',
                    'Tesserati': st.column_config.NumberColumn('Tesserati', format='%d'),
                    'GareMedia': st.column_config.NumberColumn('Gare Media', format='%.1f'),
                    'PuntiMedi': st.column_config.NumberColumn('Punti Medi', format='%.0f'),
                    'AllieviSB': st.column_config.NumberColumn('Allievi SB', format='%d'),
                    'QuotaSB': st.column_config.NumberColumn('% SB', format='%.1f%%')
                }
            )

            # Analisi conversione per circolo (se abbiamo i dati)
            if len(df_conv) > 0:
                st.markdown("---")
                st.markdown("### Conversione per Circolo")

                # Aggiungi associazione al df conversione
                assoc_map = df_puglia[df_puglia['MbtDesc'] == 'Scuola Bridge'].groupby('MmbCode')[col_assoc].first().to_dict()
                df_conv['Circolo'] = df_conv['MmbCode'].map(assoc_map)

                conv_circolo = df_conv.groupby('Circolo').agg({
                    'MmbCode': 'count',
                    'Convertito': ['sum', 'mean']
                }).reset_index()
                conv_circolo.columns = ['Circolo', 'Allievi', 'Convertiti', 'TassoConv']
                conv_circolo['TassoConv'] = (conv_circolo['TassoConv'] * 100).round(1)
                conv_circolo = conv_circolo[conv_circolo['Allievi'] >= 3]  # Min 3 allievi
                conv_circolo = conv_circolo.sort_values('TassoConv', ascending=False)

                if len(conv_circolo) > 0:
                    fig_conv_circ = px.bar(
                        conv_circolo.head(15), x='TassoConv', y='Circolo',
                        orientation='h',
                        title="Top Circoli per Tasso di Conversione",
                        text='TassoConv',
                        color='TassoConv',
                        color_continuous_scale='RdYlGn'
                    )
                    fig_conv_circ.update_traces(texttemplate='%{text:.0f}%', textposition='outside', cliponaxis=False)
                    fig_conv_circ.update_layout(height=450, yaxis={'categoryorder': 'total ascending'})
                    st.plotly_chart(fig_conv_circ, use_container_width=True)

        # =====================================================================
        # TAB 5: CONFRONTO NAZIONALE
        # =====================================================================
        with tab5:
            st.subheader("📈 Confronto Puglia vs Nazionale")

            # Calcola metriche nazionali per 2022-2025
            df_naz = df[df['Anno'].isin(ANNI_PUGLIA)]

            naz_tesserati = df_naz['MmbCode'].nunique()
            pug_tesserati = df_puglia['MmbCode'].nunique()
            quota_nazionale = (pug_tesserati / naz_tesserati * 100) if naz_tesserati > 0 else 0

            naz_gare = df_naz['GareGiocate'].mean()
            pug_gare = df_puglia['GareGiocate'].mean()

            naz_eta = df_naz['Anni'].mean() if 'Anni' in df_naz.columns else 0
            pug_eta = df_puglia['Anni'].mean() if 'Anni' in df_puglia.columns else 0

            # Scuola Bridge nazionale
            naz_sb = df_naz[df_naz['MbtDesc'] == 'Scuola Bridge']['MmbCode'].nunique()
            pug_sb = df_puglia[df_puglia['MbtDesc'] == 'Scuola Bridge']['MmbCode'].nunique()

            # Tabella confronto
            confronto_data = pd.DataFrame({
                'Metrica': ['Tesserati Unici', 'Gare Medie', 'Età Media', 'Allievi Scuola Bridge'],
                'Italia': [f"{naz_tesserati:,}", f"{naz_gare:.1f}", f"{naz_eta:.1f}", f"{naz_sb:,}"],
                'Puglia': [f"{pug_tesserati:,}", f"{pug_gare:.1f}", f"{pug_eta:.1f}", f"{pug_sb:,}"],
                'Differenza': [
                    f"{quota_nazionale:.2f}% del totale",
                    f"{pug_gare - naz_gare:+.1f}",
                    f"{pug_eta - naz_eta:+.1f} anni",
                    f"{pug_sb / naz_sb * 100:.1f}% del totale" if naz_sb > 0 else "N/A"
                ]
            })

            st.dataframe(confronto_data, use_container_width=True, hide_index=True)

            st.markdown("---")

            # Confronto trend
            st.markdown("### Trend Comparativo")

            trend_naz = df_naz.groupby('Anno')['MmbCode'].nunique().reset_index()
            trend_naz.columns = ['Anno', 'Italia']

            trend_pug = df_puglia.groupby('Anno')['MmbCode'].nunique().reset_index()
            trend_pug.columns = ['Anno', 'Puglia']

            # Normalizza per confronto (base 100 = 2022)
            trend_merged = trend_naz.merge(trend_pug, on='Anno')

            base_naz = trend_merged[trend_merged['Anno'] == 2022]['Italia'].values
            base_pug = trend_merged[trend_merged['Anno'] == 2022]['Puglia'].values

            if len(base_naz) > 0 and base_naz[0] > 0:
                trend_merged['Italia_idx'] = (trend_merged['Italia'] / base_naz[0] * 100).round(1)
            else:
                trend_merged['Italia_idx'] = 100

            if len(base_pug) > 0 and base_pug[0] > 0:
                trend_merged['Puglia_idx'] = (trend_merged['Puglia'] / base_pug[0] * 100).round(1)
            else:
                trend_merged['Puglia_idx'] = 100

            fig_confronto = go.Figure()

            fig_confronto.add_trace(go.Scatter(
                x=trend_merged['Anno'], y=trend_merged['Italia_idx'],
                mode='lines+markers', name='Italia',
                line=dict(color='#64748b', width=3),
                marker=dict(size=10)
            ))

            fig_confronto.add_trace(go.Scatter(
                x=trend_merged['Anno'], y=trend_merged['Puglia_idx'],
                mode='lines+markers', name='Puglia',
                line=dict(color='#3b82f6', width=3),
                marker=dict(size=10)
            ))

            fig_confronto.add_hline(y=100, line_dash="dash", line_color="gray",
                                    annotation_text="Base 2022 = 100")

            fig_confronto.update_layout(
                title="Trend Normalizzato (Base 2022 = 100)",
                xaxis_title="Anno",
                yaxis_title="Indice (2022 = 100)",
                height=400,
                legend=dict(orientation='h', yanchor='bottom', y=1.02)
            )
            st.plotly_chart(fig_confronto, use_container_width=True)

            # Posizionamento tra regioni del Sud
            st.markdown("---")
            st.markdown("### Posizionamento nel Sud Italia")

            REGIONI_SUD = ['ABR', 'MOL', 'CAM', 'PUG', 'BAS', 'CAB', 'SIC', 'SAR']
            df_sud = df_naz[df_naz['GrpArea'].isin(REGIONI_SUD)]

            ranking_sud = df_sud.groupby('GrpArea').agg({
                'MmbCode': 'nunique',
                'GareGiocate': 'mean'
            }).reset_index()
            ranking_sud.columns = ['Regione', 'Tesserati', 'GareMedia']
            ranking_sud['NomeRegione'] = ranking_sud['Regione'].map(NOMI_REGIONI_COMPLETI)
            ranking_sud = ranking_sud.sort_values('Tesserati', ascending=False)
            ranking_sud['Posizione'] = range(1, len(ranking_sud) + 1)

            # Evidenzia Puglia
            ranking_sud['Colore'] = ranking_sud['Regione'].apply(
                lambda x: '#3b82f6' if x == 'PUG' else '#94a3b8'
            )

            fig_ranking = px.bar(
                ranking_sud, x='Tesserati', y='NomeRegione',
                orientation='h',
                title="Classifica Regioni Sud + Isole per Tesserati",
                color='Colore',
                color_discrete_map='identity'
            )
            fig_ranking.update_layout(
                height=400,
                showlegend=False,
                yaxis={'categoryorder': 'total ascending'}
            )
            st.plotly_chart(fig_ranking, use_container_width=True)

            # Posizione Puglia
            pos_puglia = ranking_sud[ranking_sud['Regione'] == 'PUG']['Posizione'].values
            if len(pos_puglia) > 0:
                st.info(f"📍 La Puglia è al **{pos_puglia[0]}° posto** tra le regioni del Sud + Isole per numero di tesserati.")

# ============================================================================
# PAGINA: GIOCATORI A RISCHIO
# ============================================================================
elif pagina == "⚠️ Giocatori a Rischio":
    st.title("⚠️ Giocatori a Rischio")

    if 'rischio' in data:
        rischio_df = data['rischio']

        # Metriche
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Totale a Rischio", f"{len(rischio_df):,}")
        with col2:
            n_critico = len(rischio_df[rischio_df['Rischio'] == 'CRITICO'])
            st.metric("Critici", f"{n_critico:,}")
        with col3:
            n_urgente = len(rischio_df[rischio_df['Priorita'] == '1-URGENTE'])
            st.metric("Urgenti", f"{n_urgente:,}")
        with col4:
            eta_media = rischio_df['Eta'].mean()
            st.metric("Età Media", f"{eta_media:.1f}")

        st.markdown("---")

        # Filtri specifici
        col1, col2, col3 = st.columns(3)

        with col1:
            priorita_filter = st.multiselect(
                "Priorità",
                rischio_df['Priorita'].unique(),
                default=['1-URGENTE', '2-ALTA']
            )

        with col2:
            rischio_filter = st.multiselect(
                "Livello Rischio",
                rischio_df['Rischio'].unique(),
                default=rischio_df['Rischio'].unique()
            )

        with col3:
            eta_rischio = st.slider(
                "Età",
                int(rischio_df['Eta'].min()),
                int(rischio_df['Eta'].max()),
                (10, 40)
            )

        # Applica filtri
        rischio_filtered = rischio_df[
            (rischio_df['Priorita'].isin(priorita_filter)) &
            (rischio_df['Rischio'].isin(rischio_filter)) &
            (rischio_df['Eta'] >= eta_rischio[0]) &
            (rischio_df['Eta'] <= eta_rischio[1])
        ]

        st.markdown(f"**Giocatori filtrati: {len(rischio_filtered):,}**")

        # Grafici
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Distribuzione per Priorità")
            prio_dist = rischio_filtered['Priorita'].value_counts()
            fig = px.pie(values=prio_dist.values, names=prio_dist.index,
                        color_discrete_sequence=['#DC3545', '#FD7E14', '#FFC107', '#28A745'])
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.subheader("Distribuzione per Età")
            fig = px.histogram(rischio_filtered, x='Eta', nbins=20,
                              color='Rischio', color_discrete_map={
                                  'CRITICO': '#DC3545', 'ALTO': '#FD7E14'
                              })
            st.plotly_chart(fig, use_container_width=True)

        # Tabella giocatori
        st.subheader("📋 Lista Giocatori a Rischio")

        # Selezione colonne
        cols_show = ['Priorita', 'Nome', 'Eta', 'Rischio', 'GareMedie', 'Associazione', 'Regione', 'Motivi']
        cols_available = [c for c in cols_show if c in rischio_filtered.columns]

        st.dataframe(
            rischio_filtered[cols_available].head(100),
            use_container_width=True,
            height=400
        )

        # Download
        csv = rischio_filtered.to_csv(index=False)
        st.download_button(
            "📥 Scarica Lista Completa (CSV)",
            csv,
            "giocatori_rischio.csv",
            "text/csv"
        )
    else:
        st.warning("Dati rischio non disponibili. Esegui prima analisi_rischio_v2.py")

# ============================================================================
# PAGINA: BRIDGISTI RECUPERABILI
# ============================================================================
elif pagina == "🔄 Bridgisti Recuperabili":
    st.title("🔄 Bridgisti Recuperabili")
    st.markdown("""
    Modello predittivo multi-fattoriale per identificare i bridgisti che hanno abbandonato
    e sono **più facilmente recuperabili**, considerando rischio salute/età.
    """)

    # Carica dati recuperabilità
    RESULTS_REC = OUTPUT_DIR / 'results_recuperabilita'

    if not RESULTS_REC.exists():
        st.error("⚠️ Dati non trovati. Esegui prima `python 04_modello_recuperabilita.py`")
    else:
        # Carica dati
        df_rec = pd.read_csv(RESULTS_REC / 'bridgisti_recuperabili_completo.csv')
        df_prov_rec = pd.read_csv(RESULTS_REC / 'recuperabili_per_provincia.csv')
        df_reg_rec = pd.read_csv(RESULTS_REC / 'recuperabili_per_regione.csv')

        with open(RESULTS_REC / 'summary_recuperabilita.json', 'r') as f:
            summary_rec = json.load(f)

        # === METRICHE PRINCIPALI ===
        col1, col2, col3, col4, col5 = st.columns(5)

        with col1:
            st.metric("Totale Churned", f"{summary_rec['totale_churned']:,}")
        with col2:
            urgenti = summary_rec['urgenti']
            st.metric("🔴 Urgenti", f"{urgenti:,}",
                     delta=f"{urgenti/summary_rec['totale_churned']*100:.1f}%")
        with col3:
            alta = summary_rec['alta_priorita']
            st.metric("🟠 Alta Priorità", f"{alta:,}",
                     delta=f"{alta/summary_rec['totale_churned']*100:.1f}%")
        with col4:
            st.metric("Score Medio", f"{summary_rec['score_medio']:.1f}/100")
        with col5:
            st.metric("Età Media", f"{summary_rec['eta_media']:.1f} anni")

        st.markdown("---")

        # === TAB LAYOUT ===
        tab1, tab2, tab3, tab4 = st.tabs(["📋 Lista Recuperabili", "🗺️ Mappa", "📊 Analisi", "📈 Dettaglio Score"])

        # ========== TAB 1: LISTA ==========
        with tab1:
            st.subheader("📋 Lista Bridgisti Recuperabili")

            # Filtri
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                priorita_filter = st.multiselect(
                    "Priorità",
                    df_rec['Priorita'].unique(),
                    default=['1-URGENTE', '2-ALTA']
                )

            with col2:
                eta_range_rec = st.slider(
                    "Età attuale",
                    int(df_rec['EtaAttuale'].min()),
                    int(df_rec['EtaAttuale'].max()),
                    (20, 80)
                )

            with col3:
                score_min = st.slider("Score minimo", 0, 100, 40)

            with col4:
                anni_assenza = st.slider("Max anni assenza", 1, 8, 5)

            # Applica filtri
            df_filtered_rec = df_rec[
                (df_rec['Priorita'].isin(priorita_filter)) &
                (df_rec['EtaAttuale'] >= eta_range_rec[0]) &
                (df_rec['EtaAttuale'] <= eta_range_rec[1]) &
                (df_rec['RecoverabilityScore'] >= score_min) &
                (df_rec['AnniDaChurn'] <= anni_assenza)
            ]

            st.markdown(f"**Risultati: {len(df_filtered_rec):,} bridgisti**")

            # Tabella
            cols_display = ['Nome', 'Priorita', 'RecoverabilityScore', 'EtaAttuale',
                           'Citta', 'Regione', 'GareMedie', 'AnniDaChurn',
                           'RischioMorte', 'RischioMalattia']
            cols_available = [c for c in cols_display if c in df_filtered_rec.columns]

            st.dataframe(
                df_filtered_rec[cols_available].head(500)
                .rename(columns={
                    'RecoverabilityScore': 'Score',
                    'EtaAttuale': 'Età',
                    'GareMedie': 'Gare/Anno',
                    'AnniDaChurn': 'Anni Assente',
                    'RischioMorte': 'Rischio Morte %',
                    'RischioMalattia': 'Rischio Malattia %'
                })
                .style.background_gradient(subset=['Score'], cmap='RdYlGn')
                .format({
                    'Score': '{:.1f}',
                    'Gare/Anno': '{:.1f}',
                    'Rischio Morte %': '{:.1f}',
                    'Rischio Malattia %': '{:.1f}'
                }),
                use_container_width=True,
                height=500
            )

            # Download
            csv_rec = df_filtered_rec[cols_available].to_csv(index=False)
            st.download_button(
                "📥 Scarica Lista Filtrata (CSV)",
                csv_rec,
                "bridgisti_recuperabili.csv",
                "text/csv"
            )

        # ========== TAB 2: MAPPA ==========
        with tab2:
            st.subheader("🗺️ Mappa Bridgisti Recuperabili")

            # Coordinate regioni
            COORD_REGIONI_REC = {
                'PIE': (45.0522, 7.5155), 'VDA': (45.7370, 7.3205),
                'LOM': (45.4791, 9.8452), 'TRT': (46.0679, 11.1211),
                'TRB': (46.7, 11.35), 'VEN': (45.4414, 12.3155),
                'FRI': (46.0711, 13.2346), 'LIG': (44.4112, 8.9327),
                'EMI': (44.4949, 11.3426), 'TOS': (43.7711, 11.2486),
                'UMB': (42.9384, 12.6218), 'MAR': (43.6168, 13.5188),
                'LAZ': (41.8931, 12.4831), 'ABR': (42.1920, 13.7289),
                'MOL': (41.6738, 14.7520), 'CAM': (40.8394, 14.2528),
                'PUG': (41.1259, 16.8670), 'BAS': (40.6396, 15.8056),
                'CAB': (38.9060, 16.5943), 'SIC': (37.5994, 14.0154),
                'SAR': (40.1209, 9.0129)
            }

            # Aggiungi coordinate
            df_reg_rec['lat'] = df_reg_rec['Regione'].map(lambda x: COORD_REGIONI_REC.get(x, (0,0))[0])
            df_reg_rec['lon'] = df_reg_rec['Regione'].map(lambda x: COORD_REGIONI_REC.get(x, (0,0))[1])

            col1, col2 = st.columns([3, 1])

            with col1:
                # Selezione metrica
                metrica_mappa_rec = st.radio(
                    "Visualizza:",
                    ["Numero Recuperabili", "Alta Priorità", "Score Medio"],
                    horizontal=True
                )

                if metrica_mappa_rec == "Numero Recuperabili":
                    size_col = 'NumRecuperabili'
                    color_col = 'NumRecuperabili'
                    title = "Bridgisti Recuperabili per Regione"
                elif metrica_mappa_rec == "Alta Priorità":
                    size_col = 'AltaPriorita'
                    color_col = 'AltaPriorita'
                    title = "Bridgisti Alta Priorità per Regione"
                else:
                    size_col = 'ScoreMedio'
                    color_col = 'ScoreMedio'
                    title = "Score Medio Recuperabilità per Regione"

                fig = px.scatter_geo(
                    df_reg_rec,
                    lat='lat', lon='lon',
                    size=size_col, color=color_col,
                    hover_name='Regione',
                    hover_data={
                        'NumRecuperabili': True,
                        'AltaPriorita': True,
                        'ScoreMedio': ':.1f',
                        'EtaMedia': ':.1f',
                        'RischioSaluteMedio': ':.1f',
                        'lat': False, 'lon': False
                    },
                    color_continuous_scale='YlOrRd',
                    size_max=50,
                    title=title
                )

                fig.update_geos(
                    scope='europe',
                    center=dict(lat=42.5, lon=12.5),
                    projection_scale=6,
                    showland=True,
                    landcolor='rgb(243, 243, 243)',
                    countrycolor='rgb(204, 204, 204)',
                    showcoastlines=True
                )
                fig.update_layout(height=550, margin=dict(l=0, r=0, t=40, b=0))
                st.plotly_chart(fig, use_container_width=True)

            with col2:
                st.markdown("**🎯 Top Regioni**")
                for _, row in df_reg_rec.nlargest(5, 'AltaPriorita').iterrows():
                    st.markdown(f"**{row['Regione']}**: {row['AltaPriorita']:.0f} alta priorità")

                st.markdown("---")
                st.markdown("**📊 Totali**")
                st.metric("Recuperabili", f"{df_reg_rec['NumRecuperabili'].sum():,}")
                st.metric("Alta Priorità", f"{df_reg_rec['AltaPriorita'].sum():.0f}")

            # Dettaglio province
            st.markdown("---")
            st.subheader("📍 Dettaglio per Provincia")

            # Top 20 province
            top_prov = df_prov_rec.nlargest(20, 'NumRecuperabili')

            col1, col2 = st.columns(2)

            with col1:
                st.markdown("##### Top 20 Province per Numero Recuperabili")
                fig = px.bar(
                    top_prov.sort_values('NumRecuperabili', ascending=True),
                    x='NumRecuperabili', y='Provincia', orientation='h',
                    color='ScoreMedio', color_continuous_scale='RdYlGn'
                )
                fig.update_layout(height=500)
                st.plotly_chart(fig, use_container_width=True)

            with col2:
                st.markdown("##### Tabella Province")
                st.dataframe(
                    df_prov_rec[['Provincia', 'NumRecuperabili', 'ScoreMedio', 'EtaMedia', 'RischioSaluteMedio']]
                    .sort_values('NumRecuperabili', ascending=False)
                    .head(30)
                    .style.background_gradient(subset=['NumRecuperabili'], cmap='Blues')
                    .format({
                        'ScoreMedio': '{:.1f}',
                        'EtaMedia': '{:.1f}',
                        'RischioSaluteMedio': '{:.1f}'
                    }),
                    use_container_width=True,
                    height=450
                )

        # ========== TAB 3: ANALISI ==========
        with tab3:
            st.subheader("📊 Analisi Recuperabilità")

            col1, col2 = st.columns(2)

            with col1:
                st.markdown("##### Distribuzione per Priorità")
                prio_counts = df_rec['Priorita'].value_counts().sort_index()
                colors_prio = {
                    '1-URGENTE': '#d62728',
                    '2-ALTA': '#ff7f0e',
                    '3-MEDIA': '#2ca02c',
                    '4-BASSA': '#1f77b4',
                    '4-DIFFICILE': '#7f7f7f',
                    '5-NON_RECUPERABILE': '#bcbd22'
                }
                fig = px.pie(
                    values=prio_counts.values,
                    names=prio_counts.index,
                    color=prio_counts.index,
                    color_discrete_map=colors_prio
                )
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)

            with col2:
                st.markdown("##### Score vs Età")
                # Sample per performance
                sample_size = min(2000, len(df_rec))
                df_sample = df_rec.sample(sample_size)
                fig = px.scatter(
                    df_sample,
                    x='EtaAttuale', y='RecoverabilityScore',
                    color='Priorita',
                    color_discrete_map=colors_prio,
                    opacity=0.6,
                    title="Score Recuperabilità vs Età"
                )
                fig.add_hline(y=50, line_dash="dash", line_color="orange",
                             annotation_text="Soglia Alta Priorità")
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)

            # Rischio salute per età
            st.markdown("---")
            st.markdown("##### Rischio Salute per Fascia d'Età")

            df_rec['FasciaEtaRec'] = pd.cut(
                df_rec['EtaAttuale'],
                bins=[0, 50, 60, 70, 75, 80, 85, 90, 120],
                labels=['<50', '50-60', '60-70', '70-75', '75-80', '80-85', '85-90', '90+']
            )

            rischio_eta = df_rec.groupby('FasciaEtaRec').agg({
                'MmbCode': 'count',
                'RischioMorte': 'mean',
                'RischioMalattia': 'mean',
                'RecoverabilityScore': 'mean'
            }).reset_index()
            rischio_eta.columns = ['Fascia Età', 'N Giocatori', 'Rischio Morte %',
                                  'Rischio Malattia %', 'Score Medio']

            col1, col2 = st.columns(2)

            with col1:
                fig = px.bar(
                    rischio_eta,
                    x='Fascia Età', y=['Rischio Morte %', 'Rischio Malattia %'],
                    barmode='group',
                    title="Rischio Salute per Età",
                    color_discrete_sequence=['#d62728', '#ff7f0e']
                )
                fig.update_layout(height=350)
                st.plotly_chart(fig, use_container_width=True)

            with col2:
                fig = px.bar(
                    rischio_eta,
                    x='Fascia Età', y='N Giocatori',
                    color='Score Medio',
                    color_continuous_scale='RdYlGn',
                    title="Distribuzione Churned per Età"
                )
                fig.update_layout(height=350)
                st.plotly_chart(fig, use_container_width=True)

            # Tabella riepilogativa
            st.markdown("---")
            st.dataframe(
                rischio_eta.style.background_gradient(subset=['Rischio Morte %'], cmap='Reds')
                .background_gradient(subset=['Score Medio'], cmap='Greens')
                .format({
                    'Rischio Morte %': '{:.1f}',
                    'Rischio Malattia %': '{:.1f}',
                    'Score Medio': '{:.1f}'
                }),
                use_container_width=True
            )

        # ========== TAB 4: DETTAGLIO SCORE ==========
        with tab4:
            st.subheader("📈 Componenti dello Score di Recuperabilità")

            st.markdown("""
            Il **RecoverabilityScore** (0-100) è calcolato combinando:
            - **Engagement Score** (25%): Gare giocate, punti, agonismo
            - **Loyalty Score** (20%): Anni di presenza, progressione categoria
            - **Recency Score** (20%): Quanto recente è l'abbandono
            - **Geographic Score** (10%): Retention storica della zona
            - **Social Score** (10%): Connessioni nel circolo
            - **Health Penalty** (15%): Rischio mortalità/malattia per età
            """)

            # Medie componenti per priorità
            st.markdown("##### Media Componenti per Priorità")

            components = ['EngagementScore', 'LoyaltyScore', 'RecencyScore',
                         'GeographicScore', 'SocialScore', 'HealthPenalty']
            components_available = [c for c in components if c in df_rec.columns]

            if components_available:
                comp_by_prio = df_rec.groupby('Priorita')[components_available].mean().reset_index()

                fig = px.bar(
                    comp_by_prio.melt(id_vars='Priorita', var_name='Componente', value_name='Valore'),
                    x='Priorita', y='Valore', color='Componente',
                    barmode='group',
                    title="Confronto Componenti Score per Priorità"
                )
                fig.update_layout(height=450)
                st.plotly_chart(fig, use_container_width=True)

            # Correlazioni
            st.markdown("---")
            st.markdown("##### Correlazione tra Componenti")

            if len(components_available) > 1:
                corr_matrix = df_rec[components_available + ['RecoverabilityScore']].corr()
                fig = px.imshow(
                    corr_matrix,
                    text_auto='.2f',
                    color_continuous_scale='RdBu_r',
                    title="Matrice Correlazioni"
                )
                fig.update_layout(height=450)
                st.plotly_chart(fig, use_container_width=True)

# ============================================================================
# PAGINA: MODELLO PREDITTIVO
# ============================================================================
elif pagina == "🔮 Modello Predittivo":
    st.title("🔮 Modello Predittivo 2025-2035")

    if 'proiezioni' in data:
        proiezioni = data['proiezioni']
        rischi_pred = data['rischi_pred']

        # Metriche
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric(
                "Tesserati 2025",
                f"{rischi_pred['tesserati_2025']:,}"
            )
        with col2:
            st.metric(
                "Tesserati 2035",
                f"{rischi_pred['tesserati_2035']:,}",
                delta=f"{rischi_pred['variazione_2025_2035']:+.1f}%"
            )
        with col3:
            st.metric(
                "Età Media 2035",
                f"{rischi_pred['eta_media_2035']:.1f}"
            )
        with col4:
            st.metric(
                "Reclutamento/anno",
                f"{rischi_pred['reclutamento_breakeven']:,}",
                delta="necessario"
            )

        st.markdown("---")

        # Grafico proiezioni
        st.subheader("📈 Proiezione Tesserati")

        fig = go.Figure()

        # Area range
        fig.add_trace(go.Scatter(
            x=proiezioni['Anno'],
            y=proiezioni['Tesserati'] * 1.1,
            mode='lines',
            line=dict(width=0),
            showlegend=False
        ))
        fig.add_trace(go.Scatter(
            x=proiezioni['Anno'],
            y=proiezioni['Tesserati'] * 0.9,
            mode='lines',
            fill='tonexty',
            fillcolor='rgba(74, 144, 217, 0.2)',
            line=dict(width=0),
            name='Range scenari'
        ))

        # Linea principale
        fig.add_trace(go.Scatter(
            x=proiezioni['Anno'],
            y=proiezioni['Tesserati'],
            mode='lines+markers',
            name='Scenario base',
            line=dict(color='#1E3A5F', width=3)
        ))

        fig.update_layout(height=400, xaxis_title="Anno", yaxis_title="Tesserati")
        fig.update_xaxes(dtick=1)
        st.plotly_chart(fig, use_container_width=True)

        # Evoluzione età
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("👴 Evoluzione Età Media")
            fig = px.line(proiezioni, x='Anno', y='EtaMedia', markers=True)
            fig.add_hline(y=70, line_dash="dash", line_color="red",
                         annotation_text="Soglia critica")
            fig.update_xaxes(dtick=1)
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.subheader("📊 Nuovi vs Usciti per Anno")
            fig = go.Figure()
            fig.add_trace(go.Bar(x=proiezioni['Anno'], y=proiezioni['Nuovi'],
                                name='Nuovi', marker_color='#28A745'))
            fig.add_trace(go.Bar(x=proiezioni['Anno'], y=proiezioni['Usciti'],
                                name='Usciti', marker_color='#DC3545'))
            fig.update_layout(barmode='group')
            fig.update_xaxes(dtick=1)
            st.plotly_chart(fig, use_container_width=True)

        # Scenario simulator
        st.markdown("---")
        st.subheader("🎮 Simulatore Scenari")

        col1, col2 = st.columns(2)

        with col1:
            nuovi_anno = st.slider(
                "Nuovi tesserati/anno",
                500, 3000, 1500, 100
            )

        with col2:
            riduzione_churn = st.slider(
                "Riduzione churn (%)",
                0, 50, 0, 5
            )

        # Calcolo scenario
        base_2025 = rischi_pred['tesserati_2025']
        tasso_uscita = 0.12 * (1 - riduzione_churn/100)

        anni = list(range(2025, 2036))
        tesserati_sim = [base_2025]
        for _ in range(10):
            nuovo = tesserati_sim[-1] * (1 - tasso_uscita) + nuovi_anno
            tesserati_sim.append(int(nuovo))

        fig = px.line(x=anni, y=tesserati_sim, markers=True,
                     title=f"Scenario: {nuovi_anno} nuovi/anno, -{riduzione_churn}% churn")
        fig.add_hline(y=base_2025, line_dash="dash",
                     annotation_text=f"Livello 2025: {base_2025:,}")
        st.plotly_chart(fig, use_container_width=True)

        variazione = (tesserati_sim[-1] - base_2025) / base_2025 * 100
        if variazione > 0:
            st.success(f"✅ Con questi parametri: **+{variazione:.1f}%** tesserati nel 2035 ({tesserati_sim[-1]:,})")
        else:
            st.error(f"⚠️ Con questi parametri: **{variazione:.1f}%** tesserati nel 2035 ({tesserati_sim[-1]:,})")

    else:
        st.warning("Dati predittivi non disponibili. Esegui prima modello_predittivo.py")

# ============================================================================
# PAGINA: OPPORTUNITA' CRESCITA
# ============================================================================
elif pagina == "🌱 Opportunità Crescita":
    st.title("🌱 Opportunità di Crescita")

    st.markdown("""
    Analisi delle opportunità per aumentare il numero di bridgisti,
    categorizzate per facilità di "attacco".
    """)

    RESULTS_OPP = OUTPUT_DIR / 'results_opportunita'

    if RESULTS_OPP.exists():
        # Carica dati
        with open(RESULTS_OPP / 'summary_opportunita.json', 'r') as f:
            summary_opp = json.load(f)

        quasi_agganciati = pd.read_csv(RESULTS_OPP / 'quasi_agganciati.csv')
        dormienti = pd.read_csv(RESULTS_OPP / 'dormienti.csv')
        gap_demo = pd.read_csv(RESULTS_OPP / 'gap_demografico.csv')
        opp_geo = pd.read_csv(RESULTS_OPP / 'opportunita_geografiche.csv')
        persi_covid = pd.read_csv(RESULTS_OPP / 'persi_covid.csv')

        # Carica deceduti e filtra dalle liste da ricontattare
        deceduti_file = BASE_DIR / 'Deceduti.xlsx'
        deceduti_codes = set()
        n_deceduti_qa = 0
        n_deceduti_covid = 0

        if deceduti_file.exists():
            deceduti_df = pd.read_excel(deceduti_file)
            deceduti_codes = set(deceduti_df['MmbCode'].str.strip())

            # Filtra quasi_agganciati
            n_deceduti_qa = quasi_agganciati['MmbCode'].str.strip().isin(deceduti_codes).sum()
            quasi_agganciati = quasi_agganciati[~quasi_agganciati['MmbCode'].str.strip().isin(deceduti_codes)]

            # Filtra persi_covid
            n_deceduti_covid = persi_covid['MmbCode'].str.strip().isin(deceduti_codes).sum()
            persi_covid = persi_covid[~persi_covid['MmbCode'].str.strip().isin(deceduti_codes)]

        # Overview KPI
        st.markdown("### 📊 Riepilogo Opportunità")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric(
                "Quasi Agganciati",
                f"{len(quasi_agganciati):,}",
                help="Hanno provato 1-2 anni, poche gare, poi spariti (filtrati deceduti)"
            )
        with col2:
            st.metric(
                "Dormienti",
                f"{len(dormienti):,}",
                help="Tesserati attivi che non giocano gare"
            )
        with col3:
            st.metric(
                "Gap 60-70 anni",
                f"{summary_opp['gap_60_70']['gap']:,}",
                help="Bridgisti potenziali nella fascia 60-70"
            )
        with col4:
            st.metric(
                "Persi COVID",
                f"{len(persi_covid):,}",
                help="Non tornati dopo il 2020 (filtrati deceduti)"
            )

        # Nota discreta sui filtrati
        if n_deceduti_qa > 0 or n_deceduti_covid > 0:
            st.caption(f"ℹ️ Liste nettificate: esclusi {n_deceduti_qa + n_deceduti_covid} nominativi non più ricontattabili")

        st.markdown("---")

        # Tabs per sezioni
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "🎯 Quasi Agganciati",
            "😴 Dormienti",
            "📊 Gap Demografico",
            "🗺️ Opportunità Geo",
            "😷 Effetto COVID"
        ])

        # TAB 1: Quasi Agganciati
        with tab1:
            st.subheader("🎯 Quasi Agganciati")
            st.markdown("""
            **Chi sono:** Persone che hanno fatto 1-2 anni di tessera, giocato poche gare,
            e poi sono sparite. Hanno "assaggiato" il bridge ma non si sono agganciati.

            **Perché sono un'opportunità:** Conoscono già il gioco, potrebbero essere
            ricontattati con offerte mirate.
            """)

            if len(quasi_agganciati) > 0:
                col1, col2 = st.columns(2)

                with col1:
                    # Per regione
                    qa_reg = quasi_agganciati.groupby('Regione').agg({
                        'MmbCode': 'count',
                        'GareTotali': 'mean',
                        'Eta': 'mean'
                    }).reset_index()
                    qa_reg.columns = ['Regione', 'Numero', 'GareMedie', 'EtàMedia']
                    qa_reg = qa_reg.sort_values('Numero', ascending=True).tail(15)

                    fig = px.bar(qa_reg, y='Regione', x='Numero', orientation='h',
                                title="Top 15 Regioni con Quasi Agganciati",
                                text='Numero')
                    fig.update_traces(textposition='auto', cliponaxis=False)
                    fig.update_layout(margin=dict(r=60))
                    st.plotly_chart(fig, use_container_width=True)

                with col2:
                    # Per anno di abbandono
                    qa_anno = quasi_agganciati.groupby('AnnoFine').size().reset_index(name='Numero')
                    fig = px.bar(qa_anno, x='AnnoFine', y='Numero',
                                title="Quando hanno abbandonato",
                                text='Numero')
                    fig.update_traces(textposition='auto', cliponaxis=False)
                    fig.update_xaxes(dtick=1)
                    st.plotly_chart(fig, use_container_width=True)

                # Profilo
                st.markdown("#### Profilo Tipo")
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Età Media", f"{quasi_agganciati['Eta'].mean():.0f} anni")
                with col2:
                    st.metric("Gare Totali Medie", f"{quasi_agganciati['GareTotali'].mean():.1f}")
                with col3:
                    st.metric("Anni Assenza Media", f"{quasi_agganciati['AnniAssenza'].mean():.1f}")

                # Top associazioni
                qa_ass = quasi_agganciati.groupby('Associazione').size().reset_index(name='Numero')
                qa_ass = qa_ass.sort_values('Numero', ascending=False).head(20)

                with st.expander("🏢 Top 20 Associazioni con Quasi Agganciati"):
                    st.dataframe(qa_ass, use_container_width=True)

                # MODELLO PREDITTIVO PRIORITÀ INTERVENTO
                st.markdown("---")
                st.markdown("### 🎯 Priorità Intervento (Modello Predittivo)")
                st.markdown("""
                Il modello calcola uno **Score di Recuperabilità** basato su:
                - **Età** (40%): Under 70 = alta priorità, 70-80 = media, Over 80 = bassa
                - **Engagement** (30%): Gare totali giocate (più gare = più attaccati al gioco)
                - **Recenza** (30%): Anni di assenza (meno anni = più facile recuperare)
                """)

                # Calcolo score predittivo
                qa_priority = quasi_agganciati.copy()

                # Score Età (0-100): più giovane = score più alto
                qa_priority['ScoreEta'] = qa_priority['Eta'].apply(
                    lambda x: 100 if x < 65 else (80 if x < 70 else (60 if x < 75 else (40 if x < 80 else 20)))
                )

                # Score Engagement (0-100): normalizzato su max gare
                max_gare = qa_priority['GareTotali'].max()
                qa_priority['ScoreEngagement'] = (qa_priority['GareTotali'] / max_gare * 100).clip(0, 100)

                # Score Recenza (0-100): meno anni assenza = score più alto
                qa_priority['ScoreRecenza'] = qa_priority['AnniAssenza'].apply(
                    lambda x: 100 if x <= 2 else (80 if x <= 3 else (60 if x <= 4 else (40 if x <= 5 else 20)))
                )

                # Score Totale pesato
                qa_priority['ScoreTotale'] = (
                    qa_priority['ScoreEta'] * 0.4 +
                    qa_priority['ScoreEngagement'] * 0.3 +
                    qa_priority['ScoreRecenza'] * 0.3
                ).round(1)

                # Classificazione priorità
                qa_priority['Priorità'] = qa_priority['ScoreTotale'].apply(
                    lambda x: '🔴 ALTA' if x >= 70 else ('🟡 MEDIA' if x >= 50 else '🟢 BASSA')
                )

                # Ordinamento per score
                qa_priority = qa_priority.sort_values('ScoreTotale', ascending=False)

                # Metriche riepilogo
                col1, col2, col3 = st.columns(3)
                n_alta = len(qa_priority[qa_priority['Priorità'] == '🔴 ALTA'])
                n_media = len(qa_priority[qa_priority['Priorità'] == '🟡 MEDIA'])
                n_bassa = len(qa_priority[qa_priority['Priorità'] == '🟢 BASSA'])

                with col1:
                    st.metric("🔴 Alta Priorità", f"{n_alta:,}", help="Score ≥ 70")
                with col2:
                    st.metric("🟡 Media Priorità", f"{n_media:,}", help="Score 50-69")
                with col3:
                    st.metric("🟢 Bassa Priorità", f"{n_bassa:,}", help="Score < 50")

                # Tabella top priorità
                st.markdown("#### 📋 Top 100 Quasi Agganciati da Ricontattare")

                qa_display = qa_priority[['Nome', 'Associazione', 'Regione', 'Eta', 'GareTotali',
                                          'AnniAssenza', 'ScoreTotale', 'Priorità']].head(100).copy()
                qa_display.columns = ['Nome', 'Associazione', 'Regione', 'Età', 'Gare Totali',
                                      'Anni Assenza', 'Score', 'Priorità']

                st.dataframe(
                    qa_display.style.background_gradient(subset=['Score'], cmap='RdYlGn'),
                    use_container_width=True,
                    height=400
                )

                # Export lista alta priorità
                alta_priorita_qa = qa_priority[qa_priority['Priorità'] == '🔴 ALTA'][
                    ['Nome', 'Associazione', 'Regione', 'Eta', 'GareTotali', 'AnniAssenza', 'ScoreTotale']
                ]

                with st.expander(f"📥 Lista Completa Alta Priorità ({n_alta} persone)"):
                    st.dataframe(alta_priorita_qa, use_container_width=True)

                    # Download button
                    csv_alta = alta_priorita_qa.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        label="⬇️ Scarica CSV Alta Priorità",
                        data=csv_alta,
                        file_name="quasi_agganciati_alta_priorita.csv",
                        mime="text/csv"
                    )

                # Analisi per associazione (priorità aggregate)
                with st.expander("🏢 Priorità per Associazione"):
                    qa_ass_priority = qa_priority.groupby('Associazione').agg({
                        'ScoreTotale': 'mean',
                        'Nome': 'count',
                        'Eta': 'mean',
                        'GareTotali': 'mean'
                    }).reset_index()
                    qa_ass_priority.columns = ['Associazione', 'Score Medio', 'N. Persone', 'Età Media', 'Gare Medie']
                    qa_ass_priority = qa_ass_priority.sort_values('N. Persone', ascending=False).head(30)
                    qa_ass_priority['Score Medio'] = qa_ass_priority['Score Medio'].round(1)
                    qa_ass_priority['Età Media'] = qa_ass_priority['Età Media'].round(0)
                    qa_ass_priority['Gare Medie'] = qa_ass_priority['Gare Medie'].round(1)

                    st.dataframe(
                        qa_ass_priority.style.background_gradient(subset=['Score Medio'], cmap='RdYlGn'),
                        use_container_width=True
                    )
            else:
                st.info("Nessun quasi agganciato identificato")

        # TAB 2: Dormienti
        with tab2:
            st.subheader("😴 Dormienti")
            st.markdown("""
            **Chi sono:** Persone attualmente tesserate che non giocano nessuna gara.

            **Perché sono un'opportunità:** Sono già dentro la federazione!
            Basta attivarli con eventi dedicati.
            """)

            if len(dormienti) > 0:
                col1, col2 = st.columns(2)

                with col1:
                    dorm_cat = dormienti.groupby('MbtDesc').size().reset_index(name='Numero')
                    dorm_cat = dorm_cat.sort_values('Numero', ascending=True)

                    fig = px.bar(dorm_cat, y='MbtDesc', x='Numero', orientation='h',
                                title="Dormienti per Tipo Tessera",
                                text='Numero')
                    fig.update_traces(textposition='auto', cliponaxis=False)
                    fig.update_layout(margin=dict(r=60))
                    st.plotly_chart(fig, use_container_width=True)

                with col2:
                    dorm_reg = dormienti.groupby('Regione').size().reset_index(name='Numero')
                    dorm_reg = dorm_reg.sort_values('Numero', ascending=True).tail(15)

                    fig = px.bar(dorm_reg, y='Regione', x='Numero', orientation='h',
                                title="Top 15 Regioni con Dormienti",
                                text='Numero')
                    fig.update_traces(textposition='auto', cliponaxis=False)
                    fig.update_layout(margin=dict(r=60))
                    st.plotly_chart(fig, use_container_width=True)

                st.metric("Età Media Dormienti", f"{dormienti['Anni'].mean():.0f} anni")
            else:
                st.success("✅ Ottimo! Nessun dormiente nel dataset - tutti i tesserati giocano!")

        # TAB 3: Gap Demografico
        with tab3:
            st.subheader("📊 Gap Demografico")
            st.markdown("""
            **Cos'è:** Confronto tra la penetrazione del bridge nelle diverse fasce d'età
            rispetto alla popolazione italiana.

            **Insight chiave:** La fascia 60-70 anni ha una penetrazione molto più bassa
            della fascia 70-80 (benchmark). C'è un gap di ~3.600 potenziali bridgisti!
            """)

            # Grafico penetrazione
            fig = px.bar(gap_demo, x='FasciaEta', y='Per100k',
                        title="Penetrazione Bridge per 100k abitanti",
                        text='Per100k',
                        color='Per100k',
                        color_continuous_scale='Blues')
            fig.update_traces(textposition='auto', cliponaxis=False, texttemplate='%{text:.1f}')
            st.plotly_chart(fig, use_container_width=True)

            # Focus 60-70
            st.markdown("### 🎯 Focus Fascia 60-70")
            gap_60_70 = gap_demo[gap_demo['FasciaEta'] == '60-70'].iloc[0] if '60-70' in gap_demo['FasciaEta'].values else None

            if gap_60_70 is not None:
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Popolazione", f"{gap_60_70['Popolazione']:,.0f}")
                with col2:
                    st.metric("Bridgisti Attuali", f"{gap_60_70['Bridgisti']:,.0f}")
                with col3:
                    st.metric("Gap vs Benchmark 70-80", f"{gap_60_70['Gap']:,.0f}",
                             help="Se avesse la stessa penetrazione della fascia 70-80")

                st.info(f"""
                💡 **Insight:** La fascia 60-70 ha una penetrazione di {gap_60_70['Per100k']:.1f} per 100k abitanti,
                mentre la fascia 70-80 ha {gap_demo[gap_demo['FasciaEta']=='70-80']['Per100k'].values[0]:.1f} per 100k.

                Se raggiungessimo la stessa penetrazione, avremmo **{gap_60_70['Gap']:,.0f} bridgisti in più**!
                """)

            # Tabella completa
            with st.expander("📋 Dettaglio per fascia d'età"):
                st.dataframe(gap_demo, use_container_width=True)

        # TAB 4: Opportunità Geografiche
        with tab4:
            st.subheader("🗺️ Opportunità Geografiche")
            st.markdown("""
            **Cos'è:** Province con alto potenziale inespresso, calcolato confrontando
            la penetrazione del bridge rispetto alla media nazionale.

            **Come usarlo:** Queste province potrebbero beneficiare di nuove iniziative,
            apertura di circoli, o campagne promozionali.
            """)

            # Top 20 province
            top_province = opp_geo.sort_values('Gap', ascending=False).head(20)

            fig = px.bar(top_province.sort_values('Gap'),
                        y='Provincia', x='Gap', orientation='h',
                        title="Top 20 Province con Maggior Potenziale",
                        text='Gap',
                        color='Per100k',
                        color_continuous_scale='RdYlGn')
            fig.update_traces(textposition='outside', cliponaxis=False, texttemplate='%{text:.0f}')
            fig.update_layout(
                height=600,
                margin=dict(l=150, r=80),
                yaxis=dict(tickfont=dict(size=11))
            )
            st.plotly_chart(fig, use_container_width=True)

            # Dettagli
            col1, col2 = st.columns(2)

            with col1:
                st.markdown("#### Province con 0 bridgisti")
                zero_bridge = opp_geo[opp_geo['Bridgisti'] == 0].sort_values('Popolazione', ascending=False)
                if len(zero_bridge) > 0:
                    st.dataframe(zero_bridge[['Provincia', 'Popolazione']], use_container_width=True)
                else:
                    st.success("Tutte le province hanno almeno un bridgista!")

            with col2:
                st.markdown("#### Province più sotto-penetrate")
                sotto_pen = opp_geo[opp_geo['Bridgisti'] > 0].sort_values('Per100k').head(10)
                st.dataframe(sotto_pen[['Provincia', 'Bridgisti', 'Per100k']], use_container_width=True)

            with st.expander("📋 Tutte le province"):
                st.dataframe(opp_geo.sort_values('Gap', ascending=False), use_container_width=True)

        # TAB 5: Effetto COVID
        with tab5:
            st.subheader("😷 Effetto COVID Persistente")
            st.markdown("""
            **Chi sono:** Bridgisti che erano attivi nel 2019 e non sono mai tornati dopo il COVID.

            **Segmentazione:**
            - **Alta Priorità:** Under 75, molte gare, potrebbero tornare
            - **Media Priorità:** 75-85 anni, discretamente attivi
            - **Difficile:** Over 85 o poche gare storiche
            """)

            if len(persi_covid) > 0:
                col1, col2 = st.columns(2)

                with col1:
                    # Per recuperabilità
                    rec_count = persi_covid['Recuperabile'].value_counts().reset_index()
                    rec_count.columns = ['Categoria', 'Numero']

                    fig = px.pie(rec_count, values='Numero', names='Categoria',
                                title="Segmentazione Recuperabilità",
                                color_discrete_sequence=px.colors.qualitative.Set2)
                    st.plotly_chart(fig, use_container_width=True)

                with col2:
                    # Per regione
                    covid_reg = persi_covid.groupby('Regione').size().reset_index(name='Numero')
                    covid_reg = covid_reg.sort_values('Numero', ascending=True).tail(15)

                    fig = px.bar(covid_reg, y='Regione', x='Numero', orientation='h',
                                title="Top 15 Regioni - Persi COVID",
                                text='Numero')
                    fig.update_traces(textposition='auto', cliponaxis=False)
                    fig.update_layout(margin=dict(r=60))
                    st.plotly_chart(fig, use_container_width=True)

                # Profilo
                st.markdown("#### Profilo Persi COVID")
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Età Media Attuale", f"{persi_covid['Eta'].mean():.0f} anni")
                with col2:
                    gare_medie = persi_covid['GareTotali'].sum() / persi_covid['AnniTotali'].sum() if persi_covid['AnniTotali'].sum() > 0 else 0
                    st.metric("Gare Medie (quando attivi)", f"{gare_medie:.0f}")
                with col3:
                    st.metric("Anni Tessera", f"{persi_covid['AnniTotali'].mean():.1f}")

                # Alta priorità
                alta_priorita = persi_covid[persi_covid['Recuperabile'] == 'Alta Priorità']
                if len(alta_priorita) > 0:
                    st.markdown(f"### 🎯 Alta Priorità: {len(alta_priorita):,} persone")
                    st.markdown("Under 75, molte gare storiche - i più probabili a tornare")

                    with st.expander("📋 Dettaglio Alta Priorità per Associazione"):
                        ap_ass = alta_priorita.groupby('Associazione').agg({
                            'MmbCode': 'count',
                            'GareTotali': 'mean'
                        }).reset_index()
                        ap_ass.columns = ['Associazione', 'Numero', 'GareTotaliMedie']
                        ap_ass = ap_ass.sort_values('Numero', ascending=False).head(30)
                        st.dataframe(ap_ass, use_container_width=True)
            else:
                st.info("Dati COVID non disponibili")

        # Riepilogo finale
        st.markdown("---")
        st.markdown("### 📋 Piano d'Azione Suggerito")

        st.markdown("""
        | Priorità | Target | Azione | Impatto Stimato |
        |----------|--------|--------|-----------------|
        | 🟢 Alta | Dormienti | Eventi dedicati, contatto diretto | Immediato |
        | 🟢 Alta | Quasi Agganciati | Ricontatto, offerte speciali | Medio termine |
        | 🟡 Media | Persi COVID Alta Priorità | Campagna "Torna al Bridge" | Medio termine |
        | 🟡 Media | Gap 60-70 | Marketing mirato, corsi senior | Lungo termine |
        | 🔴 Bassa | Province scoperte | Nuovi circoli, eventi itineranti | Lungo termine |
        """)

    else:
        st.warning("Dati opportunità non disponibili. Esegui prima `08_analisi_opportunita_crescita.py`")

# ============================================================================
# PAGINA: ANALISI AVANZATE
# ============================================================================
elif pagina == "🔬 Analisi Avanzate":
    st.title("🔬 Analisi Avanzate Innovative")

    st.markdown("""
    Analisi comportamentali e predittive per insight strategici.
    """)

    RESULTS_AVZ = OUTPUT_DIR / 'results_avanzate'

    if RESULTS_AVZ.exists():
        # Carica dati
        with open(RESULTS_AVZ / 'summary_avanzate.json', 'r') as f:
            summary_avz = json.load(f)

        curva = pd.read_csv(RESULTS_AVZ / 'curva_apprendimento.csv')
        curva_confronto = pd.read_csv(RESULTS_AVZ / 'curva_confronto_attivi_persi.csv')
        early_warning = pd.read_csv(RESULTS_AVZ / 'early_warning_circoli.csv')
        effetto_maestro = pd.read_csv(RESULTS_AVZ / 'effetto_maestro.csv')
        profilo_migrazione = pd.read_csv(RESULTS_AVZ / 'profilo_migrazione.csv')

        # Overview KPI
        st.markdown("### 📊 Insight Chiave")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric(
                "Soglia Gare Anno 1",
                f"{summary_avz['curva_apprendimento']['gare_anno1_attivi']:.0f}",
                f"vs {summary_avz['curva_apprendimento']['gare_anno1_persi']:.0f} chi abbandona",
                help="Chi resta gioca più gare il primo anno"
            )
        with col2:
            st.metric(
                "Circoli a Rischio",
                f"{summary_avz['early_warning']['circoli_critici'] + summary_avz['early_warning']['circoli_alto_rischio']}",
                help="Critici + Alto rischio"
            )
        with col3:
            st.metric(
                "Effetto Corsi",
                f"+{summary_avz['effetto_maestro']['differenza_pp']:.0f}pp",
                help="Retention con corsi vs senza"
            )
        with col4:
            st.metric(
                "Giocatori Fedeli",
                f"{summary_avz['migrazione']['pct_fedeli']:.0f}%",
                help="1 solo circolo nella carriera"
            )

        st.markdown("---")

        # Tabs
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "📈 Curva Apprendimento",
            "⚠️ Early Warning Circoli",
            "🎓 Effetto Maestro",
            "🔄 Migrazione",
            "👫 Gender Gap"
        ])

        # TAB 1: Curva Apprendimento
        with tab1:
            st.subheader("📈 Curva di Apprendimento")
            st.markdown("""
            Come progrediscono i giocatori nei primi anni di carriera?
            Confronto tra chi resta e chi abbandona.
            """)

            col1, col2 = st.columns(2)

            with col1:
                # Curva gare
                fig = px.line(curva, x='AnnoCarriera', y='GareMedie',
                             title="Gare Medie per Anno di Carriera",
                             markers=True)
                fig.update_layout(xaxis_title="Anno di Carriera", yaxis_title="Gare Medie")
                st.plotly_chart(fig, use_container_width=True)

            with col2:
                # Curva punti
                fig = px.line(curva, x='AnnoCarriera', y='PuntiMedi',
                             title="Punti Medi per Anno di Carriera",
                             markers=True)
                fig.update_layout(xaxis_title="Anno di Carriera", yaxis_title="Punti Medi")
                st.plotly_chart(fig, use_container_width=True)

            # Confronto attivi vs persi
            st.markdown("### 🎯 Confronto: Chi Resta vs Chi Abbandona")

            fig = px.line(curva_confronto, x='AnnoCarriera', y='GareMedie',
                         color='AncoraAttivo',
                         title="Gare Medie: Attivi vs Abbandonati",
                         markers=True,
                         labels={'AncoraAttivo': 'Ancora Attivo'})
            fig.update_layout(xaxis_title="Anno di Carriera", yaxis_title="Gare Medie")
            st.plotly_chart(fig, use_container_width=True)

            # Insight box
            st.success(f"""
            💡 **Insight Chiave:** Il primo anno è decisivo!
            - Chi resta gioca **{summary_avz['curva_apprendimento']['gare_anno1_attivi']:.0f} gare**
            - Chi abbandona ne gioca solo **{summary_avz['curva_apprendimento']['gare_anno1_persi']:.0f}**
            - **Soglia critica: ~{(summary_avz['curva_apprendimento']['gare_anno1_attivi'] + summary_avz['curva_apprendimento']['gare_anno1_persi'])/2:.0f} gare/anno**

            → Bisogna far giocare i nuovi iscritti il prima possibile!
            """)

        # TAB 2: Early Warning
        with tab2:
            st.subheader("⚠️ Early Warning Circoli")
            st.markdown("""
            Identificazione precoce dei circoli a rischio chiusura basata su:
            trend tesserati, età media, attività, numero iscritti.
            """)

            # Distribuzione rischio
            col1, col2 = st.columns(2)

            with col1:
                rischio_dist = early_warning['LivelioRischio'].value_counts().reset_index()
                rischio_dist.columns = ['Livello', 'Numero']

                # Ordina
                ordine = ['CRITICO', 'ALTO', 'MEDIO', 'BASSO']
                rischio_dist['Ordine'] = rischio_dist['Livello'].map({v: i for i, v in enumerate(ordine)})
                rischio_dist = rischio_dist.sort_values('Ordine')

                fig = px.pie(rischio_dist, values='Numero', names='Livello',
                            title="Distribuzione Livelli di Rischio",
                            color='Livello',
                            color_discrete_map={'CRITICO': 'red', 'ALTO': 'orange',
                                               'MEDIO': 'yellow', 'BASSO': 'green'})
                st.plotly_chart(fig, use_container_width=True)

            with col2:
                # Rischio per regione
                if 'Regione' in early_warning.columns:
                    rischio_reg = early_warning.groupby('Regione').agg({
                        'RiskScore': 'mean',
                        'Circolo': 'count'
                    }).reset_index()
                    rischio_reg.columns = ['Regione', 'RischioMedio', 'NumCircoli']
                    rischio_reg = rischio_reg.sort_values('RischioMedio', ascending=True).tail(15)

                    fig = px.bar(rischio_reg, y='Regione', x='RischioMedio', orientation='h',
                                title="Rischio Medio per Regione",
                                text='RischioMedio',
                                color='RischioMedio',
                                color_continuous_scale='RdYlGn_r')
                    fig.update_traces(textposition='auto', cliponaxis=False, texttemplate='%{text:.1f}')
                    fig.update_layout(margin=dict(r=60))
                    st.plotly_chart(fig, use_container_width=True)

            # Lista circoli critici
            st.markdown("### 🚨 Circoli a Rischio Critico/Alto")

            critici = early_warning[early_warning['LivelioRischio'].isin(['CRITICO', 'ALTO'])].sort_values('RiskScore', ascending=False)

            if len(critici) > 0:
                # Seleziona colonne da mostrare
                cols_show = ['Circolo', 'Tess_2022', 'Tess_2025', 'TrendPct', 'EtaMedia', 'LivelioRischio', 'Regione']
                cols_show = [c for c in cols_show if c in critici.columns]
                st.dataframe(critici[cols_show].head(30), use_container_width=True)

                st.warning(f"""
                ⚠️ **{len(critici)} circoli richiedono attenzione immediata!**

                Azioni suggerite:
                1. Contattare i responsabili per capire le cause
                2. Supportare con eventi o risorse
                3. Valutare fusioni con circoli vicini
                """)
            else:
                st.success("Nessun circolo a rischio critico!")

        # TAB 3: Effetto Maestro
        with tab3:
            st.subheader("🎓 Effetto Maestro")
            st.markdown("""
            I circoli che organizzano corsi (Scuola Bridge) hanno retention migliore?
            """)

            col1, col2 = st.columns(2)

            with col1:
                # Confronto retention
                confronto_ret = pd.DataFrame({
                    'Tipo': ['Con Corsi', 'Senza Corsi'],
                    'Retention': [summary_avz['effetto_maestro']['retention_con_corsi'],
                                 summary_avz['effetto_maestro']['retention_senza_corsi']]
                })

                fig = px.bar(confronto_ret, x='Tipo', y='Retention',
                            title="Retention Media: Con vs Senza Corsi",
                            text='Retention',
                            color='Tipo',
                            color_discrete_map={'Con Corsi': 'green', 'Senza Corsi': 'gray'})
                fig.update_traces(textposition='auto', cliponaxis=False, texttemplate='%{text:.1f}%')
                st.plotly_chart(fig, use_container_width=True)

            with col2:
                # Per fascia corsisti
                fig = px.bar(effetto_maestro, x='FasciaCorsisti', y='RetentionMedia',
                            title="Retention per Numero di Corsisti Formati",
                            text='RetentionMedia',
                            color='RetentionMedia',
                            color_continuous_scale='Greens')
                fig.update_traces(textposition='auto', cliponaxis=False, texttemplate='%{text:.1f}%')
                st.plotly_chart(fig, use_container_width=True)

            st.success(f"""
            💡 **Insight:** I corsi aumentano la retention di **+{summary_avz['effetto_maestro']['differenza_pp']:.1f} punti percentuali**!

            - Circoli CON corsi: {summary_avz['effetto_maestro']['retention_con_corsi']:.1f}% retention
            - Circoli SENZA corsi: {summary_avz['effetto_maestro']['retention_senza_corsi']:.1f}% retention

            → **Ogni circolo dovrebbe avere un programma di formazione!**
            """)

        # TAB 4: Migrazione
        with tab4:
            st.subheader("🔄 Migrazione Giocatori")
            st.markdown("""
            Analisi dei giocatori che cambiano circolo durante la carriera.
            """)

            col1, col2 = st.columns(2)

            with col1:
                # Pie fedeli vs migranti
                mig_data = pd.DataFrame({
                    'Tipo': ['Fedeli (1 circolo)', 'Migranti (2+ circoli)'],
                    'Numero': [summary_avz['migrazione']['giocatori_fedeli'],
                              summary_avz['migrazione']['giocatori_migranti']]
                })

                fig = px.pie(mig_data, values='Numero', names='Tipo',
                            title="Fedeltà al Circolo",
                            color_discrete_sequence=['#2ecc71', '#3498db'])
                st.plotly_chart(fig, use_container_width=True)

            with col2:
                # Profilo comparativo
                st.markdown("#### Profilo Comparativo")
                st.dataframe(profilo_migrazione, use_container_width=True)

            st.info(f"""
            💡 **Insight:**
            - **{summary_avz['migrazione']['pct_fedeli']:.0f}%** dei giocatori resta sempre nello stesso circolo
            - I "migranti" giocano **più gare** e accumulano **più punti**
            - La migrazione non è negativa: indica giocatori più attivi!
            """)

        # TAB 5: Gender Gap
        with tab5:
            st.subheader("👫 Gender Gap per Livello")
            st.markdown("""
            Le donne abbandonano più degli uomini? A quali livelli?
            """)

            col1, col2 = st.columns(2)

            with col1:
                gender_data = pd.DataFrame({
                    'Sesso': ['Uomini', 'Donne'],
                    'Retention': [summary_avz['gender_gap']['retention_uomini'],
                                 summary_avz['gender_gap']['retention_donne']]
                })

                fig = px.bar(gender_data, x='Sesso', y='Retention',
                            title="Retention Globale per Sesso",
                            text='Retention',
                            color='Sesso',
                            color_discrete_map={'Uomini': '#3498db', 'Donne': '#e74c3c'})
                fig.update_traces(textposition='auto', cliponaxis=False, texttemplate='%{text:.1f}%')
                st.plotly_chart(fig, use_container_width=True)

            with col2:
                # Gender gap per categoria
                if (RESULTS_AVZ / 'gender_gap_categoria.csv').exists():
                    gender_cat = pd.read_csv(RESULTS_AVZ / 'gender_gap_categoria.csv')

                    # Pivot per visualizzazione
                    gender_pivot = gender_cat.pivot(index='Categoria', columns='Sesso', values='Retention')
                    if 'M' in gender_pivot.columns and 'F' in gender_pivot.columns:
                        gender_pivot['Gap'] = gender_pivot['M'] - gender_pivot['F']
                        gender_pivot = gender_pivot.reset_index()

                        # Top gap positivi (uomini meglio)
                        top_gap = gender_pivot.sort_values('Gap', ascending=False).head(10)

                        fig = px.bar(top_gap, y='Categoria', x='Gap', orientation='h',
                                    title="Gap Retention (M-F) per Categoria",
                                    text='Gap',
                                    color='Gap',
                                    color_continuous_scale='RdBu_r')
                        fig.update_traces(textposition='auto', cliponaxis=False, texttemplate='%{text:.1f}')
                        fig.update_layout(margin=dict(r=60))
                        st.plotly_chart(fig, use_container_width=True)

            gap = summary_avz['gender_gap']['gap_pp']
            if abs(gap) < 2:
                st.success(f"""
                ✅ **Buona notizia:** Il gender gap è minimo ({gap:+.1f} punti)!

                Uomini e donne hanno retention molto simile.
                """)
            else:
                st.warning(f"""
                ⚠️ **Attenzione:** Gender gap di {gap:+.1f} punti

                {'Gli uomini' if gap > 0 else 'Le donne'} hanno retention maggiore.
                Analizzare le cause per categoria.
                """)

    else:
        st.warning("Dati analisi avanzate non disponibili. Esegui prima `09_analisi_avanzate_innovative.py`")

# ============================================================================
# PAGINA: ATTIVITÀ PER ETÀ/SESSO
# ============================================================================
elif pagina == "🎯 Attività per Età/Sesso":
    st.title("🎯 Attività per Età e Sesso")

    st.markdown("""
    Analisi delle gare e campionati per fascia d'età e sesso.
    """)

    RESULTS_ATT = OUTPUT_DIR / 'results_attivita'

    if RESULTS_ATT.exists():
        # Carica dati
        with open(RESULTS_ATT / 'summary_attivita.json', 'r') as f:
            summary_att = json.load(f)

        gare_pivot = pd.read_csv(RESULTS_ATT / 'gare_pivot_eta_sesso.csv')
        camp_pivot = pd.read_csv(RESULTS_ATT / 'campionati_pivot_eta_sesso.csv')
        part_pivot = pd.read_csv(RESULTS_ATT / 'partecipazione_campionati.csv')
        gare_eta_sesso = pd.read_csv(RESULTS_ATT / 'gare_per_eta_sesso.csv')

        # KPI
        st.markdown("### 📊 Riepilogo")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric(
                "Fascia Più Attiva",
                summary_att['fascia_piu_attiva']['fascia'],
                f"{summary_att['fascia_piu_attiva']['gare_medie']} gare/anno"
            )
        with col2:
            st.metric(
                "Gap Gare M-F",
                f"{summary_att['gare_medie_globali']['gap']:+.1f}",
                "gare/anno"
            )
        with col3:
            st.metric(
                "Gap Campionati M-F",
                f"{summary_att['campionati_medi_globali']['gap']:+.0f}",
                "punti"
            )
        with col4:
            st.metric(
                "% Campionati M/F",
                f"{summary_att['partecipazione_campionati']['M']:.0f}% / {summary_att['partecipazione_campionati']['F']:.0f}%"
            )

        st.markdown("---")

        # Tabs
        tab1, tab2, tab3 = st.tabs([
            "🎮 Gare per Età/Sesso",
            "🏆 Campionati per Età/Sesso",
            "📊 Partecipazione Campionati"
        ])

        # Ordine fasce età
        ordine_eta = ['<18', '18-30', '30-40', '40-50', '50-60', '60-70', '70-80', '80-90', '90+']

        # TAB 1: Gare
        with tab1:
            st.subheader("🎮 Gare Medie Annuali per Età e Sesso")

            # Prepara dati per grafico
            gare_long = gare_eta_sesso[gare_eta_sesso['Sesso'].isin(['M', 'F'])].copy()
            gare_long['FasciaEta'] = pd.Categorical(gare_long['FasciaEta'], categories=ordine_eta, ordered=True)
            gare_long = gare_long.sort_values('FasciaEta')

            fig = px.bar(gare_long, x='FasciaEta', y='GareMedie', color='Sesso',
                        barmode='group',
                        title="Gare Medie Annuali per Fascia d'Età e Sesso",
                        labels={'GareMedie': 'Gare Medie', 'FasciaEta': "Fascia d'Età"},
                        color_discrete_map={'M': '#3498db', 'F': '#e74c3c'},
                        text='GareMedie')
            fig.update_traces(textposition='auto', cliponaxis=False, texttemplate='%{text:.0f}')
            fig.update_layout(xaxis_title="Fascia d'Età", yaxis_title="Gare Medie/Anno")
            st.plotly_chart(fig, use_container_width=True)

            # Gap M-F
            st.markdown("#### Gap Uomini-Donne per Fascia d'Età")

            gare_pivot_calc = gare_pivot.copy()
            if 'M' in gare_pivot_calc.columns and 'F' in gare_pivot_calc.columns:
                gare_pivot_calc['Gap'] = gare_pivot_calc['M'] - gare_pivot_calc['F']
                gare_pivot_calc['FasciaEta'] = pd.Categorical(gare_pivot_calc['FasciaEta'], categories=ordine_eta, ordered=True)
                gare_pivot_calc = gare_pivot_calc.sort_values('FasciaEta')

                fig = px.bar(gare_pivot_calc, x='FasciaEta', y='Gap',
                            title="Gap Gare (M-F) per Fascia d'Età",
                            text='Gap',
                            color='Gap',
                            color_continuous_scale='RdBu_r',
                            color_continuous_midpoint=0)
                fig.update_traces(textposition='auto', cliponaxis=False, texttemplate='%{text:+.1f}')
                fig.update_layout(xaxis_title="Fascia d'Età", yaxis_title="Gap (M-F)")
                st.plotly_chart(fig, use_container_width=True)

            # Tabella
            with st.expander("📋 Tabella Dati"):
                st.dataframe(gare_pivot, use_container_width=True)

            st.info("""
            💡 **Insight:**
            - La fascia **70-80** è la più attiva con quasi 48 gare/anno
            - Il gap M-F è massimo nella fascia **30-40** (+10 gare)
            - Le donne **90+** giocano PIÙ degli uomini coetanei!
            """)

        # TAB 2: Campionati
        with tab2:
            st.subheader("🏆 Punti Campionati Medi per Età e Sesso")

            # Prepara dati
            camp_long = gare_eta_sesso[gare_eta_sesso['Sesso'].isin(['M', 'F'])].copy()
            camp_long['FasciaEta'] = pd.Categorical(camp_long['FasciaEta'], categories=ordine_eta, ordered=True)
            camp_long = camp_long.sort_values('FasciaEta')

            fig = px.bar(camp_long, x='FasciaEta', y='PuntiCampMedi', color='Sesso',
                        barmode='group',
                        title="Punti Campionati Medi per Fascia d'Età e Sesso",
                        labels={'PuntiCampMedi': 'Punti Medi', 'FasciaEta': "Fascia d'Età"},
                        color_discrete_map={'M': '#3498db', 'F': '#e74c3c'},
                        text='PuntiCampMedi')
            fig.update_traces(textposition='auto', cliponaxis=False, texttemplate='%{text:.0f}')
            fig.update_layout(xaxis_title="Fascia d'Età", yaxis_title="Punti Campionati Medi")
            st.plotly_chart(fig, use_container_width=True)

            # Picco per fascia
            st.markdown("#### Picco Attività Agonistica")

            camp_totale = camp_pivot.copy()
            camp_totale['FasciaEta'] = pd.Categorical(camp_totale['FasciaEta'], categories=ordine_eta, ordered=True)
            camp_totale = camp_totale.sort_values('FasciaEta')

            fig = px.line(camp_totale, x='FasciaEta', y='Totale',
                         title="Punti Campionati Medi per Fascia d'Età (Totale)",
                         markers=True)
            fig.update_layout(xaxis_title="Fascia d'Età", yaxis_title="Punti Medi")
            st.plotly_chart(fig, use_container_width=True)

            with st.expander("📋 Tabella Dati"):
                st.dataframe(camp_pivot, use_container_width=True)

            st.info("""
            💡 **Insight:**
            - Il picco agonistico è nella fascia **40-50** (~6.800 punti)
            - Le donne **30-40** hanno più punti degli uomini (+822)!
            - Dopo i 70 anni i punti calano progressivamente
            """)

        # TAB 3: Partecipazione
        with tab3:
            st.subheader("📊 % Partecipazione a Campionati")

            part_long = part_pivot.melt(id_vars='FasciaEta', value_vars=['M', 'F'],
                                        var_name='Sesso', value_name='Partecipazione')
            part_long['FasciaEta'] = pd.Categorical(part_long['FasciaEta'], categories=ordine_eta, ordered=True)
            part_long = part_long.sort_values('FasciaEta')

            fig = px.bar(part_long, x='FasciaEta', y='Partecipazione', color='Sesso',
                        barmode='group',
                        title="% Partecipazione a Campionati per Fascia d'Età e Sesso",
                        labels={'Partecipazione': '% Partecipazione', 'FasciaEta': "Fascia d'Età"},
                        color_discrete_map={'M': '#3498db', 'F': '#e74c3c'},
                        text='Partecipazione')
            fig.update_traces(textposition='auto', cliponaxis=False, texttemplate='%{text:.0f}%')
            fig.update_layout(xaxis_title="Fascia d'Età", yaxis_title="% Partecipazione")
            st.plotly_chart(fig, use_container_width=True)

            # Gap partecipazione
            part_pivot_calc = part_pivot.copy()
            if 'M' in part_pivot_calc.columns and 'F' in part_pivot_calc.columns:
                part_pivot_calc['Gap'] = part_pivot_calc['M'] - part_pivot_calc['F']
                part_pivot_calc['FasciaEta'] = pd.Categorical(part_pivot_calc['FasciaEta'], categories=ordine_eta, ordered=True)
                part_pivot_calc = part_pivot_calc.sort_values('FasciaEta')

                fig = px.bar(part_pivot_calc, x='FasciaEta', y='Gap',
                            title="Gap % Partecipazione Campionati (M-F)",
                            text='Gap',
                            color='Gap',
                            color_continuous_scale='RdBu_r',
                            color_continuous_midpoint=0)
                fig.update_traces(textposition='auto', cliponaxis=False, texttemplate='%{text:+.1f}pp')
                fig.update_layout(xaxis_title="Fascia d'Età", yaxis_title="Gap (M-F) punti %")
                st.plotly_chart(fig, use_container_width=True)

            with st.expander("📋 Tabella Dati"):
                st.dataframe(part_pivot, use_container_width=True)

            st.info("""
            💡 **Insight:**
            - Picco partecipazione: fascia **40-50** (~70%)
            - Gap M-F costante di **5-7 punti %** (uomini più competitivi)
            - Unica eccezione: fascia 40-50 dove le donne partecipano di più!
            """)

    else:
        st.warning("Dati attività non disponibili. Esegui prima l'analisi.")

# ============================================================================
# PAGINA: CLUSTER E TERRITORI
# ============================================================================
elif pagina == "🧩 Cluster e Territori":
    st.title("🧩 Cluster Comportamentali e Analisi Territoriali")

    st.markdown("""
    Segmentazione giocatori per comportamento e analisi delle dinamiche territoriali.
    """)

    RESULTS_COMP = OUTPUT_DIR / 'results_comportamentali'

    if RESULTS_COMP.exists():
        # Carica dati
        with open(RESULTS_COMP / 'summary_comportamentali.json', 'r') as f:
            summary_comp = json.load(f)

        cluster_stats = pd.read_csv(RESULTS_COMP / 'cluster_stats.csv')
        retention_cluster = pd.read_csv(RESULTS_COMP / 'retention_cluster.csv')
        confronto_metro = pd.read_csv(RESULTS_COMP / 'confronto_metro_provincia.csv')
        stats_area = pd.read_csv(RESULTS_COMP / 'stats_per_area.csv')
        evol_province = pd.read_csv(RESULTS_COMP / 'evoluzione_province.csv')

        # KPI
        st.markdown("### 📊 Riepilogo")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            top_cluster = cluster_stats.iloc[0]
            st.metric(
                "Cluster Principale",
                top_cluster['Cluster'],
                f"{top_cluster['Percentuale']:.0f}% giocatori"
            )
        with col2:
            best_ret = retention_cluster.sort_values('Retention', ascending=False).iloc[0]
            st.metric(
                "Miglior Retention",
                best_ret['Cluster'],
                f"{best_ret['Retention']:.0f}%"
            )
        with col3:
            st.metric(
                "Cambio Circolo Locale",
                f"{summary_comp['cannibalizzazione']['cambio_stessa_provincia_pct']:.0f}%",
                "restano in provincia"
            )
        with col4:
            ret_metro = summary_comp['citta_vs_provincia']['retention_metro']
            ret_prov = summary_comp['citta_vs_provincia']['retention_provincia']
            st.metric(
                "Gap Retention Metro/Prov",
                f"{ret_metro - ret_prov:+.1f}pp"
            )

        st.markdown("---")

        # Tabs
        tab1, tab2, tab3 = st.tabs([
            "🧩 Cluster Comportamentali",
            "🔄 Cannibalizzazione Circoli",
            "🏙️ Città vs Provincia"
        ])

        # TAB 1: Cluster
        with tab1:
            st.subheader("🧩 Cluster Comportamentali")
            st.markdown("""
            Segmentazione dei giocatori basata su:
            - Gare giocate (intensità)
            - Anni di presenza (fedeltà)
            - Punti campionati (competitività)
            """)

            col1, col2 = st.columns(2)

            with col1:
                # Distribuzione cluster
                fig = px.pie(cluster_stats, values='NumGiocatori', names='Cluster',
                            title="Distribuzione Cluster",
                            color_discrete_sequence=px.colors.qualitative.Set2)
                st.plotly_chart(fig, use_container_width=True)

            with col2:
                # Retention per cluster
                ret_sorted = retention_cluster.sort_values('Retention', ascending=True)
                fig = px.bar(ret_sorted, y='Cluster', x='Retention', orientation='h',
                            title="Retention per Cluster",
                            text='Retention',
                            color='Retention',
                            color_continuous_scale='RdYlGn')
                fig.update_traces(textposition='auto', cliponaxis=False, texttemplate='%{text:.1f}%')
                fig.update_layout(margin=dict(r=60))
                st.plotly_chart(fig, use_container_width=True)

            # Profilo cluster
            st.markdown("#### Profilo dei Cluster")

            fig = px.scatter(cluster_stats, x='GareMedie', y='AnniMedi',
                            size='NumGiocatori', color='Cluster',
                            hover_data=['EtaMedia', 'Percentuale'],
                            title="Mappa Cluster: Gare vs Anni Presenza",
                            labels={'GareMedie': 'Gare Medie/Anno', 'AnniMedi': 'Anni Presenza'})
            st.plotly_chart(fig, use_container_width=True)

            # Tabella dettaglio
            with st.expander("📋 Dettaglio Cluster"):
                st.dataframe(cluster_stats.round(1), use_container_width=True)

            st.info("""
            💡 **Insight:**
            - **37.9% Occasionali**: giocano poco, restano poco → target per engagement
            - **26.0% Sociali**: ~19 gare/anno, 4.7 anni presenza → base stabile
            - **Super Agonisti** hanno **86.7% retention** → modello da replicare
            - Il segreto: più gare = più retention!
            """)

        # TAB 2: Cannibalizzazione
        with tab2:
            st.subheader("🔄 Cannibalizzazione Circoli")
            st.markdown("""
            I circoli vicini si rubano iscritti o crescono insieme?
            """)

            col1, col2 = st.columns(2)

            with col1:
                # Correlazione
                corr = summary_comp['cannibalizzazione']['correlazione_circoli_tesserati']
                if corr:
                    st.metric("Correlazione Circoli-Tesserati", f"{corr:.2f}",
                             help="Più circoli = più tesserati?")

                    if corr > 0.7:
                        st.success("✅ Correlazione FORTE: più circoli nella provincia = più tesserati totali!")
                    elif corr > 0.4:
                        st.warning("⚠️ Correlazione moderata")
                    else:
                        st.error("❌ Correlazione debole")

            with col2:
                # Cambio circolo
                cambio_locale = summary_comp['cannibalizzazione']['cambio_stessa_provincia_pct']
                cambio_data = pd.DataFrame({
                    'Tipo': ['Stessa Provincia', 'Altra Provincia'],
                    'Percentuale': [cambio_locale, 100 - cambio_locale]
                })

                fig = px.pie(cambio_data, values='Percentuale', names='Tipo',
                            title="Chi Cambia Circolo Dove Va?",
                            color_discrete_sequence=['#3498db', '#e74c3c'])
                st.plotly_chart(fig, use_container_width=True)

            # Evoluzione province
            st.markdown("#### Evoluzione Province (Circoli vs Tesserati)")

            # Province che hanno aggiunto circoli
            prov_piu = evol_province[evol_province['DeltaCircoli'] > 0].sort_values('DeltaCircoli', ascending=False).head(10)
            prov_meno = evol_province[evol_province['DeltaCircoli'] < 0].sort_values('DeltaCircoli').head(10)

            col1, col2 = st.columns(2)

            with col1:
                st.markdown("**Province che hanno AGGIUNTO circoli:**")
                if len(prov_piu) > 0:
                    fig = px.bar(prov_piu, x='Provincia', y='DeltaTessPct',
                                title="Effetto su Tesserati",
                                text='DeltaTessPct',
                                color='DeltaTessPct',
                                color_continuous_scale='RdYlGn',
                                color_continuous_midpoint=0)
                    fig.update_traces(textposition='auto', cliponaxis=False, texttemplate='%{text:+.0f}%')
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("Nessuna provincia ha aggiunto circoli")

            with col2:
                st.markdown("**Province che hanno PERSO circoli:**")
                if len(prov_meno) > 0:
                    fig = px.bar(prov_meno, x='Provincia', y='DeltaTessPct',
                                title="Effetto su Tesserati",
                                text='DeltaTessPct',
                                color='DeltaTessPct',
                                color_continuous_scale='RdYlGn',
                                color_continuous_midpoint=0)
                    fig.update_traces(textposition='auto', cliponaxis=False, texttemplate='%{text:+.0f}%')
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("Nessuna provincia ha perso circoli")

            st.info("""
            💡 **Insight:**
            - Correlazione 0.94: **PIÙ circoli = PIÙ tesserati** (non cannibalizzazione!)
            - **83.9%** di chi cambia circolo resta nella stessa provincia
            - Aprire nuovi circoli è positivo per il territorio
            """)

        # TAB 3: Città vs Provincia
        with tab3:
            st.subheader("🏙️ Città Metropolitana vs Provincia")
            st.markdown("""
            Confronto delle dinamiche tra aree metropolitane e province.
            """)

            col1, col2 = st.columns(2)

            with col1:
                # Confronto metriche
                fig = px.bar(confronto_metro, x='Metrica', y=['Città Metro', 'Provincia'],
                            title="Confronto Metriche",
                            barmode='group')
                st.plotly_chart(fig, use_container_width=True)

            with col2:
                # Retention
                ret_data = pd.DataFrame({
                    'Area': ['Città Metropolitana', 'Provincia'],
                    'Retention': [summary_comp['citta_vs_provincia']['retention_metro'],
                                 summary_comp['citta_vs_provincia']['retention_provincia']]
                })

                fig = px.bar(ret_data, x='Area', y='Retention',
                            title="Retention per Tipo Area",
                            text='Retention',
                            color='Area',
                            color_discrete_map={'Città Metropolitana': '#3498db', 'Provincia': '#2ecc71'})
                fig.update_traces(textposition='auto', cliponaxis=False, texttemplate='%{text:.1f}%')
                st.plotly_chart(fig, use_container_width=True)

            # Trend nel tempo
            st.markdown("#### Trend Tesserati nel Tempo")

            fig = px.line(stats_area, x='Anno', y='Tesserati', color='TipoArea',
                         title="Evoluzione Tesserati: Metro vs Provincia",
                         markers=True)
            fig.update_xaxes(dtick=1)
            st.plotly_chart(fig, use_container_width=True)

            # ANALISI DECLINO: Chi sta morendo di più?
            st.markdown("#### 📉 Chi Sta Perdendo di Più?")

            # Calcola variazioni dal 2019 (pre-COVID)
            stats_2019 = stats_area[stats_area['Anno'] == 2019].set_index('TipoArea')
            stats_2025 = stats_area[stats_area['Anno'] == stats_area['Anno'].max()].set_index('TipoArea')

            if 'Città Metropolitana' in stats_2019.index and 'Provincia' in stats_2019.index:
                metro_2019 = stats_2019.loc['Città Metropolitana', 'Tesserati']
                metro_2025 = stats_2025.loc['Città Metropolitana', 'Tesserati']
                prov_2019 = stats_2019.loc['Provincia', 'Tesserati']
                prov_2025 = stats_2025.loc['Provincia', 'Tesserati']

                var_metro = (metro_2025 - metro_2019) / metro_2019 * 100
                var_prov = (prov_2025 - prov_2019) / prov_2019 * 100

                col1, col2 = st.columns(2)

                with col1:
                    st.metric(
                        "Città Metropolitane (2019→2025)",
                        f"{metro_2025:,.0f}",
                        f"{var_metro:+.1f}%",
                        delta_color="inverse"
                    )

                with col2:
                    st.metric(
                        "Province (2019→2025)",
                        f"{prov_2025:,.0f}",
                        f"{var_prov:+.1f}%",
                        delta_color="inverse"
                    )

                if var_metro < var_prov:
                    st.error(f"🚨 **Le CITTÀ METROPOLITANE stanno peggio!** ({var_metro:+.1f}% vs {var_prov:+.1f}%)")
                else:
                    st.error(f"🚨 **Le PROVINCE stanno peggio!** ({var_prov:+.1f}% vs {var_metro:+.1f}%)")

            # Dettaglio singole città metropolitane
            st.markdown("#### 🏙️ Dettaglio Singole Città Metropolitane")

            citta_metro_list = ['Milano', 'Roma', 'Napoli', 'Torino', 'Firenze', 'Bologna', 'Genova',
                              'Venezia', 'Bari', 'Palermo', 'Catania', 'Cagliari', 'Messina', 'Reggio Calabria']

            # Calcola variazione per ogni città
            citta_var = []
            for citta in citta_metro_list:
                df_citta = df[df['Provincia'] == citta]
                t2019 = df_citta[df_citta['Anno'] == 2019]['MmbCode'].nunique()
                t2025 = df_citta[df_citta['Anno'] == df['Anno'].max()]['MmbCode'].nunique()
                if t2019 > 0:
                    var = (t2025 - t2019) / t2019 * 100
                    citta_var.append({'Città': citta, 'Tess2019': t2019, 'Tess2025': t2025, 'Variazione': var})

            df_citta_var = pd.DataFrame(citta_var).sort_values('Variazione')

            fig = px.bar(df_citta_var, y='Città', x='Variazione', orientation='h',
                        title="Variazione % Tesserati 2019→2025 per Città",
                        text='Variazione',
                        color='Variazione',
                        color_continuous_scale='RdYlGn',
                        color_continuous_midpoint=0)
            fig.update_traces(textposition='auto', cliponaxis=False, texttemplate='%{text:+.1f}%')
            fig.update_layout(margin=dict(l=100, r=60))
            st.plotly_chart(fig, use_container_width=True)

            # Tabella confronto
            with st.expander("📋 Confronto Dettagliato"):
                st.dataframe(confronto_metro, use_container_width=True)

            with st.expander("📋 Dettaglio Città Metropolitane"):
                st.dataframe(df_citta_var.round(1), use_container_width=True)

            gap_gare = summary_comp['citta_vs_provincia']['gare_medie_metro'] - summary_comp['citta_vs_provincia']['gare_medie_provincia']
            st.info(f"""
            💡 **Insight:**
            - **Le grandi città perdono di più** (-32.6% vs -28.2%)
            - **Milano, Roma, Torino, Genova** perdono ~37%
            - **Bari e Reggio Calabria** in controtendenza POSITIVA!
            - Venezia e Messina tengono bene (-5%)
            - La provincia sta recuperando terreno
            """)

    else:
        st.warning("Dati comportamentali non disponibili. Esegui prima `10_analisi_comportamentali.py`")

# ============================================================================
# PAGINA: PRIORITÀ INTERVENTO
# ============================================================================
elif pagina == "🎖️ Priorità Intervento":
    st.title("🎖️ Priorità di Intervento")

    st.markdown("""
    Matrice delle priorità basata su tutte le analisi effettuate.
    Ogni intervento è valutato per **impatto**, **difficoltà**, **tempo di ritorno** e **forza delle evidenze**.
    """)

    RESULTS_PRIO = OUTPUT_DIR / 'results_priorita'

    if RESULTS_PRIO.exists():
        # Carica dati
        with open(RESULTS_PRIO / 'summary_priorita.json', 'r') as f:
            summary_prio = json.load(f)

        priorita_df = pd.read_csv(RESULTS_PRIO / 'priorita_interventi.csv')

        # KPI principali
        st.markdown("### 📊 Riepilogo Impatto")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric(
                "Tesserati Attuali",
                f"{summary_prio['tesserati_attuali']:,}"
            )
        with col2:
            st.metric(
                "Impatto Totale Stimato",
                f"+{summary_prio['impatto_totale_stimato']:,}",
                f"+{100*summary_prio['impatto_totale_stimato']/summary_prio['tesserati_attuali']:.1f}%"
            )
        with col3:
            st.metric(
                "N. Interventi",
                len(priorita_df)
            )

        st.markdown("---")

        # Grafico Score
        st.markdown("### 🏆 Classifica Priorità (Score)")

        priorita_sorted = priorita_df.sort_values('Score', ascending=True)

        fig = px.bar(priorita_sorted, y='Intervento', x='Score', orientation='h',
                    title="Score Priorità (0-100)",
                    text='Score',
                    color='Score',
                    color_continuous_scale='RdYlGn')
        fig.update_traces(textposition='auto', cliponaxis=False, texttemplate='%{text:.0f}')
        fig.update_layout(margin=dict(l=250, r=60), height=500)
        st.plotly_chart(fig, use_container_width=True)

        st.markdown("""
        **Come si calcola lo Score:**
        - **Impatto potenziale** (40%): quanti tesserati possiamo guadagnare
        - **Facilità** (30%): quanto è difficile implementare l'intervento
        - **Tempo di ritorno** (15%): quanto velocemente vediamo i risultati
        - **Forza evidenze** (15%): quanto sono solide le correlazioni statistiche
        """)

        st.markdown("---")

        # Dettaglio per intervento
        st.markdown("### 📋 Dettaglio Interventi per Priorità")

        for idx, row in priorita_df.sort_values('Score', ascending=False).iterrows():
            rank = priorita_df.sort_values('Score', ascending=False).index.get_loc(idx) + 1

            # Colore basato su priorità
            if rank <= 3:
                emoji = "🥇🥈🥉"[rank-1]
                color = "green" if rank == 1 else "blue" if rank == 2 else "orange"
            else:
                emoji = f"#{rank}"
                color = "gray"

            with st.expander(f"{emoji} **{row['Intervento']}** (Score: {row['Score']:.0f})", expanded=(rank <= 3)):
                col1, col2 = st.columns(2)

                with col1:
                    st.markdown(f"**🎯 Target:** {row['Target']}")
                    st.markdown(f"**📊 Evidenza:** {row['Evidenza']}")
                    st.markdown(f"**🔗 Correlazione:** {row['Correlazione']}")

                with col2:
                    st.metric("Impatto Stimato", f"+{row['ImpattoPotenziale']:,} tesserati")

                    diff_color = {'BASSA': '🟢', 'MEDIA': '🟡', 'ALTA': '🟠', 'MOLTO ALTA': '🔴'}
                    st.markdown(f"**Difficoltà:** {diff_color.get(row['Difficoltà'], '⚪')} {row['Difficoltà']}")

                    tempo_color = {'BREVE': '🟢', 'MEDIO': '🟡', 'LUNGO': '🔴'}
                    st.markdown(f"**Tempo Ritorno:** {tempo_color.get(row['TempoRitorno'], '⚪')} {row['TempoRitorno']}")

        st.markdown("---")

        # Grafico impatto vs difficoltà
        st.markdown("### 📈 Matrice Impatto vs Difficoltà")

        diff_map = {'BASSA': 1, 'MEDIA': 2, 'ALTA': 3, 'MOLTO ALTA': 4}
        priorita_df['DiffNum'] = priorita_df['Difficoltà'].map(diff_map)

        fig = px.scatter(priorita_df, x='DiffNum', y='ImpattoPotenziale',
                        size='Score', color='TempoRitorno',
                        hover_name='Intervento',
                        title="Matrice: Impatto vs Difficoltà",
                        labels={'DiffNum': 'Difficoltà (1=Bassa, 4=Molto Alta)',
                               'ImpattoPotenziale': 'Impatto Potenziale (tesserati)'},
                        color_discrete_map={'BREVE': 'green', 'MEDIO': 'orange', 'LUNGO': 'red'})
        fig.update_layout(xaxis=dict(tickvals=[1, 2, 3, 4], ticktext=['Bassa', 'Media', 'Alta', 'Molto Alta']))

        # Aggiungi quadranti
        fig.add_hline(y=priorita_df['ImpattoPotenziale'].median(), line_dash="dash", line_color="gray", opacity=0.5)
        fig.add_vline(x=2.5, line_dash="dash", line_color="gray", opacity=0.5)

        # Annotazioni quadranti
        fig.add_annotation(x=1.5, y=priorita_df['ImpattoPotenziale'].max()*0.9,
                          text="⭐ PRIORITÀ ALTA", showarrow=False, font=dict(color="green", size=12))
        fig.add_annotation(x=3.5, y=priorita_df['ImpattoPotenziale'].max()*0.9,
                          text="⚠️ VALUTARE", showarrow=False, font=dict(color="orange", size=12))
        fig.add_annotation(x=1.5, y=priorita_df['ImpattoPotenziale'].min()*1.5,
                          text="✓ QUICK WINS", showarrow=False, font=dict(color="blue", size=12))
        fig.add_annotation(x=3.5, y=priorita_df['ImpattoPotenziale'].min()*1.5,
                          text="❌ BASSA PRIORITÀ", showarrow=False, font=dict(color="red", size=12))

        st.plotly_chart(fig, use_container_width=True)

        st.markdown("---")

        # Piano d'azione suggerito
        st.markdown("### 🚀 Piano d'Azione Suggerito")

        top3 = priorita_df.sort_values('Score', ascending=False).head(3)

        st.success(f"""
        **FASE 1 - AZIONI IMMEDIATE (0-6 mesi):**

        1. **{top3.iloc[0]['Intervento']}**
           - {top3.iloc[0]['Target']}
           - Impatto stimato: +{top3.iloc[0]['ImpattoPotenziale']:,} tesserati

        2. **{top3.iloc[1]['Intervento']}**
           - {top3.iloc[1]['Target']}
           - Impatto stimato: +{top3.iloc[1]['ImpattoPotenziale']:,} tesserati

        3. **{top3.iloc[2]['Intervento']}**
           - {top3.iloc[2]['Target']}
           - Impatto stimato: +{top3.iloc[2]['ImpattoPotenziale']:,} tesserati

        **IMPATTO FASE 1:** +{top3['ImpattoPotenziale'].sum():,} tesserati potenziali
        """)

        mid_prio = priorita_df.sort_values('Score', ascending=False).iloc[3:6]
        st.warning(f"""
        **FASE 2 - AZIONI MEDIO TERMINE (6-18 mesi):**

        4. {mid_prio.iloc[0]['Intervento']} (+{mid_prio.iloc[0]['ImpattoPotenziale']:,})
        5. {mid_prio.iloc[1]['Intervento']} (+{mid_prio.iloc[1]['ImpattoPotenziale']:,})
        6. {mid_prio.iloc[2]['Intervento']} (+{mid_prio.iloc[2]['ImpattoPotenziale']:,})
        """)

        low_prio = priorita_df.sort_values('Score', ascending=False).iloc[6:]
        if len(low_prio) > 0:
            st.info(f"""
            **FASE 3 - AZIONI LUNGO TERMINE (18+ mesi):**

            {', '.join([f"{r['Intervento']} (+{r['ImpattoPotenziale']:,})" for _, r in low_prio.iterrows()])}
            """)

        # Tabella completa
        with st.expander("📋 Tabella Completa"):
            st.dataframe(priorita_df.sort_values('Score', ascending=False), use_container_width=True)

    else:
        st.warning("Dati priorità non disponibili. Esegui prima l'analisi priorità.")

# ============================================================================
# PAGINA: ESPLORA DATI
# ============================================================================
elif pagina == "🔍 Esplora Dati":
    st.title("🔍 Esplora Dati")

    st.markdown("Esplora liberamente i dati con filtri personalizzati.")

    # Statistiche dataset filtrato
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Record", f"{len(df_filtered):,}")
    with col2:
        st.metric("Giocatori Unici", f"{df_filtered['MmbCode'].nunique():,}")
    with col3:
        col_assoc = 'Associazione' if 'Associazione' in df_filtered.columns else 'GrpName'
        st.metric("Associazioni", f"{df_filtered[col_assoc].nunique():,}")

    st.markdown("---")

    # Analisi personalizzata
    st.subheader("📊 Crea il tuo grafico")

    col1, col2, col3 = st.columns(3)

    with col1:
        x_axis = st.selectbox(
            "Asse X",
            ['Anno', 'GrpArea', 'CatLabel', 'FasciaEta', 'Associazione']
        )

    with col2:
        y_axis = st.selectbox(
            "Metrica Y",
            ['Conteggio', 'GareGiocate', 'Anni', 'PuntiTotali']
        )

    with col3:
        color_by = st.selectbox(
            "Colora per",
            [None, 'GrpArea', 'CatLabel', 'IsAgonista', 'MmbSex']
        )

    # Genera grafico
    if y_axis == 'Conteggio':
        if color_by:
            chart_data = df_filtered.groupby([x_axis, color_by]).size().reset_index(name='Conteggio')
            fig = px.bar(chart_data, x=x_axis, y='Conteggio', color=color_by)
        else:
            chart_data = df_filtered.groupby(x_axis).size().reset_index(name='Conteggio')
            fig = px.bar(chart_data, x=x_axis, y='Conteggio')
    else:
        if color_by:
            chart_data = df_filtered.groupby([x_axis, color_by])[y_axis].mean().reset_index()
            fig = px.bar(chart_data, x=x_axis, y=y_axis, color=color_by)
        else:
            chart_data = df_filtered.groupby(x_axis)[y_axis].mean().reset_index()
            fig = px.bar(chart_data, x=x_axis, y=y_axis)

    st.plotly_chart(fig, use_container_width=True)

    # Ricerca giocatore
    st.markdown("---")
    st.subheader("🔍 Cerca Giocatore")

    search_name = st.text_input("Nome giocatore:", "")

    if search_name and len(search_name) >= 3:
        results = df_filtered[df_filtered['MmbName'].str.contains(search_name, case=False, na=False)]

        if len(results) > 0:
            # Aggrega per giocatore
            giocatore_info = results.groupby('MmbCode').agg({
                'MmbName': 'first',
                'Anno': ['min', 'max', 'count'],
                'GareGiocate': ['mean', 'sum'],
                'Anni': 'last',
                'CatLabel': 'last',
                'Associazione': 'last'
            }).reset_index()

            giocatore_info.columns = ['Codice', 'Nome', 'Primo Anno', 'Ultimo Anno',
                                      'Anni Presenza', 'Gare Medie', 'Gare Totali',
                                      'Età', 'Categoria', 'Associazione']

            st.dataframe(giocatore_info, use_container_width=True)

            # Dettaglio singolo giocatore
            if len(giocatore_info) > 0:
                selected = st.selectbox("Seleziona giocatore per dettaglio:",
                                       giocatore_info['Nome'].tolist())

                if selected:
                    player_data = results[results['MmbName'] == selected]

                    col1, col2 = st.columns(2)

                    with col1:
                        fig = px.line(player_data.sort_values('Anno'),
                                     x='Anno', y='GareGiocate',
                                     title=f"Gare per anno - {selected}",
                                     markers=True)
                        fig.update_xaxes(dtick=1)
                        st.plotly_chart(fig, use_container_width=True)

                    with col2:
                        fig = px.bar(player_data.sort_values('Anno'),
                                    x='Anno', y='PuntiTotali',
                                    title=f"Punti per anno - {selected}")
                        fig.update_xaxes(dtick=1)
                        st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Nessun giocatore trovato con questo nome")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: gray;'>
    <small>FIGB Dashboard | Dati 2017-2025 | Sviluppato con Streamlit</small>
</div>
""", unsafe_allow_html=True)
