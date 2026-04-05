"""Application-wide constants and default input values.

This module centralises every tunable default so that the rest of the
codebase can import them from a single place.  All monetary values are
in US dollars and all weights are in pounds (lbs).
"""

from __future__ import annotations

from typing import Any

# ── Persistence ──────────────────────────────────────────────────────────────

SCENARIOS_FILENAME: str = "scenarios.json"
"""Name of the JSON file where saved scenarios are stored."""

# ── Default Input Values ─────────────────────────────────────────────────────
# Each key mirrors the Streamlit widget key (without the ``in_`` prefix).

DEFAULT_INPUTS: dict[str, Any] = {
    # Plantation & land
    "total_hectares": 5.0,
    "plants_per_ha": 5000,
    "productive_hectares": 4.0,
    "land_cost": 2000.0,

    # Yield estimates
    "cherry_yield_per_ha": 8000.0,
    "cherry_to_green": 20.0,       # percent
    "green_to_roasted": 82.0,      # percent

    # Production allocation (must sum to 100)
    "pct_green": 40.0,
    "pct_processed": 30.0,
    "pct_roasted": 30.0,

    # Labour
    "permanent_workers": 3,
    "monthly_wage": 400.0,
    "seasonal_workers": 10,
    "seasonal_daily_wage": 15.0,
    "harvest_days": 60,
    "labor_benefits": 30.0,        # percent

    # Inputs & materials (annual)
    "fertilizer": 3000.0,
    "pesticide": 1500.0,
    "seedlings": 500.0,
    "water": 1200.0,
    "tools": 800.0,
    "fuel": 1000.0,

    # Processing & roasting (per-lb)
    "processing_cost_lb": 0.50,
    "roasting_cost_lb": 1.50,
    "packaging_cost_lb": 0.75,

    # Overhead & fixed (annual)
    "transport": 2000.0,
    "certification": 1500.0,
    "admin": 1200.0,
    "insurance": 800.0,
    "maintenance": 600.0,
    "marketing": 500.0,
    "loan_interest": 0.0,
    "depreciation": 1000.0,
    "tax_rate": 15.0,              # percent
    "contingency": 5.0,            # percent

    # Sales prices (per-lb)
    "price_green": 2.50,
    "price_processed": 4.00,
    "price_roasted": 8.00,
}

# ── Chart Colour Palette ─────────────────────────────────────────────────────

COLOURS_GREEN: list[str] = ["#2d6a4f", "#40916c", "#74c69d"]
"""Three-shade green palette used for bean-type charts."""

COLOUR_POSITIVE: str = "#2d6a4f"
COLOUR_NEGATIVE: str = "#d62828"
COLOUR_TOTAL: str = "#1d3557"
