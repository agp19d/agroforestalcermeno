import { useInputs } from '@/hooks/use-inputs';
import { NumberField } from './number-field';

export function AllocationSection() {
  const { inputs } = useInputs();
  const total = inputs.pct_cereza + inputs.pct_honey + inputs.pct_natural + inputs.pct_pilado;
  const isValid = Math.abs(total - 100) < 0.01;

  return (
    <>
      <p className="text-xs text-[var(--muted-foreground)]">¿Que % de la cereza va a cada destino?</p>
      <NumberField label="Vendida como Cereza (%)" field="pct_cereza" step={5} max={100} />
      <NumberField label="Proceso Honey (%)" field="pct_honey" step={5} max={100} />
      <NumberField label="Proceso Natural (%)" field="pct_natural" step={5} max={100} />
      <NumberField label="Proceso Pilado (%)" field="pct_pilado" step={5} max={100} />
      <div className={`text-xs font-medium px-2 py-1.5 rounded-md ${isValid ? 'bg-[var(--colour-positive)]/20 text-emerald-400' : 'bg-[var(--colour-negative)]/20 text-red-400'}`}>
        {isValid ? 'Distribución: 100%' : `Total: ${total.toFixed(0)}% — debe sumar 100%`}
      </div>
    </>
  );
}
