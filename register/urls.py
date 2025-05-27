from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenBlacklistView,
)
from register.views import RegisterView, VerifyEmail, ForgotPasswordView, ResetPasswordConfirmView, SetNewPasswordView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('email-verify/<int:uid>/<str:token>/', VerifyEmail.as_view(), name='email-verify'),
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('logout/', TokenBlacklistView.as_view(), name='token_blacklist'),
    path('reset-password-confirm/<int:uid>/<str:token>/', ResetPasswordConfirmView.as_view(), name='reset-password-confirm'),
    path('forgot-password/', ForgotPasswordView.as_view(), name='forgot-password'),
    path('set-new-password/', SetNewPasswordView.as_view(), name='set-new-password'),

]
