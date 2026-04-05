import type { InputValues } from './config';
import { DEFAULT_VARIABLE_KEYS, TRACKED_METRICS, METRIC_LABELS } from './config';
import type { FinancialResults } from './models';
import { calculate } from './models';

export interface VariableRange {
  key: string;
  label: string;
  low: number;
  base: number;
  high: number;
  enabled: boolean;
}

export function buildDefaultRanges(baseInputs: InputValues, spread = 0.20): VariableRange[] {
  return DEFAULT_VARIABLE_KEYS.map((spec) => {
    const baseVal = baseInputs[spec.key as keyof InputValues] as number;
    const low = Math.round(baseVal * (1 - spread) * 10000) / 10000;
    const high = Math.round(baseVal * (1 + spread) * 10000) / 10000;
    return {
      key: spec.key,
      label: spec.label,
      low,
      base: Math.round(baseVal * 10000) / 10000,
      high,
      enabled: true,
    };
  });
}

function triangular(low: number, mode: number, high: number): number {
  const u = Math.random();
  const fc = (mode - low) / (high - low);
  return u < fc
    ? low + Math.sqrt(u * (high - low) * (mode - low))
    : high - Math.sqrt((1 - u) * (high - low) * (high - mode));
}

function mean(arr: number[]): number {
  let sum = 0;
  for (let i = 0; i < arr.length; i++) sum += arr[i];
  return sum / arr.length;
}

function std(arr: number[], avg: number): number {
  let sum = 0;
  for (let i = 0; i < arr.length; i++) {
    const d = arr[i] - avg;
    sum += d * d;
  }
  return Math.sqrt(sum / arr.length);
}

function percentile(sorted: number[], p: number): number {
  const idx = (p / 100) * (sorted.length - 1);
  const lo = Math.floor(idx);
  const hi = Math.ceil(idx);
  if (lo === hi) return sorted[lo];
  return sorted[lo] + (sorted[hi] - sorted[lo]) * (idx - lo);
}

export interface SummaryRow {
  metric: string;
  label: string;
  mean: number;
  std: number;
  p5: number;
  p25: number;
  median: number;
  p75: number;
  p95: number;
  probLoss: number;
}

export interface SimulationResults {
  nIterations: number;
  metricArrays: Record<string, number[]>;
  summaryRows: SummaryRow[];
}

export function runSimulation(
  baseInputs: InputValues,
  variableRanges: VariableRange[],
  nIterations = 5000,
): SimulationResults {
  const arrays: Record<string, number[]> = {};
  for (const m of TRACKED_METRICS) {
    arrays[m] = new Array(nIterations);
  }

  const activeRanges = variableRanges.filter((vr) => vr.enabled);

  for (let i = 0; i < nIterations; i++) {
    const sampled = { ...baseInputs };

    for (const vr of activeRanges) {
      const lo = Math.min(vr.low, vr.base);
      const hi = Math.max(vr.high, vr.base);
      const mode = Math.max(lo, Math.min(vr.base, hi));
      const value = lo === hi ? lo : triangular(lo, mode, hi);
      (sampled as Record<string, number>)[vr.key] = value;
    }

    const result: FinancialResults = calculate(sampled);
    for (const metric of TRACKED_METRICS) {
      arrays[metric][i] = result[metric as keyof FinancialResults] as number;
    }
  }

  const summaryRows: SummaryRow[] = TRACKED_METRICS.map((metric) => {
    const arr = arrays[metric];
    const avg = mean(arr);
    const sorted = [...arr].sort((a, b) => a - b);
    const negCount = arr.reduce((c, v) => c + (v < 0 ? 1 : 0), 0);
    return {
      metric,
      label: METRIC_LABELS[metric] ?? metric,
      mean: avg,
      std: std(arr, avg),
      p5: percentile(sorted, 5),
      p25: percentile(sorted, 25),
      median: percentile(sorted, 50),
      p75: percentile(sorted, 75),
      p95: percentile(sorted, 95),
      probLoss: (negCount / arr.length) * 100,
    };
  });

  return { nIterations, metricArrays: arrays, summaryRows };
}
