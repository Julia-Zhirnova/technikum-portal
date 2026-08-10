import re
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework.exceptions import AuthenticationFailed
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model

User = get_user_model()


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Кастомный сериализатор JWT с ролями и флагом смены пароля."""

    def validate_email(self, value):
        """БП 1.1-046: Валидация формата email на сервере.
        
        Использует django.core.validators.EmailValidator.
        Возвращает 400 Bad Request при невалидном формате.
        """
        from django.core.validators import validate_email
        from django.core.exceptions import ValidationError as DjangoValidationError
        
        if not value or not value.strip():
            raise serializers.ValidationError("Введите корректный email")
        
        try:
            validate_email(value.strip())
        except DjangoValidationError:
            raise serializers.ValidationError("Введите корректный email")
        
        return value.strip()


    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        from core.models import UserRole
        roles = list(UserRole.objects.filter(user=user).values_list('role__id_role', flat=True))
        token['roles'] = roles
        token['requires_password_change'] = user.requires_password_change
        token['password_version'] = getattr(user, 'password_version', 1)
        return token

    def validate(self, attrs):
        # БП 1.1.3: нормализация email (вход с любым регистром)
        # Поиск в БД — case-insensitive, чтобы не ломать существующие записи
        # в смешанном регистре (например, 'YVZhirnova@yandex.ru')
        email_input = (attrs.get('email') or '').strip()
        try:
            user = User.objects.get(email__iexact=email_input)
        except User.DoesNotExist:
            raise AuthenticationFailed(_("Неверный email или пароль"))
        except User.MultipleObjectsReturned:
            # Защита от перебора: не раскрываем наличие дубликатов
            raise AuthenticationFailed(_("Неверный email или пароль"))
        # ВАЖНО: подставляем оригинальный email из БД (сохраняем регистр),
        # иначе authenticate() внутри super().validate() не найдёт пользователя
        attrs['email'] = user.email

        if not user.is_active:
            raise AuthenticationFailed(_("Ваша учетная запись заблокирована. Обратитесь к администратору."))

        try:
            data = super().validate(attrs)
        except AuthenticationFailed:
            raise AuthenticationFailed(_("Неверный email или пароль"))

        from core.models import UserRole
        data['roles'] = list(UserRole.objects.filter(user=user).values_list('role__id_role', flat=True))
        data['requires_password_change'] = user.requires_password_change
        # БП 1.1.3: флаг для пользователей без ролей (фронтенд редиректит на /access-denied)
        data['no_roles'] = len(data['roles']) == 0
        data['password_version'] = getattr(user, 'password_version', 1)
        return data


class ForceChangePasswordSerializer(serializers.Serializer):
    """Валидатор для принудительной смены пароля."""
    new_password = serializers.CharField(write_only=True, required=True)
    confirm_password = serializers.CharField(write_only=True, required=True)

    def validate(self, attrs):
        user = self.context['request'].user
        password = attrs['new_password']

        # 1. Совпадение полей
        if attrs['new_password'] != attrs['confirm_password']:
            raise serializers.ValidationError({"confirm_password": "Пароли не совпадают."})

        # 2. Запрет на использование текущего пароля
        if user.check_password(password):
            raise serializers.ValidationError({"new_password": "Новый пароль не должен совпадать с текущим."})

        # 3. Проверка сложности (собираем все ошибки в массив)
        errors = []
        
        # 3.1 Минимальная длина (8 символов)
        if len(password) < 8:
            errors.append("Пароль должен содержать минимум 8 символов.")
        
        # 3.2 Максимальная длина (20 символов) — БП 1.2-TC045
        if len(password) > 20:
            errors.append("Длина пароля не должна превышать 20 символов.")
        
        # 3.3 Заглавная буква
        if not re.search(r'[A-Z]', password):
            errors.append("Пароль должен содержать хотя бы одну заглавную букву.")
        
        # 3.4 Цифра
        if not re.search(r'\d', password):
            errors.append("Пароль должен содержать хотя бы одну цифру.")
        
        # 3.5 Спецсимвол
        if not re.search(r'[^A-Za-z0-9]', password):
            errors.append("Пароль должен содержать хотя бы один спецсимвол.")
        
        # 3.6 Пробелы запрещены — БП 1.2-TC026
        if ' ' in password:
            errors.append("Пароль не должен содержать пробелы.")
        
        # 3.7 Проверка на популярные пароли — БП 1.2-TC017
        try:
            from django.contrib.auth.password_validation import CommonPasswordValidator
            CommonPasswordValidator().validate(password)
        except Exception:
            errors.append("Этот пароль слишком распространён. Используйте более сложный.")
        
        # 3.8 Проверка на персональную информацию — БП 1.2-TC018/019/020
        personal_info_errors = []
        
        # Email (полное совпадение, регистронезависимо)
        if user.email and password.lower().startswith(user.email.lower()):
            personal_info_errors.append("Пароль не должен содержать ваше имя или email.")
        
        # first_name (полное совпадение, регистронезависимо)
        if user.first_name and password.lower().startswith(user.first_name.lower()):
            personal_info_errors.append("Пароль не должен содержать ваше имя или email.")
        
        # last_name (полное совпадение, регистронезависимо)
        if user.last_name and password.lower().startswith(user.last_name.lower()):
            personal_info_errors.append("Пароль не должен содержать ваше имя или email.")
        
        # Добавляем только одну ошибку персональной информации (избегаем дублирования)
        if personal_info_errors:
            errors.append(personal_info_errors[0])

        # 4. Возвращаем все ошибки массивом — БП 1.2-TC030
        if errors:
            raise serializers.ValidationError({"new_password": errors})

        return attrs


# ============================================
# БП 1.4: Email-восстановление пароля — Serializers
# ============================================

class RecoveryRequestSerializer(serializers.Serializer):
    """Сериализатор запроса восстановления пароля (БП 1.4)."""
    email = serializers.EmailField(required=True)


class RecoveryConfirmSerializer(serializers.Serializer):
    """Сериализатор подтверждения восстановления пароля (БП 1.4)."""
    token = serializers.CharField(required=True, max_length=64)
    new_password = serializers.CharField(required=True, write_only=True)
    confirm_password = serializers.CharField(required=True, write_only=True)

    def validate(self, attrs):
        if attrs['new_password'] != attrs['confirm_password']:
            raise serializers.ValidationError({"confirm_password": "Пароли не совпадают."})
        
        # Проверка сложности (переиспользуем логику из ForceChangePasswordSerializer)
        password = attrs['new_password']
        errors = []
        
        if len(password) < 8:
            errors.append("Пароль должен содержать минимум 8 символов.")
        if len(password) > 20:
            errors.append("Длина пароля не должна превышать 20 символов.")
        if not re.search(r'[A-Z]', password):
            errors.append("Пароль должен содержать хотя бы одну заглавную букву.")
        if not re.search(r'\d', password):
            errors.append("Пароль должен содержать хотя бы одну цифру.")
        if not re.search(r'[^A-Za-z0-9]', password):
            errors.append("Пароль должен содержать хотя бы один спецсимвол.")
        if ' ' in password:
            errors.append("Пароль не должен содержать пробелы.")
        
        # CommonPasswordValidator
        try:
            from django.contrib.auth.password_validation import CommonPasswordValidator
            CommonPasswordValidator().validate(password)
        except Exception:
            errors.append("Этот пароль слишком распространён. Используйте более сложный.")
        
        if errors:
            raise serializers.ValidationError({"new_password": errors})
        
        return attrs
