"""E2E-тесты для БП 1.1 (страница /login)."""
import pytest
from playwright.sync_api import Page, expect

BASE_URL = "http://localhost:5173"


def test_1_1_001_login_page_ui(page: Page):
    """[1.1-001] Страница /login загружается, содержит брендинг и форму."""
    page.goto(f"{BASE_URL}/login")

    # Брендинг — используем heading для точного матчинга
    expect(page.get_by_role("heading", name="ТехноПортал")).to_be_visible()

    # Форма входа
    expect(page.locator('input[type="email"]')).to_be_visible()
    expect(page.locator('input[type="password"]')).to_be_visible()
    expect(page.get_by_role("button", name="Войти")).to_be_enabled()


def test_1_1_002_successful_login_and_routing(page: Page):
    """[1.1-002, 1.1-006] Успешный вход студента → редирект на /student/profile."""
    page.goto(f"{BASE_URL}/login")

    page.locator('input[type="email"]').fill("arhipov_kyu@luberteh.ru")
    page.locator('input[type="password"]').fill("student2026")
    page.get_by_role("button", name="Войти").click()

    # Ждём редирект на /student/profile
    page.wait_for_url("**/student/profile**", timeout=10000)
    assert "/student/profile" in page.url
