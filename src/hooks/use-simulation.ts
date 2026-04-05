import { useState, useRef, useEffect, useCallback } from 'react';
import type { InputValues } from '@/lib/config';
import type { VariableRange, SimulationResults } from '@/lib/simulation';
import type { WorkerInput } from '@/lib/simulation.worker';

export function useSimulation() {
  const [isRunning, setIsRunning] = useState(false);
  const [results, setResults] = useState<SimulationResults | null>(null);
  const workerRef = useRef<Worker | null>(null);

  useEffect(() => {
    return () => {
      workerRef.current?.terminate();
    };
  }, []);

  const run = useCallback((inputs: InputValues, ranges: VariableRange[], nIterations: number) => {
    workerRef.current?.terminate();
    const worker = new Worker(
      new URL('../lib/simulation.worker.ts', import.meta.url),
      { type: 'module' },
    );
    workerRef.current = worker;
    setIsRunning(true);
    setResults(null);

    worker.onmessage = (e: MessageEvent<SimulationResults>) => {
      setResults(e.data);
      setIsRunning(false);
    };

    worker.onerror = () => {
      setIsRunning(false);
    };

    const msg: WorkerInput = { inputs, ranges, nIterations };
    worker.postMessage(msg);
  }, []);

  return { isRunning, results, run };
}
