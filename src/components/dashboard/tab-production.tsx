import { BarChart, Bar, XAxis, YAxis, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { fmtNumber } from '@/lib/formatting';
import { COLOURS_PRODUCT, TOOLTIP_STYLE } from '@/lib/config';
import type { FinancialResults } from '@/lib/models';

interface Props { results: FinancialResults }

export function TabProduction({ results: r }: Props) {
  const tableRows = [
    { label: 'Total Cereza Cosechada', value: r.total_cherry },
    { label: 'Cereza Vendida', value: r.cherry_sold_lbs },
    { label: 'Cereza → Honey', value: r.cherry_to_honey_lbs },
    { label: 'Cereza → Natural', value: r.cherry_to_natural_lbs },
    { label: 'Cereza → Pilado', value: r.cherry_to_pilado_lbs },
    { label: '', value: 0, separator: true },
    { label: 'Producción Seco Honey', value: r.honey_output_lbs },
    { label: 'Producción Seco Natural', value: r.natural_output_lbs },
    { label: 'Producción Seco Pilado', value: r.pilado_output_lbs },
  ];

  const chartData = [
    { name: 'Honey', entrada: r.cherry_to_honey_lbs, producto: r.honey_output_lbs },
    { name: 'Natural', entrada: r.cherry_to_natural_lbs, producto: r.natural_output_lbs },
    { name: 'Pilado', entrada: r.cherry_to_pilado_lbs, producto: r.pilado_output_lbs },
  ];

  return (
    <div>
      <h3 className="text-lg font-bold text-[var(--gold)] mb-4 font-['Playfair_Display',serif]">Producción (lbs)</h3>
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-[var(--border)]">
                <th className="text-left py-2 text-[var(--muted-foreground)]">Etapa</th>
                <th className="text-right py-2 text-[var(--muted-foreground)]">Libras (lbs)</th>
              </tr>
            </thead>
            <tbody>
              {tableRows.map((row, i) =>
                row.separator ? (
                  <tr key={i}><td colSpan={2} className="py-1 border-b border-[var(--border)]" /></tr>
                ) : (
                  <tr key={i} className="border-b border-[var(--border)]/50">
                    <td className="py-2 text-[var(--parchment)]">{row.label}</td>
                    <td className="py-2 text-right text-[var(--parchment)]">{fmtNumber(row.value)}</td>
                  </tr>
                ),
              )}
            </tbody>
          </table>
        </div>
        <div>
          <ResponsiveContainer width="100%" height={350}>
            <BarChart data={chartData}>
              <XAxis dataKey="name" stroke="var(--muted-foreground)" fontSize={12} />
              <YAxis stroke="var(--muted-foreground)" fontSize={12} tickFormatter={(v) => fmtNumber(v)} />
              <Tooltip
                contentStyle={TOOLTIP_STYLE}
                formatter={(value) => fmtNumber(Number(value))}
              />
              <Legend />
              <Bar dataKey="entrada" name="Cereza Entrada" fill="rgba(224,96,112,0.4)" />
              <Bar dataKey="producto" name="Producto Obtenido" fill={COLOURS_PRODUCT.pilado} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
}
