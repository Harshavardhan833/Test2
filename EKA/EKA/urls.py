from django.urls import path
from . import views
from django.contrib import admin


urlpatterns = [
    path('users/', views.users, name='EKA_users'),
    path('admin/', admin.site.urls),
    path('index/', views.index, name='EKA_index'),
    # path('admin/', views.admin, name='EKA_admin'),
    # path('health-check/', views.health_check, name='EKA_health_check'),
    # path('about/', views.about, name='EKA_about'),
    path('details/<int:user_id>/', views.details, name='EKA_details'),
    path('', views.main, name='main'),
    path('testing/', views.testing, name='testing'),  
]