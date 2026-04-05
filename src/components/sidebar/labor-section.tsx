import { NumberField } from './number-field';

export function LaborSection() {
  return (
    <>
      <NumberField label="Trabajadores Permanentes" field="permanent_workers" step={1} />
      <NumberField label="Salario Mensual / Trabajador (B/.)" field="monthly_wage" step={10} />
      <NumberField label="Trabajadores Temporales" field="seasonal_workers" step={1} />
      <NumberField label="Jornal Diario / Temporal (B/.)" field="seasonal_daily_wage" step={1} />
      <NumberField label="Días de Cosecha" field="harvest_days" step={5} />
      <NumberField label="Prestaciones (%)" field="labor_benefits" step={1} max={100} help="INSS, décimo, vacaciones, etc." />
    </>
  );
}
