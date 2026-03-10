"""
URL configuration for supercareer project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path

from accounts.views import RegisterView, ProfileView, CustomTokenObtainPairView, LogoutView
from notifications.views import ForgotPasswordView, VerifyOTPView, ResetPasswordView
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('admin/', admin.site.urls),
    
    path('api/register/', RegisterView.as_view()),
    path('api/login/', CustomTokenObtainPairView.as_view()),
    path('api/logout/', LogoutView.as_view()),
    path('api/token/refresh/', TokenRefreshView.as_view()),

    path('api/forgot-password/', ForgotPasswordView.as_view()),
    path('api/verify-otp/', VerifyOTPView.as_view()),
    path('api/reset-password/', ResetPasswordView.as_view()),

    path('api/profile/', ProfileView.as_view()),
]
