/**
 * БП 1.1.3: Выход из системы и полная маршрутизация ролей
 * Тест-кейсы: 1.1-009, 1.1-018, 1.1-017
 */
import { test, expect } from '@playwright/test';

test.describe('БП 1.1.3: Выход из системы и маршрутизация', () => {

  test('1.1-009: Маршрутизация председателя МЦК на /mck/rpd', async ({ page }) => {
    await page.goto('http://localhost:5173/login');
    await page.locator('input[type="email"]').fill('tardv69@yandex.ru');
    await page.locator('input[type="password"]').fill('student2026');
    await page.locator('button:has-text("Войти")').click();

    // tardv69 имеет роли [curator, mck_chairman, teacher]
    // Приоритет: mck_chairman > teacher > curator → редирект на /mck/rpd
    await page.waitForURL('**/mck/rpd**', { timeout: 10000 });
    await expect(page).toHaveURL(/\/mck\/rpd/);

    // Проверяем наличие кнопки переключения ролей
    const roleSwitcher = page.getByTestId('role-switcher-button');
    await expect(roleSwitcher).toBeVisible();
  });

  test('1.1-018: Пользователь без ролей редиректится на /access-denied', async ({ page }) => {
    await page.goto('http://localhost:5173/login');
    await page.locator('input[type="email"]').fill('no_roles_e2e@test.ru');
    await page.locator('input[type="password"]').fill('TestPass123!');
    await page.locator('button:has-text("Войти")').click();

    // Пользователь без ролей должен быть редирекнут на /access-denied
    await page.waitForURL('**/access-denied**', { timeout: 10000 });
    await expect(page).toHaveURL(/\/access-denied/);

    // На странице должна быть понятная информация
    await expect(page.locator('text=Нет доступа')).toBeVisible();
    await expect(page.locator('text=обратитесь к администратору')).toBeVisible();
  });

  test('1.1-017: Кнопка ВЫХОД вызывает POST /api/logout/ и редиректит на /login', async ({ page }) => {
    // Входим как студент
    await page.goto('http://localhost:5173/login');
    await page.locator('input[type="email"]').fill('arhipov_kyu@luberteh.ru');
    await page.locator('input[type="password"]').fill('student2026');
    await page.locator('button:has-text("Войти")').click();
    await page.waitForURL('**/student**', { timeout: 10000 });

    // Проверяем, что кнопка ВЫХОД видна и имеет data-testid
    const logoutButton = page.getByTestId('logout-button');
    await expect(logoutButton).toBeVisible();

    // Перехватываем запрос к /api/logout/
    let logoutCalled = false;
    await page.route('**/api/logout/**', async route => {
      logoutCalled = true;
      // Проверяем, что это POST
      expect(route.request().method()).toBe('POST');
      await route.fulfill({ status: 200, contentType: 'application/json', body: '{"detail":"ok"}' });
    });

    // Нажимаем кнопку ВЫХОД
    await logoutButton.click();

    // Проверяем редирект на /login
    await page.waitForURL('**/login**', { timeout: 10000 });
    await expect(page).toHaveURL(/\/login/);

    // Проверяем, что POST /api/logout/ действительно был вызван
    expect(logoutCalled).toBe(true);

    // Проверяем, что access_token очищен из localStorage
    const accessToken = await page.evaluate(() => localStorage.getItem('access_token'));
    expect(accessToken).toBeNull();
  });

});
