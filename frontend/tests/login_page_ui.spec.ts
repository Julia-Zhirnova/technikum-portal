import { test, expect } from '@playwright/test';

/**
 * БП 1.1-001: UI страницы /login
 * 
 * Спецификация:
 * - Страница загружается
 * - Видна карточка с логотипом
 * - Заголовок "ТехноПортал" + полное название техникума в 4 строки
 * - Поля Email/Пароль
 * - Кнопка "Войти"
 * - Текст "Забыли пароль? Обратитесь к куратору или администратору учебного заведения"
 */

test.describe('БП 1.1-001: UI страницы /login', () => {
  test.beforeEach(async ({ page }) => {
    // Открываем страницу логина
    await page.goto('/login');
  });

  test('страница /login загружается', async ({ page }) => {
    // Проверяем, что страница загрузилась
    await expect(page).toHaveURL(/.*login/);
    await expect(page).toHaveTitle(/.*/); // Любой заголовок
  });

  test('видна карточка входа', async ({ page }) => {
    // Ищем карточку (обычно это container/card/div с определенными классами)
    // MUI Card или кастомный контейнер
    const card = page.locator('[class*="card"], [class*="Card"], [class*="container"], [class*="Container"]').first();
    await expect(card).toBeVisible();
  });

  test('виден заголовок "ТехноПортал"', async ({ page }) => {
    // БП 1.1-001: ищем именно <h2> заголовок (а не подзаголовок <p>)
    await expect(page.getByRole('heading', { name: 'ТехноПортал' })).toBeVisible();
  });

  test('видно полное название техникума', async ({ page }) => {
    // Ищем часть названия техникума (ГБПОУ МО Люберецкий техникум)
    await expect(page.getByText(/ГБПОУ|Люберецкий|техникум/i).first()).toBeVisible();
  });

  test('видно поле Email', async ({ page }) => {
    // Ищем поле email (input type="email" или input с placeholder "Email")
    const emailInput = page.locator('input[type="email"], input[placeholder*="mail" i], input[name="email"]').first();
    await expect(emailInput).toBeVisible();
    await expect(emailInput).toBeEnabled();
  });

  test('видно поле Пароль', async ({ page }) => {
    // Ищем поле password
    const passwordInput = page.locator('input[type="password"], input[placeholder*="пароль" i], input[name="password"]').first();
    await expect(passwordInput).toBeVisible();
    await expect(passwordInput).toBeEnabled();
  });

  test('видна кнопка "Войти"', async ({ page }) => {
    // Ищем кнопку с текстом "Войти"
    const loginButton = page.getByRole('button', { name: /войти/i });
    await expect(loginButton).toBeVisible();
    await expect(loginButton).toBeEnabled();
  });

  test('виден текст о забытом пароле', async ({ page }) => {
    // Ищем текст "Забыли пароль" или "Обратитесь к куратору"
    const forgotPasswordText = page.getByText(/забыли пароль|обратитесь к куратору/i);
    await expect(forgotPasswordText.first()).toBeVisible();
  });


});
