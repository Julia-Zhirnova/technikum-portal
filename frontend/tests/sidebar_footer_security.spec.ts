import { test, expect } from '@playwright/test';

test.describe('Блок 1.4.10-1.4.12, 1.5 и 1.6: Сайдбар, Подвал и Безопасность', () => {
  
  test('1.4.10, 1.4.11, 1.4.12: Скролл, мобильное меню и отступы сайдбара', async ({ page }) => {
    await page.goto('http://localhost:5173/login');
    await page.locator('input[type="email"]').fill('arhipov_kyu@luberteh.ru');
    await page.locator('input[type="password"]').fill('student2026');
    await page.locator('button:has-text("Войти")').click();
    await page.waitForURL('**/student**');

    // 1.4.10: Нет горизонтального скролла
    const sidebarStyle = await page.locator('[data-testid="sidebar-content"]').first().evaluate((el) => window.getComputedStyle(el).overflowX);
    expect(sidebarStyle).toBe('hidden');

    // 1.4.12: Первый элемент виден (padding-top > 0)
    const paddingTop = await page.locator('[data-testid="sidebar-content"]').first().evaluate((el) => window.getComputedStyle(el).paddingTop);
    expect(parseInt(paddingTop)).toBeGreaterThan(0);

    // 1.4.11: Мобильная версия (Бургер-меню при ширине < 768px). Используем 767px.
    await page.setViewportSize({ width: 767, height: 720 });
    await expect(page.locator('[data-testid="burger-menu-button"]').first()).toBeVisible();
    
    // Возвращаем десктопный размер
    await page.setViewportSize({ width: 1280, height: 720 });
  });

  test('1.5.1 - 1.5.4: Подвал (Footer)', async ({ page }) => {
    await page.goto('http://localhost:5173/login');
    await page.locator('input[type="email"]').fill('arhipov_kyu@luberteh.ru');
    await page.locator('input[type="password"]').fill('student2026');
    await page.locator('button:has-text("Войти")').click();
    await page.waitForURL('**/student**');

    // Прокручиваем вниз
    await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight));

    // 1.5.1: Текст копирайта
    await expect(page.locator('text=© 2026 ТехноПортал. ГБПОУ МО «Люберецкий техникум им. Ю.А. Гагарина»')).toBeVisible();

    // 1.5.2: Ссылка на сайт
    const siteLink = page.locator('a[href="https://luberteh.ru/"]');
    await expect(siteLink).toBeVisible();
    await expect(siteLink).toContainText('Перейти на сайт');

    // 1.5.3: Ссылка на карту
    const mapLink = page.locator('a[href*="yandex.ru/maps"]');
    await expect(mapLink).toBeVisible();
    await expect(mapLink).toContainText('Посмотреть на карте');

    // 1.5.4: Корпуса в строчку
    await expect(page.locator('text=Люберецкий').first()).toBeVisible();
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

    // У студента только 1 роль, переключателя быть не должно
    await expect(page.locator('[data-testid="role-switcher-button"]')).toHaveCount(0);
  });

  test('1.6.2: Студент не может сменить роль через localStorage', async ({ page }) => {
    await page.goto('http://localhost:5173/login');
    await page.locator('input[type="email"]').fill('arhipov_kyu@luberteh.ru');
    await page.locator('input[type="password"]').fill('student2026');
    await page.locator('button:has-text("Войти")').click();
    await page.waitForURL('**/student**');

    // Подменяем роль на заведомо несуществующую
    await page.evaluate(() => {
      localStorage.setItem('activeRole', 'super_fake_role_xyz');
    });

    // Перезагружаем страницу
    await page.reload();
    
    // Ожидаем, что система обнаружит подмену и вернет на дефолтный маршрут студента
    await page.waitForURL('**/student**');
    expect(page.url()).toContain('/student');
    
    // Даем небольшую задержку, чтобы React гарантированно завершил useEffect и запись в localStorage
    await page.waitForTimeout(500);

    const activeRole = await page.evaluate(() => localStorage.getItem('activeRole'));
    expect(activeRole).toBe('student');
  });
});
