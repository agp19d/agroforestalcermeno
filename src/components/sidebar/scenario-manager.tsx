import { useState } from 'react';
import { useInputs } from '@/hooks/use-inputs';
import { useScenarios } from '@/hooks/use-scenarios';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';

export function ScenarioManager() {
  const { inputs, loadScenario } = useInputs();
  const { names, save, remove, load } = useScenarios();
  const [name, setName] = useState('Escenario 1');
  const [selected, setSelected] = useState('');

  return (
    <div className="space-y-3">
      <div className="space-y-1">
        <Label>Nombre del escenario</Label>
        <Input value={name} onChange={(e) => setName(e.target.value)} />
      </div>
      <div className="grid grid-cols-2 gap-2">
        <Button size="sm" onClick={() => save(name, inputs)}>Guardar</Button>
        <Button
          size="sm"
          variant="secondary"
          onClick={() => {
            if (selected) {
              const data = load(selected);
              if (data) loadScenario(data);
            }
          }}
        >
          Cargar
        </Button>
      </div>
      {names.length > 0 && (
        <>
          <div className="space-y-1">
            <Label>Cargar escenario</Label>
            <select
              className="flex h-9 w-full rounded-lg border border-[var(--input)] bg-black/30 px-3 py-1 text-sm text-[var(--parchment)] focus:outline-none focus:border-[var(--gold)]"
              value={selected}
              onChange={(e) => setSelected(e.target.value)}
            >
              <option value="">Seleccionar...</option>
              {names.map((n) => (
                <option key={n} value={n}>{n}</option>
              ))}
            </select>
          </div>
          <Button
            size="sm"
            variant="destructive"
            className="w-full"
            onClick={() => {
              if (selected) {
                remove(selected);
                setSelected('');
              }
            }}
          >
            Eliminar seleccionado
          </Button>
        </>
      )}
    </div>
  );
}
