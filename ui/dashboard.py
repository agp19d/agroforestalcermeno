"""Tablero principal — métricas, tablas y gráficos.

Cada pestaña (Producción, Ingresos, Costos, Rentabilidad, Comparar,
Monte Carlo) es renderizada por una función privada dedicada.
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
    COLOURS_GREEN,
)
from formatting import fmt_currency, fmt_number, fmt_percent
from models import FinancialResults, calculate
from ui import montecarlo


# ── Renderizadores de Pestañas ───────────────────────────────────────────────

def _render_production_tab(r: FinancialResults) -> None:
    """Renderiza la pestaña de Producción con tabla y gráfico de barras.

    Args:
        r: Resultados financieros precalculados del escenario activo.
    """
    st.subheader("Producción (lbs)")
    col_table, col_chart = st.columns(2)

    with col_table:
        prod_df = pd.DataFrame({
            "Etapa": [
                "Cosecha de Cereza",
                "Café Verde",
                "Vendido Verde/Crudo",
                "Procesado",
                "Tostado (producto final)",
            ],
            "Libras (lbs)": [
                r.total_cherry,
                r.total_green,
                r.green_sold_lbs,
                r.processed_lbs,
                r.roasted_output_lbs,
            ],
        })
        st.dataframe(
            prod_df.style.format({"Libras (lbs)": "{:,.0f}"}),
            use_container_width=True,
            hide_index=True,
        )

    with col_chart:
        output_labels = ["Verde/Crudo", "Procesado", "Tostado"]
        output_values = [r.green_sold_lbs, r.processed_lbs, r.roasted_output_lbs]

        fig = go.Figure(data=[go.Bar(
            x=output_labels,
            y=output_values,
            marker_color=COLOURS_GREEN,
            text=[fmt_number(v) for v in output_values],
            textposition="outside",
        )])
        fig.update_layout(
            title="Producción por Tipo de Grano (lbs)",
            yaxis_title="Libras",
            height=350,
        )
        st.plotly_chart(fig, use_container_width=True)


def _render_revenue_tab(r: FinancialResults) -> None:
    """Renderiza la pestaña de Ingresos con tabla resumen y gráfico de torta.

    Args:
        r: Resultados financieros precalculados del escenario activo.
    """
    st.subheader("Desglose de Ingresos")
    col_table, col_chart = st.columns(2)

    with col_table:
        rev_df = pd.DataFrame({
            "Fuente": [
                "Ventas Verde/Crudo",
                "Ventas Procesado",
                "Ventas Tostado",
                "TOTAL",
            ],
            "Ingresos (B/.)": [
                r.rev_green,
                r.rev_processed,
                r.rev_roasted,
                r.total_revenue,
            ],
        })
        st.dataframe(
            rev_df.style.format({"Ingresos (B/.)": "B/.{:,.2f}"}),
            use_container_width=True,
            hide_index=True,
        )

    with col_chart:
        fig = go.Figure(data=[go.Pie(
            labels=["Verde/Crudo", "Procesado", "Tostado"],
            values=[r.rev_green, r.rev_processed, r.rev_roasted],
            marker_colors=COLOURS_GREEN,
            textinfo="label+percent+value",
            texttemplate="%{label}<br>%{percent}<br>B/.%{value:,.0f}",
        )])
        fig.update_layout(title="Ingresos por Tipo de Producto", height=350)
        st.plotly_chart(fig, use_container_width=True)


def _render_costs_tab(r: FinancialResults) -> None:
    """Renderiza la pestaña de Costos con tabla desglosada y gráfico de dona.

    Args:
        r: Resultados financieros precalculados del escenario activo.
    """
    st.subheader("Desglose de Costos")
    col_table, col_chart = st.columns(2)

    cost_items: list[tuple[str, float]] = [
        ("Mano de obra (permanente)", r.permanent_labor),
        ("Mano de obra (temporal)", r.seasonal_labor),
        ("Prestaciones e Impuestos Laborales", r.labor_benefits),
        ("Insumos y Materiales", r.inputs_materials),
        ("Procesamiento", r.processing_cost),
        ("Tueste", r.roasting_cost),
        ("Empaque", r.packaging_cost),
        ("Terreno", r.land_cost),
        ("Gastos Generales y Fijos", r.overhead),
        ("Contingencia", r.contingency),
    ]

    with col_table:
        cost_df = pd.DataFrame(cost_items, columns=["Categoría", "Monto (B/.)"])
        total_row = pd.DataFrame(
            [("TOTAL", r.total_costs)],
            columns=["Categoría", "Monto (B/.)"],
        )
        cost_df = pd.concat([cost_df, total_row], ignore_index=True)
        st.dataframe(
            cost_df.style.format({"Monto (B/.)": "B/.{:,.2f}"}),
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
        fig.update_layout(title="Distribución de Costos", height=400)
        st.plotly_chart(fig, use_container_width=True)


def _render_profitability_tab(r: FinancialResults) -> None:
    """Renderiza la pestaña de Rentabilidad con KPIs y gráfico de cascada.

    Args:
        r: Resultados financieros precalculados del escenario activo.
    """
    st.subheader("Análisis de Rentabilidad")

    # Fila de KPIs 1
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    kpi1.metric("Ganancia Bruta", fmt_currency(r.gross_profit))
    kpi2.metric("Impuestos", fmt_currency(r.taxes))
    kpi3.metric("Costo / lb (verde)", fmt_currency(r.cost_per_lb_green))
    kpi4.metric("Punto de Equilibrio (B/./lb verde)", fmt_currency(r.breakeven))

    # Fila de KPIs 2
    kpi5, kpi6 = st.columns(2)
    kpi5.metric("Ingresos / Hectárea", fmt_currency(r.rev_per_ha))
    kpi6.metric("Ganancia / Hectárea", fmt_currency(r.profit_per_ha))

    # Gráfico de cascada: ingresos menos cada categoría de costo = ganancia neta
    waterfall_labels = [
        "Ingresos", "Mano de Obra", "Insumos", "Procesamiento", "Tueste",
        "Empaque", "Terreno", "Gastos Generales", "Contingencia", "Impuestos",
        "Ganancia Neta",
    ]
    waterfall_values = [
        r.total_revenue,
        -r.total_labor, -r.inputs_materials, -r.processing_cost,
        -r.roasting_cost, -r.packaging_cost, -r.land_cost,
        -r.overhead, -r.contingency, -r.taxes,
        0,  # marcador de posición — Plotly calcula la medida "total"
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
        title="Cascada de Ingresos a Ganancia Neta",
        height=450,
        showlegend=False,
    )
    st.plotly_chart(fig, use_container_width=True)


def _render_compare_tab() -> None:
    """Renderiza la pestaña de comparación de escenarios.

    Carga todos los escenarios guardados, permite al usuario seleccionar
    cuáles comparar, y muestra una tabla resumen más un gráfico de barras.
    """
    st.subheader("Comparar Escenarios Guardados")
    all_scenarios = scenarios.load_all()

    if len(all_scenarios) < 2:
        st.info("Guarda al menos 2 escenarios para compararlos lado a lado.")
        return

    selected_names: list[str] = st.multiselect(
        "Seleccionar escenarios a comparar",
        list(all_scenarios.keys()),
        default=list(all_scenarios.keys())[:3],
    )

    if len(selected_names) < 2:
        return

    # Construir tabla de comparación
    rows: list[dict[str, float | str]] = []
    for name in selected_names:
        sr = calculate(all_scenarios[name])
        rows.append({
            "Escenario": name,
            "Ingresos (B/.)": sr.total_revenue,
            "Costos Totales (B/.)": sr.total_costs,
            "Ganancia Neta (B/.)": sr.net_profit,
            "Margen (%)": sr.margin,
            "Producción Verde (lbs)": sr.green_sold_lbs,
            "Procesado (lbs)": sr.processed_lbs,
            "Tostado (lbs)": sr.roasted_output_lbs,
            "Costo/lb Verde (B/.)": sr.cost_per_lb_green,
            "Punto Equilibrio (B/./lb)": sr.breakeven,
        })

    comp_df = pd.DataFrame(rows)
    st.dataframe(
        comp_df.style.format({
            "Ingresos (B/.)": "B/.{:,.2f}",
            "Costos Totales (B/.)": "B/.{:,.2f}",
            "Ganancia Neta (B/.)": "B/.{:,.2f}",
            "Margen (%)": "{:.1f}%",
            "Producción Verde (lbs)": "{:,.0f}",
            "Procesado (lbs)": "{:,.0f}",
            "Tostado (lbs)": "{:,.0f}",
            "Costo/lb Verde (B/.)": "B/.{:,.2f}",
            "Punto Equilibrio (B/./lb)": "B/.{:,.2f}",
        }),
        use_container_width=True,
        hide_index=True,
    )

    # Gráfico de barras agrupadas
    fig = go.Figure()
    for name in selected_names:
        sr = calculate(all_scenarios[name])
        fig.add_trace(go.Bar(
            name=name,
            x=["Ingresos", "Costos", "Ganancia Neta"],
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
        title="Comparación de Escenarios",
        yaxis_title="Balboas (B/.)",
        height=400,
    )
    st.plotly_chart(fig, use_container_width=True)


# ── API Pública ──────────────────────────────────────────────────────────────

def render(results: FinancialResults, base_inputs: dict[str, Any]) -> None:
    """Renderiza el tablero completo del área principal.

    Muestra KPIs principales en la parte superior, seguido de seis
    pestañas con desgloses detallados, comparación de escenarios y
    simulación Monte Carlo.

    Args:
        results: Los :class:`~models.FinancialResults` del conjunto
            actual de entradas.
        base_inputs: Diccionario de entradas del panel lateral, pasado
            a la pestaña Monte Carlo para muestrear alrededor de estos
            valores.
    """
    # KPIs principales
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Ingresos Totales", fmt_currency(results.total_revenue))
    col2.metric("Costos Totales", fmt_currency(results.total_costs))
    col3.metric("Ganancia Neta", fmt_currency(results.net_profit))
    col4.metric("Margen de Ganancia", fmt_percent(results.margin))

    st.divider()

    # Pestañas detalladas
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
