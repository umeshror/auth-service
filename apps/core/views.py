from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.hashers import make_password
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework.exceptions import PermissionDenied
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from apps.core.models import User
from apps.core.utilities.email_helper import send_templated_email
from apps.core.utilities.otp import get_new_otp, check_valid_otp
from apps.core.utilities.sms_helper import send_templated_sms
from apps.core.utilities.user_helper import get_jwt_token


class UserProfileSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='get_full_name')
    profile_pic = serializers.CharField(source='profile_picture_url')

    class Meta:
        model = User
        fields = (
            'id',
            'name',
            'profile_pic'
        )


class UserSerializer(serializers.HyperlinkedModelSerializer):
    password = serializers.CharField(write_only=True)
    username = serializers.CharField(write_only=True)
    id = serializers.IntegerField(read_only=True)

    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'first_name',
            'last_name',
            'password',
            'username')


class UserViewSet(ModelViewSet):
    """
    User API used for listing of users
    and creating new user
    This is Admin only API
    Non staff user cant access this api.
    Check openapi.yaml for detailed request/response body
    """
    permission_classes = (IsAdminUser,)
    queryset = User.objects.all()
    serializer_class = UserSerializer
    http_method_names = ['get', 'post', 'head']


class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('first_name', 'last_name',
                  'email', 'password',
                  'country_code', 'phone_number',
                  'profile_picture_url')

    def validate_password(self, password):
        return make_password(password)


class UserCreateAPIView(CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserCreateSerializer
    permission_classes = (AllowAny,)


class GoogleAuthView(APIView):
    permission_classes = (AllowAny,)
    serializer_class = UserCreateSerializer

    def post(self, request):
        """
        Called after Google auto login to get access token
        Sends Google Profile data.
        """
        data = request.data

        # create user if not exist
        try:
            user = User.objects.get(email=data.get('email'))
        except User.DoesNotExist:
            data = request.data

            data._mutable = True
            # insert random default password
            data['password'] = BaseUserManager().make_random_password()
            data._mutable = False

            ser = self.serializer_class(data=data)
            ser.is_valid(raise_exception=True)
            user = ser.save()

        # Give access token for further API interactions
        return Response(data=get_jwt_token(user))


class OTPGenerateView(APIView):
    """
    A 6 digit OTP is sent to user, which user needs to enter to verify
    OTP is sent to user's email and phone
    """

    def post(self, request, *args, **kwargs):
        """
        :param request.data:  { 'email': 'email_of@user.com'}
        :return: 200: OTP sent
        :return: 404: User does not exists
        """
        data = request.data
        email = data.get('email')

        # create user if not exist
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise Exception("We couldn't find an account with this email, please verify the email you " \
                            "entered.")

        otp_code = get_new_otp(user)

        email_template = 'email/otp/otp-generate.html'

        send_templated_email(user=user,
                             subject="auth-service One Time Password",
                             template=email_template,
                             context={'otp_code': otp_code})
        send_templated_sms(user=user,
                           subject="Reset Password OTP",
                           template=email_template,
                           context={'otp_code': otp_code})
        return Response('OTP sent to your Email address and phone if exist')


class OTPLoginSerialiser(serializers.Serializer):
    email = serializers.EmailField(required=True, allow_blank=False)
    code = serializers.CharField(required=True, max_length=6, min_length=6, allow_blank=False)

    def validate(self, attrs):
        # check if user exist
        try:
            user = User.objects.get(email=attrs['email'])
        except User.DoesNotExist:
            raise Exception("We couldn't find an account with this email, "
                            "please verify the email you entered.")
        attrs['user'] = user
        return attrs


class OTPLoginView(APIView):
    """
    OTP login is used for to sign in using user's OTP
    This OTP is generated in OTPGenerateView with expiry time
    We check if OTP is valid. If valid then an access token and refresh token is given
    """

    def post(self, request, *args, **kwargs):
        """
        :param request.data:  { 'code': 'D4VW14', 'email': 'user@example.com'}
        :return: 200: Success
        :return: 403: OTP invalid
        :return: 403: Token not found for user
        """
        ser = OTPLoginSerialiser(data=request.data)
        ser.is_valid(raise_exception=True)
        data = ser.validated_data
        user = data['user']
        # check if OTP is valid
        if not check_valid_otp(user, data['code']):
            raise PermissionDenied("Invalid OTP code")

        return Response(data=get_jwt_token(user))


class ForgotPasswordView(APIView):
    """
    Used when user requests for new Password.
    A 6 digit OTP is sent to user, which user needs to enter to verify
    OTP is sent to user's email and phone
    """
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        """
        :param request.data:  { 'email': 'email_of@user.com'}
        :return: 200: OTP sent
        :return: 403: OTP invalid
        :return: 404: User does not exists
        """
        data = request.data
        email = data.get('email')

        # check user exists
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise Exception("We couldn't find an account with this email,"
                            " please verify the email you entered.")

        # Get new OTP
        otp_code = get_new_otp(user)

        # Send OTP by email
        send_templated_email(user=user,
                             subject="Reset Password OTP",
                             template='email/password-reset/forgot_password.html',
                             context={'otp_code': otp_code})
        # todo: implement sms
        # Send OTP by SMS
        send_templated_sms(user=user,
                           subject="Reset Password OTP",
                           template='email_template',
                           context={'otp_code': otp_code})
        return Response('OTP has sent to email address')


class ResetPasswordSerialiser(serializers.Serializer):
    email = serializers.EmailField(required=True, allow_blank=False)
    code = serializers.CharField(required=True, max_length=6, min_length=6, allow_blank=False)
    new_password = serializers.CharField(required=True, write_only=True, validators=[validate_password])

    def validate(self, attrs):
        # check if user exist
        try:
            user = User.objects.get(email=attrs['email'])
        except User.DoesNotExist:
            raise Exception("We couldn't find an account with this email, "
                            "please verify the email you entered.")
        attrs['user'] = user
        return attrs


class ResetPasswordView(APIView):
    """
    Used when user creates a new password
    New password is sent with OTP.
    OTP is checked against email address and password is saved if OTP is valid.
    """
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        """
        :param request.data:  { 'email': 'email_of@user.com', 'code': 'STS34Z', 'new_password': 'password'}
        :return: 200: OTP sent
        :return: 404: User does not exists
        :return: 403: OTP invalid
        """
        ser = ResetPasswordSerialiser(data=request.data)
        ser.is_valid(raise_exception=True)
        data = ser.validated_data
        user = data['user']
        # check if OTP is valid
        if not check_valid_otp(user, data['code']):
            raise PermissionDenied({'code': ['Invalid OTP code']})

        user.set_password(data['new_password'])
        user.save()
        return Response('Password reset successfully.')
