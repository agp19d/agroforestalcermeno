import { describe, it, expect, beforeEach } from 'vitest';
import { renderHook, act } from '@testing-library/react';
import { useScenarios } from './use-scenarios';
import { DEFAULT_INPUTS } from '@/lib/config';

beforeEach(() => {
  localStorage.clear();
});

describe('useScenarios', () => {
  it('starts with empty names', () => {
    const { result } = renderHook(() => useScenarios());
    expect(result.current.names).toHaveLength(0);
  });

  it('save adds a scenario', () => {
    const { result } = renderHook(() => useScenarios());
    act(() => result.current.save('test', DEFAULT_INPUTS));
    expect(result.current.names).toContain('test');
  });

  it('load returns saved data', () => {
    const { result } = renderHook(() => useScenarios());
    const custom = { ...DEFAULT_INPUTS, productive_hectares: 42 };
    act(() => result.current.save('test', custom));
    const loaded = result.current.load('test');
    expect(loaded?.productive_hectares).toBe(42);
  });

  it('load returns null for nonexistent scenario', () => {
    const { result } = renderHook(() => useScenarios());
    expect(result.current.load('nope')).toBeNull();
  });

  it('remove deletes a scenario', () => {
    const { result } = renderHook(() => useScenarios());
    act(() => result.current.save('test', DEFAULT_INPUTS));
    act(() => result.current.remove('test'));
    expect(result.current.names).not.toContain('test');
  });
});
