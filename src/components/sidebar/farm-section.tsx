import { NumberField } from './number-field';

export function FarmSection() {
  return (
    <>
      <NumberField label="Hectáreas Totales" field="total_hectares" step={0.5} />
      <NumberField label="Hectáreas Productivas" field="productive_hectares" step={0.5} />
      <NumberField label="Plantas por Hectárea" field="plants_per_ha" step={100} />
      <NumberField label="Costo de Terreno / Año (B/.)" field="land_cost" step={100} />
    </>
  );
}
