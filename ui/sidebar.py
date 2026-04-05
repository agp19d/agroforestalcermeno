"""Sidebar input widgets for the coffee financial planner.

This module renders every input control inside ``st.sidebar`` and
returns the collected values so the main app can feed them into the
calculation engine.
"""

from __future__ import annotations

from typing import Any

import streamlit as st

import scenarios
from config import DEFAULT_INPUTS


# ── Helpers ──────────────────────────────────────────────────────────────────

def _get_inputs() -> dict[str, Any]:
    """Collect all Streamlit session-state keys that start with ``in_``.

    Returns:
        A dictionary of current widget values suitable for
        :func:`models.calculate`.
    """
    return {
        k: v for k, v in st.session_state.items() if k.startswith("in_")
    }


def _restore_inputs(data: dict[str, Any]) -> None:
    """Write saved values back into Streamlit session state.

    Args:
        data: A previously-saved input dictionary.
    """
    for key, value in data.items():
        if key.startswith("in_"):
            st.session_state[key] = value


# ── Section Renderers ────────────────────────────────────────────────────────

def _render_scenario_management() -> None:
    """Render save / load / delete controls for named scenarios."""
    with st.expander("Save / Load Scenarios", expanded=False):
        all_scenarios = scenarios.load_all()

        name: str = st.text_input(
            "Scenario name",
            value="Scenario 1",
            key="scenario_name",
        )

        col_save, col_load = st.columns(2)

        if col_save.button("Save", use_container_width=True):
            scenarios.save_one(name, _get_inputs())
            st.success(f"Saved '{name}'")
            st.rerun()

        if all_scenarios:
            selected: str = st.selectbox(
                "Load scenario",
                [""] + list(all_scenarios.keys()),
            )
            if col_load.button("Load", use_container_width=True) and selected:
                _restore_inputs(all_scenarios[selected])
                st.rerun()
            if (
                st.button("Delete selected", use_container_width=True)
                and selected
            ):
                scenarios.delete_one(selected)
                st.rerun()


def _render_plantation_and_land() -> None:
    """Render inputs for plantation size and land costs."""
    d = DEFAULT_INPUTS
    st.subheader("Plantation & Land")
    st.number_input(
        "Total Hectares",
        min_value=0.0, value=d["total_hectares"], step=0.5,
        key="in_total_hectares",
    )
    st.number_input(
        "Plants per Hectare",
        min_value=0, value=d["plants_per_ha"], step=100,
        key="in_plants_per_ha",
    )
    st.number_input(
        "Productive Hectares",
        min_value=0.0, value=d["productive_hectares"], step=0.5,
        key="in_productive_hectares",
    )
    st.number_input(
        "Land Cost / Year ($)",
        min_value=0.0, value=d["land_cost"], step=100.0,
        key="in_land_cost",
    )


def _render_yield_estimates() -> None:
    """Render inputs for cherry yield and conversion ratios."""
    d = DEFAULT_INPUTS
    st.subheader("Yield Estimates")
    st.number_input(
        "Cherry Yield (lbs/hectare)",
        min_value=0.0, value=d["cherry_yield_per_ha"], step=100.0,
        key="in_cherry_yield_per_ha",
    )
    st.number_input(
        "Cherry to Green Ratio (%)",
        min_value=1.0, max_value=100.0,
        value=d["cherry_to_green"], step=1.0,
        key="in_cherry_to_green",
        help="Typically 18-22 %. Weight of green beans relative to cherry.",
    )
    st.number_input(
        "Green to Roasted Ratio (%)",
        min_value=1.0, max_value=100.0,
        value=d["green_to_roasted"], step=1.0,
        key="in_green_to_roasted",
        help="Typically 80-85 %. Weight loss during roasting.",
    )


def _render_production_allocation() -> None:
    """Render percentage allocation of green coffee to each output channel.

    Shows a warning when the three percentages do not sum to 100 %.
    """
    d = DEFAULT_INPUTS
    st.subheader("Production Allocation")
    st.markdown("_What % of green coffee goes to each output?_")

    pct_g: float = st.number_input(
        "Sold as Green/Raw (%)",
        min_value=0.0, max_value=100.0,
        value=d["pct_green"], step=5.0,
        key="in_pct_green",
    )
    pct_p: float = st.number_input(
        "Sold as Processed (%)",
        min_value=0.0, max_value=100.0,
        value=d["pct_processed"], step=5.0,
        key="in_pct_processed",
        help="Washed, natural, honey, etc.",
    )
    pct_r: float = st.number_input(
        "Sold as Roasted (%)",
        min_value=0.0, max_value=100.0,
        value=d["pct_roasted"], step=5.0,
        key="in_pct_roasted",
    )

    alloc_total: float = pct_g + pct_p + pct_r
    if abs(alloc_total - 100.0) > 0.01:
        st.warning(f"Allocation total: {alloc_total:.0f} % (should be 100 %)")
    else:
        st.success("Allocation: 100 %")


def _render_labor_costs() -> None:
    """Render inputs for permanent and seasonal labour expenses."""
    d = DEFAULT_INPUTS
    st.subheader("Labor Costs")
    st.number_input(
        "Permanent Workers",
        min_value=0, value=d["permanent_workers"], step=1,
        key="in_permanent_workers",
    )
    st.number_input(
        "Monthly Wage / Worker ($)",
        min_value=0.0, value=d["monthly_wage"], step=10.0,
        key="in_monthly_wage",
    )
    st.number_input(
        "Seasonal Workers (harvest)",
        min_value=0, value=d["seasonal_workers"], step=1,
        key="in_seasonal_workers",
    )
    st.number_input(
        "Daily Wage / Seasonal ($)",
        min_value=0.0, value=d["seasonal_daily_wage"], step=1.0,
        key="in_seasonal_daily_wage",
    )
    st.number_input(
        "Harvest Days",
        min_value=0, value=d["harvest_days"], step=5,
        key="in_harvest_days",
    )
    st.number_input(
        "Benefits & Taxes (%)",
        min_value=0.0, max_value=100.0,
        value=d["labor_benefits"], step=1.0,
        key="in_labor_benefits",
        help="Social security, insurance, bonuses.",
    )


def _render_inputs_and_materials() -> None:
    """Render annual inputs-and-materials cost fields."""
    d = DEFAULT_INPUTS
    st.subheader("Inputs & Materials (Annual)")
    st.number_input(
        "Fertilizer ($)",
        min_value=0.0, value=d["fertilizer"], step=100.0,
        key="in_fertilizer",
    )
    st.number_input(
        "Pest & Disease Control ($)",
        min_value=0.0, value=d["pesticide"], step=100.0,
        key="in_pesticide",
    )
    st.number_input(
        "Seedlings & Replanting ($)",
        min_value=0.0, value=d["seedlings"], step=50.0,
        key="in_seedlings",
    )
    st.number_input(
        "Water & Irrigation ($)",
        min_value=0.0, value=d["water"], step=100.0,
        key="in_water",
    )
    st.number_input(
        "Tools & Equipment ($)",
        min_value=0.0, value=d["tools"], step=50.0,
        key="in_tools",
    )
    st.number_input(
        "Fuel & Energy ($)",
        min_value=0.0, value=d["fuel"], step=50.0,
        key="in_fuel",
    )


def _render_processing_and_roasting() -> None:
    """Render per-lb processing, roasting, and packaging cost inputs."""
    d = DEFAULT_INPUTS
    st.subheader("Processing & Roasting")
    st.number_input(
        "Processing Cost ($/lb green)",
        min_value=0.0, value=d["processing_cost_lb"], step=0.05,
        key="in_processing_cost_lb",
        help="Wet milling, drying, sorting.",
    )
    st.number_input(
        "Roasting Cost ($/lb roasted)",
        min_value=0.0, value=d["roasting_cost_lb"], step=0.10,
        key="in_roasting_cost_lb",
    )
    st.number_input(
        "Packaging Cost ($/lb)",
        min_value=0.0, value=d["packaging_cost_lb"], step=0.05,
        key="in_packaging_cost_lb",
    )


def _render_overhead() -> None:
    """Render annual overhead, fixed costs, tax, and contingency inputs."""
    d = DEFAULT_INPUTS
    st.subheader("Overhead & Fixed Costs (Annual)")
    st.number_input(
        "Transport & Logistics ($)",
        min_value=0.0, value=d["transport"], step=100.0,
        key="in_transport",
    )
    st.number_input(
        "Certifications ($)",
        min_value=0.0, value=d["certification"], step=100.0,
        key="in_certification",
        help="Organic, Fair Trade, Rainforest Alliance.",
    )
    st.number_input(
        "Admin & Office ($)",
        min_value=0.0, value=d["admin"], step=100.0,
        key="in_admin",
    )
    st.number_input(
        "Insurance ($)",
        min_value=0.0, value=d["insurance"], step=100.0,
        key="in_insurance",
    )
    st.number_input(
        "Maintenance & Repairs ($)",
        min_value=0.0, value=d["maintenance"], step=50.0,
        key="in_maintenance",
    )
    st.number_input(
        "Marketing & Sales ($)",
        min_value=0.0, value=d["marketing"], step=50.0,
        key="in_marketing",
    )
    st.number_input(
        "Loan Interest / Year ($)",
        min_value=0.0, value=d["loan_interest"], step=100.0,
        key="in_loan_interest",
    )
    st.number_input(
        "Depreciation ($)",
        min_value=0.0, value=d["depreciation"], step=100.0,
        key="in_depreciation",
    )
    st.number_input(
        "Tax Rate (%)",
        min_value=0.0, max_value=100.0,
        value=d["tax_rate"], step=1.0,
        key="in_tax_rate",
    )
    st.number_input(
        "Contingency (%)",
        min_value=0.0, max_value=50.0,
        value=d["contingency"], step=1.0,
        key="in_contingency",
        help="Buffer for unexpected costs.",
    )


def _render_sales_prices() -> None:
    """Render per-lb sales-price inputs for each product type."""
    d = DEFAULT_INPUTS
    st.subheader("Sales Prices")
    st.number_input(
        "Green/Raw Coffee ($/lb)",
        min_value=0.0, value=d["price_green"], step=0.10,
        key="in_price_green",
    )
    st.number_input(
        "Processed Coffee ($/lb)",
        min_value=0.0, value=d["price_processed"], step=0.10,
        key="in_price_processed",
    )
    st.number_input(
        "Roasted Coffee ($/lb)",
        min_value=0.0, value=d["price_roasted"], step=0.10,
        key="in_price_roasted",
    )


# ── Public API ───────────────────────────────────────────────────────────────

def render() -> dict[str, Any]:
    """Render the full sidebar and return the current input values.

    Returns:
        A dictionary whose keys match Streamlit session-state widget
        keys (``in_<param_name>``).
    """
    with st.sidebar:
        st.header("Scenario Inputs")
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
