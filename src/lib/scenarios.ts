import { DEFAULT_INPUTS, type InputValues } from './config';

const STORAGE_KEY = 'agroforestal-scenarios';

type ScenarioMap = Record<string, InputValues>;

// Security: allowlist of valid InputValues keys to prevent prototype pollution
// and extraneous property injection from untrusted localStorage data.
const VALID_KEYS = new Set<string>(Object.keys(DEFAULT_INPUTS));

/**
 * Sanitize and validate data loaded from localStorage.
 * Strips unknown keys (including __proto__, constructor, etc.),
 * ensures all values are finite numbers, and fills missing keys
 * with defaults.
 */
function sanitizeInputs(raw: unknown): InputValues | null {
  if (raw == null || typeof raw !== 'object' || Array.isArray(raw)) {
    return null;
  }
  const result = { ...DEFAULT_INPUTS };
  const obj = raw as Record<string, unknown>;
  for (const key of VALID_KEYS) {
    if (key in obj) {
      const val = obj[key];
      if (typeof val === 'number' && Number.isFinite(val)) {
        (result as Record<string, number>)[key] = val;
      }
      // Non-numeric or non-finite values fall back to the default
    }
  }
  return result;
}

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
