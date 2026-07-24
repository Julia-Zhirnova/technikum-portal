import { test, expect } from '@playwright/test';

test.describe('Блок 1.2: Принудительная смена пароля', () => {
  test('1.2.1: Страница смены пароля доступна и корректна', async ({ page }) => {
    await page.goto('http://localhost:5173/change-password');
    
    await expect(page.getByRole('heading', { name: 'Смена пароля' })).toBeVisible();
    
    // Используем nth() для избежания strict mode violation в MUI
    const passwordInputs = page.locator('input[type="password"]');
    await expect(passwordInputs.nth(0)).toBeVisible(); // Новый пароль
    await expect(passwordInputs.nth(1)).toBeVisible(); // Подтвердите новый пароль
    
    // 1.2.2: Проверяем отсутствие текста "Текущий пароль" на странице
    await expect(page.locator('text=Текущий пароль')).toHaveCount(0);
  });

  test('1.2.2 и 1.2.3: UI страницы смены пароля и индикатор сложности', async ({ page }) => {
    await page.goto('http://localhost:5173/change-password');
    
    const passwordInputs = page.locator('input[type="password"]');
    
    // Вводим очень слабый пароль (длина < 8, нет заглавных, цифр и спецсимволов)
    await passwordInputs.nth(0).fill('weak');
    
    // 1.2.3: Проверяем появление индикатора сложности по data-testid
    const indicator = page.locator('[data-testid="password-strength-indicator"]');
    await expect(indicator).toBeVisible();
    await expect(indicator).toContainText('Очень слабый');
    
    // Вводим сильный пароль
    await passwordInputs.nth(0).fill('StrongPass123!');
    await expect(indicator).toContainText('Отличный');
  });
});
