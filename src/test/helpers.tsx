import { render, type RenderOptions } from '@testing-library/react';
import { InputsProvider } from '@/hooks/use-inputs';
import type { ReactElement } from 'react';

export function renderWithProviders(
  ui: ReactElement,
  options?: Omit<RenderOptions, 'wrapper'>,
) {
  return render(ui, {
    wrapper: ({ children }) => <InputsProvider>{children}</InputsProvider>,
    ...options,
  });
}
