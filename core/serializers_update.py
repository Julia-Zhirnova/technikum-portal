from rest_framework import serializers
from .models import (
    Student, User, Passport, Health, Military, Family, FamilyMember, Profile,
    EducationInstitution
)


class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'middle_name', 'email']
        extra_kwargs = {
            'first_name': {'required': False, 'allow_blank': True},
            'last_name': {'required': False, 'allow_blank': True},
            'middle_name': {'required': False, 'allow_blank': True},
            'email': {
                'required': False, 
                'allow_blank': True,
                'validators': [],  # Отключаем проверку уникальности
            },
        }


class PassportUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Passport
        fields = [
            'is_foreigner', 'citizenship', 'series_number', 'issue_date',
            'issuer', 'unit_code', 'region_city', 'address_detail',
            'fact_region', 'fact_detail', 'temp_reg', 'absence_reason'
        ]
        extra_kwargs = {
            'is_foreigner': {'required': False},
            'temp_reg': {'required': False},
            'issue_date': {'required': False},
            'citizenship': {'required': False, 'allow_blank': True},
            'series_number': {'required': False, 'allow_blank': True},
            'issuer': {'required': False, 'allow_blank': True},
            'unit_code': {'required': False, 'allow_blank': True},
            'region_city': {'required': False, 'allow_blank': True},
            'address_detail': {'required': False, 'allow_blank': True},
            'fact_region': {'required': False, 'allow_blank': True},
            'fact_detail': {'required': False, 'allow_blank': True},
            'absence_reason': {'required': False, 'allow_blank': True},
        }


class HealthUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Health
        fields = [
            'status', 'diagnosis', 'oms_number', 'oms_date',
            'oms_issuer', 'oms_absence_reason'
        ]
        extra_kwargs = {
            'status': {'required': False, 'allow_blank': True},
            'diagnosis': {'required': False, 'allow_blank': True},
            'oms_number': {'required': False, 'allow_blank': True},
            'oms_issuer': {'required': False, 'allow_blank': True},
            'oms_absence_reason': {'required': False, 'allow_blank': True},
            'oms_date': {'required': False},
        }


class MilitaryUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Military
        fields = [
            'registration_number', 'commissariat', 'issue_date',
            'fitness_category', 'absence_reason'
        ]
        extra_kwargs = {
            'registration_number': {'required': False, 'allow_blank': True},
            'commissariat': {'required': False, 'allow_blank': True},
            'fitness_category': {'required': False, 'allow_blank': True},
            'absence_reason': {'required': False, 'allow_blank': True},
            'issue_date': {'required': False},
        }


class FamilyMemberUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = FamilyMember
        fields = [
            'id_member', 'relation', 'full_name', 'birth_date',
            'education', 'workplace', 'phone', 'is_pensioner',
            'is_svo', 'is_priority_contact'
        ]
        extra_kwargs = {
            'id_member': {'required': False},
            'is_pensioner': {'required': False},
            'is_svo': {'required': False},
            'is_priority_contact': {'required': False},
            'birth_date': {'required': False},
            'relation': {'required': False, 'allow_blank': True},
            'full_name': {'required': False, 'allow_blank': True},
            'education': {'required': False, 'allow_blank': True},
            'workplace': {'required': False, 'allow_blank': True},
            'phone': {'required': False, 'allow_blank': True},
        }


class FamilyUpdateSerializer(serializers.ModelSerializer):
    members = FamilyMemberUpdateSerializer(many=True, required=False)
    
    class Meta:
        model = Family
        fields = [
            'minors_count', 'adults_count', 'status', 'housing_type', 'members'
        ]
        extra_kwargs = {
            'minors_count': {'required': False},
            'adults_count': {'required': False},
            'status': {'required': False, 'allow_blank': True},
            'housing_type': {'required': False, 'allow_blank': True},
        }


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
        extra_kwargs = {
            'programming_langs': {'required': False, 'allow_blank': True},
            'hobbies': {'required': False, 'allow_blank': True},
            'extra_edu': {'required': False, 'allow_blank': True},
            'sports_ranks': {'required': False, 'allow_blank': True},
            'character_behavior': {'required': False, 'allow_blank': True},
            # JSON поля
            'it_skills': {'required': False},
            'creative_skills': {'required': False},
            'school_participation': {'required': False},
            'college_participation': {'required': False},
            'achievements': {'required': False},
            'social_networks': {'required': False},
            'motivation_college': {'required': False},
            'motivation_specialty': {'required': False},
            'desired_participation': {'required': False},
            'foreign_langs': {'required': False},
            'drivers_license': {'required': False},
        }


class EducationUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = EducationInstitution
        fields = ['name', 'type', 'profile', 'graduation_date']
        extra_kwargs = {
            'name': {'required': False, 'allow_blank': True},
            'type': {'required': False, 'allow_blank': True},
            'profile': {'required': False, 'allow_blank': True},
            'graduation_date': {'required': False},
        }


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
    education = EducationUpdateSerializer(required=False, allow_null=True)
    
    def update(self, instance, validated_data):
        # Обновляем данные пользователя
        user_data = validated_data.pop('user', None)
        if user_data:
            user = instance.user
            for attr, value in user_data.items():
                if value is not None:
                    setattr(user, attr, value)
            user.save()
        
        # Обновляем основные поля студента
        for attr in ['phone', 'inn', 'birth_place']:
            if attr in validated_data:
                value = validated_data.pop(attr)
                if value is not None:
                    setattr(instance, attr, value)
        
        # Обновляем паспорт
        passport_data = validated_data.pop('passport', None)
        if passport_data:
            if not instance.passport:
                instance.passport = Passport.objects.create()
            for attr, value in passport_data.items():
                if value is not None:
                    setattr(instance.passport, attr, value)
            instance.passport.save()
        
        # Обновляем здоровье
        health_data = validated_data.pop('health', None)
        if health_data:
            if not instance.health:
                instance.health = Health.objects.create()
            for attr, value in health_data.items():
                if value is not None:
                    setattr(instance.health, attr, value)
            instance.health.save()
        
        # Обновляем воинский учет
        military_data = validated_data.pop('military', None)
        if military_data:
            if not instance.military:
                instance.military = Military.objects.create()
            for attr, value in military_data.items():
                if value is not None:
                    setattr(instance.military, attr, value)
            instance.military.save()
        
        # Обновляем семью
        family_data = validated_data.pop('family', None)
        if family_data:
            if not instance.family:
                instance.family = Family.objects.create()
            
            for attr in ['minors_count', 'adults_count', 'status', 'housing_type']:
                if attr in family_data:
                    value = family_data[attr]
                    if value is not None:
                        setattr(instance.family, attr, value)
            
            members_data = family_data.pop('members', [])
            if members_data:
                instance.family.familymember_set.all().delete()
                for member_data in members_data:
                    member_data.pop('id_member', None)
                    member_data = {k: v for k, v in member_data.items() if v is not None}
                    if member_data:
                        FamilyMember.objects.create(family=instance.family, **member_data)
            
            instance.family.save()
        
        # Обновляем профиль
        profile_data = validated_data.pop('profile', None)
        if profile_data:
            if not instance.profile:
                instance.profile = Profile.objects.create()
            for attr, value in profile_data.items():
                if value is not None:
                    setattr(instance.profile, attr, value)
            instance.profile.save()
        
        # Обновляем образование
        education_data = validated_data.pop('education', None)
        if education_data:
            if not instance.education:
                instance.education = EducationInstitution.objects.create()
            for attr, value in education_data.items():
                if value is not None:
                    setattr(instance.education, attr, value)
            instance.education.save()
        
        instance.save()
        return instance
