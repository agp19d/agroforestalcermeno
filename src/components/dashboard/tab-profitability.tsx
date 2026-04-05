import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell, ReferenceLine } from 'recharts';
import { fmtCurrency, fmtPercent } from '@/lib/formatting';
import { COLOUR_POSITIVE, COLOUR_NEGATIVE, COLOUR_TOTAL, TOOLTIP_STYLE } from '@/lib/config';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import type { FinancialResults } from '@/lib/models';

interface Props { results: FinancialResults }

export function TabProfitability({ results: r }: Props) {
  const kpis = [
    { label: 'Ganancia Bruta', value: fmtCurrency(r.gross_profit) },
    { label: 'Impuestos', value: fmtCurrency(r.taxes) },
    { label: 'Costo / lb Cereza', value: fmtCurrency(r.cost_per_lb_cherry) },
    { label: 'Margen Neto', value: fmtPercent(r.margin) },
    { label: 'Ingresos / Hectárea', value: fmtCurrency(r.rev_per_ha) },
    { label: 'Ganancia / Hectárea', value: fmtCurrency(r.profit_per_ha) },
  ];

  // Waterfall data
  const steps = [
    { name: 'Ingresos', value: r.total_revenue, type: 'positive' as const },
    { name: 'Mano de Obra', value: -r.total_labor, type: 'negative' as const },
    { name: 'Insumos', value: -r.inputs_materials, type: 'negative' as const },
    { name: 'Proc. Honey', value: -r.processing_honey, type: 'negative' as const },
    { name: 'Proc. Natural', value: -r.processing_natural, type: 'negative' as const },
    { name: 'Proc. Pilado', value: -r.processing_pilado, type: 'negative' as const },
    { name: 'Empaque', value: -r.packaging_cost, type: 'negative' as const },
    { name: 'Terreno', value: -r.land_cost, type: 'negative' as const },
    { name: 'Gastos Grales.', value: -r.overhead, type: 'negative' as const },
    { name: 'Contingencia', value: -r.contingency, type: 'negative' as const },
    { name: 'Impuestos', value: -r.taxes, type: 'negative' as const },
  ];

  // Build waterfall bars: invisible base + visible bar
  let running = 0;
  const waterfallData = steps.map((step) => {
    const base = running;
    running += step.value;
    return {
      name: step.name,
      base: step.value >= 0 ? base : base + step.value,
      value: Math.abs(step.value),
      total: running,
      color: step.value >= 0 ? COLOUR_POSITIVE : COLOUR_NEGATIVE,
    };
  });
  waterfallData.push({
    name: 'Ganancia Neta',
    base: 0,
    value: Math.abs(r.net_profit),
    total: r.net_profit,
    color: COLOUR_TOTAL,
  });

  return (
    <div>
      <h3 className="text-lg font-bold text-[var(--gold)] mb-4 font-['Playfair_Display',serif]">Análisis de Rentabilidad</h3>

      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3 mb-6">
        {kpis.map((kpi) => (
          <Card key={kpi.label}>
            <CardHeader className="p-3 pb-1">
              <CardTitle className="text-[10px]">{kpi.label}</CardTitle>
            </CardHeader>
            <CardContent className="p-3 pt-0">
              <p className="text-base font-bold text-[var(--gold)]">{kpi.value}</p>
            </CardContent>
          </Card>
        ))}
      </div>

      <h4 className="text-sm font-semibold text-[var(--gold)] mb-2">Cascada de Ingresos a Ganancia Neta</h4>
      <ResponsiveContainer width="100%" height={400}>
        <BarChart data={waterfallData} barCategoryGap="15%">
          <XAxis dataKey="name" stroke="var(--muted-foreground)" fontSize={10} interval={0} angle={-30} textAnchor="end" height={80} />
          <YAxis stroke="var(--muted-foreground)" fontSize={11} tickFormatter={(v) => `B/.${(v / 1000).toFixed(0)}k`} />
          <Tooltip
            contentStyle={TOOLTIP_STYLE}
            // Recharts does not expose payload.total in its formatter type — cast required
            formatter={(_value, _name, props) => fmtCurrency((props as unknown as { payload: { total: number } }).payload.total)}
            labelFormatter={(label) => label}
          />
          <ReferenceLine y={0} stroke="var(--muted-foreground)" />
          <Bar dataKey="base" stackId="a" fill="transparent" />
          <Bar dataKey="value" stackId="a">
            {waterfallData.map((entry, i) => (
              <Cell key={i} fill={entry.color} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
