from django.conf.urls import url

from apps.chat.consumers import ChatConsumer

websocket_urlpatterns = [
    url(r"^messages/(?P<user_id>\w+)/$", ChatConsumer),
]
