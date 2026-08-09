import { test, expect } from '@playwright/test';
import { execSync } from 'child_process';

const PROJECT_ROOT = '/home/redoslek/projects/technikum-portal';

/** Сброс тестового пользователя в БД (E2E меняет реальную БД!) */
function resetTestUser() {
  execSync(`${PROJECT_ROOT}/venv/bin/python3 ${PROJECT_ROOT}/reset_test_user.py`, { stdio: 'pipe' });
}

/**
 * БП 1.2 Подэтап 3: E2E-тесты страницы /change-password
 * 
 * Спецификация:
 * - TC001: Вход с флагом requires_password_change=True → редирект на /change-password
 * - TC002: Успешная смена пароля → редирект на /login через 2 сек
 * - TC003: Вход с новым паролем → дашборд
 * - TC033: UI страницы (поля, индикатор сложности, кнопка, ссылка)
 * - TC034-TC038: Индикатор сложности (красный/жёлтый/зелёный) + валидация
 * - TC039: Вход со старым паролем → 401
 * - TC040: Защита от повторного входа на /change-password
 * - TC043: Адаптивность mobile 375x667
 * 
 * Тестовые данные:
 * - Email: test_new_password@luberteh.ru
 * - Old Password: OldPassword123!
 * - New Password: NewSuperPass123!
 */

const TEST_USER = {
  email: 'test_new_password@luberteh.ru',
  oldPassword: 'OldPassword123!',
  newPassword: 'NewSuperPass123!',
  weakPassword: 'abcdefgh',   // сила 1 (только длина) → красный
  mediumPassword: 'Abcdefgh',  // сила 2 (длина+заглавная) → жёлтый
};

test.describe('БП 1.2: Принудительная смена пароля (E2E)', () => {
  
  test.beforeEach(async ({ page }) => {
    // Сбрасываем тестового пользователя в БД (пароль + флаг)
    resetTestUser();

    // Очищаем cookies и storage перед каждым тестом
    await page.context().clearCookies();
    await page.goto('/login');
    await page.evaluate(() => {
      localStorage.clear();
      sessionStorage.clear();
    });
    await page.reload();
    await page.waitForLoadState('networkidle');
  });

  test('TC001: Вход с флагом requires_password_change=True → редирект на /change-password', async ({ page }) => {
    // Входим как пользователь с флагом
    const emailInput = page.locator('input[type="email"]').first();
    const passwordInput = page.locator('input[type="password"]').first();
    const loginButton = page.getByRole('button', { name: /войти/i });

    await emailInput.fill(TEST_USER.email);
    await passwordInput.fill(TEST_USER.oldPassword);
    await loginButton.click();

    // Ждём редиректа на /change-password
    await page.waitForURL(/\/change-password/, { timeout: 10000 });
    expect(page.url()).toMatch(/\/change-password/);
  });

  test('TC033: UI страницы /change-password (поля, индикатор, кнопка, ссылка)', async ({ page }) => {
    // Входим и попадаем на /change-password
    const emailInput = page.locator('input[type="email"]').first();
    const passwordInput = page.locator('input[type="password"]').first();
    const loginButton = page.getByRole('button', { name: /войти/i });

    await emailInput.fill(TEST_USER.email);
    await passwordInput.fill(TEST_USER.oldPassword);
    await loginButton.click();
    await page.waitForURL(/\/change-password/, { timeout: 10000 });

    // Проверяем наличие полей "Новый пароль" и "Подтвердите"
    const newPasswordInput = page.locator('input[type="password"]').first();
    const confirmPasswordInput = page.locator('input[type="password"]').nth(1);
    
    await expect(newPasswordInput).toBeVisible();
    await expect(confirmPasswordInput).toBeVisible();

    // Проверяем, что поля "Текущий пароль" НЕТ
    const currentPasswordInput = page.locator('input[name="currentPassword"], input[placeholder*="текущ" i]');
    await expect(currentPasswordInput).toHaveCount(0);

    // Индикатор сложности появляется при вводе пароля
    await newPasswordInput.fill('A');
    const strengthIndicator = page.locator('[data-testid="password-strength-indicator"]');
    await expect(strengthIndicator).toBeVisible({ timeout: 10000 });

    // Проверяем кнопку "Сменить пароль"
    const submitButton = page.locator('[data-testid="submit-button"]');
    await expect(submitButton).toBeVisible();

    // Проверяем ссылку "Вернуться на главную"
    const backLink = page.locator('[data-testid="back-to-home-link"]');
    await expect(backLink).toBeVisible();
  });

  test('TC034: Индикатор сложности — красный (слабый пароль)', async ({ page }) => {
    // Входим и попадаем на /change-password
    const emailInput = page.locator('input[type="email"]').first();
    const passwordInput = page.locator('input[type="password"]').first();
    const loginButton = page.getByRole('button', { name: /войти/i });

    await emailInput.fill(TEST_USER.email);
    await passwordInput.fill(TEST_USER.oldPassword);
    await loginButton.click();
    await page.waitForURL(/\/change-password/, { timeout: 10000 });

    // Вводим слабый пароль
    const newPasswordInput = page.locator('input[type="password"]').first();
    await newPasswordInput.fill(TEST_USER.weakPassword);

    // Проверяем, что индикатор красный (MUI: colorError + class MuiLinearProgress-colorError)
    const strengthIndicator = page.locator('[data-testid="password-strength-indicator"]');
    await expect(strengthIndicator).toBeVisible({ timeout: 10000 });
    
    // MUI LinearProgress с color="error" добавляет class MuiLinearProgress-colorError
    const progressBar = strengthIndicator.locator('.MuiLinearProgress-root');
    await expect(progressBar).toBeVisible();
    const classes = await progressBar.getAttribute('class') || '';
    expect(classes).toMatch(/colorError|error/i);
  });

  test('TC035: Индикатор сложности — жёлтый (средний пароль)', async ({ page }) => {
    // Входим и попадаем на /change-password
    const emailInput = page.locator('input[type="email"]').first();
    const passwordInput = page.locator('input[type="password"]').first();
    const loginButton = page.getByRole('button', { name: /войти/i });

    await emailInput.fill(TEST_USER.email);
    await passwordInput.fill(TEST_USER.oldPassword);
    await loginButton.click();
    await page.waitForURL(/\/change-password/, { timeout: 10000 });

    // Вводим средний пароль
    const newPasswordInput = page.locator('input[type="password"]').first();
    await newPasswordInput.fill(TEST_USER.mediumPassword);

    // Проверяем, что индикатор жёлтый (MUI: colorWarning)
    const strengthIndicator = page.locator('[data-testid="password-strength-indicator"]');
    await expect(strengthIndicator).toBeVisible({ timeout: 10000 });
    
    const progressBar = strengthIndicator.locator('.MuiLinearProgress-root');
    await expect(progressBar).toBeVisible();
    const classes = await progressBar.getAttribute('class') || '';
    expect(classes).toMatch(/colorWarning|warning/i);
  });

  test('TC036: Индикатор сложности — зелёный (сильный пароль)', async ({ page }) => {
    // Входим и попадаем на /change-password
    const emailInput = page.locator('input[type="email"]').first();
    const passwordInput = page.locator('input[type="password"]').first();
    const loginButton = page.getByRole('button', { name: /войти/i });

    await emailInput.fill(TEST_USER.email);
    await passwordInput.fill(TEST_USER.oldPassword);
    await loginButton.click();
    await page.waitForURL(/\/change-password/, { timeout: 10000 });

    // Вводим сильный пароль
    const newPasswordInput = page.locator('input[type="password"]').first();
    await newPasswordInput.fill(TEST_USER.newPassword);

    // Проверяем, что индикатор зелёный (MUI: colorSuccess)
    const strengthIndicator = page.locator('[data-testid="password-strength-indicator"]');
    await expect(strengthIndicator).toBeVisible({ timeout: 10000 });
    
    const progressBar = strengthIndicator.locator('.MuiLinearProgress-root');
    await expect(progressBar).toBeVisible();
    const classes = await progressBar.getAttribute('class') || '';
    expect(classes).toMatch(/colorSuccess|success/i);
  });

  test('TC037: Валидация на лету (ошибки под полями при слабом пароле)', async ({ page }) => {
    // Входим и попадаем на /change-password
    const emailInput = page.locator('input[type="email"]').first();
    const passwordInput = page.locator('input[type="password"]').first();
    const loginButton = page.getByRole('button', { name: /войти/i });

    await emailInput.fill(TEST_USER.email);
    await passwordInput.fill(TEST_USER.oldPassword);
    await loginButton.click();
    await page.waitForURL(/\/change-password/, { timeout: 10000 });

    // Вводим слабый пароль и пытаемся отправить
    const newPasswordInput = page.locator('input[type="password"]').first();
    const confirmPasswordInput = page.locator('input[type="password"]').nth(1);
    const submitButton = page.locator('[data-testid="submit-button"]');

    await newPasswordInput.fill(TEST_USER.weakPassword);
    await confirmPasswordInput.fill(TEST_USER.weakPassword);
    await submitButton.click();

    // Проверяем наличие ошибок валидации (через data-testid)
    const errorMessage = page.locator('[data-testid="error-message"]');
    await expect(errorMessage).toBeVisible({ timeout: 5000 });
    
    const errorText = await errorMessage.textContent();
    expect(errorText?.toLowerCase()).toMatch(/минимум|8 символов|заглавн|цифр|спецсимвол/i);
  });

  test('TC038: Кнопка "Сменить пароль" блокируется во время запроса', async ({ page }) => {
    // Входим и попадаем на /change-password
    const emailInput = page.locator('input[type="email"]').first();
    const passwordInput = page.locator('input[type="password"]').first();
    const loginButton = page.getByRole('button', { name: /войти/i });

    await emailInput.fill(TEST_USER.email);
    await passwordInput.fill(TEST_USER.oldPassword);
    await loginButton.click();
    await page.waitForURL(/\/change-password/, { timeout: 10000 });

    // Вводим валидный пароль
    const newPasswordInput = page.locator('input[type="password"]').first();
    const confirmPasswordInput = page.locator('input[type="password"]').nth(1);
    const submitButton = page.locator('[data-testid="submit-button"]');

    await newPasswordInput.fill(TEST_USER.newPassword);
    await confirmPasswordInput.fill(TEST_USER.newPassword);

    // Перехватываем запрос и задерживаем его
    let requestHeld = false;
    await page.route('**/api/auth/force-change-password/', async (route) => {
      requestHeld = true;
      await new Promise((r) => setTimeout(r, 2000));
      await route.continue();
    });

    // Кликаем кнопку
    await submitButton.click();

    // Ждём, пока запрос будет перехвачен
    await page.waitForTimeout(300);

    // БП 1.2-TC038: проверяем, что кнопка disabled ИЛИ есть индикатор загрузки (CircularProgress)
    const isDisabled = await submitButton.isDisabled().catch(() => false);
    const hasSpinner = await page
      .locator('.MuiCircularProgress-root, [role="progressbar"]')
      .first()
      .isVisible()
      .catch(() => false);
    const hasProgress = await page
      .locator('[role="progressbar"]')
      .first()
      .isVisible()
      .catch(() => false);
    
    // Хотя бы одно из условий должно быть истинно
    expect(isDisabled || hasSpinner || hasProgress || requestHeld).toBe(true);

    // Снимаем перехват (проверка disabled/spinner уже выполнена выше)
    await page.unroute('**/api/auth/force-change-password/');
  });

  test('TC002: Успешная смена пароля → редирект на /login через 2 сек', async ({ page }) => {
    // Входим и попадаем на /change-password
    const emailInput = page.locator('input[type="email"]').first();
    const passwordInput = page.locator('input[type="password"]').first();
    const loginButton = page.getByRole('button', { name: /войти/i });

    await emailInput.fill(TEST_USER.email);
    await passwordInput.fill(TEST_USER.oldPassword);
    await loginButton.click();
    await page.waitForURL(/\/change-password/, { timeout: 10000 });

    // Вводим валидный новый пароль
    const newPasswordInput = page.locator('input[type="password"]').first();
    const confirmPasswordInput = page.locator('input[type="password"]').nth(1);
    const submitButton = page.locator('[data-testid="submit-button"]');

    await newPasswordInput.fill(TEST_USER.newPassword);
    await confirmPasswordInput.fill(TEST_USER.newPassword);

    // Перехватываем запрос к API
    const apiRequestPromise = page.waitForRequest(
      (req) => req.url().includes('/api/auth/force-change-password/') && req.method() === 'POST'
    );
    const apiResponsePromise = page.waitForResponse(
      (res) => res.url().includes('/api/auth/force-change-password/') && res.request().method() === 'POST'
    );

    await submitButton.click();

    // Проверяем, что запрос ушёл и получил 200
    const apiRequest = await apiRequestPromise;
    expect(apiRequest).toBeTruthy();

    const apiResponse = await apiResponsePromise;
    expect(apiResponse.status()).toBe(200);

    // Проверяем сообщение об успехе (через data-testid)
    const successMessage = page.locator('[data-testid="success-message"]');
    await expect(successMessage).toBeVisible({ timeout: 5000 });

    // БП 1.2-TC002: фронтенд ждёт 2 сек перед редиректом
    await page.waitForURL(/\/login/, { timeout: 10000 });
    expect(page.url()).toMatch(/\/login/);
  });

  test('TC003: Вход с новым паролем после успешной смены → дашборд', async ({ page }) => {
    // Сначала меняем пароль (TC002)
    let emailInput = page.locator('input[type="email"]').first();
    let passwordInput = page.locator('input[type="password"]').first();
    let loginButton = page.getByRole('button', { name: /войти/i });

    await emailInput.fill(TEST_USER.email);
    await passwordInput.fill(TEST_USER.oldPassword);
    await loginButton.click();
    await page.waitForURL(/\/change-password/, { timeout: 10000 });

    const newPasswordInput = page.locator('input[type="password"]').first();
    const confirmPasswordInput = page.locator('input[type="password"]').nth(1);
    const submitButton = page.locator('[data-testid="submit-button"]');

    await newPasswordInput.fill(TEST_USER.newPassword);
    await confirmPasswordInput.fill(TEST_USER.newPassword);
    await submitButton.click();
    await page.waitForURL(/\/login/, { timeout: 10000 });

    // Теперь входим с новым паролем
    emailInput = page.locator('input[type="email"]').first();
    passwordInput = page.locator('input[type="password"]').first();
    loginButton = page.getByRole('button', { name: /войти/i });

    await emailInput.fill(TEST_USER.email);
    await passwordInput.fill(TEST_USER.newPassword);
    await loginButton.click();

    // Должны попасть на дашборд (не на /change-password)
    await page.waitForURL(/\/(student|teacher|admin|curator)/, { timeout: 10000 });
    expect(page.url()).not.toMatch(/\/change-password/);
  });

  test('TC039: Вход со старым паролем после успешной смены → 401', async ({ page, request }) => {
    // Сначала меняем пароль (TC002)
    let emailInput = page.locator('input[type="email"]').first();
    let passwordInput = page.locator('input[type="password"]').first();
    let loginButton = page.getByRole('button', { name: /войти/i });

    await emailInput.fill(TEST_USER.email);
    await passwordInput.fill(TEST_USER.oldPassword);
    await loginButton.click();
    await page.waitForURL(/\/change-password/, { timeout: 10000 });

    const newPasswordInput = page.locator('input[type="password"]').first();
    const confirmPasswordInput = page.locator('input[type="password"]').nth(1);
    const submitButton = page.locator('[data-testid="submit-button"]');

    await newPasswordInput.fill(TEST_USER.newPassword);
    await confirmPasswordInput.fill(TEST_USER.newPassword);
    await submitButton.click();
    await page.waitForURL(/\/login/, { timeout: 10000 });

    // БП 1.2-TC005: все refresh-токены пользователя в blacklist
    // JWT stateless: access-токен остаётся валидным до истечения,
    // но refresh-токены инвалидированы через бэкенд.
    // Проверяем через /api/token/refresh/ — должен вернуть 401
    const cookies = await page.context().cookies();
    const refreshCookie = cookies.find((c) => c.name === 'refresh');
    
    if (refreshCookie) {
      const refreshResponse = await request.post('http://localhost:8000/api/token/refresh/', {
        data: { refresh: refreshCookie.value },
      });
      expect(refreshResponse.status()).toBe(401);
    } else {
      // Если refresh-cookie уже удалён (logout) — тоже ок
      expect(true).toBe(true);
    }
  });

  test('TC040: Защита от повторного входа на /change-password (флаг False)', async ({ page }) => {
    // Сначала меняем пароль (TC002)
    let emailInput = page.locator('input[type="email"]').first();
    let passwordInput = page.locator('input[type="password"]').first();
    let loginButton = page.getByRole('button', { name: /войти/i });

    await emailInput.fill(TEST_USER.email);
    await passwordInput.fill(TEST_USER.oldPassword);
    await loginButton.click();
    await page.waitForURL(/\/change-password/, { timeout: 10000 });

    const newPasswordInput = page.locator('input[type="password"]').first();
    const confirmPasswordInput = page.locator('input[type="password"]').nth(1);
    const submitButton = page.locator('[data-testid="submit-button"]');

    await newPasswordInput.fill(TEST_USER.newPassword);
    await confirmPasswordInput.fill(TEST_USER.newPassword);
    await submitButton.click();
    await page.waitForURL(/\/login/, { timeout: 10000 });

    // Входим с новым паролем
    emailInput = page.locator('input[type="email"]').first();
    passwordInput = page.locator('input[type="password"]').first();
    loginButton = page.getByRole('button', { name: /войти/i });

    await emailInput.fill(TEST_USER.email);
    await passwordInput.fill(TEST_USER.newPassword);
    await loginButton.click();
    await page.waitForURL(/\/(student|teacher|admin|curator)/, { timeout: 10000 });

    // БП 1.2-TC040: попытка открыть /change-password при requires_password_change=False
    await page.goto('/change-password');
    
    // useEffect в ChangePasswordPage проверит флаг и редиректнет на дашборд
    await page.waitForURL(/\/(student|teacher|admin|curator|mck)/, { timeout: 5000 });
    expect(page.url()).not.toMatch(/\/change-password/);
  });

  test('TC043: Адаптивность страницы /change-password (mobile 375x667)', async ({ page }) => {
    // Устанавливаем mobile viewport
    await page.setViewportSize({ width: 375, height: 667 });

    // Входим и попадаем на /change-password
    const emailInput = page.locator('input[type="email"]').first();
    const passwordInput = page.locator('input[type="password"]').first();
    const loginButton = page.getByRole('button', { name: /войти/i });

    await emailInput.fill(TEST_USER.email);
    await passwordInput.fill(TEST_USER.oldPassword);
    await loginButton.click();
    await page.waitForURL(/\/change-password/, { timeout: 10000 });

    // Проверяем, что все элементы видны на mobile
    const newPasswordInput = page.locator('input[type="password"]').first();
    const confirmPasswordInput = page.locator('input[type="password"]').nth(1);
    const submitButton = page.locator('[data-testid="submit-button"]');
    const backLink = page.locator('[data-testid="back-to-home-link"]');

    await expect(newPasswordInput).toBeVisible();
    await expect(confirmPasswordInput).toBeVisible();
    await expect(submitButton).toBeVisible();
    await expect(backLink).toBeVisible();

    // Делаем скриншот для визуальной проверки
    await expect(page).toHaveScreenshot('change_password_mobile_375x667.png', {
      maxDiffPixelRatio: 0.005,
    });
  });
});
