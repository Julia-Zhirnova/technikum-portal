from rest_framework import serializers
from .models import (
    User, Student, Group, Statement, StatementGrade,
    StudentRequest, Notification,
    Passport, Health, Military, Family, FamilyMember, Profile,
    EducationInstitution,
)

# ==============================================================================
# СЕРИАЛИЗАТОРЫ ДЛЯ ПРОФИЛЯ СТУДЕНТА
# ==============================================================================

class PassportSerializer(serializers.ModelSerializer):
    """Сериализатор паспорта."""
    class Meta:
        model = Passport
        fields = (
            'id_passport', 'is_foreigner', 'citizenship', 'series_number',
            'issue_date', 'issuer', 'unit_code', 'region_city',
            'address_detail', 'fact_region', 'fact_detail', 'temp_reg',
            'absence_reason', 'file_path',
        )
        read_only_fields = ('id_passport',)


class HealthSerializer(serializers.ModelSerializer):
    """Сериализатор здоровья."""
    class Meta:
        model = Health
        fields = (
            'id_health', 'status', 'diagnosis', 'diagnosis_scan',
            'oms_number', 'oms_date', 'oms_issuer', 'oms_scan',
            'oms_absence_reason',
        )
        read_only_fields = ('id_health',)


class MilitarySerializer(serializers.ModelSerializer):
    """Сериализатор воинского учёта."""
    class Meta:
        model = Military
        fields = (
            'id_military', 'registration_number', 'commissariat',
            'issue_date', 'fitness_category', 'absence_reason', 'file_path',
        )
        read_only_fields = ('id_military',)


class FamilyMemberSerializer(serializers.ModelSerializer):
    """Сериализатор члена семьи."""
    class Meta:
        model = FamilyMember
        fields = (
            'id_member', 'relation', 'full_name', 'birth_date',
            'education', 'workplace', 'phone', 'is_pensioner',
            'is_svo', 'is_priority_contact',
        )
        read_only_fields = ('id_member',)


class FamilySerializer(serializers.ModelSerializer):
    """Сериализатор семьи с членами."""
    members = FamilyMemberSerializer(source='familymember_set', many=True, read_only=True)
    
    class Meta:
        model = Family
        fields = (
            'id_family', 'minors_count', 'adults_count',
            'status', 'housing_type', 'members',
        )
        read_only_fields = ('id_family',)


class EducationInstitutionSerializer(serializers.ModelSerializer):
    """Сериализатор предыдущего образования."""
    class Meta:
        model = EducationInstitution
        fields = (
            'id_institution', 'name', 'type', 'profile', 'graduation_date',
        )
        read_only_fields = ('id_institution',)


class ProfileSerializer(serializers.ModelSerializer):
    """Сериализатор профиля студента (хобби, навыки и т.д.)."""
    class Meta:
        model = Profile
        fields = (
            'id_profile', 'it_skills', 'programming_langs', 'creative_skills',
            'school_participation', 'college_participation', 'achievements',
            'hobbies', 'extra_edu', 'social_networks', 'motivation_college',
            'motivation_specialty', 'desired_participation', 'foreign_langs',
            'drivers_license', 'sports_ranks', 'character_behavior',
        )
        read_only_fields = ('id_profile',)


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор пользователя (только публичные поля)."""
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = (
            'id_user', 'email', 'last_name', 'first_name', 'middle_name',
            'full_name',
        )
        read_only_fields = ('id_user', 'email')
    
    def get_full_name(self, obj):
        return obj.get_full_name()


class StudentProfileSerializer(serializers.ModelSerializer):
    """
    Полный сериализатор студента для личного кабинета.
    Возвращает все связанные данные одним запросом.
    """
    user = UserSerializer(read_only=True)
    group_name = serializers.CharField(source='group.id_group', read_only=True)
    passport = PassportSerializer(read_only=True)
    health = HealthSerializer(read_only=True)
    military = MilitarySerializer(read_only=True)
    family = FamilySerializer(read_only=True)
    education = EducationInstitutionSerializer(read_only=True)
    profile = ProfileSerializer(read_only=True)
    
    # Вычисляемые поля
    age = serializers.SerializerMethodField()
    age_status = serializers.SerializerMethodField()
    completion_percentage = serializers.SerializerMethodField()
    
    class Meta:
        model = Student
        fields = (
            'snils', 'user', 'group_name', 'birth_date', 'gender',
            'birth_place', 'phone', 'inn', 'pd_consent', 'pd_consent_date',
            'status', 'last_change', 'photo_path', 'study_plan', 'dual_edu',
            'snils_file', 'inn_file',
            'passport', 'health', 'military', 'family', 'education', 'profile',
            'age', 'age_status', 'completion_percentage',
        )
        read_only_fields = (
            'snils', 'status', 'last_change', 'group_name',
        )
    
    def get_age(self, obj):
        """Вычисляем возраст студента."""
        if not obj.birth_date:
            return None
        from datetime import date
        today = date.today()
        age = today.year - obj.birth_date.year
        if (today.month, today.day) < (obj.birth_date.month, obj.birth_date.day):
            age -= 1
        return age
    
    def get_age_status(self, obj):
        """Совершеннолетний или нет."""
        age = self.get_age(obj)
        if age is None:
            return None
        return "Совершеннолетний" if age >= 18 else "Несовершеннолетний"
    
    def get_completion_percentage(self, obj):
        """Вычисляем процент заполненности анкеты."""
        total_fields = 0
        filled_fields = 0
        
        # Основные поля студента
        student_fields = [
            obj.phone, obj.inn, obj.birth_place, obj.photo_path,
        ]
        total_fields += len(student_fields)
        filled_fields += sum(1 for f in student_fields if f)
        
        # Паспорт
        if obj.passport:
            passport_fields = [
                obj.passport.series_number, obj.passport.issue_date,
                obj.passport.issuer, obj.passport.address_detail,
            ]
            total_fields += len(passport_fields)
            filled_fields += sum(1 for f in passport_fields if f)
        
        # Здоровье
        if obj.health:
            total_fields += 1
            if obj.health.oms_number:
                filled_fields += 1
        
        # Семья
        if obj.family:
            total_fields += 1
            if obj.family.status:
                filled_fields += 1
        
        # Профиль
        if obj.profile:
            profile_fields = [
                obj.profile.it_skills, obj.profile.hobbies,
                obj.profile.social_networks,
            ]
            total_fields += len(profile_fields)
            filled_fields += sum(1 for f in profile_fields if f)
        
        if total_fields == 0:
            return 0
        return round((filled_fields / total_fields) * 100)


# ==============================================================================
# СЕРИАЛИЗАТОРЫ ДЛЯ КУРАТОРА
# ==============================================================================

class StudentBriefSerializer(serializers.ModelSerializer):
    """Краткая информация о студенте для куратора."""
    full_name = serializers.SerializerMethodField()
    group_name = serializers.CharField(source='group.id_group', read_only=True)
    
    class Meta:
        model = Student
        fields = ('snils', 'full_name', 'group_name', 'phone', 'status', 'birth_date')
    
    def get_full_name(self, obj):
        if obj.user:
            return obj.user.get_full_name()
        return "Без ФИО"


class GroupWithStudentsSerializer(serializers.ModelSerializer):
    """Группа со списком студентов для куратора."""
    students = StudentBriefSerializer(source='student_set', many=True, read_only=True)
    curator_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Group
        fields = ('id_group', 'year_start', 'year_end', 'curator_name', 'students')
    
    def get_curator_name(self, obj):
        if obj.curator:
            return obj.curator.get_full_name()
        return "Не назначен"


# ==============================================================================
# СЕРИАЛИЗАТОРЫ ДЛЯ ПРЕПОДАВАТЕЛЯ
# ==============================================================================

class StatementGradeSerializer(serializers.ModelSerializer):
    """Оценка студента в ведомости."""
    student_name = serializers.SerializerMethodField()
    
    class Meta:
        model = StatementGrade
        fields = ('id_grade', 'student_name', 'grade', 'date', 'is_retake')
    
    def get_student_name(self, obj):
        if obj.student and obj.student.user:
            return obj.student.user.get_full_name()
        return "Без ФИО"


class StatementSerializer(serializers.ModelSerializer):
    """Ведомость с оценками для преподавателя."""
    group_name = serializers.CharField(source='group.id_group', read_only=True)
    discipline_name = serializers.SerializerMethodField()
    grades = StatementGradeSerializer(source='statementgrade_set', many=True, read_only=True)
    teacher_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Statement
        fields = (
            'id_statement', 'number', 'group_name', 'discipline_name',
            'teacher_name', 'issue_date', 'return_date', 'status', 'grades',
        )
    
    def get_discipline_name(self, obj):
        if obj.discipline_in_group and obj.discipline_in_group.discipline_ref:
            return obj.discipline_in_group.discipline_ref.name
        return "—"
    
    def get_teacher_name(self, obj):
        if obj.teacher:
            return obj.teacher.get_full_name()
        return "—"


# ==============================================================================
# СЕРИАЛИЗАТОР ДЛЯ ПОЛЬЗОВАТЕЛЯ (КУРАТОР/ПРЕПОДАВАТЕЛЬ/АДМИН)
# ==============================================================================

class UserProfileSerializer(serializers.ModelSerializer):
    """Сериализатор для кураторов/преподавателей/админов (без данных Student)."""
    full_name = serializers.SerializerMethodField()
    roles = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = (
            'id_user', 'email', 'last_name', 'first_name', 'middle_name',
            'full_name', 'roles',
        )
        read_only_fields = ('id_user', 'email')
    
    def get_full_name(self, obj):
        return obj.get_full_name()
    
    def get_roles(self, obj):
        from .models import UserRole
        user_roles = UserRole.objects.filter(user=obj).select_related('role')
        return [ur.role.id_role for ur in user_roles]


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


# ==============================================================================
# СЕРИАЛИЗАТОРЫ ДЛЯ ЗАЯВОК И УВЕДОМЛЕНИЙ
# ==============================================================================

class StudentRequestSerializer(serializers.ModelSerializer):
    """Сериализатор заявок студента."""
    request_type_display = serializers.CharField(source='get_request_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    student_name = serializers.CharField(source='student.user.get_full_name', read_only=True)

    class Meta:
        model = StudentRequest
        fields = ['id_request', 'student_name', 'request_type', 'request_type_display', 'description', 
                  'status', 'status_display', 'comment', 'created_at', 'updated_at']
        read_only_fields = ['id_request', 'student_name', 'request_type_display', 'status_display', 'created_at', 'updated_at']


class NotificationSerializer(serializers.ModelSerializer):
    """Сериализатор уведомлений."""
    class Meta:
        model = Notification
        fields = ['id_notification', 'title', 'message', 'is_read', 'link', 'created_at']
