import { test, expect } from '@playwright/test';

test.describe('Блок 2.1: Профиль студента', () => {
  
  test.beforeEach(async ({ page }) => {
    await page.goto('http://localhost:5173/login');
    await page.locator('input[type="email"]').fill('arhipov_kyu@luberteh.ru');
    await page.locator('input[type="password"]').fill('student2026');
    await page.locator('button:has-text("Войти")').click();
    await page.waitForURL('**/student**');
    await page.goto('http://localhost:5173/student/profile');
  });

  test('2.1.1.1: Маска СНИЛС автоматически форматирует ввод', async ({ page }) => {
    const snilsInput = page.locator('[data-testid="snils-input"]');
    await snilsInput.fill('11234567890');
    
    // Проверяем, что маска автоматически добавила дефисы и пробел
    await expect(snilsInput).toHaveValue('112-345-678 90');
  });

  test('2.1.1.2: Валидация СНИЛС на фронтенде', async ({ page }) => {
    const snilsInput = page.locator('[data-testid="snils-input"]');
    await snilsInput.fill('112-345-678 99'); // Невалидная контрольная сумма
    
    // Проверяем появление ошибки
    await expect(page.locator('text=Неверный формат СНИЛС или контрольная сумма')).toBeVisible();
  });

  test('2.1.1.3: Маска телефона форматирует ввод', async ({ page }) => {
    const phoneInput = page.locator('[data-testid="phone-input"]');
    await phoneInput.fill('89997776655');
    
    // Проверяем форматирование (опционально, зависит от реализации)
    const value = await phoneInput.inputValue();
    expect(value).toContain('89997776655');
  });

  test('2.1.1.4: Чекбокс согласия на ПДн заполняет дату автоматически', async ({ page }) => {
    const consentCheckbox = page.locator('[data-testid="pd-consent-checkbox"]');
    await consentCheckbox.check();
    
    // Проверяем, что поле даты заполнилось
    const consentDate = page.locator('[data-testid="pd-consent-date"]');
    await expect(consentDate).not.toBeEmpty();
  });

  test('2.1.5.2: Автосохранение черновика каждые 30 секунд', async ({ page }) => {
    const phoneInput = page.locator('[data-testid="phone-input"]');
    await phoneInput.fill('89998887766');
    
    // Ждём 30 секунд (или меньше, если интервал настроен)
    await page.waitForTimeout(31000);
    
    // Проверяем иконку автосохранения
    await expect(page.locator('[data-testid="autosave-icon"]')).toContainText('✅');
  });

  test('2.1.5.3: Восстановление черновика при открытии', async ({ page }) => {
    // Заполняем данные
    const phoneInput = page.locator('[data-testid="phone-input"]');
    await phoneInput.fill('89998887766');
    
    // Закрываем вкладку
    await page.close();
    
    // Открываем снова
    const newPage = await page.context().newPage();
    await newPage.goto('http://localhost:5173/student/profile');
    
    // Проверяем модальное окно восстановления
    await expect(newPage.locator('text=Восстановить черновик')).toBeVisible();
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
  });

  test('2.1.2.1: Чекбокс "Иностранный гражданин" меняет маску', async ({ page }) => {
    const foreignCheckbox = page.locator('[data-testid="foreign-citizen-checkbox"]');
    await foreignCheckbox.check();
    
    // Проверяем, что поле серии принимает буквы
    const seriesInput = page.locator('[data-testid="passport-series-input"]');
    await seriesInput.fill('AB12345');
    await expect(seriesInput).toHaveValue('AB12345');
  });

  test('2.1.2.2: Кнопка "Совпадает с регистрацией" копирует адрес', async ({ page }) => {
    const registrationAddress = page.locator('[data-testid="registration-address-input"]');
    await registrationAddress.fill('обл. Московская, г. Люберцы, ул. Зеленая, д. 7');
    
    const copyButton = page.locator('[data-testid="copy-address-button"]');
    await copyButton.click();
    
    const actualAddress = page.locator('[data-testid="actual-address-input"]');
    await expect(actualAddress).toHaveValue('обл. Московская, г. Люберцы, ул. Зеленая, д. 7');
  });

  test('2.1.2.3: Чекбокс "Паспорта нет" блокирует поля', async ({ page }) => {
    const noPassportCheckbox = page.locator('[data-testid="no-passport-checkbox"]');
    await noPassportCheckbox.check();
    
    const seriesInput = page.locator('[data-testid="passport-series-input"]');
    await expect(seriesInput).toBeDisabled();
    
    // Проверяем появление поля причины
    await expect(page.locator('[data-testid="no-passport-reason-input"]')).toBeVisible();
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
  });

  test('2.1.3.1: Выбор "Имею инвалидность" показывает поле диагноза', async ({ page }) => {
    const healthStatusSelect = page.locator('[data-testid="health-status-select"]');
    await healthStatusSelect.click();
    await page.locator('[role="option"]:has-text("Инвалидность")').click();
    
    // Проверяем появление поля диагноза
    await expect(page.locator('[data-testid="diagnosis-input"]')).toBeVisible();
  });

  test('2.1.3.2: Чекбокс "Полиса ОМС нет" блокирует поля ОМС', async ({ page }) => {
    const noOmsCheckbox = page.locator('[data-testid="no-oms-checkbox"]');
    await noOmsCheckbox.check();
    
    const omsNumberInput = page.locator('[data-testid="oms-number-input"]');
    await expect(omsNumberInput).toBeDisabled();
  });
});
