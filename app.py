"""
Agroforestal Cermeño — Coffee Production Financial Scenario Planner

A Streamlit app for coffee plantation owners to model production costs,
output (lbs by bean type), revenue, and profitability under different scenarios.
"""

import json
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

SCENARIOS_FILE = Path(__file__).parent / "scenarios.json"

# ─── Helpers ─────────────────────────────────────────────────────────────────

def fmt(value, prefix="$", decimals=2):
    """Format a number as currency or plain."""
    if prefix == "$":
        return f"${value:,.{decimals}f}"
    if prefix == "%":
        return f"{value:,.{decimals}f}%"
    return f"{value:,.{decimals}f}"


def load_scenarios():
    if SCENARIOS_FILE.exists():
        return json.loads(SCENARIOS_FILE.read_text())
    return {}


def save_scenarios(scenarios):
    SCENARIOS_FILE.write_text(json.dumps(scenarios, indent=2))


def get_inputs():
    """Return a dict of all current sidebar input values."""
    return {k: v for k, v in st.session_state.items() if k.startswith("in_")}


def set_inputs(data: dict):
    """Restore inputs from a saved scenario."""
    for k, v in data.items():
        if k.startswith("in_"):
            st.session_state[k] = v


# ─── Calculation Engine ─────────────────────────────────────────────────────

def calculate(inputs: dict) -> dict:
    g = lambda key, default=0: float(inputs.get(f"in_{key}", default))

    # --- Production ---
    productive_ha = g("productive_hectares")
    cherry_per_ha = g("cherry_yield_per_ha")
    cherry_to_green = g("cherry_to_green") / 100
    green_to_roasted = g("green_to_roasted") / 100

    total_cherry = productive_ha * cherry_per_ha
    total_green = total_cherry * cherry_to_green

    pct_green = g("pct_green") / 100
    pct_processed = g("pct_processed") / 100
    pct_roasted = g("pct_roasted") / 100

    green_sold_lbs = total_green * pct_green
    processed_lbs = total_green * pct_processed
    roasted_input_lbs = total_green * pct_roasted
    roasted_output_lbs = roasted_input_lbs * green_to_roasted

    # --- Revenue ---
    rev_green = green_sold_lbs * g("price_green")
    rev_processed = processed_lbs * g("price_processed")
    rev_roasted = roasted_output_lbs * g("price_roasted")
    total_revenue = rev_green + rev_processed + rev_roasted

    # --- Costs ---
    permanent_labor = g("permanent_workers") * g("monthly_wage") * 12
    seasonal_labor = g("seasonal_workers") * g("seasonal_daily_wage") * g("harvest_days")
    base_labor = permanent_labor + seasonal_labor
    labor_benefits = base_labor * g("labor_benefits") / 100
    total_labor = base_labor + labor_benefits

    inputs_materials = (
        g("fertilizer") + g("pesticide") + g("seedlings") +
        g("water") + g("tools") + g("fuel")
    )

    processing_cost = (processed_lbs + roasted_input_lbs) * g("processing_cost_lb")
    roasting_cost = roasted_output_lbs * g("roasting_cost_lb")
    packaging_cost = (processed_lbs + roasted_output_lbs) * g("packaging_cost_lb")

    land_cost = g("land_cost")

    overhead = (
        g("transport") + g("certification") + g("admin") +
        g("insurance") + g("maintenance") + g("marketing") +
        g("loan_interest") + g("depreciation")
    )

    subtotal_costs = (
        total_labor + inputs_materials + processing_cost + roasting_cost +
        packaging_cost + land_cost + overhead
    )
    contingency_amt = subtotal_costs * g("contingency") / 100
    total_costs = subtotal_costs + contingency_amt

    # --- Profitability ---
    gross_profit = total_revenue - total_costs
    taxes = max(0, gross_profit * g("tax_rate") / 100)
    net_profit = gross_profit - taxes
    margin = (net_profit / total_revenue * 100) if total_revenue > 0 else 0
    cost_per_lb_green = (total_costs / total_green) if total_green > 0 else 0
    rev_per_ha = (total_revenue / productive_ha) if productive_ha > 0 else 0
    profit_per_ha = (net_profit / productive_ha) if productive_ha > 0 else 0
    breakeven = cost_per_lb_green  # price at which green sales = total costs

    return {
        "total_cherry": total_cherry,
        "total_green": total_green,
        "green_sold_lbs": green_sold_lbs,
        "processed_lbs": processed_lbs,
        "roasted_input_lbs": roasted_input_lbs,
        "roasted_output_lbs": roasted_output_lbs,
        "rev_green": rev_green,
        "rev_processed": rev_processed,
        "rev_roasted": rev_roasted,
        "total_revenue": total_revenue,
        "permanent_labor": permanent_labor,
        "seasonal_labor": seasonal_labor,
        "labor_benefits": labor_benefits,
        "total_labor": total_labor,
        "inputs_materials": inputs_materials,
        "processing_cost": processing_cost,
        "roasting_cost": roasting_cost,
        "packaging_cost": packaging_cost,
        "land_cost": land_cost,
        "overhead": overhead,
        "contingency": contingency_amt,
        "total_costs": total_costs,
        "gross_profit": gross_profit,
        "taxes": taxes,
        "net_profit": net_profit,
        "margin": margin,
        "cost_per_lb_green": cost_per_lb_green,
        "rev_per_ha": rev_per_ha,
        "profit_per_ha": profit_per_ha,
        "breakeven": breakeven,
    }


# ─── UI ──────────────────────────────────────────────────────────────────────

def main():
    st.set_page_config(
        page_title="Agroforestal Cermeño",
        page_icon="☕",
        layout="wide",
    )

    st.title("☕ Agroforestal Cermeño")
    st.markdown("**Coffee Production Financial Scenario Planner**")

    # ── Sidebar Inputs ───────────────────────────────────────────────────────
    with st.sidebar:
        st.header("Scenario Inputs")

        # -- Scenario management --
        with st.expander("💾 Save / Load Scenarios", expanded=False):
            scenarios = load_scenarios()
            name = st.text_input("Scenario name", value="Scenario 1", key="scenario_name")
            c1, c2 = st.columns(2)
            if c1.button("Save", use_container_width=True):
                scenarios[name] = get_inputs()
                save_scenarios(scenarios)
                st.success(f"Saved '{name}'")
                st.rerun()
            if scenarios:
                selected = st.selectbox("Load scenario", [""] + list(scenarios.keys()))
                if c2.button("Load", use_container_width=True) and selected:
                    set_inputs(scenarios[selected])
                    st.rerun()
                if st.button("🗑 Delete selected", use_container_width=True) and selected:
                    del scenarios[selected]
                    save_scenarios(scenarios)
                    st.rerun()

        # -- Plantation & Land --
        st.subheader("🌱 Plantation & Land")
        st.number_input("Total Hectares", min_value=0.0, value=5.0, step=0.5, key="in_total_hectares")
        st.number_input("Plants per Hectare", min_value=0, value=5000, step=100, key="in_plants_per_ha")
        st.number_input("Productive Hectares", min_value=0.0, value=4.0, step=0.5, key="in_productive_hectares")
        st.number_input("Land Cost / Year ($)", min_value=0.0, value=2000.0, step=100.0, key="in_land_cost")

        # -- Yield --
        st.subheader("📦 Yield Estimates")
        st.number_input("Cherry Yield (lbs/hectare)", min_value=0.0, value=8000.0, step=100.0, key="in_cherry_yield_per_ha")
        st.number_input("Cherry → Green Ratio (%)", min_value=1.0, max_value=100.0, value=20.0, step=1.0, key="in_cherry_to_green",
                         help="Typically 18-22%. Weight of green beans relative to cherry.")
        st.number_input("Green → Roasted Ratio (%)", min_value=1.0, max_value=100.0, value=82.0, step=1.0, key="in_green_to_roasted",
                         help="Typically 80-85%. Weight loss during roasting.")

        # -- Production Allocation --
        st.subheader("📊 Production Allocation")
        st.markdown("_What % of green coffee goes to each output?_")
        pct_g = st.number_input("Sold as Green/Raw (%)", min_value=0.0, max_value=100.0, value=40.0, step=5.0, key="in_pct_green")
        pct_p = st.number_input("Sold as Processed (%)", min_value=0.0, max_value=100.0, value=30.0, step=5.0, key="in_pct_processed",
                                 help="Washed, natural, honey, etc.")
        pct_r = st.number_input("Sold as Roasted (%)", min_value=0.0, max_value=100.0, value=30.0, step=5.0, key="in_pct_roasted")
        alloc_total = pct_g + pct_p + pct_r
        if abs(alloc_total - 100) > 0.01:
            st.warning(f"Allocation total: {alloc_total:.0f}% (should be 100%)")
        else:
            st.success("Allocation: 100% ✓")

        # -- Labor --
        st.subheader("👷 Labor Costs")
        st.number_input("Permanent Workers", min_value=0, value=3, step=1, key="in_permanent_workers")
        st.number_input("Monthly Wage / Worker ($)", min_value=0.0, value=400.0, step=10.0, key="in_monthly_wage")
        st.number_input("Seasonal Workers (harvest)", min_value=0, value=10, step=1, key="in_seasonal_workers")
        st.number_input("Daily Wage / Seasonal ($)", min_value=0.0, value=15.0, step=1.0, key="in_seasonal_daily_wage")
        st.number_input("Harvest Days", min_value=0, value=60, step=5, key="in_harvest_days")
        st.number_input("Benefits & Taxes (%)", min_value=0.0, max_value=100.0, value=30.0, step=1.0, key="in_labor_benefits",
                         help="Social security, insurance, bonuses")

        # -- Inputs & Materials --
        st.subheader("🧪 Inputs & Materials (Annual)")
        st.number_input("Fertilizer ($)", min_value=0.0, value=3000.0, step=100.0, key="in_fertilizer")
        st.number_input("Pest & Disease Control ($)", min_value=0.0, value=1500.0, step=100.0, key="in_pesticide")
        st.number_input("Seedlings & Replanting ($)", min_value=0.0, value=500.0, step=50.0, key="in_seedlings")
        st.number_input("Water & Irrigation ($)", min_value=0.0, value=1200.0, step=100.0, key="in_water")
        st.number_input("Tools & Equipment ($)", min_value=0.0, value=800.0, step=50.0, key="in_tools")
        st.number_input("Fuel & Energy ($)", min_value=0.0, value=1000.0, step=50.0, key="in_fuel")

        # -- Processing & Roasting --
        st.subheader("🔥 Processing & Roasting")
        st.number_input("Processing Cost ($/lb green)", min_value=0.0, value=0.50, step=0.05, key="in_processing_cost_lb",
                         help="Wet milling, drying, sorting")
        st.number_input("Roasting Cost ($/lb roasted)", min_value=0.0, value=1.50, step=0.10, key="in_roasting_cost_lb")
        st.number_input("Packaging Cost ($/lb)", min_value=0.0, value=0.75, step=0.05, key="in_packaging_cost_lb")

        # -- Overhead --
        st.subheader("🏢 Overhead & Fixed Costs (Annual)")
        st.number_input("Transport & Logistics ($)", min_value=0.0, value=2000.0, step=100.0, key="in_transport")
        st.number_input("Certifications ($)", min_value=0.0, value=1500.0, step=100.0, key="in_certification",
                         help="Organic, Fair Trade, Rainforest Alliance")
        st.number_input("Admin & Office ($)", min_value=0.0, value=1200.0, step=100.0, key="in_admin")
        st.number_input("Insurance ($)", min_value=0.0, value=800.0, step=100.0, key="in_insurance")
        st.number_input("Maintenance & Repairs ($)", min_value=0.0, value=600.0, step=50.0, key="in_maintenance")
        st.number_input("Marketing & Sales ($)", min_value=0.0, value=500.0, step=50.0, key="in_marketing")
        st.number_input("Loan Interest / Year ($)", min_value=0.0, value=0.0, step=100.0, key="in_loan_interest")
        st.number_input("Depreciation ($)", min_value=0.0, value=1000.0, step=100.0, key="in_depreciation")
        st.number_input("Tax Rate (%)", min_value=0.0, max_value=100.0, value=15.0, step=1.0, key="in_tax_rate")
        st.number_input("Contingency (%)", min_value=0.0, max_value=50.0, value=5.0, step=1.0, key="in_contingency",
                         help="Buffer for unexpected costs")

        # -- Sales Prices --
        st.subheader("💰 Sales Prices")
        st.number_input("Green/Raw Coffee ($/lb)", min_value=0.0, value=2.50, step=0.10, key="in_price_green")
        st.number_input("Processed Coffee ($/lb)", min_value=0.0, value=4.00, step=0.10, key="in_price_processed")
        st.number_input("Roasted Coffee ($/lb)", min_value=0.0, value=8.00, step=0.10, key="in_price_roasted")

    # ── Calculations ─────────────────────────────────────────────────────────
    r = calculate(get_inputs())

    # ── Main Area: Results ───────────────────────────────────────────────────

    # Key metrics row
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Revenue", fmt(r["total_revenue"]))
    col2.metric("Total Costs", fmt(r["total_costs"]))
    profit_color = "normal" if r["net_profit"] >= 0 else "inverse"
    col3.metric("Net Profit", fmt(r["net_profit"]))
    col4.metric("Profit Margin", fmt(r["margin"], prefix="%", decimals=1))

    st.divider()

    # ── Production Output ────────────────────────────────────────────────────
    tab_prod, tab_rev, tab_costs, tab_profit, tab_compare = st.tabs(
        ["📦 Production", "💰 Revenue", "📉 Costs", "📈 Profitability", "🔄 Compare Scenarios"]
    )

    with tab_prod:
        st.subheader("Production Output (lbs)")
        pcol1, pcol2 = st.columns([1, 1])

        with pcol1:
            prod_data = {
                "Stage": ["Cherry Harvest", "Green Coffee", "Sold Green/Raw", "Processed", "Roasted (output)"],
                "Pounds (lbs)": [
                    r["total_cherry"], r["total_green"], r["green_sold_lbs"],
                    r["processed_lbs"], r["roasted_output_lbs"],
                ],
            }
            st.dataframe(
                pd.DataFrame(prod_data).style.format({"Pounds (lbs)": "{:,.0f}"}),
                use_container_width=True, hide_index=True,
            )

        with pcol2:
            fig = go.Figure(data=[go.Bar(
                x=["Green/Raw", "Processed", "Roasted"],
                y=[r["green_sold_lbs"], r["processed_lbs"], r["roasted_output_lbs"]],
                marker_color=["#2d6a4f", "#40916c", "#74c69d"],
                text=[f"{v:,.0f}" for v in [r["green_sold_lbs"], r["processed_lbs"], r["roasted_output_lbs"]]],
                textposition="outside",
            )])
            fig.update_layout(title="Output by Bean Type (lbs)", yaxis_title="Pounds", height=350)
            st.plotly_chart(fig, use_container_width=True)

    with tab_rev:
        st.subheader("Revenue Breakdown")
        rcol1, rcol2 = st.columns([1, 1])

        with rcol1:
            rev_data = {
                "Source": ["Green/Raw Sales", "Processed Sales", "Roasted Sales", "TOTAL"],
                "Revenue ($)": [r["rev_green"], r["rev_processed"], r["rev_roasted"], r["total_revenue"]],
            }
            st.dataframe(
                pd.DataFrame(rev_data).style.format({"Revenue ($)": "${:,.2f}"}),
                use_container_width=True, hide_index=True,
            )

        with rcol2:
            fig = go.Figure(data=[go.Pie(
                labels=["Green/Raw", "Processed", "Roasted"],
                values=[r["rev_green"], r["rev_processed"], r["rev_roasted"]],
                marker_colors=["#2d6a4f", "#40916c", "#74c69d"],
                textinfo="label+percent+value",
                texttemplate="%{label}<br>%{percent}<br>$%{value:,.0f}",
            )])
            fig.update_layout(title="Revenue by Product Type", height=350)
            st.plotly_chart(fig, use_container_width=True)

    with tab_costs:
        st.subheader("Cost Breakdown")
        ccol1, ccol2 = st.columns([1, 1])

        with ccol1:
            cost_items = [
                ("Labor (permanent)", r["permanent_labor"]),
                ("Labor (seasonal)", r["seasonal_labor"]),
                ("Labor Benefits & Taxes", r["labor_benefits"]),
                ("Inputs & Materials", r["inputs_materials"]),
                ("Processing", r["processing_cost"]),
                ("Roasting", r["roasting_cost"]),
                ("Packaging", r["packaging_cost"]),
                ("Land", r["land_cost"]),
                ("Overhead & Fixed", r["overhead"]),
                ("Contingency", r["contingency"]),
            ]
            cost_df = pd.DataFrame(cost_items, columns=["Category", "Amount ($)"])
            total_row = pd.DataFrame([("TOTAL", r["total_costs"])], columns=["Category", "Amount ($)"])
            cost_df = pd.concat([cost_df, total_row], ignore_index=True)
            st.dataframe(
                cost_df.style.format({"Amount ($)": "${:,.2f}"}),
                use_container_width=True, hide_index=True,
            )

        with ccol2:
            labels = [c[0] for c in cost_items]
            values = [c[1] for c in cost_items]
            fig = go.Figure(data=[go.Pie(
                labels=labels, values=values,
                textinfo="label+percent",
                hole=0.35,
            )])
            fig.update_layout(title="Cost Distribution", height=400)
            st.plotly_chart(fig, use_container_width=True)

    with tab_profit:
        st.subheader("Profitability Analysis")

        p1, p2, p3, p4 = st.columns(4)
        p1.metric("Gross Profit", fmt(r["gross_profit"]))
        p2.metric("Taxes", fmt(r["taxes"]))
        p3.metric("Cost / lb (green)", fmt(r["cost_per_lb_green"]))
        p4.metric("Break-even ($/lb green)", fmt(r["breakeven"]))

        p5, p6 = st.columns(2)
        p5.metric("Revenue / Hectare", fmt(r["rev_per_ha"]))
        p6.metric("Profit / Hectare", fmt(r["profit_per_ha"]))

        # Waterfall chart
        fig = go.Figure(go.Waterfall(
            x=["Revenue", "Labor", "Inputs", "Processing", "Roasting",
               "Packaging", "Land", "Overhead", "Contingency", "Taxes", "Net Profit"],
            y=[r["total_revenue"],
               -r["total_labor"], -r["inputs_materials"], -r["processing_cost"],
               -r["roasting_cost"], -r["packaging_cost"], -r["land_cost"],
               -r["overhead"], -r["contingency"], -r["taxes"], 0],
            measure=["absolute", "relative", "relative", "relative", "relative",
                      "relative", "relative", "relative", "relative", "relative", "total"],
            connector={"line": {"color": "rgba(0,0,0,0.1)"}},
            increasing={"marker": {"color": "#2d6a4f"}},
            decreasing={"marker": {"color": "#d62828"}},
            totals={"marker": {"color": "#1d3557"}},
            textposition="outside",
            text=[fmt(abs(v)) for v in [
                r["total_revenue"], r["total_labor"], r["inputs_materials"],
                r["processing_cost"], r["roasting_cost"], r["packaging_cost"],
                r["land_cost"], r["overhead"], r["contingency"], r["taxes"], r["net_profit"]
            ]],
        ))
        fig.update_layout(title="Revenue → Net Profit Waterfall", height=450, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    with tab_compare:
        st.subheader("Compare Saved Scenarios")
        scenarios = load_scenarios()
        if len(scenarios) < 2:
            st.info("Save at least 2 scenarios to compare them side by side.")
        else:
            selected_scenarios = st.multiselect(
                "Select scenarios to compare",
                list(scenarios.keys()),
                default=list(scenarios.keys())[:3],
            )
            if len(selected_scenarios) >= 2:
                comparison_rows = []
                for sname in selected_scenarios:
                    sr = calculate(scenarios[sname])
                    comparison_rows.append({
                        "Scenario": sname,
                        "Revenue ($)": sr["total_revenue"],
                        "Total Costs ($)": sr["total_costs"],
                        "Net Profit ($)": sr["net_profit"],
                        "Margin (%)": sr["margin"],
                        "Green Output (lbs)": sr["green_sold_lbs"],
                        "Processed (lbs)": sr["processed_lbs"],
                        "Roasted (lbs)": sr["roasted_output_lbs"],
                        "Cost/lb Green ($)": sr["cost_per_lb_green"],
                        "Break-even ($/lb)": sr["breakeven"],
                    })
                comp_df = pd.DataFrame(comparison_rows)
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
                    use_container_width=True, hide_index=True,
                )

                # Grouped bar chart
                fig = go.Figure()
                for sname in selected_scenarios:
                    sr = calculate(scenarios[sname])
                    fig.add_trace(go.Bar(
                        name=sname,
                        x=["Revenue", "Costs", "Net Profit"],
                        y=[sr["total_revenue"], sr["total_costs"], sr["net_profit"]],
                        text=[fmt(v) for v in [sr["total_revenue"], sr["total_costs"], sr["net_profit"]]],
                        textposition="outside",
                    ))
                fig.update_layout(
                    barmode="group", title="Scenario Comparison",
                    yaxis_title="USD ($)", height=400,
                )
                st.plotly_chart(fig, use_container_width=True)


if __name__ == "__main__":
    main()
