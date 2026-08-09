import { test, expect } from '@playwright/test';

/**
 * БП 1.1-007/008/009/022/023/024: Маршрутизация и переключение ролей
 *
 * Спецификация:
 * 1.1-007 🔴: Куратор+Преподаватель → редирект на /teacher/statements,
 *            видны кнопки переключения между "Преподаватель" и "Куратор"
 * 1.1-008 🔴: Администратор → редирект на /admin/users,
 *            видны кнопки переключения всех доступных ролей
 * 1.1-009 🔴: Председатель МЦК → редирект на /mck/rpd,
 *            видны кнопки переключения между "Преподаватель" и "Председатель МЦК"
 * 1.1-022 🟡: Переключение роли: URL меняется на соответствующий
 * 1.1-023 🟡: F5 сохраняет контекст выбранной роли
 * 1.1-024 🟡: Защита фронтенда от подмены localStorage.activeRole
 */

// Тестовые данные (из conftest.py)
const USERS = {
  curator_teacher: {
    email: 'YVZhirnova@yandex.ru',
    password: 'student2026',
    roles: ['teacher', 'curator'],
    defaultRoute: /\/teacher\/statements/,
  },
  admin: {
    email: 'ang-bl@rambler.ru',
    password: 'student2026',
    roles: ['admin', 'teacher', 'curator'],
    defaultRoute: /\/admin\/users/,
  },
  mck: {
    email: 'tardv69@yandex.ru',
    password: 'student2026',
    roles: ['mck_head', 'teacher'],
    defaultRoute: /\/mck\/rpd/,
  },
};

/**
 * Хелпер: вход пользователя по email/password
 */
async function loginUser(page, email: string, password: string) {
  await page.context().clearCookies();
  await page.goto('/login');
  await page.evaluate(() => {
    localStorage.clear();
    sessionStorage.clear();
  });
  await page.reload();
  await page.waitForLoadState('networkidle');

  const emailInput = page.locator('input[type="email"], input[name="email"]').first();
  const passwordInput = page.locator('input[type="password"]').first();
  const loginButton = page.getByRole('button', { name: /войти/i });

  await emailInput.fill(email);
  await passwordInput.fill(password);
  await loginButton.click();
}

test.describe('БП 1.1-007: Маршрутизация Куратор+Преподаватель', () => {
  test.beforeEach(async ({ page }) => {
    await loginUser(page, USERS.curator_teacher.email, USERS.curator_teacher.password);
  });

  test('Редирект на /teacher/statements (роль с высшим приоритетом)', async ({ page }) => {
    await page.waitForURL(USERS.curator_teacher.defaultRoute, { timeout: 10000 });
    expect(page.url()).toMatch(USERS.curator_teacher.defaultRoute);
  });

  test('Виден переключатель ролей (Преподаватель ↔ Куратор)', async ({ page }) => {
    await page.waitForURL(USERS.curator_teacher.defaultRoute, { timeout: 10000 });

    // Ищем кнопку открытия RoleSwitcher (MUI Button с data-testid)
    const roleSwitcherButton = page.locator('[data-testid="role-switcher-button"]');
    await expect(roleSwitcherButton).toBeVisible();

    // Открываем dropdown
    await roleSwitcherButton.click();

    // Проверяем, что в меню есть пункты "Преподаватель" и "Куратор"
    const teacherMenuItem = page.getByRole('menuitem', { name: /преподаватель/i });
    const curatorMenuItem = page.getByRole('menuitem', { name: /куратор/i });
    
    await expect(teacherMenuItem).toBeVisible();
    await expect(curatorMenuItem).toBeVisible();
  });
});

test.describe('БП 1.1-008: Маршрутизация Администратора', () => {
  test.beforeEach(async ({ page }) => {
    await loginUser(page, USERS.admin.email, USERS.admin.password);
  });

  test('Редирект на /admin/users', async ({ page }) => {
    await page.waitForURL(USERS.admin.defaultRoute, { timeout: 10000 });
    expect(page.url()).toMatch(USERS.admin.defaultRoute);
  });

  test('Видны кнопки переключения всех ролей', async ({ page }) => {
    await page.waitForURL(USERS.admin.defaultRoute, { timeout: 10000 });

    // Открываем dropdown ролей
    const roleSwitcherButton = page.locator('[data-testid="role-switcher-button"]');
    await expect(roleSwitcherButton).toBeVisible();
    await roleSwitcherButton.click();

    // Проверяем наличие всех 3 ролей в меню
    const adminMenuItem = page.getByRole('menuitem', { name: /администратор/i });
    const teacherMenuItem = page.getByRole('menuitem', { name: /преподаватель/i });
    const curatorMenuItem = page.getByRole('menuitem', { name: /куратор/i });
    
    await expect(adminMenuItem).toBeVisible();
    await expect(teacherMenuItem).toBeVisible();
    await expect(curatorMenuItem).toBeVisible();
  });
});

test.describe('БП 1.1-009: Маршрутизация Председателя МЦК', () => {
  test.beforeEach(async ({ page }) => {
    await loginUser(page, USERS.mck.email, USERS.mck.password);
  });

  test('Редирект на /mck/rpd', async ({ page }) => {
    await page.waitForURL(USERS.mck.defaultRoute, { timeout: 10000 });
    expect(page.url()).toMatch(USERS.mck.defaultRoute);
  });

  test('Виден переключатель ролей (Преподаватель ↔ Председатель МЦК)', async ({ page }) => {
    await page.waitForURL(USERS.mck.defaultRoute, { timeout: 10000 });

    // Открываем dropdown ролей
    const roleSwitcherButton = page.locator('[data-testid="role-switcher-button"]');
    await expect(roleSwitcherButton).toBeVisible();
    await roleSwitcherButton.click();

    // Проверяем наличие "Преподаватель" и "МЦК" в меню
    const teacherMenuItem = page.getByRole('menuitem', { name: /преподаватель/i });
    const mckMenuItem = page.getByRole('menuitem', { name: /мцк|председатель/i });
    
    await expect(teacherMenuItem).toBeVisible();
    await expect(mckMenuItem).toBeVisible();
  });
});

test.describe('БП 1.1-022/023: Переключение ролей', () => {
  test('1.1-022: Клик на "Куратор" меняет URL', async ({ page }) => {
    // Входим как Куратор+Преподаватель
    await loginUser(page, USERS.curator_teacher.email, USERS.curator_teacher.password);
    await page.waitForURL(USERS.curator_teacher.defaultRoute, { timeout: 10000 });

    // 1. Открываем dropdown ролей
    const roleSwitcherButton = page.locator('[data-testid="role-switcher-button"]');
    await roleSwitcherButton.click();

    // 2. Кликаем на пункт "Куратор" в меню
    const curatorMenuItem = page.getByRole('menuitem', { name: /куратор/i });
    await curatorMenuItem.click();

    // URL должен измениться на /curator/... или /curator/group
    await page.waitForURL(/\/curator\//, { timeout: 10000 });
    expect(page.url()).toMatch(/\/curator\//);
  });

  test('1.1-023: F5 сохраняет выбранную роль', async ({ page }) => {
    // Входим как Куратор+Преподаватель
    await loginUser(page, USERS.curator_teacher.email, USERS.curator_teacher.password);
    await page.waitForURL(USERS.curator_teacher.defaultRoute, { timeout: 10000 });

    // 1. Открываем dropdown
    const roleSwitcherButton = page.locator('[data-testid="role-switcher-button"]');
    await roleSwitcherButton.click();

    // 2. Кликаем на "Куратор"
    const curatorMenuItem = page.getByRole('menuitem', { name: /куратор/i });
    await curatorMenuItem.click();

    await page.waitForURL(/\/curator\//, { timeout: 10000 });

    // F5 — обновляем страницу
    await page.reload();
    await page.waitForLoadState('networkidle');

    // URL должен остаться тем же (роль "Куратор")
    await page.waitForURL(/\/curator\//, { timeout: 10000 });
    expect(page.url()).toMatch(/\/curator\//);
  });
});

test.describe('БП 1.1-024: Защита от подмены localStorage.activeRole', () => {
  test('Студент вручную ставит activeRole=admin → редирект на свою роль', async ({ page }) => {
    // Входим как студент (только одна роль)
    await loginUser(page, 'arhipov_kyu@luberteh.ru', 'student2026');
    await page.waitForURL(/\/student\/profile/, { timeout: 10000 });

    // Хакерская атака: подменяем activeRole в localStorage
    await page.evaluate(() => {
      localStorage.setItem('activeRole', 'admin');
    });

    // F5 — обновляем страницу
    await page.reload();
    await page.waitForLoadState('networkidle');

    // Фронтенд должен обнаружить несоответствие и редиректить обратно на /student/profile
    // (или показать страницу "Нет доступа")
    await page.waitForTimeout(2000);
    const finalUrl = page.url();

    // Админ-панель НЕ должна быть доступна
    expect(finalUrl).not.toMatch(/\/admin\/users/);

    // Должны остаться на /student/... или увидеть страницу "нет доступа"
    const isStudentRoute = finalUrl.match(/\/student\//);
    const isAccessDenied = finalUrl.match(/access-denied|no-access|forbidden/i);
    expect(isStudentRoute || isAccessDenied).toBeTruthy();
  });
});
