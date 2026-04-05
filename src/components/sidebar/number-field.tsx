import { Label } from '@/components/ui/label';
import { Input } from '@/components/ui/input';
import type { InputValues } from '@/lib/config';
import { useInputs } from '@/hooks/use-inputs';

interface NumberFieldProps {
  label: string;
  field: keyof InputValues;
  step?: number;
  min?: number;
  max?: number;
  help?: string;
}

export function NumberField({ label, field, step = 1, min = 0, max, help }: NumberFieldProps) {
  const { inputs, setField } = useInputs();
  const value = inputs[field];

  return (
    <div className="space-y-1">
      <Label htmlFor={field} title={help}>{label}</Label>
      <Input
        id={field}
        type="number"
        value={value}
        step={step}
        min={min}
        max={max}
        onChange={(e) => {
          const v = parseFloat(e.target.value);
          if (!isNaN(v)) setField(field, v);
        }}
      />
    </div>
  );
}
