/**
 * БП 1.3: Партия 2 — E2E тесты переключения ролей (TC012-TC021, TC029)
 */
import { test, expect } from '@playwright/test';

test.describe('БП 1.3: Переключение ролей', () => {
  
  // TC012-TC017: Переключение между ролями
  test('TC012: Преподаватель → Куратор (URL меняется на /curator/group)', async ({ page }) => {
    await page.goto('/login');
    await page.fill('input[type="email"]', 'YVZhirnova@yandex.ru');
    await page.fill('input[type="password"]', 'student2026');
    await page.click('button:has-text("Войти")');
    await page.waitForURL('**/teacher/statements');
    
    // Открываем dropdown (кнопка с data-testid="role-switcher-button")
    await page.locator('[data-testid="role-switcher-button"]').click();
    
    // Выбираем "Куратор"
    await page.locator('li:has-text("Куратор")').click();
    
    await page.waitForURL('**/curator/group');
    expect(page.url()).toContain('/curator/group');
  });

  test('TC013: Куратор → Преподаватель (URL меняется на /teacher/statements)', async ({ page }) => {
    await page.goto('/login');
    await page.fill('input[type="email"]', 'YVZhirnova@yandex.ru');
    await page.fill('input[type="password"]', 'student2026');
    await page.click('button:has-text("Войти")');
    await page.waitForURL('**/teacher/statements');
    
    // Переключаем на куратора
    await page.locator('[data-testid="role-switcher-button"]').click();
    await page.locator('li:has-text("Куратор")').click();
    await page.waitForURL('**/curator/group');
    
    // Переключаем обратно на преподавателя
    await page.locator('[data-testid="role-switcher-button"]').click();
    await page.locator('li:has-text("Преподаватель")').click();
    await page.waitForURL('**/teacher/statements');
    
    expect(page.url()).toContain('/teacher/statements');
  });

  test('TC014: Админ → Преподаватель (URL меняется на /teacher/statements)', async ({ page }) => {
    await page.goto('/login');
    await page.fill('input[type="email"]', 'ang-bl@rambler.ru');
    await page.fill('input[type="password"]', 'student2026');
    await page.click('button:has-text("Войти")');
    await page.waitForURL('**/admin/users');
    
    await page.locator('[data-testid="role-switcher-button"]').click();
    await page.locator('li:has-text("Преподаватель")').click();
    await page.waitForURL('**/teacher/statements');
    
    expect(page.url()).toContain('/teacher/statements');
  });

  test('TC015: Админ → Куратор (URL меняется на /curator/group)', async ({ page }) => {
    await page.goto('/login');
    await page.fill('input[type="email"]', 'ang-bl@rambler.ru');
    await page.fill('input[type="password"]', 'student2026');
    await page.click('button:has-text("Войти")');
    await page.waitForURL('**/admin/users');
    
    await page.locator('[data-testid="role-switcher-button"]').click();
    await page.locator('li:has-text("Куратор")').click();
    await page.waitForURL('**/curator/group');
    
    expect(page.url()).toContain('/curator/group');
  });

  test('TC016: Председатель МЦК → Преподаватель (URL меняется на /teacher/statements)', async ({ page }) => {
    await page.goto('/login');
    await page.fill('input[type="email"]', 'tardv69@yandex.ru');
    await page.fill('input[type="password"]', 'student2026');
    await page.click('button:has-text("Войти")');
    await page.waitForURL('**/mck/rpd');
    
    await page.locator('[data-testid="role-switcher-button"]').click();
    await page.locator('li:has-text("Преподаватель")').click();
    await page.waitForURL('**/teacher/statements');
    
    expect(page.url()).toContain('/teacher/statements');
  });

  test('TC017: Преподаватель → Председатель МЦК (URL меняется на /mck/rpd)', async ({ page }) => {
    await page.goto('/login');
    await page.fill('input[type="email"]', 'tardv69@yandex.ru');
    await page.fill('input[type="password"]', 'student2026');
    await page.click('button:has-text("Войти")');
    await page.waitForURL('**/mck/rpd');
    
    await page.locator('[data-testid="role-switcher-button"]').click();
    await page.locator('li:has-text("Преподаватель")').click();
    await page.waitForURL('**/teacher/statements');
    
    await page.locator('[data-testid="role-switcher-button"]').click();
    await page.locator('li:has-text("МЦК")').click();
    await page.waitForURL('**/mck/rpd');
    
    expect(page.url()).toContain('/mck/rpd');
  });

  // TC018-TC019: Шапка (одна роль vs dropdown)
  test('TC018: Шапка для пользователя с одной ролью (студент) — нет dropdown', async ({ page }) => {
    await page.goto('/login');
    await page.fill('input[type="email"]', 'arhipov_kyu@luberteh.ru');
    await page.fill('input[type="password"]', 'student2026');
    await page.click('button:has-text("Войти")');
    await page.waitForURL('**/student/profile');
    
    // Для одной роли: нет role-switcher (div оборачивает только при >1 роли)
    const roleSwitcher = page.locator('[data-testid="role-switcher"]');
    await expect(roleSwitcher).toHaveCount(0);
    
    // Нет кнопки открытия dropdown
    const dropdownButton = page.locator('[data-testid="role-switcher-button"]');
    await expect(dropdownButton).toHaveCount(0);
    
    // Статический текст роли виден (через data-testid, чтобы избежать strict mode)
    await expect(page.locator('[data-testid="role-label"]')).toBeVisible();
  });

  test('TC019: Шапка для пользователя с несколькими ролями — есть dropdown', async ({ page }) => {
    await page.goto('/login');
    await page.fill('input[type="email"]', 'YVZhirnova@yandex.ru');
    await page.fill('input[type="password"]', 'student2026');
    await page.click('button:has-text("Войти")');
    await page.waitForURL('**/teacher/statements');
    
    // Проверяем: есть role-switcher
    const roleSwitcher = page.locator('[data-testid="role-switcher"]');
    await expect(roleSwitcher).toBeVisible();
    
    // Открываем dropdown
    await page.locator('[data-testid="role-switcher-button"]').click();
    
    // Проверяем: dropdown открыт (видны элементы меню)
    await expect(page.locator('li:has-text("Куратор")')).toBeVisible();
  });

  // TC020-TC021: Обновление sidebar
  test('TC020: Обновление sidebar после переключения на Куратор', async ({ page }) => {
    await page.goto('/login');
    await page.fill('input[type="email"]', 'YVZhirnova@yandex.ru');
    await page.fill('input[type="password"]', 'student2026');
    await page.click('button:has-text("Войти")');
    await page.waitForURL('**/teacher/statements');
    
    // Переключаем на куратора
    await page.locator('[data-testid="role-switcher-button"]').click();
    await page.locator('li:has-text("Куратор")').click();
    await page.waitForURL('**/curator/group');
    await page.waitForTimeout(1000); // ждём рендеринга sidebar
    
    // Проверяем sidebar: пункты куратора
    const sidebar = page.locator('[data-testid="sidebar"]').first();
    await expect(sidebar).toBeVisible();
    
    await expect(sidebar.getByText('Моя группа')).toBeVisible();
    await expect(sidebar.getByText('Успеваемость')).toBeVisible();
    await expect(sidebar.getByText('Заявки студентов')).toBeVisible();
  });

  test('TC021: Обновление sidebar после переключения на Преподаватель', async ({ page }) => {
    await page.goto('/login');
    await page.fill('input[type="email"]', 'YVZhirnova@yandex.ru');
    await page.fill('input[type="password"]', 'student2026');
    await page.click('button:has-text("Войти")');
    await page.waitForURL('**/teacher/statements');
    
    // Явно переключаем на преподавателя (спецификация: "после ПЕРЕКЛЮЧЕНИЯ на роль преподавателя")
    // Это гарантирует, что activeRole в state станет 'teacher'
    await page.locator('[data-testid="role-switcher-button"]').click();
    await page.locator('li:has-text("Преподаватель")').click();
    await page.waitForURL('**/teacher/statements');
    await page.waitForTimeout(500);
    
    // Проверяем sidebar: пункты преподавателя
    const sidebar = page.locator('[data-testid="sidebar"]').first();
    await expect(sidebar).toBeVisible();
    
    await expect(sidebar.getByText('Мои ведомости')).toBeVisible();
    await expect(sidebar.getByText('Расписание экзаменов')).toBeVisible();
  });

  // TC029: Dropdown содержит только роли пользователя
  test('TC029: Dropdown содержит только роли пользователя (teacher + curator)', async ({ page }) => {
    await page.goto('/login');
    await page.fill('input[type="email"]', 'YVZhirnova@yandex.ru');
    await page.fill('input[type="password"]', 'student2026');
    await page.click('button:has-text("Войти")');
    await page.waitForURL('**/teacher/statements');
    
    // Открываем dropdown
    await page.locator('[data-testid="role-switcher-button"]').click();
    
    // Проверяем: только "Преподаватель" и "Куратор"
    await expect(page.locator('li:has-text("Преподаватель")')).toBeVisible();
    await expect(page.locator('li:has-text("Куратор")')).toBeVisible();
    
    // НЕ должно быть "Администратор", "Студент", "МЦК"
    await expect(page.locator('li:has-text("Администратор")')).not.toBeVisible();
    await expect(page.locator('li:has-text("Студент")')).not.toBeVisible();
    await expect(page.locator('li:has-text("МЦК")')).not.toBeVisible();
  });
});
