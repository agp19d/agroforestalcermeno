import { useState, useMemo } from 'react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { fmtCurrency, fmtPercent, fmtNumber } from '@/lib/formatting';
import { calculate } from '@/lib/models';
import { useScenarios } from '@/hooks/use-scenarios';

const BAR_COLORS = ['#A0D585', '#E8C547', '#E06070', '#6984A9', '#E8A040'];

export function TabCompare() {
  const { scenarios, names } = useScenarios();
  const [selected, setSelected] = useState<string[]>([]);

  const rows = useMemo(() => {
    return selected.map((name) => {
      const sr = calculate(scenarios[name]);
      return { name, ...sr };
    });
  }, [selected, scenarios]);

  if (names.length < 2) {
    return (
      <div className="text-center py-12 text-[var(--muted-foreground)]">
        Guarda al menos 2 escenarios para compararlos.
      </div>
    );
  }

  return (
    <div>
      <h3 className="text-lg font-bold text-[var(--gold)] mb-4 font-['Playfair_Display',serif]">Comparar Escenarios Guardados</h3>

      <div className="mb-4 flex flex-wrap gap-2">
        {names.map((name) => (
          <button
            key={name}
            className={`px-3 py-1.5 rounded-lg text-sm border transition-all ${
              selected.includes(name)
                ? 'bg-[var(--gold)]/20 border-[var(--gold)] text-[var(--gold)]'
                : 'border-[var(--border)] text-[var(--muted-foreground)] hover:border-[var(--gold)]/50'
            }`}
            onClick={() =>
              setSelected((prev) =>
                prev.includes(name) ? prev.filter((n) => n !== name) : [...prev, name],
              )
            }
          >
            {name}
          </button>
        ))}
      </div>

      {selected.length >= 2 && (
        <>
          <div className="overflow-x-auto mb-6">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-[var(--border)]">
                  <th className="text-left py-2 text-[var(--muted-foreground)]">Escenario</th>
                  <th className="text-right py-2 text-[var(--muted-foreground)]">Ingresos</th>
                  <th className="text-right py-2 text-[var(--muted-foreground)]">Costos</th>
                  <th className="text-right py-2 text-[var(--muted-foreground)]">Ganancia Neta</th>
                  <th className="text-right py-2 text-[var(--muted-foreground)]">Margen</th>
                  <th className="text-right py-2 text-[var(--muted-foreground)]">Honey (lbs)</th>
                  <th className="text-right py-2 text-[var(--muted-foreground)]">Natural (lbs)</th>
                  <th className="text-right py-2 text-[var(--muted-foreground)]">Pilado (lbs)</th>
                </tr>
              </thead>
              <tbody>
                {rows.map((row) => (
                  <tr key={row.name} className="border-b border-[var(--border)]/50">
                    <td className="py-2 text-[var(--parchment)] font-medium">{row.name}</td>
                    <td className="py-2 text-right text-[var(--parchment)]">{fmtCurrency(row.total_revenue)}</td>
                    <td className="py-2 text-right text-[var(--parchment)]">{fmtCurrency(row.total_costs)}</td>
                    <td className="py-2 text-right text-[var(--parchment)]">{fmtCurrency(row.net_profit)}</td>
                    <td className="py-2 text-right text-[var(--parchment)]">{fmtPercent(row.margin)}</td>
                    <td className="py-2 text-right text-[var(--parchment)]">{fmtNumber(row.honey_output_lbs)}</td>
                    <td className="py-2 text-right text-[var(--parchment)]">{fmtNumber(row.natural_output_lbs)}</td>
                    <td className="py-2 text-right text-[var(--parchment)]">{fmtNumber(row.pilado_output_lbs)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <ResponsiveContainer width="100%" height={350}>
            <BarChart
              data={[
                { metric: 'Ingresos', ...Object.fromEntries(rows.map((r) => [r.name, r.total_revenue])) },
                { metric: 'Costos', ...Object.fromEntries(rows.map((r) => [r.name, r.total_costs])) },
                { metric: 'Ganancia Neta', ...Object.fromEntries(rows.map((r) => [r.name, r.net_profit])) },
              ]}
            >
              <XAxis dataKey="metric" stroke="var(--muted-foreground)" fontSize={12} />
              <YAxis stroke="var(--muted-foreground)" fontSize={11} tickFormatter={(v) => `B/.${(v / 1000).toFixed(0)}k`} />
              <Tooltip
                contentStyle={{ background: 'var(--dark-roast)', border: '1px solid var(--border)', borderRadius: '8px', color: 'var(--parchment)' }}
                formatter={(value) => fmtCurrency(Number(value))}
              />
              <Legend />
              {selected.map((name, i) => (
                <Bar key={name} dataKey={name} fill={BAR_COLORS[i % BAR_COLORS.length]} />
              ))}
            </BarChart>
          </ResponsiveContainer>
        </>
      )}
    </div>
  );
}
