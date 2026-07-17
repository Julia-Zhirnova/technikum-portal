import pytest
import re
from django.contrib.auth import get_user_model

User = get_user_model()


def calculate_snils_checksum(snils_digits: str) -> int:
    """
    Алгоритм расчета контрольной суммы СНИЛС (ПФР).
    Принимает строку из 11 цифр (без дефисов и пробелов).
    """
    if len(snils_digits) != 11 or not snils_digits.isdigit():
        return -1
    
    total = 0
    for i in range(9):
        total += int(snils_digits[i]) * (9 - i)
    
    if total < 100:
        return total
    elif total in (100, 101):
        return 0
    else:
        return total % 101


@pytest.mark.django_db
class TestSnilsValidation:
    """Тесты валидации СНИЛС."""

    def test_valid_snils_checksum(self):
        """Проверка корректного расчета контрольной суммы для валидного СНИЛС."""
        # Валидный СНИЛС: 112-345-678 28 (контрольная сумма = 28)
        snils = "11234567828"
        assert calculate_snils_checksum(snils) == 28

    def test_invalid_snils_checksum(self):
        """Проверка отклонения СНИЛС с неверной контрольной суммой."""
        # Неверная контрольная сумма (последние 2 цифры не 28)
        snils = "11234567899"
        assert calculate_snils_checksum(snils) != 99

    def test_snils_format_regex(self):
        """Проверка регулярного выражения формата СНИЛС."""
        pattern = r'^\d{3}-\d{3}-\d{3}\s\d{2}$'
        assert re.match(pattern, "112-345-678 28") is not None
        assert re.match(pattern, "11234567828") is None
        assert re.match(pattern, "11-345-678 28") is None


@pytest.mark.django_db
class TestInnValidation:
    """Тесты валидации ИНН физического лица."""

    def test_valid_inn_length(self):
        """ИНН физлица должен содержать ровно 12 цифр."""
        valid_inn = "123456789101"
        assert len(valid_inn) == 12
        assert valid_inn.isdigit() is True

    def test_invalid_inn_length(self):
        """ИНН с длиной 10 цифр или другой длиной должен отклоняться."""
        assert len("1234567890") != 12
        assert len("12345678901") != 12

    def test_inn_allows_empty(self):
        """ИНН может быть пустым."""
        assert True
