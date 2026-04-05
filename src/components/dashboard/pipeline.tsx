import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { fmtNumber } from '@/lib/formatting';
import type { FinancialResults } from '@/lib/models';

interface PipelineProps {
  results: FinancialResults;
}

export function Pipeline({ results: r }: PipelineProps) {
  const items = [
    { label: 'Total Cereza', value: `${fmtNumber(r.total_cherry)} lbs`, sub: null },
    { label: 'Seco Honey', value: `${fmtNumber(r.honey_output_lbs)} lbs`, sub: `${fmtNumber(r.cherry_to_honey_lbs)} lbs cereza entrada` },
    { label: 'Seco Natural', value: `${fmtNumber(r.natural_output_lbs)} lbs`, sub: `${fmtNumber(r.cherry_to_natural_lbs)} lbs cereza entrada` },
    { label: 'Seco Pilado', value: `${fmtNumber(r.pilado_output_lbs)} lbs`, sub: `${fmtNumber(r.cherry_to_pilado_lbs)} lbs cereza entrada` },
  ];

  return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
      {items.map((item) => (
        <Card key={item.label}>
          <CardHeader>
            <CardTitle>{item.label}</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-lg font-bold text-[var(--parchment)]">{item.value}</p>
            {item.sub && <p className="text-xs text-[var(--muted-foreground)] mt-1">{item.sub}</p>}
          </CardContent>
        </Card>
      ))}
    </div>
  );
}
