from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from core import api_views
from core import student_views as personal_data_views
from core.api_views import (
    StudentPracticeView, StudentRequestView, NotificationView,
    TeacherPracticeStudentsView, CuratorStudentRequestsView,
    CuratorStudentPracticeView
)

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Аутентификация JWT
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # Смена пароля
    path('api/auth/force-change-password/', api_views.ForcePasswordChangeView.as_view(), name='force-change-password'),
    
    # Корпуса
    path('api/campuses/', api_views.CampusListView.as_view(), name='campuses'),
    
    # Существующие API (Блоки 1, 5)
    path('api/user/profile/', api_views.UserProfileView.as_view(), name='user-profile'),
    path('api/student/profile/', api_views.StudentProfileView.as_view(), name='student-profile-legacy'),
    path('api/teacher/statements/', api_views.TeacherStatementsView.as_view(), name='teacher_statements'),
    path('api/teacher/statements/<int:statement_id>/grades/', api_views.TeacherStatementGradesView.as_view(), name='teacher-statement-grades'),
    path('api/teacher/statements/<int:statement_id>/export/', api_views.StatementGradesExportView.as_view(), name='teacher-statement-export'),
    path('api/teacher/statements/<int:statement_id>/import/', api_views.StatementGradesImportView.as_view(), name='teacher-statement-import'),
    path('api/teacher/statements/<int:statement_id>/generate-docx/', api_views.StatementGenerateDocxView.as_view(), name='teacher-statement-generate-docx'),
    path('api/teacher/grades/<int:grade_id>/', api_views.UpdateGradeView.as_view(), name='update-grade'),
    path('api/student/grades/', api_views.StudentGradesView.as_view(), name='student_grades'),
    path('api/student/requests/', StudentRequestView.as_view(), name='student-requests'),
    path('api/student/notifications/', NotificationView.as_view(), name='student-notifications'),
    path('api/student/practice/', StudentPracticeView.as_view(), name='student-practice'),
    path('api/curator/group/', api_views.CuratorGroupView.as_view(), name='curator_group'),
    path('api/curator/requests/', CuratorStudentRequestsView.as_view(), name='curator-requests'),
    path('api/curator/practice/', CuratorStudentPracticeView.as_view(), name='curator-practice'),
    path('api/teacher/practice/students/', TeacherPracticeStudentsView.as_view(), name='teacher-practice-students'),
    path('api/admin/users/', api_views.AdminUsersView.as_view(), name='admin_users'),
    path('api/whoami/', api_views.WhoAmIView.as_view(), name='whoami'),
    path('api/references/', api_views.ReferencesView.as_view(), name='references'),
    
    # API персональных данных студента (Блок 2)
    path('api/v1/student/profile/', personal_data_views.StudentProfileView.as_view(), name='student-profile'),
    path('api/v1/student/passport/', personal_data_views.PassportView.as_view(), name='student-passport'),
    path('api/v1/student/health/', personal_data_views.HealthView.as_view(), name='student-health'),
    path('api/v1/student/military/', personal_data_views.MilitaryView.as_view(), name='student-military'),
    path('api/v1/student/family/', personal_data_views.FamilyView.as_view(), name='student-family'),
    path('api/v1/student/family/members/', personal_data_views.FamilyMemberListCreateView.as_view(), name='student-family-members'),
    path('api/v1/student/family/members/<int:pk>/', personal_data_views.FamilyMemberDetailView.as_view(), name='student-family-member-detail'),
    path('api/v1/student/education/', personal_data_views.EducationInstitutionView.as_view(), name='student-education'),
]
