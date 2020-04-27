from django.conf.urls import url
from rest_framework import routers

from apps.core.views import UserCreateAPIView, GroupViewSet
from apps.core.views import UserViewSet

router = routers.DefaultRouter()
router.register(r'user', UserViewSet, basename='users')
router.register(r'group', GroupViewSet, basename='groups')
urlpatterns = router.urls
urlpatterns += [
    url(r'^user-create/$', UserCreateAPIView.as_view(), name='user-create'),
]
