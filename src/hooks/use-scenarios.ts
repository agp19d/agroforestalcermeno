import { useState, useCallback } from 'react';
import * as scenarios from '@/lib/scenarios';
import type { InputValues } from '@/lib/config';

export function useScenarios() {
  const [version, setVersion] = useState(0);

  const all = scenarios.loadAll();
  const names = Object.keys(all);

  const save = useCallback((name: string, inputs: InputValues) => {
    scenarios.saveOne(name, inputs);
    setVersion((v) => v + 1);
  }, []);

  const remove = useCallback((name: string) => {
    scenarios.deleteOne(name);
    setVersion((v) => v + 1);
  }, []);

  const load = useCallback((name: string): InputValues | null => {
    const data = scenarios.loadAll();
    return data[name] ?? null;
  }, []);

  // version is used to trigger re-renders
  void version;

  return { scenarios: all, names, save, remove, load };
}
