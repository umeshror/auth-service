from rest_framework import routers

from apps.core.views import UserViewSet, GroupViewSet

router = routers.DefaultRouter()
router.register(r'user', UserViewSet, basename='users')
router.register(r'group', GroupViewSet, basename='groups')
urlpatterns = router.urls
