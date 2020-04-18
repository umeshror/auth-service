from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet
from oauth2_provider.contrib.rest_framework import TokenHasReadWriteScope, TokenHasScope


class UserSerializer(serializers.HyperlinkedModelSerializer):
    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'password')


class UserViewSet(ModelViewSet):
    permission_classes = (IsAuthenticated, TokenHasReadWriteScope)
    queryset = User.objects.all()
    serializer_class = UserSerializer
