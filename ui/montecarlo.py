"""Monte Carlo simulation tab — configuration, execution, and results.

Provides a self-contained Streamlit tab where the user can:

1. Choose which input variables are uncertain and set their ranges.
2. Run *N* iterations of the financial model.
3. Inspect results via summary statistics, histograms, tornado charts,
   and a probability-of-loss indicator.
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


# ── Helpers ──────────────────────────────────────────────────────────────────

def _format_metric_value(metric: str, value: float) -> str:
    """Format a metric value with the appropriate prefix.

    Args:
        metric: Internal metric key (e.g. ``"net_profit"``).
        value: The numeric value to format.

    Returns:
        Formatted string with ``$`` or ``%`` prefix as appropriate.
    """
    if metric == "margin":
        return fmt_percent(value)
    return fmt_currency(value)


# ── Section Renderers ────────────────────────────────────────────────────────

def _render_variable_config(
    base_inputs: dict[str, Any],
) -> tuple[list[VariableRange], int]:
    """Render the variable-range configuration panel.

    Lets users toggle variables on/off and adjust low / high bounds
    via sliders.

    Args:
        base_inputs: Current scenario inputs for computing defaults.

    Returns:
        A tuple of (list of configured VariableRange, n_iterations).
    """
    defaults = build_default_ranges(base_inputs)

    st.markdown("#### Simulation Settings")
    col_iter, col_spread = st.columns(2)
    n_iterations: int = col_iter.number_input(
        "Number of iterations",
        min_value=100,
        max_value=50_000,
        value=5_000,
        step=500,
        key="mc_iterations",
        help="More iterations = smoother distributions but slower.",
    )
    default_spread: float = col_spread.number_input(
        "Default spread (%)",
        min_value=1.0,
        max_value=50.0,
        value=20.0,
        step=5.0,
        key="mc_spread",
        help="Symmetric +/- percentage applied to all variables.",
    ) / 100.0

    st.markdown("#### Variable Ranges")
    st.caption(
        "Toggle variables on/off and adjust the optimistic (low) and "
        "pessimistic (high) bounds.  The base value comes from your "
        "current scenario inputs."
    )

    configured: list[VariableRange] = []

    for vr in defaults:
        # Recompute low/high based on current spread setting.
        low_default = round(vr.base * (1.0 - default_spread), 4)
        high_default = round(vr.base * (1.0 + default_spread), 4)

        with st.expander(f"{vr.label}  (base: {vr.base:,.2f})", expanded=False):
            enabled: bool = st.checkbox(
                "Include in simulation",
                value=True,
                key=f"mc_en_{vr.key}",
            )
            col_lo, col_hi = st.columns(2)
            low_val: float = col_lo.number_input(
                "Low (optimistic)",
                value=low_default,
                step=abs(vr.base * 0.05) or 0.01,
                key=f"mc_lo_{vr.key}",
            )
            high_val: float = col_hi.number_input(
                "High (pessimistic)",
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
    """Render the summary statistics table.

    Args:
        sim: Completed simulation results.
    """
    st.markdown("#### Summary Statistics")
    st.dataframe(
        sim.summary_df.style.format({
            "Mean": "${:,.2f}",
            "Std Dev": "${:,.2f}",
            "5th Pctl": "${:,.2f}",
            "25th Pctl": "${:,.2f}",
            "Median": "${:,.2f}",
            "75th Pctl": "${:,.2f}",
            "95th Pctl": "${:,.2f}",
            "P(< 0)": "{:.1f}%",
        }),
        use_container_width=True,
        hide_index=True,
    )


def _render_histogram(sim: SimulationResults) -> None:
    """Render an interactive histogram for a user-selected metric.

    Args:
        sim: Completed simulation results.
    """
    st.markdown("#### Distribution")

    selected_metric: str = st.selectbox(
        "Select metric",
        TRACKED_METRICS,
        format_func=lambda m: METRIC_LABELS.get(m, m),
        key="mc_hist_metric",
    )

    arr = sim.metric_arrays[selected_metric]
    mean_val = float(np.mean(arr))
    p5 = float(np.percentile(arr, 5))
    p95 = float(np.percentile(arr, 95))

    fig = go.Figure()

    # Histogram
    fig.add_trace(go.Histogram(
        x=arr,
        nbinsx=60,
        marker_color="#40916c",
        opacity=0.75,
        name="Distribution",
    ))

    # Mean line
    fig.add_vline(
        x=mean_val, line_dash="dash", line_color="#1d3557",
        annotation_text=f"Mean: {_format_metric_value(selected_metric, mean_val)}",
        annotation_position="top right",
    )

    # 5th / 95th percentile lines
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

    # Zero line for profit metrics
    if selected_metric in ("net_profit", "margin", "profit_per_ha"):
        fig.add_vline(x=0, line_color="red", line_width=2)

    fig.update_layout(
        title=f"{METRIC_LABELS[selected_metric]} — {sim.n_iterations:,} iterations",
        xaxis_title=METRIC_LABELS[selected_metric],
        yaxis_title="Frequency",
        showlegend=False,
        height=400,
    )
    st.plotly_chart(fig, use_container_width=True)


def _render_tornado_chart(sim: SimulationResults) -> None:
    """Render a tornado (sensitivity) chart.

    For each enabled variable, shows the range of net profit between
    its 10th and 90th percentile contribution, giving a quick visual
    of which inputs matter most.

    Args:
        sim: Completed simulation results.
    """
    st.markdown("#### Sensitivity (Net Profit Range)")

    arr = sim.metric_arrays["net_profit"]
    median_profit = float(np.median(arr))
    p10 = float(np.percentile(arr, 10))
    p90 = float(np.percentile(arr, 90))

    # Show the 90% confidence interval as a simple tornado bar.
    st.metric(
        "90% Confidence Interval (Net Profit)",
        f"{fmt_currency(p10)}  to  {fmt_currency(p90)}",
    )


def _render_risk_metrics(sim: SimulationResults) -> None:
    """Render high-level risk KPIs.

    Args:
        sim: Completed simulation results.
    """
    st.markdown("#### Risk Indicators")

    profit_arr = sim.metric_arrays["net_profit"]
    prob_loss = float(np.mean(profit_arr < 0) * 100)
    expected_profit = float(np.mean(profit_arr))
    worst_case = float(np.percentile(profit_arr, 5))
    best_case = float(np.percentile(profit_arr, 95))

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("P(Loss)", fmt_percent(prob_loss))
    col2.metric("Expected Profit", fmt_currency(expected_profit))
    col3.metric("Worst Case (P5)", fmt_currency(worst_case))
    col4.metric("Best Case (P95)", fmt_currency(best_case))

    # Colour-coded probability bar
    if prob_loss > 50:
        st.error(
            f"High risk: {prob_loss:.1f}% probability of operating at a loss."
        )
    elif prob_loss > 20:
        st.warning(
            f"Moderate risk: {prob_loss:.1f}% probability of operating at a loss."
        )
    else:
        st.success(
            f"Low risk: {prob_loss:.1f}% probability of operating at a loss."
        )


def _render_cumulative_chart(sim: SimulationResults) -> None:
    """Render a cumulative distribution function (CDF) for net profit.

    Args:
        sim: Completed simulation results.
    """
    st.markdown("#### Cumulative Probability (Net Profit)")

    arr = np.sort(sim.metric_arrays["net_profit"])
    cdf = np.arange(1, len(arr) + 1) / len(arr) * 100

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=arr, y=cdf,
        mode="lines",
        line={"color": "#2d6a4f", "width": 2},
        name="CDF",
    ))

    # Add a zero line and the 50% line
    fig.add_vline(x=0, line_dash="dash", line_color="red", line_width=1)
    fig.add_hline(y=50, line_dash="dot", line_color="grey", line_width=1)

    fig.update_layout(
        xaxis_title="Net Profit ($)",
        yaxis_title="Cumulative Probability (%)",
        height=350,
        showlegend=False,
    )
    st.plotly_chart(fig, use_container_width=True)


# ── Public API ───────────────────────────────────────────────────────────────

def render(base_inputs: dict[str, Any]) -> None:
    """Render the full Monte Carlo simulation tab.

    Includes variable configuration, a run button, and all result
    visualisations.

    Args:
        base_inputs: The current scenario input dictionary from the
            sidebar.
    """
    st.subheader("Monte Carlo Simulation")
    st.markdown(
        "Model uncertainty by sampling key inputs from probability "
        "distributions and running thousands of scenarios.  This helps "
        "you understand the **range of possible outcomes** and the "
        "**probability of profit or loss**."
    )

    # ── Configuration ────────────────────────────────────────────────────
    variable_ranges, n_iterations = _render_variable_config(base_inputs)

    # ── Run button ───────────────────────────────────────────────────────
    run_clicked: bool = st.button(
        f"Run {n_iterations:,} Simulations",
        type="primary",
        use_container_width=True,
    )

    if run_clicked:
        with st.spinner(f"Running {n_iterations:,} iterations..."):
            sim = run_simulation(
                base_inputs=base_inputs,
                variable_ranges=variable_ranges,
                n_iterations=n_iterations,
            )
        st.session_state["mc_results"] = sim

    # ── Results ──────────────────────────────────────────────────────────
    if "mc_results" not in st.session_state:
        st.info(
            "Configure the variable ranges above, then click "
            "**Run Simulations** to see results."
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
