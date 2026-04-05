import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { KpiBar } from './kpi-bar';
import { calculate } from '@/lib/models';
import { DEFAULT_INPUTS } from '@/lib/config';
import { fmtCurrency, fmtPercent } from '@/lib/formatting';

const results = calculate(DEFAULT_INPUTS);

describe('KpiBar', () => {
  it('renders 4 KPI cards', () => {
    render(<KpiBar results={results} />);
    expect(screen.getByText('Ingresos Totales')).toBeInTheDocument();
    expect(screen.getByText('Costos Totales')).toBeInTheDocument();
    expect(screen.getByText('Ganancia Neta')).toBeInTheDocument();
    expect(screen.getByText('Margen de Ganancia')).toBeInTheDocument();
  });

  it('displays formatted revenue', () => {
    render(<KpiBar results={results} />);
    expect(screen.getByText(fmtCurrency(results.total_revenue))).toBeInTheDocument();
  });

  it('displays formatted costs', () => {
    render(<KpiBar results={results} />);
    expect(screen.getByText(fmtCurrency(results.total_costs))).toBeInTheDocument();
  });

  it('displays formatted net profit', () => {
    render(<KpiBar results={results} />);
    expect(screen.getByText(fmtCurrency(results.net_profit))).toBeInTheDocument();
  });

  it('displays formatted margin', () => {
    render(<KpiBar results={results} />);
    expect(screen.getByText(fmtPercent(results.margin))).toBeInTheDocument();
  });
});
