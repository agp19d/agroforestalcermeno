import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from '@/components/ui/accordion';
import { ScenarioManager } from './scenario-manager';
import { FarmSection } from './farm-section';
import { YieldSection } from './yield-section';
import { AllocationSection } from './allocation-section';
import { ConversionSection } from './conversion-section';
import { PricesSection } from './prices-section';
import { LaborSection } from './labor-section';
import { MaterialsSection } from './materials-section';
import { ProcessingSection } from './processing-section';
import { OverheadSection } from './overhead-section';

export function SidebarContent() {
  return (
    <div className="space-y-2">
      <h2 className="text-lg font-bold text-[var(--gold)] font-['Playfair_Display',serif]">
        Parámetros
      </h2>
      <Accordion type="multiple" defaultValue={['scenarios', 'farm', 'allocation']}>
        <AccordionItem value="scenarios">
          <AccordionTrigger>Guardar / Cargar Escenarios</AccordionTrigger>
          <AccordionContent><ScenarioManager /></AccordionContent>
        </AccordionItem>
        <AccordionItem value="farm">
          <AccordionTrigger>Finca y Terreno</AccordionTrigger>
          <AccordionContent><FarmSection /></AccordionContent>
        </AccordionItem>
        <AccordionItem value="yield">
          <AccordionTrigger>Rendimiento</AccordionTrigger>
          <AccordionContent><YieldSection /></AccordionContent>
        </AccordionItem>
        <AccordionItem value="allocation">
          <AccordionTrigger>Distribución de Cereza</AccordionTrigger>
          <AccordionContent><AllocationSection /></AccordionContent>
        </AccordionItem>
        <AccordionItem value="conversion">
          <AccordionTrigger>Ratios de Conversión</AccordionTrigger>
          <AccordionContent><ConversionSection /></AccordionContent>
        </AccordionItem>
        <AccordionItem value="prices">
          <AccordionTrigger>Precios de Venta</AccordionTrigger>
          <AccordionContent><PricesSection /></AccordionContent>
        </AccordionItem>
        <AccordionItem value="labor">
          <AccordionTrigger>Mano de Obra</AccordionTrigger>
          <AccordionContent><LaborSection /></AccordionContent>
        </AccordionItem>
        <AccordionItem value="materials">
          <AccordionTrigger>Insumos y Materiales</AccordionTrigger>
          <AccordionContent><MaterialsSection /></AccordionContent>
        </AccordionItem>
        <AccordionItem value="processing">
          <AccordionTrigger>Costos de Procesamiento</AccordionTrigger>
          <AccordionContent><ProcessingSection /></AccordionContent>
        </AccordionItem>
        <AccordionItem value="overhead">
          <AccordionTrigger>Gastos Generales</AccordionTrigger>
          <AccordionContent><OverheadSection /></AccordionContent>
        </AccordionItem>
      </Accordion>
    </div>
  );
}
