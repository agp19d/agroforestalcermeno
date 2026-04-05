import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { fmtCurrency, fmtPercent } from '@/lib/formatting';
import type { FinancialResults } from '@/lib/models';

interface KpiBarProps {
  results: FinancialResults;
}

export function KpiBar({ results: r }: KpiBarProps) {
  const kpis = [
    { label: 'Ingresos Totales', value: fmtCurrency(r.total_revenue) },
    { label: 'Costos Totales', value: fmtCurrency(r.total_costs) },
    { label: 'Ganancia Neta', value: fmtCurrency(r.net_profit) },
    { label: 'Margen de Ganancia', value: fmtPercent(r.margin) },
  ];

  return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
      {kpis.map((kpi) => (
        <Card key={kpi.label} className="hover:border-[var(--gold)]/30 transition-all hover:shadow-lg hover:shadow-black/30">
          <CardHeader>
            <CardTitle>{kpi.label}</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-xl font-bold text-[var(--gold)]">{kpi.value}</p>
          </CardContent>
        </Card>
      ))}
    </div>
  );
}
