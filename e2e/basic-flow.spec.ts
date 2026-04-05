import { test, expect } from '@playwright/test';

test.describe('Basic app flow', () => {
  test('app loads and displays title', async ({ page }) => {
    await page.goto('/');
    await expect(page.getByText('Agroforestal Cermeño')).toBeVisible();
  });

  test('KPI bar shows 4 cards', async ({ page }) => {
    await page.goto('/');
    await expect(page.getByText('Ingresos Totales')).toBeVisible();
    await expect(page.getByText('Costos Totales')).toBeVisible();
    await expect(page.getByText('Ganancia Neta')).toBeVisible();
    await expect(page.getByText('Margen de Ganancia')).toBeVisible();
  });

  test('KPI values contain B/. currency format', async ({ page }) => {
    await page.goto('/');
    const kpiSection = page.locator('text=B/.');
    await expect(kpiSection.first()).toBeVisible();
  });

  test('all 6 tabs are visible and clickable', async ({ page }) => {
    await page.goto('/');
    const tabs = ['Producción', 'Ingresos', 'Costos', 'Rentabilidad', 'Comparar', 'Monte Carlo'];
    for (const tab of tabs) {
      const tabEl = page.getByRole('tab', { name: tab });
      await expect(tabEl).toBeVisible();
    }
  });

  test('clicking a tab changes its state', async ({ page }) => {
    await page.goto('/');
    const revenueTab = page.getByRole('tab', { name: 'Ingresos' });
    await revenueTab.click();
    await expect(revenueTab).toHaveAttribute('data-state', 'active');
  });

  test('changing input updates KPI values', async ({ page }) => {
    // Use a wide viewport so sidebar is visible
    await page.setViewportSize({ width: 1280, height: 800 });
    await page.goto('/');

    // Get the KPI value for Ganancia Neta (the bold gold text inside the card)
    const kpiCard = page.locator('text=Ganancia Neta').locator('..').locator('..').locator('p');
    const initialValue = await kpiCard.textContent();

    // Find the productive_hectares input and change it
    const input = page.locator('#productive_hectares');
    await expect(input).toBeVisible();
    await input.fill('20');
    await input.press('Tab');

    // Wait for re-render
    await page.waitForTimeout(300);

    // KPI value should have changed
    const newValue = await kpiCard.textContent();
    expect(newValue).not.toBe(initialValue);
  });
});
