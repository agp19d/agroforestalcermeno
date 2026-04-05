import { NumberField } from './number-field';

export function YieldSection() {
  return (
    <NumberField label="Cereza por Hectárea (lbs)" field="cherry_yield_per_ha" step={100} />
  );
}
