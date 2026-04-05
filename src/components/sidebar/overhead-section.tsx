import { NumberField } from './number-field';

export function OverheadSection() {
  return (
    <>
      <NumberField label="Transporte (B/.)" field="transport" step={100} />
      <NumberField label="Certificaciones (B/.)" field="certification" step={100} />
      <NumberField label="Administración (B/.)" field="admin" step={100} />
      <NumberField label="Seguros (B/.)" field="insurance" step={100} />
      <NumberField label="Mantenimiento (B/.)" field="maintenance" step={50} />
      <NumberField label="Mercadeo (B/.)" field="marketing" step={50} />
      <NumberField label="Interés de Préstamos (B/.)" field="loan_interest" step={100} />
      <NumberField label="Depreciación (B/.)" field="depreciation" step={100} />
      <NumberField label="Tasa de Impuestos (%)" field="tax_rate" step={1} max={100} />
      <NumberField label="Contingencia (%)" field="contingency" step={1} max={50} help="Reserva para costos inesperados" />
    </>
  );
}
