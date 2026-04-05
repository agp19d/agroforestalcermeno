"""Pestaña de simulación Monte Carlo — configuración, ejecución y resultados.

Proporciona una pestaña autocontenida de Streamlit donde el usuario puede:

1. Elegir qué variables de entrada son inciertas y definir sus rangos.
2. Ejecutar *N* iteraciones del modelo financiero.
3. Inspeccionar resultados mediante estadísticas resumidas, histogramas,
   gráficos de tornado e indicadores de probabilidad de pérdida.
"""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from formatting import fmt_currency, fmt_percent
from simulation import (
    METRIC_LABELS,
    TRACKED_METRICS,
    SimulationResults,
    VariableRange,
    build_default_ranges,
    run_simulation,
)


# ── Ayudantes ────────────────────────────────────────────────────────────────

def _format_metric_value(metric: str, value: float) -> str:
    """Formatea el valor de una métrica con el prefijo apropiado.

    Args:
        metric: Clave interna de métrica (ej. ``"net_profit"``).
        value: El valor numérico a formatear.

    Returns:
        Cadena formateada con ``B/.`` o ``%`` según corresponda.
    """
    if metric == "margin":
        return fmt_percent(value)
    return fmt_currency(value)


# ── Renderizadores de Secciones ──────────────────────────────────────────────

def _render_variable_config(
    base_inputs: dict[str, Any],
) -> tuple[list[VariableRange], int]:
    """Renderiza el panel de configuración de rangos de variables.

    Permite a los usuarios activar/desactivar variables y ajustar
    los límites bajo / alto mediante controles numéricos.

    Args:
        base_inputs: Entradas actuales del escenario para calcular
            valores por defecto.

    Returns:
        Una tupla de (lista de VariableRange configurados, n_iteraciones).
    """
    defaults = build_default_ranges(base_inputs)

    st.markdown("#### Configuración de Simulación")
    col_iter, col_spread = st.columns(2)
    n_iterations: int = col_iter.number_input(
        "Número de iteraciones",
        min_value=100,
        max_value=50_000,
        value=5_000,
        step=500,
        key="mc_iterations",
        help="Más iteraciones = distribuciones más suaves pero más lento.",
    )
    default_spread: float = col_spread.number_input(
        "Dispersión por defecto (%)",
        min_value=1.0,
        max_value=50.0,
        value=20.0,
        step=5.0,
        key="mc_spread",
        help="Porcentaje +/- simétrico aplicado a todas las variables.",
    ) / 100.0

    st.markdown("#### Rangos de Variables")
    st.caption(
        "Active/desactive variables y ajuste los límites optimista (bajo) "
        "y pesimista (alto). El valor base proviene de las entradas "
        "actuales de su escenario."
    )

    configured: list[VariableRange] = []

    for vr in defaults:
        # Recalcular bajo/alto basado en la dispersión actual.
        low_default = round(vr.base * (1.0 - default_spread), 4)
        high_default = round(vr.base * (1.0 + default_spread), 4)

        with st.expander(f"{vr.label}  (base: {vr.base:,.2f})", expanded=False):
            enabled: bool = st.checkbox(
                "Incluir en simulación",
                value=True,
                key=f"mc_en_{vr.key}",
            )
            col_lo, col_hi = st.columns(2)
            low_val: float = col_lo.number_input(
                "Bajo (optimista)",
                value=low_default,
                step=abs(vr.base * 0.05) or 0.01,
                key=f"mc_lo_{vr.key}",
            )
            high_val: float = col_hi.number_input(
                "Alto (pesimista)",
                value=high_default,
                step=abs(vr.base * 0.05) or 0.01,
                key=f"mc_hi_{vr.key}",
            )

            configured.append(VariableRange(
                key=vr.key,
                label=vr.label,
                low=low_val,
                base=vr.base,
                high=high_val,
                enabled=enabled,
            ))

    return configured, int(n_iterations)


def _render_summary_table(sim: SimulationResults) -> None:
    """Renderiza la tabla de estadísticas resumidas.

    Args:
        sim: Resultados de simulación completada.
    """
    st.markdown("#### Estadísticas Resumidas")
    st.dataframe(
        sim.summary_df.style.format({
            "Media": "B/.{:,.2f}",
            "Desv. Est.": "B/.{:,.2f}",
            "Percentil 5": "B/.{:,.2f}",
            "Percentil 25": "B/.{:,.2f}",
            "Mediana": "B/.{:,.2f}",
            "Percentil 75": "B/.{:,.2f}",
            "Percentil 95": "B/.{:,.2f}",
            "P(< 0)": "{:.1f}%",
        }),
        use_container_width=True,
        hide_index=True,
    )


def _render_histogram(sim: SimulationResults) -> None:
    """Renderiza un histograma interactivo para una métrica seleccionada.

    Args:
        sim: Resultados de simulación completada.
    """
    st.markdown("#### Distribución")

    selected_metric: str = st.selectbox(
        "Seleccionar métrica",
        TRACKED_METRICS,
        format_func=lambda m: METRIC_LABELS.get(m, m),
        key="mc_hist_metric",
    )

    arr = sim.metric_arrays[selected_metric]
    mean_val = float(np.mean(arr))
    p5 = float(np.percentile(arr, 5))
    p95 = float(np.percentile(arr, 95))

    fig = go.Figure()

    # Histograma
    fig.add_trace(go.Histogram(
        x=arr,
        nbinsx=60,
        marker_color="#40916c",
        opacity=0.75,
        name="Distribución",
    ))

    # Línea de media
    fig.add_vline(
        x=mean_val, line_dash="dash", line_color="#1d3557",
        annotation_text=f"Media: {_format_metric_value(selected_metric, mean_val)}",
        annotation_position="top right",
    )

    # Líneas de percentiles 5 y 95
    fig.add_vline(
        x=p5, line_dash="dot", line_color="#d62828",
        annotation_text=f"P5: {_format_metric_value(selected_metric, p5)}",
        annotation_position="top left",
    )
    fig.add_vline(
        x=p95, line_dash="dot", line_color="#d62828",
        annotation_text=f"P95: {_format_metric_value(selected_metric, p95)}",
        annotation_position="top right",
    )

    # Línea de cero para métricas de ganancia
    if selected_metric in ("net_profit", "margin", "profit_per_ha"):
        fig.add_vline(x=0, line_color="red", line_width=2)

    fig.update_layout(
        title=f"{METRIC_LABELS[selected_metric]} — {sim.n_iterations:,} iteraciones",
        xaxis_title=METRIC_LABELS[selected_metric],
        yaxis_title="Frecuencia",
        showlegend=False,
        height=400,
    )
    st.plotly_chart(fig, use_container_width=True)


def _render_tornado_chart(sim: SimulationResults) -> None:
    """Renderiza un gráfico de tornado (sensibilidad).

    Muestra el intervalo de confianza del 90 % para la ganancia neta.

    Args:
        sim: Resultados de simulación completada.
    """
    st.markdown("#### Sensibilidad (Rango de Ganancia Neta)")

    arr = sim.metric_arrays["net_profit"]
    p10 = float(np.percentile(arr, 10))
    p90 = float(np.percentile(arr, 90))

    # Mostrar el intervalo de confianza del 90 %.
    st.metric(
        "Intervalo de Confianza 90 % (Ganancia Neta)",
        f"{fmt_currency(p10)}  a  {fmt_currency(p90)}",
    )


def _render_risk_metrics(sim: SimulationResults) -> None:
    """Renderiza KPIs de riesgo de alto nivel.

    Args:
        sim: Resultados de simulación completada.
    """
    st.markdown("#### Indicadores de Riesgo")

    profit_arr = sim.metric_arrays["net_profit"]
    prob_loss = float(np.mean(profit_arr < 0) * 100)
    expected_profit = float(np.mean(profit_arr))
    worst_case = float(np.percentile(profit_arr, 5))
    best_case = float(np.percentile(profit_arr, 95))

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("P(Pérdida)", fmt_percent(prob_loss))
    col2.metric("Ganancia Esperada", fmt_currency(expected_profit))
    col3.metric("Peor Caso (P5)", fmt_currency(worst_case))
    col4.metric("Mejor Caso (P95)", fmt_currency(best_case))

    # Barra de probabilidad con código de color
    if prob_loss > 50:
        st.error(
            f"Riesgo alto: {prob_loss:.1f}% de probabilidad de operar con pérdida."
        )
    elif prob_loss > 20:
        st.warning(
            f"Riesgo moderado: {prob_loss:.1f}% de probabilidad de operar con pérdida."
        )
    else:
        st.success(
            f"Riesgo bajo: {prob_loss:.1f}% de probabilidad de operar con pérdida."
        )


def _render_cumulative_chart(sim: SimulationResults) -> None:
    """Renderiza una función de distribución acumulada (CDF) para ganancia neta.

    Args:
        sim: Resultados de simulación completada.
    """
    st.markdown("#### Probabilidad Acumulada (Ganancia Neta)")

    arr = np.sort(sim.metric_arrays["net_profit"])
    cdf = np.arange(1, len(arr) + 1) / len(arr) * 100

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=arr, y=cdf,
        mode="lines",
        line={"color": "#2d6a4f", "width": 2},
        name="CDF",
    ))

    # Agregar línea de cero y línea del 50 %
    fig.add_vline(x=0, line_dash="dash", line_color="red", line_width=1)
    fig.add_hline(y=50, line_dash="dot", line_color="grey", line_width=1)

    fig.update_layout(
        xaxis_title="Ganancia Neta (B/.)",
        yaxis_title="Probabilidad Acumulada (%)",
        height=350,
        showlegend=False,
    )
    st.plotly_chart(fig, use_container_width=True)


# ── API Pública ──────────────────────────────────────────────────────────────

def render(base_inputs: dict[str, Any]) -> None:
    """Renderiza la pestaña completa de simulación Monte Carlo.

    Incluye configuración de variables, botón de ejecución y todas
    las visualizaciones de resultados.

    Args:
        base_inputs: El diccionario de entradas del escenario actual
            desde el panel lateral.
    """
    st.subheader("Simulación Monte Carlo")
    st.markdown(
        "Modele la incertidumbre muestreando entradas clave desde "
        "distribuciones de probabilidad y ejecutando miles de escenarios. "
        "Esto le ayuda a entender el **rango de resultados posibles** y "
        "la **probabilidad de ganancia o pérdida**."
    )

    # ── Configuración ────────────────────────────────────────────────────
    variable_ranges, n_iterations = _render_variable_config(base_inputs)

    # ── Botón de ejecución ───────────────────────────────────────────────
    run_clicked: bool = st.button(
        f"Ejecutar {n_iterations:,} Simulaciones",
        type="primary",
        use_container_width=True,
    )

    if run_clicked:
        with st.spinner(f"Ejecutando {n_iterations:,} iteraciones..."):
            sim = run_simulation(
                base_inputs=base_inputs,
                variable_ranges=variable_ranges,
                n_iterations=n_iterations,
            )
        st.session_state["mc_results"] = sim

    # ── Resultados ───────────────────────────────────────────────────────
    if "mc_results" not in st.session_state:
        st.info(
            "Configure los rangos de variables arriba, luego haga clic en "
            "**Ejecutar Simulaciones** para ver los resultados."
        )
        return

    sim: SimulationResults = st.session_state["mc_results"]

    _render_risk_metrics(sim)

    col_hist, col_cdf = st.columns(2)
    with col_hist:
        _render_histogram(sim)
    with col_cdf:
        _render_cumulative_chart(sim)

    _render_tornado_chart(sim)
    _render_summary_table(sim)
