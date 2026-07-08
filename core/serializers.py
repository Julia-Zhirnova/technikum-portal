from rest_framework import serializers
from .models import (
    User, Student, Group, Statement, StatementGrade,
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
