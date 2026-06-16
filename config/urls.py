from django.contrib import admin
from django.urls import path
from accounts import views

urlpatterns = [
    path('admin/', admin.site.urls),  # ← Используем стандартный admin.site
    path('', views.hello, name='hello'),
    path('api/campuses/', views.api_campuses, name='api_campuses'),
]
