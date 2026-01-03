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

# ============================================================================
# SIDEBAR - FILTRI
# ============================================================================
st.sidebar.title("🃏 FIGB Dashboard")
st.sidebar.markdown("---")

# Navigazione
pagina = st.sidebar.selectbox(
    "📊 Sezione",
    ["🏠 Overview", "📈 Trend Temporale", "🗺️ Analisi Regionale",
     "🏆 Mappa Agonismo", "🏢 Analisi Associazioni", "⚠️ Giocatori a Rischio",
     "🔮 Modello Predittivo", "🔍 Esplora Dati"]
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
# PAGINA: OVERVIEW
# ============================================================================
if pagina == "🏠 Overview":
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
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("👥 Piramide Età 2025")
        # Usa solo dati 2025 (rispettando altri filtri globali)
        df_2025 = df_filtered[df_filtered['Anno'] == 2025].copy()
        if len(df_2025) > 0:
            df_2025['FasciaEta'] = pd.cut(df_2025['Anni'],
                                           bins=[0, 30, 40, 50, 60, 70, 80, 100],
                                           labels=['<30', '30-39', '40-49', '50-59', '60-69', '70-79', '80+'])
            eta_dist = df_2025['FasciaEta'].value_counts().sort_index()
            fig = px.bar(x=eta_dist.index, y=eta_dist.values,
                         color=eta_dist.values, color_continuous_scale='RdYlGn_r')
            fig.update_layout(height=350, showlegend=False)
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
    st.plotly_chart(fig, use_container_width=True)

    # Trend per categoria
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Distribuzione Categorie")
        cat_trend = df_filtered.groupby(['Anno', 'CatLabel']).size().reset_index(name='Count')
        fig = px.bar(cat_trend, x='Anno', y='Count', color='CatLabel',
                     title="Tesserati per Categoria")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Età Media nel Tempo")
        eta_trend = df_filtered.groupby('Anno')['Anni'].mean().reset_index()
        fig = px.line(eta_trend, x='Anno', y='Anni', markers=True,
                      title="Evoluzione Età Media")
        fig.add_hline(y=70, line_dash="dash", line_color="red",
                      annotation_text="Soglia critica")
        st.plotly_chart(fig, use_container_width=True)

    # Gare medie
    st.subheader("Partecipazione Gare")
    gare_trend = df_filtered.groupby('Anno')['GareGiocate'].mean().reset_index()
    fig = px.bar(gare_trend, x='Anno', y='GareGiocate',
                 title="Gare Medie per Anno", color='GareGiocate',
                 color_continuous_scale='Viridis')
    st.plotly_chart(fig, use_container_width=True)

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
        fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
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

    # Usa dati già filtrati dalla sidebar + filtro anno e punti > 0
    df_anno = df_filtered[(df_filtered['Anno'] == anno_mappa) & (df_filtered['PuntiCampionati'] > 0)]

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

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🏆 Top 15 Associazioni Virtuose")
        associazioni_v = data['associazioni_v'].head(15)
        fig = px.bar(associazioni_v, x='TassoSuccesso', y='NomeCircolo',
                     orientation='h', color='TassoSuccesso',
                     color_continuous_scale='Greens',
                     hover_data=['Regione', 'AllievoSB'],
                     labels={'NomeCircolo': 'Associazione'})
        fig.update_layout(height=500, yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("⚠️ Top 15 Associazioni Critiche")
        associazioni_c = data['associazioni_c'].head(15)
        fig = px.bar(associazioni_c, x='TassoChurn', y='NomeCircolo',
                     orientation='h', color='TassoChurn',
                     color_continuous_scale='Reds',
                     hover_data=['Regione', 'AllievoSB'],
                     labels={'NomeCircolo': 'Associazione'})
        fig.update_layout(height=500, yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig, use_container_width=True)

    # Analisi associazioni con filtri
    st.markdown("---")
    st.subheader("🔍 Esplora Associazioni")

    col_assoc = 'Associazione' if 'Associazione' in df_filtered.columns else 'GrpName'
    associazioni_df = df_filtered.groupby([col_assoc, 'GrpArea']).agg({
        'MmbCode': 'nunique',
        'GareGiocate': 'mean',
        'Anni': 'mean'
    }).reset_index()
    associazioni_df.columns = ['Associazione', 'Regione', 'Tesserati', 'Gare Medie', 'Età Media']
    associazioni_df = associazioni_df.sort_values('Tesserati', ascending=False)

    # Filtro per nome associazione
    search = st.text_input("🔍 Cerca associazione:", "")
    if search:
        associazioni_df = associazioni_df[associazioni_df['Associazione'].str.contains(search, case=False)]

    st.dataframe(associazioni_df.head(50), use_container_width=True)

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
        st.plotly_chart(fig, use_container_width=True)

        # Evoluzione età
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("👴 Evoluzione Età Media")
            fig = px.line(proiezioni, x='Anno', y='EtaMedia', markers=True)
            fig.add_hline(y=70, line_dash="dash", line_color="red",
                         annotation_text="Soglia critica")
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.subheader("📊 Nuovi vs Usciti per Anno")
            fig = go.Figure()
            fig.add_trace(go.Bar(x=proiezioni['Anno'], y=proiezioni['Nuovi'],
                                name='Nuovi', marker_color='#28A745'))
            fig.add_trace(go.Bar(x=proiezioni['Anno'], y=proiezioni['Usciti'],
                                name='Usciti', marker_color='#DC3545'))
            fig.update_layout(barmode='group')
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
                        st.plotly_chart(fig, use_container_width=True)

                    with col2:
                        fig = px.bar(player_data.sort_values('Anno'),
                                    x='Anno', y='PuntiTotali',
                                    title=f"Punti per anno - {selected}")
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
