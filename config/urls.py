from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from accounts import views as account_views
from core import api_views
from core.views_restore_statement import RestoreStatementView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', account_views.hello, name='hello'),
    path('api/campuses/', account_views.api_campuses, name='api_campuses'),
    
    # JWT аутентификация
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/auth/change-password/', account_views.ChangePasswordView.as_view(), name='change-password'),
    
    # Универсальные
    path('api/whoami/', api_views.WhoAmIView.as_view(), name='whoami'),
    
    # Студент
    path('api/student/profile/', api_views.StudentProfileView.as_view(), name='student_profile'),
    path('api/student/profile/update/', api_views.StudentProfileUpdateView.as_view(), name='student_profile_update'),
    path('api/student/grades/', api_views.StudentGradesView.as_view(), name='student_grades'),
    # Студент: Заявки и уведомления
    path('api/student/requests/', api_views.StudentRequestView.as_view(), name='student_requests'),
    path('api/student/notifications/', api_views.NotificationView.as_view(), name='student_notifications'),
    path('api/student/notifications/<int:notification_id>/read/', api_views.MarkNotificationReadView.as_view(), name='mark_notification_read'),

    path('api/references/', api_views.ReferencesView.as_view(), name='references'),
    path('api/user/profile/', api_views.UserProfileView.as_view(), name='user_profile'),
    
    # Куратор
    path('api/curator/group/', api_views.CuratorGroupView.as_view(), name='curator_group'),
    path('api/curator/students/<str:snils>/', api_views.CuratorStudentDetailView.as_view(), name='curator_student_detail'),
    # Куратор: Заявки студентов
    path('api/curator/requests/', api_views.CuratorStudentRequestsView.as_view(), name='curator_requests'),
    path('api/curator/requests/<int:request_id>/', api_views.CuratorUpdateRequestView.as_view(), name='curator_update_request'),

    # Практика студента
    path('api/student/practice/', api_views.StudentPracticeView.as_view(), name='student_practice'),
    path('api/curator/practice/', api_views.CuratorStudentPracticeView.as_view(), name='curator_practice'),

    # Практика для преподавателя
    path('api/teacher/practice/students/', api_views.TeacherPracticeStudentsView.as_view(), name='teacher_practice_students'),
    path('api/teacher/practice/place/<int:place_id>/', api_views.TeacherUpdatePracticePlaceView.as_view(), name='teacher_update_practice_place'),
    path('api/teacher/practice/diary/<int:entry_id>/', api_views.TeacherApproveDiaryEntryView.as_view(), name='teacher_approve_diary_entry'),



    
    # Преподаватель
    path('api/teacher/statements/', api_views.TeacherStatementsView.as_view(), name='teacher_statements'),
    
    # Session auth (для тестирования через браузер)
    path('api/auth/', include('rest_framework.urls')),
path('api/teacher/grades/<int:grade_id>/', api_views.UpdateGradeView.as_view(), name='update-grade'),
    path('api/teacher/statements/<int:statement_id>/restore/', RestoreStatementView.as_view(), name='restore-statement'),
    path('api/teacher/statements/<int:statement_id>/grades/', api_views.TeacherStatementGradesView.as_view(), name='teacher-statement-grades'),
    path('api/teacher/statements/<int:statement_id>/export/', api_views.StatementGradesExportView.as_view(), name='teacher-statement-export'),
    path('api/teacher/statements/<int:statement_id>/debug-export/', api_views.debug_export_fbv, name='debug-export'),
    path('api/teacher/statements/<int:statement_id>/test-export/', api_views.TestExportView.as_view(), name='test-export'),
    path('api/teacher/statements/<int:statement_id>/import/', api_views.StatementGradesImportView.as_view(), name='teacher-statement-import'),
    path('api/teacher/statements/<int:statement_id>/generate-docx/', api_views.StatementGenerateDocxView.as_view(), name='teacher-statement-generate-docx'),
]

# Отдаём медиа-файлы в режиме разработки
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
