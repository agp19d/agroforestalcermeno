"""Motor de simulación Monte Carlo para escenarios de producción de café.

Ejecuta N iteraciones del modelo financiero, muestreando cada entrada
incierta de una distribución triangular. Devuelve SimulationResults
con arreglos por métrica y estadísticas resumidas.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np
import pandas as pd

from models import FinancialResults, calculate


@dataclass
class VariableRange:
    key: str
    label: str
    low: float
    base: float
    high: float
    enabled: bool = True


DEFAULT_VARIABLE_KEYS: list[dict[str, str]] = [
    {"key": "cherry_yield_per_ha", "label": "Rendimiento de Cereza (lbs/ha)"},
    {"key": "ratio_honey", "label": "Ratio Cereza → Honey (%)"},
    {"key": "ratio_natural", "label": "Ratio Cereza → Natural (%)"},
    {"key": "ratio_pilado", "label": "Ratio Cereza → Pilado (%)"},
    {"key": "price_cereza", "label": "Precio Cereza (B/./lb)"},
    {"key": "price_honey", "label": "Precio Seco Honey (B/./lb)"},
    {"key": "price_natural", "label": "Precio Seco Natural (B/./lb)"},
    {"key": "price_pilado", "label": "Precio Seco Pilado (B/./lb)"},
    {"key": "fertilizer", "label": "Costo de Fertilizante (B/.)"},
    {"key": "pesticide", "label": "Control de Plagas (B/.)"},
    {"key": "seasonal_workers", "label": "Trabajadores Temporales"},
    {"key": "seasonal_daily_wage", "label": "Jornal Diario Temporal (B/.)"},
    {"key": "harvest_days", "label": "Días de Cosecha"},
    {"key": "cost_honey_lb", "label": "Costo Proceso Honey (B/./lb)"},
    {"key": "cost_natural_lb", "label": "Costo Proceso Natural (B/./lb)"},
    {"key": "cost_pilado_lb", "label": "Costo Proceso Pilado (B/./lb)"},
    {"key": "fuel", "label": "Combustible y Energía (B/.)"},
    {"key": "transport", "label": "Transporte y Logística (B/.)"},
]


def build_default_ranges(
    base_inputs: dict[str, Any],
    spread: float = 0.20,
) -> list[VariableRange]:
    ranges: list[VariableRange] = []
    for spec in DEFAULT_VARIABLE_KEYS:
        key = spec["key"]
        base_val = float(base_inputs.get(f"in_{key}", base_inputs.get(key, 0)))
        low = base_val * (1.0 - spread)
        high = base_val * (1.0 + spread)
        ranges.append(VariableRange(
            key=key, label=spec["label"],
            low=round(low, 4), base=round(base_val, 4), high=round(high, 4),
            enabled=True,
        ))
    return ranges


TRACKED_METRICS: list[str] = [
    "total_revenue",
    "total_costs",
    "net_profit",
    "margin",
    "cost_per_lb_cherry",
    "total_cherry",
    "honey_output_lbs",
    "natural_output_lbs",
    "pilado_output_lbs",
    "rev_per_ha",
    "profit_per_ha",
]

METRIC_LABELS: dict[str, str] = {
    "total_revenue": "Ingresos Totales (B/.)",
    "total_costs": "Costos Totales (B/.)",
    "net_profit": "Ganancia Neta (B/.)",
    "margin": "Margen de Ganancia (%)",
    "cost_per_lb_cherry": "Costo por lb Cereza (B/.)",
    "total_cherry": "Total Cereza (lbs)",
    "honey_output_lbs": "Producción Honey (lbs)",
    "natural_output_lbs": "Producción Natural (lbs)",
    "pilado_output_lbs": "Producción Pilado (lbs)",
    "rev_per_ha": "Ingresos por Hectárea (B/.)",
    "profit_per_ha": "Ganancia por Hectárea (B/.)",
}


@dataclass
class SimulationResults:
    n_iterations: int
    metric_arrays: dict[str, np.ndarray]
    summary_df: pd.DataFrame


def run_simulation(
    base_inputs: dict[str, Any],
    variable_ranges: list[VariableRange],
    n_iterations: int = 5000,
    seed: int | None = None,
) -> SimulationResults:
    rng = np.random.default_rng(seed)

    arrays: dict[str, np.ndarray] = {
        m: np.empty(n_iterations, dtype=np.float64) for m in TRACKED_METRICS
    }

    active_ranges = [vr for vr in variable_ranges if vr.enabled]

    for i in range(n_iterations):
        sampled = dict(base_inputs)

        for vr in active_ranges:
            low = min(vr.low, vr.base)
            high = max(vr.high, vr.base)
            mode = max(low, min(vr.base, high))
            if low == high:
                value = low
            else:
                value = rng.triangular(low, mode, high)
            sampled[f"in_{vr.key}"] = value

        result: FinancialResults = calculate(sampled)
        result_dict = result.as_dict()
        for metric in TRACKED_METRICS:
            arrays[metric][i] = result_dict[metric]

    summary_rows: list[dict[str, Any]] = []
    for metric in TRACKED_METRICS:
        arr = arrays[metric]
        summary_rows.append({
            "Métrica": METRIC_LABELS.get(metric, metric),
            "Media": np.mean(arr),
            "Desv. Est.": np.std(arr),
            "Percentil 5": np.percentile(arr, 5),
            "Percentil 25": np.percentile(arr, 25),
            "Mediana": np.percentile(arr, 50),
            "Percentil 75": np.percentile(arr, 75),
            "Percentil 95": np.percentile(arr, 95),
            "P(< 0)": np.mean(arr < 0) * 100,
        })

    return SimulationResults(
        n_iterations=n_iterations,
        metric_arrays=arrays,
        summary_df=pd.DataFrame(summary_rows),
    )
