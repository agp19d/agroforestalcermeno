"""Widgets de entrada del panel lateral para el planificador financiero de café.

Este módulo renderiza todos los controles de entrada dentro de
``st.sidebar`` y devuelve los valores recopilados para alimentar
el motor de cálculo.
"""

from __future__ import annotations

from typing import Any

import streamlit as st

import scenarios
from config import DEFAULT_INPUTS


# ── Ayudantes ────────────────────────────────────────────────────────────────

def _get_inputs() -> dict[str, Any]:
    """Recopila todas las claves del estado de sesión que empiezan con ``in_``.

    Returns:
        Un diccionario de valores actuales de widgets adecuado para
        :func:`models.calculate`.
    """
    return {
        k: v for k, v in st.session_state.items() if k.startswith("in_")
    }


def _restore_inputs(data: dict[str, Any]) -> None:
    """Restaura valores guardados en el estado de sesión de Streamlit.

    Args:
        data: Un diccionario de entradas previamente guardado.
    """
    for key, value in data.items():
        if key.startswith("in_"):
            st.session_state[key] = value


# ── Secciones de Entrada ─────────────────────────────────────────────────────

def _render_scenario_management() -> None:
    """Renderiza los controles de guardar / cargar / eliminar escenarios."""
    with st.expander("Guardar / Cargar Escenarios", expanded=False):
        all_scenarios = scenarios.load_all()

        name: str = st.text_input(
            "Nombre del escenario",
            value="Escenario 1",
            key="scenario_name",
        )

        col_save, col_load = st.columns(2)

        if col_save.button("Guardar", use_container_width=True):
            scenarios.save_one(name, _get_inputs())
            st.success(f"Guardado '{name}'")
            st.rerun()

        if all_scenarios:
            selected: str = st.selectbox(
                "Cargar escenario",
                [""] + list(all_scenarios.keys()),
            )
            if col_load.button("Cargar", use_container_width=True) and selected:
                _restore_inputs(all_scenarios[selected])
                st.rerun()
            if (
                st.button("Eliminar seleccionado", use_container_width=True)
                and selected
            ):
                scenarios.delete_one(selected)
                st.rerun()


def _render_plantation_and_land() -> None:
    """Renderiza entradas de tamaño de finca y costos de terreno."""
    d = DEFAULT_INPUTS
    st.subheader("Finca y Terreno")
    st.number_input(
        "Hectáreas Totales",
        min_value=0.0, value=d["total_hectares"], step=0.5,
        key="in_total_hectares",
    )
    st.number_input(
        "Plantas por Hectárea",
        min_value=0, value=d["plants_per_ha"], step=100,
        key="in_plants_per_ha",
    )
    st.number_input(
        "Hectáreas Productivas",
        min_value=0.0, value=d["productive_hectares"], step=0.5,
        key="in_productive_hectares",
    )
    st.number_input(
        "Costo de Terreno / Año (B/.)",
        min_value=0.0, value=d["land_cost"], step=100.0,
        key="in_land_cost",
    )


def _render_yield_estimates() -> None:
    """Renderiza entradas de rendimiento de cereza y ratios de conversión."""
    d = DEFAULT_INPUTS
    st.subheader("Estimaciones de Rendimiento")
    st.number_input(
        "Rendimiento de Cereza (lbs/hectárea)",
        min_value=0.0, value=d["cherry_yield_per_ha"], step=100.0,
        key="in_cherry_yield_per_ha",
    )
    st.number_input(
        "Ratio Cereza a Verde (%)",
        min_value=1.0, max_value=100.0,
        value=d["cherry_to_green"], step=1.0,
        key="in_cherry_to_green",
        help="Típicamente 18-22 %. Peso del grano verde respecto a la cereza.",
    )
    st.number_input(
        "Ratio Verde a Tostado (%)",
        min_value=1.0, max_value=100.0,
        value=d["green_to_roasted"], step=1.0,
        key="in_green_to_roasted",
        help="Típicamente 80-85 %. Pérdida de peso durante el tueste.",
    )


def _render_production_allocation() -> None:
    """Renderiza la asignación porcentual de café verde a cada canal de salida.

    Muestra una advertencia cuando los tres porcentajes no suman 100 %.
    """
    d = DEFAULT_INPUTS
    st.subheader("Asignación de Producción")
    st.markdown("_¿Qué % del café verde va a cada producto?_")

    pct_g: float = st.number_input(
        "Vendido como Verde/Crudo (%)",
        min_value=0.0, max_value=100.0,
        value=d["pct_green"], step=5.0,
        key="in_pct_green",
    )
    pct_p: float = st.number_input(
        "Vendido como Procesado (%)",
        min_value=0.0, max_value=100.0,
        value=d["pct_processed"], step=5.0,
        key="in_pct_processed",
        help="Lavado, natural, honey, etc.",
    )
    pct_r: float = st.number_input(
        "Vendido como Tostado (%)",
        min_value=0.0, max_value=100.0,
        value=d["pct_roasted"], step=5.0,
        key="in_pct_roasted",
    )

    alloc_total: float = pct_g + pct_p + pct_r
    if abs(alloc_total - 100.0) > 0.01:
        st.warning(f"Total de asignación: {alloc_total:.0f} % (debe ser 100 %)")
    else:
        st.success("Asignación: 100 %")


def _render_labor_costs() -> None:
    """Renderiza entradas de mano de obra permanente y temporal."""
    d = DEFAULT_INPUTS
    st.subheader("Costos de Mano de Obra")
    st.number_input(
        "Trabajadores Permanentes",
        min_value=0, value=d["permanent_workers"], step=1,
        key="in_permanent_workers",
    )
    st.number_input(
        "Salario Mensual / Trabajador (B/.)",
        min_value=0.0, value=d["monthly_wage"], step=10.0,
        key="in_monthly_wage",
    )
    st.number_input(
        "Trabajadores Temporales (cosecha)",
        min_value=0, value=d["seasonal_workers"], step=1,
        key="in_seasonal_workers",
    )
    st.number_input(
        "Jornal Diario / Temporal (B/.)",
        min_value=0.0, value=d["seasonal_daily_wage"], step=1.0,
        key="in_seasonal_daily_wage",
    )
    st.number_input(
        "Días de Cosecha",
        min_value=0, value=d["harvest_days"], step=5,
        key="in_harvest_days",
    )
    st.number_input(
        "Prestaciones e Impuestos (%)",
        min_value=0.0, max_value=100.0,
        value=d["labor_benefits"], step=1.0,
        key="in_labor_benefits",
        help="Seguro social, décimo, vacaciones, etc.",
    )


def _render_inputs_and_materials() -> None:
    """Renderiza campos de costos anuales de insumos y materiales."""
    d = DEFAULT_INPUTS
    st.subheader("Insumos y Materiales (Anual)")
    st.number_input(
        "Fertilizante (B/.)",
        min_value=0.0, value=d["fertilizer"], step=100.0,
        key="in_fertilizer",
    )
    st.number_input(
        "Control de Plagas y Enfermedades (B/.)",
        min_value=0.0, value=d["pesticide"], step=100.0,
        key="in_pesticide",
    )
    st.number_input(
        "Plántulas y Resiembra (B/.)",
        min_value=0.0, value=d["seedlings"], step=50.0,
        key="in_seedlings",
    )
    st.number_input(
        "Agua y Riego (B/.)",
        min_value=0.0, value=d["water"], step=100.0,
        key="in_water",
    )
    st.number_input(
        "Herramientas y Equipos (B/.)",
        min_value=0.0, value=d["tools"], step=50.0,
        key="in_tools",
    )
    st.number_input(
        "Combustible y Energía (B/.)",
        min_value=0.0, value=d["fuel"], step=50.0,
        key="in_fuel",
    )


def _render_processing_and_roasting() -> None:
    """Renderiza entradas de costos por libra de procesamiento, tueste y empaque."""
    d = DEFAULT_INPUTS
    st.subheader("Procesamiento y Tueste")
    st.number_input(
        "Costo de Procesamiento (B/./lb verde)",
        min_value=0.0, value=d["processing_cost_lb"], step=0.05,
        key="in_processing_cost_lb",
        help="Despulpado, secado, clasificación.",
    )
    st.number_input(
        "Costo de Tueste (B/./lb tostado)",
        min_value=0.0, value=d["roasting_cost_lb"], step=0.10,
        key="in_roasting_cost_lb",
    )
    st.number_input(
        "Costo de Empaque (B/./lb)",
        min_value=0.0, value=d["packaging_cost_lb"], step=0.05,
        key="in_packaging_cost_lb",
    )


def _render_overhead() -> None:
    """Renderiza entradas de gastos generales, fijos, impuestos y contingencia."""
    d = DEFAULT_INPUTS
    st.subheader("Gastos Generales y Fijos (Anual)")
    st.number_input(
        "Transporte y Logística (B/.)",
        min_value=0.0, value=d["transport"], step=100.0,
        key="in_transport",
    )
    st.number_input(
        "Certificaciones (B/.)",
        min_value=0.0, value=d["certification"], step=100.0,
        key="in_certification",
        help="Orgánico, Comercio Justo, Rainforest Alliance.",
    )
    st.number_input(
        "Administración y Oficina (B/.)",
        min_value=0.0, value=d["admin"], step=100.0,
        key="in_admin",
    )
    st.number_input(
        "Seguros (B/.)",
        min_value=0.0, value=d["insurance"], step=100.0,
        key="in_insurance",
    )
    st.number_input(
        "Mantenimiento y Reparaciones (B/.)",
        min_value=0.0, value=d["maintenance"], step=50.0,
        key="in_maintenance",
    )
    st.number_input(
        "Mercadeo y Ventas (B/.)",
        min_value=0.0, value=d["marketing"], step=50.0,
        key="in_marketing",
    )
    st.number_input(
        "Intereses de Préstamos / Año (B/.)",
        min_value=0.0, value=d["loan_interest"], step=100.0,
        key="in_loan_interest",
    )
    st.number_input(
        "Depreciación (B/.)",
        min_value=0.0, value=d["depreciation"], step=100.0,
        key="in_depreciation",
    )
    st.number_input(
        "Tasa de Impuestos (%)",
        min_value=0.0, max_value=100.0,
        value=d["tax_rate"], step=1.0,
        key="in_tax_rate",
    )
    st.number_input(
        "Contingencia (%)",
        min_value=0.0, max_value=50.0,
        value=d["contingency"], step=1.0,
        key="in_contingency",
        help="Reserva para costos inesperados.",
    )


def _render_sales_prices() -> None:
    """Renderiza entradas de precios de venta por libra para cada tipo de producto."""
    d = DEFAULT_INPUTS
    st.subheader("Precios de Venta")
    st.number_input(
        "Café Verde/Crudo (B/./lb)",
        min_value=0.0, value=d["price_green"], step=0.10,
        key="in_price_green",
    )
    st.number_input(
        "Café Procesado (B/./lb)",
        min_value=0.0, value=d["price_processed"], step=0.10,
        key="in_price_processed",
    )
    st.number_input(
        "Café Tostado (B/./lb)",
        min_value=0.0, value=d["price_roasted"], step=0.10,
        key="in_price_roasted",
    )


# ── API Pública ──────────────────────────────────────────────────────────────

def render() -> dict[str, Any]:
    """Renderiza el panel lateral completo y devuelve los valores de entrada.

    Returns:
        Un diccionario cuyas claves corresponden a las claves de
        widgets de Streamlit (``in_<nombre_param>``).
    """
    with st.sidebar:
        st.header("Entradas del Escenario")
        _render_scenario_management()
        _render_plantation_and_land()
        _render_yield_estimates()
        _render_production_allocation()
        _render_labor_costs()
        _render_inputs_and_materials()
        _render_processing_and_roasting()
        _render_overhead()
        _render_sales_prices()

    return _get_inputs()
