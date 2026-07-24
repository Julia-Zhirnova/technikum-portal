import pytest
from datetime import date, timedelta
from core.validators import (
    validate_snils, validate_inn, validate_phone,
    validate_email_custom, validate_birth_date,
    validate_passport_series_rf, validate_passport_number_rf,
    validate_passport_issue_date, validate_oms_policy_number,
    validate_passport_code
)
from core.exceptions import ValidationError

class TestSnilsValidation:
    def test_valid_snils_format(self):
        validate_snils("182-530-946 72")

    def test_valid_snils_checksum(self):
        validate_snils("182-530-946 72")

    def test_invalid_snils_checksum(self):
        with pytest.raises(ValidationError) as exc_info:
            validate_snils("182-530-946 99")
        assert "контрольная сумма" in str(exc_info.value).lower()

    def test_invalid_snils_format(self):
        with pytest.raises(ValidationError) as exc_info:
            validate_snils("18253094672")
        assert "формат" in str(exc_info.value).lower()

    def test_snils_with_letters(self):
        with pytest.raises(ValidationError):
            validate_snils("182-530-946 AB")

    def test_snils_too_short(self):
        with pytest.raises(ValidationError):
            validate_snils("182-530-94")

class TestInnValidation:
    def test_valid_inn_12_digits(self):
        validate_inn("123456789101")

    def test_valid_inn_empty(self):
        validate_inn("")

    def test_invalid_inn_10_digits(self):
        with pytest.raises(ValidationError) as exc_info:
            validate_inn("1234567890")
        assert "12 цифр" in str(exc_info.value)

    def test_invalid_inn_letters(self):
        with pytest.raises(ValidationError):
            validate_inn("12345678910A")

    def test_invalid_inn_too_long(self):
        with pytest.raises(ValidationError):
            validate_inn("1234567891011")

class TestPhoneValidation:
    def test_valid_phone_format(self):
        validate_phone("89997776655")

    def test_valid_phone_with_plus(self):
        validate_phone("+79997776655")

    def test_invalid_phone_too_short(self):
        with pytest.raises(ValidationError) as exc_info:
            validate_phone("899977766")
        assert "11 цифр" in str(exc_info.value)

    def test_invalid_phone_letters(self):
        with pytest.raises(ValidationError):
            validate_phone("8999777665A")

class TestEmailValidation:
    def test_valid_email(self):
        validate_email_custom("test@yandex.ru")

    def test_invalid_email_no_at(self):
        with pytest.raises(ValidationError):
            validate_email_custom("testyandex.ru")

    def test_invalid_email_no_domain(self):
        with pytest.raises(ValidationError):
            validate_email_custom("test@")

    def test_invalid_email_spaces(self):
        with pytest.raises(ValidationError):
            validate_email_custom("test @yandex.ru")

class TestBirthDateValidation:
    def test_valid_birth_date(self):
        validate_birth_date(date(2007, 7, 7))

    def test_invalid_birth_date_future(self):
        future_date = date.today() + timedelta(days=1)
        with pytest.raises(ValidationError) as exc_info:
            validate_birth_date(future_date)
        assert "будущем" in str(exc_info.value).lower()

    def test_invalid_birth_date_too_old(self):
        old_date = date.today() - timedelta(days=365 * 101)
        with pytest.raises(ValidationError) as exc_info:
            validate_birth_date(old_date)
        assert "100 лет" in str(exc_info.value)

class TestPassportValidation:
    def test_valid_passport_series_rf(self):
        validate_passport_series_rf("4619")

    def test_invalid_passport_series_rf_letters(self):
        with pytest.raises(ValidationError):
            validate_passport_series_rf("46AB")

    def test_valid_passport_number_rf(self):
        validate_passport_number_rf("686868")

    def test_invalid_passport_number_rf_too_short(self):
        with pytest.raises(ValidationError):
            validate_passport_number_rf("68686")

    def test_valid_passport_issue_date(self):
        birth_date = date(2007, 7, 7)
        issue_date = date(2023, 7, 7)
        validate_passport_issue_date(issue_date, birth_date, is_foreign=False)

    def test_invalid_passport_issue_date_before_14(self):
        birth_date = date(2008, 9, 28)
        issue_date = date(2020, 1, 1)
        with pytest.raises(ValidationError) as exc_info:
            validate_passport_issue_date(issue_date, birth_date, is_foreign=False)
        assert "14" in str(exc_info.value)

    def test_valid_passport_code(self):
        validate_passport_code("500-066")

    def test_invalid_passport_code_format(self):
        with pytest.raises(ValidationError):
            validate_passport_code("500066")

class TestOmsValidation:
    def test_valid_oms_16_digits(self):
        validate_oms_policy_number("5091199794001932")

    def test_valid_oms_10_digits(self):
        validate_oms_policy_number("1234567890")

    def test_invalid_oms_5_digits(self):
        with pytest.raises(ValidationError) as exc_info:
            validate_oms_policy_number("12345")
        assert "10-16 цифр" in str(exc_info.value)

    def test_valid_oms_empty(self):
        validate_oms_policy_number("")
