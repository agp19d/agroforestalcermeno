import { test, expect } from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';

test.describe('Accessibility', () => {
  test('main page has no critical a11y violations', async ({ page }) => {
    // Use desktop viewport so sidebar is visible (not hidden in Sheet)
    await page.setViewportSize({ width: 1280, height: 800 });
    await page.goto('/');
    await page.waitForLoadState('networkidle');

    const results = await new AxeBuilder({ page })
      .withTags(['wcag2a', 'wcag2aa'])
      .disableRules(['color-contrast']) // Custom dark theme may have intentional contrast choices
      .analyze();

    const critical = results.violations.filter(
      (v) => v.impact === 'critical' || v.impact === 'serious'
    );
    expect(critical).toEqual([]);
  });

  test('each tab panel has no critical a11y violations', async ({ page }) => {
    // Use desktop viewport so sidebar is visible (not hidden in Sheet)
    await page.setViewportSize({ width: 1280, height: 800 });
    await page.goto('/');
    await page.waitForLoadState('networkidle');

    const tabs = ['Ingresos', 'Costos', 'Rentabilidad', 'Comparar', 'Monte Carlo'];
    for (const tabName of tabs) {
      await page.getByRole('tab', { name: tabName }).click();
      await page.waitForTimeout(300);

      const results = await new AxeBuilder({ page })
        .withTags(['wcag2a', 'wcag2aa'])
        .disableRules(['color-contrast'])
        .analyze();

      const critical = results.violations.filter(
        (v) => v.impact === 'critical' || v.impact === 'serious'
      );
      expect(critical, `Tab "${tabName}" has a11y violations`).toEqual([]);
    }
  });
});
