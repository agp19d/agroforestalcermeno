"""Motor de simulación Monte Carlo para escenarios de producción de café.

Ejecuta *N* iteraciones del modelo financiero, muestreando cada
entrada incierta de una distribución de probabilidad definida por el
usuario (triangular por defecto).  Devuelve un objeto
:class:`SimulationResults` con arreglos por métrica y estadísticas
resumidas precalculadas.
"""

from __future__ import annotations

from dataclasses import dataclass, fields
from typing import Any

import numpy as np
import pandas as pd

from models import FinancialResults, calculate


# ── Configuración ────────────────────────────────────────────────────────────

@dataclass
class VariableRange:
    """Define el rango de incertidumbre para una variable de entrada.

    La distribución triangular se parametriza con *low*, *base*
    (moda) y *high*.  Si la variable no está marcada como *enabled*,
    se mantendrá constante en su valor *base* durante la simulación.

    Attributes:
        key: Nombre de la clave de entrada (sin el prefijo ``in_``).
        label: Etiqueta legible para la interfaz de usuario.
        low: Límite optimista / mínimo.
        base: Valor más probable (moda del triángulo).
        high: Límite pesimista / máximo.
        enabled: Si esta variable debe ser muestreada.
    """

    key: str
    label: str
    low: float
    base: float
    high: float
    enabled: bool = True


# Subconjunto de entradas más comúnmente sujetas a incertidumbre.
DEFAULT_VARIABLE_KEYS: list[dict[str, str]] = [
    {"key": "cherry_yield_per_ha", "label": "Rendimiento de Cereza (lbs/ha)"},
    {"key": "cherry_to_green", "label": "Ratio Cereza a Verde (%)"},
    {"key": "price_green", "label": "Precio Café Verde (B/./lb)"},
    {"key": "price_processed", "label": "Precio Café Procesado (B/./lb)"},
    {"key": "price_roasted", "label": "Precio Café Tostado (B/./lb)"},
    {"key": "fertilizer", "label": "Costo de Fertilizante (B/.)"},
    {"key": "pesticide", "label": "Control de Plagas (B/.)"},
    {"key": "seasonal_workers", "label": "Trabajadores Temporales"},
    {"key": "seasonal_daily_wage", "label": "Jornal Diario Temporal (B/.)"},
    {"key": "harvest_days", "label": "Días de Cosecha"},
    {"key": "processing_cost_lb", "label": "Costo de Procesamiento (B/./lb)"},
    {"key": "roasting_cost_lb", "label": "Costo de Tueste (B/./lb)"},
    {"key": "fuel", "label": "Combustible y Energía (B/.)"},
    {"key": "transport", "label": "Transporte y Logística (B/.)"},
]


def build_default_ranges(
    base_inputs: dict[str, Any],
    spread: float = 0.20,
) -> list[VariableRange]:
    """Crea objetos :class:`VariableRange` predeterminados desde las entradas actuales.

    Cada variable obtiene un rango simétrico de +/- *spread* (por defecto
    20 %) alrededor de su valor base.

    Args:
        base_inputs: Diccionario de entradas del escenario actual (las
            claves pueden tener el prefijo ``in_``).
        spread: Dispersión fraccional aplicada simétricamente (0.20 = 20 %).

    Returns:
        Una lista de instancias :class:`VariableRange` para cada clave
        en :data:`DEFAULT_VARIABLE_KEYS`.
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


# ── Resultados de Simulación ─────────────────────────────────────────────────

# Métricas que rastreamos a través de las iteraciones.
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
    "total_revenue": "Ingresos Totales (B/.)",
    "total_costs": "Costos Totales (B/.)",
    "net_profit": "Ganancia Neta (B/.)",
    "margin": "Margen de Ganancia (%)",
    "cost_per_lb_green": "Costo por lb Verde (B/.)",
    "breakeven": "Punto de Equilibrio (B/./lb)",
    "total_green": "Total Café Verde (lbs)",
    "roasted_output_lbs": "Producción Tostado (lbs)",
    "rev_per_ha": "Ingresos por Hectárea (B/.)",
    "profit_per_ha": "Ganancia por Hectárea (B/.)",
}


@dataclass
class SimulationResults:
    """Contenedor para los resultados de simulación Monte Carlo.

    Attributes:
        n_iterations: Número de iteraciones ejecutadas.
        metric_arrays: Mapeo de nombre de métrica → arreglo NumPy 1-D
            de longitud *n_iterations*.
        summary_df: DataFrame precalculado con columnas de media,
            desviación estándar y percentiles para cada métrica.
    """

    n_iterations: int
    metric_arrays: dict[str, np.ndarray]
    summary_df: pd.DataFrame


# ── Motor ────────────────────────────────────────────────────────────────────

def run_simulation(
    base_inputs: dict[str, Any],
    variable_ranges: list[VariableRange],
    n_iterations: int = 5000,
    seed: int | None = None,
) -> SimulationResults:
    """Ejecuta la simulación Monte Carlo.

    Para cada iteración, cada :class:`VariableRange` *habilitada* es
    muestreada de una distribución triangular.  Los valores muestreados
    reemplazan las entradas base correspondientes, y el modelo financiero
    completo se evalúa vía :func:`models.calculate`.

    Args:
        base_inputs: Las entradas determinísticas del escenario (usadas
            como punto de partida para cada iteración).
        variable_ranges: Lista de variables inciertas con sus
            parámetros de distribución.
        n_iterations: Cuántas iteraciones ejecutar (por defecto 5 000).
        seed: Semilla opcional del generador aleatorio para
            reproducibilidad.

    Returns:
        Una instancia de :class:`SimulationResults`.
    """
    rng = np.random.default_rng(seed)

    # Pre-asignar arreglos de resultados.
    arrays: dict[str, np.ndarray] = {
        m: np.empty(n_iterations, dtype=np.float64) for m in TRACKED_METRICS
    }

    # Filtrar solo rangos habilitados.
    active_ranges = [vr for vr in variable_ranges if vr.enabled]

    for i in range(n_iterations):
        # Partir de una copia de las entradas base.
        sampled = dict(base_inputs)

        # Muestrear cada variable incierta.
        for vr in active_ranges:
            # Asegurar low <= mode <= high para la distribución triangular.
            low = min(vr.low, vr.base)
            high = max(vr.high, vr.base)
            mode = vr.base
            # Limitar mode dentro de [low, high] para satisfacer numpy.
            mode = max(low, min(mode, high))
            if low == high:
                value = low
            else:
                value = rng.triangular(low, mode, high)
            sampled[f"in_{vr.key}"] = value

        # Ejecutar el modelo financiero.
        result: FinancialResults = calculate(sampled)

        # Almacenar métricas rastreadas.
        result_dict = result.as_dict()
        for metric in TRACKED_METRICS:
            arrays[metric][i] = result_dict[metric]

    # Construir estadísticas resumidas.
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

    summary_df = pd.DataFrame(summary_rows)

    return SimulationResults(
        n_iterations=n_iterations,
        metric_arrays=arrays,
        summary_df=summary_df,
    )
