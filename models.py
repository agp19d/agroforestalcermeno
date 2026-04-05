"""Motor de cálculo financiero para producción de café.

Modelo: Cereza → venta directa o procesamiento (honey / natural / pilado).
Todos los valores monetarios en Balboas panameños (B/.), pesos en libras.
"""

from __future__ import annotations

from dataclasses import dataclass, fields
from typing import Any


@dataclass(frozen=True)
class FinancialResults:
    """Resultados inmutables del modelo financiero."""

    # Producción (lbs)
    total_cherry: float
    cherry_sold_lbs: float
    cherry_to_honey_lbs: float
    cherry_to_natural_lbs: float
    cherry_to_pilado_lbs: float
    honey_output_lbs: float
    natural_output_lbs: float
    pilado_output_lbs: float

    # Ingresos (B/.)
    rev_cereza: float
    rev_honey: float
    rev_natural: float
    rev_pilado: float
    total_revenue: float

    # Costos (B/.)
    permanent_labor: float
    seasonal_labor: float
    labor_benefits: float
    total_labor: float
    inputs_materials: float
    processing_honey: float
    processing_natural: float
    processing_pilado: float
    total_processing: float
    packaging_cost: float
    land_cost: float
    overhead: float
    contingency: float
    total_costs: float

    # Rentabilidad
    gross_profit: float
    taxes: float
    net_profit: float
    margin: float
    cost_per_lb_cherry: float
    rev_per_ha: float
    profit_per_ha: float

    def as_dict(self) -> dict[str, float]:
        return {f.name: getattr(self, f.name) for f in fields(self)}


def _get(inputs: dict[str, Any], key: str, default: float = 0.0) -> float:
    """Obtiene valor numérico, soportando prefijo ``in_``."""
    return float(inputs.get(f"in_{key}", inputs.get(key, default)))


def calculate(inputs: dict[str, Any]) -> FinancialResults:
    """Ejecuta el modelo financiero completo.

    Puro, sin efectos secundarios.
    """
    # ── Producción ───────────────────────────────────────────────────────
    productive_ha = _get(inputs, "productive_hectares")
    cherry_per_ha = _get(inputs, "cherry_yield_per_ha")
    total_cherry = productive_ha * cherry_per_ha

    pct_cereza = _get(inputs, "pct_cereza") / 100.0
    pct_honey = _get(inputs, "pct_honey") / 100.0
    pct_natural = _get(inputs, "pct_natural") / 100.0
    pct_pilado = _get(inputs, "pct_pilado") / 100.0

    cherry_sold_lbs = total_cherry * pct_cereza
    cherry_to_honey = total_cherry * pct_honey
    cherry_to_natural = total_cherry * pct_natural
    cherry_to_pilado = total_cherry * pct_pilado

    ratio_honey = _get(inputs, "ratio_honey") / 100.0
    ratio_natural = _get(inputs, "ratio_natural") / 100.0
    ratio_pilado = _get(inputs, "ratio_pilado") / 100.0

    honey_output = cherry_to_honey * ratio_honey
    natural_output = cherry_to_natural * ratio_natural
    pilado_output = cherry_to_pilado * ratio_pilado

    # ── Ingresos ─────────────────────────────────────────────────────────
    rev_cereza = cherry_sold_lbs * _get(inputs, "price_cereza")
    rev_honey = honey_output * _get(inputs, "price_honey")
    rev_natural = natural_output * _get(inputs, "price_natural")
    rev_pilado = pilado_output * _get(inputs, "price_pilado")
    total_revenue = rev_cereza + rev_honey + rev_natural + rev_pilado

    # ── Costos ───────────────────────────────────────────────────────────
    permanent_labor = _get(inputs, "permanent_workers") * _get(inputs, "monthly_wage") * 12
    seasonal_labor = (
        _get(inputs, "seasonal_workers")
        * _get(inputs, "seasonal_daily_wage")
        * _get(inputs, "harvest_days")
    )
    base_labor = permanent_labor + seasonal_labor
    labor_benefits = base_labor * _get(inputs, "labor_benefits") / 100.0
    total_labor = base_labor + labor_benefits

    inputs_materials = sum(
        _get(inputs, k)
        for k in ("fertilizer", "pesticide", "seedlings", "water", "tools", "fuel")
    )

    # Costos de procesamiento: por lb de cereza que entra al proceso
    processing_honey = cherry_to_honey * _get(inputs, "cost_honey_lb")
    processing_natural = cherry_to_natural * _get(inputs, "cost_natural_lb")
    processing_pilado = cherry_to_pilado * _get(inputs, "cost_pilado_lb")
    total_processing = processing_honey + processing_natural + processing_pilado

    # Empaque: por lb de producto terminado (solo procesados, no cereza)
    total_packaged_lbs = honey_output + natural_output + pilado_output
    packaging_cost = total_packaged_lbs * _get(inputs, "cost_packaging_lb")

    land_cost = _get(inputs, "land_cost")

    overhead = sum(
        _get(inputs, k)
        for k in (
            "transport", "certification", "admin", "insurance",
            "maintenance", "marketing", "loan_interest", "depreciation",
        )
    )

    subtotal = total_labor + inputs_materials + total_processing + packaging_cost + land_cost + overhead
    contingency_amt = subtotal * _get(inputs, "contingency") / 100.0
    total_costs = subtotal + contingency_amt

    # ── Rentabilidad ─────────────────────────────────────────────────────
    gross_profit = total_revenue - total_costs
    taxes = max(0.0, gross_profit * _get(inputs, "tax_rate") / 100.0)
    net_profit = gross_profit - taxes
    margin = (net_profit / total_revenue * 100.0) if total_revenue else 0.0
    cost_per_lb_cherry = (total_costs / total_cherry) if total_cherry else 0.0
    rev_per_ha = (total_revenue / productive_ha) if productive_ha else 0.0
    profit_per_ha = (net_profit / productive_ha) if productive_ha else 0.0

    return FinancialResults(
        total_cherry=total_cherry,
        cherry_sold_lbs=cherry_sold_lbs,
        cherry_to_honey_lbs=cherry_to_honey,
        cherry_to_natural_lbs=cherry_to_natural,
        cherry_to_pilado_lbs=cherry_to_pilado,
        honey_output_lbs=honey_output,
        natural_output_lbs=natural_output,
        pilado_output_lbs=pilado_output,
        rev_cereza=rev_cereza,
        rev_honey=rev_honey,
        rev_natural=rev_natural,
        rev_pilado=rev_pilado,
        total_revenue=total_revenue,
        permanent_labor=permanent_labor,
        seasonal_labor=seasonal_labor,
        labor_benefits=labor_benefits,
        total_labor=total_labor,
        inputs_materials=inputs_materials,
        processing_honey=processing_honey,
        processing_natural=processing_natural,
        processing_pilado=processing_pilado,
        total_processing=total_processing,
        packaging_cost=packaging_cost,
        land_cost=land_cost,
        overhead=overhead,
        contingency=contingency_amt,
        total_costs=total_costs,
        gross_profit=gross_profit,
        taxes=taxes,
        net_profit=net_profit,
        margin=margin,
        cost_per_lb_cherry=cost_per_lb_cherry,
        rev_per_ha=rev_per_ha,
        profit_per_ha=profit_per_ha,
    )
