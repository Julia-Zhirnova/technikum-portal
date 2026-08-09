import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from core.models import Role, UserRole

User = get_user_model()


@pytest.mark.django_db
class TestForcePasswordChange:
    """Тесты Функции 1.2: Принудительная смена пароля."""

    def _create_user_with_role(self, email='test@test.ru', password='OldPass123!'):
        """Хелпер: создаёт пользователя со ролью student."""
        user = User.objects.create_user(
            email=email,
            password=password,
            requires_password_change=True
        )
        role, _ = Role.objects.get_or_create(id_role='student', name='Студент')
        UserRole.objects.get_or_create(user=user, role=role)
        return user

    def test_force_change_password_success(self):
        """1. Успешная смена пароля: флаг becomes False."""
        user = self._create_user_with_role(email='force@test.ru')
        client = APIClient()
        client.force_authenticate(user=user)

        response = client.post('/api/auth/force-change-password/', {
            'new_password': 'NewSuperPass123!',
            'confirm_password': 'NewSuperPass123!'
        })

        assert response.status_code == 200
        user.refresh_from_db()
        assert user.requires_password_change is False
        assert user.check_password('NewSuperPass123!') is True

    def test_force_change_password_weak_password(self):
        """2. Слабый пароль "12345678" отклоняется."""
        user = self._create_user_with_role(email='weak@test.ru')
        client = APIClient()
        client.force_authenticate(user=user)

        response = client.post('/api/auth/force-change-password/', {
            'new_password': '12345678',
            'confirm_password': '12345678'
        })

        assert response.status_code == 400
        assert 'new_password' in response.data
        user.refresh_from_db()
        assert user.requires_password_change is True

    def test_force_change_password_same_as_current(self):
        """3. Пароль, совпадающий с текущим, отклоняется."""
        user = self._create_user_with_role(email='same@test.ru', password='OldPass123!')
        client = APIClient()
        client.force_authenticate(user=user)

        response = client.post('/api/auth/force-change-password/', {
            'new_password': 'OldPass123!',
            'confirm_password': 'OldPass123!'
        })

        assert response.status_code == 400
        assert 'Новый пароль не должен совпадать с текущим' in str(response.data)

    def test_force_change_password_mismatch(self):
        """4. Поля "Новый пароль" и "Подтверждение" не совпадают."""
        user = self._create_user_with_role(email='mismatch@test.ru')
        client = APIClient()
        client.force_authenticate(user=user)

        response = client.post('/api/auth/force-change-password/', {
            'new_password': 'NewSuperPass123!',
            'confirm_password': 'DifferentPass123!'
        })

        assert response.status_code == 400
        assert 'Пароли не совпадают' in str(response.data)

    def test_force_change_password_no_uppercase(self):
        """5. Пароль без заглавной буквы отклоняется."""
        user = self._create_user_with_role(email='noupper@test.ru')
        client = APIClient()
        client.force_authenticate(user=user)

        response = client.post('/api/auth/force-change-password/', {
            'new_password': 'newpassword123!',
            'confirm_password': 'newpassword123!'
        })

        assert response.status_code == 400
        assert 'заглавную' in str(response.data)

    def test_force_change_password_no_digit(self):
        """6. Пароль без цифры отклоняется."""
        user = self._create_user_with_role(email='nodigit@test.ru')
        client = APIClient()
        client.force_authenticate(user=user)

        response = client.post('/api/auth/force-change-password/', {
            'new_password': 'NewPassword!!',
            'confirm_password': 'NewPassword!!'
        })

        assert response.status_code == 400
        assert 'цифру' in str(response.data)

    def test_force_change_password_no_special(self):
        """7. Пароль без спецсимвола отклоняется."""
        user = self._create_user_with_role(email='nospecial@test.ru')
        client = APIClient()
        client.force_authenticate(user=user)

        response = client.post('/api/auth/force-change-password/', {
            'new_password': 'NewPassword123',
            'confirm_password': 'NewPassword123'
        })

        assert response.status_code == 400
        assert 'спецсимвол' in str(response.data)

    def test_force_change_password_unauthenticated(self):
        """8. Неаутентифицированный запрос отклоняется (403)."""
        client = APIClient()
        response = client.post('/api/auth/force-change-password/', {
            'new_password': 'NewSuperPass123!',
            'confirm_password': 'NewSuperPass123!'
        })
        assert response.status_code == 403


@pytest.mark.xdist_group("cache_sensitive")
class TestPasswordChangeSecurity:
    """Тесты безопасности при смене пароля (TC005-TC008)."""

    def test_TC005_invalidate_all_refresh_tokens(self, api_client, db):
        """TC005: После смены пароля все refresh-токены добавлены в blacklist."""
        from django.contrib.auth import get_user_model
        from rest_framework_simplejwt.tokens import RefreshToken
        from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken
        
        User = get_user_model()
        user = User.objects.create_user(
            email='tc005@test.ru',
            password='OldPassword123!',
            requires_password_change=True,
        )
        
        # Создаём 2 refresh-токена (имитация 2 устройств)
        refresh1 = RefreshToken.for_user(user)
        refresh2 = RefreshToken.for_user(user)
        
        # Меняем пароль
        api_client.force_authenticate(user=user)
        response = api_client.post(
            '/api/auth/force-change-password/',
            {'new_password': 'NewSuperPass123!', 'confirm_password': 'NewSuperPass123!'},
            format='json',
        )
        assert response.status_code == 200
        
        # Проверяем, что оба токена в blacklist
        blacklisted_count = BlacklistedToken.objects.filter(
            token__user=user
        ).count()
        assert blacklisted_count >= 2

    def test_TC006_old_access_token_invalid(self, api_client, db):
        """TC006: Старый access-токен невалиден после смены пароля."""
        from django.contrib.auth import get_user_model
        from rest_framework_simplejwt.tokens import AccessToken
        
        User = get_user_model()
        user = User.objects.create_user(
            email='tc006@test.ru',
            password='OldPassword123!',
            requires_password_change=True,
        )
        
        # Получаем старый access-токен
        old_access = AccessToken.for_user(user)
        
        # Меняем пароль
        api_client.force_authenticate(user=user)
        response = api_client.post(
            '/api/auth/force-change-password/',
            {'new_password': 'NewSuperPass123!', 'confirm_password': 'NewSuperPass123!'},
            format='json',
        )
        assert response.status_code == 200
        
        # Пытаемся использовать старый токен
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {old_access}')
        response = api_client.get('/api/user/profile/')
        assert response.status_code == 401
        # JsonResponse (Django) или Response (DRF) — читаем безопасно
        try:
            body = response.json()
        except Exception:
            body = getattr(response, 'data', {})
        assert body.get('code') == 'password_changed'

    def test_TC007_block_after_3_failed_attempts(self, api_client, db, mock_client_ip):
        """TC007: После 3 неудачных попыток → блокировка на 5 минут."""
        from django.contrib.auth import get_user_model
        
        User = get_user_model()
        user = User.objects.create_user(
            email='tc007@test.ru',
            password='OldPassword123!',
            requires_password_change=True,
        )
        
        api_client.force_authenticate(user=user)
        
        # 3 неудачные попытки (слабый пароль)
        for _ in range(3):
            api_client.post(
                '/api/auth/force-change-password/',
                {'new_password': '12345678', 'confirm_password': '12345678'},
                format='json',
            )
        
        # 4-я попытка → 429
        response = api_client.post(
            '/api/auth/force-change-password/',
            {'new_password': '12345678', 'confirm_password': '12345678'},
            format='json',
        )
        assert response.status_code == 429
        assert 'Слишком много попыток' in response.data.get('detail', '')

    def test_TC008_block_by_user_id_not_ip(self, api_client, db, mock_client_ip):
        """TC008: Блокировка по user_id, другой пользователь с тем же IP не заблокирован."""
        from django.contrib.auth import get_user_model
        
        User = get_user_model()
        user_a = User.objects.create_user(
            email='tc008a@test.ru',
            password='OldPassword123!',
            requires_password_change=True,
        )
        user_b = User.objects.create_user(
            email='tc008b@test.ru',
            password='OldPassword123!',
            requires_password_change=True,
        )
        
        # Блокируем user_a (3 неудачные попытки)
        api_client.force_authenticate(user=user_a)
        for _ in range(3):
            api_client.post(
                '/api/auth/force-change-password/',
                {'new_password': '12345678', 'confirm_password': '12345678'},
                format='json',
            )
        
        # user_b с тем же IP не заблокирован
        api_client.force_authenticate(user=user_b)
        response = api_client.post(
            '/api/auth/force-change-password/',
            {'new_password': 'NewSuperPass123!', 'confirm_password': 'NewSuperPass123!'},
            format='json',
        )
        assert response.status_code == 200  # Не 429

class TestForcePasswordChangeValidation:
    """БП 1.2: Валидация сложности пароля при принудительной смене."""

    def test_TC017_common_password_rejected(self, api_client, db):
        """TC017: Пароль из списка популярных → 400 Bad Request.
        
        Password1! проходит все проверки сложности (длина, заглавная, цифра, спецсимвол),
        но распознаётся Django CommonPasswordValidator как популярный ('password!').
        """
        # Создаём пользователя с requires_password_change=True
        from django.contrib.auth import get_user_model
        User = get_user_model()
        user = User.objects.create_user(
            email='test_common_pwd@luberteh.ru',
            password='OldPassword123!',
            first_name='Test',
            last_name='User',
            requires_password_change=True
        )
        
        url = '/api/auth/force-change-password/'
        data = {
            'new_password': 'Password1!',
            'confirm_password': 'Password1!'
        }
        api_client.force_authenticate(user=user)
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == 400
        assert 'new_password' in response.data
        assert any('распространён' in str(err).lower() or 'common' in str(err).lower() 
                   for err in response.data['new_password'])

    def test_TC018_password_contains_email(self, api_client, db):
        """TC018: Пароль содержит email → 400 Bad Request."""
        from django.contrib.auth import get_user_model
        User = get_user_model()
        user = User.objects.create_user(
            email='test_email_pwd@luberteh.ru',
            password='OldPassword123!',
            first_name='Test',
            last_name='User',
            requires_password_change=True
        )
        
        url = '/api/auth/force-change-password/'
        data = {
            'new_password': 'test_email_pwd@luberteh.ru1!',
            'confirm_password': 'test_email_pwd@luberteh.ru1!'
        }
        api_client.force_authenticate(user=user)
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == 400
        assert 'new_password' in response.data

    def test_TC019_password_contains_first_name(self, api_client, db):
        """TC019: Пароль содержит first_name → 400 Bad Request."""
        from django.contrib.auth import get_user_model
        User = get_user_model()
        user = User.objects.create_user(
            email='test_name_pwd@luberteh.ru',
            password='OldPassword123!',
            first_name='Test',
            last_name='User',
            requires_password_change=True
        )
        
        url = '/api/auth/force-change-password/'
        data = {
            'new_password': 'Test12345!',
            'confirm_password': 'Test12345!'
        }
        api_client.force_authenticate(user=user)
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == 400
        assert 'new_password' in response.data

    def test_TC020_password_contains_last_name(self, api_client, db):
        """TC020: Пароль содержит last_name → 400 Bad Request."""
        from django.contrib.auth import get_user_model
        User = get_user_model()
        user = User.objects.create_user(
            email='test_lastname_pwd@luberteh.ru',
            password='OldPassword123!',
            first_name='Test',
            last_name='Password',
            requires_password_change=True
        )
        
        url = '/api/auth/force-change-password/'
        data = {
            'new_password': 'Password123!',
            'confirm_password': 'Password123!'
        }
        api_client.force_authenticate(user=user)
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == 400
        assert 'new_password' in response.data

    def test_TC023_boundary_8_symbols_minimum(self, api_client, db):
        """TC023: Пароль ровно 8 символов (минимум) → 200 OK."""
        from django.contrib.auth import get_user_model
        User = get_user_model()
        user = User.objects.create_user(
            email='test_8symbols@luberteh.ru',
            password='OldPassword123!',
            first_name='Test',
            last_name='User',
            requires_password_change=True
        )
        
        url = '/api/auth/force-change-password/'
        data = {
            'new_password': 'Ab1!xxxx',  # ровно 8 символов
            'confirm_password': 'Ab1!xxxx'
        }
        api_client.force_authenticate(user=user)
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == 200

    def test_TC025_boundary_7_symbols_too_short(self, api_client, db):
        """TC025: Пароль 7 символов (меньше минимума) → 400 Bad Request."""
        from django.contrib.auth import get_user_model
        User = get_user_model()
        user = User.objects.create_user(
            email='test_7symbols@luberteh.ru',
            password='OldPassword123!',
            first_name='Test',
            last_name='User',
            requires_password_change=True
        )
        
        url = '/api/auth/force-change-password/'
        data = {
            'new_password': 'Ab1!xxx',  # 7 символов
            'confirm_password': 'Ab1!xxx'
        }
        api_client.force_authenticate(user=user)
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == 400
        assert 'new_password' in response.data

    def test_TC044_boundary_20_symbols_maximum(self, api_client, db):
        """TC044: Пароль ровно 20 символов (максимум) → 200 OK."""
        from django.contrib.auth import get_user_model
        User = get_user_model()
        user = User.objects.create_user(
            email='test_20symbols@luberteh.ru',
            password='OldPassword123!',
            first_name='Test',
            last_name='User',
            requires_password_change=True
        )
        
        url = '/api/auth/force-change-password/'
        data = {
            'new_password': 'A1!' + 'a' * 17,  # ровно 20 символов
            'confirm_password': 'A1!' + 'a' * 17
        }
        api_client.force_authenticate(user=user)
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == 200

    def test_TC045_boundary_21_symbols_too_long(self, api_client, db):
        """TC045: Пароль 21 символ (больше максимума) → 400 Bad Request."""
        from django.contrib.auth import get_user_model
        User = get_user_model()
        user = User.objects.create_user(
            email='test_21symbols@luberteh.ru',
            password='OldPassword123!',
            first_name='Test',
            last_name='User',
            requires_password_change=True
        )
        
        url = '/api/auth/force-change-password/'
        data = {
            'new_password': 'A1!' + 'a' * 18,  # 21 символ
            'confirm_password': 'A1!' + 'a' * 18
        }
        api_client.force_authenticate(user=user)
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == 400
        assert 'new_password' in response.data

    def test_TC026_password_contains_space(self, api_client, db):
        """TC026: Пароль содержит пробел → 400 Bad Request."""
        from django.contrib.auth import get_user_model
        User = get_user_model()
        user = User.objects.create_user(
            email='test_space_pwd@luberteh.ru',
            password='OldPassword123!',
            first_name='Test',
            last_name='User',
            requires_password_change=True
        )
        
        url = '/api/auth/force-change-password/'
        data = {
            'new_password': 'New Pass123!',
            'confirm_password': 'New Pass123!'
        }
        api_client.force_authenticate(user=user)
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == 400
        assert 'new_password' in response.data

    def test_TC030_multiple_validation_errors(self, api_client, db):
        """TC030: Возвращаются все ошибки валидации сразу (массив)."""
        from django.contrib.auth import get_user_model
        User = get_user_model()
        user = User.objects.create_user(
            email='test_multiple_errors@luberteh.ru',
            password='OldPassword123!',
            first_name='Test',
            last_name='User',
            requires_password_change=True
        )
        
        url = '/api/auth/force-change-password/'
        data = {
            'new_password': '1234567',  # 7 символов, без заглавной, без спецсимвола
            'confirm_password': '1234567'
        }
        api_client.force_authenticate(user=user)
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == 400
        assert 'new_password' in response.data
        errors = response.data['new_password']
        
        # Должно быть минимум 3 ошибки: длина, заглавная буква, спецсимвол
        assert len(errors) >= 3

    def test_TC028_empty_confirm_password(self, api_client, db):
        """TC028: Пустое поле confirm_password → 400 Bad Request."""
        from django.contrib.auth import get_user_model
        User = get_user_model()
        user = User.objects.create_user(
            email='test_empty_confirm@luberteh.ru',
            password='OldPassword123!',
            first_name='Test',
            last_name='User',
            requires_password_change=True
        )
        
        url = '/api/auth/force-change-password/'
        data = {
            'new_password': 'NewPass123!',
            'confirm_password': ''
        }
        api_client.force_authenticate(user=user)
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == 400
        assert 'confirm_password' in response.data

    def test_TC029_missing_confirm_password(self, api_client, db):
        """TC029: Отсутствует поле confirm_password → 400 Bad Request."""
        from django.contrib.auth import get_user_model
        User = get_user_model()
        user = User.objects.create_user(
            email='test_missing_confirm@luberteh.ru',
            password='OldPassword123!',
            first_name='Test',
            last_name='User',
            requires_password_change=True
        )
        
        url = '/api/auth/force-change-password/'
        data = {
            'new_password': 'NewPass123!'
            # confirm_password отсутствует
        }
        api_client.force_authenticate(user=user)
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == 400
        assert 'confirm_password' in response.data
