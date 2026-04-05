import { describe, it, expect, beforeEach } from 'vitest';
import { loadAll, saveOne, deleteOne, listNames } from './scenarios';
import { DEFAULT_INPUTS } from './config';

const STORAGE_KEY = 'agroforestal-scenarios';

beforeEach(() => {
  localStorage.clear();
});

describe('CRUD operations', () => {
  it('loadAll returns empty object when storage is empty', () => {
    expect(loadAll()).toEqual({});
  });

  it('saveOne persists a scenario', () => {
    saveOne('test', DEFAULT_INPUTS);
    const all = loadAll();
    expect(Object.keys(all)).toContain('test');
  });

  it('saved scenario has all expected keys', () => {
    saveOne('test', DEFAULT_INPUTS);
    const all = loadAll();
    const scenario = all['test'];
    for (const key of Object.keys(DEFAULT_INPUTS)) {
      expect(scenario).toHaveProperty(key);
    }
  });

  it('deleteOne removes a scenario', () => {
    saveOne('test', DEFAULT_INPUTS);
    expect(deleteOne('test')).toBe(true);
    expect(loadAll()).toEqual({});
  });

  it('deleteOne returns false for nonexistent scenario', () => {
    expect(deleteOne('nonexistent')).toBe(false);
  });

  it('listNames returns scenario names', () => {
    saveOne('alpha', DEFAULT_INPUTS);
    saveOne('beta', DEFAULT_INPUTS);
    const names = listNames();
    expect(names).toContain('alpha');
    expect(names).toContain('beta');
  });

  it('multiple save/delete cycle', () => {
    saveOne('a', DEFAULT_INPUTS);
    saveOne('b', DEFAULT_INPUTS);
    saveOne('c', DEFAULT_INPUTS);
    deleteOne('b');
    const names = listNames();
    expect(names).toEqual(expect.arrayContaining(['a', 'c']));
    expect(names).not.toContain('b');
  });
});

describe('security: prototype pollution protection', () => {
  it('strips __proto__ keys', () => {
    localStorage.setItem(STORAGE_KEY, JSON.stringify({
      __proto__: { productive_hectares: 999 },
      valid: DEFAULT_INPUTS,
    }));
    const all = loadAll();
    expect(all).not.toHaveProperty('__proto__');
    expect(all).toHaveProperty('valid');
  });

  it('strips constructor key', () => {
    localStorage.setItem(STORAGE_KEY, JSON.stringify({
      constructor: { productive_hectares: 999 },
      valid: DEFAULT_INPUTS,
    }));
    const all = loadAll();
    expect(all).not.toHaveProperty('constructor');
    expect(all).toHaveProperty('valid');
  });

  it('strips prototype key', () => {
    localStorage.setItem(STORAGE_KEY, JSON.stringify({
      prototype: { productive_hectares: 999 },
      valid: DEFAULT_INPUTS,
    }));
    const all = loadAll();
    expect(all).not.toHaveProperty('prototype');
  });
});

describe('security: malformed data handling', () => {
  it('handles non-JSON in localStorage', () => {
    localStorage.setItem(STORAGE_KEY, 'not-json{{{');
    expect(loadAll()).toEqual({});
  });

  it('handles array in localStorage', () => {
    localStorage.setItem(STORAGE_KEY, '[1,2,3]');
    expect(loadAll()).toEqual({});
  });

  it('handles null in localStorage', () => {
    localStorage.setItem(STORAGE_KEY, 'null');
    expect(loadAll()).toEqual({});
  });

  it('handles string in localStorage', () => {
    localStorage.setItem(STORAGE_KEY, '"hello"');
    expect(loadAll()).toEqual({});
  });

  it('handles number in localStorage', () => {
    localStorage.setItem(STORAGE_KEY, '42');
    expect(loadAll()).toEqual({});
  });
});

describe('security: input sanitization', () => {
  it('replaces non-numeric values with defaults', () => {
    const tampered = { ...DEFAULT_INPUTS, productive_hectares: 'hacked' as unknown as number };
    localStorage.setItem(STORAGE_KEY, JSON.stringify({ test: tampered }));
    const all = loadAll();
    expect(all['test'].productive_hectares).toBe(DEFAULT_INPUTS.productive_hectares);
  });

  it('replaces NaN values with defaults', () => {
    // NaN serializes to null in JSON
    const data = { test: { ...DEFAULT_INPUTS } };
    const json = JSON.stringify(data).replace(
      `"productive_hectares":${DEFAULT_INPUTS.productive_hectares}`,
      '"productive_hectares":null'
    );
    localStorage.setItem(STORAGE_KEY, json);
    const all = loadAll();
    expect(all['test'].productive_hectares).toBe(DEFAULT_INPUTS.productive_hectares);
  });

  it('ignores extra keys not in VALID_KEYS', () => {
    const tampered = { ...DEFAULT_INPUTS, evil_key: 12345 };
    localStorage.setItem(STORAGE_KEY, JSON.stringify({ test: tampered }));
    const all = loadAll();
    expect(all['test']).not.toHaveProperty('evil_key');
  });

  it('fills missing keys with defaults', () => {
    const partial = { productive_hectares: 10 };
    localStorage.setItem(STORAGE_KEY, JSON.stringify({ test: partial }));
    const all = loadAll();
    expect(all['test'].productive_hectares).toBe(10);
    expect(all['test'].cherry_yield_per_ha).toBe(DEFAULT_INPUTS.cherry_yield_per_ha);
  });

  it('rejects scenario that is an array', () => {
    localStorage.setItem(STORAGE_KEY, JSON.stringify({ test: [1, 2, 3] }));
    const all = loadAll();
    expect(all).not.toHaveProperty('test');
  });

  it('rejects scenario that is null', () => {
    localStorage.setItem(STORAGE_KEY, JSON.stringify({ test: null }));
    const all = loadAll();
    expect(all).not.toHaveProperty('test');
  });

  it('rejects Infinity values (via JSON they become null)', () => {
    // JSON.stringify converts Infinity to null
    const data = { test: { ...DEFAULT_INPUTS } };
    const json = JSON.stringify(data).replace(
      `"tax_rate":${DEFAULT_INPUTS.tax_rate}`,
      '"tax_rate":null'
    );
    localStorage.setItem(STORAGE_KEY, json);
    const all = loadAll();
    expect(all['test'].tax_rate).toBe(DEFAULT_INPUTS.tax_rate);
  });
});
