import { test, expect } from '@playwright/test';

/**
 * БП 1.1-TC039, TC040, TC041, TC042: Визуальные регрессионные тесты
 * 
 * Эталонные скриншоты создаются при первом запуске.
 * Для обновления baseline: npx playwright test visual_regression.spec.ts --update-snapshots
 */

test.describe('БП 1.1-TC039: Визуальная регрессия страницы /login', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/login');
  });

  test('TC039: Desktop (1920x1080)', async ({ page }) => {
    await page.setViewportSize({ width: 1920, height: 1080 });
    await expect(page).toHaveScreenshot('login_desktop_1920x1080.png', {
      maxDiffPixelRatio: 0.005,
    });
  });

  test('TC040: Mobile (375x667, iPhone SE)', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });
    await expect(page).toHaveScreenshot('login_mobile_375x667.png', {
      maxDiffPixelRatio: 0.005,
    });
  });

  test('TC041: Tablet (768x1024)', async ({ page }) => {
    await page.setViewportSize({ width: 768, height: 1024 });
    await expect(page).toHaveScreenshot('login_tablet_768x1024.png', {
      maxDiffPixelRatio: 0.005,
    });
  });

  test('TC042: 4K (3840x2160)', async ({ page }) => {
    await page.setViewportSize({ width: 3840, height: 2160 });
    await expect(page).toHaveScreenshot('login_4k_3840x2160.png', {
      maxDiffPixelRatio: 0.005,
    });
  });
});
