# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a data analysis project for FIGB (Federazione Italiana Gioco Bridge) membership data from 2017-2024. It consists of two main components:

1. **Python analysis scripts** - Data processing, statistical analysis, and chart generation
2. **React dashboard** - Interactive web visualization of the analysis results

## Data Source

- Primary data: Excel file with yearly sheets (2017-2024) containing member registration data
- Key fields: `MmbCode` (member ID), `Anno` (year), `GrpArea` (region), `MmbSex`, `Anni` (age), `CatLabel` (category), `MbtDesc` (membership type), `GareGiocate` (games played), `PuntiCampionati`, `PuntiTotali`

## Python Analysis Scripts

Located in `Script/`, these scripts expect data at `/home/ubuntu/bridge_analysis/` (designed for server deployment):

- `data_exploration.py` - Initial data loading from Excel, creates unified CSV
- `statistical_analysis.py` - Core analysis: temporal, regional, demographic, retention rates
- `advanced_statistics.py` - Extended metrics (100+): activity levels, point distributions, churn
- `create_visualizations.py` - Generates PNG charts using matplotlib/seaborn

### Running Python Scripts

```bash
python Script/data_exploration.py      # Run first to create unified dataset
python Script/statistical_analysis.py  # Core statistical analysis
python Script/advanced_statistics.py   # Extended metrics
python Script/create_visualizations.py # Generate charts
```

**Dependencies**: pandas, numpy, matplotlib, seaborn

## React Dashboard

The TSX files in `Script/` are components for a React dashboard using:
- wouter for routing
- shadcn/ui components (`@/components/ui/`)
- Tailwind CSS with custom theme (index.css)
- lucide-react for icons

### Dashboard Pages

| Route | Component | Description |
|-------|-----------|-------------|
| `/` | Overview.tsx | Summary KPIs and main insights |
| `/temporale` | Temporale.tsx | Year-over-year trends |
| `/regionale` | Regionale.tsx | Geographic distribution |
| `/demografia` | Demografia.tsx | Age/sex demographics |
| `/categorie` | Categorie.tsx | Player categories |
| `/retention` | Retention.tsx | Re-registration rates |
| `/churn` | Churn.tsx | Lost members analysis |
| `/tessere` | Tessere.tsx | Membership types |
| `/statistiche` | Statistiche.tsx | Advanced statistics |

### Dashboard Architecture

- `App.tsx` - Root component with routing and providers
- `DashboardLayout.tsx` - Sidebar navigation with responsive mobile menu
- Pages fetch JSON/CSV results and display static chart images from Python scripts

## Key Analysis Concepts

- **Retention Rate**: Percentage of members who renew their registration year-over-year
- **Churn**: Members who don't renew, analyzed by age bracket and membership type
- **FasciaEta**: Age brackets (<18, 18-30, 30-40, ..., 90+)
- **FasciaPunti**: Point brackets for activity level classification

## Italian Terminology

The codebase uses Italian for domain-specific terms:
- Tesserati = registered members
- Ritesserati = renewed members
- Gare = games/competitions
- Circoli = clubs
- Regioni = regions
