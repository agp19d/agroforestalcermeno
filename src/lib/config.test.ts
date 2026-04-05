import { describe, it, expect } from 'vitest';
import { DEFAULT_INPUTS, PRODUCTS, TRACKED_METRICS, METRIC_LABELS, DEFAULT_VARIABLE_KEYS } from './config';

describe('DEFAULT_INPUTS', () => {
  const keys = Object.keys(DEFAULT_INPUTS);

  it('has 42 fields', () => {
    expect(keys).toHaveLength(42);
  });

  it('all values are finite numbers', () => {
    for (const key of keys) {
      const val = DEFAULT_INPUTS[key as keyof typeof DEFAULT_INPUTS];
      expect(typeof val).toBe('number');
      expect(Number.isFinite(val)).toBe(true);
    }
  });

  it('no values are negative', () => {
    for (const key of keys) {
      expect(DEFAULT_INPUTS[key as keyof typeof DEFAULT_INPUTS]).toBeGreaterThanOrEqual(0);
    }
  });

  it('allocation percentages sum to 100', () => {
    const sum = DEFAULT_INPUTS.pct_cereza + DEFAULT_INPUTS.pct_honey +
      DEFAULT_INPUTS.pct_natural + DEFAULT_INPUTS.pct_pilado;
    expect(sum).toBe(100);
  });
});

describe('PRODUCTS', () => {
  it('has 4 entries', () => {
    expect(PRODUCTS).toHaveLength(4);
  });

  it('has unique keys', () => {
    const keys = PRODUCTS.map((p) => p.key);
    expect(new Set(keys).size).toBe(4);
  });

  it('each product has required fields', () => {
    for (const p of PRODUCTS) {
      expect(p.key).toBeTruthy();
      expect(p.label).toBeTruthy();
      expect(p.icon).toBeTruthy();
      expect(p.desc).toBeTruthy();
    }
  });
});

describe('TRACKED_METRICS', () => {
  it('has 11 entries', () => {
    expect(TRACKED_METRICS).toHaveLength(11);
  });

  it('every metric has a label', () => {
    for (const metric of TRACKED_METRICS) {
      expect(METRIC_LABELS[metric]).toBeTruthy();
    }
  });
});

describe('DEFAULT_VARIABLE_KEYS', () => {
  it('all keys exist in DEFAULT_INPUTS', () => {
    for (const spec of DEFAULT_VARIABLE_KEYS) {
      expect(spec.key in DEFAULT_INPUTS).toBe(true);
    }
  });

  it('all entries have labels', () => {
    for (const spec of DEFAULT_VARIABLE_KEYS) {
      expect(spec.label).toBeTruthy();
    }
  });
});
