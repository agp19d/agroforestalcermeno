import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from 'recharts';
import { fmtCurrency } from '@/lib/formatting';
import { PRODUCTS, COLOURS_PRODUCT, TOOLTIP_STYLE } from '@/lib/config';
import type { FinancialResults } from '@/lib/models';

interface Props { results: FinancialResults }

export function TabRevenue({ results: r }: Props) {
  const revenues = [r.rev_cereza, r.rev_honey, r.rev_natural, r.rev_pilado];
  const labels = PRODUCTS.map((p) => p.label);
  const colors = PRODUCTS.map((p) => COLOURS_PRODUCT[p.key]);

  const tableRows = labels.map((label, i) => ({ label, value: revenues[i] }));
  tableRows.push({ label: 'TOTAL', value: r.total_revenue });

  const pieData = labels.map((label, i) => ({ name: label, value: revenues[i] }));

  return (
    <div>
      <h3 className="text-lg font-bold text-[var(--gold)] mb-4 font-['Playfair_Display',serif]">Desglose de Ingresos</h3>
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-[var(--border)]">
                <th className="text-left py-2 text-[var(--muted-foreground)]">Producto</th>
                <th className="text-right py-2 text-[var(--muted-foreground)]">Ingresos (B/.)</th>
              </tr>
            </thead>
            <tbody>
              {tableRows.map((row) => (
                <tr key={row.label} className={`border-b border-[var(--border)]/50 ${row.label === 'TOTAL' ? 'font-bold' : ''}`}>
                  <td className="py-2 text-[var(--parchment)]">{row.label}</td>
                  <td className="py-2 text-right text-[var(--parchment)]">{fmtCurrency(row.value)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <div>
          <ResponsiveContainer width="100%" height={350}>
            <PieChart>
              <Pie
                data={pieData}
                cx="50%"
                cy="50%"
                innerRadius={60}
                outerRadius={120}
                dataKey="value"
                label={({ name, percent }) => `${name ?? ''} ${((percent ?? 0) * 100).toFixed(0)}%`}
              >
                {pieData.map((_, i) => (
                  <Cell key={i} fill={colors[i]} />
                ))}
              </Pie>
              <Tooltip
                contentStyle={TOOLTIP_STYLE}
                formatter={(value) => fmtCurrency(Number(value))}
              />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
}
