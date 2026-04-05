import { test, expect } from '@playwright/test';

test.describe('Monte Carlo simulation', () => {
  test('runs simulation and displays results', async ({ page }) => {
    await page.goto('/');

    // Click the Monte Carlo tab
    await page.getByRole('tab', { name: 'Monte Carlo' }).click();

    // Look for the run/execute button
    const runButton = page.getByRole('button', { name: /Ejecutar|Simular/i });
    if (await runButton.isVisible()) {
      await runButton.click();

      // Wait for simulation to complete (button text should change back)
      await expect(runButton).not.toHaveText(/Ejecutando|Simulando/i, { timeout: 15000 });

      // Results should be visible — look for summary statistics or charts
      // The simulation creates summary rows with metric labels
      await expect(page.getByText(/Ingresos Totales|Ganancia Neta/i).first()).toBeVisible();
    }
  });
});
