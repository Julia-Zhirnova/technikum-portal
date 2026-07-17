import { test, expect } from '@playwright/test';

test.describe('Функция 1.2: Принудительная смена пароля', () => {
  
  test('1. Редирект на /change-password при requires_password_change=True', async ({ page }) => {
    await page.route('**/api/token/', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ access: 'mock', refresh: 'mock', requires_password_change: true, roles: ['student'] })
      });
    });

    await page.goto('http://localhost:5173/login');
    await page.fill('input[type="email"]', 'test@test.ru');
    await page.fill('input[type="password"]', 'OldPass123!');
    await page.click('button[type="submit"]');

    await expect(page).toHaveURL(/.*\/change-password/);
    await expect(page.locator('text=Смена пароля')).toBeVisible();
  });

  test('2. Успешная смена пароля и редирект на дашборд роли', async ({ page }) => {
    await page.route('**/api/token/', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ access: 'mock', refresh: 'mock', requires_password_change: true, roles: ['student'] })
      });
    });

    await page.route('**/api/auth/force-change-password/', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ detail: 'Пароль успешно изменен.' })
      });
    });

    await page.route('**/api/user/profile/', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ roles: ['student'], requires_password_change: false })
      });
    });

    await page.goto('http://localhost:5173/login');
    await page.fill('input[type="email"]', 'test@test.ru');
    await page.fill('input[type="password"]', 'OldPass123!');
    await page.click('button[type="submit"]');

    await expect(page).toHaveURL(/.*\/change-password/);
    
    await page.locator('input[type="password"]').first().fill('NewSuperPass123!');
    await page.locator('input[type="password"]').nth(1).fill('NewSuperPass123!');
    await page.locator('button:has-text("Сменить пароль")').click();

    await expect(page.locator('text=Пароль успешно изменен!')).toBeVisible();
    // SmartRedirect перенаправит на /student
    await expect(page).toHaveURL(/.*\/student/, { timeout: 5000 });
  });

  test('3. Валидация слабого пароля', async ({ page }) => {
    await page.goto('http://localhost:5173/change-password');
    await page.locator('input[type="password"]').first().fill('12345678');
    await page.locator('input[type="password"]').nth(1).fill('12345678');
    await page.locator('button:has-text("Сменить пароль")').click();
    
    // Ожидаем ошибку от бэкенда о недостаточной сложности
    await expect(page.locator('text=Пароль должен содержать')).toBeVisible();
  });

  test('4. Запрет на использование текущего пароля', async ({ page }) => {
    await page.route('**/api/auth/force-change-password/', async route => {
      await route.fulfill({
        status: 400,
        contentType: 'application/json',
        body: JSON.stringify({ new_password: ['Новый пароль не должен совпадать с текущим.'] })
      });
    });
    
    await page.goto('http://localhost:5173/change-password');
    await page.locator('input[type="password"]').first().fill('OldPass123!');
    await page.locator('input[type="password"]').nth(1).fill('OldPass123!');
    await page.locator('button:has-text("Сменить пароль")').click();

    await expect(page.locator('text=Новый пароль не должен совпадать с текущим')).toBeVisible();
  });
});
