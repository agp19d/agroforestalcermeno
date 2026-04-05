"""Financial calculation engine for coffee production scenarios.

All monetary results are in US dollars; all weights are in pounds (lbs).
The single public entry point is :func:`calculate`, which takes a flat
dictionary of inputs and returns a :class:`FinancialResults` dataclass.
"""

from __future__ import annotations

from dataclasses import dataclass, fields
from typing import Any


# ── Result Data Structure ────────────────────────────────────────────────────

@dataclass(frozen=True)
class FinancialResults:
    """Immutable container for every computed financial metric.

    Attributes are grouped into four categories:

    * **Production** — physical output in lbs at each stage.
    * **Revenue** — income by product type and total.
    * **Costs** — itemised cost lines and total.
    * **Profitability** — derived margins, per-unit costs, break-even.
    """

    # Production (lbs)
    total_cherry: float
    total_green: float
    green_sold_lbs: float
    processed_lbs: float
    roasted_input_lbs: float
    roasted_output_lbs: float

    # Revenue ($)
    rev_green: float
    rev_processed: float
    rev_roasted: float
    total_revenue: float

    # Costs ($)
    permanent_labor: float
    seasonal_labor: float
    labor_benefits: float
    total_labor: float
    inputs_materials: float
    processing_cost: float
    roasting_cost: float
    packaging_cost: float
    land_cost: float
    overhead: float
    contingency: float
    total_costs: float

    # Profitability
    gross_profit: float
    taxes: float
    net_profit: float
    margin: float
    cost_per_lb_green: float
    rev_per_ha: float
    profit_per_ha: float
    breakeven: float

    def as_dict(self) -> dict[str, float]:
        """Return all fields as a plain dictionary."""
        return {f.name: getattr(self, f.name) for f in fields(self)}


# ── Helpers ──────────────────────────────────────────────────────────────────

def _get(inputs: dict[str, Any], key: str, default: float = 0.0) -> float:
    """Retrieve a numeric input, coercing to *float*.

    Args:
        inputs: Raw input dictionary (keys may or may not carry the
            ``in_`` prefix used by Streamlit widget keys).
        key: Logical key name **without** the ``in_`` prefix.
        default: Fallback when the key is missing.

    Returns:
        The value as a Python float.
    """
    return float(inputs.get(f"in_{key}", inputs.get(key, default)))


# ── Public API ───────────────────────────────────────────────────────────────

def calculate(inputs: dict[str, Any]) -> FinancialResults:
    """Run the full financial model and return computed results.

    The function is **pure** — it has no side-effects and depends only on
    the values in *inputs*.

    Args:
        inputs: Dictionary of scenario parameters.  Keys may optionally
            carry the ``in_`` prefix (as stored by Streamlit session
            state).  See :pymod:`config` for the canonical key names and
            their defaults.

    Returns:
        A :class:`FinancialResults` instance with every metric populated.
    """
    # ── Production ───────────────────────────────────────────────────────
    productive_ha = _get(inputs, "productive_hectares")
    cherry_per_ha = _get(inputs, "cherry_yield_per_ha")
    cherry_to_green = _get(inputs, "cherry_to_green") / 100.0
    green_to_roasted = _get(inputs, "green_to_roasted") / 100.0

    total_cherry: float = productive_ha * cherry_per_ha
    total_green: float = total_cherry * cherry_to_green

    pct_green = _get(inputs, "pct_green") / 100.0
    pct_processed = _get(inputs, "pct_processed") / 100.0
    pct_roasted = _get(inputs, "pct_roasted") / 100.0

    green_sold_lbs: float = total_green * pct_green
    processed_lbs: float = total_green * pct_processed
    roasted_input_lbs: float = total_green * pct_roasted
    roasted_output_lbs: float = roasted_input_lbs * green_to_roasted

    # ── Revenue ──────────────────────────────────────────────────────────
    rev_green: float = green_sold_lbs * _get(inputs, "price_green")
    rev_processed: float = processed_lbs * _get(inputs, "price_processed")
    rev_roasted: float = roasted_output_lbs * _get(inputs, "price_roasted")
    total_revenue: float = rev_green + rev_processed + rev_roasted

    # ── Costs ────────────────────────────────────────────────────────────
    permanent_labor: float = (
        _get(inputs, "permanent_workers")
        * _get(inputs, "monthly_wage")
        * 12
    )
    seasonal_labor: float = (
        _get(inputs, "seasonal_workers")
        * _get(inputs, "seasonal_daily_wage")
        * _get(inputs, "harvest_days")
    )
    base_labor: float = permanent_labor + seasonal_labor
    labor_benefits: float = base_labor * _get(inputs, "labor_benefits") / 100.0
    total_labor: float = base_labor + labor_benefits

    inputs_materials: float = sum(
        _get(inputs, k)
        for k in ("fertilizer", "pesticide", "seedlings", "water", "tools", "fuel")
    )

    processing_cost: float = (
        (processed_lbs + roasted_input_lbs) * _get(inputs, "processing_cost_lb")
    )
    roasting_cost: float = roasted_output_lbs * _get(inputs, "roasting_cost_lb")
    packaging_cost: float = (
        (processed_lbs + roasted_output_lbs) * _get(inputs, "packaging_cost_lb")
    )

    land_cost: float = _get(inputs, "land_cost")

    overhead: float = sum(
        _get(inputs, k)
        for k in (
            "transport", "certification", "admin", "insurance",
            "maintenance", "marketing", "loan_interest", "depreciation",
        )
    )

    subtotal_costs: float = (
        total_labor + inputs_materials + processing_cost + roasting_cost
        + packaging_cost + land_cost + overhead
    )
    contingency_amt: float = subtotal_costs * _get(inputs, "contingency") / 100.0
    total_costs: float = subtotal_costs + contingency_amt

    # ── Profitability ────────────────────────────────────────────────────
    gross_profit: float = total_revenue - total_costs
    taxes: float = max(0.0, gross_profit * _get(inputs, "tax_rate") / 100.0)
    net_profit: float = gross_profit - taxes
    margin: float = (net_profit / total_revenue * 100.0) if total_revenue else 0.0
    cost_per_lb_green: float = (total_costs / total_green) if total_green else 0.0
    rev_per_ha: float = (total_revenue / productive_ha) if productive_ha else 0.0
    profit_per_ha: float = (net_profit / productive_ha) if productive_ha else 0.0
    breakeven: float = cost_per_lb_green

    return FinancialResults(
        total_cherry=total_cherry,
        total_green=total_green,
        green_sold_lbs=green_sold_lbs,
        processed_lbs=processed_lbs,
        roasted_input_lbs=roasted_input_lbs,
        roasted_output_lbs=roasted_output_lbs,
        rev_green=rev_green,
        rev_processed=rev_processed,
        rev_roasted=rev_roasted,
        total_revenue=total_revenue,
        permanent_labor=permanent_labor,
        seasonal_labor=seasonal_labor,
        labor_benefits=labor_benefits,
        total_labor=total_labor,
        inputs_materials=inputs_materials,
        processing_cost=processing_cost,
        roasting_cost=roasting_cost,
        packaging_cost=packaging_cost,
        land_cost=land_cost,
        overhead=overhead,
        contingency=contingency_amt,
        total_costs=total_costs,
        gross_profit=gross_profit,
        taxes=taxes,
        net_profit=net_profit,
        margin=margin,
        cost_per_lb_green=cost_per_lb_green,
        rev_per_ha=rev_per_ha,
        profit_per_ha=profit_per_ha,
        breakeven=breakeven,
    )
