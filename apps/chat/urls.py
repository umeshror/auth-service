from django.urls import path
from rest_framework import routers

from apps.chat.views import MessagesAPIView

router = routers.DefaultRouter()

urlpatterns = [
    path('messages/<int:receiver_id>', MessagesAPIView.as_view(), name='messages'),
]

urlpatterns += router.urls
