import { describe, it, expect } from 'vitest';
import { renderHook } from '@testing-library/react';
import { useFinancial } from './use-financial';
import { calculate } from '@/lib/models';
import { DEFAULT_INPUTS } from '@/lib/config';

describe('useFinancial', () => {
  it('returns same result as calculate()', () => {
    const { result } = renderHook(() => useFinancial(DEFAULT_INPUTS));
    const direct = calculate(DEFAULT_INPUTS);
    expect(result.current).toEqual(direct);
  });

  it('memoizes: same input ref yields same output ref', () => {
    const { result, rerender } = renderHook(() => useFinancial(DEFAULT_INPUTS));
    const first = result.current;
    rerender();
    expect(result.current).toBe(first);
  });
});
