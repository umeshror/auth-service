from django.contrib.auth.models import Group
from oauth2_provider.contrib.rest_framework import TokenHasReadWriteScope
from rest_framework import serializers
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from rest_framework.viewsets import ModelViewSet

from apps.core.models import User


class UserSerializer(serializers.HyperlinkedModelSerializer):
    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'password')


class UserViewSet(ModelViewSet):
    permission_classes = (IsAdminUser,)
    queryset = User.objects.all()
    serializer_class = UserSerializer


class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'phone_number', 'password')


class UserCreateAPIView(CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserCreateSerializer
    permission_classes = (AllowAny,)


class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ('name', 'id')


class GroupViewSet(ModelViewSet):
    permission_classes = (IsAuthenticated, TokenHasReadWriteScope,)
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
