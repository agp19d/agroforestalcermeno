"""Widgets de entrada del panel lateral.

Recopila todos los parámetros del escenario: finca, rendimiento,
distribución de cereza, precios, costos de mano de obra, insumos,
procesamiento y gastos generales.
"""

from __future__ import annotations

from typing import Any

import streamlit as st

import scenarios
from config import DEFAULT_INPUTS


def _get_inputs() -> dict[str, Any]:
    return {k: v for k, v in st.session_state.items() if k.startswith("in_")}


def _restore_inputs(data: dict[str, Any]) -> None:
    for key, value in data.items():
        if key.startswith("in_"):
            st.session_state[key] = value


# ── Secciones ────────────────────────────────────────────────────────────────

def _render_scenario_management() -> None:
    with st.expander("💾 Guardar / Cargar Escenarios", expanded=False):
        all_scenarios = scenarios.load_all()
        name = st.text_input("Nombre del escenario", value="Escenario 1", key="scenario_name")
        c1, c2 = st.columns(2)
        if c1.button("Guardar", use_container_width=True):
            scenarios.save_one(name, _get_inputs())
            st.success(f"Guardado '{name}'")
            st.rerun()
        if all_scenarios:
            selected = st.selectbox("Cargar escenario", [""] + list(all_scenarios.keys()))
            if c2.button("Cargar", use_container_width=True) and selected:
                _restore_inputs(all_scenarios[selected])
                st.rerun()
            if st.button("Eliminar seleccionado", use_container_width=True) and selected:
                scenarios.delete_one(selected)
                st.rerun()


def _render_farm() -> None:
    d = DEFAULT_INPUTS
    st.subheader("🌿 Finca y Terreno")
    st.number_input("Hectáreas Totales", min_value=0.0, value=d["total_hectares"], step=0.5, key="in_total_hectares")
    st.number_input("Hectáreas Productivas", min_value=0.0, value=d["productive_hectares"], step=0.5, key="in_productive_hectares")
    st.number_input("Plantas por Hectárea", min_value=0, value=d["plants_per_ha"], step=100, key="in_plants_per_ha")
    st.number_input("Costo de Terreno / Año (B/.)", min_value=0.0, value=d["land_cost"], step=100.0, key="in_land_cost")


def _render_yield() -> None:
    d = DEFAULT_INPUTS
    st.subheader("📊 Rendimiento")
    st.number_input(
        "Cereza por Hectárea (lbs)",
        min_value=0.0, value=d["cherry_yield_per_ha"], step=100.0,
        key="in_cherry_yield_per_ha",
    )


def _render_allocation() -> None:
    d = DEFAULT_INPUTS
    st.subheader("🍒 Distribución de Cereza")
    st.caption("¿Qué % de la cereza va a cada destino?")

    pct_c = st.number_input("Vendida como Cereza (%)", min_value=0.0, max_value=100.0, value=d["pct_cereza"], step=5.0, key="in_pct_cereza")
    pct_h = st.number_input("Proceso Honey (%)", min_value=0.0, max_value=100.0, value=d["pct_honey"], step=5.0, key="in_pct_honey")
    pct_n = st.number_input("Proceso Natural (%)", min_value=0.0, max_value=100.0, value=d["pct_natural"], step=5.0, key="in_pct_natural")
    pct_p = st.number_input("Proceso Pilado (%)", min_value=0.0, max_value=100.0, value=d["pct_pilado"], step=5.0, key="in_pct_pilado")

    total = pct_c + pct_h + pct_n + pct_p
    if abs(total - 100.0) > 0.01:
        st.warning(f"Total: {total:.0f}% — debe sumar 100%")
    else:
        st.success("Distribución: 100%")


def _render_conversion() -> None:
    d = DEFAULT_INPUTS
    st.subheader("🔄 Ratios de Conversión")
    st.caption("Lbs de producto por cada 100 lbs de cereza")
    st.number_input(
        "Cereza → Seco Honey (%)", min_value=1.0, max_value=100.0,
        value=d["ratio_honey"], step=0.5, key="in_ratio_honey",
        help="Típicamente 20-25%. El mucílago retenido aporta peso.",
    )
    st.number_input(
        "Cereza → Seco Natural (%)", min_value=1.0, max_value=100.0,
        value=d["ratio_natural"], step=0.5, key="in_ratio_natural",
        help="Típicamente 18-22%. Se seca con toda la cereza.",
    )
    st.number_input(
        "Cereza → Seco Pilado (%)", min_value=1.0, max_value=100.0,
        value=d["ratio_pilado"], step=0.5, key="in_ratio_pilado",
        help="Típicamente 16-20%. Mayor pérdida por lavado y despulpado.",
    )


def _render_prices() -> None:
    d = DEFAULT_INPUTS
    st.subheader("💰 Precios de Venta")
    st.number_input("Cereza (B/./lb)", min_value=0.0, value=d["price_cereza"], step=0.10, key="in_price_cereza")
    st.number_input("Seco Honey (B/./lb)", min_value=0.0, value=d["price_honey"], step=0.10, key="in_price_honey")
    st.number_input("Seco Natural (B/./lb)", min_value=0.0, value=d["price_natural"], step=0.10, key="in_price_natural")
    st.number_input("Seco Pilado (B/./lb)", min_value=0.0, value=d["price_pilado"], step=0.10, key="in_price_pilado")


def _render_labor() -> None:
    d = DEFAULT_INPUTS
    st.subheader("👷 Mano de Obra")
    st.number_input("Trabajadores Permanentes", min_value=0, value=d["permanent_workers"], step=1, key="in_permanent_workers")
    st.number_input("Salario Mensual / Trabajador (B/.)", min_value=0.0, value=d["monthly_wage"], step=10.0, key="in_monthly_wage")
    st.number_input("Trabajadores Temporales", min_value=0, value=d["seasonal_workers"], step=1, key="in_seasonal_workers")
    st.number_input("Jornal Diario / Temporal (B/.)", min_value=0.0, value=d["seasonal_daily_wage"], step=1.0, key="in_seasonal_daily_wage")
    st.number_input("Días de Cosecha", min_value=0, value=d["harvest_days"], step=5, key="in_harvest_days")
    st.number_input("Prestaciones (%)", min_value=0.0, max_value=100.0, value=d["labor_benefits"], step=1.0, key="in_labor_benefits", help="INSS, décimo, vacaciones, etc.")


def _render_inputs_materials() -> None:
    d = DEFAULT_INPUTS
    st.subheader("🧪 Insumos y Materiales (Anual)")
    st.number_input("Fertilizante (B/.)", min_value=0.0, value=d["fertilizer"], step=100.0, key="in_fertilizer")
    st.number_input("Control de Plagas (B/.)", min_value=0.0, value=d["pesticide"], step=100.0, key="in_pesticide")
    st.number_input("Plántulas y Resiembra (B/.)", min_value=0.0, value=d["seedlings"], step=50.0, key="in_seedlings")
    st.number_input("Agua y Riego (B/.)", min_value=0.0, value=d["water"], step=100.0, key="in_water")
    st.number_input("Herramientas (B/.)", min_value=0.0, value=d["tools"], step=50.0, key="in_tools")
    st.number_input("Combustible y Energía (B/.)", min_value=0.0, value=d["fuel"], step=50.0, key="in_fuel")


def _render_processing() -> None:
    d = DEFAULT_INPUTS
    st.subheader("🏭 Costos de Procesamiento")
    st.caption("Por libra de cereza que entra al proceso")
    st.number_input("Proceso Honey (B/./lb)", min_value=0.0, value=d["cost_honey_lb"], step=0.05, key="in_cost_honey_lb")
    st.number_input("Proceso Natural (B/./lb)", min_value=0.0, value=d["cost_natural_lb"], step=0.05, key="in_cost_natural_lb")
    st.number_input("Proceso Pilado (B/./lb)", min_value=0.0, value=d["cost_pilado_lb"], step=0.05, key="in_cost_pilado_lb")
    st.number_input("Empaque (B/./lb producto)", min_value=0.0, value=d["cost_packaging_lb"], step=0.05, key="in_cost_packaging_lb")


def _render_overhead() -> None:
    d = DEFAULT_INPUTS
    st.subheader("🏢 Gastos Generales (Anual)")
    st.number_input("Transporte (B/.)", min_value=0.0, value=d["transport"], step=100.0, key="in_transport")
    st.number_input("Certificaciones (B/.)", min_value=0.0, value=d["certification"], step=100.0, key="in_certification", help="Orgánico, Comercio Justo, Rainforest Alliance")
    st.number_input("Administración (B/.)", min_value=0.0, value=d["admin"], step=100.0, key="in_admin")
    st.number_input("Seguros (B/.)", min_value=0.0, value=d["insurance"], step=100.0, key="in_insurance")
    st.number_input("Mantenimiento (B/.)", min_value=0.0, value=d["maintenance"], step=50.0, key="in_maintenance")
    st.number_input("Mercadeo (B/.)", min_value=0.0, value=d["marketing"], step=50.0, key="in_marketing")
    st.number_input("Interés de Préstamos (B/.)", min_value=0.0, value=d["loan_interest"], step=100.0, key="in_loan_interest")
    st.number_input("Depreciación (B/.)", min_value=0.0, value=d["depreciation"], step=100.0, key="in_depreciation")
    st.number_input("Tasa de Impuestos (%)", min_value=0.0, max_value=100.0, value=d["tax_rate"], step=1.0, key="in_tax_rate")
    st.number_input("Contingencia (%)", min_value=0.0, max_value=50.0, value=d["contingency"], step=1.0, key="in_contingency", help="Reserva para costos inesperados")


# ── API Pública ──────────────────────────────────────────────────────────────

def render() -> dict[str, Any]:
    with st.sidebar:
        st.header("Parámetros del Escenario")
        _render_scenario_management()
        _render_farm()
        _render_yield()
        _render_allocation()
        _render_conversion()
        _render_prices()
        _render_labor()
        _render_inputs_materials()
        _render_processing()
        _render_overhead()
    return _get_inputs()
