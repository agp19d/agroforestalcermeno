import { NumberField } from './number-field';

export function PricesSection() {
  return (
    <>
      <NumberField label="Cereza (B/./lb)" field="price_cereza" step={0.1} />
      <NumberField label="Seco Honey (B/./lb)" field="price_honey" step={0.1} />
      <NumberField label="Seco Natural (B/./lb)" field="price_natural" step={0.1} />
      <NumberField label="Seco Pilado (B/./lb)" field="price_pilado" step={0.1} />
    </>
  );
}
