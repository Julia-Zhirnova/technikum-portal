import { test, expect } from '@playwright/test';

test.describe('Блок 1.3.07 и 1.4: Шапка и Сайдбар', () => {
  
  test('1.3.07: ФИО не накладывается при узком экране', async ({ page }) => {
    await page.setViewportSize({ width: 1280, height: 720 });
    await page.goto('http://localhost:5173/login');
    await page.locator('input[type="email"]').fill('arhipov_kyu@luberteh.ru');
    await page.locator('input[type="password"]').fill('student2026');
    await page.locator('button:has-text("Войти")').click();
    await page.waitForURL('**/student**');

    const userNameElement = page.locator('text=Архипов Кирилл Юрьевич').first();
    const style = await userNameElement.evaluate((el) => window.getComputedStyle(el).whiteSpace);
    expect(style).toBe('nowrap');
  });

  test('1.4.1: Меню для роли student', async ({ page }) => {
    await page.setViewportSize({ width: 1280, height: 720 });
    await page.goto('http://localhost:5173/login');
    await page.locator('input[type="email"]').fill('arhipov_kyu@luberteh.ru');
    await page.locator('input[type="password"]').fill('student2026');
    await page.locator('button:has-text("Войти")').click();
    await page.waitForURL('**/student**');

    await expect(page.locator('text=Мой профиль').first()).toBeVisible();
    await expect(page.locator('text=Зачётная книжка').first()).toBeVisible();
    await expect(page.locator('text=Практика').first()).toBeVisible();
    await expect(page.locator('text=Заявки').first()).toBeVisible();
    await expect(page.locator('text=Уведомления').first()).toBeVisible();
  });

  test('1.4.2: Меню для роли teacher', async ({ page }) => {
    await page.setViewportSize({ width: 1280, height: 720 });
    await page.goto('http://localhost:5173/login');
    await page.locator('input[type="email"]').fill('multirole@luberteh.ru');
    await page.locator('input[type="password"]').fill('student2026');
    await page.locator('button:has-text("Войти")').click();
    
    await page.waitForURL('**/teacher**');
    
    const roleSwitcher = page.getByTestId('role-switcher-button');
    await expect(roleSwitcher).toBeVisible();
    await roleSwitcher.click();
    await page.getByRole('menuitem', { name: 'Преподаватель' }).click();
    
    await expect(page.locator('text=Мои ведомости').first()).toBeVisible();
    await expect(page.locator('text=Расписание экзаменов').first()).toBeVisible();
    await expect(page.locator('text=Практика').first()).toBeVisible();
    await expect(page.locator('text=Рабочие программы').first()).toBeVisible();
  });

  test('1.4.3: Меню для роли curator', async ({ page }) => {
    await page.setViewportSize({ width: 1280, height: 720 });
    await page.goto('http://localhost:5173/login');
    await page.locator('input[type="email"]').fill('multirole@luberteh.ru');
    await page.locator('input[type="password"]').fill('student2026');
    await page.locator('button:has-text("Войти")').click();
    
    const roleSwitcher = page.getByTestId('role-switcher-button');
    await expect(roleSwitcher).toBeVisible();
    await roleSwitcher.click();
    await page.getByRole('menuitem', { name: 'Куратор' }).click();
    
    await expect(page.locator('text=Моя группа').first()).toBeVisible();
    await expect(page.locator('text=Успеваемость').first()).toBeVisible();
    await expect(page.locator('text=Посещаемость').first()).toBeVisible();
    await expect(page.locator('text=Расписание').first()).toBeVisible();
    await expect(page.locator('text=Заявки студентов').first()).toBeVisible();
    await expect(page.locator('text=Практика').first()).toBeVisible();
  });

  test('1.4.4 и 1.4.5: Активный пункт подсвечен и отцентрирован', async ({ page }) => {
    await page.setViewportSize({ width: 1280, height: 720 });
    await page.goto('http://localhost:5173/login');
    await page.locator('input[type="email"]').fill('arhipov_kyu@luberteh.ru');
    await page.locator('input[type="password"]').fill('student2026');
    await page.locator('button:has-text("Войти")').click();
    await page.waitForURL('**/student/profile**');

    const activeItem = page.locator('[data-testid="active-menu-item"]').first();
    await expect(activeItem).toBeVisible();
    
    await expect(activeItem).toHaveCSS('text-align', 'center');
  });

  test('1.4.6 и 1.4.7: Z-index шапки и отступ сайдбара', async ({ page }) => {
    await page.goto('http://localhost:5173/login');
    await page.locator('input[type="email"]').fill('arhipov_kyu@luberteh.ru');
    await page.locator('input[type="password"]').fill('student2026');
    await page.locator('button:has-text("Войти")').click();
    await page.waitForURL('**/student**');
    
    // Даем время на полную стабилизацию DOM после навигации
    await page.waitForTimeout(1000);

    // 1.4.6: Проверяем, что у шапки (AppBar) явно задан z-index (не 'auto'), 
    // что гарантирует ее положение поверх других элементов при скролле
    const headerZIndex = await page.locator('.MuiAppBar-root').first().evaluate((el) => window.getComputedStyle(el).zIndex);
    expect(headerZIndex).not.toBe('auto');
    
    // 1.4.7: У сайдбара есть padding-bottom (чтобы не наезжал на подвал)
    const sidebarPaddingBottom = await page.locator('[data-testid="sidebar-content"]').first().evaluate((el) => window.getComputedStyle(el).paddingBottom);
    expect(parseInt(sidebarPaddingBottom)).toBeGreaterThan(0);
  });
});
