from import_export import resources, fields, widgets
from import_export.widgets import ForeignKeyWidget
from django.contrib.auth import get_user_model
from .models import (
    # Блок 1: Ядро
    Role, User, UserRole, Campus, Specialty, Qualification, Setting, Order, Group,
    # Блок 2: Персональные данные
    DocumentType, FinancialAidGround, Passport, Health, Military, Family, FamilyMember,
    Profile, EducationInstitution, Student,
    # Блок 3: Трудоустройство и практика
    Industry, Country, Region, CityDistrict, EmploymentType, TargetContract, Organization,
    Employment, PracticeOrder, Module, PracticeOrderModule, StudentPracticePlace,
    DocumentGenerationType,
    # Блок 4: Отчеты по практике
    PracticeTask, PracticeDiary, PracticeControlPoint, PracticeAttestation,
    # Блок 5: Оценки, зачетка, протоколы
    MCK, DisciplineReference, DisciplineInGroup, AssessmentSchedule, AssessmentTeacher,
    Statement, StatementGrade, GEKProtocol, GEKMember, GIAResult, GIADefenseQuestion,
    AttendanceTable, AttendanceTableRow,
)


# ==============================================================================
# БЛОК 1: ЯДРО СИСТЕМЫ
# ==============================================================================

class RoleResource(resources.ModelResource):
    class Meta:
        model = Role
        import_id_fields = ('id_role',)
        fields = ('id_role', 'name')
        export_order = fields


class UserResource(resources.ModelResource):
    """Ресурс для импорта/экспорта пользователей с хешированием пароля."""

    def before_import_row(self, row, **kwargs):
        """Хешируем пароль и обрабатываем пустые значения перед импортом."""
        # Хешируем пароль, если он не захеширован
        password = row.get('password', '')
        if password and not password.startswith(('pbkdf2_', 'argon2', 'bcrypt')):
            from django.contrib.auth.hashers import make_password
            row['password'] = make_password(password)

        # Преобразуем пустые строки в None для поля esia_id
        esia_id = row.get('esia_id', '')
        if esia_id in ('', None):
            row['esia_id'] = None

        return super().before_import_row(row, **kwargs)

    class Meta:
        model = User
        import_id_fields = ('id_user',)
        fields = (
            'id_user', 'last_name', 'first_name', 'middle_name',
            'email', 'password', 'email_confirmed', 'requires_password_change',
            'esia_id', 'is_staff', 'is_active',
        )
        export_order = fields


class UserRoleResource(resources.ModelResource):
    user = fields.Field(
        column_name='user',
        attribute='user',
        widget=ForeignKeyWidget(User, field='id_user')
    )
    role = fields.Field(
        column_name='role',
        attribute='role',
        widget=ForeignKeyWidget(Role, field='id_role')
    )

    class Meta:
        model = UserRole
        import_id_fields = ('user', 'role')
        fields = ('user', 'role')
        export_order = fields


class CampusResource(resources.ModelResource):
    class Meta:
        model = Campus
        import_id_fields = ('id_campus',)
        fields = ('id_campus', 'address')
        export_order = fields


class SpecialtyResource(resources.ModelResource):
    class Meta:
        model = Specialty
        import_id_fields = ('id_specialty',)
        fields = ('id_specialty', 'name', 'level')
        export_order = fields


class QualificationResource(resources.ModelResource):
    specialty = fields.Field(
        column_name='specialty_id',
        attribute='specialty',
        widget=ForeignKeyWidget(Specialty, field='id_specialty')
    )

    class Meta:
        model = Qualification
        import_id_fields = ('id_qualification',)
        fields = ('id_qualification', 'specialty', 'name', 'professionalitet_role')
        export_order = fields


class SettingResource(resources.ModelResource):
    class Meta:
        model = Setting
        import_id_fields = ('id_setting',)
        fields = ('id_setting', 'field_name', 'value', 'description')
        export_order = fields


class OrderResource(resources.ModelResource):
    class Meta:
        model = Order
        import_id_fields = ('id_order',)
        fields = ('id_order', 'number', 'date', 'name', 'file_path', 'type')
        export_order = fields


class GroupResource(resources.ModelResource):
    qualification = fields.Field(
        column_name='qualification',
        attribute='qualification',
        widget=ForeignKeyWidget(Qualification, field='id_qualification')
    )
    campus = fields.Field(
        column_name='campus',
        attribute='campus',
        widget=ForeignKeyWidget(Campus, field='id_campus')
    )
    curator = fields.Field(
        column_name='curator',
        attribute='curator',
        widget=ForeignKeyWidget(User, field='id_user')
    )

    class Meta:
        model = Group
        import_id_fields = ('id_group',)
        fields = (
            'id_group', 'qualification', 'year_start', 'year_end',
            'duration', 'form', 'financing', 'campus', 'curator',
        )
        export_order = fields


# ==============================================================================
# БЛОК 2: ПЕРСОНАЛЬНЫЕ ДАННЫЕ
# ==============================================================================

class DocumentTypeResource(resources.ModelResource):
    class Meta:
        model = DocumentType
        import_id_fields = ('code',)
        fields = ('code', 'name')
        export_order = fields


class FinancialAidGroundResource(resources.ModelResource):
    class Meta:
        model = FinancialAidGround
        import_id_fields = ('id_ground',)
        fields = ('id_ground', 'name', 'requires_mo', 'required_docs')
        export_order = fields


class PassportResource(resources.ModelResource):
    class Meta:
        model = Passport
        import_id_fields = ('id_passport',)
        fields = (
            'id_passport', 'is_foreigner', 'citizenship', 'series_number',
            'issue_date', 'issuer', 'unit_code', 'region_city',
            'address_detail', 'fact_region', 'fact_detail',
            'temp_reg', 'absence_reason', 'file_path',
        )
        export_order = fields


class HealthResource(resources.ModelResource):
    class Meta:
        model = Health
        import_id_fields = ('id_health',)
        fields = (
            'id_health', 'status', 'diagnosis', 'diagnosis_scan',
            'oms_number', 'oms_date', 'oms_issuer', 'oms_scan',
            'oms_absence_reason',
        )
        export_order = fields


class MilitaryResource(resources.ModelResource):
    class Meta:
        model = Military
        import_id_fields = ('id_military',)
        fields = (
            'id_military', 'registration_number', 'commissariat',
            'issue_date', 'fitness_category', 'absence_reason', 'file_path',
        )
        export_order = fields


class FamilyResource(resources.ModelResource):
    fin_aid_ground = fields.Field(
        column_name='fin_aid_ground',
        attribute='fin_aid_ground',
        widget=ForeignKeyWidget(FinancialAidGround, field='id_ground')
    )

    class Meta:
        model = Family
        import_id_fields = ('id_family',)
        fields = (
            'id_family', 'minors_count', 'adults_count', 'status',
            'housing_type', 'fin_aid_ground',
        )
        export_order = fields


class FamilyMemberResource(resources.ModelResource):
    family = fields.Field(
        column_name='family',
        attribute='family',
        widget=ForeignKeyWidget(Family, field='id_family')
    )

    class Meta:
        model = FamilyMember
        import_id_fields = ('id_member',)
        fields = (
            'id_member', 'family', 'relation', 'full_name', 'birth_date',
            'education', 'workplace', 'phone', 'is_pensioner',
            'is_svo', 'is_priority_contact',
        )
        export_order = fields


class ProfileResource(resources.ModelResource):
    class Meta:
        model = Profile
        import_id_fields = ('id_profile',)
        fields = (
            'id_profile', 'it_skills', 'programming_langs', 'creative_skills',
            'school_participation', 'college_participation', 'achievements',
            'hobbies', 'extra_edu', 'social_networks', 'motivation_college',
            'motivation_specialty', 'desired_participation', 'foreign_langs',
            'drivers_license', 'sports_ranks', 'character_behavior',
        )
        export_order = fields


class EducationInstitutionResource(resources.ModelResource):
    class Meta:
        model = EducationInstitution
        import_id_fields = ('id_institution',)
        fields = (
            'id_institution', 'name', 'type', 'profile', 'graduation_date',
        )
        export_order = fields


class StudentResource(resources.ModelResource):
    user = fields.Field(
        column_name='user',
        attribute='user',
        widget=ForeignKeyWidget(User, field='id_user')
    )
    group = fields.Field(
        column_name='group',
        attribute='group',
        widget=ForeignKeyWidget(Group, field='id_group')
    )
    order = fields.Field(
        column_name='order',
        attribute='order',
        widget=ForeignKeyWidget(Order, field='id_order')
    )
    passport = fields.Field(
        column_name='passport',
        attribute='passport',
        widget=ForeignKeyWidget(Passport, field='id_passport')
    )
    health = fields.Field(
        column_name='health',
        attribute='health',
        widget=ForeignKeyWidget(Health, field='id_health')
    )
    military = fields.Field(
        column_name='military',
        attribute='military',
        widget=ForeignKeyWidget(Military, field='id_military')
    )
    family = fields.Field(
        column_name='family',
        attribute='family',
        widget=ForeignKeyWidget(Family, field='id_family')
    )
    education = fields.Field(
        column_name='education',
        attribute='education',
        widget=ForeignKeyWidget(EducationInstitution, field='id_institution')
    )
    profile = fields.Field(
        column_name='profile',
        attribute='profile',
        widget=ForeignKeyWidget(Profile, field='id_profile')
    )

    class Meta:
        model = Student
        import_id_fields = ('snils',)
        fields = (
            'snils', 'snils_file', 'user', 'group', 'order', 'birth_date',
            'gender', 'birth_place', 'phone', 'inn', 'inn_file',
            'pd_consent', 'pd_consent_date', 'status', 'last_change',
            'passport', 'health', 'military', 'family', 'education', 'profile',
            'photo_path', 'study_plan', 'dual_edu',
        )
        export_order = fields


# ==============================================================================
# БЛОК 3: ТРУДОУСТРОЙСТВО И ПРАКТИКА
# ==============================================================================

class IndustryResource(resources.ModelResource):
    class Meta:
        model = Industry
        import_id_fields = ('id_industry',)
        fields = ('id_industry', 'name')
        export_order = fields


class CountryResource(resources.ModelResource):
    class Meta:
        model = Country
        import_id_fields = ('id_country',)
        fields = ('id_country', 'name')
        export_order = fields


class RegionResource(resources.ModelResource):
    class Meta:
        model = Region
        import_id_fields = ('id_region',)
        fields = ('id_region', 'name')
        export_order = fields


class CityDistrictResource(resources.ModelResource):
    class Meta:
        model = CityDistrict
        import_id_fields = ('id_district',)
        fields = ('id_district', 'name')
        export_order = fields


class EmploymentTypeResource(resources.ModelResource):
    class Meta:
        model = EmploymentType
        import_id_fields = ('id_type',)
        fields = ('id_type', 'name')
        export_order = fields


class TargetContractResource(resources.ModelResource):
    student = fields.Field(
        column_name='student',
        attribute='student',
        widget=ForeignKeyWidget(Student, field='snils')
    )

    class Meta:
        model = TargetContract
        import_id_fields = ('id_contract',)
        fields = (
            'id_contract', 'student', 'has_contract', 'format',
            'number', 'date', 'company_name',
        )
        export_order = fields


class OrganizationResource(resources.ModelResource):
    class Meta:
        model = Organization
        import_id_fields = ('inn',)
        fields = (
            'inn', 'legal_name', 'short_name', 'kpp', 'ogrn',
            'rusprofile_link', 'index', 'region', 'city', 'street',
            'building', 'extra_info', 'fact_address',
            'director_name', 'director_position', 'director_phone',
            'email', 'responsible_name', 'responsible_position',
            'responsible_phone', 'mentor_name', 'mentor_position',
            'mentor_phone', 'bank_name', 'account', 'corr_account',
            'bik', 'basis',
        )
        export_order = fields


class EmploymentResource(resources.ModelResource):
    student = fields.Field(
        column_name='student',
        attribute='student',
        widget=ForeignKeyWidget(Student, field='snils')
    )
    organization = fields.Field(
        column_name='organization',
        attribute='organization',
        widget=ForeignKeyWidget(Organization, field='inn')
    )
    employment_type = fields.Field(
        column_name='employment_type',
        attribute='employment_type',
        widget=ForeignKeyWidget(EmploymentType, field='id_type')
    )
    industry = fields.Field(
        column_name='industry',
        attribute='industry',
        widget=ForeignKeyWidget(Industry, field='id_industry')
    )
    city_district = fields.Field(
        column_name='city_district',
        attribute='city_district',
        widget=ForeignKeyWidget(CityDistrict, field='id_district')
    )

    class Meta:
        model = Employment
        import_id_fields = ('id_employment',)
        fields = (
            'id_employment', 'student', 'organization', 'employment_type',
            'is_cluster_partner', 'industry', 'city_district',
            'is_by_profession', 'position', 'update_date',
            'scan_szv_td', 'scan_self_employed', 'scan_ip',
            'scan_self_employed_tax',
        )
        export_order = fields


class PracticeOrderResource(resources.ModelResource):
    group = fields.Field(
        column_name='group',
        attribute='group',
        widget=ForeignKeyWidget(Group, field='id_group')
    )

    class Meta:
        model = PracticeOrder
        import_id_fields = ('id_order',)
        fields = (
            'id_order', 'number', 'date', 'start_date', 'end_date',
            'report_date', 'type', 'group', 'file_path',
        )
        export_order = fields


class ModuleResource(resources.ModelResource):
    group = fields.Field(
        column_name='group',
        attribute='group',
        widget=ForeignKeyWidget(Group, field='id_group')
    )

    class Meta:
        model = Module
        import_id_fields = ('id_module',)
        fields = ('id_module', 'group', 'code', 'name')
        export_order = fields


class PracticeOrderModuleResource(resources.ModelResource):
    order = fields.Field(
        column_name='order',
        attribute='order',
        widget=ForeignKeyWidget(PracticeOrder, field='id_order')
    )
    module = fields.Field(
        column_name='module',
        attribute='module',
        widget=ForeignKeyWidget(Module, field='id_module')
    )

    class Meta:
        model = PracticeOrderModule
        import_id_fields = ('order', 'module')
        fields = ('order', 'module')
        export_order = fields


class StudentPracticePlaceResource(resources.ModelResource):
    order = fields.Field(
        column_name='order',
        attribute='order',
        widget=ForeignKeyWidget(PracticeOrder, field='id_order')
    )
    student = fields.Field(
        column_name='student',
        attribute='student',
        widget=ForeignKeyWidget(Student, field='snils')
    )
    organization = fields.Field(
        column_name='organization',
        attribute='organization',
        widget=ForeignKeyWidget(Organization, field='inn')
    )
    teacher1 = fields.Field(
        column_name='teacher1',
        attribute='teacher1',
        widget=ForeignKeyWidget(User, field='id_user')
    )
    teacher2 = fields.Field(
        column_name='teacher2',
        attribute='teacher2',
        widget=ForeignKeyWidget(User, field='id_user')
    )

    class Meta:
        model = StudentPracticePlace
        import_id_fields = ('id_place',)
        fields = (
            'id_place', 'order', 'student', 'organization', 'position',
            'status', 'teacher1', 'teacher2',
        )
        export_order = fields


class DocumentGenerationTypeResource(resources.ModelResource):
    class Meta:
        model = DocumentGenerationType
        import_id_fields = ('code',)
        fields = ('code', 'name', 'description', 'template_path')
        export_order = fields


# ==============================================================================
# БЛОК 4: ОТЧЕТЫ ПО ПРАКТИКЕ
# ==============================================================================

class PracticeTaskResource(resources.ModelResource):
    practice_place = fields.Field(
        column_name='practice_place',
        attribute='practice_place',
        widget=ForeignKeyWidget(StudentPracticePlace, field='id_place')
    )

    class Meta:
        model = PracticeTask
        import_id_fields = ('id_task',)
        fields = (
            'id_task', 'practice_place', 'topic_number', 'topic_name',
            'work_types', 'competencies', 'hours',
        )
        export_order = fields


class PracticeDiaryResource(resources.ModelResource):
    practice_place = fields.Field(
        column_name='practice_place',
        attribute='practice_place',
        widget=ForeignKeyWidget(StudentPracticePlace, field='id_place')
    )

    class Meta:
        model = PracticeDiary
        import_id_fields = ('id_entry',)
        fields = (
            'id_entry', 'practice_place', 'date', 'work_content',
            'hours', 'is_approved_by_org',
        )
        export_order = fields


class PracticeControlPointResource(resources.ModelResource):
    practice_place = fields.Field(
        column_name='practice_place',
        attribute='practice_place',
        widget=ForeignKeyWidget(StudentPracticePlace, field='id_place')
    )

    class Meta:
        model = PracticeControlPoint
        import_id_fields = ('id_point',)
        fields = (
            'id_point', 'practice_place', 'control_date',
            'work_done', 'is_signed_by_org',
        )
        export_order = fields


class PracticeAttestationResource(resources.ModelResource):
    practice_place = fields.Field(
        column_name='practice_place',
        attribute='practice_place',
        widget=ForeignKeyWidget(StudentPracticePlace, field='id_place')
    )

    class Meta:
        model = PracticeAttestation
        import_id_fields = ('id_attestation',)
        fields = (
            'id_attestation', 'practice_place', 'competencies_eval',
            'characteristic_text', 'recommended_grade', 'fill_date',
        )
        export_order = fields


# ==============================================================================
# БЛОК 5: ОЦЕНКИ, ЗАЧЕТКА, ПРОТОКОЛЫ
# ==============================================================================

class MCKResource(resources.ModelResource):
    chairman = fields.Field(
        column_name='chairman',
        attribute='chairman',
        widget=ForeignKeyWidget(User, field='id_user')
    )

    class Meta:
        model = MCK
        import_id_fields = ('id_mck',)
        fields = ('id_mck', 'name', 'short_name', 'chairman')
        export_order = fields


class DisciplineReferenceResource(resources.ModelResource):
    """Ресурс для импорта/экспорта справочника дисциплин с очисткой данных."""

    def before_import_row(self, row, row_number=None, **kwargs):
        """Очищаем данные перед импортом."""
        # Очищаем код от пробелов
        code = row.get('code', '')
        if isinstance(code, str):
            code = code.strip().replace(' ', '')
        row['code'] = code

        # Очищаем название от пробелов в начале и конце и точек в конце
        name = row.get('name', '')
        if isinstance(name, str):
            name = name.strip()
            if name.endswith('.'):
                name = name[:-1]
        row['name'] = name

        # Преобразуем тип в нижний регистр
        type_value = row.get('type', '')
        if isinstance(type_value, str):
            type_value = type_value.strip()
        type_mapping = {
            'МДК': 'мдк',
            'Практика': 'практика',
            'ГИА': 'гиа',
        }

        if type_value in type_mapping:
            row['type'] = type_mapping[type_value]

        return super().before_import_row(row, row_number=row_number, **kwargs)

    class Meta:
        model = DisciplineReference
        import_id_fields = ('code',)
        fields = ('code', 'name', 'type')
        export_order = fields
        skip_unchanged = False
        use_bulk = False
        force_init_instance = True


class DisciplineInGroupResource(resources.ModelResource):
    group = fields.Field(
        column_name='group',
        attribute='group',
        widget=ForeignKeyWidget(Group, field='id_group')
    )
    discipline_ref = fields.Field(
        column_name='discipline_ref',
        attribute='discipline_ref',
        widget=ForeignKeyWidget(DisciplineReference, field='code')
    )
    mck = fields.Field(
        column_name='mck',
        attribute='mck',
        widget=ForeignKeyWidget(MCK, field='id_mck')
    )

    class Meta:
        model = DisciplineInGroup
        import_id_fields = ('id_record',)
        fields = (
            'id_record', 'group', 'discipline_ref', 'semester',
            'assessment_form', 'hours', 'mck',
        )
        export_order = fields


# ==============================================================================
# РАСПИСАНИЕ АТТЕСТАЦИИ (с поддержкой M2M через AssessmentTeacher)
# ==============================================================================

class AssessmentScheduleResource(resources.ModelResource):
    """
    Ресурс для импорта/экспорта расписания аттестации.
    
    Поддерживает импорт:
    - teacher (основной преподаватель) — через ForeignKeyWidget по id_user
    - co_teachers (со-преподаватели) — через строку с ID через / или ,
      значения вида "34/19" или "34,19" преобразуются в записи AssessmentTeacher
    
    После сохранения объекта AssessmentSchedule автоматически создаются
    соответствующие записи в AssessmentTeacher.
    """
    
    group = fields.Field(
        column_name='group',
        attribute='group',
        widget=widgets.ForeignKeyWidget(Group, 'id_group')
    )
    
    discipline_in_group = fields.Field(
        column_name='discipline_in_group',
        attribute='discipline_in_group',
        widget=widgets.ForeignKeyWidget(DisciplineInGroup, 'id_record')
    )
    
    # Основной преподаватель — импортируется напрямую через ForeignKeyWidget
    teacher = fields.Field(
        column_name='teacher',
        attribute=None,  # не привязываем напрямую к модели
        widget=widgets.ForeignKeyWidget(User, 'id_user')
    )
    
    # Со-преподаватели — импортируются как строка ID через / или ,
    co_teachers = fields.Field(
        column_name='co_teachers',
        attribute=None,
    )
    
    class Meta:
        model = AssessmentSchedule
        import_id_fields = ('id_schedule',)
        fields = (
            'id_schedule',
            'group',
            'discipline_in_group',
            'date',
            'time',
            'room',
            'teacher',
            'co_teachers',
            'retake_date',
            'retake_time',
        )
        skip_unchanged = False
        report_skipped = False
    
    def before_import_row(self, row, row_number=None, **kwargs):
        """
        Перед импортом строки извлекаем teacher и co_teachers,
        чтобы после создания объекта AssessmentSchedule создать записи AssessmentTeacher.
        """
        # Сохраняем teacher и co_teachers во временные атрибуты
        teacher_id = row.get('teacher', '')
        co_teachers_str = row.get('co_teachers', '')
        
        # Преобразуем в int или None
        self._current_teacher_id = None
        if teacher_id and str(teacher_id).strip().isdigit():
            self._current_teacher_id = int(teacher_id)
        
        self._current_co_teacher_ids = []
        if co_teachers_str:
            import re
            ids = re.split(r'[,/\s]+', str(co_teachers_str).strip())
            for id_str in ids:
                if id_str.strip().isdigit():
                    self._current_co_teacher_ids.append(int(id_str))
        
        # Удаляем эти поля из row, чтобы они не мешали импорту модели
        row.pop('teacher', None)
        row.pop('co_teachers', None)
        
        return super().before_import_row(row, row_number=row_number, **kwargs)
    
    def after_save_instance(self, instance, row, **kwargs):
        """
        После сохранения AssessmentSchedule создаём записи AssessmentTeacher.
        """
        dry_run = kwargs.get('dry_run', False)
        if dry_run:
            return
        
        # Очищаем существующие записи (для обновления)
        instance.assessment_teachers.all().delete()
        
        # Создаём запись для основного преподавателя
        if self._current_teacher_id:
            try:
                teacher = User.objects.get(id_user=self._current_teacher_id)
                AssessmentTeacher.objects.create(
                    schedule=instance,
                    teacher=teacher,
                    role='primary'
                )
            except User.DoesNotExist:
                pass
        
        # Создаём записи для со-преподавателей
        for co_teacher_id in self._current_co_teacher_ids:
            try:
                co_teacher = User.objects.get(id_user=co_teacher_id)
                # Пропускаем, если это тот же, что и основной
                if co_teacher_id != self._current_teacher_id:
                    AssessmentTeacher.objects.get_or_create(
                        schedule=instance,
                        teacher=co_teacher,
                        defaults={'role': 'co'}
                    )
            except User.DoesNotExist:
                pass
    
    def dehydrate_teacher(self, obj):
        """Экспорт: возвращает ID основного преподавателя."""
        primary = obj.get_primary_teacher()
        return primary.id_user if primary else None
    
    def dehydrate_co_teachers(self, obj):
        """Экспорт: возвращает IDs со-преподавателей через слэш."""
        co_teachers = obj.get_co_teachers()
        if not co_teachers.exists():
            return None
        return '/'.join([str(t.id_user) for t in co_teachers])


# ==============================================================================
# AssessmentTeacherResource — для прямого импорта промежуточной таблицы
# ==============================================================================

class AssessmentTeacherResource(resources.ModelResource):
    """
    Ресурс для прямого импорта/экспорта промежуточной таблицы AssessmentTeacher.
    Полезен, если нужно массово добавить преподавателей к существующим записям расписания.
    
    Формат CSV:
    id_assessment_teacher, schedule_id, teacher_id, role
    1, 5, 34, primary
    2, 5, 19, co
    """
    
    schedule = fields.Field(
        column_name='schedule_id',
        attribute='schedule',
        widget=widgets.ForeignKeyWidget(AssessmentSchedule, 'id_schedule')
    )
    
    teacher = fields.Field(
        column_name='teacher_id',
        attribute='teacher',
        widget=widgets.ForeignKeyWidget(User, 'id_user')
    )
    
    class Meta:
        model = AssessmentTeacher
        import_id_fields = ('id_assessment_teacher',)
        fields = (
            'id_assessment_teacher',
            'schedule',
            'teacher',
            'role',
        )
        skip_unchanged = True
        report_skipped = False


class StatementResource(resources.ModelResource):
    group = fields.Field(
        column_name='group',
        attribute='group',
        widget=ForeignKeyWidget(Group, field='id_group')
    )
    discipline_in_group = fields.Field(
        column_name='discipline_in_group',
        attribute='discipline_in_group',
        widget=ForeignKeyWidget(DisciplineInGroup, field='id_record')
    )
    teacher = fields.Field(
        column_name='teacher',
        attribute='teacher',
        widget=ForeignKeyWidget(User, field='id_user')
    )

    class Meta:
        model = Statement
        import_id_fields = ('id_statement',)
        fields = (
            'id_statement', 'number', 'group', 'discipline_in_group',
            'teacher', 'issue_date', 'return_date', 'status',
        )
        export_order = fields


class StatementGradeResource(resources.ModelResource):
    statement = fields.Field(
        column_name='statement',
        attribute='statement',
        widget=ForeignKeyWidget(Statement, field='id_statement')
    )
    student = fields.Field(
        column_name='student',
        attribute='student',
        widget=ForeignKeyWidget(Student, field='snils')
    )

    class Meta:
        model = StatementGrade
        import_id_fields = ('id_grade',)
        fields = (
            'id_grade', 'statement', 'student', 'grade',
            'date', 'is_retake',
        )
        export_order = fields


class GEKProtocolResource(resources.ModelResource):
    group = fields.Field(
        column_name='group',
        attribute='group',
        widget=ForeignKeyWidget(Group, field='id_group')
    )
    chairman = fields.Field(
        column_name='chairman',
        attribute='chairman',
        widget=ForeignKeyWidget(User, field='id_user')
    )

    class Meta:
        model = GEKProtocol
        import_id_fields = ('id_protocol',)
        fields = (
            'id_protocol', 'number', 'group', 'date', 'gia_type', 'chairman',
        )
        export_order = fields


class GEKMemberResource(resources.ModelResource):
    protocol = fields.Field(
        column_name='protocol',
        attribute='protocol',
        widget=ForeignKeyWidget(GEKProtocol, field='id_protocol')
    )
    user = fields.Field(
        column_name='user',
        attribute='user',
        widget=ForeignKeyWidget(User, field='id_user')
    )

    class Meta:
        model = GEKMember
        import_id_fields = ('protocol', 'user')
        fields = ('protocol', 'user', 'role')
        export_order = fields


class GIAResultResource(resources.ModelResource):
    protocol = fields.Field(
        column_name='protocol',
        attribute='protocol',
        widget=ForeignKeyWidget(GEKProtocol, field='id_protocol')
    )
    student = fields.Field(
        column_name='student',
        attribute='student',
        widget=ForeignKeyWidget(Student, field='snils')
    )
    diploma_supervisor = fields.Field(
        column_name='diploma_supervisor',
        attribute='diploma_supervisor',
        widget=ForeignKeyWidget(User, field='id_user')
    )

    class Meta:
        model = GIAResult
        import_id_fields = ('id_result',)
        fields = (
            'id_result', 'protocol', 'student', 'de_score', 'de_grade',
            'diploma_topic', 'diploma_supervisor', 'diploma_grade',
            'final_gia_grade',
        )
        export_order = fields


class GIADefenseQuestionResource(resources.ModelResource):
    gia_result = fields.Field(
        column_name='gia_result',
        attribute='gia_result',
        widget=ForeignKeyWidget(GIAResult, field='id_result')
    )
    expert = fields.Field(
        column_name='expert',
        attribute='expert',
        widget=ForeignKeyWidget(User, field='id_user')
    )

    class Meta:
        model = GIADefenseQuestion
        import_id_fields = ('id_question',)
        fields = (
            'id_question', 'gia_result', 'question_number',
            'question_text', 'expert', 'student_answer',
        )
        export_order = fields


class AttendanceTableResource(resources.ModelResource):
    group = fields.Field(
        column_name='group',
        attribute='group',
        widget=ForeignKeyWidget(Group, field='id_group')
    )
    curator = fields.Field(
        column_name='curator',
        attribute='curator',
        widget=ForeignKeyWidget(User, field='id_user')
    )

    class Meta:
        model = AttendanceTable
        import_id_fields = ('id_table',)
        fields = ('id_table', 'group', 'month', 'year', 'curator')
        export_order = fields


class AttendanceTableRowResource(resources.ModelResource):
    table = fields.Field(
        column_name='table',
        attribute='table',
        widget=ForeignKeyWidget(AttendanceTable, field='id_table')
    )
    student = fields.Field(
        column_name='student',
        attribute='student',
        widget=ForeignKeyWidget(Student, field='snils')
    )

    class Meta:
        model = AttendanceTableRow
        import_id_fields = ('id_row',)
        fields = (
            'id_row', 'table', 'student', 'study_days',
            'sick_leave', 'practice', 'truancy',
        )
        export_order = fields
