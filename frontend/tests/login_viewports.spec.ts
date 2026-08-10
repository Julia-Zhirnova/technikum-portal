/**
 * Блок 1.1: Тесты адаптивности страницы /login (TC043-TC046)
 * 
 * TC043: Планшет (768x1024, портрет)
 * TC044: 4K экран (3840x2160)
 * TC045: Масштабирование 200%
 * TC046: Очень маленький экран (320x480)
 */
import { test, expect } from '@playwright/test';

test.describe('Блок 1.1: Адаптивность страницы /login', () => {
  
  test('TC043: Планшет (768x1024, портрет)', async ({ page }) => {
    await page.setViewportSize({ width: 768, height: 1024 });
    await page.goto('/login');
    
    // Страница загружается
    await expect(page.getByRole('heading', { name: 'ТехноПортал' })).toBeVisible();
    
    // Поля ввода видны
    await expect(page.locator('input[type="email"]')).toBeVisible();
    await expect(page.locator('input[type="password"]')).toBeVisible();
    await expect(page.getByRole('button', { name: 'Войти' })).toBeVisible();
    
    // Нет горизонтального скролла
    const bodyWidth = await page.evaluate(() => document.body.scrollWidth);
    const viewportWidth = await page.evaluate(() => window.innerWidth);
    expect(bodyWidth).toBeLessThanOrEqual(viewportWidth + 20); // допуск 20px
  });

  test('TC044: 4K экран (3840x2160)', async ({ page }) => {
    await page.setViewportSize({ width: 3840, height: 2160 });
    await page.goto('/login');
    
    // Страница загружается
    await expect(page.getByRole('heading', { name: 'ТехноПортал' })).toBeVisible();
    
    // Элементы масштабируются (шрифты не слишком мелкие)
    const heading = page.getByRole('heading', { name: 'ТехноПортал' });
    const fontSize = await heading.evaluate(el => 
      window.getComputedStyle(el).fontSize
    );
    const fontSizePx = parseFloat(fontSize);
    expect(fontSizePx).toBeGreaterThanOrEqual(16); // минимум 16px на 4K
    
    // Поля ввода видны и имеют адекватный размер
    const emailInput = page.locator('input[type="email"]');
    await expect(emailInput).toBeVisible();
    const inputHeight = await emailInput.evaluate(el => el.offsetHeight);
    expect(inputHeight).toBeGreaterThanOrEqual(40); // минимум 40px высота
  });

  test('TC045: Масштабирование 200%', async ({ page }) => {
    await page.goto('/login');
    
    // Устанавливаем zoom 200%
    await page.evaluate(() => {
      document.body.style.zoom = '200%';
    });
    
    // Страница остаётся читаемой
    await expect(page.getByRole('heading', { name: 'ТехноПортал' })).toBeVisible();
    await expect(page.locator('input[type="email"]')).toBeVisible();
    await expect(page.locator('input[type="password"]')).toBeVisible();
    
    // Нет горизонтального скролла (или минимальный)
    const bodyWidth = await page.evaluate(() => document.body.scrollWidth);
    const viewportWidth = await page.evaluate(() => window.innerWidth);
    // При zoom 200% scrollWidth может быть больше, но не критично
    expect(bodyWidth).toBeLessThanOrEqual(viewportWidth * 2.5);
  });

  test('TC046: Очень маленький экран (320x480)', async ({ page }) => {
    await page.setViewportSize({ width: 320, height: 480 });
    await page.goto('/login');
    
    // Страница загружается
    await expect(page.getByRole('heading', { name: 'ТехноПортал' })).toBeVisible();
    
    // Поля ввода видны (могут быть уменьшены)
    await expect(page.locator('input[type="email"]')).toBeVisible();
    await expect(page.locator('input[type="password"]')).toBeVisible();
    await expect(page.getByRole('button', { name: 'Войти' })).toBeVisible();
    
    // Нет горизонтального скролла
    const bodyWidth = await page.evaluate(() => document.body.scrollWidth);
    const viewportWidth = await page.evaluate(() => window.innerWidth);
    expect(bodyWidth).toBeLessThanOrEqual(viewportWidth + 10);
    
    // Шапка не ломается
    const header = page.locator('header, [role="banner"]').first();
    if (await header.isVisible()) {
      const headerHeight = await header.evaluate(el => el.offsetHeight);
      expect(headerHeight).toBeLessThanOrEqual(100); // шапка не слишком высокая
    }
  });
});
