# Agroforestal Cermeño — Coffee Production Financial Planner

A Streamlit web application for coffee plantation owners to model production costs, output volumes, revenue, and profitability under different financial scenarios — including Monte Carlo risk analysis.

## Features

- **Production Modeling** — estimate cherry harvest, green coffee yield, and final output in lbs for three product types: raw (green), processed (washed/natural/honey), and roasted.
- **Full Cost Tracking** — labour (permanent and seasonal), inputs and materials, processing, roasting, packaging, land, overhead, taxes, and contingency.
- **Revenue Projections** — per-lb pricing for each bean type with automatic revenue calculation.
- **Profitability Analysis** — gross/net profit, margins, cost per lb, break-even price, revenue and profit per hectare, and a waterfall chart from revenue to net profit.
- **Scenario Management** — save, load, delete, and compare multiple named scenarios side by side with tables and grouped bar charts.
- **Monte Carlo Simulation** — model uncertainty by sampling key inputs from triangular distributions across thousands of iterations. Outputs include:
  - Probability of loss indicator
  - Histograms with mean, P5, and P95 lines
  - Cumulative distribution function (CDF) chart
  - Summary statistics table (mean, std dev, percentiles)

## Project Structure

```
├── app.py              # Entry point — wires sidebar, engine, and dashboard
├── config.py           # Constants, default input values, colour palette
├── models.py           # FinancialResults dataclass and calculation engine
├── simulation.py       # Monte Carlo simulation engine
├── scenarios.py        # JSON-based scenario persistence
├── formatting.py       # Currency, percent, and number formatting helpers
├── ui/
│   ├── __init__.py
│   ├── sidebar.py      # All sidebar input widgets
│   ├── dashboard.py    # Main-area KPIs, tables, and Plotly charts
│   └── montecarlo.py   # Monte Carlo configuration and result charts
├── requirements.txt
└── README.md
```

## Requirements

- Python 3.10+
- Dependencies listed in `requirements.txt`

## Getting Started

1. **Clone the repository**

   ```bash
   git clone https://github.com/agp19d/agroforestalcermeno.git
   cd agroforestalcermeno
   ```

2. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**

   ```bash
   streamlit run app.py
   ```

   The app will open in your browser at `http://localhost:8501`.

## Usage

1. Adjust inputs in the **sidebar** — plantation size, yield estimates, production allocation, labour, materials, processing costs, overhead, and sales prices.
2. View real-time results in the **main area** across six tabs: Production, Revenue, Costs, Profitability, Compare Scenarios, and Monte Carlo.
3. Save scenarios with a name, then load or compare them later.
4. In the **Monte Carlo** tab, configure uncertainty ranges for key variables, run the simulation, and review the probability distributions and risk indicators.

## Input Categories

| Category | Examples |
|---|---|
| Plantation & Land | total hectares, productive hectares, land cost |
| Yield | cherry yield per hectare, cherry-to-green ratio, green-to-roasted ratio |
| Production Allocation | % sold as green, processed, or roasted |
| Labour | permanent workers, seasonal workers, wages, benefits |
| Inputs & Materials | fertilizer, pesticides, seedlings, water, tools, fuel |
| Processing & Roasting | processing cost/lb, roasting cost/lb, packaging cost/lb |
| Overhead & Fixed | transport, certifications, admin, insurance, maintenance, marketing, loans, depreciation |
| Financial | tax rate, contingency buffer |
| Sales Prices | price per lb for green, processed, and roasted coffee |

## License

This project is provided as-is for private use by Agroforestal Cermeño.
