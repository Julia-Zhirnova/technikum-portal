import { test, expect } from '@playwright/test';

test.describe('Блок 1.4.10-1.4.12, 1.5 и 1.6: Сайдбар, Подвал и Безопасность', () => {
  
  test('1.4.10, 1.4.11, 1.4.12: Скролл, мобильное меню и отступы сайдбара', async ({ page }) => {
    await page.goto('http://localhost:5173/login');
    await page.locator('input[type="email"]').fill('arhipov_kyu@luberteh.ru');
    await page.locator('input[type="password"]').fill('student2026');
    await page.locator('button:has-text("Войти")').click();
    await page.waitForURL('**/student**');

    const sidebarStyle = await page.locator('[data-testid="sidebar-content"]').first().evaluate((el) => window.getComputedStyle(el).overflowX);
    expect(sidebarStyle).toBe('hidden');

    const paddingTop = await page.locator('[data-testid="sidebar-content"]').first().evaluate((el) => window.getComputedStyle(el).paddingTop);
    expect(parseInt(paddingTop)).toBeGreaterThan(0);

    // 1.4.11: Теперь бургер в AppBar, он будет виден при изменении размера окна
    await page.setViewportSize({ width: 767, height: 720 });
    await expect(page.locator('[data-testid="burger-menu-button"]').first()).toBeVisible();
    
    await page.setViewportSize({ width: 1280, height: 720 });
  });

  test('1.5.1 - 1.5.4: Подвал (Footer)', async ({ page }) => {
    await page.goto('http://localhost:5173/login');
    await page.locator('input[type="email"]').fill('arhipov_kyu@luberteh.ru');
    await page.locator('input[type="password"]').fill('student2026');
    await page.locator('button:has-text("Войти")').click();
    await page.waitForURL('**/student**');

    await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight));

    await expect(page.locator('text=© 2026 ТехноПортал. ГБПОУ МО «Люберецкий техникум им. Ю.А. Гагарина»')).toBeVisible();

    const siteLink = page.locator('a[href="https://luberteh.ru/"]');
    await expect(siteLink).toBeVisible();
    await expect(siteLink).toContainText('Перейти на сайт');

    const mapLink = page.locator('a[href*="yandex.ru/maps"]');
    await expect(mapLink).toBeVisible();
    await expect(mapLink).toContainText('Посмотреть на карте');

    await expect(page.locator('text=Корпуса: Люберецкий').first()).toBeVisible();
    await expect(page.locator('text=Гагаринский').first()).toBeVisible();
    await expect(page.locator('text=Красково').first()).toBeVisible();
    await expect(page.locator('text=Угреша').first()).toBeVisible();
  });

  test('1.6.1: Студент не видит кнопки переключения ролей', async ({ page }) => {
    await page.goto('http://localhost:5173/login');
    await page.locator('input[type="email"]').fill('arhipov_kyu@luberteh.ru');
    await page.locator('input[type="password"]').fill('student2026');
    await page.locator('button:has-text("Войти")').click();
    await page.waitForURL('**/student**');

    await expect(page.locator('[data-testid="role-switcher-button"]')).toHaveCount(0);
  });

  test('1.6.2: Студент не может сменить роль через localStorage', async ({ page }) => {
    await page.goto('http://localhost:5173/login');
    await page.locator('input[type="email"]').fill('arhipov_kyu@luberteh.ru');
    await page.locator('input[type="password"]').fill('student2026');
    await page.locator('button:has-text("Войти")').click();
    await page.waitForURL('**/student**');

    // Подменяем роль на заведомо несуществующую роль
    await page.evaluate(() => {
      localStorage.setItem('activeRole', 'super_fake_role_xyz');
    });

    // 1. Ожидаем ответ от API профиля после перезагрузки, чтобы убедиться, что useEffect отработал
    const profileResponsePromise = page.waitForResponse('**/api/user/profile/**');
    
    // 2. Перезагружаем страницу
    await page.reload();
    
    // 3. Ждем завершения запроса профиля
    await profileResponsePromise;
    
    // 4. Ждем финального URL
    await page.waitForURL('**/student**');
    expect(page.url()).toContain('/student');
    
    // 5. Даем небольшую задержку, чтобы React успел выполнить setState и записать в localStorage
    await page.waitForTimeout(500);

    // 6. Проверяем, что роль в localStorage была сброшена обратно на student
    const activeRole = await page.evaluate(() => localStorage.getItem('activeRole'));
    expect(activeRole).toBe('student');
  });
});
