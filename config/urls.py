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

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', account_views.hello, name='hello'),
    path('api/campuses/', account_views.api_campuses, name='api_campuses'),
    
    # JWT аутентификация
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # Универсальные
    path('api/whoami/', api_views.WhoAmIView.as_view(), name='whoami'),
    
    # Студент
    path('api/student/profile/', api_views.StudentProfileView.as_view(), name='student_profile'),
    path('api/student/profile/update/', api_views.StudentProfileUpdateView.as_view(), name='student_profile_update'),
    path('api/references/', api_views.ReferencesView.as_view(), name='references'),
    path('api/user/profile/', api_views.UserProfileView.as_view(), name='user_profile'),
    
    # Куратор
    path('api/curator/group/', api_views.CuratorGroupView.as_view(), name='curator_group'),
    path('api/curator/students/<str:snils>/', api_views.CuratorStudentDetailView.as_view(), name='curator_student_detail'),
    
    # Преподаватель
    path('api/teacher/statements/', api_views.TeacherStatementsView.as_view(), name='teacher_statements'),
    
    # Session auth (для тестирования через браузер)
    path('api/auth/', include('rest_framework.urls')),
]

# Отдаём медиа-файлы в режиме разработки
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
