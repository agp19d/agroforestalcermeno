import { describe, it, expect } from 'vitest';
import { screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { NumberField } from './number-field';
import { renderWithProviders } from '@/test/helpers';
import { DEFAULT_INPUTS } from '@/lib/config';

describe('NumberField', () => {
  it('renders label and input', () => {
    renderWithProviders(<NumberField label="Hectáreas" field="productive_hectares" />);
    expect(screen.getByLabelText('Hectáreas')).toBeInTheDocument();
  });

  it('displays current value from context', () => {
    renderWithProviders(<NumberField label="Hectáreas" field="productive_hectares" />);
    const input = screen.getByLabelText('Hectáreas') as HTMLInputElement;
    expect(input.value).toBe(String(DEFAULT_INPUTS.productive_hectares));
  });

  it('input has correct id matching field prop', () => {
    renderWithProviders(<NumberField label="Hectáreas" field="productive_hectares" />);
    const input = screen.getByLabelText('Hectáreas');
    expect(input.id).toBe('productive_hectares');
  });

  it('input type is number', () => {
    renderWithProviders(<NumberField label="Hectáreas" field="productive_hectares" />);
    const input = screen.getByLabelText('Hectáreas') as HTMLInputElement;
    expect(input.type).toBe('number');
  });

  it('updates value on valid input', async () => {
    const user = userEvent.setup();
    renderWithProviders(<NumberField label="Hectáreas" field="productive_hectares" />);
    const input = screen.getByLabelText('Hectáreas') as HTMLInputElement;
    // Triple-click to select all, then type replacement value
    await user.tripleClick(input);
    await user.keyboard('10');
    expect(input.value).toBe('10');
  });

  it('applies step, min, max props', () => {
    renderWithProviders(
      <NumberField label="Test" field="productive_hectares" step={0.5} min={1} max={100} />
    );
    const input = screen.getByLabelText('Test') as HTMLInputElement;
    expect(input.step).toBe('0.5');
    expect(input.min).toBe('1');
    expect(input.max).toBe('100');
  });

  it('renders help text as title attribute', () => {
    renderWithProviders(
      <NumberField label="Hectáreas" field="productive_hectares" help="Tooltip text" />
    );
    expect(screen.getByTitle('Tooltip text')).toBeInTheDocument();
  });
});
