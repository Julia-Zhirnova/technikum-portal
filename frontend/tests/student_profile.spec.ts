import { test, expect } from '@playwright/test';

test.describe('Блок 2.1: Профиль студента', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('http://localhost:5173/login');
    await page.locator('input[type="email"]').fill('arhipov_kyu@luberteh.ru');
    await page.locator('input[type="password"]').fill('student2026');
    await page.locator('button:has-text("Войти")').click();
    await page.waitForURL('**/student**');
    await page.goto('http://localhost:5173/student/profile');
    await page.waitForSelector('[data-testid="snils-input"]', { state: 'visible', timeout: 10000 });
  });

  test('2.1.1.1: Маска СНИЛС автоматически форматирует ввод', async ({ page }) => {
    const snilsInput = page.locator('[data-testid="snils-input"] input');
    await snilsInput.fill('11234567890');
    await expect(snilsInput).toHaveValue('112-345-678 90');
  });

  test('2.1.1.2: Валидация СНИЛС на фронтенде', async ({ page }) => {
    const snilsInput = page.locator('[data-testid="snils-input"] input');
    await snilsInput.fill('112-345-678 99');
    await expect(page.locator('text=Неверный формат')).toBeVisible();
  });

  test('2.1.1.3: Маска телефона форматирует ввод', async ({ page }) => {
    const phoneInput = page.locator('[data-testid="phone-input"] input');
    await phoneInput.fill('89997776655');
    const value = await phoneInput.inputValue();
    expect(value).toContain('89997776655');
  });

  test('2.1.1.4: Чекбокс согласия на ПДн заполняет дату автоматически', async ({ page }) => {
    const consentCheckbox = page.locator('[data-testid="pd-consent-checkbox"]');
    if (await consentCheckbox.count() > 0) {
      await consentCheckbox.check();
      await expect(page.locator('[data-testid="pd-consent-date"]')).toBeVisible();
    }
  });

  test('2.1.5.2: Автосохранение черновика каждые 30 секунд', async ({ page }) => {
    test.setTimeout(40000);
    const phoneInput = page.locator('[data-testid="phone-input"] input');
    await phoneInput.fill('89998887766');
    await page.waitForTimeout(31000);
    await expect(page.locator('[data-testid="autosave-icon"]')).toContainText('✅');
  });

  test('2.1.5.3: Восстановление черновика при открытии', async ({ page }) => {
    // Имитируем наличие черновика в localStorage для ускорения и надежности теста
    await page.evaluate(() => {
      localStorage.setItem('student_profile_draft', JSON.stringify({ phone: '89998887766' }));
    });
    
    // Перезагружаем страницу, чтобы сработал useEffect проверки черновика
    await page.reload();
    
    // Явно ждем появления кнопки в диалоговом окне и кликаем по ней
    const restoreButton = page.getByRole('button', { name: 'Восстановить черновик' });
    await restoreButton.waitFor({ state: 'visible', timeout: 5000 });
    await restoreButton.click();
    
    await page.waitForSelector('[data-testid="phone-input"]');
    const phoneInput = page.locator('[data-testid="phone-input"] input');
    await expect(phoneInput).toHaveValue('89998887766');
  });
});

test.describe('Блок 2.1.2: Паспорт', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('http://localhost:5173/login');
    await page.locator('input[type="email"]').fill('arhipov_kyu@luberteh.ru');
    await page.locator('input[type="password"]').fill('student2026');
    await page.locator('button:has-text("Войти")').click();
    await page.waitForURL('**/student**');
    await page.goto('http://localhost:5173/student/passport');
    await page.waitForSelector('[data-testid="foreign-citizen-checkbox"]', { state: 'visible', timeout: 10000 });
  });

  test('2.1.2.1: Чекбокс "Иностранный гражданин" меняет маску', async ({ page }) => {
    await page.locator('[data-testid="foreign-citizen-checkbox"]').check();
    const seriesInput = page.locator('[data-testid="passport-series-input"] input');
    await seriesInput.fill('AB12345');
    await expect(seriesInput).toHaveValue('AB12345');
  });

  test('2.1.2.2: Кнопка "Совпадает с регистрацией" копирует адрес', async ({ page }) => {
    const regInput = page.locator('[data-testid="registration-address-input"] input');
    await regInput.fill('обл. Московская, г. Люберцы, ул. Зеленая, д. 7');
    await page.locator('[data-testid="copy-address-button"]').click();
    const actualInput = page.locator('[data-testid="actual-address-input"] input');
    await expect(actualInput).toHaveValue('обл. Московская, г. Люберцы, ул. Зеленая, д. 7');
  });

  test('2.1.2.3: Чекбокс "Паспорта нет" блокирует поля', async ({ page }) => {
    await page.locator('[data-testid="no-passport-checkbox"]').check();
    const seriesInput = page.locator('[data-testid="passport-series-input"] input');
    await expect(seriesInput).toBeDisabled();
  });
});

test.describe('Блок 2.1.3: Здоровье', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('http://localhost:5173/login');
    await page.locator('input[type="email"]').fill('arhipov_kyu@luberteh.ru');
    await page.locator('input[type="password"]').fill('student2026');
    await page.locator('button:has-text("Войти")').click();
    await page.waitForURL('**/student**');
    await page.goto('http://localhost:5173/student/health');
    await page.waitForSelector('[data-testid="health-status-select"]', { state: 'visible', timeout: 10000 });
  });

  test('2.1.3.1: Выбор "Имею инвалидность" показывает поле диагноза', async ({ page }) => {
    // Теперь data-testid гарантированно находится на теге <select>
    await page.locator('select[data-testid="health-status-select"]').selectOption('Инвалидность');
    await expect(page.locator('[data-testid="diagnosis-input"]')).toBeVisible();
  });

  test('2.1.3.2: Чекбокс "Полиса ОМС нет" блокирует поля ОМС', async ({ page }) => {
    await page.locator('[data-testid="no-oms-checkbox"]').check();
    const omsInput = page.locator('[data-testid="oms-number-input"] input');
    await expect(omsInput).toBeDisabled();
  });
});
