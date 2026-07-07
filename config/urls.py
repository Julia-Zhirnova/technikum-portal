from django.contrib import admin
from django.urls import path, include
from accounts import views as account_views
from core import api_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', account_views.hello, name='hello'),
    path('api/campuses/', account_views.api_campuses, name='api_campuses'),
    
    # Новые API эндпоинты для личных кабинетов
    path('api/whoami/', api_views.WhoAmIView.as_view(), name='whoami'),
    path('api/student/profile/', api_views.StudentProfileView.as_view(), name='student_profile'),
    path('api/curator/group/', api_views.CuratorGroupView.as_view(), name='curator_group'),
    path('api/teacher/statements/', api_views.TeacherStatementsView.as_view(), name='teacher_statements'),
    
    # JWT аутентификация (для будущего использования)
    path('api/auth/', include('rest_framework.urls')),
]
