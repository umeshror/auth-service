from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.hashers import make_password
from rest_framework import serializers
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework_simplejwt.tokens import RefreshToken

from apps.core.models import User


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
           # provider random default password
            data['password'] = BaseUserManager().make_random_password()
            data._mutable = False

            ser = self.serializer_class(data=data)
            ser.is_valid(raise_exception=True)
            user = ser.save()

        # Give access token for further API interactions
        token = RefreshToken.for_user(user)
        response = {
            'access': str(token.access_token),
            'refresh': str(token)
        }
        return Response(data=response)
