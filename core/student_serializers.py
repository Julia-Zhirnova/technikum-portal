from rest_framework import serializers
from .models import (
    User, Student, Passport, Health, Military, Family, 
    FamilyMember, EducationInstitution
)
from .validators import (
    validate_snils, validate_inn, validate_phone,
    validate_email_custom, validate_birth_date,
    validate_passport_series_rf, validate_passport_number_rf,
    validate_passport_issue_date, validate_oms_policy_number,
    validate_passport_code
)
from .exceptions import ValidationError


class StudentProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = [
            'snils', 'birth_date', 'birth_place',
            'gender', 'phone', 'pd_consent', 'pd_consent_date', 'inn'
        ]
        read_only_fields = ['pd_consent_date']
    
    def validate_snils(self, value):
        if value:
            try:
                validate_snils(value)
            except ValidationError as e:
                raise serializers.ValidationError(str(e))
            queryset = Student.objects.filter(snils=value)
            if self.instance:
                queryset = queryset.exclude(pk=self.instance.pk)
            if queryset.exists():
                raise serializers.ValidationError(
                    "Студент с таким СНИЛС уже зарегистрирован"
                )
        return value
    
    def validate_inn(self, value):
        if value:
            try:
                validate_inn(value)
            except ValidationError as e:
                raise serializers.ValidationError(str(e))
        return value
    
    def validate_phone(self, value):
        if value:
            try:
                validate_phone(value)
            except ValidationError as e:
                raise serializers.ValidationError(str(e))
        return value
    
    def validate_birth_date(self, value):
        if value:
            try:
                validate_birth_date(value)
            except ValidationError as e:
                raise serializers.ValidationError(str(e))
        return value
    
    def update(self, instance, validated_data):
        if validated_data.get('pd_consent') and not instance.pd_consent_date:
            from django.utils import timezone
            validated_data['pd_consent_date'] = timezone.now().date()
        return super().update(instance, validated_data)


class PassportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Passport
        fields = [
            'is_foreigner', 'citizenship', 'series_number', 
            'issue_date', 'issuer', 'unit_code',
            'region_city', 'address_detail', 'fact_region', 'fact_detail',
            'temp_reg', 'absence_reason', 'file_path'
        ]
    
    def validate(self, data):
        if not data.get('absence_reason'):
            # Базовые обязательные поля для всех паспортов
            required_fields = ['series_number', 'issue_date', 'issuer', 'region_city']
            
            # unit_code обязателен только для РФ
            if not data.get('is_foreigner'):
                required_fields.append('unit_code')
            
            for field in required_fields:
                if not data.get(field):
                    raise serializers.ValidationError(
                        {field: "Это поле обязательно"}
                    )
            
            # Валидация серии и номера только для РФ
            if not data.get('is_foreigner'):
                series_number = data.get('series_number', '')
                if len(series_number) >= 10:
                    series = series_number[:4]
                    number = series_number[4:]
                    try:
                        validate_passport_series_rf(series)
                    except ValidationError as e:
                        raise serializers.ValidationError({'series_number': str(e)})
                    try:
                        validate_passport_number_rf(number)
                    except ValidationError as e:
                        raise serializers.ValidationError({'series_number': str(e)})
                
                if data.get('unit_code'):
                    try:
                        validate_passport_code(data['unit_code'])
                    except ValidationError as e:
                        raise serializers.ValidationError({'unit_code': str(e)})
            
            # Валидация даты выдачи
            if data.get('issue_date') and self.context.get('student'):
                try:
                    validate_passport_issue_date(
                        data['issue_date'],
                        self.context['student'].birth_date,
                        data.get('is_foreigner', False)
                    )
                except ValidationError as e:
                    raise serializers.ValidationError({'issue_date': str(e)})
        
        return data


class HealthSerializer(serializers.ModelSerializer):
    class Meta:
        model = Health
        fields = [
            'status', 'diagnosis', 'diagnosis_scan',
            'oms_number', 'oms_date', 'oms_issuer',
            'oms_scan', 'oms_absence_reason'
        ]
    
    def validate(self, data):
        health_status = data.get('status')
        diagnosis = data.get('diagnosis')
        if health_status in ['хронические_заболевания', 'инвалидность'] and not diagnosis:
            raise serializers.ValidationError({
                'diagnosis': "Диагноз обязателен при хронических заболеваниях или инвалидности"
            })
        if data.get('oms_number'):
            try:
                validate_oms_policy_number(data['oms_number'])
            except ValidationError as e:
                raise serializers.ValidationError({'oms_number': str(e)})
        return data


class MilitarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Military
        fields = '__all__'


class FamilySerializer(serializers.ModelSerializer):
    class Meta:
        model = Family
        fields = [
            'minors_count', 'adults_count', 'status',
            'housing_type'
        ]
    
    def validate_minors_count(self, value):
        if value is not None and value < 0:
            raise serializers.ValidationError(
                "Количество несовершеннолетних не может быть отрицательным"
            )
        return value
    
    def validate_adults_count(self, value):
        if value is not None and value < 0:
            raise serializers.ValidationError(
                "Количество совершеннолетних не может быть отрицательным"
            )
        return value


class FamilyMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = FamilyMember
        fields = [
            'relation', 'full_name', 'birth_date',
            'education', 'workplace', 'phone', 'is_pensioner',
            'is_svo', 'is_priority_contact'
        ]
    
    def validate(self, data):
        # Получаем family из контекста (передаётся из view)
        family = self.context.get('family')
        is_priority = data.get('is_priority_contact', False)
        
        if is_priority and family:
            queryset = FamilyMember.objects.filter(
                family=family, is_priority_contact=True
            )
            if self.instance:
                queryset = queryset.exclude(pk=self.instance.pk)
            if queryset.exists():
                raise serializers.ValidationError({
                    'is_priority_contact': "В семье уже есть приоритетный контакт"
                })
        return data


class EducationInstitutionSerializer(serializers.ModelSerializer):
    class Meta:
        model = EducationInstitution
        fields = [
            'name', 'type', 'profile',
            'graduation_date'
        ]
    
    def validate_name(self, value):
        if len(value) < 5:
            raise serializers.ValidationError(
                "Наименование должно содержать минимум 5 символов"
            )
        return value
    
    def validate(self, data):
        student = self.context.get('student')
        graduation_date = data.get('graduation_date')
        if graduation_date and student and student.birth_date:
            if graduation_date < student.birth_date:
                raise serializers.ValidationError({
                    'graduation_date': "Дата окончания школы не может быть раньше даты рождения"
                })
        return data
