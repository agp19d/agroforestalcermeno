import { NumberField } from './number-field';

export function ProcessingSection() {
  return (
    <>
      <p className="text-xs text-[var(--muted-foreground)]">Por libra de cereza que entra al proceso</p>
      <NumberField label="Proceso Honey (B/./lb)" field="cost_honey_lb" step={0.05} />
      <NumberField label="Proceso Natural (B/./lb)" field="cost_natural_lb" step={0.05} />
      <NumberField label="Proceso Pilado (B/./lb)" field="cost_pilado_lb" step={0.05} />
      <NumberField label="Empaque (B/./lb producto)" field="cost_packaging_lb" step={0.05} />
    </>
  );
}
