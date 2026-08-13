from django.test import TestCase

# Create your tests here.

# ============================================
# БП 1.1: Brute Force Protection Tests
# ============================================
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.cache import cache
from rest_framework.test import APIClient
from unittest.mock import patch

User = get_user_model()

class RoleBasedRoutingTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.student = User.objects.create_user(
            email='student@test.ru',
            password='StudentPass123!'
        )
        self.teacher = User.objects.create_user(
            email='teacher@test.ru',
            password='TeacherPass123!'
        )
        self.admin = User.objects.create_user(
            email='admin@test.ru',
            password='AdminPass123!'
        )
        from core.models import Role, UserRole
        student_role, _ = Role.objects.get_or_create(id_role='student', defaults={'name': 'Студент'})
        teacher_role, _ = Role.objects.get_or_create(id_role='teacher', defaults={'name': 'Преподаватель'})
        admin_role, _ = Role.objects.get_or_create(id_role='admin', defaults={'name': 'Администратор'})
        curator_role, _ = Role.objects.get_or_create(id_role='curator', defaults={'name': 'Куратор'})
        UserRole.objects.get_or_create(user=self.student, role=student_role)
        UserRole.objects.get_or_create(user=self.teacher, role=teacher_role)
        UserRole.objects.get_or_create(user=self.teacher, role=curator_role)
        UserRole.objects.get_or_create(user=self.admin, role=admin_role)
    
    def test_student_routing(self):
        response = self.client.post('/api/token/', {
            'email': 'student@test.ru',
            'password': 'StudentPass123!'
        })
        self.assertEqual(response.status_code, 200)
        roles = response.data.get('roles', [])
        self.assertIn('student', roles)
    
    def test_teacher_with_multiple_roles(self):
        response = self.client.post('/api/token/', {
            'email': 'teacher@test.ru',
            'password': 'TeacherPass123!'
        })
        self.assertEqual(response.status_code, 200)
        roles = response.data.get('roles', [])
        self.assertIn('teacher', roles)
        self.assertIn('curator', roles)
    
    def test_admin_routing(self):
        response = self.client.post('/api/token/', {
            'email': 'admin@test.ru',
            'password': 'AdminPass123!'
        })
        self.assertEqual(response.status_code, 200)
        roles = response.data.get('roles', [])
        self.assertIn('admin', roles)
    
    def test_user_without_roles(self):
        user_no_roles = User.objects.create_user(
            email='nobody@test.ru',
            password='NoRolesPass123!'
        )
        response = self.client.post('/api/token/', {
            'email': 'nobody@test.ru',
            'password': 'NoRolesPass123!'
        })
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data.get('no_roles', False))
        self.assertEqual(len(response.data.get('roles', [])), 0)

# ============================================
# БП 1.1: Email Validation Tests
# ============================================
class EmailValidationTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email='valid@test.ru',
            password='ValidPass123!'
        )
    
    def test_invalid_email_format(self):
        response = self.client.post('/api/token/', {
            'email': 'invalid-email',
            'password': 'ValidPass123!'
        })
        self.assertEqual(response.status_code, 400)
        self.assertIn('email', response.data)
    
    def test_empty_email(self):
        response = self.client.post('/api/token/', {
            'email': '',
            'password': 'ValidPass123!'
        })
        self.assertEqual(response.status_code, 400)
        self.assertIn('email', response.data)
    
    def test_case_insensitive_login(self):
        response = self.client.post('/api/token/', {
            'email': 'VALID@TEST.RU',
            'password': 'ValidPass123!'
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn('access', response.data)
    
    def test_email_with_spaces_trimmed(self):
        response = self.client.post('/api/token/', {
            'email': '  valid@test.ru  ',
            'password': 'ValidPass123!'
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn('access', response.data)

# ============================================
# БП 1.1: Brute Force Protection Tests (FIXED)
# ============================================
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.cache import cache
from rest_framework.test import APIClient
from unittest.mock import patch

User = get_user_model()



# ============================================
# БП 1.1: Brute Force Protection Tests (FINAL FIX)
# ============================================
from django.test import TestCase, override_settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from rest_framework.test import APIClient
from unittest.mock import patch, MagicMock

User = get_user_model()



# ============================================
# БП 1.1: Brute Force Protection Tests (FINAL)
# ============================================
from django.test import TestCase, override_settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from rest_framework.test import APIClient
from unittest.mock import patch, MagicMock
import json

User = get_user_model()



# ============================================
# БП 1.1: Brute Force Protection Tests (FINAL)
# ============================================
from django.test import TestCase, override_settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from rest_framework.test import APIClient
from unittest.mock import patch, MagicMock
import json

User = get_user_model()

class BruteForceProtectionTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email='test@example.com',
            password='ValidPass123!',
            is_active=True
        )
        cache.clear()
    
    @override_settings(CACHES={
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        },
        'brute_force': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
            'LOCATION': 'brute_force',
        }
    })
    def test_bruteforce_after_5_attempts_requires_captcha(self):
        """[1.1-022] После 5 неудачных попыток требуется капча."""
        from django.test import Client
        
        client = Client()
        url = '/api/token/'
        data = json.dumps({'email': 'test@example.com', 'password': 'wrongpassword'})
        
        # Делаем 5 неудачных попыток
        for i in range(5):
            response = client.post(url, data, content_type='application/json')
            self.assertEqual(response.status_code, 401)
        
        # 6-я попытка должна вернуть require_captcha
        response = client.post(url, data, content_type='application/json')
        self.assertEqual(response.status_code, 401)
        response_data = json.loads(response.content)
        self.assertTrue(
            response_data.get('require_captcha', False),
            f"Expected require_captcha=True, got {response_data}"
        )
    
    @override_settings(CACHES={
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        },
        'brute_force': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
            'LOCATION': 'brute_force',
        }
    })
    def test_bruteforce_after_10_attempts_blocked(self):
        """[1.1-023] После 10 неудачных попыток блокировка на 15 минут (429)."""
        from django.test import Client
        
        client = Client()
        url = '/api/token/'
        data = json.dumps({'email': 'test@example.com', 'password': 'wrongpassword'})
        
        # Делаем 10 неудачных попыток (последняя 10-я уже возвращает 429)
        for i in range(10):
            response = client.post(url, data, content_type='application/json')
            # 10-я попытка уже должна вернуть 429
            if i == 9:
                self.assertEqual(response.status_code, 429)
                response_data = json.loads(response.content)
                # Проверяем русское сообщение о блокировке
                detail = response_data.get('detail', '').lower()
                self.assertTrue(
                    'слишком много попыток' in detail or 
                    'повторите через' in detail or
                    'blocked' in detail,
                    f"Expected block message, got: {detail}"
                )
            else:
                self.assertEqual(response.status_code, 401)
        
        # 11-я попытка тоже должна вернуть 429
        response = client.post(url, data, content_type='application/json')
        self.assertEqual(response.status_code, 429)
        response_data = json.loads(response.content)
        detail = response_data.get('detail', '').lower()
        self.assertTrue(
            'слишком много попыток' in detail or 
            'повторите через' in detail or
            'blocked' in detail,
            f"Expected block message, got: {detail}"
        )
    
    @override_settings(CACHES={
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        },
        'brute_force': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
            'LOCATION': 'brute_force',
        }
    })
    def test_successful_login_resets_attempts(self):
        """[1.1-024] Успешный вход сбрасывает счётчик попыток."""
        from django.test import Client
        
        client = Client()
        url = '/api/token/'
        wrong_data = json.dumps({'email': 'test@example.com', 'password': 'wrongpassword'})
        correct_data = json.dumps({'email': 'test@example.com', 'password': 'ValidPass123!'})
        
        # 3 неудачные попытки
        for i in range(3):
            response = client.post(url, wrong_data, content_type='application/json')
            self.assertEqual(response.status_code, 401)
        
        # Успешный вход
        response = client.post(url, correct_data, content_type='application/json')
        self.assertEqual(response.status_code, 200)
        
        # Следующая неудачная попытка не должна требовать капчу
        response = client.post(url, wrong_data, content_type='application/json')
        self.assertEqual(response.status_code, 401)
        response_data = json.loads(response.content)
        self.assertFalse(response_data.get('require_captcha', False))
