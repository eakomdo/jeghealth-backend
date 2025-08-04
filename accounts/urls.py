from django.urls import path, re_path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

urlpatterns = [
    # Authentication endpoints (with flexible slash handling)
    re_path(r'^register/?$', views.RegisterView.as_view(), name='register'),
    re_path(r'^register-with-profile/?$', views.ComprehensiveRegisterView.as_view(), name='register_with_profile'),
    re_path(r'^login/?$', views.LoginView.as_view(), name='login'),
    re_path(r'^logout/?$', views.LogoutView.as_view(), name='logout'),
    re_path(r'^token/refresh/?$', TokenRefreshView.as_view(), name='token_refresh'),
    
    # User profile endpoints
    re_path(r'^profile/?$', views.UserProfileView.as_view(), name='user_profile'),
    re_path(r'^profile/details/?$', views.UserProfileDetailView.as_view(), name='user_profile_details'),
    re_path(r'^change-password/?$', views.ChangePasswordView.as_view(), name='change_password'),
    re_path(r'^current-user/?$', views.CurrentUserView.as_view(), name='current_user'),
    
    # Role management endpoints (admin only)
    re_path(r'^roles/?$', views.RoleListCreateView.as_view(), name='roles'),
    re_path(r'^assign-role/?$', views.assign_role_to_user, name='assign_role'),

    # Basic and personal information endpoints
    re_path(r'^profile/basic/?$', views.BasicInformationView.as_view(), name='profile_basic'),
    re_path(r'^profile/personal/?$', views.PersonalInformationView.as_view(), name='profile_personal'),
]
