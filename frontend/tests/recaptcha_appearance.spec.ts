import { test, expect } from '@playwright/test';

/**
 * БП 1.1-013 (E2E часть): После 5 неудачных попыток появляется reCAPTCHA
 * Backend уже покрыт в test_brute_force.py, этот тест проверяет UI
 */

test.describe('БП 1.1: reCAPTCHA после 5 неудачных попыток', () => {
  test.beforeEach(async ({ page }) => {
    await page.context().clearCookies();
    await page.goto('/login');
    await page.evaluate(() => {
      localStorage.clear();
      sessionStorage.clear();
    });
  });

  test('После 5 неудачных попыток появляется сообщение о reCAPTCHA', async ({ page }) => {
    const emailInput = page.locator('input[type="email"]').first();
    const passwordInput = page.locator('input[type="password"]').first();
    const loginButton = page.getByRole('button', { name: /Войти/i });

    // 5 неудачных попыток
    for (let i = 0; i < 5; i++) {
      await page.goto('/login');
      await emailInput.fill('arhipov_kyu@luberteh.ru');
      await passwordInput.fill('WrongPass!');
      await loginButton.click();
      await page.waitForTimeout(500);
    }

    // 6-я попытка — должна вернуть require_captcha
    await page.goto('/login');
    await emailInput.fill('arhipov_kyu@luberteh.ru');
    await passwordInput.fill('WrongPass!');
    
    // Перехватываем ответ от /api/token/
    const responsePromise = page.waitForResponse(
      (response) => response.url().includes('/api/token/') && response.status() === 401
    );
    
    await loginButton.click();
    const response = await responsePromise;
    const responseData = await response.json();
    
    // Проверяем, что сервер вернул require_captcha: true
    expect(responseData.require_captcha).toBe(true);
    
    // Проверяем, что фронтенд показал виджет reCAPTCHA или сообщение
    // (в зависимости от реализации — либо iframe reCAPTCHA, либо текст)
    const recaptchaWidget = page.locator('iframe[src*="recaptcha"], [class*="recaptcha"], .g-recaptcha');
    const recaptchaMessage = page.getByText(/captcha|робот/i);
    
    // Хотя бы один из элементов должен быть виден
    const widgetCount = await recaptchaWidget.count();
    const messageCount = await recaptchaMessage.count();
    
    expect(widgetCount + messageCount).toBeGreaterThan(0);
  });
});
