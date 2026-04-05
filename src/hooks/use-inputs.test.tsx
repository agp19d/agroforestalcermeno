import { describe, it, expect } from 'vitest';
import { renderHook, act } from '@testing-library/react';
import { InputsProvider, useInputs } from './use-inputs';
import { DEFAULT_INPUTS } from '@/lib/config';
import type { ReactNode } from 'react';

const wrapper = ({ children }: { children: ReactNode }) => (
  <InputsProvider>{children}</InputsProvider>
);

describe('useInputs', () => {
  it('throws when used outside InputsProvider', () => {
    expect(() => {
      renderHook(() => useInputs());
    }).toThrow('useInputs must be used within InputsProvider');
  });

  it('provides DEFAULT_INPUTS as initial state', () => {
    const { result } = renderHook(() => useInputs(), { wrapper });
    expect(result.current.inputs).toEqual(DEFAULT_INPUTS);
  });

  describe('SET_FIELD', () => {
    it('updates a single field', () => {
      const { result } = renderHook(() => useInputs(), { wrapper });
      act(() => result.current.setField('productive_hectares', 10));
      expect(result.current.inputs.productive_hectares).toBe(10);
    });

    it('leaves other fields unchanged', () => {
      const { result } = renderHook(() => useInputs(), { wrapper });
      act(() => result.current.setField('productive_hectares', 10));
      expect(result.current.inputs.cherry_yield_per_ha).toBe(DEFAULT_INPUTS.cherry_yield_per_ha);
    });

    it('rejects NaN', () => {
      const { result } = renderHook(() => useInputs(), { wrapper });
      act(() => result.current.setField('productive_hectares', NaN));
      expect(result.current.inputs.productive_hectares).toBe(DEFAULT_INPUTS.productive_hectares);
    });

    it('rejects Infinity', () => {
      const { result } = renderHook(() => useInputs(), { wrapper });
      act(() => result.current.setField('productive_hectares', Infinity));
      expect(result.current.inputs.productive_hectares).toBe(DEFAULT_INPUTS.productive_hectares);
    });

    it('rejects -Infinity', () => {
      const { result } = renderHook(() => useInputs(), { wrapper });
      act(() => result.current.setField('productive_hectares', -Infinity));
      expect(result.current.inputs.productive_hectares).toBe(DEFAULT_INPUTS.productive_hectares);
    });
  });

  describe('LOAD_SCENARIO', () => {
    it('loads a full scenario', () => {
      const { result } = renderHook(() => useInputs(), { wrapper });
      const custom = { ...DEFAULT_INPUTS, productive_hectares: 99 };
      act(() => result.current.loadScenario(custom));
      expect(result.current.inputs.productive_hectares).toBe(99);
    });

    it('sanitizes NaN values in loaded scenario', () => {
      const { result } = renderHook(() => useInputs(), { wrapper });
      const tampered = { ...DEFAULT_INPUTS, productive_hectares: NaN };
      act(() => result.current.loadScenario(tampered));
      expect(result.current.inputs.productive_hectares).toBe(DEFAULT_INPUTS.productive_hectares);
    });

    it('sanitizes non-numeric values in loaded scenario', () => {
      const { result } = renderHook(() => useInputs(), { wrapper });
      const tampered = { ...DEFAULT_INPUTS, productive_hectares: 'hacked' as unknown as number };
      act(() => result.current.loadScenario(tampered));
      expect(result.current.inputs.productive_hectares).toBe(DEFAULT_INPUTS.productive_hectares);
    });
  });

  describe('RESET_DEFAULTS', () => {
    it('restores initial state after modifications', () => {
      const { result } = renderHook(() => useInputs(), { wrapper });
      act(() => result.current.setField('productive_hectares', 99));
      act(() => result.current.resetDefaults());
      expect(result.current.inputs).toEqual(DEFAULT_INPUTS);
    });
  });
});
