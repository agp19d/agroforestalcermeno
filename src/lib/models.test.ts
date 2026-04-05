import { describe, it, expect } from 'vitest';
import { calculate } from './models';
import { DEFAULT_INPUTS, type InputValues } from './config';

function inputs(overrides: Partial<InputValues> = {}): InputValues {
  return { ...DEFAULT_INPUTS, ...overrides };
}

describe('calculate()', () => {
  describe('golden test with DEFAULT_INPUTS', () => {
    const r = calculate(DEFAULT_INPUTS);

    it('computes total cherry production', () => {
      // 4 ha * 8000 lbs/ha = 32000 lbs
      expect(r.total_cherry).toBe(32000);
    });

    it('allocates cherry by percentage', () => {
      // 10% cereza, 30% honey, 30% natural, 30% pilado
      expect(r.cherry_sold_lbs).toBe(3200);
      expect(r.cherry_to_honey_lbs).toBe(9600);
      expect(r.cherry_to_natural_lbs).toBe(9600);
      expect(r.cherry_to_pilado_lbs).toBe(9600);
    });

    it('applies conversion ratios to processed products', () => {
      // honey: 9600 * 22/100 = 2112
      expect(r.honey_output_lbs).toBe(2112);
      // natural: 9600 * 20/100 = 1920
      expect(r.natural_output_lbs).toBe(1920);
      // pilado: 9600 * 18/100 = 1728
      expect(r.pilado_output_lbs).toBe(1728);
    });

    it('computes revenue per product', () => {
      expect(r.rev_cereza).toBe(3200 * 0.50);        // 1600
      expect(r.rev_honey).toBe(2112 * 4.50);          // 9504
      expect(r.rev_natural).toBe(1920 * 3.80);        // 7296
      expect(r.rev_pilado).toBe(1728 * 5.00);         // 8640
      expect(r.total_revenue).toBe(1600 + 9504 + 7296 + 8640);
    });

    it('computes labor costs', () => {
      // permanent: 3 * 400 * 12 = 14400
      expect(r.permanent_labor).toBe(14400);
      // seasonal: 10 * 15 * 60 = 9000
      expect(r.seasonal_labor).toBe(9000);
      // benefits: (14400 + 9000) * 30/100 = 7020
      expect(r.labor_benefits).toBe(7020);
      expect(r.total_labor).toBe(14400 + 9000 + 7020);
    });

    it('computes materials/inputs cost', () => {
      // 3000 + 1500 + 500 + 1200 + 800 + 1000 = 8000
      expect(r.inputs_materials).toBe(8000);
    });

    it('computes processing costs', () => {
      expect(r.processing_honey).toBe(9600 * 0.35);
      expect(r.processing_natural).toBe(9600 * 0.25);
      expect(r.processing_pilado).toBe(9600 * 0.50);
      expect(r.total_processing).toBe(9600 * 0.35 + 9600 * 0.25 + 9600 * 0.50);
    });

    it('computes packaging cost', () => {
      // (2112 + 1920 + 1728) * 0.75 = 5760 * 0.75 = 4320
      expect(r.packaging_cost).toBe((2112 + 1920 + 1728) * 0.75);
    });

    it('computes overhead', () => {
      // 2000 + 1500 + 1200 + 800 + 600 + 500 + 0 + 1000 = 7600
      expect(r.overhead).toBe(7600);
    });

    it('applies contingency on subtotal', () => {
      const subtotal = r.total_labor + r.inputs_materials + r.total_processing +
        r.packaging_cost + r.land_cost + r.overhead;
      expect(r.contingency).toBeCloseTo(subtotal * 0.05);
      expect(r.total_costs).toBeCloseTo(subtotal + r.contingency);
    });

    it('computes profitability metrics', () => {
      expect(r.gross_profit).toBeCloseTo(r.total_revenue - r.total_costs);
      expect(r.taxes).toBeCloseTo(Math.max(0, r.gross_profit * 0.15));
      expect(r.net_profit).toBeCloseTo(r.gross_profit - r.taxes);
      expect(r.margin).toBeCloseTo((r.net_profit / r.total_revenue) * 100);
    });

    it('computes per-unit metrics', () => {
      expect(r.cost_per_lb_cherry).toBeCloseTo(r.total_costs / 32000);
      expect(r.rev_per_ha).toBeCloseTo(r.total_revenue / 4);
      expect(r.profit_per_ha).toBeCloseTo(r.net_profit / 4);
    });

    it('returns all expected fields', () => {
      const keys = Object.keys(r);
      expect(keys).toHaveLength(34);
      for (const v of Object.values(r)) {
        expect(Number.isFinite(v)).toBe(true);
      }
    });
  });

  describe('edge cases', () => {
    it('handles zero hectares without division by zero', () => {
      const r = calculate(inputs({ productive_hectares: 0 }));
      expect(r.total_cherry).toBe(0);
      expect(r.total_revenue).toBe(0);
      expect(r.cost_per_lb_cherry).toBe(0);
      expect(r.rev_per_ha).toBe(0);
      expect(r.profit_per_ha).toBe(0);
      expect(r.margin).toBe(0);
    });

    it('handles zero revenue (all prices = 0)', () => {
      const r = calculate(inputs({
        price_cereza: 0, price_honey: 0,
        price_natural: 0, price_pilado: 0,
      }));
      expect(r.total_revenue).toBe(0);
      expect(r.margin).toBe(0);
    });

    it('taxes are never negative (loss scenario)', () => {
      const r = calculate(inputs({
        price_cereza: 0, price_honey: 0,
        price_natural: 0, price_pilado: 0,
      }));
      expect(r.gross_profit).toBeLessThan(0);
      expect(r.taxes).toBe(0);
    });

    it('100% allocation to cereza produces zero processed output', () => {
      const r = calculate(inputs({
        pct_cereza: 100, pct_honey: 0,
        pct_natural: 0, pct_pilado: 0,
      }));
      expect(r.honey_output_lbs).toBe(0);
      expect(r.natural_output_lbs).toBe(0);
      expect(r.pilado_output_lbs).toBe(0);
      expect(r.processing_honey).toBe(0);
      expect(r.processing_natural).toBe(0);
      expect(r.processing_pilado).toBe(0);
      expect(r.cherry_sold_lbs).toBe(32000);
    });

    it('allocation > 100% still computes (no validation)', () => {
      const r = calculate(inputs({
        pct_cereza: 50, pct_honey: 50,
        pct_natural: 50, pct_pilado: 50,
      }));
      // 200% allocation — total cherry allocated = 64000
      expect(r.cherry_sold_lbs + r.cherry_to_honey_lbs +
        r.cherry_to_natural_lbs + r.cherry_to_pilado_lbs).toBe(64000);
      expect(Number.isFinite(r.total_revenue)).toBe(true);
    });

    it('handles very large input values', () => {
      const r = calculate(inputs({
        productive_hectares: 1_000_000,
        cherry_yield_per_ha: 1_000_000,
      }));
      expect(Number.isFinite(r.total_cherry)).toBe(true);
      expect(Number.isFinite(r.total_revenue)).toBe(true);
      expect(Number.isFinite(r.net_profit)).toBe(true);
    });
  });

  describe('boundary values', () => {
    it('zero contingency', () => {
      const r = calculate(inputs({ contingency: 0 }));
      expect(r.contingency).toBe(0);
    });

    it('zero tax rate', () => {
      const r = calculate(inputs({ tax_rate: 0 }));
      expect(r.taxes).toBe(0);
    });

    it('zero labor benefits', () => {
      const r = calculate(inputs({ labor_benefits: 0 }));
      expect(r.labor_benefits).toBe(0);
      expect(r.total_labor).toBe(r.permanent_labor + r.seasonal_labor);
    });

    it('zero workers', () => {
      const r = calculate(inputs({
        permanent_workers: 0, seasonal_workers: 0,
      }));
      expect(r.permanent_labor).toBe(0);
      expect(r.seasonal_labor).toBe(0);
      expect(r.total_labor).toBe(0);
    });
  });
});
