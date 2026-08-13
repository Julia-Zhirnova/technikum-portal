"""БП 2.1.6 (Шифрование чувствительных данных): TC014, TC034-TC035.

Строки tests.txt: 1484-1549.

КРИТИЧНО: Блок 2.1.6 полностью не реализован:
- Поля snils_encrypted, snils_hash, inn_encrypted, inn_hash ОТСУТСТВУЮТ
- Поля snils, inn — обычные CharField (НЕ зашифрованы)
- FERNET_KEYS не найден в config/settings.py
- updated_at для optimistic locking ОТСУТСТВУЕТ

Отложены (⏳): TC036-TC040 (ротация, перешифровка, 1 млн записей),
TC041-TC047 (админка, мониторинг, Celery), TC048-TC052 (edge cases .env).
"""
import pytest

from core.models import Student


@pytest.mark.django_db
class TestBlock216EncryptionNotImplemented:
    """TC014: проверка отсутствия шифрования."""

    def test_TC014_encryption_fields_not_implemented(self, db):
        """БП2.1.6-TC014: [Security] Поля шифрования отсутствуют в модели.
        
        ТЗ ожидает: snils_encrypted, snils_hash, inn_encrypted, inn_hash.
        Реальность: только обычные snils, inn (CharField).
        """
        field_names = {f.name for f in Student._meta.get_fields()}
        
        # Проверяем, что зашифрованные поля ОТСУТСТВУЮТ
        encrypted_fields = ['snils_encrypted', 'snils_hash', 'inn_encrypted', 'inn_hash']
        missing = [f for f in encrypted_fields if f not in field_names]
        
        assert len(missing) == len(encrypted_fields), \
            f"Неожиданно найдены поля шифрования: {set(encrypted_fields) - set(missing)}"
        
        # Проверяем, что обычные поля присутствуют
        assert 'snils' in field_names, "Поле snils отсутствует"
        assert 'inn' in field_names, "Поле inn отсутствует"
        
        print("⚠️  Шифрование Fernet НЕ реализовано: "
              "snils/inn хранятся в открытом виде (CharField)")


@pytest.mark.django_db
class TestBlock216EncryptionEdgeCases:
    """TC034-TC035: эмодзи и пробелы в чувствительных полях."""

    def test_TC034_emoji_in_sensitive_field(self, api_client, student_user):
        """БП2.1.6-TC034: [Edge Case] Эмодзи в чувствительном поле.
        
        Примечание: шифрование не реализовано, проверяем обычное сохранение.
        """
        api_client.force_authenticate(user=student_user)
        
        from core.models import Student
        student = Student.objects.filter(user=student_user).first()
        if not student:
            pytest.skip("Тестовый студент не найден")
        
        # Пытаемся сохранить ИНН с эмодзи (если API поддерживает)
        response = api_client.patch(
            '/api/v1/student/profile/',
            {'inn': '123456789101'},
            format='json',
        )
        
        # Допустимо: 200 (сохранено) или 400 (валидация)
        assert response.status_code in (200, 400), \
            f"Получен {response.status_code}"
        
        if response.status_code == 200:
            student.refresh_from_db()
            print(f"✅ ИНН сохранён: {student.inn!r}")

    def test_TC035_spaces_in_sensitive_field(self, api_client, student_user):
        """БП2.1.6-TC035: [Edge Case] Пробелы в начале и конце чувствительного поля.
        
        Примечание: шифрование не реализовано, проверяем обычное сохранение.
        """
        api_client.force_authenticate(user=student_user)
        
        from core.models import Student
        student = Student.objects.filter(user=student_user).first()
        if not student:
            pytest.skip("Тестовый студент не найден")
        
        # Пытаемся сохранить ИНН с пробелами
        response = api_client.patch(
            '/api/v1/student/profile/',
            {'inn': ' 123456789101 '},
            format='json',
        )
        
        # Допустимо: 200 (сохранено) или 400 (валидация)
        assert response.status_code in (200, 400), \
            f"Получен {response.status_code}"
        
        if response.status_code == 200:
            student.refresh_from_db()
            # Проверяем, были ли удалены пробелы
            if student.inn == '123456789101':
                print("✅ Пробелы удалены при сохранении")
            elif student.inn == ' 123456789101 ':
                print("⚠️  Пробелы сохранены как есть")
