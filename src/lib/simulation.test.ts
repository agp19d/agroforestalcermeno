import { describe, it, expect } from 'vitest';
import { buildDefaultRanges, runSimulation, type VariableRange } from './simulation';
import { DEFAULT_INPUTS, TRACKED_METRICS, DEFAULT_VARIABLE_KEYS } from './config';
import { calculate } from './models';

describe('buildDefaultRanges()', () => {
  it('returns one range per DEFAULT_VARIABLE_KEYS entry', () => {
    const ranges = buildDefaultRanges(DEFAULT_INPUTS);
    expect(ranges).toHaveLength(DEFAULT_VARIABLE_KEYS.length);
  });

  it('computes low/high with default 20% spread', () => {
    const ranges = buildDefaultRanges(DEFAULT_INPUTS);
    for (const range of ranges) {
      const base = DEFAULT_INPUTS[range.key as keyof typeof DEFAULT_INPUTS];
      expect(range.base).toBeCloseTo(base, 2);
      expect(range.low).toBeCloseTo(base * 0.8, 2);
      expect(range.high).toBeCloseTo(base * 1.2, 2);
      expect(range.enabled).toBe(true);
    }
  });

  it('spread=0 gives low === base === high', () => {
    const ranges = buildDefaultRanges(DEFAULT_INPUTS, 0);
    for (const range of ranges) {
      expect(range.low).toBe(range.base);
      expect(range.high).toBe(range.base);
    }
  });

  it('preserves labels from DEFAULT_VARIABLE_KEYS', () => {
    const ranges = buildDefaultRanges(DEFAULT_INPUTS);
    for (let i = 0; i < ranges.length; i++) {
      expect(ranges[i].label).toBe(DEFAULT_VARIABLE_KEYS[i].label);
    }
  });
});

describe('runSimulation()', () => {
  describe('iteration clamping (DoS protection)', () => {
    it('clamps below MIN to 100', () => {
      const result = runSimulation(DEFAULT_INPUTS, [], 10);
      expect(result.nIterations).toBe(100);
    });

    it('clamps above MAX to 50000', () => {
      const result = runSimulation(DEFAULT_INPUTS, [], 100000);
      expect(result.nIterations).toBe(50000);
    });

    it('NaN falls back to 5000', () => {
      const result = runSimulation(DEFAULT_INPUTS, [], NaN);
      expect(result.nIterations).toBe(5000);
    });

    it('floors fractional values', () => {
      const result = runSimulation(DEFAULT_INPUTS, [], 500.9);
      expect(result.nIterations).toBe(500);
    });
  });

  describe('output structure', () => {
    const result = runSimulation(DEFAULT_INPUTS, [], 100);

    it('metricArrays has all TRACKED_METRICS keys', () => {
      for (const metric of TRACKED_METRICS) {
        expect(result.metricArrays[metric]).toBeDefined();
      }
    });

    it('each metric array has correct length', () => {
      for (const metric of TRACKED_METRICS) {
        expect(result.metricArrays[metric]).toHaveLength(100);
      }
    });

    it('summaryRows has 11 entries', () => {
      expect(result.summaryRows).toHaveLength(TRACKED_METRICS.length);
    });

    it('summaryRows have correct fields', () => {
      for (const row of result.summaryRows) {
        expect(row).toHaveProperty('metric');
        expect(row).toHaveProperty('label');
        expect(row).toHaveProperty('mean');
        expect(row).toHaveProperty('std');
        expect(row).toHaveProperty('p5');
        expect(row).toHaveProperty('p25');
        expect(row).toHaveProperty('median');
        expect(row).toHaveProperty('p75');
        expect(row).toHaveProperty('p95');
        expect(row).toHaveProperty('probLoss');
      }
    });
  });

  describe('deterministic mode (all ranges disabled)', () => {
    it('produces identical results every iteration', () => {
      const ranges: VariableRange[] = buildDefaultRanges(DEFAULT_INPUTS).map((r) => ({
        ...r,
        enabled: false,
      }));
      const result = runSimulation(DEFAULT_INPUTS, ranges, 200);

      for (const row of result.summaryRows) {
        // Floating-point arithmetic may produce tiny variance even with identical inputs
        expect(row.std).toBeCloseTo(0, 5);
        expect(row.p5).toBeCloseTo(row.median, 5);
        expect(row.p95).toBeCloseTo(row.median, 5);
        expect(row.mean).toBeCloseTo(row.median, 5);
      }
    });

    it('matches direct calculate() output', () => {
      const ranges = buildDefaultRanges(DEFAULT_INPUTS).map((r) => ({
        ...r,
        enabled: false,
      }));
      const simResult = runSimulation(DEFAULT_INPUTS, ranges, 100);
      const directResult = calculate(DEFAULT_INPUTS);

      const revenueRow = simResult.summaryRows.find((r) => r.metric === 'total_revenue')!;
      expect(revenueRow.mean).toBeCloseTo(directResult.total_revenue);

      const profitRow = simResult.summaryRows.find((r) => r.metric === 'net_profit')!;
      expect(profitRow.mean).toBeCloseTo(directResult.net_profit);
    });
  });

  describe('stochastic mode', () => {
    it('produces variance when ranges are enabled', () => {
      const ranges = buildDefaultRanges(DEFAULT_INPUTS, 0.20);
      const result = runSimulation(DEFAULT_INPUTS, ranges, 1000);

      const profitRow = result.summaryRows.find((r) => r.metric === 'net_profit')!;
      expect(profitRow.std).toBeGreaterThan(0);
      expect(profitRow.p5).toBeLessThan(profitRow.median);
      expect(profitRow.p95).toBeGreaterThan(profitRow.median);
    });
  });

  describe('probLoss', () => {
    it('is 0 when inputs always produce profit', () => {
      // DEFAULT_INPUTS produce a loss, so boost prices to ensure profit
      const profitInputs = {
        ...DEFAULT_INPUTS,
        price_cereza: 5.00, price_honey: 20.00,
        price_natural: 20.00, price_pilado: 25.00,
      };
      const ranges = buildDefaultRanges(profitInputs).map((r) => ({
        ...r,
        enabled: false,
      }));
      const result = runSimulation(profitInputs, ranges, 100);
      const profitRow = result.summaryRows.find((r) => r.metric === 'net_profit')!;
      expect(profitRow.probLoss).toBe(0);
    });

    it('is 100 when inputs always produce loss', () => {
      const lossInputs = {
        ...DEFAULT_INPUTS,
        price_cereza: 0, price_honey: 0,
        price_natural: 0, price_pilado: 0,
      };
      const ranges = buildDefaultRanges(lossInputs).map((r) => ({
        ...r,
        enabled: false,
      }));
      const result = runSimulation(lossInputs, ranges, 100);
      const profitRow = result.summaryRows.find((r) => r.metric === 'net_profit')!;
      expect(profitRow.probLoss).toBe(100);
    });
  });

  describe('performance', () => {
    it('calculate() runs in under 1ms', () => {
      const start = performance.now();
      for (let i = 0; i < 1000; i++) {
        calculate(DEFAULT_INPUTS);
      }
      const elapsed = performance.now() - start;
      // 1000 calls in under 1000ms = each under 1ms
      expect(elapsed).toBeLessThan(1000);
    });

    it('5000 iterations complete in under 5s', () => {
      const ranges = buildDefaultRanges(DEFAULT_INPUTS, 0.20);
      const start = performance.now();
      runSimulation(DEFAULT_INPUTS, ranges, 5000);
      const elapsed = performance.now() - start;
      expect(elapsed).toBeLessThan(5000);
    });
  });
});
