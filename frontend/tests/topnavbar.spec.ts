import { test, expect } from '@playwright/test';

test.describe('Блок 1.3: Шапка (TopNavbar)', () => {
  
  test('1.3.1 - 1.3.6: UI элементы шапки для студента', async ({ page }) => {
    await page.setViewportSize({ width: 1280, height: 720 });
    
    await page.goto('http://localhost:5173/login');
    await page.locator('input[type="email"]').fill('arhipov_kyu@luberteh.ru');
    await page.locator('input[type="password"]').fill('student2026');
    await page.locator('button:has-text("Войти")').click();
    await page.waitForURL('**/student**');

    // 1.3.1: Логотип слева
    await expect(page.locator('img[alt="Логотип"]')).toBeVisible();
    
    // 1.3.2: «ТехноПортал» рядом с логотипом
    await expect(page.locator('text=ТехноПортал').first()).toBeVisible();
    
    // 1.3.3: ФИО полностью справа
    await expect(page.locator('text=Архипов Кирилл Юрьевич')).toBeVisible();
    
    // 1.3.4: Активная роль выделена (теперь она видна даже при 1 роли)
    await expect(page.locator('text=Студент').first()).toBeVisible();
    
    // 1.3.5: Выпадающий список ролей ОТСУТСТВУЕТ (у студента 1 роль)
    await expect(page.locator('button#role-switcher-button')).toHaveCount(0);
    
    // 1.3.6: Колокольчик уведомлений
    await expect(page.locator('[data-testid="NotificationsIcon"]').first()).toBeVisible();
  });

  test('1.3.8 - 1.3.10: Переключение ролей, сохранение контекста и выход', async ({ page }) => {
    await page.setViewportSize({ width: 1280, height: 720 });
    
    await page.goto('http://localhost:5173/login');
    await page.locator('input[type="email"]').fill('multirole@luberteh.ru');
    await page.locator('input[type="password"]').fill('student2026');
    await page.locator('button:has-text("Войти")').click();
    
    await page.waitForURL('**/teacher**');
    await page.waitForTimeout(1000);

    // 1.3.5 (для мульти-роли): Кнопка переключателя ролей ДОЛЖНА быть видна
    const roleSwitcher = page.getByTestId('role-switcher-button');
    await expect(roleSwitcher).toBeVisible({ timeout: 10000 });
    
    // Открываем меню
    await roleSwitcher.click();
    
    // 1.3.8: Используем getByRole для точного поиска пункта меню (избегаем strict mode violation)
    await expect(page.getByRole('menuitem', { name: 'Преподаватель' })).toBeVisible();
    await expect(page.getByRole('menuitem', { name: 'Куратор' })).toBeVisible();

    // Переключаем роль на Куратора
    await page.getByRole('menuitem', { name: 'Куратор' }).click();
    await page.waitForURL('**/curator**');
    expect(page.url()).toContain('/curator');
    
    const activeRole = await page.evaluate(() => localStorage.getItem('activeRole'));
    expect(activeRole).toBe('curator');

    // 1.3.9: Сохранение контекста (F5)
    await page.reload();
    await page.waitForURL('**/curator**');
    expect(page.url()).toContain('/curator');
    
    const roleAfterReload = await page.evaluate(() => localStorage.getItem('activeRole'));
    expect(roleAfterReload).toBe('curator');

    // 1.3.10: Выход
    await page.locator('button[title="Выйти из системы"]').click();
    await page.waitForURL('**/login**');
    expect(page.url()).toContain('/login');
    
    const tokenAfterLogout = await page.evaluate(() => localStorage.getItem('access_token'));
    expect(tokenAfterLogout).toBeNull();
  });
});
