export interface InputValues {
  total_hectares: number;
  plants_per_ha: number;
  productive_hectares: number;
  land_cost: number;
  cherry_yield_per_ha: number;
  pct_cereza: number;
  pct_honey: number;
  pct_natural: number;
  pct_pilado: number;
  ratio_honey: number;
  ratio_natural: number;
  ratio_pilado: number;
  price_cereza: number;
  price_honey: number;
  price_natural: number;
  price_pilado: number;
  permanent_workers: number;
  monthly_wage: number;
  seasonal_workers: number;
  seasonal_daily_wage: number;
  harvest_days: number;
  labor_benefits: number;
  fertilizer: number;
  pesticide: number;
  seedlings: number;
  water: number;
  tools: number;
  fuel: number;
  cost_honey_lb: number;
  cost_natural_lb: number;
  cost_pilado_lb: number;
  cost_packaging_lb: number;
  transport: number;
  certification: number;
  admin: number;
  insurance: number;
  maintenance: number;
  marketing: number;
  loan_interest: number;
  depreciation: number;
  tax_rate: number;
  contingency: number;
}

export const DEFAULT_INPUTS: InputValues = {
  total_hectares: 5.0,
  plants_per_ha: 5000,
  productive_hectares: 4.0,
  land_cost: 2000.0,
  cherry_yield_per_ha: 8000.0,
  pct_cereza: 10.0,
  pct_honey: 30.0,
  pct_natural: 30.0,
  pct_pilado: 30.0,
  ratio_honey: 22.0,
  ratio_natural: 20.0,
  ratio_pilado: 18.0,
  price_cereza: 0.50,
  price_honey: 4.50,
  price_natural: 3.80,
  price_pilado: 5.00,
  permanent_workers: 3,
  monthly_wage: 400.0,
  seasonal_workers: 10,
  seasonal_daily_wage: 15.0,
  harvest_days: 60,
  labor_benefits: 30.0,
  fertilizer: 3000.0,
  pesticide: 1500.0,
  seedlings: 500.0,
  water: 1200.0,
  tools: 800.0,
  fuel: 1000.0,
  cost_honey_lb: 0.35,
  cost_natural_lb: 0.25,
  cost_pilado_lb: 0.50,
  cost_packaging_lb: 0.75,
  transport: 2000.0,
  certification: 1500.0,
  admin: 1200.0,
  insurance: 800.0,
  maintenance: 600.0,
  marketing: 500.0,
  loan_interest: 0.0,
  depreciation: 1000.0,
  tax_rate: 15.0,
  contingency: 5.0,
};

export interface Product {
  key: string;
  label: string;
  icon: string;
  desc: string;
}

export const PRODUCTS: Product[] = [
  { key: 'cereza', label: 'Cereza', icon: '🍒', desc: 'Grano en cereza, recién cosechado' },
  { key: 'honey', label: 'Seco Honey', icon: '🍯', desc: 'Proceso honey — secado con mucílago' },
  { key: 'natural', label: 'Seco Natural', icon: '☀️', desc: 'Proceso natural — secado entero' },
  { key: 'pilado', label: 'Seco Pilado', icon: '⚙️', desc: 'Proceso lavado — despulpado y pilado' },
];

export const COLOURS_PRODUCT: Record<string, string> = {
  cereza: '#E06070',
  honey: '#E8C547',
  natural: '#E8A040',
  pilado: '#A0D585',
};

export const COLOUR_POSITIVE = '#A0D585';
export const COLOUR_NEGATIVE = '#d62828';
export const COLOUR_TOTAL = '#6984A9';

export const DEFAULT_VARIABLE_KEYS = [
  { key: 'cherry_yield_per_ha', label: 'Rendimiento de Cereza (lbs/ha)' },
  { key: 'ratio_honey', label: 'Ratio Cereza → Honey (%)' },
  { key: 'ratio_natural', label: 'Ratio Cereza → Natural (%)' },
  { key: 'ratio_pilado', label: 'Ratio Cereza → Pilado (%)' },
  { key: 'price_cereza', label: 'Precio Cereza (B/./lb)' },
  { key: 'price_honey', label: 'Precio Seco Honey (B/./lb)' },
  { key: 'price_natural', label: 'Precio Seco Natural (B/./lb)' },
  { key: 'price_pilado', label: 'Precio Seco Pilado (B/./lb)' },
  { key: 'fertilizer', label: 'Costo de Fertilizante (B/.)' },
  { key: 'pesticide', label: 'Control de Plagas (B/.)' },
  { key: 'seasonal_workers', label: 'Trabajadores Temporales' },
  { key: 'seasonal_daily_wage', label: 'Jornal Diario Temporal (B/.)' },
  { key: 'harvest_days', label: 'Días de Cosecha' },
  { key: 'cost_honey_lb', label: 'Costo Proceso Honey (B/./lb)' },
  { key: 'cost_natural_lb', label: 'Costo Proceso Natural (B/./lb)' },
  { key: 'cost_pilado_lb', label: 'Costo Proceso Pilado (B/./lb)' },
  { key: 'fuel', label: 'Combustible y Energía (B/.)' },
  { key: 'transport', label: 'Transporte y Logística (B/.)' },
] as const;

export const TRACKED_METRICS = [
  'total_revenue',
  'total_costs',
  'net_profit',
  'margin',
  'cost_per_lb_cherry',
  'total_cherry',
  'honey_output_lbs',
  'natural_output_lbs',
  'pilado_output_lbs',
  'rev_per_ha',
  'profit_per_ha',
] as const;

export const METRIC_LABELS: Record<string, string> = {
  total_revenue: 'Ingresos Totales (B/.)',
  total_costs: 'Costos Totales (B/.)',
  net_profit: 'Ganancia Neta (B/.)',
  margin: 'Margen de Ganancia (%)',
  cost_per_lb_cherry: 'Costo por lb Cereza (B/.)',
  total_cherry: 'Total Cereza (lbs)',
  honey_output_lbs: 'Producción Honey (lbs)',
  natural_output_lbs: 'Producción Natural (lbs)',
  pilado_output_lbs: 'Producción Pilado (lbs)',
  rev_per_ha: 'Ingresos por Hectárea (B/.)',
  profit_per_ha: 'Ganancia por Hectárea (B/.)',
};
