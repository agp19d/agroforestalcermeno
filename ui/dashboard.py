"""Main-area dashboard — metrics, tables, and charts.

Each tab (Production, Revenue, Costs, Profitability, Compare) is
rendered by a dedicated private function, keeping the public
:func:`render` entry point concise.
"""

from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

import scenarios
from config import (
    COLOUR_NEGATIVE,
    COLOUR_POSITIVE,
    COLOUR_TOTAL,
    COLOURS_GREEN,
)
from formatting import fmt_currency, fmt_number, fmt_percent
from models import FinancialResults, calculate


# ── Tab Renderers ────────────────────────────────────────────────────────────

def _render_production_tab(r: FinancialResults) -> None:
    """Render the Production Output tab with a table and bar chart.

    Args:
        r: Pre-calculated financial results for the active scenario.
    """
    st.subheader("Production Output (lbs)")
    col_table, col_chart = st.columns(2)

    with col_table:
        prod_df = pd.DataFrame({
            "Stage": [
                "Cherry Harvest",
                "Green Coffee",
                "Sold Green/Raw",
                "Processed",
                "Roasted (output)",
            ],
            "Pounds (lbs)": [
                r.total_cherry,
                r.total_green,
                r.green_sold_lbs,
                r.processed_lbs,
                r.roasted_output_lbs,
            ],
        })
        st.dataframe(
            prod_df.style.format({"Pounds (lbs)": "{:,.0f}"}),
            use_container_width=True,
            hide_index=True,
        )

    with col_chart:
        output_labels = ["Green/Raw", "Processed", "Roasted"]
        output_values = [r.green_sold_lbs, r.processed_lbs, r.roasted_output_lbs]

        fig = go.Figure(data=[go.Bar(
            x=output_labels,
            y=output_values,
            marker_color=COLOURS_GREEN,
            text=[fmt_number(v) for v in output_values],
            textposition="outside",
        )])
        fig.update_layout(
            title="Output by Bean Type (lbs)",
            yaxis_title="Pounds",
            height=350,
        )
        st.plotly_chart(fig, use_container_width=True)


def _render_revenue_tab(r: FinancialResults) -> None:
    """Render the Revenue tab with a summary table and pie chart.

    Args:
        r: Pre-calculated financial results for the active scenario.
    """
    st.subheader("Revenue Breakdown")
    col_table, col_chart = st.columns(2)

    with col_table:
        rev_df = pd.DataFrame({
            "Source": [
                "Green/Raw Sales",
                "Processed Sales",
                "Roasted Sales",
                "TOTAL",
            ],
            "Revenue ($)": [
                r.rev_green,
                r.rev_processed,
                r.rev_roasted,
                r.total_revenue,
            ],
        })
        st.dataframe(
            rev_df.style.format({"Revenue ($)": "${:,.2f}"}),
            use_container_width=True,
            hide_index=True,
        )

    with col_chart:
        fig = go.Figure(data=[go.Pie(
            labels=["Green/Raw", "Processed", "Roasted"],
            values=[r.rev_green, r.rev_processed, r.rev_roasted],
            marker_colors=COLOURS_GREEN,
            textinfo="label+percent+value",
            texttemplate="%{label}<br>%{percent}<br>$%{value:,.0f}",
        )])
        fig.update_layout(title="Revenue by Product Type", height=350)
        st.plotly_chart(fig, use_container_width=True)


def _render_costs_tab(r: FinancialResults) -> None:
    """Render the Costs tab with an itemised table and donut chart.

    Args:
        r: Pre-calculated financial results for the active scenario.
    """
    st.subheader("Cost Breakdown")
    col_table, col_chart = st.columns(2)

    cost_items: list[tuple[str, float]] = [
        ("Labor (permanent)", r.permanent_labor),
        ("Labor (seasonal)", r.seasonal_labor),
        ("Labor Benefits & Taxes", r.labor_benefits),
        ("Inputs & Materials", r.inputs_materials),
        ("Processing", r.processing_cost),
        ("Roasting", r.roasting_cost),
        ("Packaging", r.packaging_cost),
        ("Land", r.land_cost),
        ("Overhead & Fixed", r.overhead),
        ("Contingency", r.contingency),
    ]

    with col_table:
        cost_df = pd.DataFrame(cost_items, columns=["Category", "Amount ($)"])
        total_row = pd.DataFrame(
            [("TOTAL", r.total_costs)],
            columns=["Category", "Amount ($)"],
        )
        cost_df = pd.concat([cost_df, total_row], ignore_index=True)
        st.dataframe(
            cost_df.style.format({"Amount ($)": "${:,.2f}"}),
            use_container_width=True,
            hide_index=True,
        )

    with col_chart:
        labels = [item[0] for item in cost_items]
        values = [item[1] for item in cost_items]
        fig = go.Figure(data=[go.Pie(
            labels=labels,
            values=values,
            textinfo="label+percent",
            hole=0.35,
        )])
        fig.update_layout(title="Cost Distribution", height=400)
        st.plotly_chart(fig, use_container_width=True)


def _render_profitability_tab(r: FinancialResults) -> None:
    """Render the Profitability tab with KPIs and a waterfall chart.

    Args:
        r: Pre-calculated financial results for the active scenario.
    """
    st.subheader("Profitability Analysis")

    # KPI row 1
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    kpi1.metric("Gross Profit", fmt_currency(r.gross_profit))
    kpi2.metric("Taxes", fmt_currency(r.taxes))
    kpi3.metric("Cost / lb (green)", fmt_currency(r.cost_per_lb_green))
    kpi4.metric("Break-even ($/lb green)", fmt_currency(r.breakeven))

    # KPI row 2
    kpi5, kpi6 = st.columns(2)
    kpi5.metric("Revenue / Hectare", fmt_currency(r.rev_per_ha))
    kpi6.metric("Profit / Hectare", fmt_currency(r.profit_per_ha))

    # Waterfall chart: revenue minus each cost category equals net profit
    waterfall_labels = [
        "Revenue", "Labor", "Inputs", "Processing", "Roasting",
        "Packaging", "Land", "Overhead", "Contingency", "Taxes",
        "Net Profit",
    ]
    waterfall_values = [
        r.total_revenue,
        -r.total_labor, -r.inputs_materials, -r.processing_cost,
        -r.roasting_cost, -r.packaging_cost, -r.land_cost,
        -r.overhead, -r.contingency, -r.taxes,
        0,  # placeholder — Plotly computes the "total" measure
    ]
    waterfall_measures = (
        ["absolute"]
        + ["relative"] * 9
        + ["total"]
    )

    fig = go.Figure(go.Waterfall(
        x=waterfall_labels,
        y=waterfall_values,
        measure=waterfall_measures,
        connector={"line": {"color": "rgba(0,0,0,0.1)"}},
        increasing={"marker": {"color": COLOUR_POSITIVE}},
        decreasing={"marker": {"color": COLOUR_NEGATIVE}},
        totals={"marker": {"color": COLOUR_TOTAL}},
        textposition="outside",
        text=[fmt_currency(abs(v)) for v in [
            r.total_revenue, r.total_labor, r.inputs_materials,
            r.processing_cost, r.roasting_cost, r.packaging_cost,
            r.land_cost, r.overhead, r.contingency, r.taxes,
            r.net_profit,
        ]],
    ))
    fig.update_layout(
        title="Revenue to Net Profit Waterfall",
        height=450,
        showlegend=False,
    )
    st.plotly_chart(fig, use_container_width=True)


def _render_compare_tab() -> None:
    """Render the scenario-comparison tab.

    Loads all saved scenarios, lets the user pick which ones to compare,
    and shows a summary table plus a grouped bar chart.
    """
    st.subheader("Compare Saved Scenarios")
    all_scenarios = scenarios.load_all()

    if len(all_scenarios) < 2:
        st.info("Save at least 2 scenarios to compare them side by side.")
        return

    selected_names: list[str] = st.multiselect(
        "Select scenarios to compare",
        list(all_scenarios.keys()),
        default=list(all_scenarios.keys())[:3],
    )

    if len(selected_names) < 2:
        return

    # Build comparison table
    rows: list[dict[str, float | str]] = []
    for name in selected_names:
        sr = calculate(all_scenarios[name])
        rows.append({
            "Scenario": name,
            "Revenue ($)": sr.total_revenue,
            "Total Costs ($)": sr.total_costs,
            "Net Profit ($)": sr.net_profit,
            "Margin (%)": sr.margin,
            "Green Output (lbs)": sr.green_sold_lbs,
            "Processed (lbs)": sr.processed_lbs,
            "Roasted (lbs)": sr.roasted_output_lbs,
            "Cost/lb Green ($)": sr.cost_per_lb_green,
            "Break-even ($/lb)": sr.breakeven,
        })

    comp_df = pd.DataFrame(rows)
    st.dataframe(
        comp_df.style.format({
            "Revenue ($)": "${:,.2f}",
            "Total Costs ($)": "${:,.2f}",
            "Net Profit ($)": "${:,.2f}",
            "Margin (%)": "{:.1f}%",
            "Green Output (lbs)": "{:,.0f}",
            "Processed (lbs)": "{:,.0f}",
            "Roasted (lbs)": "{:,.0f}",
            "Cost/lb Green ($)": "${:,.2f}",
            "Break-even ($/lb)": "${:,.2f}",
        }),
        use_container_width=True,
        hide_index=True,
    )

    # Grouped bar chart
    fig = go.Figure()
    for name in selected_names:
        sr = calculate(all_scenarios[name])
        fig.add_trace(go.Bar(
            name=name,
            x=["Revenue", "Costs", "Net Profit"],
            y=[sr.total_revenue, sr.total_costs, sr.net_profit],
            text=[
                fmt_currency(sr.total_revenue),
                fmt_currency(sr.total_costs),
                fmt_currency(sr.net_profit),
            ],
            textposition="outside",
        ))
    fig.update_layout(
        barmode="group",
        title="Scenario Comparison",
        yaxis_title="USD ($)",
        height=400,
    )
    st.plotly_chart(fig, use_container_width=True)


# ── Public API ───────────────────────────────────────────────────────────────

def render(results: FinancialResults) -> None:
    """Render the entire main-area dashboard.

    Displays headline KPIs at the top, followed by five tabs for
    detailed breakdowns and scenario comparison.

    Args:
        results: The :class:`~models.FinancialResults` for the current
            set of inputs.
    """
    # Headline KPIs
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Revenue", fmt_currency(results.total_revenue))
    col2.metric("Total Costs", fmt_currency(results.total_costs))
    col3.metric("Net Profit", fmt_currency(results.net_profit))
    col4.metric("Profit Margin", fmt_percent(results.margin))

    st.divider()

    # Detailed tabs
    tab_prod, tab_rev, tab_costs, tab_profit, tab_compare = st.tabs([
        "Production",
        "Revenue",
        "Costs",
        "Profitability",
        "Compare Scenarios",
    ])

    with tab_prod:
        _render_production_tab(results)
    with tab_rev:
        _render_revenue_tab(results)
    with tab_costs:
        _render_costs_tab(results)
    with tab_profit:
        _render_profitability_tab(results)
    with tab_compare:
        _render_compare_tab()
