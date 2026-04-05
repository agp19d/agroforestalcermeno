# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Streamlit web app for Agroforestal Cermeño — a coffee production financial planner for a Panamanian farm. All UI text is in Spanish (Panama). All monetary values are in **Balboas panameños (B/.)**, all weights in **pounds (lbs)**.

## Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run app.py
```

There are no tests, linter, or build steps configured.

## Architecture

The app follows a clear data-flow pipeline: **sidebar inputs → calculation engine → dashboard output**.

- **`app.py`** — Entry point. Wires sidebar → `calculate()` → dashboard. No logic lives here.
- **`config.py`** — Single source of truth for all default input values (`DEFAULT_INPUTS` dict), color palette constants, and the scenarios filename.
- **`models.py`** — Pure financial calculation engine. `calculate(inputs) → FinancialResults` (frozen dataclass). No side effects. Input keys can optionally carry the `in_` prefix from Streamlit session state; the `_get()` helper resolves both forms.
- **`simulation.py`** — Monte Carlo engine. `run_simulation()` samples uncertain variables from triangular distributions, runs `calculate()` N times, returns `SimulationResults` with NumPy arrays and a summary DataFrame.
- **`scenarios.py`** — JSON file persistence for named scenarios (save/load/delete). Stores to `scenarios.json` next to the app (gitignored).
- **`formatting.py`** — Pure formatting helpers: `fmt_currency()` (B/. prefix), `fmt_percent()`, `fmt_number()`.
- **`ui/sidebar.py`** — Renders all Streamlit sidebar input widgets. Widget keys use `in_` prefix (e.g., `in_price_green`). Returns collected inputs dict.
- **`ui/dashboard.py`** — Main area with 6 tabs: Producción, Ingresos, Costos, Rentabilidad, Comparar Escenarios, Monte Carlo. Uses Plotly for all charts.
- **`ui/montecarlo.py`** — Self-contained Monte Carlo tab: variable range configuration, simulation execution, and result visualization (histograms, CDF, risk metrics, summary table).

## Key Conventions

- Input dict keys use `in_` prefix in Streamlit session state (e.g., `in_cherry_yield_per_ha`), but `config.DEFAULT_INPUTS` uses bare keys. The `_get()` helper in `models.py` transparently handles both.
- Production allocation percentages (`pct_green`, `pct_processed`, `pct_roasted`) must sum to 100%.
- The `FinancialResults` dataclass is frozen/immutable — all fields are computed in `calculate()`.
- Charts use the `COLOURS_GREEN` palette (`#2d6a4f`, `#40916c`, `#74c69d`) for bean-type breakdowns and `COLOUR_POSITIVE`/`COLOUR_NEGATIVE`/`COLOUR_TOTAL` for waterfall charts.
