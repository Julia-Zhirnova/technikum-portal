import re
from datetime import date, timedelta
from .exceptions import ValidationError


def validate_snils(snils: str) -> None:
    """Валидация СНИЛС: формат XXX-XXX-XXX XX и контрольная сумма ПФР"""
    if not snils:
        raise ValidationError("СНИЛС не может быть пустым")
    
    pattern = r'^\d{3}-\d{3}-\d{3} \d{2}$'
    if not re.match(pattern, snils):
        raise ValidationError("Неверный формат СНИЛС. Ожидается формат XXX-XXX-XXX XX")
    
    digits = snils.replace('-', '').replace(' ', '')
    if len(digits) != 11:
        raise ValidationError("СНИЛС должен содержать 11 цифр")
    
    number = digits[:9]
    checksum = int(digits[9:])
    
    weights = [9, 8, 7, 6, 5, 4, 3, 2, 1]
    total = sum(int(number[i]) * weights[i] for i in range(9))
    
    if total < 100:
        expected_checksum = total
    elif total in (100, 101):
        expected_checksum = 0
    else:
        total = total % 101
        if total in (100, 101):
            expected_checksum = 0
        else:
            expected_checksum = total
    
    if checksum != expected_checksum:
        raise ValidationError("Неверный формат СНИЛС или контрольная сумма не совпадает")


def validate_inn(inn: str) -> None:
    """Валидация ИНН: 12 цифр или пустое"""
    if not inn:
        return
    
    if not inn.isdigit():
        raise ValidationError("ИНН должен содержать только цифры")
    
    if len(inn) != 12:
        raise ValidationError("ИНН должен содержать 12 цифр")


def validate_phone(phone: str) -> None:
    """Валидация телефона: 11 цифр"""
    clean_phone = re.sub(r'[^\d]', '', phone)
    
    if len(clean_phone) != 11:
        raise ValidationError("Телефон должен содержать 11 цифр")
    
    if not clean_phone.startswith('7') and not clean_phone.startswith('8'):
        raise ValidationError("Телефон должен начинаться с 7 или 8")


def validate_email_custom(email: str) -> None:
    """Валидация email"""
    if not email:
        raise ValidationError("Email не может быть пустым")
    
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(pattern, email):
        raise ValidationError("Некорректный email")


def validate_birth_date(birth_date: date) -> None:
    """Валидация даты рождения: не в будущем, не старше 100 лет"""
    if birth_date > date.today():
        raise ValidationError("Дата рождения не может быть в будущем")
    
    if birth_date < date.today() - timedelta(days=365 * 100):
        raise ValidationError("Дата рождения не может быть старше 100 лет")


def validate_passport_series_rf(series: str) -> None:
    """Валидация серии паспорта РФ: 4 цифры"""
    if not series.isdigit() or len(series) != 4:
        raise ValidationError("Серия паспорта РФ должна содержать 4 цифры")


def validate_passport_number_rf(number: str) -> None:
    """Валидация номера паспорта РФ: 6 цифр"""
    if not number.isdigit() or len(number) != 6:
        raise ValidationError("Номер паспорта РФ должен содержать 6 цифр")


def validate_passport_issue_date(issue_date: date, birth_date: date, is_foreign: bool = False) -> None:
    """Валидация даты выдачи паспорта"""
    if issue_date > date.today():
        raise ValidationError("Дата выдачи не может быть в будущем")
    
    if not is_foreign:
        min_issue_date = birth_date + timedelta(days=365 * 14)
        if issue_date < min_issue_date:
            raise ValidationError("Дата выдачи паспорта не может быть раньше 14-летия")


def validate_oms_policy_number(policy_number: str) -> None:
    """Валидация номера полиса ОМС: 10-16 цифр или пустое"""
    if not policy_number:
        return
    
    if not policy_number.isdigit():
        raise ValidationError("Номер полиса ОМС должен содержать только цифры")
    
    if len(policy_number) < 10 or len(policy_number) > 16:
        raise ValidationError("Номер полиса ОМС должен содержать 10-16 цифр")


def validate_passport_code(code: str) -> None:
    """Валидация кода подразделения: формат XXX-XXX"""
    pattern = r'^\d{3}-\d{3}$'
    if not re.match(pattern, code):
        raise ValidationError("Код подразделения должен иметь формат XXX-XXX")
