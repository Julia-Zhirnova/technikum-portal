from rest_framework import serializers
from .models import (
    Student, User, Passport, Health, Military, Family, FamilyMember, Profile,
    EducationInstitution
)


class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'middle_name', 'email']


class PassportUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Passport
        fields = [
            'is_foreigner', 'citizenship', 'series_number', 'issue_date',
            'issuer', 'unit_code', 'region_city', 'address_detail',
            'fact_region', 'fact_detail', 'temp_reg', 'absence_reason'
        ]


class HealthUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Health
        fields = [
            'status', 'diagnosis', 'oms_number', 'oms_date',
            'oms_issuer', 'oms_absence_reason'
        ]


class MilitaryUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Military
        fields = [
            'registration_number', 'commissariat', 'issue_date',
            'fitness_category', 'absence_reason'
        ]


class FamilyMemberUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = FamilyMember
        fields = [
            'id_member', 'relation', 'full_name', 'birth_date',
            'education', 'workplace', 'phone', 'is_pensioner',
            'is_svo', 'is_priority_contact'
        ]


class FamilyUpdateSerializer(serializers.ModelSerializer):
    members = FamilyMemberUpdateSerializer(many=True, required=False)
    
    class Meta:
        model = Family
        fields = [
            'minors_count', 'adults_count', 'status', 'housing_type', 'members'
        ]


class ProfileUpdateSerializer(serializers.ModelSerializer):
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
    class Meta:
        model = EducationInstitution
        fields = ['name', 'type', 'profile', 'graduation_date']


class StudentProfileUpdateSerializer(serializers.Serializer):
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
            print(f"✅ Паспорт обновлен: {passport.series_number}")
        
        # Обновляем здоровье
        health_data = validated_data.pop('health', None)
        if health_data and instance.health:
            health = instance.health
            for attr, value in health_data.items():
                setattr(health, attr, value)
            health.save()
            print(f"✅ Здоровье обновлено: {health.status}")
        
        # Обновляем воинский учет
        military_data = validated_data.pop('military', None)
        if military_data and instance.military:
            military = instance.military
            for attr, value in military_data.items():
                setattr(military, attr, value)
            military.save()
            print(f"✅ Военный учет обновлен: {military.registration_number}")
        
        # Обновляем семью
        family_data = validated_data.pop('family', None)
        if family_data and instance.family:
            family = instance.family
            # Обновляем основные поля семьи
            for attr in ['minors_count', 'adults_count', 'status', 'housing_type']:
                if attr in family_data:
                    setattr(family, attr, family_data[attr])
            
            # Обновляем членов семьи
            members_data = family_data.get('members', [])
            if members_data:
                # Удаляем старых членов семьи
                family.familymember_set.all().delete()
                # Создаем новых
                for member_data in members_data:
                    member_data.pop('id_member', None)  # Удаляем id, если есть
                    FamilyMember.objects.create(family=family, **member_data)
            
            family.save()
            print(f"✅ Семья обновлена")
        
        # Обновляем профиль
        profile_data = validated_data.pop('profile', None)
        if profile_data and instance.profile:
            profile = instance.profile
            for attr, value in profile_data.items():
                setattr(profile, attr, value)
            profile.save()
            print(f"✅ Профиль обновлен")
        
        # Обновляем образование
        education_data = validated_data.pop('education', None)
        if education_data and instance.education:
            education = instance.education
            for attr, value in education_data.items():
                setattr(education, attr, value)
            education.save()
            print(f"✅ Образование обновлено")
        
        instance.save()
        print(f"✅ Студент сохранен")
        return instance
