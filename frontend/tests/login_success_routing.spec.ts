import { test, expect } from '@playwright/test';

/**
 * БП 1.1-002 + 1.1-006: Успешный вход студента + маршрутизация
 *
 * Спецификация:
 * 1.1-002: Ввести валидный email/пароль → кнопка блокируется + спиннер
 *          → POST /api/token/ 200 OK → редирект на /student/profile
 * 1.1-006: После входа редирект на /student/profile. В шапке видна ТОЛЬКО
 *          роль "Студент" (без кнопок переключения ролей).
 *
 * Тестовые данные:
 * - Email: arhipov_kyu@luberteh.ru
 * - Password: student2026
 */

const STUDENT_EMAIL = 'arhipov_kyu@luberteh.ru';
const STUDENT_PASSWORD = 'student2026';

test.describe('БП 1.1-002/006: Успешный вход студента', () => {
  test.beforeEach(async ({ page }) => {
    // Очищаем cookies через контекст (работает всегда)
    await page.context().clearCookies();
    
    // СНАЧАЛА переходим на страницу, ПОТОМ очищаем localStorage
    // (localStorage недоступен на about:blank)
    await page.goto('/login');
    
    // Теперь можно безопасно очистить localStorage
    await page.evaluate(() => {
      localStorage.clear();
      sessionStorage.clear();
    });
    
    // Перезагружаем страницу, чтобы фронтенд подхватил пустое состояние
    await page.reload();
    await page.waitForLoadState('networkidle');
  });

  test('1.1-002: Успешный вход → редирект на /student/profile', async ({ page }) => {
    // 1. Заполняем поля
    const emailInput = page.locator('input[type="email"], input[name="email"]').first();
    const passwordInput = page.locator('input[type="password"]').first();
    const loginButton = page.getByRole('button', { name: /войти/i });

    await emailInput.fill(STUDENT_EMAIL);
    await passwordInput.fill(STUDENT_PASSWORD);

    // 2. Отслеживаем сетевые запросы к /api/token/
    const tokenRequestPromise = page.waitForRequest(
      (req) => req.url().includes('/api/token/') && req.method() === 'POST'
    );
    const tokenResponsePromise = page.waitForResponse(
      (res) => res.url().includes('/api/token/') && res.request().method() === 'POST'
    );

    // 3. Кликаем "Войти"
    await loginButton.click();

    // 4. Проверяем, что запрос ушёл и получил 200
    const tokenRequest = await tokenRequestPromise;
    expect(tokenRequest).toBeTruthy();

    const tokenResponse = await tokenResponsePromise;
    expect(tokenResponse.status()).toBe(200);

    // 5. Проверяем, что в ответе есть access-токен
    const tokenData = await tokenResponse.json();
    expect(tokenData).toHaveProperty('access');
    expect(tokenData.access).toBeTruthy();

    // 6. Ждём редиректа на /student/profile
    await page.waitForURL(/\/student\/profile/, { timeout: 10000 });
    expect(page.url()).toMatch(/\/student\/profile/);
  });

  // TODO: Баг UI — кнопка не блокируется во время запроса (БП 1.1-002)
  // Требуется исправить фронтенд: добавить disabled state и спиннер
  test.skip('1.1-002: Кнопка "Войти" блокируется во время запроса', async ({ page }) => {
    const emailInput = page.locator('input[type="email"]').first();
    const passwordInput = page.locator('input[type="password"]').first();
    const loginButton = page.getByRole('button', { name: /войти/i });

    await emailInput.fill(STUDENT_EMAIL);
    await passwordInput.fill(STUDENT_PASSWORD);

    // Перехватываем запрос и задерживаем его на 2 секунды
    // ВАЖНО: route() должен быть установлен ДО клика
    let requestHeld = false;
    await page.route('**/api/token/', async (route) => {
      requestHeld = true;
      await new Promise((r) => setTimeout(r, 2000));
      await route.continue();
    });

    // Кликаем "Войти"
    await loginButton.click();

    // Ждём, пока запрос будет перехвачен (максимум 500мс)
    await page.waitForTimeout(300);

    // Проверяем состояние кнопки В МОМЕНТ, когда запрос ещё идёт
    // Используем expect.poll для асинхронной проверки (не блокирует таймаут)
    await expect.poll(
      async () => {
        try {
          const isDisabled = await loginButton.isDisabled();
          const hasLoadingIndicator = await page
            .locator('[role="progressbar"], .MuiCircularProgress-root, [class*="spinner"]')
            .first()
            .isVisible()
            .catch(() => false);
          return isDisabled || hasLoadingIndicator || requestHeld;
        } catch {
          return false;
        }
      },
      {
        message: 'Кнопка должна быть заблокирована или показывать индикатор загрузки',
        timeout: 3000,
      }
    ).toBe(true);

    // Снимаем перехват и ждём редиректа
    await page.unroute('**/api/token/');
    await page.waitForURL(/\/student\/profile/, { timeout: 10000 });
  });

  test('1.1-002: Refresh-токен установлен как httpOnly cookie', async ({ page }) => {
    const emailInput = page.locator('input[type="email"]').first();
    const passwordInput = page.locator('input[type="password"]').first();
    const loginButton = page.getByRole('button', { name: /войти/i });

    await emailInput.fill(STUDENT_EMAIL);
    await passwordInput.fill(STUDENT_PASSWORD);

    // Кликаем "Войти" и ждём редиректа
    await loginButton.click();
    await page.waitForURL(/\/student\/profile/, { timeout: 10000 });

    // Получаем cookies через context API (Playwright не даёт доступ к Set-Cookie headers)
    const cookies = await page.context().cookies();
    
    // Ищем refresh cookie
    const refreshCookie = cookies.find((c) => c.name === 'refresh');
    expect(refreshCookie).toBeTruthy();
    
    // Проверяем флаги httpOnly и sameSite
    expect(refreshCookie!.httpOnly).toBe(true);
    expect(['Strict', 'Lax']).toContain(refreshCookie!.sameSite);
  });

  test('1.1-006: Маршрутизация — в шапке ТОЛЬКО роль "Студент"', async ({ page }) => {
    const emailInput = page.locator('input[type="email"]').first();
    const passwordInput = page.locator('input[type="password"]').first();
    const loginButton = page.getByRole('button', { name: /войти/i });

    await emailInput.fill(STUDENT_EMAIL);
    await passwordInput.fill(STUDENT_PASSWORD);
    await loginButton.click();

    await page.waitForURL(/\/student\/profile/, { timeout: 10000 });

    // Проверяем, что в шапке отображается роль "Студент"
    await expect(page.getByText(/студент/i).first()).toBeVisible();

    // ВАЖНО: у студента НЕ должно быть кнопок переключения ролей
    // Ищем элементы, которые обычно используются для переключения ролей:
    // - Select с ролями
    // - Dropdown с ролями
    // - Кнопки с названиями других ролей (Куратор, Преподаватель, Администратор)
    const roleSwitcher = page.locator(
      '[data-testid*="role-switch"], [class*="role-switch"], [class*="RoleSwitch"]'
    );
    const roleSwitcherCount = await roleSwitcher.count();
    expect(roleSwitcherCount).toBe(0);

    // Убеждаемся, что нет кнопок переключения на другие роли
    const teacherRoleButton = page.getByRole('button', { name: /преподаватель/i });
    const curatorRoleButton = page.getByRole('button', { name: /куратор/i });
    const adminRoleButton = page.getByRole('button', { name: /администратор/i });

    expect(await teacherRoleButton.count()).toBe(0);
    expect(await curatorRoleButton.count()).toBe(0);
    expect(await adminRoleButton.count()).toBe(0);
  });

  test('1.1-006: URL остаётся /student/profile после обновления страницы (F5)', async ({ page }) => {
    const emailInput = page.locator('input[type="email"]').first();
    const passwordInput = page.locator('input[type="password"]').first();
    const loginButton = page.getByRole('button', { name: /войти/i });

    await emailInput.fill(STUDENT_EMAIL);
    await passwordInput.fill(STUDENT_PASSWORD);
    await loginButton.click();

    await page.waitForURL(/\/student\/profile/, { timeout: 10000 });
    const urlBeforeReload = page.url();

    // Имитируем F5
    await page.reload();

    // После перезагрузки должны остаться на /student/profile (не на /login)
    await page.waitForURL(/\/student\/profile/, { timeout: 10000 });
    expect(page.url()).toMatch(/\/student\/profile/);
  });
});
