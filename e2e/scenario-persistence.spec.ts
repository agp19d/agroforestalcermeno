import { test, expect } from '@playwright/test';

test.describe('Scenario persistence', () => {
  test.beforeEach(async ({ page }) => {
    await page.setViewportSize({ width: 1280, height: 800 });
    await page.goto('/');
    await page.evaluate(() => localStorage.clear());
    await page.reload();
  });

  test('save and reload persists scenario', async ({ page }) => {
    const nameInput = page.locator('#scenario-name');
    await expect(nameInput).toBeVisible();
    await nameInput.fill('Mi Finca');
    await page.getByRole('button', { name: 'Guardar', exact: true }).click();

    await page.reload();

    // The saved scenario should appear as an option in the combobox
    const select = page.getByRole('combobox');
    await expect(select).toBeVisible();
    const options = select.locator('option');
    await expect(options.filter({ hasText: 'Mi Finca' })).toHaveCount(1);
  });

  test('load scenario updates inputs', async ({ page }) => {
    const nameInput = page.locator('#scenario-name');
    await expect(nameInput).toBeVisible();

    const hectaresInput = page.locator('#productive_hectares');
    await expect(hectaresInput).toBeVisible();
    await hectaresInput.fill('25');

    await nameInput.fill('Finca Grande');
    await page.getByRole('button', { name: 'Guardar', exact: true }).click();

    await page.reload();

    const select = page.getByRole('combobox');
    await select.selectOption('Finca Grande');
    await page.getByRole('button', { name: 'Cargar', exact: true }).click();

    await expect(hectaresInput).toHaveValue('25');
  });

  test('delete scenario removes it from dropdown', async ({ page }) => {
    const nameInput = page.locator('#scenario-name');
    await expect(nameInput).toBeVisible();

    await page.getByRole('button', { name: 'Guardar', exact: true }).click();

    const select = page.getByRole('combobox');
    await select.selectOption('Escenario 1');

    await page.getByRole('button', { name: 'Eliminar seleccionado' }).click();

    await expect(select).not.toBeVisible();
  });
});
