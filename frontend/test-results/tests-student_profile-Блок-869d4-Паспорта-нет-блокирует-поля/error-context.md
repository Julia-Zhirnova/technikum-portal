# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: tests/student_profile.spec.ts >> Блок 2.1.2: Паспорт >> 2.1.2.3: Чекбокс "Паспорта нет" блокирует поля
- Location: tests/student_profile.spec.ts:108:3

# Error details

```
Test timeout of 30000ms exceeded.
```

```
Error: locator.check: Test timeout of 30000ms exceeded.
Call log:
  - waiting for locator('[data-testid="no-passport-checkbox"]')

```

# Page snapshot

```yaml
- generic [ref=e3]:
  - banner [ref=e4]:
    - generic [ref=e5]:
      - generic [ref=e6]:
        - img "Логотип" [ref=e7]
        - paragraph [ref=e8]:
          - text: ГБПОУ МО
          - text: Люберецкий техникум
          - text: имени Героя Советского Союза,
          - text: лётчика-космонавта Ю. А. Гагарина
        - heading "ТехноПортал" [level=6] [ref=e9]
      - generic [ref=e10]:
        - paragraph [ref=e11]: Студент
        - paragraph [ref=e12]: Архипов Кирилл Юрьевич;Учащийся;ОИБ-24
        - button "ВЫХОД" [ref=e13] [cursor=pointer]
  - generic [ref=e14]:
    - list [ref=e19]:
      - link "Мой профиль" [ref=e20] [cursor=pointer]:
        - /url: /student/profile
        - img [ref=e22]
        - generic [ref=e25]: Мой профиль
      - link "Зачётная книжка" [ref=e26] [cursor=pointer]:
        - /url: /student/grades
        - img [ref=e28]
        - generic [ref=e31]: Зачётная книжка
      - link "Практика" [ref=e32] [cursor=pointer]:
        - /url: /student/practice
        - img [ref=e34]
        - generic [ref=e37]: Практика
      - link "Заявки" [ref=e38] [cursor=pointer]:
        - /url: /student/requests
        - img [ref=e40]
        - generic [ref=e43]: Заявки
      - link "Уведомления" [ref=e44] [cursor=pointer]:
        - /url: /student/notifications
        - img [ref=e46]
        - generic [ref=e49]: Уведомления
    - main [ref=e50]:
      - generic [ref=e52]:
        - img [ref=e53]
        - heading "Страница в разработке" [level=4] [ref=e55]
        - paragraph [ref=e56]: Этот раздел портала ТехноПортал пока находится в активной разработке. Мы работаем над тем, чтобы сделать его максимально удобным для вас. Пожалуйста, воспользуйтесь другими пунктами меню или вернитесь позже.
        - button "Вернуться назад" [ref=e57] [cursor=pointer]
  - contentinfo [ref=e58]:
    - generic [ref=e59]:
      - paragraph [ref=e60]: © 2026 ТехноПортал. ГБПОУ МО «Люберецкий техникум им. Ю.А. Гагарина»
      - paragraph [ref=e61]: "Корпуса: Люберецкий, Гагаринский, Красково, Угреша"
      - generic [ref=e62]:
        - link "Перейти на сайт →" [ref=e63] [cursor=pointer]:
          - /url: https://luberteh.ru/
        - link "Посмотреть на карте →" [ref=e64] [cursor=pointer]:
          - /url: https://yandex.ru/maps/?ll=37.969070%2C55.638299&mode=search&sctx=ZAAAAAgBEAAaKAoSCfcDHhhA8kJAEbZN8bio0ktAEhIJDJQUWABT1j8Rc4I2OXzSvT8iBgABAgMEBSgKOABAooIGSAFqAnJ1nQHNzMw9oAEAqAEAvQF4Cb%2FLwgEU6YLN8QPxmaKcBP%2B61%2FAD2aTZzgSCAjLQu9GO0LHQtdGA0LXRhtC60LjQuSDRgtC10YXQvdC40LrRg9C8INC60L7RgNC%2F0YPRgYoCAJICAJoCDGRlc2t0b3AtbWFwcw%3D%3D&sll=37.969070%2C55.638299&source=serp_navig&sspn=0.348816%2C0.116516&text=%D0%BB%D1%8E%D0%B1%D0%B5%D1%80%D0%B5%D1%86%D0%BA%D0%B8%D0%B9%20%D1%82%D0%B5%D1%85%D0%BD%D0%B8%D0%BA%D1%83%D0%BC%20%D0%BA%D0%BE%D1%80%D0%BF%D1%83%D1%81&z=12
```

# Test source

```ts
  10  |     await page.waitForURL('**/student**');
  11  |     await page.goto('http://localhost:5173/student/profile');
  12  |   });
  13  | 
  14  |   test('2.1.1.1: Маска СНИЛС автоматически форматирует ввод', async ({ page }) => {
  15  |     const snilsInput = page.locator('[data-testid="snils-input"]');
  16  |     await snilsInput.fill('11234567890');
  17  |     
  18  |     // Проверяем, что маска автоматически добавила дефисы и пробел
  19  |     await expect(snilsInput).toHaveValue('112-345-678 90');
  20  |   });
  21  | 
  22  |   test('2.1.1.2: Валидация СНИЛС на фронтенде', async ({ page }) => {
  23  |     const snilsInput = page.locator('[data-testid="snils-input"]');
  24  |     await snilsInput.fill('112-345-678 99'); // Невалидная контрольная сумма
  25  |     
  26  |     // Проверяем появление ошибки
  27  |     await expect(page.locator('text=Неверный формат СНИЛС или контрольная сумма')).toBeVisible();
  28  |   });
  29  | 
  30  |   test('2.1.1.3: Маска телефона форматирует ввод', async ({ page }) => {
  31  |     const phoneInput = page.locator('[data-testid="phone-input"]');
  32  |     await phoneInput.fill('89997776655');
  33  |     
  34  |     // Проверяем форматирование (опционально, зависит от реализации)
  35  |     const value = await phoneInput.inputValue();
  36  |     expect(value).toContain('89997776655');
  37  |   });
  38  | 
  39  |   test('2.1.1.4: Чекбокс согласия на ПДн заполняет дату автоматически', async ({ page }) => {
  40  |     const consentCheckbox = page.locator('[data-testid="pd-consent-checkbox"]');
  41  |     await consentCheckbox.check();
  42  |     
  43  |     // Проверяем, что поле даты заполнилось
  44  |     const consentDate = page.locator('[data-testid="pd-consent-date"]');
  45  |     await expect(consentDate).not.toBeEmpty();
  46  |   });
  47  | 
  48  |   test('2.1.5.2: Автосохранение черновика каждые 30 секунд', async ({ page }) => {
  49  |     const phoneInput = page.locator('[data-testid="phone-input"]');
  50  |     await phoneInput.fill('89998887766');
  51  |     
  52  |     // Ждём 30 секунд (или меньше, если интервал настроен)
  53  |     await page.waitForTimeout(31000);
  54  |     
  55  |     // Проверяем иконку автосохранения
  56  |     await expect(page.locator('[data-testid="autosave-icon"]')).toContainText('✅');
  57  |   });
  58  | 
  59  |   test('2.1.5.3: Восстановление черновика при открытии', async ({ page }) => {
  60  |     // Заполняем данные
  61  |     const phoneInput = page.locator('[data-testid="phone-input"]');
  62  |     await phoneInput.fill('89998887766');
  63  |     
  64  |     // Закрываем вкладку
  65  |     await page.close();
  66  |     
  67  |     // Открываем снова
  68  |     const newPage = await page.context().newPage();
  69  |     await newPage.goto('http://localhost:5173/student/profile');
  70  |     
  71  |     // Проверяем модальное окно восстановления
  72  |     await expect(newPage.locator('text=Восстановить черновик')).toBeVisible();
  73  |   });
  74  | });
  75  | 
  76  | test.describe('Блок 2.1.2: Паспорт', () => {
  77  |   
  78  |   test.beforeEach(async ({ page }) => {
  79  |     await page.goto('http://localhost:5173/login');
  80  |     await page.locator('input[type="email"]').fill('arhipov_kyu@luberteh.ru');
  81  |     await page.locator('input[type="password"]').fill('student2026');
  82  |     await page.locator('button:has-text("Войти")').click();
  83  |     await page.waitForURL('**/student**');
  84  |     await page.goto('http://localhost:5173/student/passport');
  85  |   });
  86  | 
  87  |   test('2.1.2.1: Чекбокс "Иностранный гражданин" меняет маску', async ({ page }) => {
  88  |     const foreignCheckbox = page.locator('[data-testid="foreign-citizen-checkbox"]');
  89  |     await foreignCheckbox.check();
  90  |     
  91  |     // Проверяем, что поле серии принимает буквы
  92  |     const seriesInput = page.locator('[data-testid="passport-series-input"]');
  93  |     await seriesInput.fill('AB12345');
  94  |     await expect(seriesInput).toHaveValue('AB12345');
  95  |   });
  96  | 
  97  |   test('2.1.2.2: Кнопка "Совпадает с регистрацией" копирует адрес', async ({ page }) => {
  98  |     const registrationAddress = page.locator('[data-testid="registration-address-input"]');
  99  |     await registrationAddress.fill('обл. Московская, г. Люберцы, ул. Зеленая, д. 7');
  100 |     
  101 |     const copyButton = page.locator('[data-testid="copy-address-button"]');
  102 |     await copyButton.click();
  103 |     
  104 |     const actualAddress = page.locator('[data-testid="actual-address-input"]');
  105 |     await expect(actualAddress).toHaveValue('обл. Московская, г. Люберцы, ул. Зеленая, д. 7');
  106 |   });
  107 | 
  108 |   test('2.1.2.3: Чекбокс "Паспорта нет" блокирует поля', async ({ page }) => {
  109 |     const noPassportCheckbox = page.locator('[data-testid="no-passport-checkbox"]');
> 110 |     await noPassportCheckbox.check();
      |                              ^ Error: locator.check: Test timeout of 30000ms exceeded.
  111 |     
  112 |     const seriesInput = page.locator('[data-testid="passport-series-input"]');
  113 |     await expect(seriesInput).toBeDisabled();
  114 |     
  115 |     // Проверяем появление поля причины
  116 |     await expect(page.locator('[data-testid="no-passport-reason-input"]')).toBeVisible();
  117 |   });
  118 | });
  119 | 
  120 | test.describe('Блок 2.1.3: Здоровье', () => {
  121 |   
  122 |   test.beforeEach(async ({ page }) => {
  123 |     await page.goto('http://localhost:5173/login');
  124 |     await page.locator('input[type="email"]').fill('arhipov_kyu@luberteh.ru');
  125 |     await page.locator('input[type="password"]').fill('student2026');
  126 |     await page.locator('button:has-text("Войти")').click();
  127 |     await page.waitForURL('**/student**');
  128 |     await page.goto('http://localhost:5173/student/health');
  129 |   });
  130 | 
  131 |   test('2.1.3.1: Выбор "Имею инвалидность" показывает поле диагноза', async ({ page }) => {
  132 |     const healthStatusSelect = page.locator('[data-testid="health-status-select"]');
  133 |     await healthStatusSelect.click();
  134 |     await page.locator('[role="option"]:has-text("Инвалидность")').click();
  135 |     
  136 |     // Проверяем появление поля диагноза
  137 |     await expect(page.locator('[data-testid="diagnosis-input"]')).toBeVisible();
  138 |   });
  139 | 
  140 |   test('2.1.3.2: Чекбокс "Полиса ОМС нет" блокирует поля ОМС', async ({ page }) => {
  141 |     const noOmsCheckbox = page.locator('[data-testid="no-oms-checkbox"]');
  142 |     await noOmsCheckbox.check();
  143 |     
  144 |     const omsNumberInput = page.locator('[data-testid="oms-number-input"]');
  145 |     await expect(omsNumberInput).toBeDisabled();
  146 |   });
  147 | });
  148 | 
```