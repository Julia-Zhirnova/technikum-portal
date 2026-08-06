/**
 * БП 1.1.6: Silent Auth (автообновление токенов)
 * Тест-кейсы: 1.1-025, 1.1-026
 * 
 * Источник требований: таблица тест-кейсов БП 1.1
 */
import { test, expect } from '@playwright/test';

const TEST_USER = {
  email: 'arhipov_kyu@luberteh.ru',
  password: 'student2026'
};

// Истёкший JWT (exp в прошлом)
const EXPIRED_TOKEN = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzg2MDE0MTExLCJpYXQiOjE3ODYwMTc3MTEsImp0aSI6Ijg3NGFkMzJkNGYzNTQzNTE5MzA4OTVmMzhkZmRlZWIyIiwidXNlcl9pZCI6MTkyfQ.5drbx1GM6s7NU-t9q-noSpCX3_0j_tHutEuWASx8yiQ';

test.describe('БП 1.1.6: Silent Auth', () => {

  test('1.1-025: Автоматическое обновление access-токена через axios interceptor', async ({ page }) => {
    // Входим как тестовый пользователь
    await page.goto('http://localhost:5173/login');
    await page.locator('input[type="email"]').fill(TEST_USER.email);
    await page.locator('input[type="password"]').fill(TEST_USER.password);
    await page.locator('button:has-text("Войти")').click();
    await page.waitForURL('**/student/profile**', { timeout: 10000 });

    // Получаем валидный access-токен (для сравнения)
    const validToken = await page.evaluate(() => localStorage.getItem('access_token'));
    expect(validToken).toBeTruthy();

    // Перехватываем запрос к /api/token/refresh/
    let refreshCalled = false;
    await page.route('**/api/token/refresh/**', async route => {
      refreshCalled = true;
      await route.continue();
    });

    // Искусственно "истекаем" access-токен
    await page.evaluate((expired) => {
      localStorage.setItem('access_token', expired);
    }, EXPIRED_TOKEN);

    // Делаем API-запрос ЧЕРЕЗ AXIOS (window.api) — это вызывает interceptor
    const result = await page.evaluate(async (expired) => {
      const api = (window as any).api;
      if (!api) return { error: 'api not found on window' };
      
      try {
        const response = await api.get('/user/profile/');
        return { 
          success: true, 
          newToken: localStorage.getItem('access_token'),
          status: response.status 
        };
      } catch (error: any) {
        return { 
          error: error.message,
          newToken: localStorage.getItem('access_token')
        };
      }
    }, EXPIRED_TOKEN);

    console.log('Result:', result);

    // Ждём немного
    await page.waitForTimeout(2000);

    // Проверяем, что POST /api/token/refresh/ был вызван
    expect(refreshCalled).toBe(true);

    // Проверяем, что access_token обновлён
    const newToken = await page.evaluate(() => localStorage.getItem('access_token'));
    expect(newToken).not.toBe(EXPIRED_TOKEN);
    expect(newToken).toBeTruthy();
  });

  test('1.1-026: Восстановление сессии при F5 через SmartRedirect', async ({ page }) => {
    // Перехватываем запрос к /api/token/refresh/
    let refreshCalled = false;
    await page.route('**/api/token/refresh/**', async route => {
      refreshCalled = true;
      await route.continue();
    });

    // Входим как тестовый пользователь
    await page.goto('http://localhost:5173/login');
    await page.locator('input[type="email"]').fill(TEST_USER.email);
    await page.locator('input[type="password"]').fill(TEST_USER.password);
    await page.locator('button:has-text("Войти")').click();
    await page.waitForURL('**/student/profile**', { timeout: 10000 });

    // Заменяем валидный токен на истёкший (вместо удаления)
    // Это заставит SmartRedirect проверить exp, увидеть, что токен истёк,
    // и вызвать fetch для refresh
    await page.evaluate((expired) => {
      localStorage.setItem('access_token', expired);
    }, EXPIRED_TOKEN);

    // Ждём, чтобы localStorage гарантированно обновился
    await page.waitForTimeout(500);

    // Обновляем страницу (F5)
    await page.reload();

    // Ждём, чтобы SmartRedirect успел отработать
    await page.waitForTimeout(5000);

    // Проверяем, что POST /api/token/refresh/ был вызван
    expect(refreshCalled).toBe(true);

    // Проверяем, что мы на /student/profile (не на /login)
    await expect(page).toHaveURL(/\/student\/profile/);

    // Проверяем, что access_token восстановлен (не равен EXPIRED_TOKEN)
    const restoredToken = await page.evaluate(() => localStorage.getItem('access_token'));
    expect(restoredToken).toBeTruthy();
    expect(restoredToken).not.toBe(EXPIRED_TOKEN);
  });

});
