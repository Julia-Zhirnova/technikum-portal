import { test, expect } from '@playwright/test';

/**
 * БП 1.1-017: Выход из системы
 *
 * Спецификация:
 * - Пользователь нажимает кнопку "ВЫХОД"
 * - Фронтенд отправляет POST /api/logout/ (с access-токеном)
 * - Бэкенд извлекает refresh-токен из httpOnly cookie, добавляет в blacklist
 * - Бэкенд удаляет httpOnly cookie (Set-Cookie: refresh=; Max-Age=0)
 * - Фронтенд очищает localStorage и редиректит на /login
 *
 * SQL-проверка: SELECT COUNT(*) FROM token_blacklist_blacklistedtoken
 *               WHERE token='<refresh_token>'; — значение ≥ 1
 *
 * Тестовые данные:
 * - Email: arhipov_kyu@luberteh.ru
 * - Password: student2026
 */

const STUDENT_EMAIL = 'arhipov_kyu@luberteh.ru';
const STUDENT_PASSWORD = 'student2026';

test.describe('БП 1.1-017: Выход из системы', () => {
  test.beforeEach(async ({ page }) => {
    // Очищаем cookies и storage
    await page.context().clearCookies();
    await page.goto('/login');
    await page.evaluate(() => {
      localStorage.clear();
      sessionStorage.clear();
    });
    await page.reload();
    await page.waitForLoadState('networkidle');

    // Входим как студент
    const emailInput = page.locator('input[type="email"], input[name="email"]').first();
    const passwordInput = page.locator('input[type="password"]').first();
    const loginButton = page.getByRole('button', { name: /войти/i });

    await emailInput.fill(STUDENT_EMAIL);
    await passwordInput.fill(STUDENT_PASSWORD);
    await loginButton.click();

    await page.waitForURL(/\/student\/profile/, { timeout: 10000 });
  });

  test('Кнопка "ВЫХОД" видна и кликабельна', async ({ page }) => {
    const logoutButton = page.locator('[data-testid="logout-button"]');
    await expect(logoutButton).toBeVisible();
    await expect(logoutButton).toBeEnabled();
  });

  test('Клик на "ВЫХОД" → POST /api/logout/ → редирект на /login', async ({ page }) => {
    const logoutButton = page.locator('[data-testid="logout-button"]');

    // Перехватываем запрос к /api/logout/
    const logoutRequestPromise = page.waitForRequest(
      (req) => req.url().includes('/api/logout/') && req.method() === 'POST'
    );
    const logoutResponsePromise = page.waitForResponse(
      (res) => res.url().includes('/api/logout/') && res.request().method() === 'POST'
    );

    await logoutButton.click();

    // Проверяем, что запрос ушёл
    const logoutRequest = await logoutRequestPromise;
    expect(logoutRequest).toBeTruthy();

    // Проверяем, что ответ 200 OK
    const logoutResponse = await logoutResponsePromise;
    expect(logoutResponse.status()).toBe(200);

    // Ждём редиректа на /login
    await page.waitForURL(/\/login/, { timeout: 10000 });
    expect(page.url()).toMatch(/\/login/);
  });

  test('Refresh-токен добавлен в blacklist после выхода', async ({ page }) => {
    // Получаем refresh-токен из cookies ДО выхода
    const cookiesBeforeLogout = await page.context().cookies();
    const refreshCookieBefore = cookiesBeforeLogout.find((c) => c.name === 'refresh');
    expect(refreshCookieBefore).toBeTruthy();
    const refreshTokenValue = refreshCookieBefore!.value;

    const logoutButton = page.locator('[data-testid="logout-button"]');

    // Ждём ответ от /api/logout/
    const logoutResponsePromise = page.waitForResponse(
      (res) => res.url().includes('/api/logout/')
    );

    await logoutButton.click();
    await logoutResponsePromise;
    await page.waitForURL(/\/login/, { timeout: 10000 });

    // Проверяем, что refresh-токен теперь в blacklist
    // Отправляем POST /api/token/refresh/ с этим токеном — должен вернуть 401
    const refreshResponse = await page.request.post('http://localhost:8000/api/token/refresh/', {
      data: { refresh: refreshTokenValue },
    });

    // Статус 401 подтверждает, что токен невалиден (в blacklist)
    expect(refreshResponse.status()).toBe(401);
    
    // SimpleJWT возвращает code='token_not_valid' для blacklisted токенов
    const responseData = await refreshResponse.json();
    expect(responseData.code || responseData.detail).toMatch(/invalid|blacklist|not valid|token_not_valid/i);
  });

  test('httpOnly cookie "refresh" удалена после выхода', async ({ page }) => {
    const logoutButton = page.locator('[data-testid="logout-button"]');

    await logoutButton.click();
    await page.waitForURL(/\/login/, { timeout: 10000 });

    // Проверяем cookies после выхода
    const cookiesAfterLogout = await page.context().cookies();
    const refreshCookieAfter = cookiesAfterLogout.find((c) => c.name === 'refresh');

    // Cookie 'refresh' должна быть удалена или истекла
    expect(refreshCookieAfter).toBeFalsy();
  });

  test('localStorage очищен после выхода', async ({ page }) => {
    const logoutButton = page.locator('[data-testid="logout-button"]');

    await logoutButton.click();
    await page.waitForURL(/\/login/, { timeout: 10000 });

    // Проверяем localStorage
    const accessToken = await page.evaluate(() => localStorage.getItem('access_token'));
    const activeRole = await page.evaluate(() => localStorage.getItem('activeRole'));

    expect(accessToken).toBeFalsy();
    expect(activeRole).toBeFalsy();
  });

});
