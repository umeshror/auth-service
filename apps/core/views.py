from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name')


class UserViewSet(ModelViewSet):
    permission_classes = (IsAuthenticated,)
    queryset = User.objects.all()
    serializer_class = UserSerializer
