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
    MCK, DisciplineReference, DisciplineInGroup, AssessmentSchedule, Statement,
    StatementGrade, GEKProtocol, GEKMember, GIAResult, GIADefenseQuestion,
    AttendanceTable, AttendanceTableRow,
)


# ==============================================================================
# БАЗОВЫЙ КЛАСС АДМИНКИ С ИМПОРТОМ/ЭКСПОРТОМ
# ==============================================================================

class BaseAdmin(ImportExportModelAdmin):
    list_per_page = 50
    save_on_top = True


# ==============================================================================
# 📚 ГРУППА 1: СПРАВОЧНИКИ
# ==============================================================================

class RoleAdmin(BaseAdmin):
    resource_class = resources.RoleResource
    list_display = ('id_role', 'name')
    search_fields = ('name',)


class CampusAdmin(BaseAdmin):
    resource_class = resources.CampusResource
    list_display = ('id_campus', 'address')


class SpecialtyAdmin(BaseAdmin):
    resource_class = resources.SpecialtyResource
    list_display = ('id_specialty', 'name', 'level')
    list_filter = ('level',)


class DocumentTypeAdmin(BaseAdmin):
    resource_class = resources.DocumentTypeResource
    list_display = ('code', 'name')


class CountryAdmin(BaseAdmin):
    resource_class = resources.CountryResource
    list_display = ('id_country', 'name')


class RegionAdmin(BaseAdmin):
    resource_class = resources.RegionResource
    list_display = ('name',)


class CityDistrictAdmin(BaseAdmin):
    resource_class = resources.CityDistrictResource
    list_display = ('name',)


class IndustryAdmin(BaseAdmin):
    resource_class = resources.IndustryResource
    list_display = ('name',)


class EmploymentTypeAdmin(BaseAdmin):
    resource_class = resources.EmploymentTypeResource
    list_display = ('name',)


class FinancialAidGroundAdmin(BaseAdmin):
    resource_class = resources.FinancialAidGroundResource
    list_display = ('name', 'requires_mo')
    list_filter = ('requires_mo',)


class SettingAdmin(BaseAdmin):
    resource_class = resources.SettingResource
    list_display = ('field_name', 'value')


class DocumentGenerationTypeAdmin(BaseAdmin):
    resource_class = resources.DocumentGenerationTypeResource
    list_display = ('code', 'name', 'template_path')


class DisciplineReferenceAdmin(BaseAdmin):
    resource_class = resources.DisciplineReferenceResource
    list_display = ('code', 'name', 'type')
    list_filter = ('type',)
    search_fields = ('code', 'name')


# ==============================================================================
# 👥 ГРУППА 2: ПОЛЬЗОВАТЕЛИ И БАЗОВЫЕ СУЩНОСТИ
# ==============================================================================

class UserAdmin(BaseAdmin):
    resource_class = resources.UserResource
    list_display = ('email', 'last_name', 'first_name', 'is_active', 'requires_password_change')
    list_filter = ('is_active', 'requires_password_change')
    search_fields = ('email', 'last_name', 'first_name')


class UserRoleAdmin(BaseAdmin):
    resource_class = resources.UserRoleResource
    list_display = ('user', 'role')
    list_filter = ('role',)


class QualificationAdmin(BaseAdmin):
    resource_class = resources.QualificationResource
    list_display = ('name', 'specialty', 'professionalitet_role')
    list_filter = ('professionalitet_role', 'specialty')


class OrderAdmin(BaseAdmin):
    resource_class = resources.OrderResource
    list_display = ('id_order', 'number', 'date', 'type')
    list_filter = ('type', 'date')


class MCKAdmin(BaseAdmin):
    resource_class = resources.MCKResource
    list_display = ('name', 'short_name', 'chairman')


# ==============================================================================
# 🎓 ГРУППА 3: ГРУППЫ И ДИСЦИПЛИНЫ
# ==============================================================================

class GroupAdmin(BaseAdmin):
    resource_class = resources.GroupResource
    list_display = ('id_group', 'qualification', 'year_start', 'form', 'financing', 'campus')
    list_filter = ('form', 'financing', 'campus', 'year_start')
    search_fields = ('id_group',)


class DisciplineInGroupAdmin(BaseAdmin):
    resource_class = resources.DisciplineInGroupResource
    list_display = ('discipline_ref', 'group', 'semester', 'assessment_form', 'mck')
    list_filter = ('semester', 'assessment_form', 'group', 'mck')


class AssessmentScheduleAdmin(BaseAdmin):
    resource_class = resources.AssessmentScheduleResource
    list_display = ('discipline_in_group', 'group', 'date', 'time', 'teacher', 'retake_date')
    list_filter = ('group', 'date', 'teacher')


# ==============================================================================
# 👨 ГРУППА 4: СТУДЕНТЫ И ИХ ДАННЫЕ
# ==============================================================================

class PassportAdmin(BaseAdmin):
    resource_class = resources.PassportResource
    list_display = ('id_passport', 'series_number', 'citizenship', 'is_foreigner')
    list_filter = ('is_foreigner', 'citizenship')


class HealthAdmin(BaseAdmin):
    resource_class = resources.HealthResource
    list_display = ('id_health', 'status', 'oms_number')
    list_filter = ('status',)


class MilitaryAdmin(BaseAdmin):
    resource_class = resources.MilitaryResource
    list_display = ('id_military', 'registration_number', 'fitness_category')
    list_filter = ('fitness_category',)


class FamilyAdmin(BaseAdmin):
    resource_class = resources.FamilyResource
    list_display = ('id_family', 'status', 'housing_type', 'minors_count')
    list_filter = ('status', 'housing_type')


class FamilyMemberAdmin(BaseAdmin):
    resource_class = resources.FamilyMemberResource
    list_display = ('full_name', 'relation', 'family', 'is_pensioner', 'is_svo', 'is_priority_contact')
    list_filter = ('relation', 'is_pensioner', 'is_svo', 'is_priority_contact')
    search_fields = ('full_name',)


class ProfileAdmin(BaseAdmin):
    resource_class = resources.ProfileResource
    list_display = ('id_profile',)


class EducationInstitutionAdmin(BaseAdmin):
    resource_class = resources.EducationInstitutionResource
    list_display = ('name', 'type', 'graduation_date')
    list_filter = ('type',)


class StudentAdmin(BaseAdmin):
    resource_class = resources.StudentResource
    list_display = ('snils', 'get_full_name', 'group', 'status', 'last_change')
    list_filter = ('status', 'group', 'gender', 'study_plan')
    search_fields = ('snils', 'user__last_name', 'user__first_name')

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
    search_fields = ('inn', 'short_name', 'legal_name')


class EmploymentAdmin(BaseAdmin):
    resource_class = resources.EmploymentResource
    list_display = ('student', 'organization', 'employment_type', 'is_cluster_partner', 'position')
    list_filter = ('employment_type', 'is_cluster_partner', 'is_by_profession')


class TargetContractAdmin(BaseAdmin):
    resource_class = resources.TargetContractResource
    list_display = ('id_contract', 'student', 'has_contract', 'company_name')
    list_filter = ('has_contract',)


# ==============================================================================
# 🏢 ГРУППА 6: ПРАКТИКА
# ==============================================================================

class PracticeOrderAdmin(BaseAdmin):
    resource_class = resources.PracticeOrderResource
    list_display = ('id_order', 'number', 'date', 'type', 'group')
    list_filter = ('type', 'date', 'group')


class ModuleAdmin(BaseAdmin):
    resource_class = resources.ModuleResource
    list_display = ('id_module', 'code', 'name', 'group')
    list_filter = ('group',)


class PracticeOrderModuleAdmin(BaseAdmin):
    resource_class = resources.PracticeOrderModuleResource
    list_display = ('order', 'module')


class StudentPracticePlaceAdmin(BaseAdmin):
    resource_class = resources.StudentPracticePlaceResource
    list_display = ('student', 'organization', 'order', 'status', 'position')
    list_filter = ('status', 'order')
    search_fields = ('student__user__last_name', 'organization__short_name')


class PracticeTaskAdmin(BaseAdmin):
    resource_class = resources.PracticeTaskResource
    list_display = ('topic_number', 'topic_name', 'practice_place', 'hours')


class PracticeDiaryAdmin(BaseAdmin):
    resource_class = resources.PracticeDiaryResource
    list_display = ('date', 'practice_place', 'hours', 'is_approved_by_org')
    list_filter = ('is_approved_by_org', 'date')


class PracticeControlPointAdmin(BaseAdmin):
    resource_class = resources.PracticeControlPointResource
    list_display = ('control_date', 'practice_place', 'is_signed_by_org')
    list_filter = ('is_signed_by_org',)


class PracticeAttestationAdmin(BaseAdmin):
    resource_class = resources.PracticeAttestationResource
    list_display = ('practice_place', 'recommended_grade', 'fill_date')
    list_filter = ('recommended_grade',)


# ==============================================================================
# 📊 ГРУППА 7: ОЦЕНКИ И АТТЕСТАЦИЯ
# ==============================================================================

class StatementAdmin(BaseAdmin):
    resource_class = resources.StatementResource
    list_display = ('number', 'group', 'discipline_in_group', 'teacher', 'status')
    list_filter = ('status', 'group')


class StatementGradeAdmin(BaseAdmin):
    resource_class = resources.StatementGradeResource
    list_display = ('student', 'statement', 'grade', 'date', 'is_retake')
    list_filter = ('grade', 'is_retake', 'statement')


class GEKProtocolAdmin(BaseAdmin):
    resource_class = resources.GEKProtocolResource
    list_display = ('number', 'group', 'date', 'gia_type', 'chairman')
    list_filter = ('gia_type', 'date', 'group')


class GEKMemberAdmin(BaseAdmin):
    resource_class = resources.GEKMemberResource
    list_display = ('protocol', 'user', 'role')
    list_filter = ('role',)


class GIAResultAdmin(BaseAdmin):
    resource_class = resources.GIAResultResource
    list_display = ('student', 'protocol', 'final_gia_grade', 'de_grade', 'diploma_grade')
    list_filter = ('final_gia_grade', 'protocol')


class GIADefenseQuestionAdmin(BaseAdmin):
    resource_class = resources.GIADefenseQuestionResource
    list_display = ('gia_result', 'question_number', 'expert')


# ==============================================================================
# 📅 ГРУППА 8: ПОСЕЩАЕМОСТЬ
# ==============================================================================

class AttendanceTableAdmin(BaseAdmin):
    resource_class = resources.AttendanceTableResource
    list_display = ('group', 'month', 'year', 'curator')
    list_filter = ('year', 'month', 'group')


class AttendanceTableRowAdmin(BaseAdmin):
    resource_class = resources.AttendanceTableRowResource
    list_display = ('student', 'table', 'study_days', 'sick_leave', 'practice', 'truancy')
    list_filter = ('table',)


# ==============================================================================
# РЕГИСТРАЦИЯ ВСЕХ МОДЕЛЕЙ В admin.site
# ==============================================================================
# admin.site автоматически заменён на CustomAdminSite благодаря CustomAdminConfig
# в INSTALLED_APPS. Все регистрации выполнятся на CustomAdminSite.

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
