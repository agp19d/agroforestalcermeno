"""Monte Carlo simulation engine for coffee production scenarios.

Runs *N* iterations of the financial model, sampling each uncertain
input from a user-defined probability distribution (triangular by
default).  Returns a :class:`SimulationResults` object that holds
per-metric arrays and pre-computed summary statistics.
"""

from __future__ import annotations

from dataclasses import dataclass, fields
from typing import Any

import numpy as np
import pandas as pd

from models import FinancialResults, calculate


# ── Configuration ────────────────────────────────────────────────────────────

@dataclass
class VariableRange:
    """Defines the uncertainty range for a single input variable.

    The triangular distribution is parameterised by *low*, *base*
    (mode), and *high*.  If the variable is not marked *enabled*, it
    will be held constant at its *base* value during simulation.

    Attributes:
        key: The input key name (without the ``in_`` prefix).
        label: Human-readable label for the UI.
        low: Optimistic / minimum bound.
        base: Most-likely value (mode of the triangle).
        high: Pessimistic / maximum bound.
        enabled: Whether this variable should be sampled.
    """

    key: str
    label: str
    low: float
    base: float
    high: float
    enabled: bool = True


# The subset of inputs most commonly subject to uncertainty.
DEFAULT_VARIABLE_KEYS: list[dict[str, str]] = [
    {"key": "cherry_yield_per_ha", "label": "Cherry Yield (lbs/ha)"},
    {"key": "cherry_to_green", "label": "Cherry to Green Ratio (%)"},
    {"key": "price_green", "label": "Green Coffee Price ($/lb)"},
    {"key": "price_processed", "label": "Processed Coffee Price ($/lb)"},
    {"key": "price_roasted", "label": "Roasted Coffee Price ($/lb)"},
    {"key": "fertilizer", "label": "Fertilizer Cost ($)"},
    {"key": "pesticide", "label": "Pest & Disease Control ($)"},
    {"key": "seasonal_workers", "label": "Seasonal Workers"},
    {"key": "seasonal_daily_wage", "label": "Seasonal Daily Wage ($)"},
    {"key": "harvest_days", "label": "Harvest Days"},
    {"key": "processing_cost_lb", "label": "Processing Cost ($/lb)"},
    {"key": "roasting_cost_lb", "label": "Roasting Cost ($/lb)"},
    {"key": "fuel", "label": "Fuel & Energy ($)"},
    {"key": "transport", "label": "Transport & Logistics ($)"},
]


def build_default_ranges(
    base_inputs: dict[str, Any],
    spread: float = 0.20,
) -> list[VariableRange]:
    """Create default :class:`VariableRange` objects from current inputs.

    Each variable gets a symmetric spread of +/- *spread* (default 20 %)
    around its base value.

    Args:
        base_inputs: Current scenario input dictionary (keys may have
            the ``in_`` prefix).
        spread: Fractional spread applied symmetrically (0.20 = 20 %).

    Returns:
        A list of :class:`VariableRange` instances for every key in
        :data:`DEFAULT_VARIABLE_KEYS`.
    """
    ranges: list[VariableRange] = []
    for spec in DEFAULT_VARIABLE_KEYS:
        key = spec["key"]
        base_val = float(
            base_inputs.get(f"in_{key}", base_inputs.get(key, 0))
        )
        low = base_val * (1.0 - spread)
        high = base_val * (1.0 + spread)
        ranges.append(VariableRange(
            key=key,
            label=spec["label"],
            low=round(low, 4),
            base=round(base_val, 4),
            high=round(high, 4),
            enabled=True,
        ))
    return ranges


# ── Simulation Results ───────────────────────────────────────────────────────

# Metrics we track across iterations.
TRACKED_METRICS: list[str] = [
    "total_revenue",
    "total_costs",
    "net_profit",
    "margin",
    "cost_per_lb_green",
    "breakeven",
    "total_green",
    "roasted_output_lbs",
    "rev_per_ha",
    "profit_per_ha",
]

METRIC_LABELS: dict[str, str] = {
    "total_revenue": "Total Revenue ($)",
    "total_costs": "Total Costs ($)",
    "net_profit": "Net Profit ($)",
    "margin": "Profit Margin (%)",
    "cost_per_lb_green": "Cost per lb Green ($)",
    "breakeven": "Break-even Price ($/lb)",
    "total_green": "Total Green Coffee (lbs)",
    "roasted_output_lbs": "Roasted Output (lbs)",
    "rev_per_ha": "Revenue per Hectare ($)",
    "profit_per_ha": "Profit per Hectare ($)",
}


@dataclass
class SimulationResults:
    """Container for Monte Carlo simulation output.

    Attributes:
        n_iterations: Number of iterations that were run.
        metric_arrays: Mapping of metric name → 1-D NumPy array of
            length *n_iterations*.
        summary_df: Pre-computed DataFrame with mean, std, and
            percentile columns for every tracked metric.
    """

    n_iterations: int
    metric_arrays: dict[str, np.ndarray]
    summary_df: pd.DataFrame


# ── Engine ───────────────────────────────────────────────────────────────────

def run_simulation(
    base_inputs: dict[str, Any],
    variable_ranges: list[VariableRange],
    n_iterations: int = 5000,
    seed: int | None = None,
) -> SimulationResults:
    """Execute the Monte Carlo simulation.

    For each iteration, every *enabled* :class:`VariableRange` is
    sampled from a triangular distribution.  The sampled values replace
    the corresponding base inputs, and the full financial model is
    evaluated via :func:`models.calculate`.

    Args:
        base_inputs: The deterministic scenario inputs (used as the
            starting point for each iteration).
        variable_ranges: List of uncertain variables with their
            distribution parameters.
        n_iterations: How many iterations to run (default 5 000).
        seed: Optional RNG seed for reproducibility.

    Returns:
        A :class:`SimulationResults` instance.
    """
    rng = np.random.default_rng(seed)

    # Pre-allocate result arrays.
    arrays: dict[str, np.ndarray] = {
        m: np.empty(n_iterations, dtype=np.float64) for m in TRACKED_METRICS
    }

    # Filter to only enabled ranges.
    active_ranges = [vr for vr in variable_ranges if vr.enabled]

    for i in range(n_iterations):
        # Start from a copy of the base inputs.
        sampled = dict(base_inputs)

        # Sample each uncertain variable.
        for vr in active_ranges:
            # Ensure low <= mode <= high for the triangular distribution.
            low = min(vr.low, vr.base)
            high = max(vr.high, vr.base)
            mode = vr.base
            # Clamp mode within [low, high] to satisfy numpy.
            mode = max(low, min(mode, high))
            if low == high:
                value = low
            else:
                value = rng.triangular(low, mode, high)
            sampled[f"in_{vr.key}"] = value

        # Run the financial model.
        result: FinancialResults = calculate(sampled)

        # Store tracked metrics.
        result_dict = result.as_dict()
        for metric in TRACKED_METRICS:
            arrays[metric][i] = result_dict[metric]

    # Build summary statistics.
    summary_rows: list[dict[str, Any]] = []
    for metric in TRACKED_METRICS:
        arr = arrays[metric]
        summary_rows.append({
            "Metric": METRIC_LABELS.get(metric, metric),
            "Mean": np.mean(arr),
            "Std Dev": np.std(arr),
            "5th Pctl": np.percentile(arr, 5),
            "25th Pctl": np.percentile(arr, 25),
            "Median": np.percentile(arr, 50),
            "75th Pctl": np.percentile(arr, 75),
            "95th Pctl": np.percentile(arr, 95),
            "P(< 0)": np.mean(arr < 0) * 100,
        })

    summary_df = pd.DataFrame(summary_rows)

    return SimulationResults(
        n_iterations=n_iterations,
        metric_arrays=arrays,
        summary_df=summary_df,
    )
