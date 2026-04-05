import { NumberField } from './number-field';

export function MaterialsSection() {
  return (
    <>
      <NumberField label="Fertilizante (B/.)" field="fertilizer" step={100} />
      <NumberField label="Control de Plagas (B/.)" field="pesticide" step={100} />
      <NumberField label="Plántulas y Resiembra (B/.)" field="seedlings" step={50} />
      <NumberField label="Agua y Riego (B/.)" field="water" step={100} />
      <NumberField label="Herramientas (B/.)" field="tools" step={50} />
      <NumberField label="Combustible y Energía (B/.)" field="fuel" step={50} />
    </>
  );
}
