"""Agroforestal Cermeño — Calculadora de Producción de Café.

Punto de entrada de la aplicación Streamlit.  Ejecutar con::

    streamlit run app.py
"""

from __future__ import annotations

import streamlit as st

from models import calculate
from ui import dashboard, sidebar


# ── Tema visual ──────────────────────────────────────────────────────────────

_CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;900&family=DM+Sans:wght@400;500;600;700&display=swap');

:root {
    --espresso: #1a0e0a;
    --dark-roast: #2c1810;
    --medium-roast: #4a2c1a;
    --parchment: #f5edd6;
    --gold: #c9a84c;
    --cherry: #b83030;
}

/* ── Main background ── */
.stApp {
    background: linear-gradient(170deg, #0d0805 0%, var(--espresso) 40%, var(--dark-roast) 100%);
}

/* ── Sidebar ── */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, var(--dark-roast) 0%, var(--espresso) 100%);
    border-right: 1px solid rgba(201, 168, 76, 0.12);
}

section[data-testid="stSidebar"] .stMarkdown h1,
section[data-testid="stSidebar"] .stMarkdown h2,
section[data-testid="stSidebar"] .stMarkdown h3 {
    color: var(--gold) !important;
    font-family: 'Playfair Display', serif !important;
    letter-spacing: -0.3px;
}

/* ── Headers ── */
.stApp h1 {
    font-family: 'Playfair Display', serif !important;
    color: var(--parchment) !important;
    font-weight: 900 !important;
    letter-spacing: -0.5px;
}

.stApp h1 span {
    color: var(--gold) !important;
}

.stApp h2, .stApp h3 {
    font-family: 'Playfair Display', serif !important;
    color: var(--gold) !important;
}

/* ── Text ── */
.stApp, .stApp p, .stApp label, .stApp span {
    font-family: 'DM Sans', sans-serif !important;
    color: var(--parchment) !important;
}

/* ── Metrics ── */
[data-testid="stMetric"] {
    background: var(--dark-roast);
    border: 1px solid rgba(201, 168, 76, 0.1);
    border-radius: 12px;
    padding: 1rem 1.2rem;
    transition: all 0.3s ease;
}

[data-testid="stMetric"]:hover {
    border-color: rgba(201, 168, 76, 0.3);
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
}

[data-testid="stMetricLabel"] {
    color: rgba(245, 237, 214, 0.5) !important;
    font-size: 0.75rem !important;
    text-transform: uppercase;
    letter-spacing: 1.5px;
}

[data-testid="stMetricValue"] {
    color: var(--gold) !important;
    font-weight: 700 !important;
}

[data-testid="stMetricDelta"] {
    font-size: 0.75rem !important;
}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    gap: 0;
    border-bottom: 1px solid rgba(201, 168, 76, 0.15);
}

.stTabs [data-baseweb="tab"] {
    color: rgba(245, 237, 214, 0.4) !important;
    font-weight: 600;
    letter-spacing: 0.5px;
    border-bottom: 2px solid transparent;
    padding: 0.6rem 1.2rem;
}

.stTabs [data-baseweb="tab"][aria-selected="true"] {
    color: var(--gold) !important;
    border-bottom-color: var(--gold) !important;
    background: transparent !important;
}

.stTabs [data-baseweb="tab-highlight"] {
    background-color: var(--gold) !important;
}

/* ── Inputs ── */
.stNumberInput input,
.stTextInput input,
.stSelectbox [data-baseweb="select"] {
    background: rgba(0, 0, 0, 0.3) !important;
    border-color: rgba(201, 168, 76, 0.15) !important;
    color: var(--parchment) !important;
    border-radius: 8px !important;
}

.stNumberInput input:focus,
.stTextInput input:focus {
    border-color: var(--gold) !important;
    box-shadow: 0 0 0 2px rgba(201, 168, 76, 0.15) !important;
}

/* ── Buttons ── */
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, var(--gold), #a08030) !important;
    color: var(--espresso) !important;
    border: none !important;
    font-weight: 700 !important;
    border-radius: 8px !important;
}

.stButton > button[kind="primary"]:hover {
    box-shadow: 0 4px 16px rgba(201, 168, 76, 0.3) !important;
}

.stButton > button {
    border-color: rgba(201, 168, 76, 0.2) !important;
    color: var(--parchment) !important;
    border-radius: 8px !important;
}

/* ── Expanders ── */
.streamlit-expanderHeader {
    color: var(--gold) !important;
    font-weight: 600 !important;
}

/* ── Dataframes ── */
[data-testid="stDataFrame"] {
    border-radius: 8px;
    overflow: hidden;
}

/* ── Dividers ── */
hr {
    border-color: rgba(201, 168, 76, 0.1) !important;
}

/* ── Subtitle custom ── */
.subtitle-text {
    font-size: 0.9rem;
    color: rgba(245, 237, 214, 0.4) !important;
    letter-spacing: 3px;
    text-transform: uppercase;
    font-weight: 300;
    margin-top: -1rem;
    margin-bottom: 1.5rem;
}

/* ── Success/Warning/Info boxes ── */
.stAlert {
    border-radius: 8px !important;
}

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(201, 168, 76, 0.2); border-radius: 3px; }

/* ── Noise texture overlay for depth ── */
.stApp::before {
    content: '';
    position: fixed;
    inset: 0;
    background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.85' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)' opacity='0.03'/%3E%3C/svg%3E");
    pointer-events: none;
    z-index: 0;
}
</style>
"""


def main() -> None:
    st.set_page_config(
        page_title="Agroforestal Cermeño",
        page_icon="☕",
        layout="wide",
    )

    st.markdown(_CUSTOM_CSS, unsafe_allow_html=True)

    st.title("Agroforestal Cermeño")
    st.markdown('<p class="subtitle-text">Calculadora de Producción &amp; Rentabilidad Cafetalera</p>', unsafe_allow_html=True)

    inputs = sidebar.render()
    results = calculate(inputs)
    dashboard.render(results, base_inputs=inputs)


if __name__ == "__main__":
    main()
