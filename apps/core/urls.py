from django.conf.urls import url
from rest_framework import routers

from apps.core.views import \
    UserViewSet, \
    ForgotPasswordView,\
    OTPGenerateView, \
    OTPLoginView, \
    ResetPasswordView

router = routers.DefaultRouter()
router.register(r'', UserViewSet, basename='users')

urlpatterns = [
    url(r'^otp/generate/$', OTPGenerateView.as_view(), name='otp_generate'),
    url(r'^otp/login/$', OTPLoginView.as_view(), name='otp_login'),

    url(r'^forgot-password/$', ForgotPasswordView.as_view(), name='forgot_password_request'),
    url(r'^reset-password/$', ResetPasswordView.as_view(), name='reset_password_request')

]
urlpatterns += router.urls
