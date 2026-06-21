from django.contrib import admin
from import_export.admin import ImportExportModelAdmin

from . import resources
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
# КАСТОМНЫЙ ADMIN SITE С ГРУППИРОВКОЙ ПО БЛОКАМ
# ==============================================================================

class CustomAdminSite(admin.AdminSite):
    """Кастомная админка с группировкой моделей по 8 блокам."""
    site_header = 'Люберецкий техникум — Администрирование'
    site_title = 'Портал техникума'
    index_title = 'Панель управления'

    def get_app_list(self, request, app_label=None):
        """Переопределяем стандартный метод для группировки моделей."""
        if app_label:
            return super().get_app_list(request, app_label)

        app_list = super().get_app_list(request)

        # Находим приложение 'core' и остальные
        core_app = None
        other_apps = []
        for app in app_list:
            if app['app_label'] == 'core':
                core_app = app
            else:
                other_apps.append(app)

        if not core_app:
            return app_list

        # Определяем 8 групп и модели в каждой
        groups = {
            '📚 ГРУППА 1: СПРАВОЧНИКИ': [
                'Role', 'Campus', 'Specialty', 'DocumentType', 'Country',
                'Region', 'CityDistrict', 'Industry', 'EmploymentType',
                'FinancialAidGround', 'Setting', 'DocumentGenerationType',
                'DisciplineReference',
            ],
            '👥 ГРУППА 2: ПОЛЬЗОВАТЕЛИ И БАЗОВЫЕ СУЩНОСТИ': [
                'User', 'UserRole', 'Qualification', 'Order', 'MCK',
            ],
            '🎓 ГРУППА 3: ГРУППЫ И ДИСЦИПЛИНЫ': [
                'Group', 'DisciplineInGroup', 'AssessmentSchedule', 'AssessmentTeacher',
            ],
            '👨 ГРУППА 4: СТУДЕНТЫ И ИХ ДАННЫЕ': [
                'Passport', 'Health', 'Military', 'Family', 'FamilyMember',
                'Profile', 'EducationInstitution', 'Student',
            ],
            '💼 ГРУППА 5: ТРУДОУСТРОЙСТВО И ОРГАНИЗАЦИИ': [
                'Organization', 'Employment', 'TargetContract',
            ],
            '🏢 ГРУППА 6: ПРАКТИКА': [
                'PracticeOrder', 'Module', 'PracticeOrderModule',
                'StudentPracticePlace', 'PracticeTask', 'PracticeDiary',
                'PracticeControlPoint', 'PracticeAttestation',
            ],
            '📊 ГРУППА 7: ОЦЕНКИ И АТТЕСТАЦИЯ': [
                'Statement', 'StatementGrade', 'GEKProtocol', 'GEKMember',
                'GIAResult', 'GIADefenseQuestion',
            ],
            '📅 ГРУППА 8: ПОСЕЩАЕМОСТЬ': [
                'AttendanceTable', 'AttendanceTableRow',
            ],
        }

        # Создаём словарь моделей по имени класса
        models_by_name = {m['object_name']: m for m in core_app['models']}

        # Формируем новые группы
        new_apps = []
        for group_name, model_names in groups.items():
            group_models = []
            for model_name in model_names:
                if model_name in models_by_name:
                    group_models.append(models_by_name[model_name])

            if group_models:
                new_apps.append({
                    'name': group_name,
                    'app_label': core_app['app_label'],
                    'app_url': core_app['app_url'],
                    'has_module_perms': core_app['has_module_perms'],
                    'models': group_models,
                })

        # Добавляем остальные приложения (auth, sessions и т.д.)
        new_apps.extend(other_apps)

        return new_apps


# ==============================================================================
# БАЗОВЫЙ КЛАСС АДМИНКИ С ИМПОРТОМ/ЭКСПОРТОМ И ПОИСКОМ
# ==============================================================================

class BaseAdmin(ImportExportModelAdmin):
    list_per_page = 50
    save_on_top = True
    search_help_text = 'Введите текст для поиска'


# ==============================================================================
# 📚 ГРУППА 1: СПРАВОЧНИКИ
# ==============================================================================

class RoleAdmin(BaseAdmin):
    resource_class = resources.RoleResource
    list_display = ('id_role', 'name')
    search_fields = ('id_role', 'name')
    search_help_text = 'Поиск по ID роли или названию'


class CampusAdmin(BaseAdmin):
    resource_class = resources.CampusResource
    list_display = ('id_campus', 'address')
    search_fields = ('id_campus', 'address')
    search_help_text = 'Поиск по ID корпуса или адресу'


class SpecialtyAdmin(BaseAdmin):
    resource_class = resources.SpecialtyResource
    list_display = ('id_specialty', 'name', 'level')
    list_filter = ('level',)
    search_fields = ('id_specialty', 'name')
    search_help_text = 'Поиск по коду ФГОС или названию специальности'


class DocumentTypeAdmin(BaseAdmin):
    resource_class = resources.DocumentTypeResource
    list_display = ('code', 'name')
    search_fields = ('code', 'name')
    search_help_text = 'Поиск по коду или названию типа документа'


class CountryAdmin(BaseAdmin):
    resource_class = resources.CountryResource
    list_display = ('id_country', 'name')
    search_fields = ('id_country', 'name')
    search_help_text = 'Поиск по коду страны или названию'


class RegionAdmin(BaseAdmin):
    resource_class = resources.RegionResource
    list_display = ('name',)
    search_fields = ('name',)
    search_help_text = 'Поиск по названию области/региона'


class CityDistrictAdmin(BaseAdmin):
    resource_class = resources.CityDistrictResource
    list_display = ('name',)
    search_fields = ('name',)
    search_help_text = 'Поиск по названию городского округа'


class IndustryAdmin(BaseAdmin):
    resource_class = resources.IndustryResource
    list_display = ('name',)
    search_fields = ('name',)
    search_help_text = 'Поиск по названию отрасли'


class EmploymentTypeAdmin(BaseAdmin):
    resource_class = resources.EmploymentTypeResource
    list_display = ('name',)
    search_fields = ('name',)
    search_help_text = 'Поиск по названию формы занятости'


class FinancialAidGroundAdmin(BaseAdmin):
    resource_class = resources.FinancialAidGroundResource
    list_display = ('name', 'requires_mo')
    list_filter = ('requires_mo',)
    search_fields = ('name',)
    search_help_text = 'Поиск по названию основания мат. помощи'


class SettingAdmin(BaseAdmin):
    resource_class = resources.SettingResource
    list_display = ('field_name', 'value')
    search_fields = ('field_name', 'value', 'description')
    search_help_text = 'Поиск по названию поля, значению или описанию'


class DocumentGenerationTypeAdmin(BaseAdmin):
    resource_class = resources.DocumentGenerationTypeResource
    list_display = ('code', 'name', 'template_path')
    search_fields = ('code', 'name', 'description', 'template_path')
    search_help_text = 'Поиск по коду, названию, описанию или пути к шаблону'


class DisciplineReferenceAdmin(BaseAdmin):
    resource_class = resources.DisciplineReferenceResource
    list_display = ('code', 'name', 'type')
    list_filter = ('type',)
    search_fields = ('code', 'name')
    search_help_text = 'Поиск по коду дисциплины (например, ОП.07) или названию'


# ==============================================================================
# 👥 ГРУППА 2: ПОЛЬЗОВАТЕЛИ И БАЗОВЫЕ СУЩНОСТИ
# ==============================================================================

class UserAdmin(BaseAdmin):
    resource_class = resources.UserResource
    list_display = ('email', 'last_name', 'first_name', 'is_active', 'requires_password_change')
    list_filter = ('is_active', 'requires_password_change')
    search_fields = ('email', 'last_name', 'first_name', 'middle_name', 'esia_id')
    search_help_text = 'Поиск по email, ФИО или ESIA ID'


class UserRoleAdmin(BaseAdmin):
    resource_class = resources.UserRoleResource
    list_display = ('user', 'role')
    list_filter = ('role',)
    search_fields = ('user__email', 'user__last_name', 'user__first_name', 'role__name')
    search_help_text = 'Поиск по email/ФИО пользователя или названию роли'


class QualificationAdmin(BaseAdmin):
    resource_class = resources.QualificationResource
    list_display = ('name', 'specialty', 'professionalitet_role')
    list_filter = ('professionalitet_role', 'specialty')
    search_fields = ('name', 'specialty__name', 'specialty__id_specialty')
    search_help_text = 'Поиск по названию квалификации или специальности'


class OrderAdmin(BaseAdmin):
    resource_class = resources.OrderResource
    list_display = ('id_order', 'number', 'date', 'type')
    list_filter = ('type', 'date')
    search_fields = ('id_order', 'number', 'name')
    search_help_text = 'Поиск по ID, номеру или названию приказа'


class MCKAdmin(BaseAdmin):
    resource_class = resources.MCKResource
    list_display = ('name', 'short_name', 'chairman')
    search_fields = ('name', 'short_name', 'chairman__email', 'chairman__last_name')
    search_help_text = 'Поиск по названию МЦК или ФИО председателя'


# ==============================================================================
# 🎓 ГРУППА 3: ГРУППЫ И ДИСЦИПЛИНЫ
# ==============================================================================

class GroupAdmin(BaseAdmin):
    resource_class = resources.GroupResource
    list_display = ('id_group', 'qualification', 'year_start', 'form', 'financing', 'campus')
    list_filter = ('form', 'financing', 'campus', 'year_start')
    search_fields = ('id_group',)
    search_help_text = 'Поиск по ID группы (например, ИС-24)'


class DisciplineInGroupAdmin(BaseAdmin):
    resource_class = resources.DisciplineInGroupResource
    list_display = ('discipline_ref', 'group', 'semester', 'assessment_form', 'mck')
    list_filter = ('semester', 'assessment_form', 'group', 'mck')
    search_fields = (
        'discipline_ref__code', 'discipline_ref__name',
        'group__id_group', 'mck__name',
    )
    search_help_text = 'Поиск по коду/названию дисциплины, ID группы или МЦК'


# ------------------------------------------------------------------------------
# Inline для преподавателей в расписании
# ------------------------------------------------------------------------------

class AssessmentTeacherInline(admin.TabularInline):
    """
    Inline-редактирование преподавателей прямо в форме расписания.
    Позволяет добавить основного преподавателя и со-преподавателей.
    """
    model = AssessmentTeacher
    extra = 1  # Количество пустых строк для добавления
    min_num = 0
    max_num = 10
    verbose_name = 'Преподаватель'
    verbose_name_plural = '👥 Преподаватели (основной + со-преподаватели)'
    
    fields = ('teacher', 'role')
    autocomplete_fields = ('teacher',)
    
    def get_queryset(self, request):
        """Сортируем: сначала основной преподаватель, потом со-преподаватели."""
        qs = super().get_queryset(request)
        return qs.select_related('teacher').order_by('-role', 'teacher__last_name')


# ------------------------------------------------------------------------------
# AssessmentScheduleAdmin (обновлён для M2M)
# ------------------------------------------------------------------------------

class AssessmentScheduleAdmin(BaseAdmin):
    resource_class = resources.AssessmentScheduleResource
    
    list_display = (
        'id_schedule',
        'get_discipline_name',
        'group',
        'date',
        'time',
        'room',
        'get_primary_teacher',
        'get_co_teachers_list',
        'retake_date',
    )
    
    list_filter = (
        'group',
        'date',
    )
    
    search_fields = (
        'id_schedule',
        'discipline_in_group__discipline_ref__code',
        'discipline_in_group__discipline_ref__name',
        'group__id_group',
        'room',
        'assessment_teachers__teacher__last_name',
        'assessment_teachers__teacher__first_name',
        'assessment_teachers__teacher__middle_name',
        'assessment_teachers__teacher__email',
    )
    
    readonly_fields = ('id_schedule', 'get_teachers_display')
    
    fieldsets = (
        ('Основная информация', {
            'fields': (
                'id_schedule',
                'group',
                'discipline_in_group',
            )
        }),
        ('Дата и место проведения', {
            'fields': (
                'date',
                'time',
                'room',
            )
        }),
        ('Преподаватели', {
            'description': (
                'Основной преподаватель и со-преподаватели указываются '
                'в таблице ниже. Роль «Основной преподаватель» может быть '
                'только у одного человека.'
            ),
            'fields': (
                'get_teachers_display',
            )
        }),
        ('Пересдача', {
            'fields': (
                'retake_date',
                'retake_time',
            ),
            'classes': ('collapse',)
        }),
    )
    
    inlines = [AssessmentTeacherInline]
    
    def get_primary_teacher(self, obj):
        """Основной преподаватель для списка."""
        primary = obj.get_primary_teacher()
        if primary:
            return primary.get_full_name() or primary.email
        return '—'
    get_primary_teacher.short_description = 'Основной преподаватель'
    get_primary_teacher.admin_order_field = 'assessment_teachers__teacher__last_name'
    
    def get_co_teachers_list(self, obj):
        """Список со-преподавателей для списка."""
        co_teachers = obj.get_co_teachers()
        if not co_teachers.exists():
            return '—'
        names = []
        for t in co_teachers:
            name = t.get_full_name() or t.email
            names.append(name)
        return ', '.join(names)
    get_co_teachers_list.short_description = 'Со-преподаватели'
    
    def get_discipline_name(self, obj):
        """Название дисциплины для списка."""
        if obj.discipline_in_group and obj.discipline_in_group.discipline_ref:
            return obj.discipline_in_group.discipline_ref.name
        return '—'
    get_discipline_name.short_description = 'Дисциплина'
    
    def get_teachers_display(self, obj):
        """Красивое отображение всех преподавателей в форме."""
        primary = obj.get_primary_teacher()
        co_teachers = obj.get_co_teachers()
        
        lines = []
        if primary:
            lines.append(
                f'<strong>👨‍🏫 Основной:</strong> '
                f'{primary.get_full_name() or primary.email}'
            )
        else:
            lines.append('<em>Основной преподаватель не указан</em>')
        
        if co_teachers.exists():
            lines.append('<br><strong>👥 Со-преподаватели:</strong>')
            for t in co_teachers:
                lines.append(
                    f'&nbsp;&nbsp;• {t.get_full_name() or t.email}'
                )
        else:
            lines.append('<br><em>Со-преподаватели не указаны</em>')
        
        return '<br>'.join(lines)
    get_teachers_display.short_description = 'Преподаватели'
    get_teachers_display.allow_tags = True
    
    def save_related(self, request, form, formsets, change):
        """
        Валидация: только один основной преподаватель.
        Если пользователь случайно указал несколько — лишние переключаются в co.
        """
        super().save_related(request, form, formsets, change)
        
        instance = form.instance
        primary_teachers = instance.assessment_teachers.filter(
            role='primary'
        ).order_by('id_assessment_teacher')
        
        if primary_teachers.count() > 1:
            from django.contrib import messages
            messages.warning(
                request,
                'Основной преподаватель может быть только один! '
                'Лишние записи автоматически переключены в со-преподаватели.'
            )
            for at in primary_teachers[1:]:
                at.role = 'co'
                at.save()


# ------------------------------------------------------------------------------
# AssessmentTeacherAdmin (отдельная админка для промежуточной модели)
# ------------------------------------------------------------------------------

class AssessmentTeacherAdmin(BaseAdmin):
    """
    Отдельная админка для записей связи преподавателей с расписанием.
    Обычно используется через inline в AssessmentSchedule, но можно
    редактировать и напрямую.
    """
    list_display = ('id_assessment_teacher', 'schedule', 'teacher', 'role')
    list_filter = ('role', 'schedule__group')
    search_fields = (
        'teacher__last_name',
        'teacher__first_name',
        'teacher__middle_name',
        'teacher__email',
        'schedule__group__id_group',
        'schedule__discipline_in_group__discipline_ref__name',
    )
    autocomplete_fields = ('teacher', 'schedule')
    search_help_text = 'Поиск по ФИО/email преподавателя, ID группы или названию дисциплины'


# ==============================================================================
# 👨 ГРУППА 4: СТУДЕНТЫ И ИХ ДАННЫЕ
# ==============================================================================

class PassportAdmin(BaseAdmin):
    resource_class = resources.PassportResource
    list_display = ('id_passport', 'series_number', 'citizenship', 'is_foreigner')
    list_filter = ('is_foreigner', 'citizenship')
    search_fields = ('series_number', 'issuer', 'unit_code', 'region_city')
    search_help_text = 'Поиск по серии/номеру, кем выдан, коду подразделения или региону'


class HealthAdmin(BaseAdmin):
    resource_class = resources.HealthResource
    list_display = ('id_health', 'status', 'oms_number')
    list_filter = ('status',)
    search_fields = ('oms_number', 'oms_issuer')
    search_help_text = 'Поиск по номеру полиса ОМС или страховой компании'


class MilitaryAdmin(BaseAdmin):
    resource_class = resources.MilitaryResource
    list_display = ('id_military', 'registration_number', 'fitness_category')
    list_filter = ('fitness_category',)
    search_fields = ('registration_number', 'commissariat')
    search_help_text = 'Поиск по номеру приписного или военкомату'


class FamilyAdmin(BaseAdmin):
    resource_class = resources.FamilyResource
    list_display = ('id_family', 'status', 'housing_type', 'minors_count')
    list_filter = ('status', 'housing_type')
    search_fields = ('id_family',)
    search_help_text = 'Поиск по ID семьи'


class FamilyMemberAdmin(BaseAdmin):
    resource_class = resources.FamilyMemberResource
    list_display = ('full_name', 'relation', 'family', 'is_pensioner', 'is_svo', 'is_priority_contact')
    list_filter = ('relation', 'is_pensioner', 'is_svo', 'is_priority_contact')
    search_fields = ('full_name', 'relation', 'workplace', 'phone')
    search_help_text = 'Поиск по ФИО, степени родства, месту работы или телефону'


class ProfileAdmin(BaseAdmin):
    resource_class = resources.ProfileResource
    list_display = ('id_profile',)
    search_fields = (
        'id_profile', 'programming_langs', 'hobbies',
        'extra_edu', 'sports_ranks', 'character_behavior',
    )
    search_help_text = 'Поиск по языкам программирования, хобби, доп. образованию'


class EducationInstitutionAdmin(BaseAdmin):
    resource_class = resources.EducationInstitutionResource
    list_display = ('name', 'type', 'graduation_date')
    list_filter = ('type',)
    search_fields = ('name', 'profile')
    search_help_text = 'Поиск по названию учебного заведения или профилю класса'


class StudentAdmin(BaseAdmin):
    resource_class = resources.StudentResource
    list_display = ('snils', 'get_full_name', 'group', 'status', 'last_change')
    list_filter = ('status', 'group', 'gender', 'study_plan')
    search_fields = (
        'snils', 'inn', 'phone',
        'user__email', 'user__last_name', 'user__first_name', 'user__middle_name',
        'group__id_group', 'birth_place',
    )
    search_help_text = 'Поиск по СНИЛС, ИНН, телефону, email, ФИО, группе или месту рождения'

    def get_full_name(self, obj):
        if obj.user:
            return f"{obj.user.last_name} {obj.user.first_name}"
        return "Без ФИО"
    get_full_name.short_description = 'ФИО'


# ==============================================================================
# 💼 ГРУППА 5: ТРУДОУСТРОЙСТВО И ОРГАНИЗАЦИИ
# ==============================================================================

class OrganizationAdmin(BaseAdmin):
    resource_class = resources.OrganizationResource
    list_display = ('inn', 'short_name', 'legal_name', 'city', 'region')
    search_fields = (
        'inn', 'legal_name', 'short_name', 'kpp', 'ogrn',
        'city', 'region', 'street', 'email',
        'director_name', 'responsible_name', 'mentor_name',
    )
    search_help_text = 'Поиск по ИНН, названию, городу, email или ФИО директора/наставника'


class EmploymentAdmin(BaseAdmin):
    resource_class = resources.EmploymentResource
    list_display = ('student', 'organization', 'employment_type', 'is_cluster_partner', 'position')
    list_filter = ('employment_type', 'is_cluster_partner', 'is_by_profession')
    search_fields = (
        'position',
        'student__snils', 'student__user__last_name', 'student__user__first_name',
        'organization__inn', 'organization__short_name',
    )
    search_help_text = 'Поиск по должности, СНИЛС/ФИО студента или ИНН/названию организации'


class TargetContractAdmin(BaseAdmin):
    resource_class = resources.TargetContractResource
    list_display = ('id_contract', 'student', 'has_contract', 'company_name')
    list_filter = ('has_contract',)
    search_fields = (
        'id_contract', 'number', 'company_name',
        'student__snils', 'student__user__last_name',
    )
    search_help_text = 'Поиск по ID/номеру договора, предприятию или ФИО студента'


# ==============================================================================
# 🏢 ГРУППА 6: ПРАКТИКА
# ==============================================================================

class PracticeOrderAdmin(BaseAdmin):
    resource_class = resources.PracticeOrderResource
    list_display = ('id_order', 'number', 'date', 'type', 'group')
    list_filter = ('type', 'date', 'group')
    search_fields = ('id_order', 'number', 'group__id_group')
    search_help_text = 'Поиск по ID/номеру приказа или ID группы'


class ModuleAdmin(BaseAdmin):
    resource_class = resources.ModuleResource
    list_display = ('id_module', 'code', 'name', 'group')
    list_filter = ('group',)
    search_fields = ('id_module', 'code', 'name', 'group__id_group')
    search_help_text = 'Поиск по ID/коду/названию модуля или ID группы'


class PracticeOrderModuleAdmin(BaseAdmin):
    resource_class = resources.PracticeOrderModuleResource
    list_display = ('order', 'module')
    search_fields = (
        'order__number', 'order__id_order',
        'module__code', 'module__name',
    )
    search_help_text = 'Поиск по номеру приказа или коду/названию модуля'


class StudentPracticePlaceAdmin(BaseAdmin):
    resource_class = resources.StudentPracticePlaceResource
    list_display = ('student', 'organization', 'order', 'status', 'position')
    list_filter = ('status', 'order')
    search_fields = (
        'position',
        'student__snils', 'student__user__last_name', 'student__user__first_name',
        'organization__inn', 'organization__short_name', 'organization__legal_name',
        'order__number',
    )
    search_help_text = 'Поиск по должности, СНИЛС/ФИО студента, ИНН/названию организации или номеру приказа'


class PracticeTaskAdmin(BaseAdmin):
    resource_class = resources.PracticeTaskResource
    list_display = ('topic_number', 'topic_name', 'practice_place', 'hours')
    search_fields = (
        'topic_number', 'topic_name', 'work_types', 'competencies',
        'practice_place__student__snils',
        'practice_place__student__user__last_name',
    )
    search_help_text = 'Поиск по номеру/названию темы, видам работ, компетенциям или СНИЛС студента'


class PracticeDiaryAdmin(BaseAdmin):
    resource_class = resources.PracticeDiaryResource
    list_display = ('date', 'practice_place', 'hours', 'is_approved_by_org')
    list_filter = ('is_approved_by_org', 'date')
    search_fields = (
        'work_content',
        'practice_place__student__snils',
        'practice_place__student__user__last_name',
        'practice_place__organization__short_name',
    )
    search_help_text = 'Поиск по содержанию работы, СНИЛС/ФИО студента или организации'


class PracticeControlPointAdmin(BaseAdmin):
    resource_class = resources.PracticeControlPointResource
    list_display = ('control_date', 'practice_place', 'is_signed_by_org')
    list_filter = ('is_signed_by_org',)
    search_fields = (
        'work_done',
        'practice_place__student__snils',
        'practice_place__student__user__last_name',
    )
    search_help_text = 'Поиск по выполненной работе, СНИЛС или ФИО студента'


class PracticeAttestationAdmin(BaseAdmin):
    resource_class = resources.PracticeAttestationResource
    list_display = ('practice_place', 'recommended_grade', 'fill_date')
    list_filter = ('recommended_grade',)
    search_fields = (
        'characteristic_text',
        'practice_place__student__snils',
        'practice_place__student__user__last_name',
        'practice_place__student__user__first_name',
    )
    search_help_text = 'Поиск по тексту характеристики, СНИЛС или ФИО студента'


# ==============================================================================
# 📊 ГРУППА 7: ОЦЕНКИ И АТТЕСТАЦИЯ
# ==============================================================================

class StatementAdmin(BaseAdmin):
    resource_class = resources.StatementResource
    list_display = ('number', 'group', 'discipline_in_group', 'teacher', 'status')
    list_filter = ('status', 'group')
    search_fields = (
        'number',
        'group__id_group',
        'discipline_in_group__discipline_ref__code',
        'discipline_in_group__discipline_ref__name',
        'teacher__email', 'teacher__last_name',
    )
    search_help_text = 'Поиск по номеру ведомости, ID группы, коду дисциплины или преподавателю'


class StatementGradeAdmin(BaseAdmin):
    resource_class = resources.StatementGradeResource
    list_display = ('student', 'statement', 'grade', 'date', 'is_retake')
    list_filter = ('grade', 'is_retake', 'statement')
    search_fields = (
        'grade',
        'student__snils', 'student__user__last_name', 'student__user__first_name',
        'statement__number',
    )
    search_help_text = 'Поиск по оценке, СНИЛС/ФИО студента или номеру ведомости'


class GEKProtocolAdmin(BaseAdmin):
    resource_class = resources.GEKProtocolResource
    list_display = ('number', 'group', 'date', 'gia_type', 'chairman')
    list_filter = ('gia_type', 'date', 'group')
    search_fields = (
        'number',
        'group__id_group',
        'chairman__email', 'chairman__last_name',
    )
    search_help_text = 'Поиск по номеру протокола, ID группы или ФИО председателя'


class GEKMemberAdmin(BaseAdmin):
    resource_class = resources.GEKMemberResource
    list_display = ('protocol', 'user', 'role')
    list_filter = ('role',)
    search_fields = (
        'role',
        'protocol__number',
        'user__email', 'user__last_name', 'user__first_name',
    )
    search_help_text = 'Поиск по роли, номеру протокола или email/ФИО пользователя'


class GIAResultAdmin(BaseAdmin):
    resource_class = resources.GIAResultResource
    list_display = ('student', 'protocol', 'final_gia_grade', 'de_grade', 'diploma_grade')
    list_filter = ('final_gia_grade', 'protocol')
    search_fields = (
        'diploma_topic',
        'de_grade', 'diploma_grade', 'final_gia_grade',
        'student__snils', 'student__user__last_name', 'student__user__first_name',
        'protocol__number',
        'diploma_supervisor__last_name',
    )
    search_help_text = 'Поиск по теме диплома, оценкам, СНИЛС/ФИО студента, номеру протокола или руководителю'


class GIADefenseQuestionAdmin(BaseAdmin):
    resource_class = resources.GIADefenseQuestionResource
    list_display = ('gia_result', 'question_number', 'expert')
    search_fields = (
        'question_text', 'student_answer',
        'gia_result__student__snils',
        'gia_result__student__user__last_name',
        'expert__email', 'expert__last_name',
    )
    search_help_text = 'Поиск по тексту вопроса/ответа, СНИЛС/ФИО студента или эксперту'


# ==============================================================================
# 📅 ГРУППА 8: ПОСЕЩАЕМОСТЬ
# ==============================================================================

class AttendanceTableAdmin(BaseAdmin):
    resource_class = resources.AttendanceTableResource
    list_display = ('group', 'month', 'year', 'curator')
    list_filter = ('year', 'month', 'group')
    search_fields = (
        'group__id_group',
        'curator__email', 'curator__last_name',
    )
    search_help_text = 'Поиск по ID группы или email/ФИО куратора'


class AttendanceTableRowAdmin(BaseAdmin):
    resource_class = resources.AttendanceTableRowResource
    list_display = ('student', 'table', 'study_days', 'sick_leave', 'practice', 'truancy')
    list_filter = ('table',)
    search_fields = (
        'student__snils', 'student__user__last_name', 'student__user__first_name',
        'table__group__id_group',
    )
    search_help_text = 'Поиск по СНИЛС/ФИО студента или ID группы табеля'


# ==============================================================================
# РЕГИСТРАЦИЯ ВСЕХ МОДЕЛЕЙ В admin.site
# ==============================================================================

# 📚 ГРУППА 1: СПРАВОЧНИКИ
admin.site.register(Role, RoleAdmin)
admin.site.register(Campus, CampusAdmin)
admin.site.register(Specialty, SpecialtyAdmin)
admin.site.register(DocumentType, DocumentTypeAdmin)
admin.site.register(Country, CountryAdmin)
admin.site.register(Region, RegionAdmin)
admin.site.register(CityDistrict, CityDistrictAdmin)
admin.site.register(Industry, IndustryAdmin)
admin.site.register(EmploymentType, EmploymentTypeAdmin)
admin.site.register(FinancialAidGround, FinancialAidGroundAdmin)
admin.site.register(Setting, SettingAdmin)
admin.site.register(DocumentGenerationType, DocumentGenerationTypeAdmin)
admin.site.register(DisciplineReference, DisciplineReferenceAdmin)

# 👥 ГРУППА 2: ПОЛЬЗОВАТЕЛИ И БАЗОВЫЕ СУЩНОСТИ
admin.site.register(User, UserAdmin)
admin.site.register(UserRole, UserRoleAdmin)
admin.site.register(Qualification, QualificationAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(MCK, MCKAdmin)

# 🎓 ГРУППА 3: ГРУППЫ И ДИСЦИПЛИНЫ
admin.site.register(Group, GroupAdmin)
admin.site.register(DisciplineInGroup, DisciplineInGroupAdmin)
admin.site.register(AssessmentSchedule, AssessmentScheduleAdmin)
admin.site.register(AssessmentTeacher, AssessmentTeacherAdmin)  # <-- НОВАЯ МОДЕЛЬ

# 👨 ГРУППА 4: СТУДЕНТЫ И ИХ ДАННЫЕ
admin.site.register(Passport, PassportAdmin)
admin.site.register(Health, HealthAdmin)
admin.site.register(Military, MilitaryAdmin)
admin.site.register(Family, FamilyAdmin)
admin.site.register(FamilyMember, FamilyMemberAdmin)
admin.site.register(Profile, ProfileAdmin)
admin.site.register(EducationInstitution, EducationInstitutionAdmin)
admin.site.register(Student, StudentAdmin)

# 💼 ГРУППА 5: ТРУДОУСТРОЙСТВО И ОРГАНИЗАЦИИ
admin.site.register(Organization, OrganizationAdmin)
admin.site.register(Employment, EmploymentAdmin)
admin.site.register(TargetContract, TargetContractAdmin)

# 🏢 ГРУППА 6: ПРАКТИКА
admin.site.register(PracticeOrder, PracticeOrderAdmin)
admin.site.register(Module, ModuleAdmin)
admin.site.register(PracticeOrderModule, PracticeOrderModuleAdmin)
admin.site.register(StudentPracticePlace, StudentPracticePlaceAdmin)
admin.site.register(PracticeTask, PracticeTaskAdmin)
admin.site.register(PracticeDiary, PracticeDiaryAdmin)
admin.site.register(PracticeControlPoint, PracticeControlPointAdmin)
admin.site.register(PracticeAttestation, PracticeAttestationAdmin)

# 📊 ГРУППА 7: ОЦЕНКИ И АТТЕСТАЦИЯ
admin.site.register(Statement, StatementAdmin)
admin.site.register(StatementGrade, StatementGradeAdmin)
admin.site.register(GEKProtocol, GEKProtocolAdmin)
admin.site.register(GEKMember, GEKMemberAdmin)
admin.site.register(GIAResult, GIAResultAdmin)
admin.site.register(GIADefenseQuestion, GIADefenseQuestionAdmin)

# 📅 ГРУППА 8: ПОСЕЩАЕМОСТЬ
admin.site.register(AttendanceTable, AttendanceTableAdmin)
admin.site.register(AttendanceTableRow, AttendanceTableRowAdmin)
