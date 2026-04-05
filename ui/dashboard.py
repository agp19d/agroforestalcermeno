"""Tablero principal — métricas, tablas y gráficos.

Pestañas: Producción, Ingresos, Costos, Rentabilidad, Comparar, Monte Carlo.
Modelo de 4 productos: Cereza, Seco Honey, Seco Natural, Seco Pilado.
"""

from __future__ import annotations

from typing import Any

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

import scenarios
from config import (
    COLOUR_NEGATIVE,
    COLOUR_POSITIVE,
    COLOUR_TOTAL,
    COLOURS_PRODUCT,
    PRODUCTS,
)
from formatting import fmt_currency, fmt_number, fmt_percent
from models import FinancialResults, calculate
from ui import montecarlo


# ── Colores y etiquetas ─────────────────────────────────────────────────────

_COLORS = list(COLOURS_PRODUCT.values())
_LABELS = [p["label"] for p in PRODUCTS]


def _render_production_tab(r: FinancialResults) -> None:
    st.subheader("Producción (lbs)")

    col_table, col_chart = st.columns(2)

    with col_table:
        prod_df = pd.DataFrame({
            "Etapa": [
                "🍒 Total Cereza Cosechada",
                "🍒 Cereza Vendida",
                "🍯 Cereza → Honey",
                "☀️ Cereza → Natural",
                "⚙️ Cereza → Pilado",
                "─────────────────",
                "🍯 Producción Seco Honey",
                "☀️ Producción Seco Natural",
                "⚙️ Producción Seco Pilado",
            ],
            "Libras (lbs)": [
                r.total_cherry,
                r.cherry_sold_lbs,
                r.cherry_to_honey_lbs,
                r.cherry_to_natural_lbs,
                r.cherry_to_pilado_lbs,
                0,
                r.honey_output_lbs,
                r.natural_output_lbs,
                r.pilado_output_lbs,
            ],
        })
        st.dataframe(
            prod_df.style.format({"Libras (lbs)": "{:,.0f}"}),
            use_container_width=True,
            hide_index=True,
        )

    with col_chart:
        # Gráfico de barras: cereza asignada vs producto obtenido
        categories = ["Honey", "Natural", "Pilado"]
        cherry_in = [r.cherry_to_honey_lbs, r.cherry_to_natural_lbs, r.cherry_to_pilado_lbs]
        product_out = [r.honey_output_lbs, r.natural_output_lbs, r.pilado_output_lbs]

        fig = go.Figure()
        fig.add_trace(go.Bar(
            name="Cereza Entrada",
            x=categories, y=cherry_in,
            marker_color="rgba(184, 48, 48, 0.4)",
            text=[fmt_number(v) for v in cherry_in],
            textposition="outside",
        ))
        fig.add_trace(go.Bar(
            name="Producto Obtenido",
            x=categories, y=product_out,
            marker_color=[COLOURS_PRODUCT["honey"], COLOURS_PRODUCT["natural"], COLOURS_PRODUCT["pilado"]],
            text=[fmt_number(v) for v in product_out],
            textposition="outside",
        ))
        fig.update_layout(
            title="Cereza Entrada vs Producto Obtenido (lbs)",
            barmode="group",
            yaxis_title="Libras",
            height=400,
            legend=dict(orientation="h", y=-0.15),
        )
        st.plotly_chart(fig, use_container_width=True)


def _render_revenue_tab(r: FinancialResults) -> None:
    st.subheader("Desglose de Ingresos")

    col_table, col_chart = st.columns(2)

    revenues = [r.rev_cereza, r.rev_honey, r.rev_natural, r.rev_pilado]
    labels = _LABELS

    with col_table:
        rev_df = pd.DataFrame({
            "Producto": labels + ["TOTAL"],
            "Ingresos (B/.)": revenues + [r.total_revenue],
        })
        st.dataframe(
            rev_df.style.format({"Ingresos (B/.)": "B/.{:,.2f}"}),
            use_container_width=True,
            hide_index=True,
        )

    with col_chart:
        fig = go.Figure(data=[go.Pie(
            labels=labels,
            values=revenues,
            marker_colors=_COLORS,
            textinfo="label+percent+value",
            texttemplate="%{label}<br>%{percent}<br>B/.%{value:,.0f}",
            hole=0.3,
        )])
        fig.update_layout(title="Ingresos por Producto", height=400)
        st.plotly_chart(fig, use_container_width=True)


def _render_costs_tab(r: FinancialResults) -> None:
    st.subheader("Desglose de Costos")

    col_table, col_chart = st.columns(2)

    cost_items: list[tuple[str, float]] = [
        ("Mano de obra (permanente)", r.permanent_labor),
        ("Mano de obra (temporal)", r.seasonal_labor),
        ("Prestaciones laborales", r.labor_benefits),
        ("Insumos y materiales", r.inputs_materials),
        ("Procesamiento Honey", r.processing_honey),
        ("Procesamiento Natural", r.processing_natural),
        ("Procesamiento Pilado", r.processing_pilado),
        ("Empaque", r.packaging_cost),
        ("Terreno", r.land_cost),
        ("Gastos generales", r.overhead),
        ("Contingencia", r.contingency),
    ]

    with col_table:
        cost_df = pd.DataFrame(cost_items, columns=["Categoría", "Monto (B/.)"])
        total_row = pd.DataFrame([("TOTAL", r.total_costs)], columns=["Categoría", "Monto (B/.)"])
        cost_df = pd.concat([cost_df, total_row], ignore_index=True)
        st.dataframe(
            cost_df.style.format({"Monto (B/.)": "B/.{:,.2f}"}),
            use_container_width=True,
            hide_index=True,
        )

    with col_chart:
        labels_c = [item[0] for item in cost_items]
        values_c = [item[1] for item in cost_items]
        fig = go.Figure(data=[go.Pie(
            labels=labels_c, values=values_c,
            textinfo="label+percent",
            hole=0.35,
        )])
        fig.update_layout(title="Distribución de Costos", height=450)
        st.plotly_chart(fig, use_container_width=True)


def _render_profitability_tab(r: FinancialResults) -> None:
    st.subheader("Análisis de Rentabilidad")

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Ganancia Bruta", fmt_currency(r.gross_profit))
    k2.metric("Impuestos", fmt_currency(r.taxes))
    k3.metric("Costo / lb Cereza", fmt_currency(r.cost_per_lb_cherry))
    k4.metric("Margen Neto", fmt_percent(r.margin))

    k5, k6 = st.columns(2)
    k5.metric("Ingresos / Hectárea", fmt_currency(r.rev_per_ha))
    k6.metric("Ganancia / Hectárea", fmt_currency(r.profit_per_ha))

    # Cascada
    waterfall_labels = [
        "Ingresos", "Mano de Obra", "Insumos", "Proc. Honey",
        "Proc. Natural", "Proc. Pilado", "Empaque",
        "Terreno", "Gastos Grales.", "Contingencia", "Impuestos",
        "Ganancia Neta",
    ]
    waterfall_values = [
        r.total_revenue,
        -r.total_labor, -r.inputs_materials,
        -r.processing_honey, -r.processing_natural, -r.processing_pilado,
        -r.packaging_cost, -r.land_cost, -r.overhead,
        -r.contingency, -r.taxes,
        0,
    ]
    waterfall_measures = ["absolute"] + ["relative"] * 10 + ["total"]

    display_vals = [
        r.total_revenue, r.total_labor, r.inputs_materials,
        r.processing_honey, r.processing_natural, r.processing_pilado,
        r.packaging_cost, r.land_cost, r.overhead,
        r.contingency, r.taxes, r.net_profit,
    ]

    fig = go.Figure(go.Waterfall(
        x=waterfall_labels, y=waterfall_values,
        measure=waterfall_measures,
        connector={"line": {"color": "rgba(0,0,0,0.1)"}},
        increasing={"marker": {"color": COLOUR_POSITIVE}},
        decreasing={"marker": {"color": COLOUR_NEGATIVE}},
        totals={"marker": {"color": COLOUR_TOTAL}},
        textposition="outside",
        text=[fmt_currency(abs(v)) for v in display_vals],
    ))
    fig.update_layout(
        title="Cascada de Ingresos a Ganancia Neta",
        height=450, showlegend=False,
    )
    st.plotly_chart(fig, use_container_width=True)


def _render_compare_tab() -> None:
    st.subheader("Comparar Escenarios Guardados")
    all_scenarios = scenarios.load_all()

    if len(all_scenarios) < 2:
        st.info("Guarda al menos 2 escenarios para compararlos.")
        return

    selected_names = st.multiselect(
        "Seleccionar escenarios",
        list(all_scenarios.keys()),
        default=list(all_scenarios.keys())[:3],
    )

    if len(selected_names) < 2:
        return

    rows: list[dict[str, float | str]] = []
    for name in selected_names:
        sr = calculate(all_scenarios[name])
        rows.append({
            "Escenario": name,
            "Ingresos (B/.)": sr.total_revenue,
            "Costos (B/.)": sr.total_costs,
            "Ganancia Neta (B/.)": sr.net_profit,
            "Margen (%)": sr.margin,
            "Honey (lbs)": sr.honey_output_lbs,
            "Natural (lbs)": sr.natural_output_lbs,
            "Pilado (lbs)": sr.pilado_output_lbs,
            "Costo/lb Cereza": sr.cost_per_lb_cherry,
        })

    comp_df = pd.DataFrame(rows)
    st.dataframe(
        comp_df.style.format({
            "Ingresos (B/.)": "B/.{:,.2f}",
            "Costos (B/.)": "B/.{:,.2f}",
            "Ganancia Neta (B/.)": "B/.{:,.2f}",
            "Margen (%)": "{:.1f}%",
            "Honey (lbs)": "{:,.0f}",
            "Natural (lbs)": "{:,.0f}",
            "Pilado (lbs)": "{:,.0f}",
            "Costo/lb Cereza": "B/.{:,.2f}",
        }),
        use_container_width=True, hide_index=True,
    )

    fig = go.Figure()
    for name in selected_names:
        sr = calculate(all_scenarios[name])
        fig.add_trace(go.Bar(
            name=name,
            x=["Ingresos", "Costos", "Ganancia Neta"],
            y=[sr.total_revenue, sr.total_costs, sr.net_profit],
            text=[fmt_currency(sr.total_revenue), fmt_currency(sr.total_costs), fmt_currency(sr.net_profit)],
            textposition="outside",
        ))
    fig.update_layout(
        barmode="group", title="Comparación de Escenarios",
        yaxis_title="Balboas (B/.)", height=400,
    )
    st.plotly_chart(fig, use_container_width=True)


# ── Pipeline Visual ─────────────────────────────────────────────────────────

def _render_pipeline(r: FinancialResults) -> None:
    """Muestra la cadena de producción como métricas visuales."""
    st.markdown("### 🍒 Cadena de Producción")

    cols = st.columns(4)
    with cols[0]:
        st.metric("Total Cereza", f"{r.total_cherry:,.0f} lbs")
    with cols[1]:
        st.metric("🍯 Seco Honey", f"{r.honey_output_lbs:,.0f} lbs",
                   delta=f"{r.cherry_to_honey_lbs:,.0f} lbs cereza entrada")
    with cols[2]:
        st.metric("☀️ Seco Natural", f"{r.natural_output_lbs:,.0f} lbs",
                   delta=f"{r.cherry_to_natural_lbs:,.0f} lbs cereza entrada")
    with cols[3]:
        st.metric("⚙️ Seco Pilado", f"{r.pilado_output_lbs:,.0f} lbs",
                   delta=f"{r.cherry_to_pilado_lbs:,.0f} lbs cereza entrada")


# ── API Pública ──────────────────────────────────────────────────────────────

def render(results: FinancialResults, base_inputs: dict[str, Any]) -> None:
    # Pipeline visual
    _render_pipeline(results)

    st.divider()

    # KPIs principales
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Ingresos Totales", fmt_currency(results.total_revenue))
    col2.metric("Costos Totales", fmt_currency(results.total_costs))
    col3.metric("Ganancia Neta", fmt_currency(results.net_profit))
    col4.metric("Margen de Ganancia", fmt_percent(results.margin))

    st.divider()

    # Pestañas
    tab_prod, tab_rev, tab_costs, tab_profit, tab_compare, tab_mc = st.tabs([
        "Producción",
        "Ingresos",
        "Costos",
        "Rentabilidad",
        "Comparar Escenarios",
        "Monte Carlo",
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
    with tab_mc:
        montecarlo.render(base_inputs)
