import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from 'recharts';
import { fmtCurrency } from '@/lib/formatting';
import type { FinancialResults } from '@/lib/models';

interface Props { results: FinancialResults }

const COST_COLORS = [
  '#E06070', '#E8C547', '#E8A040', '#A0D585', '#6DD4A0',
  '#B8E8C8', '#6984A9', '#88B4D0', '#EEFABD', '#D4A05A', '#C86050',
];

export function TabCosts({ results: r }: Props) {
  const costItems = [
    { label: 'Mano de obra (permanente)', value: r.permanent_labor },
    { label: 'Mano de obra (temporal)', value: r.seasonal_labor },
    { label: 'Prestaciones laborales', value: r.labor_benefits },
    { label: 'Insumos y materiales', value: r.inputs_materials },
    { label: 'Procesamiento Honey', value: r.processing_honey },
    { label: 'Procesamiento Natural', value: r.processing_natural },
    { label: 'Procesamiento Pilado', value: r.processing_pilado },
    { label: 'Empaque', value: r.packaging_cost },
    { label: 'Terreno', value: r.land_cost },
    { label: 'Gastos generales', value: r.overhead },
    { label: 'Contingencia', value: r.contingency },
  ];

  const pieData = costItems.map((item) => ({ name: item.label, value: item.value }));

  return (
    <div>
      <h3 className="text-lg font-bold text-[var(--gold)] mb-4 font-['Playfair_Display',serif]">Desglose de Costos</h3>
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-[var(--border)]">
                <th className="text-left py-2 text-[var(--muted-foreground)]">Categoría</th>
                <th className="text-right py-2 text-[var(--muted-foreground)]">Monto (B/.)</th>
              </tr>
            </thead>
            <tbody>
              {costItems.map((row) => (
                <tr key={row.label} className="border-b border-[var(--border)]/50">
                  <td className="py-2 text-[var(--parchment)]">{row.label}</td>
                  <td className="py-2 text-right text-[var(--parchment)]">{fmtCurrency(row.value)}</td>
                </tr>
              ))}
              <tr className="border-b border-[var(--border)] font-bold">
                <td className="py-2 text-[var(--parchment)]">TOTAL</td>
                <td className="py-2 text-right text-[var(--parchment)]">{fmtCurrency(r.total_costs)}</td>
              </tr>
            </tbody>
          </table>
        </div>
        <div>
          <ResponsiveContainer width="100%" height={400}>
            <PieChart>
              <Pie
                data={pieData}
                cx="50%"
                cy="50%"
                innerRadius={60}
                outerRadius={130}
                dataKey="value"
                label={({ name, percent }) => `${(name ?? '').split(' ')[0]} ${((percent ?? 0) * 100).toFixed(0)}%`}
              >
                {pieData.map((_, i) => (
                  <Cell key={i} fill={COST_COLORS[i % COST_COLORS.length]} />
                ))}
              </Pie>
              <Tooltip
                contentStyle={{ background: 'var(--dark-roast)', border: '1px solid var(--border)', borderRadius: '8px', color: 'var(--parchment)' }}
                formatter={(value) => fmtCurrency(Number(value))}
              />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
}
