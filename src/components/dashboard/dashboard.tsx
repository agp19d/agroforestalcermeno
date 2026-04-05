import { Tabs, TabsList, TabsTrigger, TabsContent } from '@/components/ui/tabs';
import { useInputs } from '@/hooks/use-inputs';
import { useFinancial } from '@/hooks/use-financial';
import { Pipeline } from './pipeline';
import { KpiBar } from './kpi-bar';
import { TabProduction } from './tab-production';
import { TabRevenue } from './tab-revenue';
import { TabCosts } from './tab-costs';
import { TabProfitability } from './tab-profitability';
import { TabCompare } from './tab-compare';
import { TabMonteCarlo } from './tab-montecarlo';

export function Dashboard() {
  const { inputs } = useInputs();
  const results = useFinancial(inputs);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl md:text-4xl font-black text-[var(--parchment)] font-['Playfair_Display',serif]">
          Agroforestal Cermeño
        </h1>
        <p className="text-xs tracking-[3px] uppercase text-[var(--muted-foreground)] font-light mt-1">
          Calculadora de Producción &amp; Rentabilidad Cafetalera
        </p>
      </div>

      <Pipeline results={results} />

      <div className="border-t border-[var(--border)]" />

      <KpiBar results={results} />

      <div className="border-t border-[var(--border)]" />

      <Tabs defaultValue="production">
        <TabsList>
          <TabsTrigger value="production">Producción</TabsTrigger>
          <TabsTrigger value="revenue">Ingresos</TabsTrigger>
          <TabsTrigger value="costs">Costos</TabsTrigger>
          <TabsTrigger value="profitability">Rentabilidad</TabsTrigger>
          <TabsTrigger value="compare">Comparar</TabsTrigger>
          <TabsTrigger value="montecarlo">Monte Carlo</TabsTrigger>
        </TabsList>
        <TabsContent value="production"><TabProduction results={results} /></TabsContent>
        <TabsContent value="revenue"><TabRevenue results={results} /></TabsContent>
        <TabsContent value="costs"><TabCosts results={results} /></TabsContent>
        <TabsContent value="profitability"><TabProfitability results={results} /></TabsContent>
        <TabsContent value="compare"><TabCompare /></TabsContent>
        <TabsContent value="montecarlo"><TabMonteCarlo /></TabsContent>
      </Tabs>
    </div>
  );
}
