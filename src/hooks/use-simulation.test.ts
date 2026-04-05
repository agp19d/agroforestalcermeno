import { describe, it, expect, vi, beforeEach } from 'vitest';
import { renderHook, act } from '@testing-library/react';
import { useSimulation } from './use-simulation';
import { DEFAULT_INPUTS } from '@/lib/config';
import { buildDefaultRanges, type SimulationResults } from '@/lib/simulation';

// Track all created MockWorker instances
const createdWorkers: MockWorker[] = [];

class MockWorker {
  onmessage: ((e: MessageEvent) => void) | null = null;
  onerror: ((e: ErrorEvent) => void) | null = null;
  terminate = vi.fn();

  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  constructor(_url: string | URL, _opts?: WorkerOptions) {
    createdWorkers.push(this);
  }

  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  postMessage(_data: unknown) {
    setTimeout(() => {
      const mockResults: SimulationResults = {
        nIterations: 100,
        metricArrays: {},
        summaryRows: [],
      };
      this.onmessage?.(new MessageEvent('message', { data: mockResults }));
    }, 0);
  }
}

beforeEach(() => {
  createdWorkers.length = 0;
  vi.stubGlobal('Worker', MockWorker);
});

describe('useSimulation', () => {
  it('starts with isRunning=false and results=null', () => {
    const { result } = renderHook(() => useSimulation());
    expect(result.current.isRunning).toBe(false);
    expect(result.current.results).toBeNull();
  });

  it('sets isRunning=true after run()', () => {
    const { result } = renderHook(() => useSimulation());
    const ranges = buildDefaultRanges(DEFAULT_INPUTS);
    act(() => result.current.run(DEFAULT_INPUTS, ranges, 100));
    expect(result.current.isRunning).toBe(true);
  });

  it('receives results and sets isRunning=false', async () => {
    const { result } = renderHook(() => useSimulation());
    const ranges = buildDefaultRanges(DEFAULT_INPUTS);

    await act(async () => {
      result.current.run(DEFAULT_INPUTS, ranges, 100);
      await new Promise((r) => setTimeout(r, 10));
    });

    expect(result.current.isRunning).toBe(false);
    expect(result.current.results).not.toBeNull();
    expect(result.current.results?.nIterations).toBe(100);
  });

  it('terminates previous worker on re-run', () => {
    const { result } = renderHook(() => useSimulation());
    const ranges = buildDefaultRanges(DEFAULT_INPUTS);

    act(() => result.current.run(DEFAULT_INPUTS, ranges, 100));
    act(() => result.current.run(DEFAULT_INPUTS, ranges, 200));

    expect(createdWorkers).toHaveLength(2);
    expect(createdWorkers[0].terminate).toHaveBeenCalled();
  });

  it('terminates worker on unmount', () => {
    const { result, unmount } = renderHook(() => useSimulation());
    const ranges = buildDefaultRanges(DEFAULT_INPUTS);

    act(() => result.current.run(DEFAULT_INPUTS, ranges, 100));
    unmount();

    expect(createdWorkers).toHaveLength(1);
    expect(createdWorkers[0].terminate).toHaveBeenCalled();
  });
});
