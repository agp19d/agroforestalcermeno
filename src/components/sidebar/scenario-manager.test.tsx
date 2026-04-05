import { describe, it, expect, beforeEach } from 'vitest';
import { screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { ScenarioManager } from './scenario-manager';
import { renderWithProviders } from '@/test/helpers';

beforeEach(() => {
  localStorage.clear();
});

describe('ScenarioManager', () => {
  it('renders scenario name input with default value', () => {
    renderWithProviders(<ScenarioManager />);
    const input = screen.getByDisplayValue('Escenario 1');
    expect(input).toBeInTheDocument();
  });

  it('renders Guardar button', () => {
    renderWithProviders(<ScenarioManager />);
    expect(screen.getByRole('button', { name: 'Guardar' })).toBeInTheDocument();
  });

  it('renders Cargar button', () => {
    renderWithProviders(<ScenarioManager />);
    expect(screen.getByRole('button', { name: 'Cargar' })).toBeInTheDocument();
  });

  it('saves a scenario and shows select dropdown', async () => {
    const user = userEvent.setup();
    renderWithProviders(<ScenarioManager />);

    await user.click(screen.getByRole('button', { name: 'Guardar' }));

    // After saving, the select dropdown should appear
    const select = screen.getByRole('combobox');
    expect(select).toBeInTheDocument();
    expect(screen.getByText('Escenario 1')).toBeInTheDocument();
  });

  it('shows Eliminar button after saving', async () => {
    const user = userEvent.setup();
    renderWithProviders(<ScenarioManager />);

    await user.click(screen.getByRole('button', { name: 'Guardar' }));

    expect(screen.getByRole('button', { name: 'Eliminar seleccionado' })).toBeInTheDocument();
  });

  it('deletes a selected scenario', async () => {
    const user = userEvent.setup();
    renderWithProviders(<ScenarioManager />);

    // Save a scenario
    await user.click(screen.getByRole('button', { name: 'Guardar' }));

    // Select the scenario
    const select = screen.getByRole('combobox');
    await user.selectOptions(select, 'Escenario 1');

    // Delete it
    await user.click(screen.getByRole('button', { name: 'Eliminar seleccionado' }));

    // Select dropdown should disappear (no more scenarios)
    expect(screen.queryByRole('combobox')).not.toBeInTheDocument();
  });
});
