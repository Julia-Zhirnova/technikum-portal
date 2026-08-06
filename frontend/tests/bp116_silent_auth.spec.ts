/**
 * БП 1.1.6: Silent Auth (автообновление токенов)
 * Тест-кейсы: 1.1-025, 1.1-026
 */
import { test, expect } from '@playwright/test';

const TEST_USER = {
  email: 'silent_auth@test.ru',
  password: 'TestPass123!'
};

test.describe('БП 1.1.6: Silent Auth', () => {

  test('1.1-025: Автоматическое обновление access-токена при 401', async ({ page }) => {
    // Входим как тестовый пользователь
    await page.goto('http://localhost:5173/login');
    await page.locator('input[type="email"]').fill(TEST_USER.email);
    await page.locator('input[type="password"]').fill(TEST_USER.password);
    await page.locator('button:has-text("Войти")').click();
    await page.waitForURL('**/student/profile**', { timeout: 10000 });

    // Искусственно "истекаем" access-токен, заменяя его на невалидный
    await page.evaluate(() => {
      localStorage.setItem('access_token', 'expired_invalid_token');
    });

    // Перехватываем запрос к /api/token/refresh/
    let refreshCalled = false;
    await page.route('**/api/token/refresh/**', async route => {
      refreshCalled = true;
      // Разрешаем запросу пройти (бэкенд вернёт новый access-токен)
      await route.continue();
    });

    // Делаем запрос к защищённому endpoint (загрузка профиля)
    // Это должно вызвать 401 → интерцептор → POST /api/token/refresh/ → повторный запрос
    const profileResponse = await page.evaluate(async () => {
      const response = await fetch('/api/user/profile/', {
        headers: { 'Authorization': `Bearer ${localStorage.getItem('access_token')}` }
      });
      return response.status;
    });

    // Проверяем, что POST /api/token/refresh/ был вызван
    expect(refreshCalled).toBe(true);

    // Проверяем, что access_token обновлён (не равен 'expired_invalid_token')
    const newToken = await page.evaluate(() => localStorage.getItem('access_token'));
    expect(newToken).not.toBe('expired_invalid_token');
    expect(newToken).toBeTruthy();
  });

  test('1.1-026: Восстановление сессии при F5 (refresh из httpOnly cookie)', async ({ page }) => {
    // Входим как тестовый пользователь
    await page.goto('http://localhost:5173/login');
    await page.locator('input[type="email"]').fill(TEST_USER.email);
    await page.locator('input[type="password"]').fill(TEST_USER.password);
    await page.locator('button:has-text("Войти")').click();
    await page.waitForURL('**/student/profile**', { timeout: 10000 });

    // Удаляем access_token из localStorage (имитируем F5, когда токен потерян)
    await page.evaluate(() => {
      localStorage.removeItem('access_token');
    });

    // Обновляем страницу (F5)
    await page.reload();

    // Ожидаем, что SmartRedirect попробует восстановить сессию через /api/token/refresh/
    // и редиректнет обратно на /student/profile (не на /login)
    await page.waitForURL('**/student/profile**', { timeout: 15000 });
    await expect(page).toHaveURL(/\/student\/profile/);

    // Проверяем, что access_token восстановлен
    const restoredToken = await page.evaluate(() => localStorage.getItem('access_token'));
    expect(restoredToken).toBeTruthy();
  });

});
