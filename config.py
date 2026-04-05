"""Constantes y valores predeterminados de la aplicación.

Este módulo centraliza todos los valores por defecto configurables.
Todos los valores monetarios están en Balboas panameños (B/.) y
todos los pesos en libras (lbs).

Modelo de producción:
  Cereza (cosechada) → se vende como cereza o se procesa por 3 métodos:
    • Seco Honey   — proceso honey (secado con mucílago parcial)
    • Seco Natural  — proceso natural (secado con cereza entera)
    • Seco Pilado   — proceso lavado/pilado (despulpado y lavado)
  Cada método tiene su propio ratio de conversión, costo y precio.
"""

from __future__ import annotations

from typing import Any

# ── Persistencia ─────────────────────────────────────────────────────────────

SCENARIOS_FILENAME: str = "scenarios.json"

# ── Productos ────────────────────────────────────────────────────────────────

PRODUCTS: list[dict[str, str]] = [
    {"key": "cereza",  "label": "Cereza",       "icon": "🍒", "desc": "Grano en cereza, recién cosechado"},
    {"key": "honey",   "label": "Seco Honey",   "icon": "🍯", "desc": "Proceso honey — secado con mucílago"},
    {"key": "natural", "label": "Seco Natural",  "icon": "☀️", "desc": "Proceso natural — secado entero"},
    {"key": "pilado",  "label": "Seco Pilado",   "icon": "⚙️", "desc": "Proceso lavado — despulpado y pilado"},
]

PRODUCT_KEYS: list[str] = [p["key"] for p in PRODUCTS]
PROCESSED_KEYS: list[str] = ["honey", "natural", "pilado"]

# ── Valores de Entrada Predeterminados ───────────────────────────────────────

DEFAULT_INPUTS: dict[str, Any] = {
    # Finca y terreno
    "total_hectares": 5.0,
    "plants_per_ha": 5_000,
    "productive_hectares": 4.0,
    "land_cost": 2_000.0,

    # Rendimiento base
    "cherry_yield_per_ha": 8_000.0,  # lbs cereza / ha

    # Distribución de cereza (debe sumar 100%)
    "pct_cereza": 10.0,     # % vendida como cereza fresca
    "pct_honey": 30.0,      # % procesada como honey
    "pct_natural": 30.0,    # % procesada como natural
    "pct_pilado": 30.0,     # % procesada como pilado

    # Ratios de conversión cereza → producto (%)
    # Cuántas lbs de producto se obtienen por cada 100 lbs de cereza
    "ratio_honey": 22.0,
    "ratio_natural": 20.0,
    "ratio_pilado": 18.0,

    # Precios de venta (B/. por libra)
    "price_cereza": 0.50,
    "price_honey": 4.50,
    "price_natural": 3.80,
    "price_pilado": 5.00,

    # Mano de obra
    "permanent_workers": 3,
    "monthly_wage": 400.0,
    "seasonal_workers": 10,
    "seasonal_daily_wage": 15.0,
    "harvest_days": 60,
    "labor_benefits": 30.0,

    # Insumos y materiales (anual)
    "fertilizer": 3_000.0,
    "pesticide": 1_500.0,
    "seedlings": 500.0,
    "water": 1_200.0,
    "tools": 800.0,
    "fuel": 1_000.0,

    # Costos de procesamiento (B/. por lb de cereza procesada)
    "cost_honey_lb": 0.35,
    "cost_natural_lb": 0.25,
    "cost_pilado_lb": 0.50,

    # Empaque (B/. por lb de producto terminado)
    "cost_packaging_lb": 0.75,

    # Gastos generales y fijos (anual)
    "transport": 2_000.0,
    "certification": 1_500.0,
    "admin": 1_200.0,
    "insurance": 800.0,
    "maintenance": 600.0,
    "marketing": 500.0,
    "loan_interest": 0.0,
    "depreciation": 1_000.0,
    "tax_rate": 15.0,
    "contingency": 5.0,
}

# ── Paleta de Colores ────────────────────────────────────────────────────────

COLOURS_PRODUCT: dict[str, str] = {
    "cereza":  "#b83030",
    "honey":   "#d4a017",
    "natural": "#e07020",
    "pilado":  "#2d6a4f",
}

COLOUR_POSITIVE: str = "#2d6a4f"
COLOUR_NEGATIVE: str = "#d62828"
COLOUR_TOTAL: str = "#1d3557"
