import { test, expect } from '@playwright/test';

test.describe('Security', () => {
  test('CSP meta tag is present and restrictive', async ({ page }) => {
    await page.goto('/');
    const csp = await page.getAttribute('meta[http-equiv="Content-Security-Policy"]', 'content');
    expect(csp).toBeTruthy();
    expect(csp).toContain("script-src 'self'");
    expect(csp).toContain("default-src 'self'");
    expect(csp).not.toContain('unsafe-eval');
  });

  test('app loads cleanly with tampered localStorage (proto pollution)', async ({ page }) => {
    await page.goto('/');

    await page.evaluate(() => {
      const malicious = {
        __proto__: { admin: true },
        constructor: { polluted: true },
        prototype: { evil: true },
        '<script>alert(1)</script>': { productive_hectares: 999 },
        valid_scenario: { productive_hectares: 10, cherry_yield_per_ha: 5000 },
      };
      localStorage.setItem('agroforestal-scenarios', JSON.stringify(malicious));
    });

    await page.reload();
    await expect(page.getByText('Agroforestal Cermeño')).toBeVisible();

    const alertTriggered = await page.evaluate(() => {
      return (window as unknown as Record<string, unknown>).__alertTriggered ?? false;
    });
    expect(alertTriggered).toBe(false);
  });

  test('app loads cleanly with malformed JSON in localStorage', async ({ page }) => {
    await page.goto('/');
    await page.evaluate(() => {
      localStorage.setItem('agroforestal-scenarios', 'not-valid-json{{{');
    });
    await page.reload();
    await expect(page.getByText('Agroforestal Cermeño')).toBeVisible();
  });

  test('script tags in scenario name are escaped (no XSS)', async ({ page }) => {
    await page.setViewportSize({ width: 1280, height: 800 });
    await page.goto('/');

    const nameInput = page.locator('#scenario-name');
    await expect(nameInput).toBeVisible();
    await nameInput.fill('<img src=x onerror=alert(1)>');
    await page.getByRole('button', { name: 'Guardar', exact: true }).click();

    await page.reload();

    let dialogAppeared = false;
    page.on('dialog', () => { dialogAppeared = true; });
    await page.waitForTimeout(500);
    expect(dialogAppeared).toBe(false);
  });

  test('app ignores query string parameters', async ({ page }) => {
    await page.goto('/?evil=<script>alert(1)</script>&xss=true');
    await expect(page.getByText('Agroforestal Cermeño')).toBeVisible();
  });
});
