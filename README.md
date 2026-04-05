# Agroforestal Cermeño — Planificador Financiero de Producción de Café

Aplicación web React + TypeScript para productores de café que permite modelar costos de producción, volúmenes, ingresos y rentabilidad bajo diferentes escenarios financieros — incluyendo análisis de riesgo con simulación Monte Carlo. Todos los valores monetarios están en **Balboas panameños (B/.)**.

## Stack

- **React 19** + **TypeScript** — SPA con recálculo instantáneo
- **Vite** — bundler y dev server
- **Tailwind CSS v4** — estilos mobile-first
- **Radix UI** — componentes accesibles (Accordion, Tabs, Dialog, etc.)
- **Recharts** — gráficos (barras, donut, cascada, histogramas, CDF)
- **Web Worker** — simulación Monte Carlo sin bloquear la UI
- **localStorage** — persistencia de escenarios

## Características

- **Modelado de Producción** — cereza cosechada → venta directa o procesamiento (Honey, Natural, Pilado)
- **Control Completo de Costos** — mano de obra, insumos, procesamiento, empaque, terreno, gastos generales
- **Proyecciones de Ingresos** — precio por libra para cada producto
- **Análisis de Rentabilidad** — márgenes, costo por libra, gráfico de cascada
- **Gestión de Escenarios** — guardar, cargar, eliminar y comparar múltiples escenarios
- **Simulación Monte Carlo** — distribuciones triangulares, histogramas, CDF, indicadores de riesgo
- **Responsive** — sidebar colapsable en móvil, layout adaptivo

## Primeros Pasos

```bash
git clone https://github.com/agp19d/agroforestalcermeno.git
cd agroforestalcermeno
npm install
npm run dev
```

La aplicación se abrirá en `http://localhost:5173`.

## Build de Producción

```bash
npm run build
npm run preview
```

## Licencia

Este proyecto es proporcionado tal cual para uso privado de Agroforestal Cermeño.
