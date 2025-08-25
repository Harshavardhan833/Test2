from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    LoginAPI, LogoutAPI, RegisterAPI, UserProfileAPI, DashboardStatsAPI, 
    VehicleSelectionAPI, VehicleAnalysisAPI, TrailsAPI, ReportsAPI, UserListAPI, HealthCheckAPI
)

urlpatterns = [
    path('auth/login/', LoginAPI.as_view(), name='login'),
    path('auth/logout/', LogoutAPI.as_view(), name='logout'), 
    path('auth/register/', RegisterAPI.as_view(), name='register'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    path('auth/me/', UserProfileAPI.as_view(), name='user-profile'),
    path('users/list/', UserListAPI.as_view(), name='user-list'), 
     path('health/', HealthCheckAPI.as_view(), name='health-check'),

    path('dashboard-stats/', DashboardStatsAPI.as_view(), name='dashboard-stats'),
    path('vehicle-selection/', VehicleSelectionAPI.as_view(), name='vehicle-selection'),
    path('vehicle-analysis/', VehicleAnalysisAPI.as_view(), name='vehicle-analysis'),
    path('trails/', TrailsAPI.as_view(), name='trails'),
    path('reports/', ReportsAPI.as_view(), name='reports'),
]