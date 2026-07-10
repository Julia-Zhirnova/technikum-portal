#!/usr/bin/env python
"""Скрипт для добавления сериализаторов обновления в core/serializers.py"""

import os

# Путь к файлу serializers.py
serializers_path = 'core/serializers.py'

# Проверяем, существует ли файл
if not os.path.exists(serializers_path):
    print(f"❌ Файл {serializers_path} не найден")
    exit(1)

# Читаем текущее содержимое
with open(serializers_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Проверяем, есть ли уже StudentProfileUpdateSerializer
if 'StudentProfileUpdateSerializer' in content:
    print("✅ StudentProfileUpdateSerializer уже есть в serializers.py")
    exit(0)

print("📝 Добавляем сериализаторы обновления...")

# Код для добавления
update_code = '''

# ==============================================================================
# СЕРИАЛИЗАТОРЫ ДЛЯ ОБНОВЛЕНИЯ ПРОФИЛЯ
# ==============================================================================

class UserUpdateSerializer(serializers.ModelSerializer):
    """Сериализатор для обновления данных пользователя."""
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'middle_name', 'email']


class PassportUpdateSerializer(serializers.ModelSerializer):
    """Сериализатор для обновления паспорта."""
    class Meta:
        model = Passport
        fields = [
            'is_foreigner', 'citizenship', 'series_number', 'issue_date',
            'issuer', 'unit_code', 'region_city', 'address_detail',
            'fact_region', 'fact_detail', 'temp_reg', 'absence_reason'
        ]


class HealthUpdateSerializer(serializers.ModelSerializer):
    """Сериализатор для обновления здоровья."""
    class Meta:
        model = Health
        fields = [
            'status', 'diagnosis', 'oms_number', 'oms_date',
            'oms_issuer', 'oms_absence_reason'
        ]


class MilitaryUpdateSerializer(serializers.ModelSerializer):
    """Сериализатор для обновления воинского учета."""
    class Meta:
        model = Military
        fields = [
            'registration_number', 'commissariat', 'issue_date',
            'fitness_category', 'absence_reason'
        ]


class FamilyMemberUpdateSerializer(serializers.ModelSerializer):
    """Сериализатор для обновления члена семьи."""
    class Meta:
        model = FamilyMember
        fields = [
            'id_member', 'relation', 'full_name', 'birth_date',
            'education', 'workplace', 'phone', 'is_pensioner',
            'is_svo', 'is_priority_contact'
        ]


class FamilyUpdateSerializer(serializers.ModelSerializer):
    """Сериализатор для обновления семьи."""
    members = FamilyMemberUpdateSerializer(many=True, required=False)
    
    class Meta:
        model = Family
        fields = [
            'minors_count', 'adults_count', 'status', 'housing_type', 'members'
        ]
    
    def update(self, instance, validated_data):
        members_data = validated_data.pop('members', None)
        
        # Обновляем основные поля семьи
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Обновляем членов семьи
        if members_data is not None:
            # Удаляем старых членов семьи
            instance.familymember_set.all().delete()
            
            # Создаем новых
            for member_data in members_data:
                FamilyMember.objects.create(family=instance, **member_data)
        
        return instance


class ProfileUpdateSerializer(serializers.ModelSerializer):
    """Сериализатор для обновления профиля."""
    class Meta:
        model = Profile
        fields = [
            'it_skills', 'programming_langs', 'creative_skills',
            'school_participation', 'college_participation', 'achievements',
            'hobbies', 'extra_edu', 'social_networks', 'motivation_college',
            'motivation_specialty', 'desired_participation', 'foreign_langs',
            'drivers_license', 'sports_ranks', 'character_behavior'
        ]


class EducationUpdateSerializer(serializers.ModelSerializer):
    """Сериализатор для обновления образования."""
    class Meta:
        model = EducationInstitution
        fields = ['name', 'type', 'profile', 'graduation_date']


class StudentProfileUpdateSerializer(serializers.Serializer):
    """Главный сериализатор для обновления полного профиля студента."""
    user = UserUpdateSerializer(required=False)
    phone = serializers.CharField(required=False, allow_blank=True)
    inn = serializers.CharField(required=False, allow_blank=True)
    birth_place = serializers.CharField(required=False, allow_blank=True)
    passport = PassportUpdateSerializer(required=False)
    health = HealthUpdateSerializer(required=False)
    military = MilitaryUpdateSerializer(required=False)
    family = FamilyUpdateSerializer(required=False)
    profile = ProfileUpdateSerializer(required=False)
    education = EducationUpdateSerializer(required=False)
    
    def update(self, instance, validated_data):
        # Обновляем данные пользователя
        user_data = validated_data.pop('user', None)
        if user_data:
            user = instance.user
            for attr, value in user_data.items():
                setattr(user, attr, value)
            user.save()
        
        # Обновляем основные поля студента
        for attr in ['phone', 'inn', 'birth_place']:
            if attr in validated_data:
                setattr(instance, attr, validated_data.pop(attr))
        
        # Обновляем паспорт
        passport_data = validated_data.pop('passport', None)
        if passport_data and instance.passport:
            passport = instance.passport
            for attr, value in passport_data.items():
                setattr(passport, attr, value)
            passport.save()
        
        # Обновляем здоровье
        health_data = validated_data.pop('health', None)
        if health_data and instance.health:
            health = instance.health
            for attr, value in health_data.items():
                setattr(health, attr, value)
            health.save()
        
        # Обновляем воинский учет
        military_data = validated_data.pop('military', None)
        if military_data and instance.military:
            military = instance.military
            for attr, value in military_data.items():
                setattr(military, attr, value)
            military.save()
        
        # Обновляем семью
        family_data = validated_data.pop('family', None)
        if family_data and instance.family:
            family = instance.family
            family_serializer = FamilyUpdateSerializer(family, data=family_data, partial=True)
            family_serializer.is_valid(raise_exception=True)
            family_serializer.save()
        
        # Обновляем профиль
        profile_data = validated_data.pop('profile', None)
        if profile_data and instance.profile:
            profile = instance.profile
            for attr, value in profile_data.items():
                setattr(profile, attr, value)
            profile.save()
        
        # Обновляем образование
        education_data = validated_data.pop('education', None)
        if education_data and instance.education:
            education = instance.education
            for attr, value in education_data.items():
                setattr(education, attr, value)
            education.save()
        
        instance.save()
        return instance
'''

# Добавляем код в конец файла
with open(serializers_path, 'a', encoding='utf-8') as f:
    f.write(update_code)

print("✅ Сериализаторы обновления успешно добавлены в core/serializers.py")
print("\nТеперь запустите:")
print("  python manage.py runserver 0.0.0.0:8000")
