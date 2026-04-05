import { describe, it, expect } from 'vitest';
import { screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { Dashboard } from './dashboard';
import { renderWithProviders } from '@/test/helpers';

describe('Dashboard', () => {
  it('renders the title', () => {
    renderWithProviders(<Dashboard />);
    expect(screen.getByText('Agroforestal Cermeño')).toBeInTheDocument();
  });

  it('renders the subtitle', () => {
    renderWithProviders(<Dashboard />);
    expect(screen.getByText(/Calculadora de Producción/)).toBeInTheDocument();
  });

  it('renders all 6 tab triggers', () => {
    renderWithProviders(<Dashboard />);
    expect(screen.getByRole('tab', { name: 'Producción' })).toBeInTheDocument();
    expect(screen.getByRole('tab', { name: 'Ingresos' })).toBeInTheDocument();
    expect(screen.getByRole('tab', { name: 'Costos' })).toBeInTheDocument();
    expect(screen.getByRole('tab', { name: 'Rentabilidad' })).toBeInTheDocument();
    expect(screen.getByRole('tab', { name: 'Comparar' })).toBeInTheDocument();
    expect(screen.getByRole('tab', { name: 'Monte Carlo' })).toBeInTheDocument();
  });

  it('production tab is selected by default', () => {
    renderWithProviders(<Dashboard />);
    const tab = screen.getByRole('tab', { name: 'Producción' });
    expect(tab).toHaveAttribute('data-state', 'active');
  });

  it('switches tab on click', async () => {
    const user = userEvent.setup();
    renderWithProviders(<Dashboard />);

    const revenueTab = screen.getByRole('tab', { name: 'Ingresos' });
    await user.click(revenueTab);
    expect(revenueTab).toHaveAttribute('data-state', 'active');

    const productionTab = screen.getByRole('tab', { name: 'Producción' });
    expect(productionTab).toHaveAttribute('data-state', 'inactive');
  });

  it('renders KPI cards', () => {
    renderWithProviders(<Dashboard />);
    expect(screen.getByText('Ingresos Totales')).toBeInTheDocument();
    expect(screen.getByText('Costos Totales')).toBeInTheDocument();
    expect(screen.getByText('Ganancia Neta')).toBeInTheDocument();
  });
});
