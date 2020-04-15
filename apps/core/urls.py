from rest_framework import routers

from apps.core.views import UserViewSet

router = routers.DefaultRouter()
router.register(r'user', UserViewSet)
urlpatterns = router.urls
