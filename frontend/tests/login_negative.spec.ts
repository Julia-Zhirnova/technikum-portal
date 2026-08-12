import { test, expect } from '@playwright/test';

/**
 * Негативные сценарии входа (БП 1.1-004, 1.1-005, 1.1-010)
 *
 * Спецификация:
 * 1.1-004 🔴: Неверный пароль → 401 + красный алерт "Неверный email или пароль"
 * 1.1-005 🔴: Несуществующий email → 401 + тот же алерт (защита от перебора)
 * 1.1-010 🔴: Заблокированный user → 401 + "Ваша учетная запись заблокирована"
 *
 * Тестовые данные:
 * - Валидный student: arhipov_kyu@luberteh.ru / student2026
 * - Заблокированный: заблокированный аккаунт в БД
 */

const STUDENT_EMAIL = 'arhipov_kyu@luberteh.ru';
const STUDENT_PASSWORD = 'student2026';

test.describe('БП 1.1: Негативные сценарии входа', () => {
  test.beforeEach(async ({ page }) => {
    await page.context().clearCookies();
    await page.goto('/login');
    await page.evaluate(() => {
      localStorage.clear();
      sessionStorage.clear();
    });
    await page.reload();
    await page.waitForLoadState('networkidle');
  });

  test('1.1-004: Неверный пароль → 401 + алерт "Неверный email или пароль"', async ({ page }) => {
    const emailInput = page.locator('input[type="email"], input[name="email"]').first();
    const passwordInput = page.locator('input[type="password"]').first();
    const loginButton = page.getByRole('button', { name: /войти/i });

    await emailInput.fill(STUDENT_EMAIL);
    await passwordInput.fill('WrongPassword123!');

    // Ждём ответ 401 от сервера
    const responsePromise = page.waitForResponse(
      (res) => res.url().includes('/api/token/') && res.status() === 401
    );

    await loginButton.click();
    const response = await responsePromise;
    expect(response.status()).toBe(401);

    // Проверяем, что URL НЕ изменился (остались на /login)
    expect(page.url()).toMatch(/\/login/);

    // Проверяем красный алерт с правильным текстом
    const alert = page.locator('[role="alert"], [class*="alert" i], [class*="error" i], [class*="Error" i]').first();
    await expect(alert).toBeVisible({ timeout: 5000 });

    const alertText = await alert.textContent();
    expect(alertText?.toLowerCase()).toMatch(/неверн|incorrect|invalid/);

    // Поля ввода должны остаться заполненными (email)
    const emailValue = await emailInput.inputValue();
    expect(emailValue).toBe(STUDENT_EMAIL);
  });

  test('1.1-005: Несуществующий email → тот же алерт (защита от перебора)', async ({ page }) => {
    const emailInput = page.locator('input[type="email"], input[name="email"]').first();
    const passwordInput = page.locator('input[type="password"]').first();
    const loginButton = page.getByRole('button', { name: /войти/i });

    await emailInput.fill('nonexistent_user@luberteh.ru');
    await passwordInput.fill('AnyPassword123!');

    const responsePromise = page.waitForResponse(
      (res) => res.url().includes('/api/token/') && res.status() === 401
    );

    await loginButton.click();
    const response = await responsePromise;
    expect(response.status()).toBe(401);

    // URL остаётся /login
    expect(page.url()).toMatch(/\/login/);

    // КРИТИЧНО: сообщение должно быть ОДИНАКОВЫМ с 1.1-004 (защита от перебора)
    const alert = page.locator('[role="alert"], [class*="alert" i], [class*="error" i], [class*="Error" i]').first();
    await expect(alert).toBeVisible({ timeout: 5000 });

    const alertText = await alert.textContent();
    expect(alertText?.toLowerCase()).toMatch(/неверн|incorrect|invalid/);

    // НЕ должно быть специфичного сообщения "такого пользователя не существует"
    expect(alertText?.toLowerCase()).not.toMatch(/не существует|does not exist|user not found/);
  });

  test('1.1-004/005: Сообщения для неверного пароля и несуществующего email идентичны', async ({ page }) => {
    // Получаем сообщение для неверного пароля
    await page.goto('/login');
    let emailInput = page.locator('input[type="email"]').first();
    let passwordInput = page.locator('input[type="password"]').first();
    let loginButton = page.getByRole('button', { name: /войти/i });

    await emailInput.fill(STUDENT_EMAIL);
    await passwordInput.fill('WrongPassword123!');
    await loginButton.click();

    await page.waitForTimeout(1000);
    let alert = page.locator('[role="alert"], [class*="alert" i], [class*="error" i]').first();
    await expect(alert).toBeVisible({ timeout: 5000 });
    const messageWrongPassword = (await alert.textContent())?.trim() || '';

    // Получаем сообщение для несуществующего email
    await page.context().clearCookies();
    await page.goto('/login');
    emailInput = page.locator('input[type="email"]').first();
    passwordInput = page.locator('input[type="password"]').first();
    loginButton = page.getByRole('button', { name: /войти/i });

    await emailInput.fill('nonexistent_user@luberteh.ru');
    await passwordInput.fill('AnyPassword123!');
    await loginButton.click();

    await page.waitForTimeout(1000);
    alert = page.locator('[role="alert"], [class*="alert" i], [class*="error" i]').first();
    await expect(alert).toBeVisible({ timeout: 5000 });
    const messageNonexistentEmail = (await alert.textContent())?.trim() || '';

    // Сообщения ДОЛЖНЫ быть идентичны (защита от перебора пользователей)
    expect(messageWrongPassword).toBe(messageNonexistentEmail);
    expect(messageWrongPassword.length).toBeGreaterThan(0);
  });

  test('1.1-010: Заблокированный пользователь → спец. сообщение', async ({ page }) => {
    // Сначала проверяем, есть ли заблокированный пользователь в БД
    // Создаём через API, если его нет (в тестах backend есть blocked_user)
    const emailInput = page.locator('input[type="email"], input[name="email"]').first();
    const passwordInput = page.locator('input[type="password"]').first();
    const loginButton = page.getByRole('button', { name: /войти/i });

    // Пробуем войти как заблокированный пользователь (существующий в фикстурах)
    await emailInput.fill('blocked_user@luberteh.ru');
    await passwordInput.fill('Password123!');

    const responsePromise = page.waitForResponse(
      (res) => res.url().includes('/api/token/')
    );

    await loginButton.click();
    const response = await responsePromise;
    
    // Ожидаем 401 Unauthorized
    expect(response.status()).toBe(401);

    // Проверяем алерт
    const alert = page.locator('[role="alert"], [class*="alert" i], [class*="error" i]').first();
    await expect(alert).toBeVisible({ timeout: 5000 });

    const alertText = await alert.textContent();
    // Сообщение должно упоминать блокировку
    expect(alertText?.toLowerCase()).toMatch(/заблокир|blocked|обратитесь к администратору/);
  });

  test('1.1-010 (вариант): is_active=False пользователь через API', async ({ page, request }) => {
    // Создаём заблокированного пользователя через API если его нет
    const createUserResponse = await request.post('http://localhost:8000/api/admin/users/', {
      data: {
        email: 'blocked_e2e@luberteh.ru',
        password: 'Password123!',
        is_active: false,
        first_name: 'Blocked',
        last_name: 'User',
      },
      headers: {
        // В тестовом окружении можно использовать force_authenticate через отдельный endpoint
        // или создать пользователя через фикстуру
      },
    }).catch(() => null);

    // Если не удалось создать через API — пропускаем
    if (!createUserResponse || createUserResponse.status() >= 400) {
      test.skip(true, 'Не удалось создать заблокированного пользователя (нужна админская фикстура)');
      return;
    }

    const emailInput = page.locator('input[type="email"]').first();
    const passwordInput = page.locator('input[type="password"]').first();
    const loginButton = page.getByRole('button', { name: /войти/i });

    await emailInput.fill('blocked_e2e@luberteh.ru');
    await passwordInput.fill('Password123!');
    await loginButton.click();

    const response = await page.waitForResponse(
      (res) => res.url().includes('/api/token/')
    );
    expect(response.status()).toBe(401);
  });

  // БП 1.1-044: Пустое поле Email
  test('1.1-044: Пустое поле "Электронная почта" → сообщение + запрос не отправляется', async ({ page }) => {
    await page.goto('/login');
    
    const emailInput = page.locator('input[type="email"], input[name="email"]').first();
    const passwordInput = page.locator('input[type="password"]').first();
    const loginButton = page.getByRole('button', { name: /Войти/i });
    
    // Заполняем только пароль, email оставляем пустым
    await passwordInput.fill('student2026');
    
    // Мониторинг сетевых запросов к /api/token/
    let apiRequestSent = false;
    page.on('request', (req) => {
      if (req.url().includes('/api/token/')) {
        apiRequestSent = true;
      }
    });
    
    // Нажимаем "Войти"
    await loginButton.click();
    
    // Проверяем появление сообщения об ошибке
    await expect(page.getByText(/Введите email и пароль/i)).toBeVisible({ timeout: 5000 });
    
    // Ждём немного и проверяем, что запрос НЕ был отправлен
    await page.waitForTimeout(1000);
    expect(apiRequestSent).toBe(false);
    
    // URL остаётся /login
    expect(page.url()).toContain('/login');
  });

  // БП 1.1-045: Пустое поле Пароль
  test('1.1-045: Пустое поле "Пароль" → сообщение + запрос не отправляется', async ({ page }) => {
    await page.goto('/login');
    
    const emailInput = page.locator('input[type="email"], input[name="email"]').first();
    const passwordInput = page.locator('input[type="password"]').first();
    const loginButton = page.getByRole('button', { name: /Войти/i });
    
    // Заполняем только email, пароль оставляем пустым
    await emailInput.fill('arhipov_kyu@luberteh.ru');
    
    // Мониторинг сетевых запросов к /api/token/
    let apiRequestSent = false;
    page.on('request', (req) => {
      if (req.url().includes('/api/token/')) {
        apiRequestSent = true;
      }
    });
    
    // Нажимаем "Войти"
    await loginButton.click();
    
    // Проверяем появление сообщения об ошибке
    await expect(page.getByText(/Введите email и пароль/i)).toBeVisible({ timeout: 5000 });
    
    // Ждём немного и проверяем, что запрос НЕ был отправлен
    await page.waitForTimeout(1000);
    expect(apiRequestSent).toBe(false);
    
    // URL остаётся /login
    expect(page.url()).toContain('/login');
  });

});
