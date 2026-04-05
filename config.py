"""Constantes y valores predeterminados de la aplicación.

Este módulo centraliza todos los valores por defecto configurables
para que el resto del código los importe desde un solo lugar.
Todos los valores monetarios están en Balboas panameños (B/.) y
todos los pesos en libras (lbs).
"""

from __future__ import annotations

from typing import Any

# ── Persistencia ─────────────────────────────────────────────────────────────

SCENARIOS_FILENAME: str = "scenarios.json"
"""Nombre del archivo JSON donde se guardan los escenarios."""

# ── Valores de Entrada Predeterminados ───────────────────────────────────────
# Cada clave corresponde al widget de Streamlit (sin el prefijo ``in_``).

DEFAULT_INPUTS: dict[str, Any] = {
    # Finca y terreno
    "total_hectares": 5.0,
    "plants_per_ha": 5000,
    "productive_hectares": 4.0,
    "land_cost": 2000.0,

    # Estimaciones de rendimiento
    "cherry_yield_per_ha": 8000.0,
    "cherry_to_green": 20.0,       # porcentaje
    "green_to_roasted": 82.0,      # porcentaje

    # Asignación de producción (debe sumar 100)
    "pct_green": 40.0,
    "pct_processed": 30.0,
    "pct_roasted": 30.0,

    # Mano de obra
    "permanent_workers": 3,
    "monthly_wage": 400.0,
    "seasonal_workers": 10,
    "seasonal_daily_wage": 15.0,
    "harvest_days": 60,
    "labor_benefits": 30.0,        # porcentaje

    # Insumos y materiales (anual)
    "fertilizer": 3000.0,
    "pesticide": 1500.0,
    "seedlings": 500.0,
    "water": 1200.0,
    "tools": 800.0,
    "fuel": 1000.0,

    # Procesamiento y tueste (por libra)
    "processing_cost_lb": 0.50,
    "roasting_cost_lb": 1.50,
    "packaging_cost_lb": 0.75,

    # Gastos generales y fijos (anual)
    "transport": 2000.0,
    "certification": 1500.0,
    "admin": 1200.0,
    "insurance": 800.0,
    "maintenance": 600.0,
    "marketing": 500.0,
    "loan_interest": 0.0,
    "depreciation": 1000.0,
    "tax_rate": 15.0,              # porcentaje
    "contingency": 5.0,            # porcentaje

    # Precios de venta (por libra)
    "price_green": 2.50,
    "price_processed": 4.00,
    "price_roasted": 8.00,
}

# ── Paleta de Colores para Gráficos ─────────────────────────────────────────

COLOURS_GREEN: list[str] = ["#2d6a4f", "#40916c", "#74c69d"]
"""Paleta de tres tonos verdes para gráficos por tipo de grano."""

COLOUR_POSITIVE: str = "#2d6a4f"
COLOUR_NEGATIVE: str = "#d62828"
COLOUR_TOTAL: str = "#1d3557"
