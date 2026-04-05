import { describe, it, expect } from 'vitest';
import { fmtCurrency, fmtPercent, fmtNumber } from './formatting';

describe('fmtCurrency()', () => {
  it('formats positive values with B/. prefix', () => {
    expect(fmtCurrency(1234.56)).toBe('B/.1,234.56');
  });

  it('formats zero', () => {
    expect(fmtCurrency(0)).toBe('B/.0.00');
  });

  it('formats negative values', () => {
    expect(fmtCurrency(-500)).toBe('B/.-500.00');
  });

  it('respects custom decimals', () => {
    expect(fmtCurrency(1234.56, 0)).toBe('B/.1,235');
  });

  it('formats large values with commas', () => {
    expect(fmtCurrency(1000000)).toBe('B/.1,000,000.00');
  });
});

describe('fmtPercent()', () => {
  it('formats standard percentage', () => {
    expect(fmtPercent(15.5)).toBe('15.5%');
  });

  it('formats zero', () => {
    expect(fmtPercent(0)).toBe('0.0%');
  });

  it('formats negative percentage', () => {
    expect(fmtPercent(-3.2)).toBe('-3.2%');
  });
});

describe('fmtNumber()', () => {
  it('formats with thousands separator', () => {
    expect(fmtNumber(32000)).toBe('32,000');
  });

  it('respects decimal places', () => {
    expect(fmtNumber(3.14159, 2)).toBe('3.14');
  });

  it('formats zero', () => {
    expect(fmtNumber(0)).toBe('0');
  });
});
