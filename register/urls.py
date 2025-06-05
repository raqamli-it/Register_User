from django.urls import path
from .views import RegisterView, LoginView, ForgotPasswordView, SetNewPasswordView, VerifyEmailView, LogoutAPIView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutAPIView.as_view(), name='logout'),
    path('forgot-password/', ForgotPasswordView.as_view(), name='forgot-password'),
    path('set-new-password/', SetNewPasswordView.as_view(), name='set-new-password'),
    path('verify-email/', VerifyEmailView.as_view(), name='verify-email'),
    # ✅ bu yerda int:user_id BO‘LMASLIGI kerak
]
