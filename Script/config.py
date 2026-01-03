#!/usr/bin/env python3
"""
Configurazione centralizzata per tutti gli script di analisi FIGB
"""

from pathlib import Path

# Directory base del progetto
BASE_DIR = Path(__file__).parent.parent

# Directory dei dati
DATA_DIR = BASE_DIR

# Directory output
OUTPUT_DIR = BASE_DIR / 'output'
OUTPUT_DIR.mkdir(exist_ok=True)

# Directory risultati analisi
RESULTS_DIR = OUTPUT_DIR / 'results'
RESULTS_DIR.mkdir(exist_ok=True)

# Directory grafici
CHARTS_DIR = OUTPUT_DIR / 'charts'
CHARTS_DIR.mkdir(exist_ok=True)

# File sorgente
FILE_STORICO = DATA_DIR / 'Dati dal 17.xlsx'
FILE_2025 = DATA_DIR / '2025 Dopo Natale.xlsx'

# File output
FILE_UNIFICATO_CSV = OUTPUT_DIR / 'dati_unificati_2017_2025.csv'

# Configurazione analisi
ANNI_ANALISI = list(range(2017, 2026))
ANNO_CORRENTE = 2025

# Fasce d'età
FASCE_ETA_BINS = [0, 18, 30, 40, 50, 60, 70, 80, 90, 120]
FASCE_ETA_LABELS = ['<18', '18-30', '30-40', '40-50', '50-60', '60-70', '70-80', '80-90', '90+']

# Fasce punti
FASCE_PUNTI_BINS = [-1, 0, 500, 2000, 5000, 10000, 20000, 50000, 500000]
FASCE_PUNTI_LABELS = ['0', '1-500', '501-2000', '2001-5000', '5001-10000', '10001-20000', '20001-50000', '50000+']

# Gemini API
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', '')
GEMINI_MODEL = 'gemini-2.0-flash'

def get_data_path():
    """Restituisce il percorso del file dati unificato"""
    return FILE_UNIFICATO_CSV

def get_results_path(filename):
    """Restituisce il percorso per un file di risultati"""
    return RESULTS_DIR / filename

def get_chart_path(filename):
    """Restituisce il percorso per un grafico"""
    return CHARTS_DIR / filename
