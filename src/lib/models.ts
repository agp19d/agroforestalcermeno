import type { InputValues } from './config';

export interface FinancialResults {
  // Production (lbs)
  total_cherry: number;
  cherry_sold_lbs: number;
  cherry_to_honey_lbs: number;
  cherry_to_natural_lbs: number;
  cherry_to_pilado_lbs: number;
  honey_output_lbs: number;
  natural_output_lbs: number;
  pilado_output_lbs: number;

  // Revenue (B/.)
  rev_cereza: number;
  rev_honey: number;
  rev_natural: number;
  rev_pilado: number;
  total_revenue: number;

  // Costs (B/.)
  permanent_labor: number;
  seasonal_labor: number;
  labor_benefits: number;
  total_labor: number;
  inputs_materials: number;
  processing_honey: number;
  processing_natural: number;
  processing_pilado: number;
  total_processing: number;
  packaging_cost: number;
  land_cost: number;
  overhead: number;
  contingency: number;
  total_costs: number;

  // Profitability
  gross_profit: number;
  taxes: number;
  net_profit: number;
  margin: number;
  cost_per_lb_cherry: number;
  rev_per_ha: number;
  profit_per_ha: number;
}

export function calculate(inputs: InputValues): FinancialResults {
  // Production
  const productive_ha = inputs.productive_hectares;
  const cherry_per_ha = inputs.cherry_yield_per_ha;
  const total_cherry = productive_ha * cherry_per_ha;

  const pct_cereza = inputs.pct_cereza / 100;
  const pct_honey = inputs.pct_honey / 100;
  const pct_natural = inputs.pct_natural / 100;
  const pct_pilado = inputs.pct_pilado / 100;

  const cherry_sold_lbs = total_cherry * pct_cereza;
  const cherry_to_honey_lbs = total_cherry * pct_honey;
  const cherry_to_natural_lbs = total_cherry * pct_natural;
  const cherry_to_pilado_lbs = total_cherry * pct_pilado;

  const honey_output_lbs = cherry_to_honey_lbs * (inputs.ratio_honey / 100);
  const natural_output_lbs = cherry_to_natural_lbs * (inputs.ratio_natural / 100);
  const pilado_output_lbs = cherry_to_pilado_lbs * (inputs.ratio_pilado / 100);

  // Revenue
  const rev_cereza = cherry_sold_lbs * inputs.price_cereza;
  const rev_honey = honey_output_lbs * inputs.price_honey;
  const rev_natural = natural_output_lbs * inputs.price_natural;
  const rev_pilado = pilado_output_lbs * inputs.price_pilado;
  const total_revenue = rev_cereza + rev_honey + rev_natural + rev_pilado;

  // Costs
  const permanent_labor = inputs.permanent_workers * inputs.monthly_wage * 12;
  const seasonal_labor = inputs.seasonal_workers * inputs.seasonal_daily_wage * inputs.harvest_days;
  const base_labor = permanent_labor + seasonal_labor;
  const labor_benefits = base_labor * (inputs.labor_benefits / 100);
  const total_labor = base_labor + labor_benefits;

  const inputs_materials =
    inputs.fertilizer + inputs.pesticide + inputs.seedlings +
    inputs.water + inputs.tools + inputs.fuel;

  const processing_honey = cherry_to_honey_lbs * inputs.cost_honey_lb;
  const processing_natural = cherry_to_natural_lbs * inputs.cost_natural_lb;
  const processing_pilado = cherry_to_pilado_lbs * inputs.cost_pilado_lb;
  const total_processing = processing_honey + processing_natural + processing_pilado;

  const total_packaged_lbs = honey_output_lbs + natural_output_lbs + pilado_output_lbs;
  const packaging_cost = total_packaged_lbs * inputs.cost_packaging_lb;

  const land_cost = inputs.land_cost;

  const overhead =
    inputs.transport + inputs.certification + inputs.admin +
    inputs.insurance + inputs.maintenance + inputs.marketing +
    inputs.loan_interest + inputs.depreciation;

  const subtotal = total_labor + inputs_materials + total_processing + packaging_cost + land_cost + overhead;
  const contingency = subtotal * (inputs.contingency / 100);
  const total_costs = subtotal + contingency;

  // Profitability
  const gross_profit = total_revenue - total_costs;
  const taxes = Math.max(0, gross_profit * (inputs.tax_rate / 100));
  const net_profit = gross_profit - taxes;
  const margin = total_revenue ? (net_profit / total_revenue) * 100 : 0;
  const cost_per_lb_cherry = total_cherry ? total_costs / total_cherry : 0;
  const rev_per_ha = productive_ha ? total_revenue / productive_ha : 0;
  const profit_per_ha = productive_ha ? net_profit / productive_ha : 0;

  return {
    total_cherry, cherry_sold_lbs,
    cherry_to_honey_lbs, cherry_to_natural_lbs, cherry_to_pilado_lbs,
    honey_output_lbs, natural_output_lbs, pilado_output_lbs,
    rev_cereza, rev_honey, rev_natural, rev_pilado, total_revenue,
    permanent_labor, seasonal_labor, labor_benefits, total_labor,
    inputs_materials,
    processing_honey, processing_natural, processing_pilado, total_processing,
    packaging_cost, land_cost, overhead, contingency, total_costs,
    gross_profit, taxes, net_profit, margin,
    cost_per_lb_cherry, rev_per_ha, profit_per_ha,
  };
}
