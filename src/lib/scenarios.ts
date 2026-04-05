import { sanitizeInputs, type InputValues } from './config';

const STORAGE_KEY = 'agroforestal-scenarios';

type ScenarioMap = Record<string, InputValues>;

export function loadAll(): ScenarioMap {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return {};
    const parsed = JSON.parse(raw);
    if (parsed == null || typeof parsed !== 'object' || Array.isArray(parsed)) {
      return {};
    }
    // Sanitize each scenario entry, skipping __proto__ and other non-own properties
    const result: ScenarioMap = {};
    for (const name of Object.keys(parsed)) {
      // Security: skip prototype-polluting keys
      if (name === '__proto__' || name === 'constructor' || name === 'prototype') {
        continue;
      }
      const sanitized = sanitizeInputs(parsed[name]);
      if (sanitized) {
        result[name] = sanitized;
      }
    }
    return result;
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
