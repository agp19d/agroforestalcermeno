"""Agroforestal Cermeño — Planificador Financiero de Producción de Café.

Punto de entrada de la aplicación Streamlit.  Ejecutar con::

    streamlit run app.py

Este módulo conecta las entradas del panel lateral, el motor de
cálculo y las visualizaciones del tablero.  La lógica de negocio
está en :pymod:`models`; los widgets de UI están en :pymod:`ui.sidebar`
y :pymod:`ui.dashboard`.
"""

from __future__ import annotations

import streamlit as st

from models import calculate
from ui import dashboard, sidebar


def main() -> None:
    """Configura la página y renderiza la aplicación completa."""
    st.set_page_config(
        page_title="Agroforestal Cermeño",
        page_icon="☕",
        layout="wide",
    )

    st.title("Agroforestal Cermeño")
    st.markdown("**Planificador Financiero de Producción de Café**")

    # Recoger entradas del panel lateral
    inputs = sidebar.render()

    # Ejecutar el modelo financiero
    results = calculate(inputs)

    # Mostrar el tablero (pasar entradas para la pestaña Monte Carlo)
    dashboard.render(results, base_inputs=inputs)


if __name__ == "__main__":
    main()
