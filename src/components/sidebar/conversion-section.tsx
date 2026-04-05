import { NumberField } from './number-field';

export function ConversionSection() {
  return (
    <>
      <p className="text-xs text-[var(--muted-foreground)]">Lbs de producto por cada 100 lbs de cereza</p>
      <NumberField label="Cereza → Seco Honey (%)" field="ratio_honey" step={0.5} min={1} max={100} />
      <NumberField label="Cereza → Seco Natural (%)" field="ratio_natural" step={0.5} min={1} max={100} />
      <NumberField label="Cereza → Seco Pilado (%)" field="ratio_pilado" step={0.5} min={1} max={100} />
    </>
  );
}
