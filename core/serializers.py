from rest_framework import serializers
from .models import (
    User, Student, Group, Statement, StatementGrade,
    Passport, Health, Military, Family, FamilyMember, Profile
)

# ==============================================================================
# СЕРИАЛИЗАТОРЫ ДЛЯ СТУДЕНТА
# ==============================================================================

class PassportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Passport
        fields = ('series_number', 'issue_date', 'issuer', 'unit_code')

class HealthSerializer(serializers.ModelSerializer):
    class Meta:
        model = Health
        fields = ('status', 'oms_number', 'oms_issuer')

class MilitarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Military
        fields = ('registration_number', 'fitness_category', 'commissariat')

class FamilyMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = FamilyMember
        fields = ('relation', 'full_name', 'birth_date', 'workplace', 'phone')

class FamilySerializer(serializers.ModelSerializer):
    members = FamilyMemberSerializer(source='familymember_set', many=True, read_only=True)
    
    class Meta:
        model = Family
        fields = ('status', 'housing_type', 'members')

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ('it_skills', 'programming_langs', 'hobbies', 'creative_skills')

class StudentSerializer(serializers.ModelSerializer):
    """Полный сериализатор студента для личного кабинета."""
    user_full_name = serializers.SerializerMethodField()
    group_name = serializers.CharField(source='group.id_group', read_only=True)
    passport = PassportSerializer(read_only=True)
    health = HealthSerializer(read_only=True)
    military = MilitarySerializer(read_only=True)
    family = FamilySerializer(read_only=True)
    profile = ProfileSerializer(read_only=True)
    
    class Meta:
        model = Student
        fields = (
            'snils', 'user_full_name', 'group_name', 'birth_date',
            'gender', 'birth_place', 'phone', 'inn', 'status',
            'passport', 'health', 'military', 'family', 'profile'
        )
    
    def get_user_full_name(self, obj):
        if obj.user:
            return obj.user.get_full_name()
        return "Без ФИО"

# ==============================================================================
# СЕРИАЛИЗАТОРЫ ДЛЯ КУРАТОРА
# ==============================================================================

class StudentBriefSerializer(serializers.ModelSerializer):
    """Краткая информация о студенте для куратора."""
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Student
        fields = ('snils', 'full_name', 'phone', 'status')
    
    def get_full_name(self, obj):
        if obj.user:
            return obj.user.get_full_name()
        return "Без ФИО"

class GroupWithStudentsSerializer(serializers.ModelSerializer):
    """Группа со списком студентов для куратора."""
    students = StudentBriefSerializer(source='student_set', many=True, read_only=True)
    
    class Meta:
        model = Group
        fields = ('id_group', 'qualification', 'year_start', 'students')

# ==============================================================================
# СЕРИАЛИЗАТОРЫ ДЛЯ ПРЕПОДАВАТЕЛЯ
# ==============================================================================

class StatementGradeSerializer(serializers.ModelSerializer):
    student_name = serializers.SerializerMethodField()
    
    class Meta:
        model = StatementGrade
        fields = ('id_grade', 'student_name', 'grade', 'date', 'is_retake')
    
    def get_student_name(self, obj):
        if obj.student.user:
            return obj.student.user.get_full_name()
        return "Без ФИО"

class StatementSerializer(serializers.ModelSerializer):
    """Ведомость с оценками для преподавателя."""
    group_name = serializers.CharField(source='group.id_group', read_only=True)
    discipline_name = serializers.SerializerMethodField()
    grades = StatementGradeSerializer(source='statementgrade_set', many=True, read_only=True)
    
    class Meta:
        model = Statement
        fields = (
            'id_statement', 'number', 'group_name', 'discipline_name',
            'issue_date', 'status', 'grades'
        )
    
    def get_discipline_name(self, obj):
        if obj.discipline_in_group and obj.discipline_in_group.discipline_ref:
            return obj.discipline_in_group.discipline_ref.name
        return "—"
