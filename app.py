"""Agroforestal Cermeno — Coffee Production Financial Scenario Planner.

Entry point for the Streamlit application.  Run with::

    streamlit run app.py

This module wires together the sidebar inputs, the calculation engine,
and the dashboard visualisations.  Business logic lives in
:pymod:`models`; UI widgets live in :pymod:`ui.sidebar` and
:pymod:`ui.dashboard`.
"""

from __future__ import annotations

import streamlit as st

from models import calculate
from ui import dashboard, sidebar


def main() -> None:
    """Configure the page and render the full application."""
    st.set_page_config(
        page_title="Agroforestal Cermeno",
        page_icon="☕",
        layout="wide",
    )

    st.title("Agroforestal Cermeno")
    st.markdown("**Coffee Production Financial Scenario Planner**")

    # Collect inputs from the sidebar
    inputs = sidebar.render()

    # Run the financial model
    results = calculate(inputs)

    # Display the dashboard (pass inputs for Monte Carlo tab)
    dashboard.render(results, base_inputs=inputs)


if __name__ == "__main__":
    main()
