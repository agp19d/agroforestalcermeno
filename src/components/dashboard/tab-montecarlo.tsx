import { useState, useMemo } from 'react';
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer,
  LineChart, Line, ReferenceLine,
} from 'recharts';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Checkbox } from '@/components/ui/checkbox';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from '@/components/ui/accordion';
import { useInputs } from '@/hooks/use-inputs';
import { useSimulation } from '@/hooks/use-simulation';
import { buildDefaultRanges, type VariableRange } from '@/lib/simulation';
import { TRACKED_METRICS, METRIC_LABELS } from '@/lib/config';
import { fmtCurrency, fmtPercent } from '@/lib/formatting';

function formatMetricValue(metric: string, value: number): string {
  return metric === 'margin' ? fmtPercent(value) : fmtCurrency(value);
}

export function TabMonteCarlo() {
  const { inputs } = useInputs();
  const { isRunning, results, run } = useSimulation();
  const [nIterations, setNIterations] = useState(5000);
  const [spread, setSpread] = useState(20);
  const [selectedMetric, setSelectedMetric] = useState<string>('net_profit');

  const defaultRanges = useMemo(() => buildDefaultRanges(inputs, spread / 100), [inputs, spread]);
  const [rangeOverrides, setRangeOverrides] = useState<Record<string, Partial<VariableRange>>>({});

  const ranges: VariableRange[] = defaultRanges.map((vr) => ({
    ...vr,
    ...rangeOverrides[vr.key],
  }));

  const handleRun = () => {
    run(inputs, ranges, nIterations);
  };

  // Histogram data
  const histogramData = useMemo(() => {
    if (!results) return [];
    const arr = results.metricArrays[selectedMetric];
    if (!arr || arr.length === 0) return [];
    const min = Math.min(...arr);
    const max = Math.max(...arr);
    const nBins = 60;
    const binWidth = (max - min) / nBins || 1;
    const bins = new Array(nBins).fill(0);
    for (const v of arr) {
      const idx = Math.min(Math.floor((v - min) / binWidth), nBins - 1);
      bins[idx]++;
    }
    return bins.map((count, i) => ({
      x: min + (i + 0.5) * binWidth,
      count,
    }));
  }, [results, selectedMetric]);

  // CDF data
  const cdfData = useMemo(() => {
    if (!results) return [];
    const arr = [...results.metricArrays['net_profit']].sort((a, b) => a - b);
    const step = Math.max(1, Math.floor(arr.length / 500));
    const data: { x: number; y: number }[] = [];
    for (let i = 0; i < arr.length; i += step) {
      data.push({ x: arr[i], y: ((i + 1) / arr.length) * 100 });
    }
    if (data.length === 0 || data[data.length - 1].y !== 100) {
      data.push({ x: arr[arr.length - 1], y: 100 });
    }
    return data;
  }, [results]);

  // Risk metrics from net_profit
  const riskMetrics = useMemo(() => {
    if (!results) return null;
    const arr = results.metricArrays['net_profit'];
    const sorted = [...arr].sort((a, b) => a - b);
    const mean = arr.reduce((a, b) => a + b, 0) / arr.length;
    const negCount = arr.filter((v) => v < 0).length;
    const p5 = sorted[Math.floor(sorted.length * 0.05)];
    const p10 = sorted[Math.floor(sorted.length * 0.10)];
    const p90 = sorted[Math.floor(sorted.length * 0.90)];
    const p95 = sorted[Math.floor(sorted.length * 0.95)];
    return {
      probLoss: (negCount / arr.length) * 100,
      expectedProfit: mean,
      worstCase: p5,
      bestCase: p95,
      p10,
      p90,
    };
  }, [results]);

  return (
    <div>
      <h3 className="text-lg font-bold text-[var(--gold)] mb-2 font-['Playfair_Display',serif]">Simulación Monte Carlo</h3>
      <p className="text-sm text-[var(--muted-foreground)] mb-4">
        Modele la incertidumbre muestreando entradas clave desde distribuciones de probabilidad y ejecutando miles de escenarios.
      </p>

      {/* Configuration */}
      <div className="grid grid-cols-2 gap-4 mb-4">
        <div className="space-y-1">
          <Label>Número de iteraciones</Label>
          <Input
            type="number"
            value={nIterations}
            min={100}
            max={50000}
            step={500}
            onChange={(e) => setNIterations(parseInt(e.target.value) || 5000)}
          />
        </div>
        <div className="space-y-1">
          <Label>Dispersión por defecto (%)</Label>
          <Input
            type="number"
            value={spread}
            min={1}
            max={50}
            step={5}
            onChange={(e) => {
              setSpread(parseInt(e.target.value) || 20);
              setRangeOverrides({});
            }}
          />
        </div>
      </div>

      <h4 className="text-sm font-semibold text-[var(--gold)] mb-2">Rangos de Variables</h4>
      <p className="text-xs text-[var(--muted-foreground)] mb-3">
        Active/desactive variables y ajuste los límites. El valor base proviene de las entradas actuales.
      </p>

      <Accordion type="multiple" className="mb-4">
        {ranges.map((vr) => (
          <AccordionItem key={vr.key} value={vr.key}>
            <AccordionTrigger className="text-xs">
              {vr.label} (base: {vr.base.toLocaleString('en-US', { maximumFractionDigits: 2 })})
            </AccordionTrigger>
            <AccordionContent>
              <div className="space-y-2">
                <div className="flex items-center gap-2">
                  <Checkbox
                    checked={vr.enabled}
                    onCheckedChange={(checked) =>
                      setRangeOverrides((prev) => ({
                        ...prev,
                        [vr.key]: { ...prev[vr.key], enabled: !!checked },
                      }))
                    }
                  />
                  <Label>Incluir en simulación</Label>
                </div>
                <div className="grid grid-cols-2 gap-2">
                  <div className="space-y-1">
                    <Label>Bajo (optimista)</Label>
                    <Input
                      type="number"
                      value={vr.low}
                      step={Math.abs(vr.base * 0.05) || 0.01}
                      onChange={(e) =>
                        setRangeOverrides((prev) => ({
                          ...prev,
                          [vr.key]: { ...prev[vr.key], low: parseFloat(e.target.value) || 0 },
                        }))
                      }
                    />
                  </div>
                  <div className="space-y-1">
                    <Label>Alto (pesimista)</Label>
                    <Input
                      type="number"
                      value={vr.high}
                      step={Math.abs(vr.base * 0.05) || 0.01}
                      onChange={(e) =>
                        setRangeOverrides((prev) => ({
                          ...prev,
                          [vr.key]: { ...prev[vr.key], high: parseFloat(e.target.value) || 0 },
                        }))
                      }
                    />
                  </div>
                </div>
              </div>
            </AccordionContent>
          </AccordionItem>
        ))}
      </Accordion>

      <Button className="w-full mb-6" onClick={handleRun} disabled={isRunning}>
        {isRunning ? 'Ejecutando...' : `Ejecutar ${nIterations.toLocaleString()} Simulaciones`}
      </Button>

      {/* Results */}
      {!results && !isRunning && (
        <div className="text-center py-8 text-[var(--muted-foreground)]">
          Configure los rangos arriba, luego haga clic en Ejecutar Simulaciones.
        </div>
      )}

      {results && riskMetrics && (
        <>
          {/* Risk KPIs */}
          <h4 className="text-sm font-semibold text-[var(--gold)] mb-2">Indicadores de Riesgo</h4>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-4">
            <Card>
              <CardHeader className="p-3 pb-1"><CardTitle className="text-[10px]">P(Pérdida)</CardTitle></CardHeader>
              <CardContent className="p-3 pt-0"><p className="text-base font-bold text-[var(--gold)]">{fmtPercent(riskMetrics.probLoss)}</p></CardContent>
            </Card>
            <Card>
              <CardHeader className="p-3 pb-1"><CardTitle className="text-[10px]">Ganancia Esperada</CardTitle></CardHeader>
              <CardContent className="p-3 pt-0"><p className="text-base font-bold text-[var(--gold)]">{fmtCurrency(riskMetrics.expectedProfit)}</p></CardContent>
            </Card>
            <Card>
              <CardHeader className="p-3 pb-1"><CardTitle className="text-[10px]">Peor Caso (P5)</CardTitle></CardHeader>
              <CardContent className="p-3 pt-0"><p className="text-base font-bold text-[var(--gold)]">{fmtCurrency(riskMetrics.worstCase)}</p></CardContent>
            </Card>
            <Card>
              <CardHeader className="p-3 pb-1"><CardTitle className="text-[10px]">Mejor Caso (P95)</CardTitle></CardHeader>
              <CardContent className="p-3 pt-0"><p className="text-base font-bold text-[var(--gold)]">{fmtCurrency(riskMetrics.bestCase)}</p></CardContent>
            </Card>
          </div>

          {/* Risk level badge */}
          <div className={`text-sm font-medium px-3 py-2 rounded-lg mb-6 ${
            riskMetrics.probLoss > 50 ? 'bg-red-900/30 text-red-400' :
            riskMetrics.probLoss > 20 ? 'bg-yellow-900/30 text-yellow-400' :
            'bg-emerald-900/30 text-emerald-400'
          }`}>
            {riskMetrics.probLoss > 50 ? 'Riesgo alto' : riskMetrics.probLoss > 20 ? 'Riesgo moderado' : 'Riesgo bajo'}
            : {riskMetrics.probLoss.toFixed(1)}% de probabilidad de operar con pérdida.
          </div>

          {/* Histogram + CDF */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
            <div>
              <div className="flex items-center gap-2 mb-2">
                <Label>Métrica:</Label>
                <select
                  className="flex h-8 rounded-lg border border-[var(--input)] bg-black/30 px-2 text-sm text-[var(--parchment)] focus:outline-none"
                  value={selectedMetric}
                  onChange={(e) => setSelectedMetric(e.target.value)}
                >
                  {TRACKED_METRICS.map((m) => (
                    <option key={m} value={m}>{METRIC_LABELS[m]}</option>
                  ))}
                </select>
              </div>
              <ResponsiveContainer width="100%" height={350}>
                <BarChart data={histogramData}>
                  <XAxis dataKey="x" stroke="var(--muted-foreground)" fontSize={10} tickFormatter={(v) => formatMetricValue(selectedMetric, v)} />
                  <YAxis stroke="var(--muted-foreground)" fontSize={10} />
                  <Tooltip
                    contentStyle={{ background: 'var(--dark-roast)', border: '1px solid var(--border)', borderRadius: '8px', color: 'var(--parchment)' }}
                    formatter={(value) => [Number(value), 'Frecuencia']}
                    labelFormatter={(v) => formatMetricValue(selectedMetric, v as number)}
                  />
                  <Bar dataKey="count" fill="#40916c" opacity={0.75} />
                </BarChart>
              </ResponsiveContainer>
            </div>

            <div>
              <h4 className="text-sm font-semibold text-[var(--gold)] mb-2">Probabilidad Acumulada (Ganancia Neta)</h4>
              <ResponsiveContainer width="100%" height={350}>
                <LineChart data={cdfData}>
                  <XAxis dataKey="x" stroke="var(--muted-foreground)" fontSize={10} tickFormatter={(v) => fmtCurrency(v)} />
                  <YAxis stroke="var(--muted-foreground)" fontSize={10} unit="%" />
                  <Tooltip
                    contentStyle={{ background: 'var(--dark-roast)', border: '1px solid var(--border)', borderRadius: '8px', color: 'var(--parchment)' }}
                    formatter={(value) => [`${Number(value).toFixed(1)}%`, 'Probabilidad']}
                    labelFormatter={(v) => fmtCurrency(v as number)}
                  />
                  <ReferenceLine x={0} stroke="#d62828" strokeDasharray="5 5" />
                  <ReferenceLine y={50} stroke="grey" strokeDasharray="3 3" />
                  <Line type="monotone" dataKey="y" stroke="#2d6a4f" strokeWidth={2} dot={false} />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Confidence interval */}
          <h4 className="text-sm font-semibold text-[var(--gold)] mb-2">Intervalo de Confianza 90% (Ganancia Neta)</h4>
          <p className="text-[var(--parchment)] mb-6">
            {fmtCurrency(riskMetrics.p10)} a {fmtCurrency(riskMetrics.p90)}
          </p>

          {/* Summary table */}
          <h4 className="text-sm font-semibold text-[var(--gold)] mb-2">Estadísticas Resumidas</h4>
          <div className="overflow-x-auto">
            <table className="w-full text-xs">
              <thead>
                <tr className="border-b border-[var(--border)]">
                  <th className="text-left py-2 text-[var(--muted-foreground)]">Métrica</th>
                  <th className="text-right py-2 text-[var(--muted-foreground)]">Media</th>
                  <th className="text-right py-2 text-[var(--muted-foreground)]">Desv. Est.</th>
                  <th className="text-right py-2 text-[var(--muted-foreground)]">P5</th>
                  <th className="text-right py-2 text-[var(--muted-foreground)]">P25</th>
                  <th className="text-right py-2 text-[var(--muted-foreground)]">Mediana</th>
                  <th className="text-right py-2 text-[var(--muted-foreground)]">P75</th>
                  <th className="text-right py-2 text-[var(--muted-foreground)]">P95</th>
                  <th className="text-right py-2 text-[var(--muted-foreground)]">P(&lt;0)</th>
                </tr>
              </thead>
              <tbody>
                {results.summaryRows.map((row) => (
                  <tr key={row.metric} className="border-b border-[var(--border)]/50">
                    <td className="py-2 text-[var(--parchment)]">{row.label}</td>
                    <td className="py-2 text-right text-[var(--parchment)]">{fmtCurrency(row.mean)}</td>
                    <td className="py-2 text-right text-[var(--parchment)]">{fmtCurrency(row.std)}</td>
                    <td className="py-2 text-right text-[var(--parchment)]">{fmtCurrency(row.p5)}</td>
                    <td className="py-2 text-right text-[var(--parchment)]">{fmtCurrency(row.p25)}</td>
                    <td className="py-2 text-right text-[var(--parchment)]">{fmtCurrency(row.median)}</td>
                    <td className="py-2 text-right text-[var(--parchment)]">{fmtCurrency(row.p75)}</td>
                    <td className="py-2 text-right text-[var(--parchment)]">{fmtCurrency(row.p95)}</td>
                    <td className="py-2 text-right text-[var(--parchment)]">{fmtPercent(row.probLoss)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </>
      )}
    </div>
  );
}
