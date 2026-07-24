import { test, expect } from '@playwright/test';

test.describe('Блок 1.1: Страница входа (/login)', () => {
  
  test.beforeEach(async ({ page }) => {
    // Переходим на страницу входа перед каждым тестом
    await page.goto('http://localhost:5173/login');
  });

  test('1.1.1 - 1.1.6, 1.1.8 - 1.1.10: Проверка UI элементов страницы входа', async ({ page }) => {
    // 1.1.1: Логотип (проверяем наличие хотя бы одного img или svg)
    await expect(page.locator('img, svg').first()).toBeVisible();

    // 1.1.2: Название техникума в 4 строки
    await expect(page.locator('text=ГБПОУ МО')).toBeVisible();
    await expect(page.locator('text=Люберецкий техникум')).toBeVisible();
    await expect(page.locator('text=имени Героя Советского Союза')).toBeVisible();
    await expect(page.locator('text=лётчика-космонавта Ю. А. Гагарина')).toBeVisible();

    // 1.1.3: Название "ТехноПортал"
    await expect(page.locator('h2.MuiTypography-h2:has-text("ТехноПортал")')).toBeVisible();

    // 1.1.4: Описание
    await expect(page.locator('text=цифровой фундамент техникума')).toBeVisible();

    // 1.1.5: Системная информация в подвале
    await expect(page.locator('text=2.4.1')).toBeVisible();
    await expect(page.locator('text=2025–2026')).toBeVisible();
    await expect(page.locator('text=I (осенний)')).toBeVisible();

    // 1.1.6: Карточки ролей (ищем именно в заголовках h6, чтобы избежать совпадений с текстом в подвале)
    await expect(page.locator('h6:has-text("Студент")')).toBeVisible();
    await expect(page.locator('h6:has-text("Преподаватель")')).toBeVisible();
    await expect(page.locator('h6:has-text("Куратор")')).toBeVisible();
    await expect(page.locator('h6:has-text("Администратор")')).toBeVisible();

    // 1.1.8: Поле Пароль скрыто
    const passwordInput = page.locator('input[type="password"]');
    await expect(passwordInput).toBeVisible();

    // 1.1.9: Кнопка "Войти" существует
    await expect(page.locator('button:has-text("Войти")')).toBeVisible();

    // 1.1.10: Текст про забытый пароль
    await expect(page.locator('text=Забыли пароль? Обратитесь к администратору учебного заведения')).toBeVisible();
  });

  test('1.1.7, 1.1.11: Валидация пустых полей и формата Email (проверка поведения)', async ({ page }) => {
    const emailInput = page.locator('input[type="email"]');
    const passwordInput = page.locator('input[type="password"]');
    const submitButton = page.locator('button:has-text("Войти")');

    // 1.1.11: Пустые поля
    await submitButton.click();
    
    // Проверяем поведение: редиректа не произошло, мы остались на /login
    expect(page.url()).toContain('/login');
    // Поля ввода все еще присутствуют на странице (форма не отправилась)
    await expect(emailInput).toBeVisible();
    await expect(passwordInput).toBeVisible();

    // 1.1.7: Валидация формата email (ввод без @)
    await emailInput.fill('invalidemail.com');
    await passwordInput.fill('student2026');
    await submitButton.click();
    
    // Проверяем поведение: редиректа не произошло
    expect(page.url()).toContain('/login');
    
    // Проверяем, что невалидное значение осталось в поле (форма не сбросила его и не отправилась)
    const emailValue = await emailInput.inputValue();
    expect(emailValue).toBe('invalidemail.com');
  });

  test('1.1.14: Успешный вход студента', async ({ page }) => {
    await page.locator('input[type="email"]').fill('arhipov_kyu@luberteh.ru');
    await page.locator('input[type="password"]').fill('student2026');
    await page.locator('button:has-text("Войти")').click();

    await page.waitForURL('**/student**');
    expect(page.url()).toContain('/student');
    
    const token = await page.evaluate(() => localStorage.getItem('access_token'));
    expect(token).toBeTruthy();
  });

  test('1.1.15: Успешный вход преподавателя (приоритет teacher)', async ({ page }) => {
    await page.locator('input[type="email"]').fill('YVZhirnova@yandex.ru');
    await page.locator('input[type="password"]').fill('student2026');
    await page.locator('button:has-text("Войти")').click();

    await page.waitForURL('**/teacher**');
    expect(page.url()).toContain('/teacher');
  });

  test('1.1.16: Успешный вход админа (приоритет admin)', async ({ page }) => {
    await page.locator('input[type="email"]').fill('ang-bl@rambler.ru');
    await page.locator('input[type="password"]').fill('student2026');
    await page.locator('button:has-text("Войти")').click();

    await page.waitForURL('**/admin**');
    expect(page.url()).toContain('/admin');
  });
});
