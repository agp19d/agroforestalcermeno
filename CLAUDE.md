# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

React + TypeScript SPA for Agroforestal Cermeño — a coffee production financial planner for a Panamanian farm. All UI text is in Spanish (Panama). All monetary values are in **Balboas panameños (B/.)**, all weights in **pounds (lbs)**.

## Commands

```bash
# Install dependencies
npm install

# Run dev server
npm run dev

# Production build (must exit 0 with no TS errors)
npm run build

# Preview production build
npm run preview
```

## Architecture

The app follows a clear data-flow pipeline: **sidebar inputs → calculation engine → dashboard output**.

### Business Logic (`src/lib/`)
- **`config.ts`** — `InputValues` interface (42 fields), `DEFAULT_INPUTS`, `PRODUCTS`, colour constants, `TRACKED_METRICS`, `METRIC_LABELS`.
- **`models.ts`** — `FinancialResults` interface + `calculate(inputs): FinancialResults`. Pure arithmetic, no side effects.
- **`simulation.ts`** — Monte Carlo engine. `runSimulation()` samples from triangular distributions using inverse CDF. Returns `SimulationResults` with `metricArrays` and `summaryRows`.
- **`simulation.worker.ts`** — Web Worker entry point. Receives inputs/ranges, calls `runSimulation()`, posts results back.
- **`scenarios.ts`** — localStorage CRUD for named scenarios (`loadAll`, `saveOne`, `deleteOne`, `listNames`).
- **`formatting.ts`** — `fmtCurrency()` (B/. prefix), `fmtPercent()`, `fmtNumber()`.
- **`utils.ts`** — `cn()` helper (clsx + tailwind-merge).

### Hooks (`src/hooks/`)
- **`use-inputs.tsx`** — React context + `useReducer` for `InputValues`. Actions: `SET_FIELD`, `LOAD_SCENARIO`, `RESET_DEFAULTS`.
- **`use-financial.ts`** — `useMemo(() => calculate(inputs), [inputs])`.
- **`use-scenarios.ts`** — Wraps `scenarios.ts` with React state.
- **`use-simulation.ts`** — Web Worker lifecycle (`run`, `isRunning`, `results`).

### Components (`src/components/`)
- **`layout/app-shell.tsx`** — Flexbox layout: 320px sidebar (desktop) or Sheet drawer (mobile).
- **`sidebar/`** — 9 section components + `scenario-manager.tsx` + `sidebar-content.tsx` (accordion wrapper).
- **`dashboard/dashboard.tsx`** — Pipeline, KPI bar, and 6 Tabs container.
- **`dashboard/`** — `kpi-bar.tsx`, `pipeline.tsx`, `tab-production.tsx`, `tab-revenue.tsx`, `tab-costs.tsx`, `tab-profitability.tsx`, `tab-compare.tsx`, `tab-montecarlo.tsx`.
- **`ui/`** — Radix-based primitives: Accordion, Button, Card, Checkbox, Input, Label, Sheet, Tabs.

## Key Conventions

- All inputs are typed via `InputValues` interface — direct property access, no `_get()` helper.
- Production allocation percentages (`pct_cereza`, `pct_honey`, `pct_natural`, `pct_pilado`) must sum to 100%.
- `FinancialResults` is a plain object (interface, not class) — all fields computed in `calculate()`.
- Charts use `COLOURS_PRODUCT` for product breakdowns, `COLOUR_POSITIVE`/`COLOUR_NEGATIVE`/`COLOUR_TOTAL` for waterfall.
- Tailwind CSS v4 with `@tailwindcss/vite` plugin. Theme via CSS custom properties in `src/index.css`.
- Path alias: `@/` maps to `src/`.
