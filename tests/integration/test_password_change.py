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

    def test_TC007_block_after_3_failed_attempts(self, api_client, db):
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

    def test_TC008_block_by_user_id_not_ip(self, api_client, db):
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
