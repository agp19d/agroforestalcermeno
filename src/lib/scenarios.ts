import type { InputValues } from './config';

const STORAGE_KEY = 'agroforestal-scenarios';

type ScenarioMap = Record<string, InputValues>;

export function loadAll(): ScenarioMap {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    return raw ? JSON.parse(raw) : {};
  } catch {
    return {};
  }
}

function saveAll(scenarios: ScenarioMap): void {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(scenarios));
}

export function saveOne(name: string, inputs: InputValues): void {
  const all = loadAll();
  all[name] = inputs;
  saveAll(all);
}

export function deleteOne(name: string): boolean {
  const all = loadAll();
  if (name in all) {
    delete all[name];
    saveAll(all);
    return true;
  }
  return false;
}

export function listNames(): string[] {
  return Object.keys(loadAll());
}
